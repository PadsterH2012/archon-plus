# Button Component

**File Path:** `archon-ui-main/src/components/ui/Button.tsx`
**Last Updated:** 2025-08-22

## Purpose
A customizable button component providing various styles, sizes, and color options with neon glow effects and luminous animations. Core UI building block used throughout the application.

## Props/Parameters

### ButtonProps Interface
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  accentColor?: 'purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange';
  neonLine?: boolean;
  icon?: React.ReactNode;
}
```

### Props Details
- **children** (React.ReactNode, required): Button content/text
- **variant** ('primary' | 'secondary' | 'outline' | 'ghost', default: 'primary'): Visual style variant
- **size** ('sm' | 'md' | 'lg', default: 'md'): Button size
- **accentColor** ('purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange', default: 'purple'): Color theme
- **neonLine** (boolean, default: false): Show neon line below button
- **icon** (React.ReactNode, optional): Icon to display before text
- **...props**: All standard HTML button attributes (onClick, disabled, etc.)

## Dependencies

### Imports
```typescript
import React from 'react';
```

### Exports
```typescript
export const Button: React.FC<ButtonProps>
```

## Key Functions/Methods

### Size Classes
```typescript
const sizeClasses = {
  sm: 'text-xs px-3 py-1.5 rounded',
  md: 'text-sm px-4 py-2 rounded-md',
  lg: 'text-base px-6 py-2.5 rounded-md'
};
```

### Variant Classes
```typescript
const variantClasses = {
  primary: `relative overflow-hidden backdrop-blur-md font-medium
    bg-${accentColor}-500/80 text-black dark:text-white
    border border-${accentColor}-500/50 border-t-${accentColor}-300
    shadow-lg shadow-${accentColor}-500/40 hover:shadow-xl hover:shadow-${accentColor}-500/50
    group`,
  secondary: `bg-black/90 border text-white border-${accentColor}-500 text-${accentColor}-400`,
  outline: `bg-white dark:bg-transparent border text-gray-800 dark:text-white 
    border-${accentColor}-500 hover:bg-${accentColor}-500/10`,
  ghost: 'bg-transparent text-gray-700 dark:text-white hover:bg-gray-100/50 dark:hover:bg-white/5'
};
```

### Neon Line Colors
```typescript
const neonLineColor = {
  purple: 'bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.8)]',
  green: 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]',
  pink: 'bg-pink-500 shadow-[0_0_10px_rgba(236,72,153,0.8)]',
  blue: 'bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)]',
  cyan: 'bg-cyan-500 shadow-[0_0_10px_rgba(34,211,238,0.8)]',
  orange: 'bg-orange-500 shadow-[0_0_10px_rgba(249,115,22,0.8)]'
};
```

## Usage Example
```typescript
import { Button } from '@/components/ui/Button';
import { Plus, Save } from 'lucide-react';

// Basic usage
<Button onClick={handleClick}>
  Click me
</Button>

// Primary button with icon
<Button 
  variant="primary" 
  size="lg" 
  accentColor="green"
  icon={<Plus size={16} />}
  onClick={handleSave}
>
  Add Item
</Button>

// Secondary button with neon line
<Button 
  variant="secondary" 
  accentColor="blue"
  neonLine={true}
  disabled={loading}
>
  {loading ? 'Loading...' : 'Submit'}
</Button>

// Ghost button for subtle actions
<Button 
  variant="ghost" 
  size="sm"
  onClick={handleCancel}
>
  Cancel
</Button>

// Outline button with custom styling
<Button 
  variant="outline" 
  accentColor="orange"
  className="w-full"
>
  Full Width Button
</Button>
```

## State Management
No internal state management - controlled through props

## Side Effects
- Hover effects with luminous glow animations
- Focus states for accessibility
- Transition animations on state changes

## Visual Features

### Primary Variant Special Effects
- **Luminous Inner Glow**: Animated inner light source with group hover effects
- **Top Highlight Line**: White highlight line at top border
- **Outer Glow Effect**: Dynamic box shadow based on accent color
- **Scale Animation**: Subtle scale effect on hover

### Accessibility Features
- Proper ARIA attributes
- Keyboard navigation support
- Focus indicators
- Screen reader compatible

## Related Files
- **Parent components:** All pages and components using buttons
- **Child components:** Icon components (lucide-react)
- **Shared utilities:** Tailwind CSS classes, color system

## Notes
- Uses Tailwind CSS for styling with dynamic color classes
- Supports all standard HTML button attributes
- Optimized for both light and dark themes
- Includes advanced visual effects for primary variant
- Icon support with proper spacing
- Responsive design with size variants
- Accessibility compliant with proper focus states

---
*Auto-generated documentation - verify accuracy before use*
