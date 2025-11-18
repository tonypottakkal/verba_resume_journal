# Schema Extensions for Resume Features

This document describes the Weaviate schema extensions added to support resume generation and work log management features.

## Overview

The `schema_extensions.py` module defines three new Weaviate collections that extend the base Verba functionality:

1. **WorkLog** - Stores work log entries created by users
2. **Skill** - Stores extracted skills with proficiency scores
3. **ResumeRecord** - Stores generated resumes with associated job descriptions

## Collections

### VERBA_WorkLog

Stores work log entries that document daily work activities and accomplishments.

**Properties:**
- `content` (TEXT): The work log entry content
- `timestamp` (DATE): When the work log entry was created
- `user_id` (TEXT): User who created the work log entry
- `extracted_skills` (TEXT_ARRAY): Skills extracted from the work log content
- `metadata` (OBJECT): Additional metadata for the work log entry

**Vectorization:** Configurable (default: none)

**Use Cases:**
- Chat-based work log entry creation
- Skill extraction from daily activities
- Source material for resume generation

### VERBA_Skill

Stores extracted skills with proficiency scores and occurrence tracking.

**Properties:**
- `name` (TEXT): The skill name
- `category` (TEXT): The skill category (e.g., programming, framework, tool)
- `proficiency_score` (NUMBER): Calculated proficiency score for the skill
- `occurrence_count` (INT): Number of times the skill appears in documents
- `source_documents` (TEXT_ARRAY): UUIDs of documents where this skill was found
- `last_used` (DATE): Most recent date the skill was mentioned

**Vectorization:** None (used for aggregation and filtering)

**Use Cases:**
- Skills analysis and visualization
- Proficiency tracking over time
- Resume content selection based on required skills

### VERBA_ResumeRecord

Stores generated resumes with their associated job descriptions for tracking and regeneration.

**Properties:**
- `resume_content` (TEXT): The generated resume content
- `job_description` (TEXT): The job description used to generate the resume
- `target_role` (TEXT): The target job role for this resume
- `generated_at` (DATE): When the resume was generated
- `format` (TEXT): The resume format (markdown, pdf, docx)
- `source_log_ids` (TEXT_ARRAY): UUIDs of work log entries used to generate this resume
- `metadata` (OBJECT): Additional metadata for the resume record

**Vectorization:** Configurable (default: none)

**Use Cases:**
- Resume history tracking
- Resume regeneration with updated data
- Job application tracking

## Initialization

The schema extensions are automatically initialized when connecting to Weaviate through the VerbaManager:

```python
from goldenverba.verba_manager import VerbaManager
from goldenverba.server.types import Credentials

manager = VerbaManager()
credentials = Credentials(deployment="Local", url="", key="")
client = await manager.connect(credentials)
# Collections are automatically created if they don't exist
```

## Manual Initialization

You can also manually initialize the collections:

```python
from goldenverba.components.schema_extensions import SchemaExtensions
from weaviate.classes.config import Configure

schema_extensions = SchemaExtensions()

# Initialize all collections
await schema_extensions.initialize_all_collections(client)

# Or initialize individual collections with custom vectorizer
vectorizer_config = Configure.Vectorizer.text2vec_openai()
await schema_extensions.verify_worklog_collection(client, vectorizer_config)
```

## Collection Management

### Verify Individual Collections

```python
# Verify WorkLog collection
await schema_extensions.verify_worklog_collection(client)

# Verify Skill collection
await schema_extensions.verify_skill_collection(client)

# Verify ResumeRecord collection
await schema_extensions.verify_resume_record_collection(client)
```

### Delete All Collections

**Warning:** This will permanently delete all data in the resume-specific collections!

```python
await schema_extensions.delete_all_collections(client)
```

## Integration with VerbaManager

The SchemaExtensions class is integrated into VerbaManager and automatically initializes collections during the connection process:

```python
# In verba_manager.py
class VerbaManager:
    def __init__(self):
        # ... other managers ...
        self.schema_extensions = SchemaExtensions()
    
    async def connect(self, credentials, port="8080"):
        client = await self.weaviate_manager.connect(...)
        if client:
            # Initialize resume-specific collections
            await self.schema_extensions.initialize_all_collections(client)
        return client
```

## Requirements Mapping

This implementation satisfies the following requirements from the design document:

- **Requirement 11.2**: WorkLog collection for storing work log entries
- **Requirement 12.3**: ResumeRecord collection for storing generated resumes
- **Requirement 12.4**: Job description storage within ResumeRecord
- **Requirement 13.1**: Resume history tracking through ResumeRecord collection

## Future Enhancements

Potential improvements to the schema:

1. Add cross-references between collections using Weaviate references
2. Implement custom vectorizers for semantic search on work logs
3. Add versioning support for resume records
4. Implement soft delete functionality
5. Add user authentication and multi-tenancy support
