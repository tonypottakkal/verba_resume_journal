"""
SkillsExtractor module for extracting and analyzing skills from text.

This module provides functionality to extract skills from work logs and documents,
categorize them into predefined categories, calculate proficiency scores, and
generate comprehensive skills reports.
"""

from wasabi import msg
from weaviate.client import WeaviateAsyncClient
from weaviate.classes.query import Filter, Sort
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID
import uuid
import json
import hashlib
from collections import defaultdict


# Predefined skill categories
SKILL_CATEGORIES = {
    "programming_languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL"
    ],
    "frameworks": [
        "React", "Angular", "Vue", "Django", "Flask", "FastAPI", "Spring", "Express",
        "Next.js", "Nuxt.js", "Laravel", "Rails", "ASP.NET", "TensorFlow", "PyTorch"
    ],
    "databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
        "DynamoDB", "Oracle", "SQL Server", "Neo4j", "Weaviate", "Pinecone"
    ],
    "cloud_platforms": [
        "AWS", "Azure", "GCP", "Heroku", "DigitalOcean", "Vercel", "Netlify",
        "CloudFlare", "IBM Cloud", "Oracle Cloud"
    ],
    "devops_tools": [
        "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions", "Terraform",
        "Ansible", "Chef", "Puppet", "CircleCI", "Travis CI", "ArgoCD"
    ],
    "data_science": [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Data Analysis",
        "Statistical Modeling", "Feature Engineering", "Model Deployment", "MLOps"
    ],
    "soft_skills": [
        "Leadership", "Communication", "Problem Solving", "Team Collaboration",
        "Project Management", "Agile", "Scrum", "Mentoring", "Technical Writing"
    ],
    "tools": [
        "Git", "VS Code", "IntelliJ", "Jupyter", "Postman", "Jira", "Confluence",
        "Slack", "Figma", "Adobe XD", "Tableau", "Power BI"
    ]
}


class Skill:
    """Represents a skill with its properties."""
    
    def __init__(
        self,
        name: str,
        category: str,
        proficiency_score: float = 0.0,
        occurrence_count: int = 1,
        source_documents: Optional[List[str]] = None,
        last_used: Optional[datetime] = None,
        skill_id: Optional[str] = None
    ):
        self.id = skill_id or str(uuid.uuid4())
        self.name = name
        self.category = category
        self.proficiency_score = proficiency_score
        self.occurrence_count = occurrence_count
        self.source_documents = source_documents or []
        self.last_used = last_used or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Skill to dictionary for Weaviate storage."""
        # Ensure datetime has timezone info for Weaviate RFC3339 format
        from datetime import timezone
        last_used_aware = self.last_used.replace(tzinfo=timezone.utc) if self.last_used.tzinfo is None else self.last_used
        
        return {
            "name": self.name,
            "category": self.category,
            "proficiency_score": self.proficiency_score,
            "occurrence_count": self.occurrence_count,
            "source_documents": self.source_documents,
            "last_used": last_used_aware.isoformat()
        }
    
    @classmethod
    def from_weaviate_object(cls, weaviate_obj) -> "Skill":
        """Create Skill from Weaviate object."""
        props = weaviate_obj.properties
        
        # Handle last_used - Weaviate returns it as datetime object, not string
        last_used_value = props.get("last_used")
        if last_used_value:
            if isinstance(last_used_value, str):
                last_used = datetime.fromisoformat(last_used_value)
            else:
                # Already a datetime object
                last_used = last_used_value
        else:
            last_used = datetime.now()
        
        return cls(
            name=props.get("name", ""),
            category=props.get("category", ""),
            proficiency_score=props.get("proficiency_score", 0.0),
            occurrence_count=props.get("occurrence_count", 1),
            source_documents=props.get("source_documents", []),
            last_used=last_used,
            skill_id=str(weaviate_obj.uuid)
        )


class SkillsReport:
    """Represents a comprehensive skills report."""
    
    def __init__(
        self,
        skills_by_category: Dict[str, List[Skill]],
        total_skills: int,
        top_skills: List[Skill],
        recent_skills: List[Skill],
        generated_at: datetime
    ):
        self.skills_by_category = skills_by_category
        self.total_skills = total_skills
        self.top_skills = top_skills
        self.recent_skills = recent_skills
        self.generated_at = generated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SkillsReport to dictionary."""
        return {
            "skills_by_category": {
                category: [skill.to_dict() for skill in skills]
                for category, skills in self.skills_by_category.items()
            },
            "total_skills": self.total_skills,
            "top_skills": [skill.to_dict() for skill in self.top_skills],
            "recent_skills": [skill.to_dict() for skill in self.recent_skills],
            "generated_at": self.generated_at.isoformat()
        }


