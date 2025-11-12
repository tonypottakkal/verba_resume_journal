# Documentation Index

Complete documentation for the Local Resume System.

## Getting Started

Start here if you're new to the system:

- **[Main README](../README.md)** - Project overview, installation, and quick start
- **[User Guide](./USER_GUIDE.md)** - Complete guide to using all features
- **[Configuration Guide](./CONFIGURATION_GUIDE.md)** - How to configure LLM providers and settings

## Feature Guides

Deep dives into specific features:

- **[Skill Extraction Guide](./SKILL_EXTRACTION_GUIDE.md)** - Understanding automatic skill extraction and proficiency scoring
- **[Hybrid Search Guide](./HYBRID_SEARCH.md)** - How the system retrieves relevant experiences for resumes
- **[API Reference](./API_REFERENCE.md)** - Complete API documentation with examples

## Implementation Documentation

Technical details for developers and advanced users:

- **[Verba Codebase Guide](./VERBA_CODEBASE_GUIDE.md)** - Deep dive into Verba's architecture
- **[Verba UI Guide](./VERBA_UI_AND_IMPLEMENTATION_GUIDE.md)** - Frontend architecture and components
- **[Technical Documentation](./TECHNICAL.md)** - Core Verba technical details
- **[Frontend Documentation](./FRONTEND.md)** - Frontend development guide

## Feature-Specific Implementation

Detailed implementation docs for resume features:

- **[Work Log API Implementation](./WORKLOG_API_IMPLEMENTATION.md)** - Work log management system
- **[Skill Extraction on Ingestion](./SKILL_EXTRACTION_ON_INGESTION.md)** - Automatic skill extraction during document upload
- **[Metadata Filtering](./METADATA_FILTERING_IMPLEMENTATION.md)** - Document organization and filtering
- **[Docker Configuration](./DOCKER_CONFIG_CHANGES.md)** - Docker setup modifications

## Deployment

Guides for deploying the system:

- **[Docker Setup Guide](./DOCKER_SETUP.md)** - Complete Docker deployment instructions
- **[Python Tutorial](./PYTHON_TUTORIAL.md)** - Python environment setup for beginners

## Troubleshooting

- **[Troubleshooting Guide](./TROUBLESHOOTING.md)** - Solutions to common issues
- **[FAQ](../README.md#faq)** - Frequently asked questions

## Contributing

- **[Contributing Guide](./CONTRIBUTING.md)** - How to contribute to the project

---

## Quick Reference

### Common Tasks

**Setting up for the first time:**
1. Read [Main README](../README.md) - Quick Start section
2. Follow [Configuration Guide](./CONFIGURATION_GUIDE.md) - Environment Variables
3. Check [Troubleshooting Guide](./TROUBLESHOOTING.md) if issues arise

**Using work logs and skills:**
1. [User Guide](./USER_GUIDE.md) - Work Log Management section
2. [Skill Extraction Guide](./SKILL_EXTRACTION_GUIDE.md) - How it works
3. [User Guide](./USER_GUIDE.md) - Skills Analysis section

**Generating resumes:**
1. [User Guide](./USER_GUIDE.md) - Resume Generation section
2. [Hybrid Search Guide](./HYBRID_SEARCH.md) - Understanding retrieval
3. [API Reference](./API_REFERENCE.md) - Resume endpoints

**Configuring the system:**
1. [Configuration Guide](./CONFIGURATION_GUIDE.md) - All settings
2. [Skill Extraction Guide](./SKILL_EXTRACTION_GUIDE.md) - Customization section
3. [Docker Setup Guide](./DOCKER_SETUP.md) - Docker-specific config

**Troubleshooting:**
1. [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues
2. [FAQ](../README.md#faq) - Frequently asked questions
3. GitHub Issues - Report bugs or ask questions

### API Quick Reference

**Work Logs:**
```bash
# Create
POST /api/worklogs

# List
GET /api/worklogs?user_id=user123&start_date=2025-01-01

# Update
PUT /api/worklogs/{id}

# Delete
DELETE /api/worklogs/{id}
```

**Skills:**
```bash
# Get breakdown
GET /api/skills?category=programming

# Extract from text
POST /api/skills/extract

# Get categories
GET /api/skills/categories
```

**Resumes:**
```bash
# Generate
POST /api/resumes/generate

# List history
GET /api/resumes

# Get specific
GET /api/resumes/{id}

# Export
POST /api/resumes/{id}/export

# Regenerate
POST /api/resumes/{id}/regenerate

# Delete
DELETE /api/resumes/{id}
```

See [API Reference](./API_REFERENCE.md) for complete documentation.

---

## Documentation Structure

```
docs/
├── README.md (this file)
│
├── Getting Started
│   ├── USER_GUIDE.md
│   ├── CONFIGURATION_GUIDE.md
│   └── PYTHON_TUTORIAL.md
│
├── Feature Guides
│   ├── SKILL_EXTRACTION_GUIDE.md
│   ├── HYBRID_SEARCH.md
│   └── API_REFERENCE.md
│
├── Implementation
│   ├── VERBA_CODEBASE_GUIDE.md
│   ├── VERBA_UI_AND_IMPLEMENTATION_GUIDE.md
│   ├── TECHNICAL.md
│   ├── FRONTEND.md
│   ├── WORKLOG_API_IMPLEMENTATION.md
│   ├── SKILL_EXTRACTION_ON_INGESTION.md
│   └── METADATA_FILTERING_IMPLEMENTATION.md
│
├── Deployment
│   ├── DOCKER_SETUP.md
│   └── DOCKER_CONFIG_CHANGES.md
│
└── Support
    ├── TROUBLESHOOTING.md
    └── CONTRIBUTING.md
```

---

## Need Help?

1. **Check the docs** - Most questions are answered here
2. **Search GitHub Issues** - Someone may have had the same problem
3. **Create an issue** - Describe your problem with details
4. **Community forum** - Ask questions and share tips

---

## Contributing to Documentation

Found an error or want to improve the docs?

1. Fork the repository
2. Make your changes
3. Submit a pull request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## Documentation Versions

This documentation is for Local Resume System v1.0.0 (based on Verba 2.0.0).

For Verba-specific documentation, see the [Verba repository](https://github.com/weaviate/Verba).
