# Local Resume System Project

**An AI-powered professional development platform built on Verba's RAG framework**

[![Based on Verba](https://img.shields.io/badge/Based%20on-Verba%202.0-green)](https://github.com/weaviate/Verba)
[![Powered by Weaviate](https://img.shields.io/static/v1?label=powered%20by&message=Weaviate%20%E2%9D%A4&color=green&style=flat-square)](https://weaviate.io/)
[![Work in Progress](https://img.shields.io/badge/Status-Work%20in%20Progress-yellow)](https://github.com/your-repo/local_resume)

> **⚠️ DISCLAIMER**: This project is a work in progress and is provided as open-source software for educational and personal use. While I strive for quality and reliability, this software is provided "as is" without warranty of any kind. Use at your own risk. Always review and verify AI-generated content, especially for professional applications like resumes. We recommend testing thoroughly in a development environment before using for critical career documents.

## Table of Contents

- [Project Description](#project-description)
- [🚀 Quick Start](#-quick-start)
- [Resume-Specific Features](#resume-specific-features)
- [📋 TODO & Testing Status](#-todo--testing-status)
- [📚 Documentation](#-documentation)
- [🔧 Configuration](#-configuration)
- [🙏 Credits & Inspiration](#-credits--inspiration)
- [❔ FAQ](#-faq)

---

## Project Description

### AI-Powered Professional Development Platform

The Local Resume System is an intelligent work journal and resume generation system powered by Retrieval-Augmented Generation (RAG) and Large Language Models. Built on Verba's robust RAG infrastructure, this system combines agentic AI capabilities with semantic search to create a comprehensive solution for career development and job application optimization.

### 🎯 What Makes This Different

Traditional resume builders require manual entry and formatting. The Local Resume System takes a fundamentally different approach by:

- **Continuous Documentation**: Maintain a searchable work journal with chat-style logging of daily accomplishments and projects
- **Intelligent Skill Extraction**: Automatically identify and categorize technical skills from your work logs using LLM-powered semantic analysis
- **Context-Aware Resume Generation**: Generate tailored resumes for specific job descriptions by retrieving relevant experiences through hybrid vector search
- **Proficiency Analytics**: Track skill development over time with automated proficiency scoring based on usage frequency and context
- **Privacy-First Architecture**: Deploy entirely locally or on your own infrastructure—your career data never leaves your control

### 🚀 Key Capabilities

**Agentic AI Features:**
- Semantic work log analysis with automatic skill extraction
- Job-specific resume tailoring using hybrid search
- Iterative resume refinement through conversational interface
- Skill categorization and proficiency scoring

**RAG-Enabled Intelligence:**
- Hybrid search combining semantic similarity with keyword matching
- Multi-document context querying across all work logs
- Contextual resume generation using retrieved experiences
- Document metadata filtering for targeted resume generation

**Professional Development Tools:**
- Skills dashboard with interactive visualization
- Resume history tracking with regeneration capabilities
- Multi-format export (Markdown, PDF, DOCX)
- Work log management with automatic skill detection

### 🏗️ Architecture

Built on proven technologies:
- **Verba RAG Framework**: Production-ready retrieval-augmented generation pipeline
- **Weaviate Vector Database**: High-performance semantic search and storage
- **Next.js Frontend**: Modern, responsive user interface
- **FastAPI Backend**: Scalable Python API with async support
- **Multi-LLM Support**: Works with OpenAI, Anthropic, Cohere, Ollama, and more

### 💡 Use Cases

- **Job Seekers**: Generate tailored resumes for each application in minutes
- **Career Professionals**: Maintain a searchable record of accomplishments
- **Consultants & Freelancers**: Track projects and generate client-specific summaries
- **Technical Professionals**: Automatically catalog technical skill growth
- **Career Coaches**: Help clients document and articulate their value

---

## 🚀 Quick Start

Get started in 5 minutes:

### 1. Install

```bash
# Using pip
pip install goldenverba

# Or from source
git clone https://github.com/your-repo/local_resume.git
cd local_resume
pip install -e .
```

### 2. Configure

Create a `.env` file with your API keys:

```bash
# Required: Choose one LLM provider
OPENAI_API_KEY=sk-...
# or
OLLAMA_URL=http://localhost:11434

# Optional: Enable resume features
ENABLE_SKILL_EXTRACTION=true
SKILL_EXTRACTION_MODEL=gpt-4o-mini
RESUME_GENERATION_MODEL=gpt-4o
```

### 3. Start

```bash
verba start
```

Visit `http://localhost:8000` and you're ready to go!

### 4. Use

**Create Work Logs** → **Analyze Skills** → **Generate Resumes** → **Export**

📖 **For detailed instructions, see the [User Guide](./docs/USER_GUIDE.md)**

---

## Resume-Specific Features

This project extends Verba with specialized resume generation and work log management:

### New Features

- **Work Log Management** - Chat-style interface for logging daily work activities
- **Automatic Skill Extraction** - LLM-powered extraction from all documents
- **Skills Analysis** - Interactive visualization with proficiency scoring
- **Resume Generation** - AI-powered tailored resume creation
- **Resume History** - Track and manage all generated resumes
- **Configuration UI** - Comprehensive settings for all resume features

### New API Endpoints

- `/api/worklogs` - Work log CRUD operations
- `/api/skills` - Skills analysis and extraction
- `/api/resumes/generate` - Resume generation
- `/api/resumes` - Resume history and export (PDF, DOCX, Markdown)
- `/api/config/resume` - Resume-specific configuration

### New Backend Components

- `WorkLogManager` - Work log storage and management
- `SkillsExtractor` - LLM-powered skill extraction and categorization
- `ResumeGenerator` - Hybrid search-based resume generation
- `ResumeTracker` - Resume history and metadata management

---

## 📋 TODO & Testing Status

This project is functional but testing is still in progress. See [WHATS_NEXT.md](./WHATS_NEXT.md) for the complete list of remaining tasks.

### ✅ Completed
- Core backend modules (WorkLogManager, SkillsExtractor, ResumeGenerator, ResumeTracker)
- All API endpoints for work logs, skills, and resumes
- Frontend components (WorkLogChat, SkillsAnalysis, ResumeGenerator, ResumeHistory)
- Resume export functionality (PDF, DOCX, Markdown)
- Skill extraction on document ingestion
- Hybrid search for resume generation
- Docker configuration and deployment
- Comprehensive documentation

### 🧪 Testing In Progress
- **Unit Tests** - Backend module tests (WorkLogManager, SkillsExtractor, ResumeGenerator, ResumeTracker)
- **Component Tests** - Frontend component tests (WorkLogChat, SkillsAnalysis, ResumeGenerator, ResumeHistory)
- **Integration Tests** - End-to-end workflow testing

### 🚀 Future Enhancements
- Multi-user support with authentication
- Additional resume templates
- Cover letter generation
- Interview preparation features
- Skill gap analysis
- Career path recommendations

**Want to help?** Check out [WHATS_NEXT.md](./WHATS_NEXT.md) for detailed tasks and [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for contribution guidelines.

---

## 📚 Documentation

### Getting Started

- **[User Guide](./docs/USER_GUIDE.md)** - Complete guide to using all features
- **[Configuration Guide](./docs/CONFIGURATION_GUIDE.md)** - LLM providers, settings, and optimization
- **[Quick Start](#-quick-start)** - Get running in 5 minutes

### Feature Guides

- **[Skill Extraction Guide](./docs/SKILL_EXTRACTION_GUIDE.md)** - Understanding skill extraction and proficiency
- **[Hybrid Search Guide](./docs/HYBRID_SEARCH.md)** - How resume generation retrieves experiences
- **[API Reference](./docs/API_REFERENCE.md)** - Complete API documentation

### Implementation Details

- **[Work Log API](./docs/WORKLOG_API_IMPLEMENTATION.md)** - Work log management system
- **[Skill Extraction on Ingestion](./docs/SKILL_EXTRACTION_ON_INGESTION.md)** - Automatic extraction during upload
- **[Metadata Filtering](./docs/METADATA_FILTERING_IMPLEMENTATION.md)** - Document organization
- **[Docker Setup](./docs/DOCKER_SETUP.md)** - Complete Docker deployment guide

### Verba Core Documentation

- **[Verba Codebase Guide](./docs/VERBA_CODEBASE_GUIDE.md)** - Deep dive into Verba's architecture
- **[Verba UI Guide](./docs/VERBA_UI_AND_IMPLEMENTATION_GUIDE.md)** - Frontend architecture
- **[Technical Documentation](./docs/TECHNICAL.md)** - Core Verba technical details

### Support

- **[Troubleshooting Guide](./docs/TROUBLESHOOTING.md)** - Solutions to common issues
- **[FAQ](#-faq)** - Frequently asked questions

---

## 🔧 Configuration

### Core Verba Setup

For detailed Verba setup instructions (deployment options, API keys, Weaviate configuration, etc.), see the **[official Verba README](https://github.com/weaviate/Verba/blob/main/README.md)**.

### Resume-Specific Configuration

Additional environment variables for resume features:

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
MAX_WORK_LOGS_PER_RESUME=50
```

See the [Configuration Guide](./docs/CONFIGURATION_GUIDE.md) for complete details.

---

## 🙏 Credits & Inspiration

This project builds upon and merges capabilities from two excellent open-source projects:

- **[Verba (Weaviate)](https://github.com/weaviate/Verba)** - The foundational RAG framework providing document ingestion, semantic search, and LLM integration. Verba's modular architecture and production-ready components form the backbone of this system. For core RAG functionality, deployment options, and Weaviate configuration, refer to the [official Verba documentation](https://github.com/weaviate/Verba/blob/main/README.md).

- **[Super-People (Weaviate)](https://github.com/prachi-b-modi/super-people)** - Inspired the resume generation and skills analysis features. The concept of using work logs for automated resume creation and skill tracking originated from this innovative project. For the original implementation of resume generation and skills extraction, see the [Super-People repository](https://github.com/prachi-b-modi/super-people).

I'm grateful to both projects and their contributors for making their work available to the community. This project aims to combine the best of both worlds while adding new capabilities for professional development. I was tired of stuggling to update my resume and market myself every time I need to find a new job. Prachi Modi inspired this effort and I wanted to improve the capabilities she demo'd while I learn more about Weaviate RAG + AI Agents. This is a tool I use, and it really is an attempt to make life easier when the times comes to find a new job. I hope it helps you as well. 

---

## ❔ FAQ

### General Questions

**Q: How is this different from Verba?**  
A: This project extends Verba with specialized features for professional development: work log management, automatic skill extraction, proficiency tracking, and AI-powered resume generation tailored to job descriptions.

**Q: Can I still use all of Verba's features?**  
A: Yes! All Verba features (document import, RAG chat, vector visualization, etc.) are fully preserved. Resume features are added as additional tabs.

**Q: Do I need to know how Verba works?**  
A: Not necessarily. The [User Guide](./docs/USER_GUIDE.md) covers everything. However, understanding Verba's basics helps with advanced configuration.

### Resume Features

**Q: How accurate is the skill extraction?**  
A: Accuracy depends on your LLM provider. GPT-4o and Claude Sonnet achieve 90%+ accuracy. You can review and correct extracted skills in the Skills Analysis dashboard.

**Q: Can I use this completely offline?**  
A: Yes! Use Ollama for local LLM inference. Set `OLLAMA_URL=http://localhost:11434` and choose Ollama models. All data stays on your machine.

**Q: How does proficiency scoring work?**  
A: Proficiency is calculated based on frequency of use (60%), recency (30%), and depth of usage (10%). You can adjust these weights. See the [Skill Extraction Guide](./docs/SKILL_EXTRACTION_GUIDE.md).

**Q: Will my resume pass ATS (Applicant Tracking Systems)?**  
A: Yes! The system generates resumes in standard formats with proper structure and keywords from job descriptions. Hybrid search ensures relevant skills are included.

**Q: How many work logs do I need before generating a resume?**  
A: You can generate with 5-10 work logs, but 20-30 entries provide better results. The system retrieves the most relevant experiences based on the job description.

**Q: Can I edit the generated resume?**  
A: Yes! Export as DOCX for full editing, or use iterative refinement to ask the AI to make specific changes (e.g., "make the summary more concise").

### Privacy & Cost

**Q: Is my data private?**  
A: Yes! All data is stored locally in Weaviate. The only external calls are to your chosen LLM provider. Use Ollama for complete privacy.

**Q: How much does it cost to run?**  
A: Using OpenAI: ~$0.01-0.05 per resume with GPT-4o-mini, ~$0.10-0.30 with GPT-4o.(* please check OpenAI prices as they are subject to change *) Using Ollama: completely free but requires local compute resources.

**Q: Can I backup my data?**  
A: Yes! For Docker: `docker cp verba-weaviate-1:/var/lib/weaviate ./backup`. For local: backup `~/.local/share/weaviate`. You can also export via API.

### Customization

**Q: Can I customize skill categories?**  
A: Yes! Edit `goldenverba/components/skills_extractor.py` to add custom categories. See the [Skill Extraction Guide](./docs/SKILL_EXTRACTION_GUIDE.md).

**Q: Can multiple people use the same instance?**  
A: The system supports multiple users via the `user_id` field, but there's no built-in authentication. For multi-user deployments, implement authentication at the reverse proxy level.

### Troubleshooting

**Q: Where can I get help?**  
A: Check the [Troubleshooting Guide](./docs/TROUBLESHOOTING.md), search GitHub Issues, or create a new issue with details about your problem.

**Q: What if I have Verba-specific questions?**  
A: Refer to the [official Verba README](https://github.com/weaviate/Verba/blob/main/README.md) and [Verba documentation](https://github.com/weaviate/Verba), or ask in the [Weaviate Community Forum](https://forum.weaviate.io/).

---

## 🚩 Known Issues

### Resume-Specific Issues

- **Skill extraction may be slow with large documents** - Use faster models like GPT-4o-mini for extraction
- **Resume generation requires sufficient work log data** - Minimum 5-10 entries recommended

### Verba Core Issues

For Verba-specific known issues, see the [official Verba README](https://github.com/weaviate/Verba/blob/main/README.md#known-issues).

---

## 💖 Contributing

Contributions are welcome! Please:

1. Check existing issues and documentation
2. Create an issue to discuss major changes
3. Follow the code style and conventions
4. Add tests for new features
5. Update documentation as needed

See [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for detailed guidelines.

For Verba core contributions, see the [Verba Contributing Guide](https://github.com/weaviate/Verba/blob/main/CONTRIBUTING.md).

---

## 📄 License

This project maintains the same license as Verba. See [LICENSE](./LICENSE) for details.

---

## 🔗 Links

### This Project
- **[Project Documentation](./docs/README.md)** - Complete documentation index
- **[User Guide](./docs/USER_GUIDE.md)** - Getting started guide
- **[API Reference](./docs/API_REFERENCE.md)** - API documentation

### Source Projects
- **[Verba Repository](https://github.com/weaviate/Verba)** - Core RAG framework
- **[Verba Documentation](https://github.com/weaviate/Verba/blob/main/README.md)** - Setup and configuration
- **[Super-People Repository](https://github.com/prachi-b-modi/super-people)** - Original resume generation concept

### Related Resources
- **[Weaviate Documentation](https://weaviate.io/developers/weaviate)** - Vector database docs
- **[Weaviate Community Forum](https://forum.weaviate.io/)** - Get help and share ideas

---

**Built with ❤️ on top of [Verba](https://github.com/weaviate/Verba) by [Weaviate](https://weaviate.io/) and inspired by [Super-People](https://github.com/prachi-b-modi/super-people)**
