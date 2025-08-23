# PRPViewer Component

**File Path:** `archon-ui-main/src/components/prp/PRPViewer.tsx`
**Last Updated:** 2025-08-22

## Purpose
The main PRP (Product Requirement Prompt) viewer component that intelligently routes content to appropriate renderers based on content type. Supports structured JSON documents, markdown content, and hybrid formats with dynamic section detection and rendering.

## Props/Parameters

### PRPViewerProps Interface
```typescript
interface PRPViewerProps {
  content: PRPContent;
  isDarkMode?: boolean;
  sectionOverrides?: Record<string, React.ComponentType<any>>;
}
```

### Props Details
- **content** (PRPContent, required): PRP document content in various formats
- **isDarkMode** (boolean, default: false): Dark mode theme toggle
- **sectionOverrides** (Record<string, React.ComponentType<any>>, default: {}): Custom section component overrides

## Dependencies

### Imports
```typescript
import React from 'react';
import { PRPContent } from './types/prp.types';
import { MetadataSection } from './sections/MetadataSection';
import { SectionRenderer } from './renderers/SectionRenderer';
import { normalizePRPDocument } from './utils/normalizer';
import { processContentForPRP, isMarkdownContent, isDocumentWithMetadata } from './utils/markdownParser';
import { MarkdownDocumentRenderer } from './components/MarkdownDocumentRenderer';
import './PRPViewer.css';
```

### Exports
```typescript
export const PRPViewer: React.FC<PRPViewerProps>
```

## Key Functions/Methods

### Content Type Detection
```typescript
// 1. Document with metadata + markdown content
if (isDocumentWithMetadata(content)) {
  return <MarkdownDocumentRenderer ... />;
}

// 2. Pure markdown string
if (typeof content === 'string' && isMarkdownContent(content)) {
  return <MarkdownDocumentRenderer ... />;
}

// 3. Object with markdown field
if (typeof content === 'object' && content.markdown) {
  return <MarkdownDocumentRenderer ... />;
}
```

### Section Priority System
```typescript
const getSectionPriority = (key: string): number => {
  const normalizedKey = key.toLowerCase();
  if (normalizedKey.includes('goal') || normalizedKey === 'why') return 1;
  if (normalizedKey.includes('what') || normalizedKey.includes('description')) return 2;
  if (normalizedKey.includes('context') || normalizedKey.includes('background')) return 3;
  if (normalizedKey.includes('persona') || normalizedKey.includes('user')) return 4;
  if (normalizedKey.includes('flow') || normalizedKey.includes('journey')) return 5;
  if (normalizedKey.includes('metric') || normalizedKey.includes('success')) return 6;
  if (normalizedKey.includes('plan') || normalizedKey.includes('implementation')) return 7;
  if (normalizedKey.includes('validation') || normalizedKey.includes('testing')) return 8;
  return 10; // Default priority for other sections
};
```

### Content Processing Pipeline
```typescript
// Process content for PRP-specific handling
const processedForPRP = processContentForPRP(content);

// Normalize the content structure
const normalizedContent = normalizePRPDocument(processedForPRP);

// Process content to handle [Image #N] placeholders
const processedContent = processContent(normalizedContent);
```

## Usage Example
```typescript
import { PRPViewer } from '@/components/prp/PRPViewer';

// Structured PRP document
const prpDocument = {
  title: "OAuth2 Authentication Implementation",
  version: "1.0",
  author: "prp-creator",
  date: "2025-07-30",
  status: "draft",
  goal: "Implement secure OAuth2 authentication",
  why: ["Enable secure user authentication", "Reduce registration friction"],
  what: {
    description: "Complete OAuth2 flow with provider selection",
    success_criteria: ["Users can authenticate in <3 clicks"]
  },
  context: {
    current_state: "Basic username/password authentication exists",
    dependencies: ["requests-oauthlib", "cryptography"]
  },
  implementation_blueprint: {
    phase_1: {
      description: "Configure OAuth2 providers",
      tasks: [
        {
          title: "Create OAuth2 provider configurations",
          files: ["src/auth/oauth/providers.py"]
        }
      ]
    }
  }
};

<PRPViewer 
  content={prpDocument}
  isDarkMode={false}
/>

// Markdown document
const markdownContent = `
# Project Requirements

## Overview
This document outlines the requirements for...

## Goals
- Improve user experience
- Increase security
- Reduce complexity
`;

<PRPViewer 
  content={markdownContent}
  isDarkMode={true}
/>

// Document with metadata and markdown
const hybridDocument = {
  title: "API Documentation",
  version: "2.0",
  author: "tech-team",
  markdown: `
# API Specification

## Authentication
All API requests require authentication...

