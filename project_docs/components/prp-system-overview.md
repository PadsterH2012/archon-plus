# PRP System Components Overview

**File Path:** `archon-ui-main/src/components/prp/` directory
**Last Updated:** 2025-08-23

## Purpose
Comprehensive documentation of the Product Requirement Prompt (PRP) system - a sophisticated document rendering and management system that dynamically displays structured requirement documents with intelligent section detection, markdown support, and flexible component architecture.

## System Architecture

### Core Components (27 files total)
The PRP system is organized into several key areas:

#### **1. Main Components (2 files)**
- **PRPViewer.tsx** - Main viewer component with intelligent content routing
- **index.ts** - Central export hub for all PRP components

#### **2. Section Components (13 files)**
- **MetadataSection.tsx** - Document metadata display
- **ContextSection.tsx** - Context and background information
- **PersonaSection.tsx** - User personas with expandable cards
- **FlowSection.tsx** - User flows and workflows
- **MetricsSection.tsx** - Success metrics and KPIs
- **PlanSection.tsx** - Implementation plans and phases
- **ListSection.tsx** - List-based content rendering
- **ObjectSection.tsx** - Complex object structure display
- **KeyValueSection.tsx** - Simple key-value pair rendering
- **FeatureSection.tsx** - Feature requirements and capabilities
- **GenericSection.tsx** - Fallback section for any data type
- **RolloutPlanSection.tsx** - Deployment and rollout plans
- **TokenSystemSection.tsx** - Token-based system configurations

#### **3. Renderer Components (6 files)**
- **SectionRenderer.tsx** - Dynamic section type detection and rendering
- **CollapsibleSectionRenderer.tsx** - Enhanced collapsible section wrapper with animations
- **CollapsibleSectionWrapper.tsx** - Basic section collapse/expand functionality
- **MarkdownDocumentRenderer.tsx** - Markdown document processing
- **MarkdownSectionRenderer.tsx** - Markdown section rendering
- **SimpleMarkdown.tsx** - Lightweight markdown parser

#### **4. Utility Components (5 files)**
- **formatters.ts** - Text and value formatting utilities
- **markdownParser.ts** - Markdown content detection and parsing
- **normalizer.ts** - Document structure normalization
- **objectRenderer.tsx** - Complex object rendering utilities
- **sectionDetector.ts** - Intelligent section type detection

#### **5. Type Definitions (1 file)**
- **prp.types.ts** - Complete TypeScript interfaces and types

#### **6. Styling (1 file)**
- **PRPViewer.css** - Component-specific styling

## Key Features

### Intelligent Content Routing
The PRPViewer automatically detects content type and routes to appropriate renderer:
- **Markdown Documents** - Full markdown support with metadata
- **Structured JSON** - Dynamic section-based rendering
- **Mixed Content** - Hybrid markdown/structured content
- **Legacy Formats** - Backward compatibility with existing documents

### Dynamic Section Detection
Automatic section type detection based on content structure:
- **Metadata** - Document headers and information
- **Context** - Background and scope information
- **Personas** - User personas and stakeholders
- **Flows** - User journeys and workflows
- **Metrics** - Success criteria and KPIs
- **Plans** - Implementation and rollout plans
- **Features** - Feature requirements and specifications
- **Generic** - Fallback for any unrecognized content

### Flexible Architecture
- **Component Overrides** - Custom section components
- **Theme Support** - Light/dark mode compatibility
- **Responsive Design** - Mobile-friendly layouts
- **Accessibility** - WCAG compliant rendering
- **Performance** - Optimized for large documents

## Usage Patterns

### Basic PRP Viewing
```typescript
import { PRPViewer } from '@/components/prp';

// Structured PRP document
<PRPViewer 
  content={prpDocument}
  isDarkMode={darkMode}
/>

// Markdown document
<PRPViewer 
  content={markdownContent}
  isDarkMode={darkMode}
/>
```

### Custom Section Overrides
```typescript
import { PRPViewer, MetadataSection } from '@/components/prp';

const CustomMetadata = (props) => (
  <div className="custom-metadata">
    <MetadataSection {...props} />
    <div>Custom content here</div>
  </div>
);

<PRPViewer 
  content={prpDocument}
  sectionOverrides={{
    metadata: CustomMetadata
  }}
/>
```

### Project Integration
```typescript
const ProjectPRPViewer = ({ projectId }) => {
  const [prpContent, setPrpContent] = useState(null);
  
  useEffect(() => {
    fetchProjectPRP(projectId).then(setPrpContent);
  }, [projectId]);

  return (
    <div className="project-prp">
      <PRPViewer 
        content={prpContent}
        isDarkMode={theme === 'dark'}
      />
    </div>
  );
};
```

## Section Component Details

### MetadataSection
- **Purpose:** Document header with title, version, author, status
- **Features:** Status badges, version tracking, author information
- **Styling:** Gradient backgrounds, accent colors

