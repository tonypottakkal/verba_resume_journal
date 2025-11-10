# Design Document

## Overview

The Local Resume System is built on the Verba RAG framework, extending it with specialized resume generation and skills analysis capabilities from Super-people-local. The architecture follows a three-tier design: a Next.js frontend, a FastAPI backend, and a Weaviate vector database. The system preserves all Verba's document processing, RAG querying, and multi-LLM support while adding new modules for work log management, skills extraction, and resume generation with tracking.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  ┌──────────┬──────────┬──────────┬──────────┬───────────┐ │
│  │   Chat   │  Import  │  Skills  │  Resume  │  History  │ │
│  │   (RAG)  │   Data   │ Analysis │   Gen    │  Tracking │ │
│  └──────────┴──────────┴──────────┴──────────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Verba Manager (Core)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────┬──────────┬──────────┬──────────────────────┐ │
│  │ Document │   RAG    │  Skills  │  Resume Generation   │ │
│  │ Ingestion│ Pipeline │ Extractor│     & Tracking       │ │
│  └──────────┴──────────┴──────────┴──────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Component Managers (Verba Core)               │  │
│  │  • Embedding Manager  • Generation Manager            │  │
│  │  • Chunking Manager   • Retriever Manager             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Weaviate Client
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Weaviate Vector Database                    │
│  ┌──────────────┬──────────────┬──────────────────────────┐│
│  │   Documents  │  Work Logs   │  Resumes & Job Descs     ││
│  │   (Chunks)   │  (Entries)   │     (Tracking)           ││
│  └──────────────┴──────────────┴──────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- Next.js 14 (from Verba)
- React 18
- TailwindCSS + DaisyUI
- React Three Fiber (3D visualizations)
- TypeScript

**Backend:**
- FastAPI (from Verba)
- Python 3.10+
- Weaviate Python Client
- OpenAI SDK
- Pydantic for data validation

**Database:**
- Weaviate (vector database)
- Embedded mode for local deployment
- Docker deployment option

**Deployment:**
- Docker Compose
- Environment-based configuration

## Components and Interfaces

### Frontend Components

#### 1. Navigation and Layout
- **MainLayout**: Extends Verba's layout with additional navigation tabs
- **TabNavigation**: Manages routing between Chat, Import, Skills, Resume, and History views
- **Sidebar**: Retains Verba's configuration and settings panel

#### 2. Existing Verba Components (Retained)
- **ChatInterface**: RAG-based document querying
- **ImportInterface**: Multi-format document upload
- **ConfigInterface**: LLM provider and chunking configuration
- **VectorViewer**: 3D visualization of document embeddings

#### 3. New Resume-Specific Components

**WorkLogChat Component**
```typescript
interface WorkLogChatProps {
  onLogSubmit: (content: string) => Promise<void>;
  logs: WorkLogEntry[];
}

interface WorkLogEntry {
  id: string;
  content: string;
  timestamp: Date;
  skills: string[];
}
```
- Chat-style interface for creating work log entries
- Real-time skill extraction preview
- Edit/delete functionality for existing logs

**SkillsAnalysis Component**
```typescript
interface SkillsAnalysisProps {
  skills: SkillCategory[];
  timeRange: DateRange;
  onFilterChange: (filters: SkillFilters) => void;
}

interface SkillCategory {
  name: string;
  skills: Skill[];
}

interface Skill {
  name: string;
  proficiency: number;
  occurrences: number;
  sources: string[];
}
```
- Interactive skill breakdown visualization
- Category-based grouping
- Proficiency scoring display
- Time-based filtering

**ResumeGenerator Component**
```typescript
interface ResumeGeneratorProps {
  onGenerate: (jobDescription: string, options: ResumeOptions) => Promise<Resume>;
}

interface ResumeOptions {
  format: 'pdf' | 'docx' | 'markdown';
  sections: string[];
  maxLength: number;
}

interface Resume {
  id: string;
  content: string;
  jobDescriptionId: string;
  generatedAt: Date;
}
```
- Job description input area
- Resume generation options
- Real-time preview
- Export functionality

