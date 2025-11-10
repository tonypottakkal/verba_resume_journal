# Implementation Plan

- [x] 1. Set up project structure and copy Verba base
  - Copy the complete Verba project from `weaviate_rag/Verba/` to `local_resume/`
  - Verify all dependencies are present in `setup.py` and `frontend/package.json`
  - Test that the base Verba application runs successfully with `verba start`
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 2. Extend Weaviate schema with new collections
  - Create `goldenverba/components/schema_extensions.py` module
  - Define WorkLog collection schema with properties: content, timestamp, user_id, extracted_skills, metadata
  - Define Skill collection schema with properties: name, category, proficiency_score, occurrence_count, source_documents, last_used
  - Define ResumeRecord collection schema with properties: resume_content, job_description, target_role, generated_at, format, source_log_ids, metadata
  - Add schema initialization function to create collections on startup
  - _Requirements: 11.2, 12.3, 12.4, 13.1_

- [x] 3. Implement WorkLogManager backend module
  - [x] 3.1 Create `goldenverba/components/worklog_manager.py`
    - Implement `create_log_entry()` method to store work log entries in Weaviate
    - Implement `get_log_entries()` method with filtering support (date range, user_id)
    - Implement `update_log_entry()` method to modify existing entries
    - Implement `delete_log_entry()` method to remove entries from Weaviate
    - Add error handling for Weaviate connection failures
    - _Requirements: 11.1, 11.2, 11.4, 11.5_

  - [ ]* 3.2 Write unit tests for WorkLogManager
    - Test work log creation with valid and invalid data
    - Test retrieval with various filter combinations
    - Test update and delete operations
    - Mock Weaviate client for isolated testing
    - _Requirements: 11.1, 11.2, 11.4_

- [ ] 4. Implement SkillsExtractor backend module
  - [ ] 4.1 Create `goldenverba/components/skills_extractor.py`
    - Implement `extract_skills()` method using LLM to identify skills from text
    - Implement `categorize_skills()` method to group skills into predefined categories
    - Implement `calculate_proficiency()` method based on frequency and context analysis
    - Implement `aggregate_skills()` method to generate comprehensive skills reports
    - Add caching for frequently extracted skills to reduce LLM calls
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ]* 4.2 Write unit tests for SkillsExtractor
    - Test skill extraction with sample work log text
    - Test skill categorization accuracy
    - Test proficiency calculation logic
    - Mock LLM responses for consistent testing
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 5. Implement ResumeGenerator backend module
  - [ ] 5.1 Create `goldenverba/components/resume_generator.py`
    - Implement `extract_job_requirements()` method to parse job descriptions
    - Implement `retrieve_relevant_experiences()` method using Weaviate hybrid search
    - Implement `generate_resume()` method that orchestrates requirement extraction, experience retrieval, and LLM-based resume writing
    - Implement `format_resume()` method to export as markdown, PDF, or DOCX
    - Add conversation context management for iterative refinement
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 9.1, 9.2_

  - [ ]* 5.2 Write unit tests for ResumeGenerator
    - Test job requirement extraction from sample descriptions
    - Test experience retrieval with mock Weaviate responses
    - Test resume generation with mock LLM responses
    - Test format conversion for different output types
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 6. Implement ResumeTracker backend module
  - [ ] 6.1 Create `goldenverba/components/resume_tracker.py`
    - Implement `save_resume_record()` method to store resume with associated job description
    - Implement `get_resume_history()` method with filtering and pagination
    - Implement `get_resume_by_id()` method for single resume retrieval
    - Implement `delete_resume_record()` method to remove from history
    - Add metadata tracking for generation date, target role, and source logs
    - _Requirements: 12.3, 12.4, 12.5, 13.1, 13.2, 13.3, 13.4, 13.5_

  - [ ]* 6.2 Write unit tests for ResumeTracker
    - Test resume record creation and storage
    - Test history retrieval with various filters
    - Test resume deletion
    - Mock Weaviate client for testing
    - _Requirements: 12.3, 12.4, 13.1, 13.2_

- [ ] 7. Create API endpoints for work log management
  - Add work log routes to `goldenverba/server/api.py`
  - Implement `POST /api/worklogs` endpoint to create new work log entries
  - Implement `GET /api/worklogs` endpoint to list entries with filtering
  - Implement `PUT /api/worklogs/{id}` endpoint to update entries
  - Implement `DELETE /api/worklogs/{id}` endpoint to delete entries
  - Add request validation using Pydantic models
  - Add error handling and appropriate HTTP status codes
  - _Requirements: 11.1, 11.2, 11.4, 11.5_

