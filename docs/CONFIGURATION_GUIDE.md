# Configuration Guide

Complete guide to configuring the Local Resume System for optimal performance.

## Table of Contents

- [Environment Variables](#environment-variables)
- [LLM Provider Configuration](#llm-provider-configuration)
- [Resume-Specific Settings](#resume-specific-settings)
- [Skill Extraction Configuration](#skill-extraction-configuration)
- [Proficiency Calculation](#proficiency-calculation)
- [Performance Tuning](#performance-tuning)
- [Docker Configuration](#docker-configuration)

---

## Environment Variables

### Core Weaviate Settings

```bash
# Weaviate Connection
WEAVIATE_URL_VERBA=http://localhost:8080
WEAVIATE_API_KEY_VERBA=your-api-key-here

# Deployment Mode
DEFAULT_DEPLOYMENT=Local  # Options: Local, Docker, Weaviate, Custom
```

**Deployment Modes:**
- `Local`: Uses Weaviate Embedded (not supported on Windows)
- `Docker`: Connects to Weaviate in Docker network
- `Weaviate`: Connects to Weaviate Cloud Services (WCS)
- `Custom`: Custom Weaviate instance with manual URL/key

### LLM Provider Keys

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
OPENAI_EMBED_MODEL=text-embedding-3-small

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Cohere
COHERE_API_KEY=...

# Groq
GROQ_API_KEY=gsk_...

# Ollama (Local)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_EMBED_MODEL=nomic-embed-text

# Novita AI
NOVITA_API_KEY=...

# Upstage
UPSTAGE_API_KEY=...
UPSTAGE_BASE_URL=https://api.upstage.ai/v1

# VoyageAI (Embeddings)
VOYAGE_API_KEY=...
```

### Resume-Specific Variables

```bash
# Skill Extraction
ENABLE_SKILL_EXTRACTION=true
SKILL_EXTRACTION_MODEL=gpt-4o-mini
SKILL_EXTRACTION_PROVIDER=OpenAI
AUTO_EXTRACT_ON_INGESTION=true

# Resume Generation
RESUME_GENERATION_MODEL=gpt-4o
RESUME_GENERATION_PROVIDER=OpenAI
DEFAULT_RESUME_FORMAT=pdf
MAX_CONVERSATION_HISTORY=10

# Proficiency Calculation
PROFICIENCY_FREQUENCY_WEIGHT=0.6
PROFICIENCY_RECENCY_WEIGHT=0.3
PROFICIENCY_CONTEXT_WEIGHT=0.1

# Hybrid Search
HYBRID_SEARCH_ALPHA=0.5
ENABLE_RECENCY_BOOST=true
RECENCY_BOOST_FACTOR=1.2
MAX_WORK_LOGS_PER_RESUME=50
```

### Data Ingestion

```bash
# Unstructured.io
UNSTRUCTURED_API_KEY=...
UNSTRUCTURED_API_URL=https://api.unstructuredapp.io/general/v0/general

# AssemblyAI (Audio)
ASSEMBLYAI_API_KEY=...

# GitHub/GitLab
GITHUB_TOKEN=ghp_...
GITLAB_TOKEN=glpat-...

# Firecrawl (Web Scraping)
FIRECRAWL_API_KEY=...
```

### Application Settings

```bash
# System Prompt
SYSTEM_MESSAGE_PROMPT="You are Verba, a professional resume assistant..."

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
```

---

## LLM Provider Configuration

### OpenAI

**Recommended Models:**
- Skill Extraction: `gpt-4o-mini` (fast, cost-effective)
- Resume Generation: `gpt-4o` (best quality)
- Embeddings: `text-embedding-3-small` (good balance)

**Configuration:**
```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
OPENAI_EMBED_MODEL=text-embedding-3-small
```

**Custom Endpoints:**
For LiteLLM or other proxies:
```bash
OPENAI_BASE_URL=http://localhost:4000
OPENAI_EMBED_BASE_URL=http://localhost:4000
OPENAI_CUSTOM_EMBED=true
```

**Cost Optimization:**
- Use `gpt-4o-mini` for skill extraction (10x cheaper)
- Use `gpt-4o` only for final resume generation
- Cache embeddings to reduce API calls

### Anthropic (Claude)

**Recommended Models:**
- Skill Extraction: `claude-3-haiku-20240307`
- Resume Generation: `claude-3-5-sonnet-20241022`

**Configuration:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
SKILL_EXTRACTION_MODEL=claude-3-haiku-20240307
RESUME_GENERATION_MODEL=claude-3-5-sonnet-20241022
```

**Advantages:**
- Excellent at following instructions
- Strong context understanding
- Good for creative resume writing

### Ollama (Local)

**Recommended Models:**
- Skill Extraction: `llama3:8b` or `mistral`
- Resume Generation: `llama3:70b` or `mixtral:8x7b`
- Embeddings: `nomic-embed-text`

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3:70b
ollama pull nomic-embed-text

# Configure
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3:70b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

**Docker Configuration:**
```bash
# For Docker deployment
OLLAMA_URL=http://host.docker.internal:11434

# For Linux Docker
OLLAMA_URL=http://172.17.0.1:11434
```

**Advantages:**
- Completely free
- Full privacy (no data leaves your machine)
- No API rate limits

**Considerations:**
- Requires significant compute (GPU recommended)
- Slower than cloud APIs
- Quality depends on model size

### Cohere

**Recommended Models:**
- Generation: `command-r-plus`
- Embeddings: `embed-english-v3.0`

**Configuration:**
```bash
COHERE_API_KEY=...
RESUME_GENERATION_MODEL=command-r-plus
```

**Advantages:**
- Good multilingual support
- Strong retrieval capabilities
- Competitive pricing

### Groq

**Recommended Models:**
- `llama-3.1-70b-versatile` (best quality)
- `llama-3.1-8b-instant` (fastest)

**Configuration:**
```bash
GROQ_API_KEY=gsk_...
RESUME_GENERATION_MODEL=llama-3.1-70b-versatile
```

**Advantages:**
- Extremely fast inference (LPU technology)
- Free tier available
- Good quality with Llama models

**Limitations:**
- No embedding models
- Rate limits on free tier

---

## Resume-Specific Settings

### Skill Extraction

**Enable/Disable:**
```bash
ENABLE_SKILL_EXTRACTION=true
```

**Model Selection:**
```bash
SKILL_EXTRACTION_MODEL=gpt-4o-mini
SKILL_EXTRACTION_PROVIDER=OpenAI
```

**Provider Options:**
- `OpenAI`: Best accuracy, moderate cost
- `Anthropic`: Excellent quality, higher cost
- `Cohere`: Good balance
- `Ollama`: Free, requires local setup

**Auto-Extract on Ingestion:**
```bash
AUTO_EXTRACT_ON_INGESTION=true
```
- `true`: Extract skills from all uploaded documents automatically
- `false`: Extract skills only from work logs or on-demand

**Skill Categories:**
Customize in `goldenverba/components/skills_extractor.py`:
```python
SKILL_CATEGORIES = [
    "Programming Languages",
    "Frameworks",
    "Databases",
    "Cloud Services",
    "DevOps Tools",
    "Soft Skills",
    "Domain Knowledge"
]
```

### Resume Generation

**Model Configuration:**
```bash
RESUME_GENERATION_MODEL=gpt-4o
RESUME_GENERATION_PROVIDER=OpenAI
```

**Default Format:**
```bash
DEFAULT_RESUME_FORMAT=pdf  # Options: pdf, docx, markdown
```

**Default Sections:**
Configure in UI or via code:
```python
DEFAULT_SECTIONS = [
    "summary",
    "experience",
    "skills",
    "education"
]
```

**Conversation History:**
```bash
MAX_CONVERSATION_HISTORY=10
```
- Higher values: More context for refinement, higher token usage
- Lower values: Less context, lower cost
- Recommended: 10 for good balance

**System Prompt:**
Customize the resume generation behavior:
```bash
SYSTEM_MESSAGE_PROMPT="You are a professional resume writer with expertise in ATS optimization and career coaching. Generate concise, impactful resumes that highlight relevant experience and skills for the target role."
```

---

## Skill Extraction Configuration

### Extraction Prompt

Customize in `goldenverba/components/skills_extractor.py`:

```python
SKILL_EXTRACTION_PROMPT = """
Extract technical and professional skills from the following text.
Categorize each skill into one of these categories:
- Programming Languages
- Frameworks
- Databases
- Cloud Services
- DevOps Tools
- Soft Skills

Return a JSON array of skills with their categories.
"""
```

### Skill Categorization

**Predefined Categories:**
Edit the category list to match your domain:

```python
# For software engineers
SKILL_CATEGORIES = [
    "Programming Languages",
    "Frameworks",
    "Databases",
    "Cloud Services",
    "DevOps Tools",
    "Testing Tools",
    "Soft Skills"
]

# For data scientists
SKILL_CATEGORIES = [
    "Programming Languages",
    "ML Frameworks",
    "Data Tools",
    "Visualization",
    "Statistics",
    "Domain Knowledge",
    "Soft Skills"
]
```

### Caching

Enable caching to reduce LLM calls:

```python
# In skills_extractor.py
ENABLE_SKILL_CACHE = True
CACHE_TTL_HOURS = 24
```

---

## Proficiency Calculation

### Weight Configuration

```bash
PROFICIENCY_FREQUENCY_WEIGHT=0.6
PROFICIENCY_RECENCY_WEIGHT=0.3
PROFICIENCY_CONTEXT_WEIGHT=0.1
```

**Weights must sum to 1.0**

### Calculation Formula

```
Proficiency = (Frequency × 0.6) + (Recency × 0.3) + (Context × 0.1)
```

**Components:**

1. **Frequency Score:**
   - Based on number of occurrences
   - Normalized to 0-1 scale
   - Formula: `min(occurrences / 50, 1.0)`

2. **Recency Score:**
   - Based on days since last use
   - Exponential decay
   - Formula: `exp(-days_since_use / 180)`

3. **Context Score:**
   - Based on depth of usage description
   - Analyzed by LLM
   - Scale: 0-1

### Customization Examples

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

## Performance Tuning

### Hybrid Search Configuration

```bash
# Alpha parameter (0 = keyword only, 1 = semantic only)
HYBRID_SEARCH_ALPHA=0.5

# Recency boost
ENABLE_RECENCY_BOOST=true
RECENCY_BOOST_FACTOR=1.2

# Maximum work logs to retrieve
MAX_WORK_LOGS_PER_RESUME=50
```

**Alpha Tuning:**
- `0.3-0.4`: Emphasize keyword matching (good for technical roles)
- `0.5`: Balanced (recommended default)
- `0.6-0.7`: Emphasize semantic similarity (good for creative roles)

See [HYBRID_SEARCH.md](./HYBRID_SEARCH.md) for detailed tuning guide.

### Chunking Strategy

Configure in UI under Config → Chunking:

**For Work Logs:**
- Strategy: Sentence-based
- Chunk size: 200-300 tokens
- Overlap: 50 tokens

**For Technical Documents:**
- Strategy: Semantic
- Chunk size: 400-500 tokens
- Overlap: 100 tokens

**For Resumes:**
- Strategy: Token-based
- Chunk size: 500 tokens
- Overlap: 50 tokens

### Embedding Configuration

**Batch Size:**
```python
EMBEDDING_BATCH_SIZE = 100
```

**Caching:**
```python
ENABLE_EMBEDDING_CACHE = True
```

### Database Optimization

**Weaviate Settings:**
```yaml
# In docker-compose.yml
environment:
  QUERY_DEFAULTS_LIMIT: 100
  PERSISTENCE_DATA_PATH: /var/lib/weaviate
  ENABLE_MODULES: text2vec-openai,generative-openai
```

---

## Docker Configuration

### Basic Setup

```yaml
# docker-compose.yml
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
      ENABLE_MODULES: 'text2vec-openai,generative-openai'
      OPENAI_APIKEY: ${OPENAI_API_KEY}
    volumes:
      - weaviate_data:/var/lib/weaviate

  verba:
    build: .
    ports:
      - "8000:8000"
    environment:
      WEAVIATE_URL_VERBA: http://weaviate:8080
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ENABLE_SKILL_EXTRACTION: 'true'
      SKILL_EXTRACTION_MODEL: gpt-4o-mini
      RESUME_GENERATION_MODEL: gpt-4o
    depends_on:
      - weaviate
    volumes:
      - ./data:/app/data

volumes:
  weaviate_data:
```

### Environment File

Create `.env` file:
```bash
# Copy from .env.example
cp .env.example .env

# Edit with your keys
nano .env
```

### Deploy

```bash
docker compose --env-file .env up -d --build
```

See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for complete Docker configuration guide.

---

## Configuration Best Practices

### Security

1. **Never commit API keys to version control**
   ```bash
   # Add to .gitignore
   .env
   .env.local
   ```

2. **Use environment-specific files**
   ```bash
   .env.development
   .env.production
   ```

3. **Rotate keys regularly**
   - Set calendar reminders
   - Use key management services
   - Monitor usage for anomalies

### Cost Optimization

1. **Use cheaper models for extraction**
   ```bash
   SKILL_EXTRACTION_MODEL=gpt-4o-mini
   ```

2. **Enable caching**
   ```python
   ENABLE_SKILL_CACHE=True
   ENABLE_EMBEDDING_CACHE=True
   ```

3. **Limit conversation history**
   ```bash
   MAX_CONVERSATION_HISTORY=5
   ```

4. **Use local models when possible**
   ```bash
   OLLAMA_URL=http://localhost:11434
   ```

### Performance

1. **Optimize chunk sizes**
   - Smaller chunks: Better precision, more API calls
   - Larger chunks: More context, fewer API calls

2. **Tune hybrid search alpha**
   - Test different values for your use case
   - Monitor retrieval quality

3. **Use appropriate batch sizes**
   ```python
   EMBEDDING_BATCH_SIZE=100
   ```

### Reliability

1. **Set up health checks**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Monitor logs**
   ```bash
   LOG_LEVEL=INFO
   ```

3. **Backup data regularly**
   ```bash
   # Backup Weaviate data
   docker cp verba-weaviate-1:/var/lib/weaviate ./backup
   ```

---

## Troubleshooting Configuration

### Common Issues

**Issue: "Weaviate connection failed"**
```bash
# Check Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# Verify URL in config
echo $WEAVIATE_URL_VERBA
```

**Issue: "OpenAI API key invalid"**
```bash
# Test key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Issue: "Skill extraction not working"**
```bash
# Verify settings
echo $ENABLE_SKILL_EXTRACTION
echo $SKILL_EXTRACTION_MODEL

# Check logs
docker logs verba-verba-1
```

**Issue: "Resume generation slow"**
```bash
# Use faster model
RESUME_GENERATION_MODEL=gpt-4o-mini

# Reduce conversation history
MAX_CONVERSATION_HISTORY=5

# Limit work logs retrieved
MAX_WORK_LOGS_PER_RESUME=30
```

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for more solutions.