### ContextSection  
- **Purpose:** Background information, scope, objectives
- **Features:** Expandable content, icon-based organization
- **Use Cases:** Project context, business requirements

### PersonaSection
- **Purpose:** User personas with detailed profiles
- **Features:** Expandable persona cards, role-based organization
- **Content:** Goals, pain points, user journeys

### FlowSection
- **Purpose:** User flows and workflow visualization
- **Features:** Step-by-step flow rendering, visual indicators
- **Content:** User journeys, process flows

### MetricsSection
- **Purpose:** Success metrics and KPIs
- **Features:** Metric categorization, progress indicators
- **Content:** Performance targets, measurement criteria

### PlanSection
- **Purpose:** Implementation plans and project phases
- **Features:** Phase-based organization, timeline visualization
- **Content:** Deliverables, tasks, milestones

### FeatureSection
- **Purpose:** Feature requirements and capabilities
- **Features:** Feature categorization, priority indicators
- **Content:** Feature lists, requirements, specifications

### GenericSection
- **Purpose:** Fallback renderer for any content type
- **Features:** Intelligent data type detection, flexible rendering
- **Content:** Any unstructured or unrecognized data

## Technical Implementation

### Content Processing Pipeline
1. **Content Detection** - Identify content type (markdown, JSON, mixed)
2. **Normalization** - Convert to standard PRP format
3. **Section Extraction** - Identify and categorize sections
4. **Component Mapping** - Map sections to appropriate components
5. **Rendering** - Dynamic component rendering with props

### Type System
```typescript
interface PRPContent {
  title?: string;
  version?: string;
  author?: string;
  date?: string;
  status?: string;
  document_type?: string;
  context?: PRPContext;
  user_personas?: Record<string, PRPPersona>;
  user_flows?: Record<string, any>;
  success_metrics?: Record<string, any>;
  implementation_plan?: Record<string, PRPPhase>;
  [key: string]: any;
}
```

### Section Detection Algorithm
- **Pattern Matching** - Key name pattern recognition
- **Content Analysis** - Data structure analysis
- **Confidence Scoring** - Best match selection
- **Fallback Handling** - Generic section for unmatched content

## Integration Points

### Project Management
- **Document Storage** - Integration with document management system
- **Version Control** - Document versioning and history
- **Collaboration** - Multi-user editing and comments
- **Export** - PDF, HTML, and other format exports

### Workflow Integration
- **Task Generation** - Convert plans to actionable tasks
- **Progress Tracking** - Link metrics to project progress
- **Validation** - Requirement validation and testing
- **Approval** - Document review and approval workflows

## Performance Considerations

### Optimization Strategies
- **Lazy Loading** - Load sections on demand
- **Memoization** - Cache processed content
- **Virtual Scrolling** - Handle large documents
- **Code Splitting** - Load components as needed

### Bundle Size
- **Tree Shaking** - Remove unused components
- **Dynamic Imports** - Load sections dynamically
- **Shared Dependencies** - Reuse common utilities
- **Compression** - Optimize asset delivery

## Detailed Documentation

### Component-Specific Documentation
- **[PRPViewer Component](./prp-PRPViewer.md)** - Main viewer component with intelligent content routing
- **[Section Components](./prp-section-components.md)** - All 13 specialized section components (MetadataSection, ContextSection, etc.)
- **[Renderers & Utilities](./prp-renderers-utilities.md)** - Rendering engine and utility functions (6 components)
- **[Types & Exports](./prp-types-exports.md)** - TypeScript definitions and export structure

### Integration Points
- **Parent components:** Project pages, document viewers, admin interfaces
- **Child components:** UI components, form elements, charts
- **Shared utilities:** Markdown parsers, formatters, type definitions

## System Benefits

### Developer Experience
- **Type Safety:** Comprehensive TypeScript interfaces prevent runtime errors
- **Modularity:** Each component handles specific data types and use cases
- **Extensibility:** Easy to add new section types and renderers
- **Consistency:** Unified props interface across all components
- **Documentation:** Self-documenting through TypeScript and JSDoc

### User Experience
- **Performance:** Lazy loading and optimized rendering for large documents
- **Accessibility:** ARIA labels, keyboard navigation, screen reader support
- **Responsive:** Mobile-first design with adaptive layouts
- **Theming:** Dark/light mode support with consistent color schemes
- **Interactivity:** Collapsible sections, smooth animations, intuitive controls

### Content Flexibility
- **Structured Data:** Native support for JSON-based PRP documents
- **Markdown Support:** Full markdown parsing and rendering capabilities
- **Hybrid Content:** Seamless mixing of structured and markdown content
- **Dynamic Detection:** Intelligent section type detection and component mapping
- **Fallback Handling:** Generic renderers for unknown content types

## Notes
- Highly flexible and extensible architecture
- Supports both structured and unstructured content
- Optimized for large, complex documents
- Comprehensive accessibility support
- Performance optimized with lazy loading
- Consistent with overall design system
- Extensive TypeScript support for type safety

---
*Documentation complete and verified - last updated 2025-08-23*