- [ ] 8. Create API endpoints for skills analysis
  - Add skills routes to `goldenverba/server/api.py`
  - Implement `GET /api/skills` endpoint to retrieve skills breakdown with filtering
  - Implement `GET /api/skills/categories` endpoint to list skill categories
  - Implement `POST /api/skills/extract` endpoint for on-demand skill extraction from text
  - Add query parameters for time range and category filtering
  - _Requirements: 2.1, 2.2, 2.3, 7.1, 7.2, 7.3, 7.5_

- [ ] 9. Create API endpoints for resume generation and tracking
  - Add resume routes to `goldenverba/server/api.py`
  - Implement `POST /api/resumes/generate` endpoint to generate new resumes from job descriptions
  - Implement `GET /api/resumes` endpoint to list resume history
  - Implement `GET /api/resumes/{id}` endpoint to retrieve specific resume
  - Implement `POST /api/resumes/{id}/regenerate` endpoint to regenerate with updated data
  - Implement `DELETE /api/resumes/{id}` endpoint to delete resume records
  - Implement `POST /api/resumes/{id}/export` endpoint to export in PDF/DOCX format
  - Add streaming support for long-running resume generation
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 12.1, 12.2, 12.3, 13.1, 13.4, 13.5_

- [ ] 10. Create WorkLogChat frontend component
  - [ ] 10.1 Create `frontend/app/components/WorkLogChat.tsx`
    - Build chat-style interface for creating work log entries
    - Add text input with submit functionality
    - Display list of existing work log entries with timestamps
    - Implement edit and delete actions for entries
    - Add real-time skill extraction preview as user types
    - Integrate with `/api/worklogs` endpoints
    - _Requirements: 11.1, 11.2, 11.4, 11.5_

  - [ ]* 10.2 Write component tests for WorkLogChat
    - Test log entry submission
    - Test edit and delete functionality
    - Test skill preview display
    - Mock API calls for testing
    - _Requirements: 11.1, 11.4_

- [ ] 11. Create SkillsAnalysis frontend component
  - [ ] 11.1 Create `frontend/app/components/SkillsAnalysis.tsx`
    - Build interactive visualization for skills breakdown using charts
    - Implement category-based grouping display
    - Add proficiency score indicators for each skill
    - Implement time range filtering controls
    - Add export functionality for skills data (JSON/CSV)
    - Integrate with `/api/skills` endpoints
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ]* 11.2 Write component tests for SkillsAnalysis
    - Test skills data rendering
    - Test filtering functionality
    - Test export feature
    - Mock API responses for testing
    - _Requirements: 7.1, 7.2, 7.3_

- [ ] 12. Create ResumeGenerator frontend component
  - [ ] 12.1 Create `frontend/app/components/ResumeGenerator.tsx`
    - Build job description input area with rich text support
    - Add resume generation options form (format, sections, length)
    - Implement real-time resume preview pane
    - Add export buttons for PDF, DOCX, and Markdown formats
    - Show loading state during generation
    - Display error messages for failed generations
    - Integrate with `/api/resumes/generate` and `/api/resumes/{id}/export` endpoints
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 12.1, 12.2_

  - [ ]* 12.2 Write component tests for ResumeGenerator
    - Test job description input
    - Test resume generation flow
    - Test export functionality
    - Mock API calls for testing
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 13. Create ResumeHistory frontend component
  - [ ] 13.1 Create `frontend/app/components/ResumeHistory.tsx`
    - Build list view displaying all generated resumes with metadata
    - Implement resume selection to show details and associated job description
    - Add regenerate button for each resume
    - Add delete functionality with confirmation dialog
    - Implement filtering by date and target role
    - Add pagination for large resume lists
    - Integrate with `/api/resumes` endpoints
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

  - [ ]* 13.2 Write component tests for ResumeHistory
    - Test resume list rendering
    - Test selection and detail view
    - Test regenerate and delete actions
    - Mock API responses for testing
    - _Requirements: 13.1, 13.2, 13.4, 13.5_

