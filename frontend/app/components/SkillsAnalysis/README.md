# SkillsAnalysis Component

## Overview

The SkillsAnalysis component provides an interactive visualization for skills breakdown with filtering, categorization, and export capabilities.

## Features

- **Interactive Visualization**: Skills displayed with proficiency bars and color-coded levels
- **Category-Based Grouping**: Skills organized by predefined categories (programming languages, frameworks, databases, etc.)
- **Multiple View Modes**:
  - By Category: All skills grouped by their categories
  - Top Skills: Ranked list of highest proficiency skills
  - Recent Skills: Most recently used skills
- **Time Range Filtering**: Filter skills by date range
- **Category Filtering**: View skills from specific categories
- **Export Functionality**: Export skills data as JSON or CSV
- **Real-time Updates**: Automatically refreshes when new work logs are added

## Usage

### Basic Integration

```tsx
import SkillsAnalysis from "@/app/components/SkillsAnalysis";

<SkillsAnalysis
  credentials={credentials}
  addStatusMessage={addStatusMessage}
/>
```

### Props

- `credentials`: Weaviate connection credentials
- `addStatusMessage`: Function to display status messages to the user

### Integration with Main App

To add the SkillsAnalysis component to the main application:

1. Import the component in `page.tsx`:
```tsx
import SkillsAnalysis from "./components/SkillsAnalysis";
```

2. Add a new page state in the Navbar component types:
```tsx
setCurrentPage: (
  page: "CHAT" | "DOCUMENTS" | "STATUS" | "ADD" | "SETTINGS" | "RAG" | "SKILLS"
) => void;
```

3. Add a navigation button in `NavbarComponent.tsx`:
```tsx
import { FaChartBar } from "react-icons/fa";

<NavbarButton
  hide={false}
  Icon={FaChartBar}
  title="Skills"
  currentPage={currentPage}
  setCurrentPage={setCurrentPage}
  setPage="SKILLS"
/>
```

4. Add the conditional rendering in `page.tsx`:
```tsx
<div className={`${currentPage === "SKILLS" ? "" : "hidden"}`}>
  <SkillsAnalysis
    addStatusMessage={addStatusMessage}
    credentials={credentials}
  />
</div>
```

## API Dependencies

The component requires the following API endpoints to be implemented:

- `POST /api/skills` - Retrieve skills breakdown with filtering
- `POST /api/skills/categories` - Get list of skill categories
- `POST /api/skills/extract` - Extract skills from text (used by WorkLogChat)

## Data Structure

### Skills Data Response
```typescript
{
  skills_by_category: {
    [category: string]: Skill[]
  },
  total_skills: number,
  top_skills: Skill[],
  recent_skills: Skill[],
  generated_at: string
}
```

### Skill Object
```typescript
{
  name: string,
  category: string,
  proficiency_score: number,  // 0.0 to 1.0
  occurrence_count: number,
  source_documents: string[],
  last_used: string  // ISO date string
}
```

## Proficiency Levels

- **Expert** (80-100%): Green badge
- **Advanced** (60-79%): Primary color badge
- **Intermediate** (40-59%): Warning color badge
- **Beginner** (0-39%): Default color badge

## Export Formats

### JSON Export
Complete skills data structure with all metadata

### CSV Export
Simplified format with columns:
- Name
- Category
- Proficiency Score
- Occurrences
- Last Used

## Styling

The component uses the Verba theme system with DaisyUI classes:
- `bg-bg-verba` - Main background
- `bg-bg-alt-verba` - Alternate background
- `text-text-verba` - Primary text
- `text-text-alt-verba` - Secondary text
- `bg-primary-verba` - Primary accent
- `bg-secondary-verba` - Secondary accent
- `bg-warning-verba` - Warning/intermediate level
- `bg-success-verba` - Success/expert level

## Performance Considerations

- Skills data is fetched on component mount and when filters are applied
- Category list is fetched once on mount (static data)
- Export operations are performed client-side
- No automatic refresh - user must apply filters to reload data
