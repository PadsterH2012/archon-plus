# NeonButton Component

**File Path:** `archon-ui-main/src/components/ui/NeonButton.tsx`
**Last Updated:** 2025-08-22

## Purpose
An advanced button component with layered neon effects, customizable corner radii, multiple glow intensities, and sophisticated visual effects. Built with Framer Motion for smooth animations and interactions.

## Props/Parameters

### NeonButtonProps Interface
```typescript
export interface NeonButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  children: React.ReactNode;
  
  // Layer controls
  showLayer2?: boolean;
  layer2Inset?: number; // Inset in pixels, can be negative for overlap
  
  // Colors
  layer1Color?: ColorOption;
  layer2Color?: ColorOption;
  
  // Corner radius per layer
  layer1Radius?: CornerRadius;
  layer2Radius?: CornerRadius;
  
  // Glow controls
  layer1Glow?: GlowIntensity;
  layer2Glow?: GlowIntensity;
  borderGlow?: GlowIntensity;
  
  // Border controls
  layer1Border?: boolean;
  layer2Border?: boolean;
  
  // Text controls
  coloredText?: boolean; // Whether text takes on the button color
  
  // Size
  size?: 'sm' | 'md' | 'lg' | 'xl';
  
  // Basic states
  disabled?: boolean;
  fullWidth?: boolean;
}
```

### Supporting Types
```typescript
export interface CornerRadius {
  topLeft?: number;
  topRight?: number;
  bottomRight?: number;
  bottomLeft?: number;
}

export type GlowIntensity = 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl';
export type ColorOption = 'none' | 'purple' | 'pink' | 'blue' | 'green' | 'red';
```

### Props Details
- **children** (React.ReactNode, required): Button content
- **showLayer2** (boolean, default: false): Enable second layer effect
- **layer2Inset** (number, default: 8): Inset for second layer in pixels
- **layer1Color/layer2Color** (ColorOption, default: 'none'): Color themes for each layer
- **layer1Radius/layer2Radius** (CornerRadius): Custom corner radius for each layer
- **layer1Glow/layer2Glow/borderGlow** (GlowIntensity): Glow intensity controls
- **layer1Border/layer2Border** (boolean): Border visibility controls
- **coloredText** (boolean, default: false): Apply color to text
- **size** ('sm' | 'md' | 'lg' | 'xl', default: 'md'): Button size
- **disabled** (boolean, default: false): Disable interaction
- **fullWidth** (boolean, default: false): Full width button

## Dependencies

### Imports
```typescript
import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { cn } from '../../lib/utils';
```

### Exports
```typescript
export const NeonButton
export interface NeonButtonProps
export interface CornerRadius
export type GlowIntensity
export type ColorOption
```

## Key Functions/Methods

### Size Mappings
```typescript
const sizeClasses = {
  sm: 'px-3 py-1.5',
  md: 'px-4 py-2',
  lg: 'px-6 py-3',
  xl: 'px-8 py-4'
};

const textSizeClasses = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
  xl: 'text-xl'
};
```

### Glow Intensity System
```typescript
const glowSizes = {
  none: { blur: 0, spread: 0, opacity: 0 },
  sm: { blur: 10, spread: 5, opacity: 0.3 },
  md: { blur: 15, spread: 10, opacity: 0.4 },
  lg: { blur: 20, spread: 15, opacity: 0.5 },
  xl: { blur: 30, spread: 20, opacity: 0.6 },
  xxl: { blur: 40, spread: 30, opacity: 0.7 }
};
```

### Color Configuration System
```typescript
const getColorConfig = (color: ColorOption) => ({
  border: 'border-{color}-400/30',
  glow: 'rgba({rgb},0.6)',
  glowDark: 'rgba({rgb},0.5)',
  aurora: 'rgba({rgb},0.8)',
  auroraDark: 'rgba({rgb},0.6)',
  text: 'rgb({rgb})',
  textRgb: '{r}, {g}, {b}'
});
```

