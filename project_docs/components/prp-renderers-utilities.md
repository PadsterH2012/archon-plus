# PRP Renderers & Utilities Documentation

**File Path:** `archon-ui-main/src/components/prp/renderers/` and `archon-ui-main/src/components/prp/utils/` directories
**Last Updated:** 2025-08-22

## Purpose
Documentation for the rendering engine and utility functions that power the PRP system. These components handle content processing, section detection, formatting, and dynamic rendering of PRP documents.

## Renderer Components

### 1. SectionRenderer
**File:** `renderers/SectionRenderer.tsx`
**Purpose:** Dynamic section type detection and component mapping

**Key Features:**
- Intelligent section type detection
- Component mapping and instantiation
- Props forwarding and management
- Error handling and fallbacks
- Performance optimization

**Usage:**
```typescript
<SectionRenderer
  sectionKey="implementation_plan"
  data={planData}
  index={0}
  isDarkMode={isDarkMode}
  sectionOverrides={customComponents}
/>
```

**Detection Algorithm:**
```typescript
const detectSectionType = (key: string, data: any): SectionType => {
  // Pattern matching for section types
  if (key.includes('persona') || key.includes('user')) return 'personas';
  if (key.includes('flow') || key.includes('journey')) return 'flows';
  if (key.includes('metric') || key.includes('success')) return 'metrics';
  if (key.includes('plan') || key.includes('implementation')) return 'plan';
  if (Array.isArray(data)) return 'list';
  if (typeof data === 'object') return 'object';
  return 'generic';
};
```

### 2. CollapsibleSectionRenderer
**File:** `components/CollapsibleSectionRenderer.tsx`
**Purpose:** Wrapper for collapsible section functionality

**Key Features:**
- Expand/collapse animations
- State management
- Icon rotation effects
- Smooth transitions
- Accessibility support

**Usage:**
```typescript
<CollapsibleSectionRenderer
  title="Implementation Plan"
  icon={<Calendar className="w-5 h-5" />}
  accentColor="cyan"
  defaultOpen={true}
  isDarkMode={isDarkMode}
>
  {/* Section content */}
</CollapsibleSectionRenderer>
```

### 3. MarkdownDocumentRenderer
**File:** `components/MarkdownDocumentRenderer.tsx`
**Purpose:** Specialized renderer for markdown-based documents

**Key Features:**
- Markdown parsing and rendering
- Metadata extraction
- Code syntax highlighting
- Table rendering
- Link processing

**Content Processing:**
```typescript
const processMarkdownDocument = (content: any) => {
  if (typeof content === 'string') {
    return { markdown: content };
  }
  
  if (content.markdown || content.content) {
    return {
      ...content,
      markdown: content.markdown || content.content
    };
  }
  
  return content;
};
```

### 4. MarkdownSectionRenderer
**File:** `components/MarkdownSectionRenderer.tsx`
**Purpose:** Individual markdown section processing

**Key Features:**
- Section-level markdown parsing
- Heading extraction
- Content structuring
- Cross-reference handling
- Image processing

### 5. SimpleMarkdown
**File:** `components/SimpleMarkdown.tsx`
**Purpose:** Lightweight markdown parser for basic content

**Key Features:**
- Basic markdown syntax support
- Performance optimized
- Minimal dependencies
- Security focused
- Customizable rendering

### 6. CollapsibleSectionWrapper
**File:** `components/CollapsibleSectionWrapper.tsx`
**Purpose:** Generic wrapper component for making any section collapsible

**Key Features:**
- Controlled and uncontrolled state management
- Smooth expand/collapse animations
- Customizable header content
- Optional collapsible behavior
- Chevron indicator with rotation animation

**Props Interface:**
```typescript
interface CollapsibleSectionWrapperProps {
  children: ReactNode;
  header: ReactNode;
  isCollapsible?: boolean;
  defaultOpen?: boolean;
  isOpen?: boolean;
  onToggle?: () => void;
}
```

**Usage:**
```typescript
<CollapsibleSectionWrapper
  header={<h3>Section Title</h3>}
  defaultOpen={true}
  isCollapsible={true}
  onToggle={() => console.log('Toggled')}
>
  <div>Section content here</div>
</CollapsibleSectionWrapper>
```

**State Management:**
- **Controlled Mode:** When `isOpen` prop is provided, component uses external state
- **Uncontrolled Mode:** When `isOpen` is undefined, component manages internal state
- **Default State:** Uses `defaultOpen` prop for initial state

## Styling & CSS

### PRPViewer.css
**File:** `PRPViewer.css`
**Purpose:** Comprehensive styling for the entire PRP system

