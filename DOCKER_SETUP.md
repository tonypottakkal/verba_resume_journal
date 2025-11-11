# Docker Deployment Guide

This guide explains how to deploy the Local Resume System using Docker Compose.

## Prerequisites

- Docker Engine 20.10 or later
- Docker Compose 2.0 or later
- At least 4GB of available RAM
- 10GB of free disk space

## Quick Start

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your API keys in `.env`:**
   Edit the `.env` file and add your API keys for the LLM providers you want to use:
   ```bash
   # Required for OpenAI
   OPENAI_API_KEY=sk-...
   
   # Optional: For local LLM execution
   OLLAMA_URL=http://host.docker.internal:11434
   OLLAMA_MODEL=llama3.1
   ```

3. **Start the services:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:8000`

## Environment Variables

### Core Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WEAVIATE_URL_VERBA` | Weaviate database URL | `http://weaviate:8080` | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | For OpenAI models |
| `COHERE_API_KEY` | Cohere API key | - | For Cohere models |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | For Claude models |

### Resume-Specific Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SKILL_EXTRACTION_MODEL` | Model for skill extraction | `gpt-4o-mini` | No |
| `SKILL_EXTRACTION_PROVIDER` | Provider for skill extraction | `OpenAI` | No |
| `RESUME_GENERATION_MODEL` | Model for resume generation | `gpt-4o` | No |
| `RESUME_GENERATION_PROVIDER` | Provider for resume generation | `OpenAI` | No |
| `DEFAULT_RESUME_FORMAT` | Default export format | `pdf` | No |
| `MAX_CONVERSATION_HISTORY` | Max conversation exchanges | `10` | No |

### Ollama Configuration (Local LLMs)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OLLAMA_URL` | Ollama server URL | `http://host.docker.internal:11434` | For Ollama |
| `OLLAMA_MODEL` | Ollama model for generation | `llama3.1` | For Ollama |
| `OLLAMA_EMBED_MODEL` | Ollama embedding model | `nomic-embed-text` | For Ollama |

## Volume Mounts

The Docker Compose configuration creates the following volumes:

- **`weaviate_data`**: Persists Weaviate vector database data
- **`resume_exports`**: Stores generated resume files (PDF, DOCX)
- **`./data`**: Mounted to `/data/` for document uploads

## Services

### Verba Application
- **Port**: 8000
- **Health Check**: HTTP GET on `http://localhost:8000`
- **Dependencies**: Weaviate

### Weaviate Vector Database
- **Ports**: 8080 (API), 3000 (alternative)
- **Health Check**: HTTP GET on `http://localhost:8080/v1/.well-known/ready`
- **Persistence**: `/var/lib/weaviate`

### Ollama (Optional)
Uncomment the `ollama` service in `docker-compose.yml` to run Ollama within Docker:
```yaml
ollama:
  image: ollama/ollama:latest
  ports:
    - 7869:11434
  volumes:
    - ./ollama/ollama:/root/.ollama
```

## Common Operations

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f verba
docker-compose logs -f weaviate
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart verba
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Data
```bash
# WARNING: This deletes all data including documents and resumes
docker-compose down -v
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

## Troubleshooting

### Service Won't Start
1. Check logs: `docker-compose logs verba`
2. Verify environment variables in `.env`
3. Ensure ports 8000 and 8080 are not in use

### Weaviate Connection Issues
1. Wait for Weaviate health check to pass (can take 30-60 seconds)
2. Check Weaviate logs: `docker-compose logs weaviate`
3. Verify `WEAVIATE_URL_VERBA` is set correctly

### Out of Memory
1. Increase Docker memory limit to at least 4GB
2. Consider using smaller models (e.g., `gpt-4o-mini` instead of `gpt-4o`)

### Resume Export Fails
1. Verify the `resume_exports` volume is mounted correctly
2. Check write permissions: `docker-compose exec verba ls -la /Verba/exports`
3. Review application logs for PDF/DOCX generation errors

## Using Local Models with Ollama

To use Ollama for completely local operation:

1. **Install Ollama on your host machine:**
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull required models:**
   ```bash
   ollama pull llama3.1
   ollama pull nomic-embed-text
   ```

3. **Configure environment variables:**
   ```bash
   SKILL_EXTRACTION_PROVIDER=Ollama
   RESUME_GENERATION_PROVIDER=Ollama
   OLLAMA_MODEL=llama3.1
   OLLAMA_EMBED_MODEL=nomic-embed-text
   ```

4. **Start services:**
   ```bash
   docker-compose up -d
   ```

## Production Deployment

For production deployments:

1. **Use secrets management** instead of `.env` files
2. **Enable authentication** on Weaviate
3. **Configure HTTPS** with a reverse proxy (nginx, Traefik)
4. **Set up backups** for the `weaviate_data` volume
5. **Monitor resource usage** and scale as needed
6. **Use specific image tags** instead of `latest`

## Data Persistence

All data is persisted in Docker volumes:
- Documents and embeddings: `weaviate_data`
- Generated resumes: `resume_exports`
- Uploaded files: `./data` (host directory)

To backup your data:
```bash
# Backup Weaviate data
docker run --rm -v local_resume_weaviate_data:/data -v $(pwd):/backup ubuntu tar czf /backup/weaviate_backup.tar.gz /data

# Backup resume exports
docker run --rm -v local_resume_resume_exports:/data -v $(pwd):/backup ubuntu tar czf /backup/resumes_backup.tar.gz /data
```

## Support

For issues and questions:
- Check the main README.md
- Review application logs
- Verify environment configuration
- Ensure all required API keys are set