class SkillsExtractor:
    """
    Extracts and analyzes skills from text using LLM.
    
    Provides methods to extract skills, categorize them, calculate proficiency,
    and generate comprehensive skills reports with caching support.
    """
    
    def __init__(
        self,
        skill_collection_name: str = "VERBA_Skill",
        cache_collection_name: str = "VERBA_Cache_Skills"
    ):
        """
        Initialize SkillsExtractor.
        
        Args:
            skill_collection_name: Name of the Weaviate collection for skills
            cache_collection_name: Name of the Weaviate collection for caching
        """
        self.skill_collection_name = skill_collection_name
        self.cache_collection_name = cache_collection_name
        self.skill_categories = SKILL_CATEGORIES
    
    def _generate_cache_key(self, text: str) -> str:
        """Generate a cache key from text content."""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def _get_cached_skills(
        self,
        client: WeaviateAsyncClient,
        cache_key: str
    ) -> Optional[List[str]]:
        """
        Retrieve cached skills for a given text.
        
        Args:
            client: Weaviate async client instance
            cache_key: Cache key for the text
            
        Returns:
            Optional[List[str]]: Cached skills if found, None otherwise
        """
        try:
            if not await client.collections.exists(self.cache_collection_name):
                return None
            
            collection = client.collections.get(self.cache_collection_name)
            response = await collection.query.fetch_objects(
                filters=Filter.by_property("cache_key").equal(cache_key),
                limit=1
            )
            
            if response.objects:
                cached_data = response.objects[0].properties.get("skills", "[]")
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            msg.warn(f"Failed to retrieve cached skills: {str(e)}")
            return None
    
    async def _cache_skills(
        self,
        client: WeaviateAsyncClient,
        cache_key: str,
        skills: List[str]
    ) -> bool:
        """
        Cache extracted skills for future use.
        
        Args:
            client: Weaviate async client instance
            cache_key: Cache key for the text
            skills: List of extracted skills
            
        Returns:
            bool: True if caching was successful
        """
        try:
            if not await client.collections.exists(self.cache_collection_name):
                # Create cache collection if it doesn't exist
                from weaviate.classes.config import Configure, Property, DataType
                await client.collections.create(
                    name=self.cache_collection_name,
                    properties=[
                        Property(name="cache_key", data_type=DataType.TEXT),
                        Property(name="skills", data_type=DataType.TEXT),
                        Property(name="cached_at", data_type=DataType.DATE)
                    ],
                    vectorizer_config=Configure.Vectorizer.none()
                )
            
            collection = client.collections.get(self.cache_collection_name)
            
            # Check if cache entry already exists
            existing = await collection.query.fetch_objects(
                filters=Filter.by_property("cache_key").equal(cache_key),
                limit=1
            )
            
            cache_data = {
                "cache_key": cache_key,
                "skills": json.dumps(skills),
                "cached_at": datetime.now().isoformat()
            }
            
            if existing.objects:
                # Update existing cache entry
                await collection.data.update(
                    uuid=existing.objects[0].uuid,
                    properties=cache_data
                )
            else:
                # Insert new cache entry
                await collection.data.insert(properties=cache_data)
            
            return True
            
        except Exception as e:
            msg.warn(f"Failed to cache skills: {str(e)}")
            return False
    
    async def extract_skills(
        self,
        client: WeaviateAsyncClient,
        text: str,
        generator_config: dict,
        use_cache: bool = True
    ) -> List[str]:
        """
        Extract skills from text using LLM.
        
        Args:
            client: Weaviate async client instance
            text: Text content to extract skills from
            generator_config: Configuration for the LLM generator
            use_cache: Whether to use caching for skill extraction
            
        Returns:
            List[str]: List of extracted skill names
            
        Raises:
            Exception: If skill extraction fails
        """
        try:
            # Check cache first
            if use_cache:
                cache_key = self._generate_cache_key(text)
                cached_skills = await self._get_cached_skills(client, cache_key)
                if cached_skills is not None:
                    msg.info(f"Retrieved {len(cached_skills)} skills from cache")
                    return cached_skills
            
            # Prepare prompt for LLM
            prompt = self._create_extraction_prompt(text)
            
            # Call LLM to extract skills
            extracted_skills = await self._call_llm_for_extraction(
                prompt,
                generator_config
            )
            
            # Cache the results
            if use_cache and extracted_skills:
                await self._cache_skills(client, cache_key, extracted_skills)
            
            msg.good(f"Extracted {len(extracted_skills)} skills from text")
            return extracted_skills
            
        except Exception as e:
            msg.fail(f"Failed to extract skills: {str(e)}")
            raise Exception(f"Failed to extract skills: {str(e)}")
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create a prompt for skill extraction."""
        return f"""Extract all technical and professional skills from the following text.
