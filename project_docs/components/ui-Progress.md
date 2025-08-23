# Progress Component

**File Path:** `archon-ui-main/src/components/ui/Progress.tsx`
**Last Updated:** 2025-08-22

## Purpose
A flexible progress bar component with multiple variants, sizes, and animation options. Used to display completion status, loading states, and progress tracking throughout the application.

## Props/Parameters

### ProgressProps Interface
```typescript
export interface ProgressProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  label?: string;
  className?: string;
  animated?: boolean;
}
```

### Props Details
- **value** (number, required): Current progress value
- **max** (number, default: 100): Maximum value for progress calculation
- **size** ('sm' | 'md' | 'lg', default: 'md'): Progress bar height
- **variant** ('default' | 'success' | 'warning' | 'error', default: 'default'): Color theme
- **showLabel** (boolean, default: false): Show label and percentage
- **label** (string, optional): Custom label text (defaults to percentage)
- **className** (string, optional): Additional CSS classes
- **animated** (boolean, default: false): Enable gradient animation

## Dependencies

### Imports
```typescript
import React from 'react';
import { clsx } from 'clsx';
```

### Exports
```typescript
export const Progress: React.FC<ProgressProps>
```

## Key Functions/Methods

### Percentage Calculation
```typescript
const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
```

### Container Classes
```typescript
const containerClasses = clsx(
  'w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden',
  {
    'h-1': size === 'sm',
    'h-2': size === 'md', 
    'h-3': size === 'lg',
  },
  className
);
```

### Bar Classes with Variants
```typescript
const barClasses = clsx(
  'h-full transition-all duration-300 ease-out rounded-full',
  {
    // Static variants
    'bg-blue-500': variant === 'default',
    'bg-green-500': variant === 'success',
    'bg-yellow-500': variant === 'warning',
    'bg-red-500': variant === 'error',
    
    // Animated variants
    'bg-gradient-to-r from-blue-400 to-blue-600 bg-size-200 animate-pulse': animated && variant === 'default',
    'bg-gradient-to-r from-green-400 to-green-600 bg-size-200 animate-pulse': animated && variant === 'success',
    'bg-gradient-to-r from-yellow-400 to-yellow-600 bg-size-200 animate-pulse': animated && variant === 'warning',
    'bg-gradient-to-r from-red-400 to-red-600 bg-size-200 animate-pulse': animated && variant === 'error',
  }
);
```

## Usage Example
```typescript
import { Progress } from '@/components/ui/Progress';

// Basic progress bar
<Progress value={75} />

// Progress with label
<Progress 
  value={45} 
  showLabel={true}
  label="Upload Progress"
/>

// Success variant with custom max
<Progress 
  value={8}
  max={10}
  variant="success"
  showLabel={true}
  label="Tasks Completed"
/>

// Large animated progress bar
<Progress 
  value={60}
  size="lg"
  variant="default"
  animated={true}
  showLabel={true}
/>

// Warning progress with custom styling
<Progress 
  value={85}
  variant="warning"
  showLabel={true}
  label="Storage Usage"
  className="mb-4"
/>

// Error state progress
<Progress 
  value={100}
  variant="error"
  showLabel={true}
  label="Failed Operations"
/>

// Small progress indicator
<Progress 
  value={30}
  size="sm"
  variant="success"
/>

// Custom label with percentage
<Progress 
  value={67}
  showLabel={true}
  label="Project Completion"
  variant="default"
/>

// Animated loading state
<Progress 
  value={25}
  animated={true}
  showLabel={true}
  label="Processing..."
  variant="default"
/>
```

## State Management
No internal state management - controlled through props

## Side Effects
- Smooth transitions on value changes
- Pulse animation when animated prop is true
- Automatic percentage calculation and clamping

## Visual Features

### Size Variants
- **Small (sm)**: 4px height (`h-1`) - for compact displays
- **Medium (md)**: 8px height (`h-2`) - default size
- **Large (lg)**: 12px height (`h-3`) - for prominent progress

### Color Variants
- **Default**: Blue theme (`bg-blue-500`)
- **Success**: Green theme (`bg-green-500`)
- **Warning**: Yellow theme (`bg-yellow-500`)
- **Error**: Red theme (`bg-red-500`)

### Animation Features
- **Gradient Animation**: Animated gradient backgrounds when `animated={true}`
- **Pulse Effect**: Subtle pulse animation for loading states
- **Smooth Transitions**: 300ms ease-out transitions on value changes

### Label System
- **Automatic Percentage**: Shows calculated percentage when no custom label
- **Custom Labels**: Support for descriptive labels
- **Dual Display**: Shows both label and percentage when `showLabel={true}`

## Accessibility Features
- **ARIA Attributes**: Proper `role="progressbar"` with `aria-valuenow` and `aria-valuemax`
- **Screen Reader Support**: Semantic HTML structure
- **Keyboard Navigation**: Focusable when interactive

## Theme Support

### Light Mode
- Light gray background (`bg-gray-200`)
- Bright progress colors
- Dark text for labels

### Dark Mode
- Dark gray background (`bg-gray-700`)
- Consistent progress colors
- Light text for labels

## Common Use Cases

### File Upload Progress
```typescript
const [uploadProgress, setUploadProgress] = useState(0);

<Progress 
  value={uploadProgress}
  showLabel={true}
  label="Uploading file..."
  animated={uploadProgress < 100}
  variant={uploadProgress === 100 ? 'success' : 'default'}
/>
```

### Task Completion
```typescript
const completedTasks = tasks.filter(t => t.status === 'done').length;
const totalTasks = tasks.length;

<Progress 
  value={completedTasks}
  max={totalTasks}
  variant="success"
  showLabel={true}
  label={`${completedTasks}/${totalTasks} tasks completed`}
/>
```

### Storage Usage
```typescript
const storagePercentage = (usedStorage / totalStorage) * 100;

<Progress 
  value={storagePercentage}
  variant={storagePercentage > 90 ? 'error' : storagePercentage > 75 ? 'warning' : 'default'}
  showLabel={true}
  label="Storage Usage"
/>
```

## Related Files
- **Parent components:** Dashboards, forms, upload components, task lists
- **Child components:** None (leaf component)
- **Shared utilities:** clsx for class management, Tailwind CSS

## Notes
- Automatic value clamping between 0 and max
- Responsive design works on all screen sizes
- Smooth animations enhance user experience
- Flexible labeling system for different contexts
- Consistent with overall design system
- Optimized for both light and dark themes
- ARIA compliant for accessibility
- CSS-only animations for performance

---
*Auto-generated documentation - verify accuracy before use*
