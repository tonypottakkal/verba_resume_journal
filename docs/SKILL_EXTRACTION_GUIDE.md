# Skill Extraction and Categorization Guide

Complete guide to understanding and optimizing the skill extraction system.

## Table of Contents

- [Overview](#overview)
- [How Skill Extraction Works](#how-skill-extraction-works)
- [Skill Categories](#skill-categories)
- [Proficiency Scoring](#proficiency-scoring)
- [Extraction Triggers](#extraction-triggers)
- [Customization](#customization)
- [Best Practices](#best-practices)

---

## Overview

The Local Resume System automatically extracts and categorizes professional skills from your work logs and documents using Large Language Models (LLMs). This enables:

- **Automatic skill tracking** without manual tagging
- **Proficiency scoring** based on usage patterns
- **Category organization** for easy visualization
- **Resume optimization** by matching skills to job requirements

### Key Features

- **Multi-source extraction**: Works with work logs, PDFs, documents, and more
- **Intelligent categorization**: Groups skills into meaningful categories
- **Context-aware**: Understands skill usage depth, not just mentions
- **Continuous learning**: Updates proficiency as you add more content
- **Privacy-first**: Can run entirely locally with Ollama

---

## How Skill Extraction Works

### Extraction Pipeline

```
Document/Work Log
       ↓
Text Preprocessing
       ↓
LLM Analysis (GPT-4, Claude, Ollama, etc.)
       ↓
Skill Identification
       ↓
Category Assignment
       ↓
Proficiency Calculation
       ↓
Storage in Weaviate
```

### Step-by-Step Process

**1. Text Preprocessing**
- Remove formatting and special characters
- Normalize whitespace
- Preserve technical terms and acronyms

**2. LLM Analysis**
The system sends text to your configured LLM with a specialized prompt:

```
Extract technical and professional skills from this text.
For each skill, identify:
- Skill name (normalized)
- Category (from predefined list)
- Usage context (how it was used)
- Confidence score (0-1)

Text: "Today I implemented a REST API using FastAPI and PostgreSQL..."
```

**3. Skill Identification**
The LLM returns structured data:
```json
{
  "skills": [
    {
      "name": "FastAPI",
      "category": "Frameworks",
      "context": "Implemented REST API",
      "confidence": 0.95
    },
    {
      "name": "PostgreSQL",
      "category": "Databases",
      "context": "Database integration",
      "confidence": 0.93
    }
  ]
}
```

**4. Category Assignment**
Skills are assigned to predefined categories:
- Programming Languages
- Frameworks
- Databases
- Cloud Services
- DevOps Tools
- Soft Skills

**5. Proficiency Calculation**
The system calculates proficiency based on:
- **Frequency**: How often you use the skill
- **Recency**: How recently you've used it
- **Context**: The depth and complexity of usage

**6. Storage**
Skills are stored in Weaviate with:
- Skill name and category
- Proficiency score
- Source documents
- Last used date
- Occurrence count

---

## Skill Categories

### Default Categories

**Programming Languages**
- Python, JavaScript, TypeScript, Java, C++, Go, Rust, etc.
- Scripting languages: Bash, PowerShell
- Query languages: SQL, GraphQL

**Frameworks**
- Web: React, Vue, Angular, Next.js, Django, Flask, FastAPI
- Mobile: React Native, Flutter, Swift UI
- ML: TensorFlow, PyTorch, scikit-learn

**Databases**
- Relational: PostgreSQL, MySQL, SQL Server, Oracle
- NoSQL: MongoDB, Redis, Cassandra, DynamoDB
- Vector: Weaviate, Pinecone, Qdrant

**Cloud Services**
- AWS: EC2, S3, Lambda, RDS, ECS
- Azure: VMs, Blob Storage, Functions
- GCP: Compute Engine, Cloud Storage, Cloud Functions

**DevOps Tools**
- Containers: Docker, Kubernetes, Podman
- CI/CD: Jenkins, GitHub Actions, GitLab CI, CircleCI
- IaC: Terraform, Ansible, CloudFormation
- Monitoring: Prometheus, Grafana, DataDog

**Soft Skills**
- Leadership, Mentoring, Communication
- Project Management, Agile, Scrum
- Problem Solving, Critical Thinking
- Collaboration, Teamwork

### Customizing Categories

Edit `goldenverba/components/skills_extractor.py`:

```python
SKILL_CATEGORIES = [
    "Programming Languages",
    "Frameworks",
    "Databases",
    "Cloud Services",
    "DevOps Tools",
    "Soft Skills",
    # Add custom categories
    "Domain Knowledge",
    "Certifications",
    "Tools & Software"
]
```

### Category-Specific Examples

**For Data Scientists:**
```python
SKILL_CATEGORIES = [
    "Programming Languages",
    "ML Frameworks",
    "Data Tools",
    "Visualization",
    "Statistics & Math",
    "Domain Knowledge",
    "Soft Skills"
]
```

**For DevOps Engineers:**
```python
SKILL_CATEGORIES = [
    "Programming Languages",
    "Container Orchestration",
    "CI/CD Tools",
    "Infrastructure as Code",
    "Monitoring & Logging",
    "Cloud Platforms",
    "Security Tools",
    "Soft Skills"
]
```

---

## Proficiency Scoring

### Calculation Formula

```
Proficiency = (Frequency × W_f) + (Recency × W_r) + (Context × W_c)

Where:
W_f = Frequency weight (default: 0.6)
W_r = Recency weight (default: 0.3)
W_c = Context weight (default: 0.1)
```

### Component Breakdown

**1. Frequency Score (0-1)**

Measures how often you use a skill:

```python
frequency_score = min(occurrence_count / 50, 1.0)
```

Examples:
- 5 occurrences → 0.10
- 25 occurrences → 0.50
- 50+ occurrences → 1.00

**2. Recency Score (0-1)**

Measures how recently you've used a skill:

```python
days_since_use = (today - last_used_date).days
recency_score = exp(-days_since_use / 180)
```

Examples:
- Used today → 1.00
- Used 90 days ago → 0.61
- Used 180 days ago → 0.37
- Used 365 days ago → 0.13

**3. Context Score (0-1)**

Measures depth of skill usage (analyzed by LLM):

- **0.9-1.0**: Expert usage
  - "Architected microservices system using Kubernetes"
  - "Led team in implementing advanced React patterns"

- **0.7-0.89**: Advanced usage
  - "Optimized PostgreSQL queries for performance"
  - "Implemented CI/CD pipeline with GitHub Actions"

- **0.5-0.69**: Intermediate usage
  - "Used Docker for containerization"
  - "Wrote unit tests with pytest"

- **0.3-0.49**: Basic usage
  - "Deployed application to AWS"
  - "Used Git for version control"

- **0.0-0.29**: Minimal usage
  - "Familiar with React"
  - "Exposure to Kubernetes"

### Proficiency Levels

**Expert (0.9-1.0)**
- Frequent, recent, and deep usage
- Can architect systems and mentor others
- Example: "Python: 0.95"

**Advanced (0.7-0.89)**
- Regular usage with good depth
- Can handle complex tasks independently
- Example: "React: 0.82"

**Intermediate (0.5-0.69)**
- Moderate usage and understanding
- Can complete standard tasks
- Example: "Docker: 0.63"

**Basic (0.3-0.49)**
- Limited usage or older experience
- Needs guidance for complex tasks
- Example: "Kubernetes: 0.41"

**Beginner (0.0-0.29)**
- Minimal exposure
- Requires significant learning
- Example: "Rust: 0.15"

### Tuning Proficiency Weights

**For Career Changers (emphasize recent skills):**
```bash
PROFICIENCY_FREQUENCY_WEIGHT=0.4
PROFICIENCY_RECENCY_WEIGHT=0.5
PROFICIENCY_CONTEXT_WEIGHT=0.1
```

**For Experienced Professionals (emphasize depth):**
```bash
PROFICIENCY_FREQUENCY_WEIGHT=0.5
PROFICIENCY_RECENCY_WEIGHT=0.2
PROFICIENCY_CONTEXT_WEIGHT=0.3
```

**For Consultants (emphasize variety):**
```bash
PROFICIENCY_FREQUENCY_WEIGHT=0.7
PROFICIENCY_RECENCY_WEIGHT=0.2
PROFICIENCY_CONTEXT_WEIGHT=0.1
```

---

## Extraction Triggers

### Automatic Extraction

**1. Work Log Creation**
```bash
# Enabled by default
ENABLE_SKILL_EXTRACTION=true
```

When you create a work log entry, skills are automatically extracted and stored.

**2. Document Ingestion**
```bash
# Optional, can be enabled
AUTO_EXTRACT_ON_INGESTION=true
```

When you upload documents (PDFs, DOCX, etc.), skills are extracted from the content.

### Manual Extraction

**1. On-Demand Extraction**
Use the API endpoint:
```bash
curl -X POST http://localhost:8000/api/skills/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here..."}'
```

**2. Batch Re-extraction**
Re-extract skills from all existing work logs:
```bash
curl -X POST http://localhost:8000/api/skills/recalculate
```

### Extraction Frequency

**Real-time:**
- Work log creation: Immediate
- Document upload: During ingestion

**Batch:**
- Proficiency recalculation: Daily (configurable)
- Skill aggregation: On-demand

---

## Customization

### Custom Extraction Prompt

Edit `goldenverba/components/skills_extractor.py`:

```python
SKILL_EXTRACTION_PROMPT = """
You are an expert at identifying professional skills from text.

Extract all technical and professional skills from the following text.
For each skill:
1. Use the standard industry name (e.g., "JavaScript" not "JS")
2. Categorize into one of these categories: {categories}
3. Assess the usage context (basic mention vs. deep usage)
4. Provide a confidence score (0-1)

Focus on:
- Programming languages and frameworks
- Tools and technologies
- Methodologies and practices
- Soft skills and competencies

Ignore:
- Company names
- Project names
- Generic terms

Return JSON format:
{{
  "skills": [
    {{
      "name": "Python",
      "category": "Programming Languages",
      "context": "Implemented data pipeline",
      "confidence": 0.95
    }}
  ]
}}

Text: {text}
"""
```

### Skill Normalization

Handle variations and aliases:

```python
SKILL_ALIASES = {
    "JavaScript": ["JS", "Javascript", "ECMAScript", "ES6", "ES2015"],
    "PostgreSQL": ["Postgres", "psql", "PostgresSQL"],
    "Kubernetes": ["K8s", "k8s", "kube"],
    "React": ["ReactJS", "React.js"],
    "Node.js": ["NodeJS", "Node"],
    "TypeScript": ["TS"],
    "Docker": ["docker"],
    "AWS": ["Amazon Web Services"],
    "CI/CD": ["Continuous Integration", "Continuous Deployment"]
}

def normalize_skill(skill_name):
    for canonical, aliases in SKILL_ALIASES.items():
        if skill_name in aliases or skill_name == canonical:
            return canonical
    return skill_name
```

### Custom Proficiency Logic

Implement domain-specific proficiency calculation:

```python
def calculate_custom_proficiency(skill, documents):
    """
    Custom proficiency calculation for data science roles
    """
    # Base calculation
    frequency = min(len(documents) / 30, 1.0)
    recency = calculate_recency(skill.last_used)
    
    # Bonus for specific contexts
    context_bonus = 0
    for doc in documents:
        if "architected" in doc.content.lower():
            context_bonus += 0.1
        if "led team" in doc.content.lower():
            context_bonus += 0.1
        if any(metric in doc.content for metric in ["improved", "reduced", "increased"]):
            context_bonus += 0.05
    
    context = min(context_bonus, 1.0)
    
    # Weighted combination
    proficiency = (frequency * 0.5) + (recency * 0.3) + (context * 0.2)
    
    return min(proficiency, 1.0)
```

---

## Best Practices

### Writing Work Logs for Better Extraction

**Be Specific About Technologies:**
```
❌ "Worked on the backend"
✅ "Implemented REST API endpoints using FastAPI with PostgreSQL database"
```

**Include Context:**
```
❌ "Used Docker"
✅ "Containerized microservices using Docker and orchestrated with Kubernetes"
```

**Mention Depth of Usage:**
```
❌ "Worked with React"
✅ "Architected React application using hooks, context API, and custom state management"
```

**Quantify When Possible:**
```
❌ "Improved performance"
✅ "Optimized SQL queries reducing response time by 60% using indexing and query optimization"
```

### Maintaining Skill Accuracy

**Regular Updates:**
- Log work daily or weekly
- Keep work logs current
- Update old entries if you use skills again

**Review Extracted Skills:**
- Check Skills Analysis dashboard monthly
- Verify categorization is correct
- Merge duplicate skills
- Remove irrelevant skills

**Provide Feedback:**
- Note which skills are extracted incorrectly
- Adjust extraction prompt if needed
- Update skill aliases for better normalization

### Optimizing for Resume Generation

**Use Job Description Language:**
- Mirror terminology from target job postings
- Use industry-standard skill names
- Include both technical and soft skills

**Document Achievements:**
- Focus on results and impact
- Include metrics and numbers
- Describe problem-solving approaches

**Maintain Breadth and Depth:**
- Document diverse skills
- Show progression and growth
- Balance technical and soft skills

### Performance Optimization

**Reduce LLM Calls:**
```python
# Enable caching
ENABLE_SKILL_CACHE = True
CACHE_TTL_HOURS = 24

# Batch processing
SKILL_EXTRACTION_BATCH_SIZE = 10
```

**Use Efficient Models:**
```bash
# For extraction, use faster models
SKILL_EXTRACTION_MODEL=gpt-4o-mini

# For proficiency analysis, use more capable models
PROFICIENCY_ANALYSIS_MODEL=gpt-4o
```

**Optimize Extraction Frequency:**
```bash
# Don't extract from every document
AUTO_EXTRACT_ON_INGESTION=false

# Extract only from work logs
EXTRACT_FROM_WORK_LOGS_ONLY=true
```

---

## Examples

### Example 1: Software Engineer Work Log

**Input:**
```
Today I completed the user authentication feature. I implemented JWT-based 
authentication using FastAPI and integrated it with our PostgreSQL database. 
I also set up Redis for session management and wrote comprehensive unit tests 
using pytest. The feature was deployed to staging using our Docker/Kubernetes 
infrastructure and GitHub Actions CI/CD pipeline.
```

**Extracted Skills:**
```json
{
  "skills": [
    {"name": "FastAPI", "category": "Frameworks", "proficiency": 0.85},
    {"name": "JWT", "category": "Security", "proficiency": 0.78},
    {"name": "PostgreSQL", "category": "Databases", "proficiency": 0.82},
    {"name": "Redis", "category": "Databases", "proficiency": 0.75},
    {"name": "pytest", "category": "Testing Tools", "proficiency": 0.80},
    {"name": "Docker", "category": "DevOps Tools", "proficiency": 0.88},
    {"name": "Kubernetes", "category": "DevOps Tools", "proficiency": 0.83},
    {"name": "GitHub Actions", "category": "CI/CD Tools", "proficiency": 0.79}
  ]
}
```

### Example 2: Data Scientist Work Log

**Input:**
```
Built a machine learning model to predict customer churn. Used Python with 
scikit-learn for feature engineering and model training. Achieved 87% accuracy 
using Random Forest classifier. Deployed the model as a REST API using Flask 
and containerized with Docker. Created visualizations using Matplotlib and 
presented findings to stakeholders.
```

**Extracted Skills:**
```json
{
  "skills": [
    {"name": "Python", "category": "Programming Languages", "proficiency": 0.92},
    {"name": "scikit-learn", "category": "ML Frameworks", "proficiency": 0.88},
    {"name": "Machine Learning", "category": "Domain Knowledge", "proficiency": 0.90},
    {"name": "Feature Engineering", "category": "Data Science", "proficiency": 0.85},
    {"name": "Random Forest", "category": "ML Algorithms", "proficiency": 0.82},
    {"name": "Flask", "category": "Frameworks", "proficiency": 0.78},
    {"name": "Docker", "category": "DevOps Tools", "proficiency": 0.80},
    {"name": "Matplotlib", "category": "Visualization", "proficiency": 0.83},
    {"name": "Presentation Skills", "category": "Soft Skills", "proficiency": 0.75}
  ]
}
```

### Example 3: DevOps Engineer Work Log

**Input:**
```
Migrated our infrastructure to Kubernetes. Set up EKS cluster on AWS with 
Terraform. Implemented Helm charts for application deployment. Configured 
Prometheus and Grafana for monitoring. Set up automated backups using Velero. 
Reduced deployment time from 2 hours to 15 minutes. Mentored junior team 
members on Kubernetes best practices.
```

**Extracted Skills:**
```json
{
  "skills": [
    {"name": "Kubernetes", "category": "Container Orchestration", "proficiency": 0.95},
    {"name": "AWS EKS", "category": "Cloud Services", "proficiency": 0.88},
    {"name": "Terraform", "category": "Infrastructure as Code", "proficiency": 0.90},
    {"name": "Helm", "category": "DevOps Tools", "proficiency": 0.85},
    {"name": "Prometheus", "category": "Monitoring", "proficiency": 0.82},
    {"name": "Grafana", "category": "Monitoring", "proficiency": 0.80},
    {"name": "Velero", "category": "Backup Tools", "proficiency": 0.75},
    {"name": "Mentoring", "category": "Soft Skills", "proficiency": 0.78}
  ]
}
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for solutions to common skill extraction issues.

---

## Further Reading

- [User Guide](./USER_GUIDE.md) - Complete usage guide
- [Configuration Guide](./CONFIGURATION_GUIDE.md) - Detailed configuration options
- [API Reference](./API_REFERENCE.md) - API endpoints for skill management
- [Hybrid Search Guide](./HYBRID_SEARCH.md) - How skills are used in resume generation
