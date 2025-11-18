# Documentation Index

Complete documentation for the Local Resume System - an AI-powered professional development platform built on Verba's RAG framework.

## 📚 Documentation Structure

### Getting Started

Start here if you're new to the system:

- **[User Guide](./USER_GUIDE.md)** - Complete guide to using all features
- **[Docker Setup](./DOCKER_SETUP.md)** - Deploy with Docker Compose
- **[Configuration Guide](./CONFIGURATION_GUIDE.md)** - LLM providers, settings, and optimization
- **[Troubleshooting](./TROUBLESHOOTING.md)** - Solutions to common issues

### Feature Documentation

Learn about specific features:

- **[Skill Extraction Guide](./SKILL_EXTRACTION_GUIDE.md)** - Understanding automatic skill extraction and proficiency scoring
- **[Skill Extraction on Ingestion](./SKILL_EXTRACTION_ON_INGESTION.md)** - How skills are extracted during document upload
- **[Testing Skill Extraction](./TESTING_SKILL_EXTRACTION.md)** - Testing and validating skill extraction
- **[Hybrid Search](./HYBRID_SEARCH.md)** - How resume generation retrieves relevant experiences
- **[Metadata Filtering](./METADATA_FILTERING_IMPLEMENTATION.md)** - Document organization and filtering

### API Documentation

For developers and integrators:

- **[API Reference](./API_REFERENCE.md)** - Complete REST API documentation
- **[Work Log API Implementation](./WORKLOG_API_IMPLEMENTATION.md)** - Work log management system details
- **[Python Tutorial](./PYTHON_TUTORIAL.md)** - Using the Python SDK

### Architecture & Implementation

Deep dives into the system:

- **[Verba Codebase Guide](./VERBA_CODEBASE_GUIDE.md)** - Understanding Verba's architecture
- **[Verba UI Guide](./VERBA_UI_AND_IMPLEMENTATION_GUIDE.md)** - Frontend architecture and components
- **[Schema Extensions](./SCHEMA_EXTENSIONS.md)** - Resume-specific Weaviate collections
- **[Technical Documentation](./TECHNICAL.md)** - Core Verba technical details
- **[Frontend Guide](./FRONTEND.md)** - Frontend development guide

### Project Status & Planning

Track progress and future plans:

- **[Setup Status](./SETUP_STATUS.md)** - Current implementation status
- **[What's Next](./WHATS_NEXT.md)** - Roadmap and future enhancements
- **[Docker Config Changes](./DOCKER_CONFIG_CHANGES.md)** - Docker configuration history
- **[Contributing](./CONTRIBUTING.md)** - How to contribute to the project

## 🎯 Quick Navigation

### By Role

**End Users:**
1. [User Guide](./USER_GUIDE.md) - Learn how to use the system
2. [Skill Extraction Guide](./SKILL_EXTRACTION_GUIDE.md) - Understand skill analysis
3. [Troubleshooting](./TROUBLESHOOTING.md) - Fix common issues

**Developers:**
1. [API Reference](./API_REFERENCE.md) - API endpoints and usage
2. [Verba Codebase Guide](./VERBA_CODEBASE_GUIDE.md) - Architecture overview
3. [Python Tutorial](./PYTHON_TUTORIAL.md) - SDK usage

**DevOps/Administrators:**
1. [Docker Setup](./DOCKER_SETUP.md) - Deployment guide
2. [Configuration Guide](./CONFIGURATION_GUIDE.md) - System configuration
3. [Troubleshooting](./TROUBLESHOOTING.md) - Operational issues

### By Task

**Setting Up:**
- [Docker Setup](./DOCKER_SETUP.md) - Docker deployment
- [Configuration Guide](./CONFIGURATION_GUIDE.md) - Configure LLMs and settings

**Using Features:**
- [User Guide](./USER_GUIDE.md) - Complete feature walkthrough
- [Skill Extraction Guide](./SKILL_EXTRACTION_GUIDE.md) - Skills analysis
- [Hybrid Search](./HYBRID_SEARCH.md) - Resume generation

**Developing:**
- [API Reference](./API_REFERENCE.md) - API documentation
- [Verba Codebase Guide](./VERBA_CODEBASE_GUIDE.md) - Code architecture
- [Contributing](./CONTRIBUTING.md) - Contribution guidelines

**Troubleshooting:**
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues
- [Setup Status](./SETUP_STATUS.md) - Known limitations

## 📖 Documentation Conventions

### File Naming

- `UPPERCASE_WITH_UNDERSCORES.md` - Major documentation files
- `lowercase_with_underscores.md` - Implementation details
- `PascalCase.md` - Component-specific docs

### Document Structure

Most guides follow this structure:
1. **Overview** - What this document covers
2. **Prerequisites** - What you need to know first
3. **Main Content** - Detailed information
4. **Examples** - Practical examples
5. **Troubleshooting** - Common issues
6. **Related Documentation** - Links to other docs

### Code Examples

Code examples use these conventions:
- `bash` - Shell commands
- `python` - Python code
- `typescript` - TypeScript/JavaScript code
- `json` - Configuration files
- `yaml` - Docker/config files

## 🔄 Documentation Updates

This documentation is actively maintained. Last major update: November 2024

### Recent Changes

- Added skill extraction troubleshooting guide
- Updated API reference with new endpoints
- Enhanced Docker setup documentation
- Added resume generation examples

### Contributing to Docs

Found an error or want to improve documentation?

1. Check [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines
2. Submit a pull request with your changes
3. Update this index if adding new documents

## 📞 Getting Help

Can't find what you're looking for?

1. **Search the docs** - Use your browser's search (Ctrl/Cmd+F)
2. **Check Troubleshooting** - [Troubleshooting Guide](./TROUBLESHOOTING.md)
3. **Review examples** - [User Guide](./USER_GUIDE.md) has many examples
4. **Ask the community** - Create a GitHub issue
5. **Check Verba docs** - [Verba Documentation](https://github.com/weaviate/Verba)

## 🔗 External Resources

### Verba (Core Framework)
- [Verba GitHub](https://github.com/weaviate/Verba)
- [Verba Documentation](https://github.com/weaviate/Verba/blob/main/README.md)

### Weaviate (Vector Database)
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [Weaviate Community Forum](https://forum.weaviate.io/)
- [Weaviate Python Client](https://weaviate.io/developers/weaviate/client-libraries/python)

### LLM Providers
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Cohere Documentation](https://docs.cohere.com/)
- [Ollama Documentation](https://ollama.ai/docs)

---

**Need to update this index?** Edit `docs/README.md` and submit a pull request.
