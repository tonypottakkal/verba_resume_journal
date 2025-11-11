"""
ResumeGenerator module for generating tailored resumes from job descriptions.

This module provides functionality to extract job requirements, retrieve relevant
work experiences using hybrid search, and generate professional resumes using LLM.
"""

from wasabi import msg
from weaviate.client import WeaviateAsyncClient
from weaviate.classes.query import Filter, MetadataQuery, HybridFusion
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID
import uuid
import json
from dataclasses import dataclass

from goldenverba.components.conversation_manager import ConversationManager


@dataclass
class JobRequirements:
    """Represents extracted requirements from a job description."""
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str
    role_description: str
    responsibilities: List[str]
    qualifications: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "experience_level": self.experience_level,
            "role_description": self.role_description,
            "responsibilities": self.responsibilities,
            "qualifications": self.qualifications
        }


@dataclass
class ResumeOptions:
    """Configuration options for resume generation."""
    format: str = "markdown"  # markdown, pdf, docx
    sections: List[str] = None
    max_length: int = 2000
    tone: str = "professional"
    
    def __post_init__(self):
        if self.sections is None:
            self.sections = ["summary", "experience", "skills", "education"]


class Resume:
    """Represents a generated resume."""
    
    def __init__(
        self,
        content: str,
        format: str = "markdown",
        generated_at: Optional[datetime] = None,
        resume_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = resume_id or str(uuid.uuid4())
        self.content = content
        self.format = format
        self.generated_at = generated_at or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Resume to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "format": self.format,
            "generated_at": self.generated_at.isoformat(),
            "metadata": self.metadata
        }


