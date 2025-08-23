# PRP Section Components Documentation

**File Path:** `archon-ui-main/src/components/prp/sections/` directory
**Last Updated:** 2025-08-22

## Purpose
Comprehensive documentation of all PRP section components that handle specific types of content within Product Requirement Prompt documents. Each component specializes in rendering particular data structures with appropriate formatting and interactivity.

## Section Component Architecture

### Common Interface
All section components implement the `SectionProps` interface:

```typescript
interface SectionProps {
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

### Color System
Consistent accent colors across all sections:
- **Blue** - General content, features
- **Purple** - Context, background
- **Pink** - Personas, users
- **Orange** - Flows, processes
- **Green** - Metrics, success criteria
- **Cyan** - Plans, implementation
- **Indigo** - Technical content
- **Emerald** - Validation, testing

## Core Section Components

### 1. MetadataSection
**File:** `MetadataSection.tsx`
**Purpose:** Document header with title, version, author, and status information

**Key Features:**
- Document title with gradient styling
- Version and author information
- Status badges with color coding
- Date formatting and display
- Responsive layout

**Usage:**
```typescript
<MetadataSection 
  content={prpDocument}
  isDarkMode={isDarkMode}
/>
```

**Content Structure:**
```typescript
{
  title: "OAuth2 Authentication Implementation",
  version: "1.0",
  author: "prp-creator", 
  date: "2025-07-30",
  status: "draft",
  document_type: "prp"
}
```

### 2. ContextSection
**File:** `ContextSection.tsx`
**Purpose:** Background information, scope, and objectives

**Key Features:**
- Expandable content sections
- Icon-based organization (Target, BookOpen, Sparkles)
- Structured background information
- Objective lists with checkmarks
- Requirements breakdown

**Usage:**
```typescript
<ContextSection 
  title="Context"
  data={contextData}
  accentColor="purple"
  isDarkMode={isDarkMode}
/>
```

**Content Structure:**
```typescript
{
  scope: "Authentication system implementation",
  background: "Current system uses basic auth...",
  objectives: [
    "Implement OAuth2 providers",
    "Enhance security",
    "Improve user experience"
  ],
  requirements: {
    functional: ["OAuth2 flow", "Token management"],
    non_functional: ["Performance", "Security"]
  }
}
```

### 3. PersonaSection
**File:** `PersonaSection.tsx`
**Purpose:** User personas with detailed profiles and characteristics

**Key Features:**
- Expandable persona cards
- Role-based organization
- Goals and pain points display
- User journey mapping
- Workflow visualization

**Usage:**
```typescript
<PersonaSection 
  title="User Personas"
  data={personaData}
  accentColor="pink"
  isDarkMode={isDarkMode}
/>
```

**Content Structure:**
```typescript
{
  "developer": {
    name: "Alex Developer",
    role: "Full-stack Developer",
    goals: ["Quick authentication", "Secure access"],
    pain_points: ["Complex setup", "Poor documentation"],
    journey: {
      discovery: "Finds auth requirement",
      evaluation: "Reviews options",
      implementation: "Integrates solution"
    }
  }
}
```

### 4. FlowSection
**File:** `FlowSection.tsx`
**Purpose:** User flows and workflow visualization

**Key Features:**
- Step-by-step flow rendering
- Visual flow indicators
- Decision points and branches
- Process documentation
- Interactive flow navigation

**Usage:**
```typescript
<FlowSection 
  title="User Flows"
  data={flowData}
  accentColor="orange"
  isDarkMode={isDarkMode}
/>
```

**Content Structure:**
```typescript
{
  "authentication_flow": {
    steps: [
      "User clicks login",
      "Redirect to OAuth provider",
      "User authorizes",
      "Redirect back with code",
      "Exchange code for token"
    ],
    decision_points: ["Provider selection", "Consent screen"],
    error_handling: ["Invalid credentials", "Network errors"]
  }
}
```

### 5. MetricsSection
**File:** `MetricsSection.tsx`
**Purpose:** Success metrics and KPIs

**Key Features:**
- Metric categorization
- Progress indicators
- Target vs actual comparisons
- Performance tracking
- Visual metric displays

**Usage:**
```typescript
<MetricsSection 
  title="Success Metrics"
  data={metricsData}
  accentColor="green"
  isDarkMode={isDarkMode}
/>
```

**Content Structure:**
```typescript
{
  "performance": {
    "authentication_time": "< 2 seconds",
    "success_rate": "> 99.5%",
    "user_satisfaction": "> 4.5/5"
  },
  "business": {
    "conversion_rate": "+15%",
    "support_tickets": "-30%",
    "user_retention": "+20%"
  }
}
```

### 6. PlanSection
**File:** `PlanSection.tsx`
**Purpose:** Implementation plans and project phases

**Key Features:**
- Phase-based organization
- Timeline visualization
- Deliverable tracking
- Task breakdown
- Milestone indicators

**Usage:**
```typescript
<PlanSection 
  title="Implementation Plan"
  data={planData}
  accentColor="cyan"
  isDarkMode={isDarkMode}