- [ ] 14. Create new page routes and navigation
  - Create `frontend/app/worklogs/page.tsx` for work log chat interface
  - Create `frontend/app/skills/page.tsx` for skills analysis view
  - Create `frontend/app/resume/page.tsx` for resume generation interface
  - Create `frontend/app/history/page.tsx` for resume history view
  - Update `frontend/app/layout.tsx` to add navigation tabs for new pages
  - Ensure all Verba pages (Chat, Import, Config) remain accessible
  - Add icons and labels for new navigation items
  - _Requirements: 14.2, 14.3, 14.5_

- [ ] 15. Integrate new modules with VerbaManager
  - Update `goldenverba/verba_manager.py` to initialize new managers
  - Add WorkLogManager, SkillsExtractor, ResumeGenerator, and ResumeTracker to VerbaManager
  - Ensure new Weaviate collections are created on initialization
  - Add configuration options for new features in settings
  - Update health check endpoint to verify new components
  - _Requirements: 14.1, 14.4, 14.5_

- [ ] 16. Update Docker configuration
  - Update `docker-compose.yml` to include new environment variables
  - Add environment variables for skill extraction and resume generation models
  - Update `Dockerfile` if additional Python dependencies are needed
  - Add volume mounts for resume export storage
  - Update `.env.example` with new configuration options
  - Test Docker deployment with all new features
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 17. Add configuration UI for new features
  - Update `frontend/app/components/ConfigInterface.tsx` to include resume-specific settings
  - Add toggle for enabling/disabling skill extraction
  - Add model selection for skill extraction and resume generation
  - Add configuration for default resume format and sections
  - Add settings for proficiency calculation parameters
  - Persist configuration in Weaviate or local storage
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 18. Implement conversation context for resume generation
  - Create `goldenverba/components/conversation_manager.py`
  - Implement context storage for resume generation sessions
  - Add methods to append user messages and assistant responses
  - Implement context pruning to maintain token limits (last 10 exchanges)
  - Add reset functionality to clear conversation history
  - Integrate with ResumeGenerator for iterative refinement
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 19. Add document metadata and filtering
  - Update Verba's document schema to include custom tags field
  - Implement tag management UI in document list view
  - Add filtering controls to document import page
  - Update RAG query interface to support metadata filtering
  - Ensure work logs and resumes are filterable by metadata
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 20. Implement resume export functionality
  - [ ] 20.1 Add PDF export using reportlab or similar library
    - Install PDF generation library
    - Create resume template for PDF format
    - Implement conversion from markdown to PDF
    - Add styling and formatting options
    - _Requirements: 4.5, 13.5_

  - [ ] 20.2 Add DOCX export using python-docx
    - Install python-docx library
    - Create resume template for DOCX format
    - Implement conversion from markdown to DOCX
    - Add styling and formatting options
    - _Requirements: 4.5, 13.5_

  - [ ] 20.3 Implement export endpoint integration
    - Wire export functions to `/api/resumes/{id}/export` endpoint
    - Add format parameter handling (pdf, docx, markdown)
    - Return file as downloadable response
    - Add error handling for export failures
    - _Requirements: 4.5, 7.5, 13.5_

- [ ] 21. Add skill extraction on document ingestion
  - Update Verba's document ingestion pipeline in `goldenverba/components/reader/`
  - Add post-processing hook to extract skills from ingested documents
  - Store extracted skills in Skill collection
  - Link skills to source documents
  - Update skills when documents are deleted
  - _Requirements: 2.1, 2.2, 2.4, 11.5_

- [ ] 22. Implement hybrid search for resume generation
  - Update ResumeGenerator to use Weaviate hybrid search
  - Combine semantic similarity with keyword matching for job requirements
  - Implement ranking algorithm to prioritize most relevant experiences
  - Add filtering by date range to focus on recent experiences
  - Tune alpha parameter for optimal semantic vs keyword balance
  - _Requirements: 3.1, 3.2, 4.2_

- [ ]* 23. Create end-to-end integration tests
  - Test complete workflow: upload work log → extract skills → generate resume
  - Test work log chat → skills analysis → resume history
  - Test document import → RAG query → resume generation
  - Verify data consistency across all components
  - Test error handling and recovery scenarios
  - _Requirements: All requirements_

- [ ] 24. Update documentation
  - Update README.md with new features and usage instructions
  - Document new API endpoints with request/response examples
  - Add configuration guide for resume-specific settings
  - Create user guide for work log management and resume generation
  - Document skill extraction and categorization logic
  - Add troubleshooting section for common issues
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