**Key Features:**
- **Animations:** Smooth fade-in effects, collapse/expand transitions
- **Responsive Design:** Mobile-first approach with adaptive layouts
- **Dark Mode Support:** Complete dark/light theme compatibility
- **Performance:** Hardware-accelerated animations using CSS transforms
- **Accessibility:** High contrast ratios, focus indicators, reduced motion support

**Animation System:**
```css
/* Fade-in animation for viewer */
.prp-viewer {
  animation: fadeIn 0.5s ease-out;
}

/* Smooth collapse transitions */
.collapsible-content {
  transition: max-height 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.3s ease-out;
}
```

**Component-Specific Styles:**
- **Persona Cards:** Hover effects, gradient backgrounds, shadow transitions
- **Metric Items:** Progress bars, status indicators, interactive elements
- **Flow Diagrams:** Connection lines, node styling, responsive layouts
- **Code Blocks:** Syntax highlighting, copy buttons, scroll indicators

## Utility Functions

### 1. Section Detector
**File:** `utils/sectionDetector.ts`
**Purpose:** Intelligent section type detection and classification

**Key Functions:**
```typescript
export const detectSectionType = (key: string, data: any): SectionDetectorResult => {
  const normalizedKey = key.toLowerCase();
  let type: SectionType = 'generic';
  let confidence = 0;

  // Pattern matching with confidence scoring
  if (normalizedKey.includes('persona') || normalizedKey.includes('user')) {
    type = 'personas';
    confidence = 0.9;
  } else if (normalizedKey.includes('flow') || normalizedKey.includes('journey')) {
    type = 'flows';
    confidence = 0.85;
  }
  // ... additional patterns

  return { type, confidence };
};

export const getSectionIcon = (sectionType: SectionType): ReactNode => {
  const iconMap = {
    context: <Target className="w-5 h-5" />,
    personas: <Users className="w-5 h-5" />,
    flows: <Workflow className="w-5 h-5" />,
    metrics: <TrendingUp className="w-5 h-5" />,
    plan: <Calendar className="w-5 h-5" />,
    features: <Package className="w-5 h-5" />,
    generic: <FileText className="w-5 h-5" />
  };
  
  return iconMap[sectionType] || iconMap.generic;
};

export const formatSectionTitle = (key: string): string => {
  return key
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();
};
```

### 2. Formatters
**File:** `utils/formatters.ts`
**Purpose:** Text and value formatting utilities

**Key Functions:**
```typescript
export const formatKey = (key: string): string => {
  return key
    .replace(/([A-Z])/g, ' $1')
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
    .trim();
};

export const formatValue = (value: any): string => {
  if (value === null || value === undefined) return 'N/A';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'number') return value.toLocaleString();
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'object') return JSON.stringify(value, null, 2);
  return String(value);
};

export const truncateText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};

export const getAccentColor = (sectionType: SectionType): string => {
  const colorMap = {
    metadata: 'blue',
    context: 'purple',
    personas: 'pink',
    flows: 'orange',
    metrics: 'green',
    plan: 'cyan',
    features: 'blue',
    generic: 'gray'
  };
  
  return colorMap[sectionType] || 'gray';
};
```

### 3. Markdown Parser
**File:** `utils/markdownParser.ts`
**Purpose:** Markdown content detection and processing

**Key Functions:**
```typescript
export const isMarkdownContent = (content: string): boolean => {
  const markdownPatterns = [
    /^#{1,6}\s+.+$/m,           // Headers
    /^\*\s+.+$/m,               // Unordered lists
    /^\d+\.\s+.+$/m,            // Ordered lists
    /\*\*.+\*\*/,               // Bold text
    /\*.+\*/,                   // Italic text
    /\[.+\]\(.+\)/,             // Links
    /```[\s\S]*?```/,           // Code blocks
    /`[^`]+`/,                  // Inline code
    /^\|.+\|$/m                 // Tables
  ];
  
  return markdownPatterns.some(pattern => pattern.test(content));
};

export const isDocumentWithMetadata = (content: any): boolean => {
  if (typeof content !== 'object' || content === null) return false;
  
  const hasMetadata = content.title || content.version || content.author;
  const hasMarkdown = content.markdown || content.content;
  
  return hasMetadata && hasMarkdown;
};

