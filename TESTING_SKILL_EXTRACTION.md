# Testing Skill Extraction

## ✅ Fixed Issues

The skill extraction has been fixed to properly retrieve document content from chunks. The error `"no such prop with name 'text' found in class 'VERBA_DOCUMENTS'"` has been resolved.

## Test Document Provided

A sample resume (`test_resume.txt`) has been included with the following skills:
- **Programming Languages**: Python, JavaScript, TypeScript, Java, Go
- **Frontend**: React, Next.js, Vue.js, HTML5, CSS3, TailwindCSS
- **Backend**: Django, FastAPI, Node.js, Express, Spring Boot
- **Databases**: PostgreSQL, MongoDB, Redis, Elasticsearch
- **Cloud & DevOps**: AWS, Docker, Kubernetes, Terraform, Jenkins, GitHub Actions
- **Data Science**: Machine Learning, TensorFlow, PyTorch, Pandas, NumPy
- **Tools**: Git, VS Code, Jira, Postman, Figma
- **Soft Skills**: Team Leadership, Problem Solving, Communication, Project Management, Agile/Scrum

## How to Test

### Step 1: Upload the Test Document

1. Open your browser to http://localhost:8000
2. Navigate to the **Import** tab
3. Click "Upload Files" or drag and drop
4. Select `test_resume.txt` from the project root
5. Configure import settings:
   - **Reader**: SimpleReader (for .txt files)
   - **Chunker**: TokenChunker or SentenceChunker
   - **Embedder**: OllamaEmbedder (using mxbai-embed-large)
6. Click "Import"
7. Wait for the import to complete (you'll see "Import completed successfully")

### Step 2: Extract Skills

1. Navigate to the **Skills** tab
2. Click the **"Extract Skills from Documents"** button (orange/warning colored)
3. Watch the status messages:
   - "Starting skill extraction from documents..."
   - Processing messages for each document
   - "Successfully extracted X skills from Y documents"
4. The page will automatically refresh to show extracted skills

### Step 3: Verify Results

You should see skills grouped by category:
- **programming_languages**: Python, JavaScript, TypeScript, Java, Go
- **frameworks**: React, Next.js, Django, FastAPI, Spring Boot
- **databases**: PostgreSQL, MongoDB, Redis, Elasticsearch
- **cloud_platforms**: AWS
- **devops_tools**: Docker, Kubernetes, Terraform, Jenkins, GitHub Actions
- **data_science**: Machine Learning, TensorFlow, PyTorch
- **tools**: Git, VS Code, Jira, Postman, Figma
- **soft_skills**: Team Leadership, Problem Solving, Communication, Project Management, Agile/Scrum

Each skill should show:
- Proficiency score (0.0 - 1.0)
- Occurrence count
- Last used date
- Source documents

## Troubleshooting

### No Documents Found

**Problem**: Extraction returns "No documents found"

**Solution**:
1. Check that documents were uploaded successfully in the Import tab
2. Navigate to the Chat tab and verify documents appear in the document list
3. Try uploading the test_resume.txt file again

### Ollama Connection Issues

**Problem**: Extraction fails with connection errors

**Solution**:
1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Check the model is available:
   ```bash
   ollama list
   ```

3. If model is missing, pull it:
   ```bash
   ollama pull qwen2.5:7b-instruct
   ollama pull mxbai-embed-large
   ```

4. Check Docker can reach Ollama:
   ```bash
   docker-compose exec verba curl http://host.docker.internal:11434/api/tags
   ```

### Extraction Takes Too Long

**Problem**: Extraction seems stuck

**Solution**:
1. Check Docker logs:
   ```bash
   docker-compose logs verba --tail=50 -f
   ```

2. The LLM processing can take 30-60 seconds per document
3. Be patient - you'll see progress messages in the logs
4. If truly stuck, restart:
   ```bash
   docker-compose restart verba
   ```

### Skills Not Categorized Correctly

**Problem**: Skills appear in "other" category

**Solution**:
- This is normal for skills not in the predefined categories
- The system has 8 predefined categories
- Skills not matching any category go to "other"
- You can still see and use these skills

## Expected Behavior

### Automatic Extraction (Future Uploads)

After this fix, when you upload new documents:
1. Document is imported and chunked
2. Skills are automatically extracted in the background
3. Skills appear in the Skills tab immediately
4. No manual extraction needed

### Manual Extraction (Existing Documents)

For documents uploaded before this feature:
1. Use the "Extract Skills from Documents" button
2. System processes up to 100 documents
3. Skills are extracted and stored
4. Results appear in the Skills tab

## Data Persistence

Your data is persisted in Docker volumes:
- **weaviate_data**: All documents, chunks, and skills
- **resume_exports**: Exported resumes

Data survives container restarts and rebuilds.

To completely reset:
```bash
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d
```

## Next Steps After Successful Test

1. **Upload your real resume documents**
2. **Extract skills** using the button
3. **Review and verify** the extracted skills
4. **Use skills for resume generation** in the Resume tab
5. **Export skills data** as JSON or CSV if needed

## Support

If you encounter issues:
1. Check Docker logs: `docker-compose logs verba --tail=100`
2. Verify Ollama is running and accessible
3. Ensure documents are properly uploaded
4. Check the browser console for frontend errors (F12)
5. Review the SKILL_EXTRACTION_GUIDE.md for more details
