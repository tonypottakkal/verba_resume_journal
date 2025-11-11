# Verba Documentation

This directory contains comprehensive documentation for the Verba Local Resume System.

## Core Documentation

### Architecture & Implementation

- **[VERBA_CODEBASE_GUIDE.md](./VERBA_CODEBASE_GUIDE.md)** - Deep dive into Verba's architecture, component system, and backend implementation. Learn how the RAG pipeline works, understand the VerbaManager orchestration, and explore the modular component system (Readers, Chunkers, Embedders, Retrievers, Generators).

- **[VERBA_UI_AND_IMPLEMENTATION_GUIDE.md](./VERBA_UI_AND_IMPLEMENTATION_GUIDE.md)** - Complete guide to Verba's frontend architecture, UI components, and implementation patterns. Covers the chat interface, document explorer, retrieval system, and how to extend the UI with custom features.

- **[TECHNICAL.md](./TECHNICAL.md)** - Technical overview of Verba's core systems and data structures.

- **[FRONTEND.md](./FRONTEND.md)** - Frontend architecture and component documentation.

## Setup & Configuration

- **[DOCKER_SETUP.md](./DOCKER_SETUP.md)** - Comprehensive Docker deployment guide including resume-specific configuration and environment variables.

- **[PYTHON_TUTORIAL.md](./PYTHON_TUTORIAL.md)** - Python environment setup guide for developers unfamiliar with virtual environments.

- **[DOCKER_CONFIG_CHANGES.md](./DOCKER_CONFIG_CHANGES.md)** - Documentation of Docker setup modifications and configuration changes for the resume features.

## Feature Implementation Documentation

### Resume-Specific Features

- **[WORKLOG_API_IMPLEMENTATION.md](./WORKLOG_API_IMPLEMENTATION.md)** - Technical details of the work log management API endpoints, data structures, and integration with the RAG system.

- **[METADATA_FILTERING_IMPLEMENTATION.md](./METADATA_FILTERING_IMPLEMENTATION.md)** - Complete guide to the document metadata and tag filtering system implementation, including backend API, frontend components, and usage workflows.

## Contributing

- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Guidelines for contributing to the Verba project, including code standards, pull request process, and community guidelines.

## Quick Links

### For Developers
1. Start with [VERBA_CODEBASE_GUIDE.md](./VERBA_CODEBASE_GUIDE.md) to understand the backend architecture
2. Read [VERBA_UI_AND_IMPLEMENTATION_GUIDE.md](./VERBA_UI_AND_IMPLEMENTATION_GUIDE.md) for frontend development
3. Check [CONTRIBUTING.md](./CONTRIBUTING.md) before making contributions

### For Deployment
1. Follow [DOCKER_SETUP.md](./DOCKER_SETUP.md) for Docker deployment
2. Use [PYTHON_TUTORIAL.md](./PYTHON_TUTORIAL.md) if setting up Python environment
3. Review [DOCKER_CONFIG_CHANGES.md](./DOCKER_CONFIG_CHANGES.md) for resume feature configuration

### For Feature Understanding
1. [WORKLOG_API_IMPLEMENTATION.md](./WORKLOG_API_IMPLEMENTATION.md) - Work log management system
2. [METADATA_FILTERING_IMPLEMENTATION.md](./METADATA_FILTERING_IMPLEMENTATION.md) - Document tagging and filtering

## Documentation Structure

```
docs/
├── README.md (this file)
├── VERBA_CODEBASE_GUIDE.md          # Backend architecture
├── VERBA_UI_AND_IMPLEMENTATION_GUIDE.md  # Frontend architecture
├── TECHNICAL.md                      # Technical overview
├── FRONTEND.md                       # Frontend details
├── DOCKER_SETUP.md                   # Docker deployment
├── PYTHON_TUTORIAL.md                # Python setup
├── DOCKER_CONFIG_CHANGES.md          # Docker modifications
├── WORKLOG_API_IMPLEMENTATION.md     # Work log feature
├── METADATA_FILTERING_IMPLEMENTATION.md  # Tag filtering feature
└── CONTRIBUTING.md                   # Contribution guidelines
```

## Additional Resources

- Main README: [../README.md](../README.md)
- Specification Documents: [../.kiro/specs/resume-rag-merger/](../.kiro/specs/resume-rag-merger/)
- Weaviate Documentation: https://weaviate.io/developers/weaviate
- Weaviate Community Forum: https://forum.weaviate.io/
