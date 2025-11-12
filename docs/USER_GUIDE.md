# User Guide

Complete guide to using the Local Resume System for work log management and resume generation.

## Table of Contents

- [Getting Started](#getting-started)
- [Work Log Management](#work-log-management)
- [Skills Analysis](#skills-analysis)
- [Resume Generation](#resume-generation)
- [Resume History](#resume-history)
- [Configuration](#configuration)
- [Best Practices](#best-practices)

---

## Getting Started

### First-Time Setup

1. **Deploy the Application**
   - Follow the installation instructions in the main README
   - Choose between pip, Docker, or source installation
   - Ensure Weaviate is running (embedded, Docker, or cloud)

2. **Configure LLM Providers**
   - Navigate to the Config tab
   - Select your preferred LLM provider (OpenAI, Ollama, Cohere, etc.)
   - Enter API keys if using cloud providers
   - Test the connection

3. **Set Resume-Specific Configuration**
   - Go to Config → Resume Settings
   - Choose models for skill extraction and resume generation
   - Set default resume format (PDF, DOCX, or Markdown)
   - Configure proficiency calculation weights

### Understanding the Interface

The application has five main tabs:

- **Chat**: RAG-based querying of your documents and work logs
- **Import**: Upload documents, PDFs, and other files
- **Skills**: View and analyze your extracted skills
- **Resume**: Generate tailored resumes from job descriptions
- **History**: View and manage previously generated resumes

---

## Work Log Management

### Creating Work Log Entries

Work logs are daily entries documenting your professional activities and accomplishments.

**Using the Chat Interface:**

1. Navigate to the **Work Logs** section (accessible from the Chat tab)
2. Type your work log entry in natural language
3. Click Submit or press Enter
4. The system automatically extracts skills from your entry

**Example Work Log Entry:**
```
Today I completed the user authentication feature using JWT tokens 
and Redis for session management. I also optimized the database 
queries by adding proper indexes, which reduced response time by 40%. 
Deployed the changes to staging using Docker and Kubernetes.
```

**Automatic Skill Extraction:**
As you type, the system identifies skills in real-time:
- JWT
- Redis
- Database Optimization
- Indexing
- Docker
- Kubernetes

### Editing Work Log Entries

1. Find the entry in your work log list
2. Click the Edit icon
3. Modify the content
4. Save changes
5. Skills are automatically re-extracted

### Deleting Work Log Entries

1. Locate the entry you want to remove
2. Click the Delete icon
3. Confirm deletion
4. Associated skills are updated automatically

### Best Practices for Work Logs

**Be Specific:**
```
❌ Bad: "Worked on the API"
✅ Good: "Implemented REST API endpoints using FastAPI with PostgreSQL 
         database integration and JWT authentication"
```

**Include Technologies:**
```
❌ Bad: "Fixed bugs"
✅ Good: "Debugged React component rendering issues using Chrome DevTools 
         and optimized state management with Redux"
```

**Quantify Results:**
```
❌ Bad: "Improved performance"
✅ Good: "Optimized SQL queries reducing page load time from 3s to 800ms, 
         improving user experience for 10,000+ daily users"
```

**Document Soft Skills:**
```
✅ "Led sprint planning meeting with 8 team members, facilitated 
    technical discussions, and mentored junior developer on API design"
```

---

## Skills Analysis

### Viewing Your Skills Dashboard

1. Navigate to the **Skills** tab
2. View your skills organized by category:
   - Programming Languages
   - Frameworks
   - Databases
   - Cloud Services
   - DevOps Tools
   - Soft Skills

### Understanding Proficiency Scores

Proficiency scores (0-1 scale) are calculated based on:

- **Frequency (60%)**: How often you mention the skill
- **Recency (30%)**: How recently you've used it
- **Context (10%)**: The depth of usage described

**Score Interpretation:**
- 0.9-1.0: Expert level
- 0.7-0.89: Advanced proficiency
- 0.5-0.69: Intermediate proficiency
- 0.3-0.49: Basic proficiency
- 0.0-0.29: Beginner level

### Filtering Skills

**By Time Period:**
```
View skills from: Last 30 days | Last 3 months | Last year | All time
```

**By Category:**
```
Select: Programming Languages, Frameworks, Databases, etc.
```

**By Proficiency:**
```
Minimum proficiency: 0.5 (shows only intermediate and above)
```

### Exporting Skills Data

1. Click the Export button
2. Choose format: JSON or CSV
3. Download the file
4. Use for portfolio websites, LinkedIn, or personal tracking

**CSV Export Example:**
```csv
Skill,Category,Proficiency,Occurrences,Last Used
Python,Programming Languages,0.92,45,2025-11-11
React,Frameworks,0.88,32,2025-11-09
PostgreSQL,Databases,0.85,28,2025-11-10
```

---

## Resume Generation

### Generating a Tailored Resume

1. Navigate to the **Resume** tab
2. Paste the job description in the input area
3. Configure generation options:
   - Format: PDF, DOCX, or Markdown
   - Sections: Summary, Experience, Skills, Education
   - Length: Short (1 page), Medium (2 pages), Long (3+ pages)
   - Tone: Professional, Technical, Creative
4. Click "Generate Resume"
5. Wait for the AI to analyze and generate (typically 10-30 seconds)
6. Review the generated resume in the preview pane

### How Resume Generation Works

**Step 1: Job Analysis**
The system extracts:
- Required skills and technologies
- Experience level requirements
- Key responsibilities
- Preferred qualifications

**Step 2: Experience Retrieval**
Using hybrid search, the system:
- Finds work logs matching job requirements
- Ranks experiences by relevance
- Prioritizes recent and high-proficiency skills

**Step 3: Resume Writing**
The LLM:
- Crafts a targeted professional summary
- Rewrites experiences to highlight relevant skills
- Organizes content for maximum impact
- Formats according to professional standards

**Step 4: Formatting**
The system:
- Applies the selected format (PDF/DOCX/Markdown)
- Ensures consistent styling
- Optimizes for ATS (Applicant Tracking Systems)

### Iterative Refinement

After generating a resume, you can refine it through conversation:

**Example Refinement Requests:**
```
"Make the summary more concise"
"Add more emphasis on leadership experience"
"Include specific metrics for the API project"
"Rewrite the experience section to focus on cloud technologies"
```

The system maintains conversation context for up to 10 exchanges, allowing you to iteratively improve the resume.

### Resume Generation Tips

**Provide Complete Job Descriptions:**
- Include all sections: requirements, responsibilities, qualifications
- More detail = better tailoring

**Review and Edit:**
- AI-generated content is a starting point
- Always review for accuracy and personal touch
- Add specific project names and company context

**Use Different Formats:**
- PDF: Best for email submissions
- DOCX: Editable for further customization
- Markdown: Easy to version control and convert

**Generate Multiple Versions:**
- Create variations for different roles
- Test different tones and lengths
- A/B test which version gets better responses

---

## Resume History

### Viewing Resume History

1. Navigate to the **History** tab
2. See all previously generated resumes with:
   - Target role
   - Generation date
   - Format
   - Job description preview

### Managing Resumes

**View Full Resume:**
- Click on any resume to see complete content
- View associated job description
- See which work logs were used

**Regenerate Resume:**
- Click "Regenerate" to create a new version
- Uses updated work log data
- Maintains the same job description
- Useful after adding new experiences

**Export Resume:**
- Click "Export" and choose format
- Download immediately
- Maintains formatting and styling

**Delete Resume:**
- Click "Delete" to remove from history
- Confirmation required
- Cannot be undone

### Organizing Your Resumes

**Naming Convention:**
Use the target role and date for easy identification:
```
Senior Backend Engineer - 2025-11-11
Frontend Developer - 2025-11-10
Full Stack Engineer - 2025-11-09
```

**Track Applications:**
Keep notes about which resume you sent where:
- Company name
- Application date
- Response status
- Interview outcomes

---

## Configuration

### Skill Extraction Settings

**Enable/Disable Automatic Extraction:**
- Toggle on: Skills extracted from all ingested documents
- Toggle off: Manual skill extraction only

**Choose Extraction Model:**
- GPT-4o-mini: Fast and cost-effective
- GPT-4o: More accurate, higher cost
- Claude Sonnet: Good balance
- Ollama (local): Free, requires local setup

**Auto-Extract on Ingestion:**
- Enable to extract skills when uploading documents
- Disable to extract skills on-demand only

### Resume Generation Settings

**Default Model:**
- GPT-4o: Best quality, recommended
- GPT-4o-mini: Faster, lower cost
- Claude Opus: Excellent for creative writing
- Ollama: Local, free option

**Default Format:**
- Set your preferred export format
- Can be overridden per generation

**Default Sections:**
- Choose which sections to include by default
- Options: Summary, Experience, Skills, Education, Projects, Certifications

**Conversation History:**
- Set maximum exchanges for iterative refinement
- Default: 10 exchanges
- Higher = more context, more tokens used

### Proficiency Calculation

Adjust weights for proficiency scoring:

**Frequency Weight (default 0.6):**
- Higher = more emphasis on how often you use a skill
- Lower = less emphasis on frequency

**Recency Weight (default 0.3):**
- Higher = more emphasis on recent usage
- Lower = skills from long ago count more

**Context Weight (default 0.1):**
- Higher = more emphasis on depth of usage
- Lower = simple mentions count more

**Example Adjustments:**

For career changers (emphasize recent skills):
```
Frequency: 0.4
Recency: 0.5
Context: 0.1
```

For experienced professionals (emphasize depth):
```
Frequency: 0.5
Recency: 0.2
Context: 0.3
```

---

## Best Practices

### Daily Work Log Routine

**End of Day Logging:**
1. Spend 5-10 minutes documenting your day
2. Focus on accomplishments, not just tasks
3. Include specific technologies and tools used
4. Note any metrics or results

**Weekly Review:**
1. Review your work logs from the week
2. Ensure all major accomplishments are documented
3. Add any missing details or context
4. Check that skills are being extracted correctly

### Building a Strong Skills Profile

**Diversify Your Skills:**
- Document technical skills (languages, frameworks, tools)
- Include soft skills (leadership, communication, mentoring)
- Note domain knowledge (finance, healthcare, e-commerce)

**Provide Context:**
- Don't just list technologies
- Explain how you used them
- Describe the problems you solved
- Quantify the impact when possible

**Keep It Current:**
- Log regularly to maintain recency scores
- Update old entries if you use skills again
- Remove outdated or irrelevant skills

### Resume Generation Strategy

**Tailor Every Resume:**
- Never send a generic resume
- Generate a new resume for each application
- Emphasize skills mentioned in the job description
- Use similar language to the job posting

**Quality Over Quantity:**
- Spend time refining each resume
- Use iterative refinement for important applications
- Proofread carefully
- Get feedback from others

**Track Your Success:**
- Note which resumes get responses
- Analyze what worked
- Refine your approach
- Update work logs with successful patterns

### Privacy and Security

**Local Deployment:**
- All data stays on your machine
- No external data transmission (except LLM API calls)
- Full control over your information

**API Key Security:**
- Store keys in environment variables
- Never commit keys to version control
- Rotate keys periodically
- Use separate keys for different environments

**Data Backup:**
- Regularly backup your Weaviate data
- Export work logs and resumes
- Keep copies of important documents
- Test restore procedures

---

## Troubleshooting

See the [Troubleshooting Guide](./TROUBLESHOOTING.md) for solutions to common issues.

---

## Getting Help

- **Documentation**: Check the docs folder for detailed guides
- **GitHub Issues**: Report bugs or request features
- **Community Forum**: Ask questions and share tips
- **Technical Docs**: See TECHNICAL.md for implementation details
