# API Reference

Complete reference for all Local Resume System API endpoints.

## Table of Contents

- [Work Log Management](#work-log-management)
- [Skills Analysis](#skills-analysis)
- [Resume Generation](#resume-generation)
- [Resume History](#resume-history)
- [Configuration](#configuration)

---

## Work Log Management

### Create Work Log Entry

Create a new work log entry with automatic skill extraction.

**Endpoint:** `POST /api/worklogs`

**Request Body:**
```json
{
  "content": "Today I implemented a new authentication system using JWT tokens and Redis for session management. Also optimized the database queries using proper indexing.",
  "user_id": "user123",
  "metadata": {
    "project": "auth-service",
    "tags": ["backend", "security"]
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "wl_abc123",
  "content": "Today I implemented a new authentication system...",
  "timestamp": "2025-11-11T10:30:00Z",
  "user_id": "user123",
  "extracted_skills": ["JWT", "Redis", "Database Optimization", "Indexing"],
  "metadata": {
    "project": "auth-service",
    "tags": ["backend", "security"]
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request body or missing required fields
- `500 Internal Server Error` - Server error during processing

---

### List Work Log Entries

Retrieve work log entries with optional filtering.

**Endpoint:** `GET /api/worklogs`

**Query Parameters:**
- `user_id` (optional) - Filter by user ID
- `start_date` (optional) - Filter entries after this date (ISO 8601 format)
- `end_date` (optional) - Filter entries before this date (ISO 8601 format)
- `limit` (optional) - Maximum number of entries to return (default: 50)
- `offset` (optional) - Number of entries to skip (default: 0)

**Example Request:**
```
GET /api/worklogs?user_id=user123&start_date=2025-11-01&limit=20
```

**Response:** `200 OK`
```json
{
  "entries": [
    {
      "id": "wl_abc123",
      "content": "Today I implemented...",
      "timestamp": "2025-11-11T10:30:00Z",
      "user_id": "user123",
      "extracted_skills": ["JWT", "Redis"],
      "metadata": {}
    }
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

---

### Update Work Log Entry

Update an existing work log entry.

**Endpoint:** `PUT /api/worklogs/{id}`

**Request Body:**
```json
{
  "content": "Updated content with new information about the implementation.",
  "metadata": {
    "project": "auth-service",
    "tags": ["backend", "security", "completed"]
  }
}
```

**Response:** `200 OK`
```json
{
  "id": "wl_abc123",
  "content": "Updated content...",
  "timestamp": "2025-11-11T10:30:00Z",
  "user_id": "user123",
  "extracted_skills": ["Implementation", "Backend"],
  "metadata": {
    "project": "auth-service",
    "tags": ["backend", "security", "completed"]
  }
}
```

**Error Responses:**
- `404 Not Found` - Work log entry not found
- `400 Bad Request` - Invalid request body

---

### Delete Work Log Entry

Delete a work log entry and associated skills.

**Endpoint:** `DELETE /api/worklogs/{id}`

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found` - Work log entry not found

---

## Skills Analysis

### Get Skills Breakdown

Retrieve aggregated skills data with proficiency scores.

**Endpoint:** `GET /api/skills`

**Query Parameters:**
- `start_date` (optional) - Filter skills used after this date
- `end_date` (optional) - Filter skills used before this date
- `category` (optional) - Filter by skill category
- `min_proficiency` (optional) - Minimum proficiency score (0-1)

**Example Request:**
```
GET /api/skills?start_date=2025-01-01&category=programming
```

**Response:** `200 OK`
```json
{
  "categories": [
    {
      "name": "Programming Languages",
      "skills": [
        {
          "name": "Python",
          "proficiency_score": 0.92,
          "occurrence_count": 45,
          "source_documents": ["wl_abc123", "wl_def456"],
          "last_used": "2025-11-11T10:30:00Z"
        },
        {
          "name": "JavaScript",
          "proficiency_score": 0.85,
          "occurrence_count": 38,
          "source_documents": ["wl_ghi789"],
          "last_used": "2025-11-10T14:20:00Z"
        }
      ]
    },
    {
      "name": "Frameworks",
      "skills": [
        {
          "name": "React",
          "proficiency_score": 0.88,
          "occurrence_count": 32,
          "source_documents": ["wl_jkl012"],
          "last_used": "2025-11-09T09:15:00Z"
        }
      ]
    }
  ],
  "total_skills": 15,
  "date_range": {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-11-11T23:59:59Z"
  }
}
```

---

### Get Skill Categories

Retrieve all available skill categories.

**Endpoint:** `GET /api/skills/categories`

**Response:** `200 OK`
```json
{
  "categories": [
    "Programming Languages",
    "Frameworks",
    "Databases",
    "Cloud Services",
    "DevOps Tools",
    "Soft Skills"
  ]
}
```

---

### Extract Skills from Text

Perform on-demand skill extraction from arbitrary text.

**Endpoint:** `POST /api/skills/extract`

**Request Body:**
```json
{
  "text": "I have experience with React, Node.js, PostgreSQL, and AWS Lambda. I've also worked extensively with Docker and Kubernetes for container orchestration."
}
```

**Response:** `200 OK`
```json
{
  "skills": [
    {
      "name": "React",
      "category": "Frameworks",
      "confidence": 0.95
    },
    {
      "name": "Node.js",
      "category": "Programming Languages",
      "confidence": 0.93
    },
    {
      "name": "PostgreSQL",
      "category": "Databases",
      "confidence": 0.97
    },
    {
      "name": "AWS Lambda",
      "category": "Cloud Services",
      "confidence": 0.91
    },
    {
      "name": "Docker",
      "category": "DevOps Tools",
      "confidence": 0.96
    },
    {
      "name": "Kubernetes",
      "category": "DevOps Tools",
      "confidence": 0.94
    }
  ]
}
```

---

## Resume Generation

### Generate Resume

Generate a tailored resume based on a job description.

**Endpoint:** `POST /api/resumes/generate`

**Request Body:**
```json
{
  "job_description": "We are looking for a Senior Backend Engineer with 5+ years of experience in Python, FastAPI, and PostgreSQL. Experience with AWS and Docker is required. The ideal candidate will have strong system design skills and experience building scalable APIs.",
  "options": {
    "format": "markdown",
    "sections": ["summary", "experience", "skills", "education"],
    "max_length": 2000,
    "tone": "professional"
  },
  "user_id": "user123"
}
```

**Response:** `200 OK`
```json
{
  "id": "resume_xyz789",
  "content": "# John Doe\n\n## Professional Summary\n\nSenior Backend Engineer with 6+ years of experience...",
  "job_description_id": "jd_abc123",
  "target_role": "Senior Backend Engineer",
  "generated_at": "2025-11-11T11:00:00Z",
  "format": "markdown",
  "source_log_ids": ["wl_abc123", "wl_def456", "wl_ghi789"],
  "metadata": {
    "model_used": "gpt-4o",
    "generation_time_ms": 3450
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid job description or options
- `422 Unprocessable Entity` - Insufficient work log data to generate resume
- `500 Internal Server Error` - Generation failed

---

### List Resume History

Retrieve all generated resumes with metadata.

**Endpoint:** `GET /api/resumes`

**Query Parameters:**
- `user_id` (optional) - Filter by user ID
- `start_date` (optional) - Filter resumes generated after this date
- `end_date` (optional) - Filter resumes generated before this date
- `target_role` (optional) - Filter by target role
- `limit` (optional) - Maximum number of resumes to return (default: 20)
- `offset` (optional) - Number of resumes to skip (default: 0)

**Response:** `200 OK`
```json
{
  "resumes": [
    {
      "id": "resume_xyz789",
      "target_role": "Senior Backend Engineer",
      "generated_at": "2025-11-11T11:00:00Z",
      "format": "markdown",
      "job_description_preview": "We are looking for a Senior Backend Engineer...",
      "source_log_count": 3
    }
  ],
  "total": 12,
  "limit": 20,
  "offset": 0
}
```

---

### Get Resume by ID

Retrieve a specific resume with full content.

**Endpoint:** `GET /api/resumes/{id}`

**Response:** `200 OK`
```json
{
  "id": "resume_xyz789",
  "content": "# John Doe\n\n## Professional Summary...",
  "job_description": "We are looking for a Senior Backend Engineer...",
  "target_role": "Senior Backend Engineer",
  "generated_at": "2025-11-11T11:00:00Z",
  "format": "markdown",
  "source_log_ids": ["wl_abc123", "wl_def456"],
  "metadata": {}
}
```

**Error Responses:**
- `404 Not Found` - Resume not found

---

### Regenerate Resume

Regenerate a resume using the same job description with updated work log data.

**Endpoint:** `POST /api/resumes/{id}/regenerate`

**Request Body:**
```json
{
  "options": {
    "format": "pdf",
    "sections": ["summary", "experience", "skills"],
    "max_length": 1500
  }
}
```

**Response:** `200 OK`
```json
{
  "id": "resume_new123",
  "content": "...",
  "job_description_id": "jd_abc123",
  "target_role": "Senior Backend Engineer",
  "generated_at": "2025-11-11T12:00:00Z",
  "format": "pdf",
  "source_log_ids": ["wl_abc123", "wl_def456", "wl_xyz999"],
  "metadata": {
    "regenerated_from": "resume_xyz789"
  }
}
```

---

### Delete Resume

Delete a resume from history.

**Endpoint:** `DELETE /api/resumes/{id}`

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found` - Resume not found

---

### Export Resume

Export a resume in a specific format (PDF, DOCX, or Markdown).

**Endpoint:** `POST /api/resumes/{id}/export`

**Request Body:**
```json
{
  "format": "pdf"
}
```

**Response:** `200 OK`
- Content-Type: `application/pdf` (for PDF)
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (for DOCX)
- Content-Type: `text/markdown` (for Markdown)
- Content-Disposition: `attachment; filename="resume_xyz789.pdf"`

Binary file content in response body.

**Error Responses:**
- `404 Not Found` - Resume not found
- `400 Bad Request` - Invalid format specified

---

## Configuration

### Get Resume Configuration

Retrieve current resume-specific configuration.

**Endpoint:** `GET /api/config/resume`

**Response:** `200 OK`
```json
{
  "skill_extraction": {
    "enabled": true,
    "model": "gpt-4o-mini",
    "provider": "OpenAI",
    "auto_extract_on_ingestion": true
  },
  "resume_generation": {
    "model": "gpt-4o",
    "provider": "OpenAI",
    "default_format": "markdown",
    "default_sections": ["summary", "experience", "skills", "education"],
    "max_conversation_history": 10
  },
  "proficiency_calculation": {
    "frequency_weight": 0.6,
    "recency_weight": 0.3,
    "context_weight": 0.1
  }
}
```

---

### Update Resume Configuration

Update resume-specific configuration settings.

**Endpoint:** `POST /api/config/resume`

**Request Body:**
```json
{
  "skill_extraction": {
    "enabled": true,
    "model": "gpt-4o-mini",
    "provider": "OpenAI"
  },
  "resume_generation": {
    "model": "gpt-4o",
    "provider": "Anthropic",
    "default_format": "pdf"
  }
}
```

**Response:** `200 OK`
```json
{
  "message": "Configuration updated successfully",
  "config": {
    "skill_extraction": {
      "enabled": true,
      "model": "gpt-4o-mini",
      "provider": "OpenAI",
      "auto_extract_on_ingestion": true
    },
    "resume_generation": {
      "model": "gpt-4o",
      "provider": "Anthropic",
      "default_format": "pdf",
      "default_sections": ["summary", "experience", "skills", "education"],
      "max_conversation_history": 10
    }
  }
}
```

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context about the error"
  }
}
```

### Common Error Codes

- `INVALID_REQUEST` - Request body or parameters are invalid
- `NOT_FOUND` - Requested resource does not exist
- `SKILL_EXTRACTION_FAILED` - Skill extraction process failed
- `RESUME_GENERATION_FAILED` - Resume generation process failed
- `INSUFFICIENT_DATA` - Not enough work log data to generate resume
- `LLM_ERROR` - Error communicating with LLM provider
- `DATABASE_ERROR` - Error accessing Weaviate database
- `EXPORT_FAILED` - Resume export process failed

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- Work Log endpoints: 100 requests per minute
- Skills endpoints: 50 requests per minute
- Resume generation: 10 requests per minute
- Export endpoints: 20 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699876543
```

---

## Authentication

Currently, the Local Resume System does not require authentication for local deployments. For production deployments, consider implementing:

- API key authentication
- OAuth 2.0 integration
- JWT token-based authentication

Future versions may include built-in authentication mechanisms.