## Usage Example
```typescript
import { NeonButton } from '@/components/ui/NeonButton';
import { Zap, Star, Heart } from 'lucide-react';

// Basic neon button
<NeonButton layer1Color="purple" layer1Glow="md">
  Click Me
</NeonButton>

// Advanced layered button
<NeonButton 
  showLayer2={true}
  layer1Color="blue"
  layer2Color="purple"
  layer1Glow="lg"
  layer2Glow="md"
  borderGlow="sm"
  size="lg"
>
  Layered Effect
</NeonButton>

// Custom corner radius
<NeonButton 
  layer1Color="green"
  layer1Radius={{ topLeft: 20, topRight: 5, bottomRight: 20, bottomLeft: 5 }}
  layer1Glow="xl"
>
  Custom Shape
</NeonButton>

// Full-width CTA button
<NeonButton 
  layer1Color="pink"
  layer1Glow="xxl"
  size="xl"
  fullWidth={true}
  coloredText={true}
>
  <Star className="mr-2" size={20} />
  Get Started Now
</NeonButton>

// Disabled state
<NeonButton 
  layer1Color="red"
  layer1Glow="md"
  disabled={true}
>
  Disabled Button
</NeonButton>

// Gaming-style button
<NeonButton 
  showLayer2={true}
  layer1Color="green"
  layer2Color="blue"
  layer2Inset={-4}
  layer1Glow="xl"
  layer2Glow="lg"
  borderGlow="md"
  layer1Radius={{ topLeft: 0, topRight: 15, bottomRight: 0, bottomLeft: 15 }}
  layer2Radius={{ topLeft: 15, topRight: 0, bottomRight: 15, bottomLeft: 0 }}
>
  <Zap className="mr-2" size={16} />
  Power Up
</NeonButton>

// Subtle professional button
<NeonButton 
  layer1Color="blue"
  layer1Glow="sm"
  layer1Border={true}
  size="md"
>
  Professional Action
</NeonButton>

// Interactive form button
<NeonButton 
  layer1Color="purple"
  layer1Glow="md"
  onClick={handleSubmit}
  disabled={isLoading}
  size="lg"
>
  {isLoading ? 'Processing...' : 'Submit Form'}
</NeonButton>
```

## State Management
No internal state management - controlled through props

## Side Effects
- Framer Motion hover and tap animations
- Dynamic box shadow generation
- Layer composition effects
- Glow intensity transitions

## Visual Features

### Layer System
- **Layer 1**: Primary button layer with customizable styling
- **Layer 2**: Optional secondary layer for complex effects
- **Inset Control**: Positive/negative insets for layer positioning
- **Independent Styling**: Each layer has separate colors, borders, and radii

### Glow System
- **Six Intensity Levels**: none, sm, md, lg, xl, xxl
- **Multiple Glow Types**: Layer glows, border glows, external glows
- **Dynamic Generation**: Box shadows generated based on intensity settings
- **Color Matching**: Glows automatically match layer colors

### Animation Features
```typescript
whileHover={!disabled ? { scale: 1.02 } : {}}
whileTap={!disabled ? { scale: 0.98 } : {}}
```

### Corner Radius System
- **Per-Corner Control**: Individual control for each corner
- **Layer Independence**: Different radii for each layer
- **Pixel Precision**: Exact pixel values for custom shapes

## Theme Support
- **Color Variants**: Purple, pink, blue, green, red, none
- **Light/Dark Adaptation**: Automatic color adjustments
- **Opacity Management**: Different opacities for light/dark modes

## Accessibility Features
- **Button Semantics**: Proper button element with ARIA support
- **Keyboard Navigation**: Standard button keyboard behavior
- **Focus Management**: Visible focus indicators
- **Disabled State**: Proper disabled attribute and styling
- **Screen Reader Support**: Content accessible to assistive technology

## Advanced Customization

### Complex Layer Effects
```typescript
<NeonButton 
  showLayer2={true}
  layer1Color="blue"
  layer2Color="purple"
  layer2Inset={-2} // Overlap effect
  layer1Glow="lg"
  layer2Glow="xl"
  borderGlow="md"
  layer1Radius={{ topLeft: 25, topRight: 5, bottomRight: 25, bottomLeft: 5 }}
  layer2Radius={{ topLeft: 5, topRight: 25, bottomRight: 5, bottomLeft: 25 }}
>
  Complex Effect
</NeonButton>
```

### Gaming UI Buttons
```typescript
const GameButton = ({ children, variant = 'primary' }) => {
  const variants = {
    primary: { color: 'green', glow: 'xl' },
    secondary: { color: 'blue', glow: 'lg' },
    danger: { color: 'red', glow: 'lg' }
  };
  
  return (
    <NeonButton 
      layer1Color={variants[variant].color}
      layer1Glow={variants[variant].glow}
      borderGlow="sm"
      size="lg"
    >
      {children}
    </NeonButton>
  );
};
```

### Dynamic Glow Intensity
```typescript
const [glowIntensity, setGlowIntensity] = useState<GlowIntensity>('md');

<NeonButton 
  layer1Color="purple"
  layer1Glow={glowIntensity}
  onMouseEnter={() => setGlowIntensity('xl')}
  onMouseLeave={() => setGlowIntensity('md')}
>
  Hover for Glow
</NeonButton>
```

## Performance Considerations
- **CSS-based Effects**: Uses CSS box-shadow for performance
- **Framer Motion**: Optimized animations with hardware acceleration
- **Conditional Rendering**: Glows only rendered when needed
- **Memoization**: Color configs computed once per render

## Related Files
- **Parent components:** Gaming interfaces, CTAs, special actions
- **Child components:** Icons, text content
- **Shared utilities:** Framer Motion, cn utility, color system

## Notes
- Most advanced button component in the system
- Designed for high-impact visual elements
- Extensive customization options
- Performance optimized despite visual complexity
- Consistent with overall design system
- Accessibility compliant
- Suitable for gaming, creative, and premium interfaces

---
*Auto-generated documentation - verify accuracy before use*