**ResumeHistory Component**
```typescript
interface ResumeHistoryProps {
  resumes: ResumeRecord[];
  onSelect: (id: string) => void;
  onRegenerate: (id: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

interface ResumeRecord {
  id: string;
  jobDescription: string;
  resume: Resume;
  targetRole: string;
  generatedAt: Date;
}
```
- List view of all generated resumes
- Associated job description display
- Regeneration and export options

### Backend Components

#### 1. Verba Core (Retained)
- **VerbaManager**: Central orchestration class
- **ComponentManagers**: Embedding, Generation, Chunking, Retrieval
- **Document/Chunk Models**: Core data structures

#### 2. New Resume Modules

**WorkLogManager**
```python
class WorkLogManager:
    def create_log_entry(self, content: str, user_id: str) -> WorkLogEntry:
        """Create and store a work log entry"""
        
    def get_log_entries(self, filters: dict) -> List[WorkLogEntry]:
        """Retrieve work log entries with filtering"""
        
    def update_log_entry(self, log_id: str, content: str) -> WorkLogEntry:
        """Update existing work log entry"""
        
    def delete_log_entry(self, log_id: str) -> bool:
        """Delete a work log entry"""
```

**SkillsExtractor**
```python
class SkillsExtractor:
    def extract_skills(self, text: str) -> List[Skill]:
        """Extract skills from text using LLM"""
        
    def categorize_skills(self, skills: List[Skill]) -> Dict[str, List[Skill]]:
        """Group skills into categories"""
        
    def calculate_proficiency(self, skill: str, documents: List[str]) -> float:
        """Calculate proficiency score based on usage"""
        
    def aggregate_skills(self, time_range: DateRange) -> SkillsReport:
        """Generate comprehensive skills report"""
```

**ResumeGenerator**
```python
class ResumeGenerator:
    def generate_resume(
        self, 
        job_description: str, 
        work_logs: List[WorkLogEntry],
        options: ResumeOptions
    ) -> Resume:
        """Generate tailored resume from job description"""
        
    def extract_job_requirements(self, job_description: str) -> JobRequirements:
        """Parse job description for requirements"""
        
    def retrieve_relevant_experiences(
        self, 
        requirements: JobRequirements
    ) -> List[WorkLogEntry]:
        """Find matching work experiences"""
        
    def format_resume(self, content: str, format: str) -> bytes:
        """Export resume in specified format"""
```

**ResumeTracker**
```python
class ResumeTracker:
    def save_resume_record(
        self, 
        resume: Resume, 
        job_description: str
    ) -> ResumeRecord:
        """Store resume with associated job description"""
        
    def get_resume_history(self, filters: dict) -> List[ResumeRecord]:
        """Retrieve resume generation history"""
        
    def get_resume_by_id(self, resume_id: str) -> ResumeRecord:
        """Get specific resume record"""
        
    def delete_resume_record(self, resume_id: str) -> bool:
        """Remove resume from history"""
```

### API Endpoints

#### Existing Verba Endpoints (Retained)
- `POST /api/query` - RAG query execution
- `POST /api/import` - Document upload
- `GET /api/documents` - List documents
- `POST /api/config` - Update configuration
- `GET /api/health` - Health check

#### New Resume Endpoints

```python
# Work Log Management
POST   /api/worklogs              # Create work log entry
GET    /api/worklogs              # List work log entries
PUT    /api/worklogs/{id}         # Update work log entry
DELETE /api/worklogs/{id}         # Delete work log entry

# Skills Analysis
GET    /api/skills                # Get skills breakdown
GET    /api/skills/categories     # Get skill categories
POST   /api/skills/extract        # Extract skills from text

# Resume Generation
POST   /api/resumes/generate      # Generate new resume
GET    /api/resumes               # List resume history
GET    /api/resumes/{id}          # Get specific resume
POST   /api/resumes/{id}/regenerate  # Regenerate resume
DELETE /api/resumes/{id}          # Delete resume
POST   /api/resumes/{id}/export   # Export resume (PDF/DOCX)

# Job Descriptions
POST   /api/job-descriptions      # Store job description
GET    /api/job-descriptions/{id} # Get job description
```