/>
```

**Content Structure:**
```typescript
{
  "phase_1": {
    duration: "2 weeks",
    deliverables: ["OAuth provider setup", "Basic flow"],
    tasks: [
      {
        title: "Configure Google OAuth",
        files: ["src/auth/google.py"],
        details: "Set up Google OAuth2 configuration"
      }
    ]
  }
}
```

### 7. FeatureSection
**File:** `FeatureSection.tsx`
**Purpose:** Feature requirements and capabilities

**Key Features:**
- Feature categorization
- Priority indicators
- Requirement specifications
- Capability mapping
- Feature dependencies

**Usage:**
```typescript
<FeatureSection 
  title="Features"
  data={featureData}
  accentColor="blue"
  isDarkMode={isDarkMode}
/>
```

**Content Structure:**
```typescript
{
  "core_features": [
    "OAuth2 authentication",
    "Token management",
    "User profile sync"
  ],
  "advanced_features": [
    "Multi-provider support",
    "SSO integration",
    "Custom scopes"
  ],
  "future_features": [
    "Biometric auth",
    "Passwordless login"
  ]
}
```

## Specialized Section Components

### 8. ListSection
**File:** `ListSection.tsx`
**Purpose:** List-based content rendering

**Key Features:**
- Ordered and unordered lists
- Nested list support
- Custom list styling
- Interactive list items
- Collapsible sublists

### 9. ObjectSection
**File:** `ObjectSection.tsx`
**Purpose:** Complex object structure display

**Key Features:**
- Nested object rendering
- Key-value pair display
- Expandable object trees
- Type-aware formatting
- Search and filtering

### 10. KeyValueSection
**File:** `KeyValueSection.tsx`
**Purpose:** Simple key-value pair rendering

**Key Features:**
- Clean key-value layout
- Type-specific formatting
- Sortable pairs
- Copy functionality
- Export options

### 11. GenericSection
**File:** `GenericSection.tsx`
**Purpose:** Fallback renderer for any content type

**Key Features:**
- Intelligent data type detection
- Flexible rendering strategies
- Auto-icon selection
- Adaptive formatting
- Error handling

### 12. RolloutPlanSection
**File:** `RolloutPlanSection.tsx`
**Purpose:** Deployment and rollout plans

**Key Features:**
- Rollout phase visualization
- Risk assessment display
- Rollback procedures
- Success criteria tracking
- Stakeholder communication

### 13. TokenSystemSection
**File:** `TokenSystemSection.tsx`
**Purpose:** Token-based system configurations

**Key Features:**
- Token type definitions
- Usage patterns
- Security considerations
- Integration examples
- Best practices

## Common Patterns

### Collapsible Sections
```typescript
const [isOpen, setIsOpen] = useState(defaultOpen);

return (
  <CollapsibleSectionWrapper
    title={title}
    icon={icon}
    accentColor={accentColor}
    isOpen={isOpen}
    onToggle={() => setIsOpen(!isOpen)}
    isDarkMode={isDarkMode}
  >
    {/* Section content */}
  </CollapsibleSectionWrapper>
);
```

### Color Mapping
```typescript
const colorMap = {
  blue: 'from-blue-400 to-blue-600',
  purple: 'from-purple-400 to-purple-600',
  green: 'from-green-400 to-green-600',
  orange: 'from-orange-400 to-orange-600',
  pink: 'from-pink-400 to-pink-600',
  cyan: 'from-cyan-400 to-cyan-600'
};
```

### Icon Integration
```typescript
import { Target, BookOpen, Users, Workflow, TrendingUp, Calendar } from 'lucide-react';

const sectionIcons = {
  context: <Target className="w-5 h-5" />,
  personas: <Users className="w-5 h-5" />,
  flows: <Workflow className="w-5 h-5" />,
  metrics: <TrendingUp className="w-5 h-5" />,
  plan: <Calendar className="w-5 h-5" />
};
```

## Integration Examples

### Custom Section Override
```typescript
const CustomPersonaSection = ({ title, data, ...props }) => (
  <div className="custom-persona-section">
    <h2>{title}</h2>
    {Object.entries(data).map(([key, persona]) => (
      <div key={key} className="persona-card">
        <img src={persona.avatar} alt={persona.name} />
        <h3>{persona.name}</h3>
        <p>{persona.role}</p>
        <ul>
          {persona.goals.map(goal => <li key={goal}>{goal}</li>)}
        </ul>
      </div>
    ))}
  </div>
);

<PRPViewer 
  content={prpDocument}
  sectionOverrides={{
    personas: CustomPersonaSection
  }}
/>
```

### Dynamic Section Loading
```typescript
const DynamicPRPViewer = ({ content }) => {
  const [sectionOverrides, setSectionOverrides] = useState({});

  useEffect(() => {
    // Load custom sections based on content type
    if (content.document_type === 'technical_spec') {
      import('./TechnicalSpecSection').then(module => {
        setSectionOverrides(prev => ({
          ...prev,
          technical: module.TechnicalSpecSection
        }));
      });
    }
  }, [content.document_type]);

  return (
    <PRPViewer 
      content={content}
      sectionOverrides={sectionOverrides}
    />
  );
};
```

## Related Files
- **Parent components:** PRPViewer, document viewers, project pages
- **Child components:** CollapsibleSectionWrapper, formatters, icons
- **Shared utilities:** Type definitions, color maps, formatters

## Notes
- All sections follow consistent design patterns
- Flexible data structure support
- Comprehensive accessibility features
- Performance optimized with lazy loading
- Extensible architecture for custom sections
- Consistent with overall design system
- Full TypeScript support for type safety

---
*Auto-generated documentation - verify accuracy before use*
