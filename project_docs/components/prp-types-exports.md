# PRP Types & Exports Documentation

**File Path:** `archon-ui-main/src/components/prp/types/prp.types.ts` and `archon-ui-main/src/components/prp/index.ts`
**Last Updated:** 2025-08-23

## Purpose
Documentation for the TypeScript type definitions and export structure that power the PRP (Product Requirement Prompt) system. These types ensure type safety and provide clear interfaces for all PRP components.

## Core Type Definitions

### 1. SectionType
**Purpose:** Enumeration of all supported PRP section types

```typescript
export type SectionType = 
  | 'metadata'
  | 'context'
  | 'personas'
  | 'flows'
  | 'metrics'
  | 'plan'
  | 'list'
  | 'object'
  | 'keyvalue'
  | 'features'
  | 'generic';
```

**Usage:** Used by the section detector and renderer to determine appropriate component mapping.

### 2. SectionProps Interface
**Purpose:** Base interface for all PRP section components

```typescript
export interface SectionProps {
  title: string;
  data: any;
  icon?: ReactNode;
  accentColor?: string;
  defaultOpen?: boolean;
  isDarkMode?: boolean;
  isCollapsible?: boolean;
  onToggle?: () => void;
  isOpen?: boolean;
}
```

**Key Properties:**
- `title` - Section display title (required)
- `data` - Section content data (required, flexible type)
- `icon` - Optional React icon component
- `accentColor` - Theme color for section styling
- `defaultOpen` - Initial collapsed/expanded state
- `isDarkMode` - Dark theme flag
- `isCollapsible` - Whether section can be collapsed
- `onToggle` - Callback for collapse/expand events
- `isOpen` - Controlled state for collapse/expand

### 3. PRPMetadata Interface
**Purpose:** Document metadata structure

```typescript
export interface PRPMetadata {
  title?: string;
  version?: string;
  author?: string;
  date?: string;
  status?: string;
  document_type?: string;
  [key: string]: any;
}
```

**Common Values:**
- `status`: "draft" | "review" | "approved" | "deprecated"
- `document_type`: "prp" | "spec" | "design" | "markdown"

### 4. PRPContext Interface
**Purpose:** Context section data structure

```typescript
export interface PRPContext {
  scope?: string;
  background?: string;
  objectives?: string[];
  requirements?: any;
  [key: string]: any;
}
```

### 5. PRPPersona Interface
**Purpose:** User persona data structure

```typescript
export interface PRPPersona {
  name?: string;
  role?: string;
  goals?: string[];
  pain_points?: string[];
  journey?: Record<string, any>;
  workflow?: Record<string, any>;
  [key: string]: any;
}
```

### 6. PRPPhase Interface
**Purpose:** Implementation phase structure

```typescript
export interface PRPPhase {
  duration?: string;
  deliverables?: string[];
  tasks?: any[];
  [key: string]: any;
}
```

### 7. PRPContent Interface
**Purpose:** Complete PRP document structure

```typescript
export interface PRPContent {
  // Metadata fields
  title?: string;
  version?: string;
  author?: string;
  date?: string;
  status?: string;
  document_type?: string;
  
  // Section fields
  context?: PRPContext;
  user_personas?: Record<string, PRPPersona>;
  user_flows?: Record<string, any>;
  success_metrics?: Record<string, string[] | Record<string, any>>;
  implementation_plan?: Record<string, PRPPhase>;
  validation_gates?: Record<string, string[]>;
  technical_implementation?: Record<string, any>;
  ui_improvements?: Record<string, any>;
  information_architecture?: Record<string, any>;
  current_state_analysis?: Record<string, any>;
  component_architecture?: Record<string, any>;
  
  // Flexible for additional fields
  [key: string]: any;
}
```

## Utility Types

### 8. SectionDetectorResult
**Purpose:** Result from section type detection

```typescript
export interface SectionDetectorResult {
  type: SectionType;
  confidence: number;
}
```

### 9. SectionComponentProps
**Purpose:** Extended props for section components

```typescript
export interface SectionComponentProps extends SectionProps {
  content: PRPContent;
  sectionKey: string;
}
```

## Constants & Configuration

### 10. Section Color Map
**Purpose:** Consistent color theming across sections

```typescript
export const sectionColorMap: Record<string, string> = {
  metadata: 'blue',
  context: 'purple',
  personas: 'pink',
  flows: 'orange',
  metrics: 'green',
  plan: 'cyan',
  technical: 'indigo',
  validation: 'emerald',
  generic: 'gray'
};
```

### 11. Icon Sizes
**Purpose:** Standardized icon sizing

```typescript
export const ICON_SIZES = {
  section: 'w-5 h-5',
  subsection: 'w-4 h-4',
  item: 'w-3 h-3'
} as const;
```

## Export Structure

### Main Exports (`index.ts`)

**Component Exports:**
```typescript
// Main viewer component
export { PRPViewer } from './PRPViewer';

// All section components (13 total)
export { MetadataSection } from './sections/MetadataSection';
export { ContextSection } from './sections/ContextSection';
export { PersonaSection } from './sections/PersonaSection';
export { FlowSection } from './sections/FlowSection';
export { MetricsSection } from './sections/MetricsSection';
export { PlanSection } from './sections/PlanSection';
export { ListSection } from './sections/ListSection';
export { ObjectSection } from './sections/ObjectSection';
export { KeyValueSection } from './sections/KeyValueSection';
export { FeatureSection } from './sections/FeatureSection';
export { GenericSection } from './sections/GenericSection';

// Renderer components
export { SectionRenderer } from './renderers/SectionRenderer';
```

**Type Exports:**
```typescript
// All types from prp.types.ts
export * from './types/prp.types';
```

**Utility Exports:**
```typescript
// Section detection utilities
export { detectSectionType, formatSectionTitle, getSectionIcon } from './utils/sectionDetector';

// Formatting utilities
export { formatKey, formatValue, truncateText, getAccentColor } from './utils/formatters';
```

## Usage Examples

### Basic Type Usage
```typescript
import { PRPContent, SectionProps } from '@/components/prp';

const prpDocument: PRPContent = {
  title: "OAuth Implementation",
  version: "1.0",
  author: "prp-creator",
  status: "draft",
  context: {
    scope: "Authentication system",
    objectives: ["Secure login", "User management"]
  }
};

const CustomSection: React.FC<SectionProps> = ({ title, data, isDarkMode }) => {
  return (
    <div className={isDarkMode ? 'dark' : ''}>
      <h3>{title}</h3>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
};
```

### Component Import Patterns
```typescript
// Import specific components
import { PRPViewer, MetadataSection, ContextSection } from '@/components/prp';

// Import types
import type { PRPContent, SectionProps } from '@/components/prp';

// Import utilities
import { detectSectionType, formatKey } from '@/components/prp';
```

## Type Safety Benefits

1. **Compile-time Validation:** TypeScript catches type mismatches during development
2. **IntelliSense Support:** IDE provides autocomplete and documentation
3. **Refactoring Safety:** Type system ensures changes don't break existing code
4. **Documentation:** Types serve as living documentation of expected data structures
5. **Component Contracts:** Clear interfaces between components and their consumers

## Integration Notes

- All PRP components implement the `SectionProps` interface for consistency
- The `PRPContent` interface supports both structured and flexible data
- Color theming is centralized through `sectionColorMap`
- Icon sizing follows standardized constants
- Export structure provides clean, organized access to all PRP functionality
