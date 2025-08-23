# Badge Component

**File Path:** `archon-ui-main/src/components/ui/Badge.tsx`
**Last Updated:** 2025-08-22

## Purpose
A small label component for displaying status, categories, tags, or other metadata. Provides consistent styling with color variants and solid/outline options.

## Props/Parameters

### BadgeProps Interface
```typescript
interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  children: React.ReactNode;
  color?: 'purple' | 'green' | 'pink' | 'blue' | 'gray' | 'orange';
  variant?: 'solid' | 'outline';
}
```

### Props Details
- **children** (React.ReactNode, required): Badge content/text
- **color** ('purple' | 'green' | 'pink' | 'blue' | 'gray' | 'orange', default: 'gray'): Color theme
- **variant** ('solid' | 'outline', default: 'outline'): Visual style variant
- **...props**: All standard HTML span attributes (className, onClick, etc.)

## Dependencies

### Imports
```typescript
import React from 'react';
```

### Exports
```typescript
export const Badge: React.FC<BadgeProps>
```

## Key Functions/Methods

### Color Mapping System
```typescript
const colorMap = {
  solid: {
    purple: 'bg-purple-500/10 text-purple-500 dark:bg-purple-500/10 dark:text-purple-500',
    green: 'bg-emerald-500/10 text-emerald-500 dark:bg-emerald-500/10 dark:text-emerald-500',
    pink: 'bg-pink-500/10 text-pink-500 dark:bg-pink-500/10 dark:text-pink-500',
    blue: 'bg-blue-500/10 text-blue-500 dark:bg-blue-500/10 dark:text-blue-500',
    gray: 'bg-gray-200 text-gray-700 dark:bg-zinc-500/10 dark:text-zinc-400',
    orange: 'bg-orange-500/10 text-orange-500 dark:bg-orange-500/10 dark:text-orange-500'
  },
  outline: {
    purple: 'border border-purple-300 text-purple-600 dark:border-purple-500/30 dark:text-purple-500',
    green: 'border border-emerald-300 text-emerald-600 dark:border-emerald-500/30 dark:text-emerald-500',
    pink: 'border border-pink-300 text-pink-600 dark:border-pink-500/30 dark:text-pink-500',
    blue: 'border border-blue-300 text-blue-600 dark:border-blue-500/30 dark:text-blue-500',
    gray: 'border border-gray-300 text-gray-700 dark:border-zinc-700 dark:text-zinc-400',
    orange: 'border border-orange-500 text-orange-500 dark:border-orange-500 dark:text-orange-500 shadow-[0_0_10px_rgba(251,146,60,0.3)]'
  }
};
```

## Usage Example
```typescript
import { Badge } from '@/components/ui/Badge';

// Basic gray badge
<Badge>Default</Badge>

// Status badges
<Badge color="green" variant="solid">Active</Badge>
<Badge color="orange" variant="outline">Pending</Badge>
<Badge color="pink" variant="solid">Error</Badge>

// Category badges
<Badge color="blue">Documentation</Badge>
<Badge color="purple">Feature</Badge>
<Badge color="gray">Archive</Badge>

// Task status badges
<Badge color="green" variant="outline">Completed</Badge>
<Badge color="blue" variant="solid">In Progress</Badge>
<Badge color="gray" variant="outline">Todo</Badge>

// Knowledge type badges
<Badge color="purple" variant="solid">Technical</Badge>
<Badge color="pink" variant="outline">Business</Badge>

// Priority badges
<Badge color="orange" variant="solid">High Priority</Badge>
<Badge color="blue" variant="outline">Medium</Badge>
<Badge color="gray">Low</Badge>

// Custom styling
<Badge 
  color="green" 
  variant="solid"
  className="uppercase font-bold"
>
  Success
</Badge>

// Interactive badges
<Badge 
  color="blue" 
  variant="outline"
  onClick={() => handleTagClick('react')}
  className="cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-500/20"
>
  React
</Badge>
```

## State Management
No internal state management - purely presentational component

## Side Effects
No side effects - static styling component

## Visual Features

### Base Styling
- **Size**: Small text (`text-xs`) with compact padding
- **Shape**: Rounded corners with `rounded` class
- **Layout**: Inline-flex for proper alignment
- **Typography**: Consistent small text sizing

### Variant Differences

#### Solid Variant
- **Background**: Colored background with 10% opacity
- **Text**: Full color intensity
- **Border**: No border
- **Effect**: Filled appearance

#### Outline Variant
- **Background**: Transparent
- **Text**: Colored text
- **Border**: Colored border with opacity
- **Effect**: Outlined appearance

### Special Features

#### Orange Color Special Effect
- **Outline Orange**: Includes glow effect with `shadow-[0_0_10px_rgba(251,146,60,0.3)]`
- **Enhanced Visibility**: Special treatment for warning/attention states

### Theme Support

#### Light Mode
- Bright colors with good contrast
- Gray variants use standard gray palette
- Solid variants use light backgrounds

#### Dark Mode
- Adjusted colors for dark backgrounds
- Zinc colors for gray variants
- Reduced opacity for better integration

## Common Use Cases

### Status Indicators
```typescript
const getStatusBadge = (status: string) => {
  switch (status) {
    case 'active':
      return <Badge color="green" variant="solid">Active</Badge>;
    case 'pending':
      return <Badge color="orange" variant="outline">Pending</Badge>;
    case 'error':
      return <Badge color="pink" variant="solid">Error</Badge>;
    default:
      return <Badge color="gray">Unknown</Badge>;
  }
};
```

### Tag Lists
```typescript
const TagList = ({ tags }: { tags: string[] }) => (
  <div className="flex flex-wrap gap-1">
    {tags.map(tag => (
      <Badge key={tag} color="blue" variant="outline">
        {tag}
      </Badge>
    ))}
  </div>
);
```

### Knowledge Types
```typescript
const KnowledgeTypeBadge = ({ type }: { type: 'technical' | 'business' }) => (
  <Badge 
    color={type === 'technical' ? 'purple' : 'pink'} 
    variant="solid"
  >
    {type}
  </Badge>
);
```

## Related Files
- **Parent components:** Cards, lists, tables, forms
- **Child components:** None (leaf component)
- **Shared utilities:** Tailwind CSS classes, color system

## Notes
- Compact design suitable for inline use
- Consistent color system across variants
- Optimized for both light and dark themes
- No JavaScript functionality - pure CSS styling
- Flexible content support (text, numbers, icons)
- Accessible color contrast ratios
- Easy to extend with additional colors
- Works well in lists and grids

---
*Auto-generated documentation - verify accuracy before use*
