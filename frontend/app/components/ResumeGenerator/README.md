# ResumeGenerator Component

## Overview

The ResumeGenerator component provides a comprehensive interface for generating tailored resumes based on job descriptions. It features a split-panel design with input/options on the left and a real-time preview on the right.

## Features

### Job Description Input
- Text input for target role/position
- Large textarea for pasting job descriptions
- Real-time validation

### Resume Options
- **Format Selection**: Choose between Markdown, PDF, or DOCX output
- **Section Selection**: Toggle which sections to include:
  - Summary
  - Experience
  - Skills
  - Education
  - Certifications
  - Projects
- **Length Control**: Slider to set maximum resume length (500-3000 words)

### Resume Preview
- Real-time display of generated resume
- Formatted markdown rendering with basic HTML conversion
- Metadata display (generation date, target role)
- Loading states during generation
- Error message display

### Export Functionality
- Export to Markdown (.md)
- Export to PDF (.pdf)
- Export to DOCX (.docx)
- Automatic file download with appropriate naming

### Additional Features
- Regenerate button to create new version with same job description
- Loading indicators during generation
- Status messages for user feedback
- Responsive layout (stacks vertically on mobile)

## Props

```typescript
interface ResumeGeneratorProps {
  credentials: Credentials;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}
```

## API Integration

The component integrates with the following backend endpoints:

- `POST /api/resumes/generate` - Generate a new resume
- `POST /api/resumes/{id}/export` - Export resume in specified format

## Usage

```tsx
import ResumeGenerator from "@/app/components/ResumeGenerator";

<ResumeGenerator
  credentials={credentials}
  addStatusMessage={addStatusMessage}
/>
```

## Styling

The component uses Verba's design system with:
- DaisyUI components (buttons, inputs, textareas)
- Verba color tokens (bg-verba, text-verba, primary-verba, etc.)
- Responsive Tailwind classes
- Consistent spacing and rounded corners

## State Management

The component manages the following state:
- `jobDescription`: User input for job posting
- `targetRole`: Position title
- `isGenerating`: Loading state during API calls
- `generatedResume`: The generated resume object
- `resumeOptions`: User-selected format, sections, and length
- `error`: Error messages from failed generations

## Requirements Addressed

This component addresses the following requirements from the design document:

- **4.1**: Extract job requirements from description
- **4.2**: Retrieve relevant work experiences
- **4.3**: Generate tailored resume content
- **4.4**: Format resume professionally
- **4.5**: Export in multiple formats (PDF, DOCX, Markdown)
- **12.1**: Provide interface for job description input
- **12.2**: Store job descriptions with generated resumes