class ResumeGenerator:
    """
    Generates tailored resumes from job descriptions and work logs.
    
    Provides methods to extract job requirements, retrieve relevant experiences
    using Weaviate hybrid search, and generate professional resumes using LLM.
    """
    
    def __init__(
        self,
        worklog_collection: str = "VERBA_WorkLog",
        document_collection: str = "VERBA_Document",
        chunk_collection: str = "VERBA_Chunk",
        max_exchanges: int = 10
    ):
        """
        Initialize ResumeGenerator.
        
        Args:
            worklog_collection: Name of the work log collection
            document_collection: Name of the document collection
            chunk_collection: Name of the chunk collection
            max_exchanges: Maximum number of conversation exchanges to keep (default: 10)
        """
        self.worklog_collection = worklog_collection
        self.document_collection = document_collection
        self.chunk_collection = chunk_collection
        self.conversation_manager = ConversationManager(max_exchanges=max_exchanges)
        msg.good(f"ResumeGenerator initialized with ConversationManager (max_exchanges={max_exchanges})")
    
    async def extract_job_requirements(
        self,
        job_description: str,
        generator,
        generator_config: dict
    ) -> JobRequirements:
        """
        Parse job description to extract requirements using LLM.
        
        Args:
            job_description: The job description text
            generator: The LLM generator instance
            generator_config: Configuration for the generator
            
        Returns:
            JobRequirements: Extracted requirements from the job description
            
        Raises:
            Exception: If extraction fails
        """
        try:
            # Create extraction prompt
            prompt = self._create_job_extraction_prompt(job_description)
            
            # Call LLM to extract requirements
            full_response = ""
            async for chunk in generator.generate_stream(
                config=generator_config,
                query=prompt,
                context="",
                conversation=[]
            ):
                if chunk.get("message"):
                    full_response += chunk["message"]
            
            # Parse JSON response
            requirements_data = self._parse_json_response(full_response)
            
            # Create JobRequirements object
            requirements = JobRequirements(
                required_skills=requirements_data.get("required_skills", []),
                preferred_skills=requirements_data.get("preferred_skills", []),
                experience_level=requirements_data.get("experience_level", ""),
                role_description=requirements_data.get("role_description", ""),
                responsibilities=requirements_data.get("responsibilities", []),
                qualifications=requirements_data.get("qualifications", [])
            )
            
            msg.good(f"Extracted {len(requirements.required_skills)} required skills from job description")
            return requirements
            
        except Exception as e:
            msg.fail(f"Failed to extract job requirements: {str(e)}")
            raise Exception(f"Failed to extract job requirements: {str(e)}")
    
    def _create_job_extraction_prompt(self, job_description: str) -> str:
        """Create a prompt for job requirement extraction."""
        return f"""Analyze the following job description and extract key information.

Return ONLY a JSON object with the following structure:
{{
    "required_skills": ["skill1", "skill2", ...],
    "preferred_skills": ["skill1", "skill2", ...],
    "experience_level": "entry/mid/senior/lead",
    "role_description": "brief description of the role",
    "responsibilities": ["responsibility1", "responsibility2", ...],
    "qualifications": ["qualification1", "qualification2", ...]
}}

Job Description:
{job_description}

JSON Response:"""
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        try:
            # Clean up response to extract JSON
            response_text = response.strip()
            
            # Try to find JSON object in response
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}")
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx + 1]
                return json.loads(json_str)
            else:
                msg.warn("Could not parse JSON from LLM response")
                return {}
                
        except Exception as e:
            msg.warn(f"JSON parsing failed: {str(e)}")
            return {}
    
    async def retrieve_relevant_experiences(
        self,
        client: WeaviateAsyncClient,
        requirements: JobRequirements,
        embedder,
        embedder_config: dict,
        limit: int = 20,
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find matching work experiences using Weaviate hybrid search.
        
        Args:
            client: Weaviate async client instance
            requirements: Extracted job requirements
            embedder: The embedder instance for vectorization
            embedder_config: Configuration for the embedder
            limit: Maximum number of results to return
            alpha: Balance between semantic (0.0) and keyword (1.0) search
            
        Returns:
            List[Dict[str, Any]]: List of relevant work log entries and chunks
            
        Raises:
            Exception: If retrieval fails
        """
        try:
            # Build search query from requirements
            search_query = self._build_search_query(requirements)
            
            # Vectorize the search query
            query_vector = await embedder.vectorize(
                config=embedder_config,
                content=[search_query]
            )
            
            experiences = []
            
            # Search work logs
            if await client.collections.exists(self.worklog_collection):
                worklog_results = await self._search_collection(
                    client=client,
                    collection_name=self.worklog_collection,
                    query=search_query,
                    vector=query_vector[0] if query_vector else None,
                    limit=limit // 2,
                    alpha=alpha,
                    required_skills=requirements.required_skills
                )
                experiences.extend(worklog_results)
            
            # Search document chunks
            if await client.collections.exists(self.chunk_collection):
                chunk_results = await self._search_collection(
                    client=client,
                    collection_name=self.chunk_collection,
                    query=search_query,
                    vector=query_vector[0] if query_vector else None,
                    limit=limit // 2,
                    alpha=alpha,
                    required_skills=requirements.required_skills
                )
                experiences.extend(chunk_results)
            
            # Sort by relevance score
            experiences.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            msg.good(f"Retrieved {len(experiences)} relevant experiences")
            return experiences[:limit]
            
        except Exception as e:
            msg.fail(f"Failed to retrieve relevant experiences: {str(e)}")
            raise Exception(f"Failed to retrieve relevant experiences: {str(e)}")
    
    def _build_search_query(self, requirements: JobRequirements) -> str:
        """Build a search query from job requirements."""
        query_parts = []
        
        # Add required skills
        if requirements.required_skills:
            query_parts.append(" ".join(requirements.required_skills))
        
        # Add role description
        if requirements.role_description:
            query_parts.append(requirements.role_description)
        
        # Add key responsibilities
        if requirements.responsibilities:
            query_parts.append(" ".join(requirements.responsibilities[:3]))
        
        return " ".join(query_parts)
    
    async def _search_collection(
        self,
        client: WeaviateAsyncClient,
        collection_name: str,
        query: str,
        vector: Optional[List[float]],
        limit: int,
        alpha: float,
        required_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Search a Weaviate collection using hybrid search.
        
        Args:
            client: Weaviate async client
            collection_name: Name of the collection to search
            query: Search query text
            vector: Query vector for semantic search
            limit: Maximum results
            alpha: Hybrid search balance
            required_skills: Skills to filter by
            
        Returns:
            List of search results with scores
        """
        try:
            collection = client.collections.get(collection_name)
            
            # Build filter for skills if applicable
            filter_obj = None
            if required_skills and collection_name == self.worklog_collection:
                # Filter work logs that contain any of the required skills
                skill_filters = [
                    Filter.by_property("extracted_skills").contains_any(required_skills)
                ]
                if skill_filters:
                    filter_obj = skill_filters[0]
            
            # Perform hybrid search
            if vector:
                response = await collection.query.hybrid(
                    query=query,
                    vector=vector,
                    limit=limit,
                    alpha=alpha,
                    fusion_type=HybridFusion.RELATIVE_SCORE,
                    filters=filter_obj,
                    return_metadata=MetadataQuery(score=True, creation_time=True)
                )
            else:
                # Fallback to keyword search if no vector
                response = await collection.query.bm25(
                    query=query,
                    limit=limit,
                    filters=filter_obj,
                    return_metadata=MetadataQuery(score=True, creation_time=True)
                )
            
            # Format results
            results = []
            for obj in response.objects:
                result = {
                    "id": str(obj.uuid),
                    "content": obj.properties.get("content", obj.properties.get("text", "")),
                    "score": obj.metadata.score if obj.metadata.score else 0.0,
                    "source": collection_name,
                    "properties": obj.properties
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            msg.warn(f"Search failed for {collection_name}: {str(e)}")
            return []
    
    async def generate_resume(
        self,
        job_description: str,
        experiences: List[Dict[str, Any]],
        requirements: JobRequirements,
        generator,
        generator_config: dict,
        options: ResumeOptions,
        session_id: Optional[str] = None,
        user_feedback: Optional[str] = None
    ) -> Resume:
        """
        Generate a tailored resume using LLM.
        
        Orchestrates requirement extraction, experience retrieval, and LLM-based
        resume writing with support for iterative refinement.
        
        Args:
            job_description: The target job description
            experiences: Retrieved relevant work experiences
            requirements: Extracted job requirements
            generator: The LLM generator instance
            generator_config: Configuration for the generator
            options: Resume generation options
            session_id: Optional session ID for conversation context
            user_feedback: Optional user feedback for refinement
            
        Returns:
            Resume: The generated resume
            
        Raises:
            Exception: If generation fails
        """
        try:
            # Get or create conversation context using ConversationManager
            conversation = []
            if session_id:
                # Create session if it doesn't exist
                if not self.conversation_manager.session_exists(session_id):
                    self.conversation_manager.create_session(
                        session_id=session_id,
                        metadata={
                            "job_description": job_description,
                            "target_role": requirements.role_description
                        }
                    )
                
                # Get conversation history in OpenAI format
                conversation = self.conversation_manager.get_conversation_history(
                    session_id,
                    format="openai"
                )
            
            # Build context from experiences
            context = self._build_resume_context(experiences, requirements)
            
            # Create resume generation prompt
            if user_feedback:
                # Refinement prompt
                prompt = self._create_refinement_prompt(
                    job_description,
                    requirements,
                    user_feedback,
                    options
                )
            else:
                # Initial generation prompt
                prompt = self._create_resume_prompt(
                    job_description,
                    requirements,
                    options
                )
            
            # Generate resume using LLM
            full_response = ""
            async for chunk in generator.generate_stream(
                config=generator_config,
                query=prompt,
                context=context,
                conversation=conversation
            ):
                if chunk.get("message"):
                    full_response += chunk["message"]
            
            # Update conversation context if session provided
            if session_id:
                self.conversation_manager.append_user_message(
                    session_id,
                    prompt,
                    metadata={"type": "refinement" if user_feedback else "initial"}
                )
                self.conversation_manager.append_assistant_message(
                    session_id,
                    full_response,
                    metadata={"resume_length": len(full_response)}
                )
            
            # Create Resume object
            resume = Resume(
                content=full_response,
                format=options.format,
                metadata={
                    "job_description": job_description,
                    "requirements": requirements.to_dict(),
                    "experience_count": len(experiences),
                    "session_id": session_id,
                    "options": {
                        "sections": options.sections,
                        "tone": options.tone,
                        "max_length": options.max_length
                    }
                }
            )
            
            msg.good(f"Generated resume with {len(full_response)} characters")
            return resume
            
        except Exception as e:
            msg.fail(f"Failed to generate resume: {str(e)}")
            raise Exception(f"Failed to generate resume: {str(e)}")
    
    def _build_resume_context(
        self,
        experiences: List[Dict[str, Any]],
        requirements: JobRequirements
    ) -> str:
        """Build context string from experiences for resume generation."""
        context_parts = []
        
        # Add job requirements summary
        context_parts.append("=== JOB REQUIREMENTS ===")
        context_parts.append(f"Required Skills: {', '.join(requirements.required_skills)}")
        context_parts.append(f"Experience Level: {requirements.experience_level}")
        context_parts.append("")
        
        # Add relevant experiences
        context_parts.append("=== RELEVANT WORK EXPERIENCES ===")
        for i, exp in enumerate(experiences, 1):
            content = exp.get("content", "")
            score = exp.get("score", 0)
            context_parts.append(f"\n[Experience {i}] (Relevance: {score:.2f})")
            context_parts.append(content)
        
        return "\n".join(context_parts)
    
    def _create_resume_prompt(
        self,
        job_description: str,
        requirements: JobRequirements,
        options: ResumeOptions
    ) -> str:
        """Create a prompt for initial resume generation."""
        sections_str = ", ".join(options.sections)
        
        return f"""Generate a professional resume tailored to the following job description.

JOB DESCRIPTION:
{job_description}

REQUIREMENTS:
- Include these sections: {sections_str}
- Tone: {options.tone}
- Maximum length: {options.max_length} words
- Format: {options.format}

INSTRUCTIONS:
1. Use the provided work experiences from the context to highlight relevant accomplishments
2. Emphasize skills and experiences that match the required skills: {', '.join(requirements.required_skills[:5])}
3. Tailor the language to match the job description's tone and requirements
4. Use action verbs and quantify achievements where possible
5. Ensure the resume is ATS-friendly and well-structured

Generate the resume now:"""
    
    def _create_refinement_prompt(
        self,
        job_description: str,
        requirements: JobRequirements,
        user_feedback: str,
        options: ResumeOptions
    ) -> str:
        """Create a prompt for resume refinement based on user feedback."""
        return f"""Refine the previously generated resume based on the following feedback:

USER FEEDBACK:
{user_feedback}

JOB DESCRIPTION (for reference):
{job_description}

INSTRUCTIONS:
1. Address the specific feedback provided by the user
2. Maintain the overall structure and quality of the resume
3. Ensure all changes align with the job requirements
4. Keep the tone {options.tone} and format as {options.format}

Generate the refined resume now:"""
    
    def create_conversation_session(
        self,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new conversation session for resume generation.
        
        Args:
            session_id: Optional custom session ID
            metadata: Optional metadata for the session
            
        Returns:
            str: The session ID
        """
        return self.conversation_manager.create_session(session_id, metadata)
    
    def get_conversation_history(
        self,
        session_id: str,
        format: str = "openai"
    ) -> Any:
        """
        Get conversation history for a session.
        
        Args:
            session_id: The session ID
            format: Output format ("list", "dict", or "openai")
            
        Returns:
            Conversation history in requested format
        """
        return self.conversation_manager.get_conversation_history(session_id, format)
    
    def reset_conversation_context(self, session_id: str) -> bool:
        """
        Clear conversation context for a session.
        
        Args:
            session_id: The session ID to reset
            
        Returns:
            bool: True if successful, False if session not found
        """
        return self.conversation_manager.reset_session(session_id)
    
    def delete_conversation_session(self, session_id: str) -> bool:
        """
        Delete a conversation session entirely.
        
        Args:
            session_id: The session ID to delete
            
        Returns:
            bool: True if successful, False if session not found
        """
        return self.conversation_manager.delete_session(session_id)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a conversation session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Dict with session info or None if not found
        """
        return self.conversation_manager.get_session_info(session_id)
    
    def format_resume(
        self,
        resume: Resume,
        target_format: str
    ) -> bytes:
        """
        Export resume in specified format (markdown, PDF, or DOCX).
        
        Args:
            resume: The resume to format
            target_format: Target format (markdown, pdf, docx)
            
        Returns:
            bytes: Formatted resume content
            
        Raises:
            Exception: If formatting fails or format is unsupported
        """
        try:
            if target_format.lower() == "markdown":
                # Return markdown as UTF-8 bytes
                return resume.content.encode('utf-8')
            
            elif target_format.lower() == "pdf":
                # PDF export will be implemented in task 20.1
                msg.warn("PDF export not yet implemented")
                raise NotImplementedError("PDF export will be implemented in task 20.1")
            
            elif target_format.lower() == "docx":
                # DOCX export will be implemented in task 20.2
                msg.warn("DOCX export not yet implemented")
                raise NotImplementedError("DOCX export will be implemented in task 20.2")
            
            else:
                raise ValueError(f"Unsupported format: {target_format}")
                
        except Exception as e:
            msg.fail(f"Failed to format resume: {str(e)}")
            raise Exception(f"Failed to format resume: {str(e)}")