Focus on:
- Programming languages
- Frameworks and libraries
- Tools and technologies
- Cloud platforms
- Databases
- Methodologies and practices
- Soft skills

Return ONLY a JSON array of skill names, nothing else. Example: ["Python", "Docker", "Leadership"]

Text:
{text}

Skills (JSON array only):"""
    
    async def _call_llm_for_extraction(
        self,
        prompt: str,
        generator_config: dict
    ) -> List[str]:
        """
        Call LLM to extract skills from prompt.
        
        Args:
            prompt: The extraction prompt
            generator_config: Configuration for the LLM generator
            
        Returns:
            List[str]: Extracted skills
        """
        try:
            # Get the selected generator from config
            selected_generator = generator_config.get("selected", "Ollama")
            
            # Import generator dynamically based on config
            if selected_generator == "OpenAI":
                from goldenverba.components.generation.OpenAIGenerator import OpenAIGenerator
                generator = OpenAIGenerator()
            elif selected_generator == "Ollama":
                from goldenverba.components.generation.OllamaGenerator import OllamaGenerator
                generator = OllamaGenerator()
            else:
                msg.warn(f"Unknown generator: {selected_generator}, defaulting to Ollama")
                from goldenverba.components.generation.OllamaGenerator import OllamaGenerator
                generator = OllamaGenerator()
            
            # Get the component-specific config
            component_config = generator_config.get("components", {}).get(selected_generator, {})
            # Extract the actual config dict with Model, System Message, etc.
            raw_config = component_config.get("config", {})
            
            # Convert raw config to InputConfig-like objects for generator compatibility
            # The generator expects config items to have .value attribute
            from goldenverba.components.types import InputConfig
            actual_config = {}
            for key, value in raw_config.items():
                if isinstance(value, dict) and "value" in value:
                    # Create InputConfig object from dict
                    actual_config[key] = InputConfig(**value)
                else:
                    actual_config[key] = value
            
            # Collect streaming response
            full_response = ""
            async for chunk in generator.generate_stream(
                config=actual_config,
                query=prompt,
                context="",
                conversation=[]
            ):
                if chunk.get("message"):
                    full_response += chunk["message"]
            
            # Parse JSON response
            # Clean up response to extract JSON array
            response_text = full_response.strip()
            
            # Try to find JSON array in response
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]")
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx + 1]
                skills = json.loads(json_str)
                return [skill.strip() for skill in skills if skill.strip()]
            else:
                msg.warn("Could not parse JSON from LLM response")
                return []
            
        except Exception as e:
            msg.fail(f"LLM extraction failed: {str(e)}")
            return []
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Group skills into predefined categories.
        
        Args:
            skills: List of skill names to categorize
            
        Returns:
            Dict[str, List[str]]: Skills grouped by category
        """
        categorized = defaultdict(list)
        uncategorized = []
        
        for skill in skills:
            skill_lower = skill.lower()
            found_category = False
            
            # Check each category for matches
            for category, category_skills in self.skill_categories.items():
                for category_skill in category_skills:
                    if (skill_lower == category_skill.lower() or 
                        skill_lower in category_skill.lower() or
                        category_skill.lower() in skill_lower):
                        categorized[category].append(skill)
                        found_category = True
                        break
                if found_category:
                    break
            
            if not found_category:
                uncategorized.append(skill)
        
        # Add uncategorized skills to "other" category
        if uncategorized:
            categorized["other"] = uncategorized
        
        msg.info(f"Categorized {len(skills)} skills into {len(categorized)} categories")
        return dict(categorized)
    
    async def calculate_proficiency(
        self,
        client: WeaviateAsyncClient,
        skill_name: str,
        documents: List[str]
    ) -> float:
        """
        Calculate proficiency score based on frequency and context analysis.
        
        The proficiency score is calculated based on:
        - Number of occurrences (frequency)
        - Recency of usage
        - Context diversity (number of different documents)
        
        Args:
            client: Weaviate async client instance
            skill_name: Name of the skill
            documents: List of document UUIDs where skill appears
            
        Returns:
            float: Proficiency score between 0.0 and 1.0
        """
        try:
            # Base score from occurrence count
            occurrence_score = min(len(documents) / 10.0, 0.5)  # Max 0.5 from occurrences
            
            # Diversity score from unique documents
            diversity_score = min(len(set(documents)) / 5.0, 0.3)  # Max 0.3 from diversity
            
            # Recency score (check if skill exists and get last_used)
            recency_score = 0.2  # Default recency score
            
            if await client.collections.exists(self.skill_collection_name):
                collection = client.collections.get(self.skill_collection_name)
                response = await collection.query.fetch_objects(
                    filters=Filter.by_property("name").equal(skill_name),
                    limit=1
                )
                
                if response.objects:
                    last_used = datetime.fromisoformat(
                        response.objects[0].properties.get("last_used")
                    )
                    days_since_use = (datetime.now() - last_used).days
                    
                    # More recent = higher score
                    if days_since_use < 30:
                        recency_score = 0.2
                    elif days_since_use < 90:
                        recency_score = 0.15
                    elif days_since_use < 180:
                        recency_score = 0.1
                    else:
                        recency_score = 0.05
            
            # Total proficiency score
            proficiency = occurrence_score + diversity_score + recency_score
            
            return min(proficiency, 1.0)  # Cap at 1.0
            
        except Exception as e:
            msg.warn(f"Failed to calculate proficiency for {skill_name}: {str(e)}")
            return 0.5  # Default proficiency
    
    async def store_or_update_skill(
        self,
        client: WeaviateAsyncClient,
        skill_name: str,
        category: str,
        source_document_id: str
    ) -> Skill:
        """
        Store a new skill or update an existing one.
        
        Args:
            client: Weaviate async client instance
            skill_name: Name of the skill
            category: Category of the skill
            source_document_id: UUID of the source document
            
        Returns:
            Skill: The stored or updated skill
        """
        try:
            if not await client.collections.exists(self.skill_collection_name):
                raise Exception(f"Collection {self.skill_collection_name} does not exist")
            
            collection = client.collections.get(self.skill_collection_name)
            
            # Check if skill already exists
            response = await collection.query.fetch_objects(
                filters=Filter.by_property("name").equal(skill_name),
                limit=1
            )
            
            if response.objects:
                # Update existing skill
                existing_skill = Skill.from_weaviate_object(response.objects[0])
                
                # Update properties
                if source_document_id not in existing_skill.source_documents:
                    existing_skill.source_documents.append(source_document_id)
                existing_skill.occurrence_count += 1
                existing_skill.last_used = datetime.now()
                
                # Recalculate proficiency
                existing_skill.proficiency_score = await self.calculate_proficiency(
                    client,
                    skill_name,
                    existing_skill.source_documents
                )
                
                # Update in Weaviate
                await collection.data.update(
                    uuid=UUID(existing_skill.id),
                    properties=existing_skill.to_dict()
                )
                
                msg.info(f"Updated skill: {skill_name}")
                return existing_skill
            else:
                # Create new skill
                proficiency = await self.calculate_proficiency(
                    client,
                    skill_name,
                    [source_document_id]
                )
                
                new_skill = Skill(
                    name=skill_name,
                    category=category,
                    proficiency_score=proficiency,
                    occurrence_count=1,
                    source_documents=[source_document_id],
                    last_used=datetime.now()
                )
                
                # Insert into Weaviate
                skill_uuid = await collection.data.insert(
                    properties=new_skill.to_dict()
                )
                new_skill.id = str(skill_uuid)
                
                msg.good(f"Created new skill: {skill_name}")
                return new_skill
                
        except Exception as e:
            msg.fail(f"Failed to store/update skill: {str(e)}")
            raise Exception(f"Failed to store/update skill: {str(e)}")
    
    async def aggregate_skills(
        self,
        client: WeaviateAsyncClient,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category_filter: Optional[str] = None
    ) -> SkillsReport:
        """
        Generate comprehensive skills report.
        
        Args:
            client: Weaviate async client instance
            start_date: Optional filter by start date
            end_date: Optional filter by end date
            category_filter: Optional filter by category
            
        Returns:
            SkillsReport: Comprehensive skills report
            
        Raises:
            Exception: If report generation fails
        """
        try:
            if not await client.collections.exists(self.skill_collection_name):
                raise Exception(f"Collection {self.skill_collection_name} does not exist")
            
            collection = client.collections.get(self.skill_collection_name)
            
            # Build filters
            filters = []
            
            if start_date:
                # Ensure timezone-aware datetime in RFC3339 format
                if start_date.tzinfo is None:
                    from datetime import timezone
                    start_date = start_date.replace(tzinfo=timezone.utc)
                filters.append(
                    Filter.by_property("last_used").greater_or_equal(start_date.isoformat())
                )
            
            if end_date:
                # Ensure timezone-aware datetime in RFC3339 format
                if end_date.tzinfo is None:
                    from datetime import timezone
                    end_date = end_date.replace(tzinfo=timezone.utc)
                filters.append(
                    Filter.by_property("last_used").less_or_equal(end_date.isoformat())
                )
            
            if category_filter:
                filters.append(
                    Filter.by_property("category").equal(category_filter)
                )
            
            # Combine filters
            combined_filter = None
            if len(filters) == 1:
                combined_filter = filters[0]
            elif len(filters) > 1:
                combined_filter = filters[0]
                for f in filters[1:]:
                    combined_filter = combined_filter & f
            
            # Fetch all matching skills
            if combined_filter:
                response = await collection.query.fetch_objects(
                    filters=combined_filter,
                    limit=1000
                )
            else:
                response = await collection.query.fetch_objects(limit=1000)
            
            # Convert to Skill objects
            all_skills = [
                Skill.from_weaviate_object(obj)
                for obj in response.objects
            ]
            
            # Group by category
            skills_by_category = defaultdict(list)
            for skill in all_skills:
                skills_by_category[skill.category].append(skill)
            
            # Sort skills within each category by proficiency
            for category in skills_by_category:
                skills_by_category[category].sort(
                    key=lambda s: s.proficiency_score,
                    reverse=True
                )
            
            # Get top skills overall
            top_skills = sorted(
                all_skills,
                key=lambda s: s.proficiency_score,
                reverse=True
            )[:10]
            
            # Get recent skills
            recent_skills = sorted(
                all_skills,
                key=lambda s: s.last_used,
                reverse=True
            )[:10]
            
            report = SkillsReport(
                skills_by_category=dict(skills_by_category),
                total_skills=len(all_skills),
                top_skills=top_skills,
                recent_skills=recent_skills,
                generated_at=datetime.now()
            )
            
            msg.good(f"Generated skills report with {len(all_skills)} skills")
            return report
            
        except Exception as e:
            msg.fail(f"Failed to generate skills report: {str(e)}")
            raise Exception(f"Failed to generate skills report: {str(e)}")
    
    async def get_all_skills(
        self,
        client: WeaviateAsyncClient,
        limit: int = 100,
        offset: int = 0
    ) -> List[Skill]:
        """
        Retrieve all skills with pagination.
        
        Args:
            client: Weaviate async client instance
            limit: Maximum number of skills to return
            offset: Number of skills to skip
            
        Returns:
            List[Skill]: List of skills
        """
        try:
            if not await client.collections.exists(self.skill_collection_name):
                return []
            
            collection = client.collections.get(self.skill_collection_name)
            
            response = await collection.query.fetch_objects(
                limit=limit,
                offset=offset,
                sort=Sort.by_property("proficiency_score", ascending=False)
            )
            
            skills = [
                Skill.from_weaviate_object(obj)
                for obj in response.objects
            ]
            
            return skills
            
        except Exception as e:
            msg.fail(f"Failed to retrieve skills: {str(e)}")
            return []
    
    async def delete_skill(
        self,
        client: WeaviateAsyncClient,
        skill_id: str
    ) -> bool:
        """
        Delete a skill from the collection.
        
        Args:
            client: Weaviate async client instance
            skill_id: UUID of the skill to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            if not await client.collections.exists(self.skill_collection_name):
                return False
            
            collection = client.collections.get(self.skill_collection_name)
            
            if await collection.data.exists(UUID(skill_id)):
                await collection.data.delete_by_id(UUID(skill_id))
                msg.good(f"Deleted skill: {skill_id}")
                return True
            else:
                msg.warn(f"Skill not found: {skill_id}")
                return False
                
        except Exception as e:
            msg.fail(f"Failed to delete skill: {str(e)}")
            return False
