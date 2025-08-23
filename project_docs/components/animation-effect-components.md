# Animation & Effect Components Documentation

**File Path:** `archon-ui-main/src/components/animations/`, `archon-ui-main/src/hooks/`, and `archon-ui-main/src/styles/` directories
**Last Updated:** 2025-08-23

## Purpose
Comprehensive documentation of the animation and visual effects system that provides sophisticated animations, transitions, and interactive effects throughout the Archon application. This system includes canvas-based animations, CSS effects, custom hooks, and performance-optimized components.

## Core Animation Components

### 1. Animations.tsx
**File:** `components/animations/Animations.tsx`
**Purpose:** Central collection of reusable animation components and effects

#### ArchonLoadingSpinner
**Purpose:** Animated loading indicator with neon trail effects

**Key Features:**
- **Multi-size Support:** Small, medium, and large variants
- **Neon Trail Effects:** Dual spinning circles with glow effects
- **Logo Integration:** Centered logo with animated borders
- **Performance Optimized:** CSS-based animations for smooth performance

**Props Interface:**
```typescript
interface ArchonLoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  logoSrc?: string;
  className?: string;
}
```

**Size Variants:**
```typescript
const sizeMap = {
  sm: { container: 'w-8 h-8', logo: 'w-4 h-4' },
  md: { container: 'w-16 h-16', logo: 'w-8 h-8' },
  lg: { container: 'w-24 h-24', logo: 'w-12 h-12' }
};
```

**Animation Structure:**
- **First Circle:** Cyan border with clockwise rotation (0.8s)
- **Second Circle:** Fuchsia border with counter-clockwise rotation (1.2s)
- **Blur Effects:** Layered blur for depth and glow
- **Scale Animation:** Subtle scaling for breathing effect

#### NeonGlowEffect
**Purpose:** Container component that adds neon glow effects to child elements

**Key Features:**
- **Color Variants:** 6 predefined neon colors (cyan, fuchsia, blue, purple, green, pink)
- **Intensity Levels:** Low, medium, high glow intensity
- **Border Integration:** Combines with border styles for complete effect
- **Dark Mode Optimization:** Enhanced glow in dark mode

**Props Interface:**
```typescript
interface NeonGlowEffectProps {
  children: React.ReactNode;
  color?: 'cyan' | 'fuchsia' | 'blue' | 'purple' | 'green' | 'pink';
  intensity?: 'low' | 'medium' | 'high';
  className?: string;
}
```

#### EdgeLitEffect
**Purpose:** Top edge lighting effect for UI elements

**Key Features:**
- **Color Matching:** Matches NeonGlowEffect color palette
- **Subtle Animation:** Gentle pulsing effect
- **Positioning:** Absolute positioned top edge highlight
- **Responsive:** Adapts to container width

### 2. DisconnectScreenAnimations.tsx
**File:** `components/animations/DisconnectScreenAnimations.tsx`
**Purpose:** Full-screen canvas-based aurora animation for disconnect states

#### DisconnectScreen Component
**Key Features:**
- **Canvas Animation:** Hardware-accelerated canvas rendering
- **Aurora Borealis Effect:** Multi-layer wave animation with dynamic colors
- **Glassmorphism Design:** Frosted glass medallion with backdrop blur
- **Performance Optimized:** RequestAnimationFrame loop with efficient rendering

**Animation Algorithm:**
```typescript
const drawAurora = () => {
  // Create dark background with vignette
  const gradient = ctx.createRadialGradient(
    canvas.width / 2, canvas.height / 2, 0,
    canvas.width / 2, canvas.height / 2, canvas.width / 1.5
  );
  
  // Draw aurora waves with varying opacity
  const colors = [
    { r: 34, g: 211, b: 238, a: 0.4 },  // Cyan
    { r: 168, g: 85, b: 247, a: 0.4 },  // Purple
    { r: 236, g: 72, b: 153, a: 0.4 },  // Pink
    { r: 59, g: 130, b: 246, a: 0.4 },  // Blue
    { r: 16, g: 185, b: 129, a: 0.4 },  // Green
  ];
  
  colors.forEach((color, index) => {
    const waveHeight = 250;
    const waveOffset = index * 60;
    const speed = 0.001 + index * 0.0002;
    
    // Multi-layered sine wave calculation
    const y = canvas.height / 2 + 
      Math.sin(x * 0.003 + time * speed) * waveHeight +
      Math.sin(x * 0.005 + time * speed * 1.5) * (waveHeight / 2) +
      Math.sin(x * 0.002 + time * speed * 0.5) * (waveHeight / 3) +
      waveOffset - 100;
  });
};
```

