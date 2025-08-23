# KnowledgeItemSkeleton

**File Path:** `archon-ui-main/src/components/knowledge-base/KnowledgeItemSkeleton.tsx`
**Last Updated:** 2025-01-22

## Purpose
Loading skeleton components for knowledge base items providing visual placeholders during data loading with shimmer animations.

## Props/Parameters
No props required - these are static skeleton components.

## Dependencies

### Imports
```javascript
import React from 'react';
import { Card } from '../ui/Card';
```

### Exports
```javascript
export const KnowledgeItemSkeleton: React.FC;
export const KnowledgeGridSkeleton: React.FC;
export const KnowledgeTableSkeleton: React.FC;
```

## Key Functions/Methods
- **KnowledgeItemSkeleton**: Individual card skeleton with shimmer effect
- **KnowledgeGridSkeleton**: Grid layout skeleton with 6 card placeholders
- **KnowledgeTableSkeleton**: Table layout skeleton with header and 5 rows

## Usage Example
```javascript
import { 
  KnowledgeItemSkeleton, 
  KnowledgeGridSkeleton, 
  KnowledgeTableSkeleton 
} from '../components/knowledge-base/KnowledgeItemSkeleton';

// Individual skeleton
<KnowledgeItemSkeleton />

// Grid view loading
{loading ? <KnowledgeGridSkeleton /> : <KnowledgeGrid items={items} />}

// Table view loading
{loading ? <KnowledgeTableSkeleton /> : <KnowledgeTable items={items} />}
```

## State Management
No state management - pure display components

## Side Effects
No side effects - static skeleton components with CSS animations

## Related Files
- **Parent components:** KnowledgeBasePage
- **Child components:** Card (UI component)
- **Shared utilities:** None

## Notes
- Shimmer animation effect for enhanced loading experience
- Responsive grid layout matching actual content structure
- Dark mode support with appropriate color schemes
- Pulse animations for individual skeleton elements
- Matches the structure of actual KnowledgeItemCard components
- Table skeleton includes proper header and row structure
- Optimized for performance with CSS-only animations

---
*Auto-generated documentation - verify accuracy before use*