## Endpoints
### GET /api/users
Returns a list of users...
  `
};

<PRPViewer 
  content={hybridDocument}
  isDarkMode={false}
/>

// Custom section overrides
const CustomMetadata = (props) => (
  <div className="custom-header">
    <h1>{props.content.title}</h1>
    <div className="custom-badges">
      <span>Version: {props.content.version}</span>
      <span>Status: {props.content.status}</span>
    </div>
  </div>
);

<PRPViewer 
  content={prpDocument}
  sectionOverrides={{
    metadata: CustomMetadata
  }}
/>

// Project integration
const ProjectPRPView = ({ project }) => {
  const [prpContent, setPrpContent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPRP = async () => {
      try {
        const content = await fetchProjectPRP(project.id);
        setPrpContent(content);
      } catch (error) {
        console.error('Failed to load PRP:', error);
      } finally {
        setLoading(false);
      }
    };

    loadPRP();
  }, [project.id]);

  if (loading) return <div>Loading PRP...</div>;
  if (!prpContent) return <div>No PRP content available</div>;

  return (
    <div className="project-prp-container">
      <PRPViewer 
        content={prpContent}
        isDarkMode={theme === 'dark'}
      />
    </div>
  );
};
```

## State Management
No internal state management - purely presentational component

## Side Effects
- Content type detection and routing
- Dynamic section rendering
- Image placeholder processing

## Visual Features

### Content Routing
- **Markdown Documents** - Routed to MarkdownDocumentRenderer
- **Structured JSON** - Processed through section-based rendering
- **Hybrid Content** - Intelligent detection and appropriate routing
- **Error Handling** - Graceful fallbacks for invalid content

### Section Organization
- **Metadata Header** - Always rendered first with document information
- **Priority-Based Sorting** - Sections ordered by logical importance
- **Dynamic Sections** - Sections rendered based on content structure
- **Fallback Handling** - Generic section for unrecognized content

### Theme Support
- **Dark Mode** - Complete dark theme support
- **Light Mode** - Clean, professional light theme
- **CSS Custom Properties** - Theme-aware styling
- **Component Consistency** - Consistent theming across all sections

## Content Processing

### Normalization Pipeline
1. **Content Detection** - Identify content type and structure
2. **Format Conversion** - Convert to standard PRP format
3. **Section Extraction** - Identify and categorize sections
4. **Metadata Processing** - Extract document metadata
5. **Content Enhancement** - Process images, links, and formatting

### Section Detection
```typescript
// Extract sections (skip metadata fields)
const metadataFields = [
  'title', 'version', 'author', 'date', 'status', 
  'document_type', 'id', '_id', 'project_id', 
  'created_at', 'updated_at'
];
const sections = Object.entries(processedContent)
  .filter(([key]) => !metadataFields.includes(key));
```

### Image Processing
```typescript
const processContent = (content: any): any => {
  // Process [Image #N] placeholders and other content enhancements
  // Returns processed content with enhanced formatting
};
```

## Error Handling

### Content Validation
```typescript
try {
  if (!content) {
    return <div className="text-gray-500">No PRP content available</div>;
  }
  // Process content...
} catch (error) {
  console.error('Error rendering PRP content:', error);
  return (
    <div className="text-red-500">
      Error rendering PRP content. Please check the document format.
    </div>
  );
}
```

### Fallback Rendering
- **Invalid Content** - Error message with guidance
- **Empty Content** - Placeholder message
- **Malformed Sections** - Generic section rendering
- **Missing Components** - Graceful degradation

## Performance Optimization

### Rendering Strategy
- **Conditional Rendering** - Only render sections with content
- **Component Memoization** - Prevent unnecessary re-renders
- **Lazy Loading** - Load sections on demand
- **Content Caching** - Cache processed content

### Bundle Optimization
- **Tree Shaking** - Remove unused section components
- **Dynamic Imports** - Load components as needed
- **Shared Dependencies** - Reuse common utilities

## Accessibility Features
- **Semantic HTML** - Proper document structure
- **ARIA Attributes** - Screen reader support
- **Keyboard Navigation** - Full keyboard accessibility
- **Focus Management** - Proper focus handling
- **Color Contrast** - WCAG compliant colors

## Integration Patterns

### Document Management
```typescript
const DocumentViewer = ({ documentId }) => {
  const { data: document, loading } = useDocument(documentId);
  
  return (
    <div className="document-viewer">
      {loading ? (
        <DocumentSkeleton />
      ) : (
        <PRPViewer 
          content={document.content}
          isDarkMode={useTheme().isDark}
        />
      )}
    </div>
  );
};
```

### Project Dashboard
```typescript
const ProjectDashboard = ({ project }) => (
  <div className="project-dashboard">
    <ProjectHeader project={project} />
    <Tabs>
      <TabPanel label="Overview">
        <ProjectOverview project={project} />
      </TabPanel>
      <TabPanel label="Requirements">
        <PRPViewer 
          content={project.prp}
          isDarkMode={isDark}
        />
      </TabPanel>
      <TabPanel label="Tasks">
        <TaskList projectId={project.id} />
      </TabPanel>
    </Tabs>
  </div>
);
```

## Related Files
- **Parent components:** Project pages, document viewers, admin interfaces
- **Child components:** Section components, renderers, utilities
- **Shared utilities:** Markdown parsers, normalizers, formatters

## Notes
- Highly flexible content routing system
- Supports multiple content formats seamlessly
- Optimized for large, complex documents
- Comprehensive error handling and fallbacks
- Performance optimized with lazy loading
- Consistent with overall design system
- Extensive TypeScript support for type safety
- Accessible and responsive design

---
*Auto-generated documentation - verify accuracy before use*