**Visual Elements:**
- **Aurora Waves:** 5 animated wave layers with different speeds
- **Glassmorphism Medallion:** Central frosted glass effect
- **Logo Integration:** Embossed logo with drop shadow
- **Status Text:** Animated "DISCONNECTED" text with red glow
- **Responsive Canvas:** Automatically resizes to viewport

## Animation Hooks

### 3. useCardTilt
**File:** `hooks/useCardTilt.ts`
**Purpose:** 3D card tilt effect with mouse tracking

**Key Features:**
- **3D Perspective:** Realistic 3D rotation based on mouse position
- **Reflection Effects:** Dynamic reflection positioning
- **Glow Tracking:** Mouse-following glow effect
- **Smooth Transitions:** Configurable easing and timing
- **Performance Optimized:** Efficient mouse tracking with refs

**Configuration Options:**
```typescript
interface TiltOptions {
  max: number;           // Maximum tilt angle (default: 15)
  scale: number;         // Hover scale factor (default: 1.05)
  speed: number;         // Transition speed in ms (default: 500)
  perspective: number;   // 3D perspective (default: 1000)
  easing: string;        // CSS easing function
}
```

**Return Values:**
```typescript
interface TiltReturn {
  tiltStyles: {
    transform: string;
    transition: string;
    reflectionOpacity: number;
    reflectionPosition: string;
    glowIntensity: number;
    glowPosition: { x: number; y: number };
  };
  cardRef: RefObject<HTMLDivElement>;
  handleMouseMove: (e: React.MouseEvent<HTMLDivElement>) => void;
  handleMouseEnter: () => void;
  handleMouseLeave: () => void;
}
```

### 4. useNeonGlow
**File:** `hooks/useNeonGlow.ts`
**Purpose:** Dynamic neon glow effects with particle system

**Key Features:**
- **Heart Chakra Pattern:** Sacred geometry-based particle positioning
- **Dynamic Particles:** Animated glow particles with pulsing effects
- **Configurable Options:** Opacity, blur, speed, and enable/disable
- **Performance Management:** Efficient DOM manipulation and cleanup
- **CSS Custom Properties:** Dynamic styling through CSS variables

**Configuration Interface:**
```typescript
interface NeonGlowOptions {
  enabled: boolean;
  opacity: number;
  blur: number;
  speed: number;
}
```

**Particle System:**
```typescript
// Heart chakra pattern calculation
const createHeartChakra = () => {
  const points = [];
  for (let i = 0; i < 12; i++) {
    const angle = (i * Math.PI * 2) / 12;
    const radius = 40;
    const x = centerX + Math.cos(angle) * radius;
    const y = centerY + Math.sin(angle) * radius;
    points.push({ x, y });
  }
  
  // Create DOM elements for each particle
  points.forEach((point, index) => {
    const element = document.createElement('div');
    element.style.cssText = `
      position: absolute;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      left: ${point.x}px;
      top: ${point.y}px;
      transform: translate(-50%, -50%);
      background: transparent;
      box-shadow: 
        0 0 10px hsla(220, 90%, 60%, var(--neon-opacity)),
        0 0 20px hsla(260, 80%, 50%, calc(var(--neon-opacity) * 0.7)),
        0 0 30px hsla(220, 70%, 40%, calc(var(--neon-opacity) * 0.5));
      filter: blur(var(--neon-blur));
      animation: neonPulse var(--neon-speed) ease-in-out infinite;
      animation-delay: ${index * 50}ms;
    `;
  });
};
```

### 5. useStaggeredEntrance
**File:** `hooks/useStaggeredEntrance.ts`
**Purpose:** Staggered animation entrance effects for lists and grids

**Key Features:**
- **Configurable Delay:** Customizable stagger timing between items
- **Force Reanimation:** Trigger reanimation with counter changes
- **Framer Motion Integration:** Returns motion variants and props
- **Visibility Management:** Handles entrance timing and visibility states

**Usage Pattern:**
```typescript
const { containerVariants, itemVariants, isVisible } = useStaggeredEntrance(
  items,
  0.15, // 150ms stagger delay
  forceReanimateCounter
);

// In component render
<motion.div
  variants={containerVariants}
  initial="hidden"
  animate={isVisible ? "visible" : "hidden"}
>
  {items.map((item, index) => (
    <motion.div key={item.id} variants={itemVariants}>
      {/* Item content */}
    </motion.div>
  ))}
</motion.div>
```

