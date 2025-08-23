# useCardTilt

**File Path:** `archon-ui-main/src/hooks/useCardTilt.ts`
**Last Updated:** 2025-01-22

## Purpose
React hook for creating interactive 3D card tilt effects with mouse tracking, reflection, glow effects, and bounce animations.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| options | Partial<TiltOptions> | no | {} | Configuration object for tilt behavior |

### TiltOptions Interface
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| max | number | no | 15 | Maximum tilt angle in degrees |
| scale | number | no | 1.05 | Scale factor on hover |
| speed | number | no | 500 | Transition speed in milliseconds |
| perspective | number | no | 1000 | CSS perspective value in pixels |
| easing | string | no | 'cubic-bezier(.03,.98,.52,.99)' | CSS easing function |

## Dependencies

### Imports
```javascript
import { useState, useRef } from 'react';
```

### Exports
```javascript
export const useCardTilt: (options?: Partial<TiltOptions>) => {
  cardRef: React.RefObject<HTMLDivElement>;
  tiltStyles: object;
  handlers: object;
};
```

## Key Functions/Methods
- **handleMouseMove**: Calculates tilt angles and glow position based on mouse position
- **handleMouseEnter**: Sets hovering state
- **handleMouseLeave**: Resets card to neutral position
- **handleClick**: Triggers bounce animation on click

## Usage Example
```javascript
import { useCardTilt } from '../hooks/useCardTilt';

const MyCard = () => {
  const { cardRef, tiltStyles, handlers } = useCardTilt({
    max: 20,
    scale: 1.1,
    speed: 300,
    perspective: 1200
  });

  return (
    <div
      ref={cardRef}
      style={{
        transform: tiltStyles.transform,
        transition: tiltStyles.transition,
        '--glow-x': `${tiltStyles.glowPosition.x}%`,
        '--glow-y': `${tiltStyles.glowPosition.y}%`,
        '--glow-intensity': tiltStyles.glowIntensity,
        '--reflection-opacity': tiltStyles.reflectionOpacity,
        '--reflection-position': tiltStyles.reflectionPosition
      }}
      {...handlers}
    >
      Card Content
    </div>
  );
};
```

## State Management
- **tiltStyles**: Object containing transform, transition, and effect properties
- **cardRef**: Ref to the card element for DOM manipulation
- **isHovering**: Ref to track hover state

## Side Effects
- **Mouse tracking**: Calculates tilt angles based on mouse position relative to card center
- **3D transforms**: Applies perspective, rotation, and scale transforms
- **Glow effects**: Calculates glow position for CSS custom properties
- **Reflection effects**: Calculates reflection position and opacity
- **Bounce animation**: Applies CSS animation on click

## Related Files
- **Parent components:** KnowledgeItemCard, GroupedKnowledgeItemCard
- **Child components:** None - this is a hook
- **Shared utilities:** None

## Notes
- Calculates tilt based on mouse position relative to card center
- Provides glow position as percentage values for CSS custom properties
- Reflection effects with dynamic positioning
- Smooth transitions with configurable easing
- Bounce animation on click with automatic cleanup
- Resets to neutral state on mouse leave
- Optimized for performance with ref-based hover tracking
- Compatible with CSS custom properties for advanced effects
- Configurable parameters for different card sizes and behaviors

---
*Auto-generated documentation - verify accuracy before use*