export const processContentForPRP = (content: any): any => {
  if (typeof content === 'string') {
    if (isMarkdownContent(content)) {
      return { markdown: content };
    }
    return content;
  }
  
  if (typeof content === 'object' && content !== null) {
    // Look for markdown content in various fields
    const markdownFields = ['markdown', 'content', 'description', 'body'];
    
    for (const field of markdownFields) {
      if (content[field] && typeof content[field] === 'string' && isMarkdownContent(content[field])) {
        return {
          ...content,
          markdown: content[field]
        };
      }
    }
  }
  
  return content;
};
```

### 4. Normalizer
**File:** `utils/normalizer.ts`
**Purpose:** Document structure normalization

**Key Functions:**
```typescript
export const normalizePRPDocument = (content: any): PRPContent => {
  if (!content || typeof content !== 'object') {
    return { title: 'Untitled Document' };
  }
  
  // Ensure required metadata fields
  const normalized: PRPContent = {
    title: content.title || 'Untitled Document',
    version: content.version || '1.0',
    author: content.author || 'Unknown',
    date: content.date || new Date().toISOString().split('T')[0],
    status: content.status || 'draft',
    document_type: content.document_type || 'prp',
    ...content
  };
  
  // Normalize section structures
  if (normalized.user_personas && typeof normalized.user_personas === 'object') {
    normalized.user_personas = normalizePersonas(normalized.user_personas);
  }
  
  if (normalized.implementation_plan && typeof normalized.implementation_plan === 'object') {
    normalized.implementation_plan = normalizePlan(normalized.implementation_plan);
  }
  
  return normalized;
};

const normalizePersonas = (personas: any): Record<string, PRPPersona> => {
  const normalized: Record<string, PRPPersona> = {};
  
  Object.entries(personas).forEach(([key, persona]) => {
    if (typeof persona === 'object' && persona !== null) {
      normalized[key] = {
        name: persona.name || key,
        role: persona.role || 'User',
        goals: Array.isArray(persona.goals) ? persona.goals : [],
        pain_points: Array.isArray(persona.pain_points) ? persona.pain_points : [],
        ...persona
      };
    }
  });
  
  return normalized;
};
```

### 5. Object Renderer
**File:** `utils/objectRenderer.tsx`
**Purpose:** Complex object structure rendering utilities

**Key Functions:**
```typescript
export const renderValue = (value: any, depth: number = 0): ReactNode => {
  if (value === null || value === undefined) {
    return <span className="text-gray-400">null</span>;
  }
  
  if (typeof value === 'boolean') {
    return (
      <span className={value ? 'text-green-600' : 'text-red-600'}>
        {value.toString()}
      </span>
    );
  }
  
  if (typeof value === 'number') {
    return <span className="text-blue-600">{value.toLocaleString()}</span>;
  }
  
  if (typeof value === 'string') {
    if (isUrl(value)) {
      return (
        <a href={value} target="_blank" rel="noopener noreferrer" 
           className="text-blue-500 hover:underline">
          {value}
        </a>
      );
    }
    return <span>{value}</span>;
  }
  
  if (Array.isArray(value)) {
    return renderArray(value, depth);
  }
  
  if (typeof value === 'object') {
    return renderObject(value, depth);
  }
  
  return <span>{String(value)}</span>;
};

export const renderValueInline = (value: any): string => {
  if (value === null || value === undefined) return 'null';
  if (typeof value === 'boolean') return value.toString();
  if (typeof value === 'number') return value.toLocaleString();
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) return `[${value.length} items]`;
  if (typeof value === 'object') return `{${Object.keys(value).length} properties}`;
  return String(value);
};
```

## Integration Patterns

### Custom Section Detection
```typescript
const customSectionDetector = (key: string, data: any): SectionDetectorResult => {
  // Custom business logic for section detection
  if (key.includes('api') && typeof data === 'object') {
    return { type: 'api_spec', confidence: 0.95 };
  }
  
  // Fallback to default detection
  return detectSectionType(key, data);
};
```

### Enhanced Formatting
```typescript
const enhancedFormatters = {
  ...defaultFormatters,
  
  formatCurrency: (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  },
  
  formatDate: (value: string): string => {
    return new Date(value).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
};
```

### Performance Optimization
```typescript
// Memoized section detection
const memoizedDetectSectionType = useMemo(() => {
  return (key: string, data: any) => detectSectionType(key, data);
}, []);

// Lazy loading for large objects
const LazyObjectRenderer = ({ data }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div>
      <button onClick={() => setIsExpanded(!isExpanded)}>
        {isExpanded ? 'Collapse' : 'Expand'} ({Object.keys(data).length} items)
      </button>
      {isExpanded && <ObjectRenderer data={data} />}
    </div>
  );
};
```

## Related Files
- **Parent components:** PRPViewer, section components
- **Child components:** UI components, icons, formatters
- **Shared utilities:** Type definitions, constants, helpers

## Notes
- Highly optimized for performance with large documents
- Extensible architecture for custom renderers
- Comprehensive error handling and fallbacks
- Type-safe with full TypeScript support
- Consistent with overall design system
- Accessible and responsive design
- Memory efficient with lazy loading

---
*Auto-generated documentation - verify accuracy before use*