## CSS Animation Systems

### 6. Card Animations
**File:** `styles/card-animations.css`
**Purpose:** Comprehensive card animation and effect system

**Animation Categories:**

#### 3D Effects
```css
.card-3d {
  transform-style: preserve-3d;
  transform: perspective(1000px);
}

.card-3d-content {
  transform: translateZ(20px);
}
```

#### Reflection Effects
```css
.card-reflection {
  background: linear-gradient(
    120deg, 
    rgba(255,255,255,0) 30%, 
    rgba(255,255,255,0.15) 50%, 
    rgba(255,255,255,0) 70%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}
```

#### Neon Line Effects
```css
.card-neon-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  transition: all 0.3s ease;
  transform: translateZ(40px);
}

.card-neon-line-pulse {
  animation: neon-pulse 2s infinite ease-in-out;
}
```

#### State Animations
- **Bounce Animation:** Scale-based bounce effect for interactions
- **Removal Animation:** Slide and rotate out animation
- **Shuffle Animations:** 3D shuffle effects for card transitions

### 7. Luminous Button Effects
**File:** `styles/luminous-button.css`
**Purpose:** Advanced button glow and pulse animations

**Key Animations:**
```css
@keyframes pulse-glow {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1) translateY(-30%);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05) translateY(-30%);
  }
}

.luminous-button-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
```

## Performance Considerations

### Canvas Optimization
- **RequestAnimationFrame:** Smooth 60fps animations
- **Efficient Rendering:** Minimal canvas operations per frame
- **Memory Management:** Proper cleanup of animation loops
- **Responsive Sizing:** Dynamic canvas resizing

### CSS Performance
- **Hardware Acceleration:** Transform3d and will-change properties
- **Composite Layers:** Isolated animation layers
- **Efficient Selectors:** Optimized CSS selectors
- **Reduced Repaints:** Transform-based animations

### JavaScript Optimization
- **Event Throttling:** Throttled mouse events for smooth tracking
- **DOM Manipulation:** Efficient element creation and cleanup
- **Memory Leaks:** Proper cleanup in useEffect hooks
- **Ref Usage:** Direct DOM access for performance-critical operations

## Usage Patterns

### Basic Animation Integration
```typescript
import { ArchonLoadingSpinner, NeonGlowEffect } from '@/components/animations/Animations';
import { useCardTilt } from '@/hooks/useCardTilt';

const AnimatedCard = () => {
  const { tiltStyles, cardRef, handleMouseMove, handleMouseEnter, handleMouseLeave } = useCardTilt({
    max: 20,
    scale: 1.1,
    speed: 400
  });

  return (
    <NeonGlowEffect color="cyan" intensity="medium">
      <div
        ref={cardRef}
        style={tiltStyles}
        onMouseMove={handleMouseMove}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        className="card-3d"
      >
        <ArchonLoadingSpinner size="md" />
      </div>
    </NeonGlowEffect>
  );
};
```

### Advanced Effect Combinations
```typescript
import { useNeonGlow } from '@/hooks/useNeonGlow';
import { useStaggeredEntrance } from '@/hooks/useStaggeredEntrance';

const AdvancedAnimatedList = ({ items }) => {
  const { containerRef, start, stop, updateOptions } = useNeonGlow({
    enabled: true,
    opacity: 0.8,
    blur: 2,
    speed: 2000
  });

  const { containerVariants, itemVariants, isVisible } = useStaggeredEntrance(items, 0.1);

  return (
    <motion.div
      ref={containerRef}
      variants={containerVariants}
      initial="hidden"
      animate={isVisible ? "visible" : "hidden"}
      onMouseEnter={start}
      onMouseLeave={stop}
    >
      {items.map((item, index) => (
        <motion.div key={item.id} variants={itemVariants}>
          {/* Item content */}
        </motion.div>
      ))}
    </motion.div>
  );
};
```

## Integration Notes

### Framework Dependencies
- **Framer Motion:** Advanced animation orchestration
- **React:** Component lifecycle and state management
- **CSS3:** Hardware-accelerated animations
- **Canvas API:** Complex visual effects

### Browser Compatibility
- **Modern Browsers:** Full feature support
- **Fallback Handling:** Graceful degradation for older browsers
- **Performance Monitoring:** FPS monitoring and optimization
- **Reduced Motion:** Respects user accessibility preferences
