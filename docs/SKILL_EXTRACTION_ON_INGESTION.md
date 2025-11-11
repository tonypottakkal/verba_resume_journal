# Skill Extraction on Document Ingestion

## Overview

This document describes the automatic skill extraction feature that runs as a post-processing hook during document ingestion.

## Implementation

### 1. Post-Processing Hook

When documents are ingested into Verba, a post-processing hook automatically extracts skills from the document content and stores them in the Skill collection.

**Location**: `goldenverba/verba_manager.py` - `_extract_skills_from_document()` method

**Trigger**: After each document is successfully imported to Weaviate

**Process**:
1. Combines document metadata and chunk content
2. Truncates to 10,000 characters to avoid token limits
3. Uses the configured LLM generator to extract skills
4. Categorizes extracted skills into predefined categories
5. Stores or updates skills in the Skill collection with document references

### 2. Skill Cleanup on Document Deletion

When documents are deleted, the system automatically cleans up associated skills.

**Location**: `goldenverba/components/managers.py` - `_cleanup_document_skills()` method

**Process**:
1. Finds all skills that reference the deleted document
2. Removes the document reference from each skill's `source_documents` list
3. Decrements the `occurrence_count` for each skill
4. Deletes skills that have no remaining document references

## Configuration

### Environment Variables

- `ENABLE_SKILL_EXTRACTION`: Set to `"true"` (default) to enable automatic skill extraction, `"false"` to disable

### Requirements

- A configured LLM generator (OpenAI, Ollama, etc.)
- The Skill collection must be initialized (handled automatically by schema_extensions)

## Skill Categories

Skills are automatically categorized into the following predefined categories:

- `programming_languages`: Python, JavaScript, Java, etc.
- `frameworks`: React, Django, Flask, etc.
- `databases`: PostgreSQL, MongoDB, Redis, etc.
- `cloud_platforms`: AWS, Azure, GCP, etc.
- `devops_tools`: Docker, Kubernetes, Jenkins, etc.
- `data_science`: Machine Learning, NLP, etc.
- `soft_skills`: Leadership, Communication, etc.
- `tools`: Git, VS Code, Jira, etc.
- `other`: Skills that don't fit predefined categories

## Data Flow

```
Document Upload
    ↓
Document Reading (Reader)
    ↓
Document Chunking (Chunker)
    ↓
Chunk Embedding (Embedder)
    ↓
Document Import to Weaviate
    ↓
[NEW] Skill Extraction Hook ← You are here
    ├─ Extract skills from document text
    ├─ Categorize skills
    ├─ Store/update skills in Skill collection
    └─ Link skills to source document
    ↓
Import Complete
```

## Skill Storage

Each skill is stored with the following properties:

- `name`: The skill name (e.g., "Python", "Docker")
- `category`: The skill category
- `proficiency_score`: Calculated based on frequency and recency (0.0 - 1.0)
- `occurrence_count`: Number of times the skill appears across documents
- `source_documents`: List of document UUIDs that reference this skill
- `last_used`: Timestamp of the most recent document containing this skill

## Performance Considerations

1. **Text Truncation**: Document text is truncated to 10,000 characters to avoid LLM token limits
2. **Caching**: Skill extraction results are cached to reduce redundant LLM calls
3. **Async Processing**: Skill extraction runs asynchronously and doesn't block document import
4. **Error Handling**: Skill extraction failures don't cause document import to fail

## Usage

### Automatic Extraction

Skills are automatically extracted when:
- New documents are uploaded via the Import interface
- Documents are ingested via the API
- Work logs are created (if they go through the document ingestion pipeline)

### Manual Extraction

Skills can also be extracted manually via the API:
```
POST /api/skills/extract
{
  "text": "Your text content here"
}
```

## Troubleshooting

### Skills Not Being Extracted

1. Check that `ENABLE_SKILL_EXTRACTION=true` in your environment
2. Verify that a generator is configured in RAG settings
3. Check logs for skill extraction errors (warnings won't fail the import)

### Skills Not Deleted When Document Removed

1. Verify that the document UUID is correct
2. Check that the Skill collection exists
3. Review logs for cleanup errors

## Future Enhancements

- Support for custom skill categories
- Configurable text truncation limits
- Batch skill extraction for multiple documents
- Skill proficiency recalculation on document updates