## Data Models

### Weaviate Schema Extensions

#### WorkLog Collection
```python
{
    "class": "WorkLog",
    "properties": [
        {"name": "content", "dataType": ["text"]},
        {"name": "timestamp", "dataType": ["date"]},
        {"name": "user_id", "dataType": ["string"]},
        {"name": "extracted_skills", "dataType": ["string[]"]},
        {"name": "metadata", "dataType": ["object"]}
    ],
    "vectorizer": "text2vec-openai"  # or configured embedder
}
```

#### Skill Collection
```python
{
    "class": "Skill",
    "properties": [
        {"name": "name", "dataType": ["string"]},
        {"name": "category", "dataType": ["string"]},
        {"name": "proficiency_score", "dataType": ["number"]},
        {"name": "occurrence_count", "dataType": ["int"]},
        {"name": "source_documents", "dataType": ["string[]"]},
        {"name": "last_used", "dataType": ["date"]}
    ]
}
```

#### ResumeRecord Collection
```python
{
    "class": "ResumeRecord",
    "properties": [
        {"name": "resume_content", "dataType": ["text"]},
        {"name": "job_description", "dataType": ["text"]},
        {"name": "target_role", "dataType": ["string"]},
        {"name": "generated_at", "dataType": ["date"]},
        {"name": "format", "dataType": ["string"]},
        {"name": "source_log_ids", "dataType": ["string[]"]},
        {"name": "metadata", "dataType": ["object"]}
    ],
    "vectorizer": "text2vec-openai"
}
```

### Python Data Models

```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict

class WorkLogEntry(BaseModel):
    id: str
    content: str
    timestamp: datetime
    user_id: str
    extracted_skills: List[str]
    metadata: Dict[str, any]

class Skill(BaseModel):
    name: str
    category: str
    proficiency_score: float
    occurrence_count: int
    source_documents: List[str]
    last_used: datetime

class JobRequirements(BaseModel):
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str
    role_description: str

class Resume(BaseModel):
    id: str
    content: str
    format: str
    generated_at: datetime

class ResumeRecord(BaseModel):
    id: str
    resume: Resume
    job_description: str
    target_role: str
    source_log_ids: List[str]
    metadata: Dict[str, any]

class ResumeOptions(BaseModel):
    format: str = "markdown"
    sections: List[str] = ["summary", "experience", "skills", "education"]
    max_length: int = 2000
    tone: str = "professional"
```

## Error Handling

### Frontend Error Handling
- Display user-friendly error messages using toast notifications
- Implement retry logic for failed API calls
- Graceful degradation when features are unavailable
- Loading states for async operations

### Backend Error Handling
```python
class ResumeGenerationError(Exception):
    """Raised when resume generation fails"""

class SkillExtractionError(Exception):
    """Raised when skill extraction fails"""

class WorkLogNotFoundError(Exception):
    """Raised when work log entry doesn't exist"""

# Error response format
{
    "error": {
        "code": "RESUME_GENERATION_FAILED",
        "message": "Failed to generate resume",
        "details": "Insufficient work log data for target role"
    }
}
```

### Error Recovery Strategies
1. **LLM Failures**: Fallback to alternative providers if configured
2. **Database Errors**: Retry with exponential backoff
3. **Validation Errors**: Return detailed field-level errors
4. **Rate Limiting**: Queue requests and notify user of delays

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies (Weaviate, LLM APIs)
- Focus on business logic in managers and extractors
- Target 80% code coverage for new modules

### Integration Tests
- Test API endpoints end-to-end
- Verify Weaviate schema creation and queries
- Test document ingestion pipeline
- Validate resume generation workflow

