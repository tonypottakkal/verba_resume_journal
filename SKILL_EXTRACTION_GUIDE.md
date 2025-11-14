# Skill Extraction Guide

## Overview

The system now automatically extracts skills from documents using AI. Skills are extracted in two ways:

1. **Automatically when you upload new documents** - Skills are extracted during the document ingestion process
2. **On-demand from existing documents** - Use the bulk extraction endpoint to process documents that were uploaded before this feature was implemented

## How It Works

### Automatic Extraction (New Uploads)

When you upload a document through the Import tab:
1. The document is processed and stored in Weaviate
2. The text content is analyzed using the configured LLM (Ollama by default)
3. Skills are automatically extracted and categorized
4. Skills are stored in the Skills collection with metadata

### Manual Extraction (Existing Documents)

For documents that were uploaded before skill extraction was implemented, you can trigger bulk extraction:

**API Endpoint:**
```bash
POST /api/skills/extract-from-documents
```

**Request Body:**
```json
{
  "limit": 100,  // Maximum number of documents to process (optional, default: 100)
  "credentials": {}  // Optional credentials
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/skills/extract-from-documents" \
  -H "Content-Type: application/json" \
  -d '{"limit": 100}'
```

**Response:**
```json
{
  "success": true,
  "documents_processed": 5,
  "skills_extracted": 47,
  "failed_documents": [],
  "message": "Successfully extracted 47 skills from 5 documents"
}
```

## Configuration

Skills extraction is configured in your `.env` file:

```bash
# Enable/disable skill extraction
ENABLE_SKILL_EXTRACTION=true

# LLM model to use for extraction
SKILL_EXTRACTION_MODEL=qwen2.5:7b-instruct
SKILL_EXTRACTION_PROVIDER=Ollama

# Automatically extract on document upload
AUTO_EXTRACT_ON_INGESTION=true
```

## Skill Categories

Skills are automatically categorized into:

- **Programming Languages**: Python, JavaScript, TypeScript, Java, etc.
- **Frameworks**: React, Django, FastAPI, Spring, etc.
- **Databases**: PostgreSQL, MongoDB, Redis, Weaviate, etc.
- **Cloud Platforms**: AWS, Azure, GCP, etc.
- **DevOps Tools**: Docker, Kubernetes, Jenkins, etc.
- **Data Science**: Machine Learning, NLP, Computer Vision, etc.
- **Soft Skills**: Leadership, Communication, Problem Solving, etc.
- **Tools**: Git, VS Code, Jira, etc.
- **Other**: Skills that don't fit the above categories

## Viewing Skills

Once skills are extracted, you can view them in the **Skills** tab:

1. Navigate to the Skills tab in the UI
2. View skills grouped by category
3. See proficiency scores based on frequency and recency
4. Filter by date range or category
5. Export skills data as JSON or CSV

## Proficiency Scoring

Skills are scored based on:

- **Frequency** (60%): How often the skill appears across documents
- **Recency** (30%): How recently the skill was used
- **Context Diversity** (10%): Number of different documents mentioning the skill

Proficiency scores range from 0.0 to 1.0:
- **0.8-1.0**: Expert
- **0.6-0.8**: Advanced
- **0.4-0.6**: Intermediate
- **0.0-0.4**: Beginner

## Troubleshooting

### No Skills Extracted

**Problem**: The bulk extraction returns 0 skills.

**Possible Causes:**
1. No documents have been uploaded yet
2. LLM is not configured properly
3. Documents don't contain enough text

**Solutions:**
1. Upload documents through the Import tab
2. Check that Ollama is running: `curl http://localhost:11434/api/tags`
3. Verify the LLM model is available: `ollama list`
4. Check the Docker logs: `docker-compose logs verba`

### Extraction Fails

**Problem**: Bulk extraction returns errors.

**Possible Causes:**
1. LLM connection issues
2. Insufficient memory
3. Documents are too large

**Solutions:**
1. Check Ollama is accessible from Docker container
2. Reduce the `limit` parameter to process fewer documents at once
3. Check Docker logs for specific error messages

### Skills Not Showing in UI

**Problem**: Skills are extracted but don't appear in the Skills tab.

**Possible Causes:**
1. Date filter is too restrictive
2. Skills collection not initialized
3. Browser cache issues

**Solutions:**
1. Reset date filters in the Skills tab
2. Refresh the browser (Ctrl+F5 or Cmd+Shift+R)
3. Check the browser console for errors
4. Restart the Docker containers

## Next Steps

1. **Upload your resume documents** through the Import tab
2. **Trigger bulk extraction** using the API endpoint or wait for a UI button (coming soon)
3. **View your skills** in the Skills tab
4. **Generate tailored resumes** using the Resume tab with your extracted skills

## API Reference

### Extract Skills from All Documents

```
POST /api/skills/extract-from-documents
```

**Request:**
```json
{
  "limit": 100,
  "credentials": {
    "deployment": "Local",
    "url": "",
    "key": ""
  }
}
```

**Response:**
```json
{
  "error": "",
  "success": true,
  "documents_processed": 10,
  "skills_extracted": 85,
  "failed_documents": [],
  "message": "Successfully extracted 85 skills from 10 documents"
}
```

### Get Skills Breakdown

```
POST /api/skills
```

**Request:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "category": null
}
```

**Response:**
```json
{
  "error": "",
  "skills_by_category": {
    "programming_languages": [
      {
        "name": "Python",
        "proficiency_score": 0.85,
        "occurrence_count": 15,
        "last_used": "2024-11-14T21:00:00Z"
      }
    ]
  },
  "total_skills": 47,
  "top_skills": [...],
  "recent_skills": [...]
}
```

## Support

For issues or questions:
1. Check the Docker logs: `docker-compose logs verba`
2. Review this guide
3. Check the GitHub repository issues
