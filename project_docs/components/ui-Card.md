# Card Component

**File Path:** `archon-ui-main/src/components/ui/Card.tsx`
**Last Updated:** 2025-08-22

## Purpose
A flexible card container component with accent color theming, glow effects, and gradient backgrounds. Provides consistent styling for content containers throughout the application.

## Props/Parameters

### CardProps Interface
```typescript
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  accentColor?: 'purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange' | 'none';
  variant?: 'default' | 'bordered';
}
```

### Props Details
- **children** (React.ReactNode, required): Card content
- **accentColor** ('purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange' | 'none', default: 'none'): Color theme with glow effects
- **variant** ('default' | 'bordered', default: 'default'): Visual style variant
- **...props**: All standard HTML div attributes (className, onClick, etc.)

## Dependencies

### Imports
```typescript
import React from 'react';
```

### Exports
```typescript
export const Card: React.FC<CardProps>
```

## Key Functions/Methods

### Accent Color Configuration
```typescript
const accentColorMap = {
  purple: {
    glow: 'before:shadow-[0_0_10px_2px_rgba(168,85,247,0.4)] dark:before:shadow-[0_0_20px_5px_rgba(168,85,247,0.7)]',
    line: 'before:bg-purple-500',
    border: 'border-purple-300 dark:border-purple-500/30',
    gradientFrom: 'from-purple-100 dark:from-purple-500/20',
    gradientTo: 'to-white dark:to-purple-500/5'
  },
  green: {
    glow: 'before:shadow-[0_0_10px_2px_rgba(16,185,129,0.4)] dark:before:shadow-[0_0_20px_5px_rgba(16,185,129,0.7)]',
    line: 'before:bg-emerald-500',
    border: 'border-emerald-300 dark:border-emerald-500/30',
    gradientFrom: 'from-emerald-100 dark:from-emerald-500/20',
    gradientTo: 'to-white dark:to-emerald-500/5'
  },
  // ... other colors
  none: {
    glow: '',
    line: '',
    border: 'border-gray-200 dark:border-zinc-800/50',
    gradientFrom: 'from-gray-50 dark:from-white/5',
    gradientTo: 'to-white dark:to-transparent'
  }
};
```

### Variant Classes
```typescript
const variantClasses = {
  default: 'border',
  bordered: 'border'
};
```

## Usage Example
```typescript
import { Card } from '@/components/ui/Card';

// Basic card
<Card>
  <h3>Simple Card</h3>
  <p>Basic card content without accent color.</p>
</Card>

// Card with accent color and glow
<Card accentColor="purple" className="p-6">
  <h3 className="text-lg font-semibold mb-2">Purple Accent Card</h3>
  <p>This card has a purple accent line and glow effect.</p>
</Card>

// Green accent card for success states
<Card accentColor="green" variant="bordered">
  <div className="flex items-center space-x-2">
    <CheckIcon className="text-green-500" />
    <span>Success message</span>
  </div>
</Card>

// Blue accent card for information
<Card accentColor="blue" className="hover:scale-105 transition-transform">
  <h4>Interactive Card</h4>
  <p>This card has hover effects and blue accent.</p>
</Card>

// Orange accent card for warnings
<Card accentColor="orange">
  <div className="flex items-start space-x-3">
    <AlertIcon className="text-orange-500 mt-1" />
    <div>
      <h4 className="font-medium">Warning</h4>
      <p className="text-sm text-gray-600">Important information here.</p>
    </div>
  </div>
</Card>

// Card without accent for neutral content
<Card accentColor="none" className="bg-gray-50 dark:bg-gray-900">
  <p>Neutral card without special effects.</p>
</Card>
```

## State Management
No internal state management - purely presentational component

## Side Effects
- Hover shadow effects with smooth transitions
- Backdrop blur effects for glassmorphism design
- Gradient overlays for accent colors

## Visual Features

### Base Styling
- **Backdrop Blur**: `backdrop-blur-md` for glassmorphism effect
- **Gradient Background**: Dynamic gradients from white/transparent
- **Border Radius**: Consistent `rounded-md` corners
- **Padding**: Default `p-4` padding (customizable via className)

### Accent Color Effects (when accentColor !== 'none')
- **Top Accent Line**: 2px colored line at top with glow effect
- **Gradient Overlay**: Colored gradient overlay in top portion
- **Border Color**: Matching border color with opacity
- **Glow Effect**: Subtle shadow glow matching accent color

### Shadow System
- **Base Shadow**: `shadow-[0_10px_30px_-15px_rgba(0,0,0,0.1)]`
- **Dark Mode Shadow**: Enhanced shadows for dark backgrounds
- **Hover Enhancement**: Increased shadow on hover
- **Accent Glow**: Additional glow for accent colors

### Responsive Design
- Works across all screen sizes
- Proper contrast in light/dark modes
- Touch-friendly spacing and sizing

## Theme Support

### Light Mode
- White/light gray backgrounds with transparency
- Subtle shadows and borders
- Bright accent colors with reduced opacity

### Dark Mode
- Dark backgrounds with white transparency
- Enhanced glow effects
- Adjusted accent colors for better contrast

## Related Files
- **Parent components:** All components using card layouts
- **Child components:** Any content components
- **Shared utilities:** Tailwind CSS classes, color system

## Notes
- Uses CSS pseudo-elements (::before, ::after) for accent effects
- Supports all standard HTML div attributes
- Optimized for both light and dark themes
- Glassmorphism design with backdrop blur
- Configurable accent colors with consistent theming
- Smooth transitions for interactive states
- Z-index layering for proper effect stacking
- Responsive and accessible design

---
*Auto-generated documentation - verify accuracy before use*