### Component Tests (Frontend)
- Test React components with React Testing Library
- Verify user interactions and state management
- Test form validation and submission
- Snapshot testing for UI consistency

### End-to-End Tests
- Test complete user workflows:
  - Upload work logs → Extract skills → Generate resume
  - Create log entry via chat → View in skills analysis
  - Generate resume → View in history → Export
- Use Playwright or Cypress for browser automation

### Performance Tests
- Measure document ingestion speed
- Test concurrent resume generation requests
- Verify vector search response times
- Monitor memory usage during large document processing

### Test Data
- Sample work logs with varied content
- Example job descriptions for different roles
- Mock LLM responses for consistent testing
- Pre-embedded test documents for retrieval testing

## Configuration Management

### Environment Variables
```bash
# Weaviate Configuration
WEAVIATE_URL_VERBA=http://localhost:8080
WEAVIATE_API_KEY_VERBA=

# LLM Providers
OPENAI_API_KEY=
OLLAMA_URL=http://localhost:11434
COHERE_API_KEY=
ANTHROPIC_API_KEY=

# Application Settings
DEFAULT_DEPLOYMENT=Local
SYSTEM_MESSAGE_PROMPT="You are a professional resume assistant..."
MAX_WORK_LOGS_PER_RESUME=50
SKILL_EXTRACTION_MODEL=gpt-4
RESUME_GENERATION_MODEL=gpt-4

# Feature Flags
ENABLE_SKILL_EXTRACTION=true
ENABLE_RESUME_TRACKING=true
ENABLE_PDF_EXPORT=true
```

### Runtime Configuration
- User-selectable LLM providers via UI
- Configurable chunking strategies
- Adjustable retrieval parameters (top_k, similarity threshold)
- Resume generation options (format, length, tone)

## Deployment Architecture

### Docker Compose Deployment
```yaml
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
      - PERSISTENCE_DATA_PATH=/var/lib/weaviate
    volumes:
      - weaviate_data:/var/lib/weaviate
      
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - WEAVIATE_URL_VERBA=http://weaviate:8080
    depends_on:
      - weaviate
    volumes:
      - ./data:/app/data
      
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### Local Development
- Weaviate Embedded for simplified setup
- Hot reload for frontend and backend
- Separate environment files for dev/prod

## Security Considerations

1. **API Key Management**: Store keys in environment variables, never in code
2. **Data Privacy**: All data stored locally by default
3. **Input Validation**: Sanitize all user inputs to prevent injection attacks
4. **Rate Limiting**: Implement rate limits on API endpoints
5. **Authentication**: Optional user authentication for multi-user deployments (future enhancement)

## Performance Optimization

1. **Caching**: Cache frequently accessed skills and resume templates
2. **Batch Processing**: Process multiple work logs in parallel
3. **Lazy Loading**: Load resume history on demand
4. **Vector Index Optimization**: Use appropriate Weaviate index settings
5. **Async Operations**: Use async/await for I/O-bound operations

## Code Integration Strategy

### From Verba (Base Framework)
- Use Verba's complete codebase as the foundation
- Retain all existing features: RAG chat, document import, vector visualization
- Extend the FastAPI backend with new endpoints
- Add new tabs to the Next.js frontend

### From Super-people-local (Feature Integration)
- Adapt the skills extraction logic from `services/weaviate.ts` and `services/resume.ts`
- Port the work log chat interface concept from `components/ChatInput.tsx`
- Integrate the skills visualization approach from `components/SkillsBreakdown.tsx`
- Adapt the resume generation workflow logic
- Convert React/Vite components to Next.js compatible components
- Translate TypeScript service logic to Python backend modules

### Integration Approach
1. Copy Verba project structure to `local_resume/`
2. Create new Python modules for work log management, skills extraction, and resume generation
3. Add new Weaviate collections for WorkLog, Skill, and ResumeRecord
4. Extend Verba's frontend with new page components for Skills, Resume Generation, and History
5. Implement new API endpoints in the existing FastAPI application
6. Update Docker configuration to include new environment variables
