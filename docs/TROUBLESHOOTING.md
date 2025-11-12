# Troubleshooting Guide

Solutions to common issues when using the Local Resume System.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Connection Problems](#connection-problems)
- [Skill Extraction Issues](#skill-extraction-issues)
- [Resume Generation Problems](#resume-generation-problems)
- [Performance Issues](#performance-issues)
- [Data Issues](#data-issues)
- [Docker Issues](#docker-issues)

---

## Installation Issues

### Python Version Incompatibility

**Problem:** `ERROR: Python version not supported`

**Solution:**
```bash
# Check Python version
python --version

# Must be Python 3.10, 3.11, or 3.12
# Install correct version if needed
pyenv install 3.11.0
pyenv local 3.11.0
```

### Pip Installation Fails

**Problem:** `ERROR: Could not install packages due to an EnvironmentError`

**Solution:**
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install Verba
pip install goldenverba
```

### Missing Dependencies

**Problem:** `ModuleNotFoundError: No module named 'weaviate'`

**Solution:**
```bash
# Reinstall with all dependencies
pip install --force-reinstall goldenverba

# Or install from source
git clone https://github.com/weaviate/Verba.git
cd Verba
pip install -e .
```

---

## Connection Problems

### Weaviate Connection Failed

**Problem:** `Could not connect to Weaviate at http://localhost:8080`

**Diagnosis:**
```bash
# Check if Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# Check Docker containers
docker ps | grep weaviate
```

**Solutions:**

**For Local Deployment:**
```bash
# Weaviate Embedded should start automatically
# If it fails, check logs
verba start --log-level DEBUG
```

**For Docker Deployment:**
```bash
# Start Weaviate container
docker compose up -d weaviate

# Check logs
docker logs verba-weaviate-1

# Verify network
docker network ls
docker network inspect verba_default
```

**For Cloud Deployment:**
```bash
# Verify WCS cluster is running
# Check URL and API key in .env
echo $WEAVIATE_URL_VERBA
echo $WEAVIATE_API_KEY_VERBA

# Test connection
curl -H "Authorization: Bearer $WEAVIATE_API_KEY_VERBA" \
  $WEAVIATE_URL_VERBA/v1/.well-known/ready
```

### LLM Provider Connection Issues

**Problem:** `OpenAI API Error: Invalid API key`

**Solution:**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Update .env file
nano .env
# Add: OPENAI_API_KEY=sk-...

# Restart application
verba start
```

**Problem:** `Ollama connection refused`

**Solution:**
```bash
# Check Ollama is running
ollama list

# Start Ollama service
ollama serve

# Verify URL
echo $OLLAMA_URL
# Should be: http://localhost:11434

# For Docker, use host.docker.internal
OLLAMA_URL=http://host.docker.internal:11434
```

### Port Already in Use

**Problem:** `Error: Port 8000 is already in use`

**Solution:**
```bash
# Find process using port
lsof -i :8000  # On macOS/Linux
netstat -ano | findstr :8000  # On Windows

# Kill process
kill -9 <PID>

# Or use different port
verba start --port 8001
```

---

## Skill Extraction Issues

### Skills Not Being Extracted

**Problem:** Work logs created but no skills extracted

**Diagnosis:**
```bash
# Check if skill extraction is enabled
echo $ENABLE_SKILL_EXTRACTION

# Check logs for errors
docker logs verba-verba-1 | grep skill

# Verify LLM provider is configured
echo $SKILL_EXTRACTION_MODEL
echo $SKILL_EXTRACTION_PROVIDER
```

**Solutions:**

1. **Enable skill extraction:**
```bash
# In .env file
ENABLE_SKILL_EXTRACTION=true
AUTO_EXTRACT_ON_INGESTION=true
```

2. **Configure LLM provider:**
```bash
SKILL_EXTRACTION_MODEL=gpt-4o-mini
SKILL_EXTRACTION_PROVIDER=OpenAI
OPENAI_API_KEY=sk-...
```

3. **Check API quota:**
```bash
# OpenAI quota exceeded
# Solution: Wait for quota reset or upgrade plan

# Use alternative provider
SKILL_EXTRACTION_PROVIDER=Ollama
OLLAMA_URL=http://localhost:11434
```

### Incorrect Skill Categorization

**Problem:** Skills assigned to wrong categories

**Solution:**

1. **Update skill categories:**
Edit `goldenverba/components/skills_extractor.py`:
```python
SKILL_CATEGORIES = [
    "Programming Languages",
    "Frameworks",
    "Databases",
    # Add your custom categories
]
```

2. **Improve extraction prompt:**
```python
SKILL_EXTRACTION_PROMPT = """
Extract skills and categorize them accurately.
Use these exact categories: [list categories]
Be specific about technical skills vs soft skills.
"""
```

3. **Use better model:**
```bash
# Switch to more capable model
SKILL_EXTRACTION_MODEL=gpt-4o
```

### Duplicate Skills

**Problem:** Same skill appears multiple times with different names

**Solution:**

1. **Implement skill normalization:**
Edit `goldenverba/components/skills_extractor.py`:
```python
SKILL_ALIASES = {
    "JavaScript": ["JS", "Javascript", "ECMAScript"],
    "PostgreSQL": ["Postgres", "psql"],
    "Kubernetes": ["K8s", "k8s"]
}
```

2. **Manual cleanup:**
```bash
# Use Skills Analysis UI
# Merge duplicate skills
# Update work logs with normalized names
```

---

## Resume Generation Problems

### Resume Generation Fails

**Problem:** `ERROR: Resume generation failed`

**Diagnosis:**
```bash
# Check logs
docker logs verba-verba-1 | grep resume

# Verify work logs exist
curl http://localhost:8000/api/worklogs

# Check LLM provider
echo $RESUME_GENERATION_MODEL
echo $RESUME_GENERATION_PROVIDER
```

**Solutions:**

1. **Insufficient work log data:**
```
Error: "Not enough work log data to generate resume"

Solution:
- Add more work log entries
- Ensure work logs contain relevant skills
- Check that work logs are being indexed
```

2. **LLM API error:**
```bash
# Check API key
echo $OPENAI_API_KEY

# Verify quota
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Use alternative provider
RESUME_GENERATION_PROVIDER=Anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

3. **Job description too long:**
```
Error: "Token limit exceeded"

Solution:
- Shorten job description
- Focus on key requirements
- Increase model context window
```

### Poor Resume Quality

**Problem:** Generated resume doesn't match job description well

**Solutions:**

1. **Tune hybrid search:**
```bash
# Adjust alpha for better retrieval
HYBRID_SEARCH_ALPHA=0.6  # More semantic
# or
HYBRID_SEARCH_ALPHA=0.4  # More keyword-based
```

2. **Increase work logs retrieved:**
```bash
MAX_WORK_LOGS_PER_RESUME=75
```

3. **Use better model:**
```bash
RESUME_GENERATION_MODEL=gpt-4o
# or
RESUME_GENERATION_MODEL=claude-3-5-sonnet-20241022
```

4. **Improve work log quality:**
- Add more specific details
- Include relevant technologies
- Quantify accomplishments
- Use keywords from job descriptions

### Export Fails

**Problem:** `ERROR: Failed to export resume as PDF`

**Diagnosis:**
```bash
# Check if export libraries are installed
pip list | grep reportlab
pip list | grep python-docx

# Check logs
docker logs verba-verba-1 | grep export
```

**Solutions:**

1. **Install missing dependencies:**
```bash
pip install reportlab python-docx
```

2. **Use alternative format:**
```bash
# If PDF fails, try DOCX
# If DOCX fails, use Markdown
```

3. **Check file permissions:**
```bash
# Ensure export directory is writable
chmod 755 ./data/exports
```

---

## Performance Issues

### Slow Resume Generation

**Problem:** Resume generation takes >60 seconds

**Solutions:**

1. **Use faster model:**
```bash
RESUME_GENERATION_MODEL=gpt-4o-mini
# or
RESUME_GENERATION_MODEL=llama-3.1-8b-instant  # Groq
```

2. **Reduce work logs retrieved:**
```bash
MAX_WORK_LOGS_PER_RESUME=30
```

3. **Optimize hybrid search:**
```bash
# Reduce search time
HYBRID_SEARCH_LIMIT=20
```

4. **Enable caching:**
```python
# In resume_generator.py
ENABLE_RESUME_CACHE=True
```

### Slow Skill Extraction

**Problem:** Skill extraction takes too long

**Solutions:**

1. **Use faster model:**
```bash
SKILL_EXTRACTION_MODEL=gpt-4o-mini
```

2. **Batch processing:**
```python
# Process multiple work logs together
SKILL_EXTRACTION_BATCH_SIZE=10
```

3. **Disable auto-extraction:**
```bash
AUTO_EXTRACT_ON_INGESTION=false
# Extract skills on-demand instead
```

### High Memory Usage

**Problem:** Application uses excessive memory

**Solutions:**

1. **Limit embedding cache:**
```python
EMBEDDING_CACHE_SIZE=1000
```

2. **Reduce chunk size:**
```bash
# In Config UI
Chunk size: 300 tokens (instead of 500)
```

3. **Use smaller embedding model:**
```bash
OPENAI_EMBED_MODEL=text-embedding-3-small
```

4. **Restart periodically:**
```bash
# For Docker
docker compose restart verba
```

---

## Data Issues

### Work Logs Not Appearing

**Problem:** Created work logs don't show up in UI

**Diagnosis:**
```bash
# Check if data was saved
curl http://localhost:8000/api/worklogs

# Check Weaviate
curl http://localhost:8080/v1/objects?class=WorkLog
```

**Solutions:**

1. **Refresh the page:**
```bash
# Clear browser cache
# Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

2. **Check indexing:**
```bash
# Verify Weaviate schema
curl http://localhost:8080/v1/schema

# Reindex if needed
# Delete and recreate work log
```

3. **Check user_id:**
```bash
# Ensure user_id is consistent
# Check filter settings in UI
```

### Skills Not Updating

**Problem:** Proficiency scores don't change after adding work logs

**Solutions:**

1. **Trigger recalculation:**
```bash
# API endpoint to recalculate
curl -X POST http://localhost:8000/api/skills/recalculate
```

2. **Check date filters:**
```bash
# Ensure date range includes new work logs
# Remove date filters to see all skills
```

3. **Clear cache:**
```bash
# Restart application
docker compose restart verba
```

### Resume History Missing

**Problem:** Previously generated resumes disappeared

**Diagnosis:**
```bash
# Check Weaviate data
curl http://localhost:8080/v1/objects?class=ResumeRecord

# Check Docker volumes
docker volume ls
docker volume inspect verba_weaviate_data
```

**Solutions:**

1. **Restore from backup:**
```bash
# If you have backups
docker cp ./backup/weaviate verba-weaviate-1:/var/lib/weaviate
docker compose restart weaviate
```

2. **Check deployment mode:**
```bash
# Ensure using persistent storage
# In docker-compose.yml:
volumes:
  - weaviate_data:/var/lib/weaviate
```

---

## Docker Issues

### Container Won't Start

**Problem:** `ERROR: Container verba-verba-1 exited with code 1`

**Diagnosis:**
```bash
# Check logs
docker logs verba-verba-1

# Check container status
docker ps -a

# Inspect container
docker inspect verba-verba-1
```

**Solutions:**

1. **Environment variables missing:**
```bash
# Verify .env file exists
ls -la .env

# Check variables are loaded
docker compose config
```

2. **Port conflicts:**
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

3. **Rebuild containers:**
```bash
docker compose down
docker compose up -d --build
```

### Volume Permission Issues

**Problem:** `Permission denied: '/var/lib/weaviate'`

**Solutions:**

1. **Fix permissions:**
```bash
# On Linux
sudo chown -R 1000:1000 ./weaviate_data

# Or use Docker user
docker compose run --user root verba chown -R 1000:1000 /var/lib/weaviate
```

2. **Use named volumes:**
```yaml
# In docker-compose.yml
volumes:
  weaviate_data:
    driver: local
```

### Network Issues

**Problem:** Containers can't communicate

**Diagnosis:**
```bash
# Check network
docker network ls
docker network inspect verba_default

# Test connectivity
docker exec verba-verba-1 ping weaviate
```

**Solutions:**

1. **Recreate network:**
```bash
docker compose down
docker network prune
docker compose up -d
```

2. **Use explicit network:**
```yaml
# In docker-compose.yml
networks:
  verba_network:
    driver: bridge

services:
  weaviate:
    networks:
      - verba_network
  verba:
    networks:
      - verba_network
```

---

## Getting Help

If you can't resolve your issue:

1. **Check Documentation:**
   - [User Guide](./USER_GUIDE.md)
   - [Configuration Guide](./CONFIGURATION_GUIDE.md)
   - [API Reference](./API_REFERENCE.md)

2. **Search GitHub Issues:**
   - Check if issue already reported
   - Look for similar problems and solutions

3. **Create GitHub Issue:**
   - Provide detailed description
   - Include error messages and logs
   - Specify environment (OS, Python version, deployment mode)
   - Include configuration (without API keys)

4. **Community Support:**
   - Weaviate Community Forum
   - Discord server
   - Stack Overflow (tag: weaviate, verba)

---

## Diagnostic Commands

### System Information

```bash
# Python version
python --version

# Pip packages
pip list

# Docker version
docker --version
docker compose version

# System resources
free -h  # Memory
df -h    # Disk space
```

### Application Status

```bash
# Check Verba
curl http://localhost:8000/api/health

# Check Weaviate
curl http://localhost:8080/v1/.well-known/ready

# Check Ollama
curl http://localhost:11434/api/tags
```

### Logs

```bash
# Verba logs
docker logs verba-verba-1 --tail 100

# Weaviate logs
docker logs verba-weaviate-1 --tail 100

# Follow logs
docker logs -f verba-verba-1
```

### Data Inspection

```bash
# List work logs
curl http://localhost:8000/api/worklogs | jq

# List skills
curl http://localhost:8000/api/skills | jq

# List resumes
curl http://localhost:8000/api/resumes | jq

# Weaviate schema
curl http://localhost:8080/v1/schema | jq
```
