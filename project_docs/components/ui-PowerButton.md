# PowerButton Component

**File Path:** `archon-ui-main/src/components/ui/PowerButton.tsx`
**Last Updated:** 2025-08-22

## Purpose
A power button component with on/off states, animated glow effects, and customizable colors. Features Framer Motion animations, inner/outer glow effects, and a realistic power button appearance.

## Props/Parameters

### PowerButtonProps Interface
```typescript
interface PowerButtonProps {
  isOn: boolean;
  onClick: () => void;
  color?: 'purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange';
  size?: number;
}
```

### Props Details
- **isOn** (boolean, required): Current power state (on/off)
- **onClick** (() => void, required): Click handler function
- **color** ('purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange', default: 'blue'): Color theme
- **size** (number, default: 40): Button size in pixels

## Dependencies

### Imports
```typescript
import React from 'react';
import { motion } from 'framer-motion';
```

### Exports
```typescript
export const PowerButton: React.FC<PowerButtonProps>
```

## Key Functions/Methods

### Color Configuration System
```typescript
const colorMap = {
  purple: {
    border: 'border-purple-400',
    glow: 'shadow-[0_0_15px_rgba(168,85,247,0.8)]',
    glowHover: 'hover:shadow-[0_0_25px_rgba(168,85,247,1)]',
    fill: 'bg-purple-400',
    innerGlow: 'shadow-[inset_0_0_10px_rgba(168,85,247,0.8)]'
  },
  // ... other colors
};
```

### Color Value Helper
```typescript
const getColorValue = (color: string) => {
  const colorValues = {
    purple: 'rgb(168,85,247)',
    green: 'rgb(16,185,129)',
    pink: 'rgb(236,72,153)',
    blue: 'rgb(59,130,246)',
    cyan: 'rgb(34,211,238)',
    orange: 'rgb(249,115,22)'
  };
  return colorValues[color as keyof typeof colorValues] || colorValues.blue;
};
```

## Usage Example
```typescript
import { PowerButton } from '@/components/ui/PowerButton';
import { useState } from 'react';

// Basic power button
const [isOn, setIsOn] = useState(false);

<PowerButton 
  isOn={isOn}
  onClick={() => setIsOn(!isOn)}
/>

// Colored power button
<PowerButton 
  isOn={systemActive}
  onClick={toggleSystem}
  color="green"
  size={50}
/>

// Settings panel power buttons
<div className="space-y-4">
  <div className="flex items-center justify-between">
    <span>Notifications</span>
    <PowerButton 
      isOn={notifications}
      onClick={() => setNotifications(!notifications)}
      color="blue"
      size={32}
    />
  </div>
  
  <div className="flex items-center justify-between">
    <span>Auto-sync</span>
    <PowerButton 
      isOn={autoSync}
      onClick={() => setAutoSync(!autoSync)}
      color="green"
      size={32}
    />
  </div>
  
  <div className="flex items-center justify-between">
    <span>Dark Mode</span>
    <PowerButton 
      isOn={darkMode}
      onClick={() => setDarkMode(!darkMode)}
      color="purple"
      size={32}
    />
  </div>
</div>

// System control panel
<div className="grid grid-cols-2 gap-4">
  <div className="text-center">
    <PowerButton 
      isOn={serverStatus}
      onClick={toggleServer}
      color="green"
      size={60}
    />
    <p className="mt-2">Server</p>
  </div>
  
  <div className="text-center">
    <PowerButton 
      isOn={databaseStatus}
      onClick={toggleDatabase}
      color="blue"
      size={60}
    />
    <p className="mt-2">Database</p>
  </div>
  
  <div className="text-center">
    <PowerButton 
      isOn={cacheStatus}
      onClick={toggleCache}
      color="orange"
      size={60}
    />
    <p className="mt-2">Cache</p>
  </div>
  
  <div className="text-center">
    <PowerButton 
      isOn={monitoringStatus}
      onClick={toggleMonitoring}
      color="pink"
      size={60}
    />
    <p className="mt-2">Monitoring</p>
  </div>
</div>

// Gaming interface
<div className="gaming-controls">
  <PowerButton 
    isOn={gameActive}
    onClick={toggleGame}
    color="cyan"
    size={80}
  />
</div>

// Device control
const DeviceControl = ({ device }) => (
  <div className="device-card">
    <h3>{device.name}</h3>
    <PowerButton 
      isOn={device.isActive}
      onClick={() => toggleDevice(device.id)}
      color={device.isActive ? 'green' : 'orange'}
      size={45}
    />
    <p>{device.isActive ? 'Online' : 'Offline'}</p>
  </div>
);
```

## State Management
No internal state management - controlled through props

## Side Effects
- Framer Motion hover and tap animations
- Dynamic glow effects based on state
- Color transitions on state changes

## Visual Features

### Power Button Design
- **Circular Shape**: Perfect circle with customizable size
- **Gradient Background**: Dark gradient from gray-900 to black
- **Border**: Colored border matching accent color
- **Realistic Appearance**: Mimics physical power button

### Glow System
- **Off State**: Subtle shadow for depth
- **On State**: Bright colored glow effect
- **Hover Enhancement**: Increased glow intensity on hover
- **Outer Ring**: Additional glow ring effect

### Animation Features
```typescript
whileHover={{ scale: 1.1 }}
whileTap={{ scale: 0.95 }}
```

### Multi-Layer Effects
- **Outer Ring Glow**: Blurred border effect
- **Inner Power Symbol**: Animated power icon
- **Pulsing Animation**: Breathing effect when on
- **Scale Animations**: Hover and tap feedback

## Theme Support
- **Color Variants**: Purple, green, pink, blue, cyan, orange
- **Dark Design**: Optimized for dark interfaces
- **Glow Effects**: Enhanced visibility in dark themes

## Accessibility Features
- **Button Semantics**: Proper button element
- **Keyboard Support**: Standard button keyboard behavior
- **Focus Indicators**: Visible focus states
- **Screen Reader Support**: Accessible button functionality

## Advanced Visual Effects

### Power Symbol Animation
```typescript
// Inner power symbol with rotation and opacity
<motion.div
  className="absolute inset-0 flex items-center justify-center"
  animate={{
    rotate: isOn ? 0 : 180,
    opacity: isOn ? 1 : 0.3
  }}
  transition={{ duration: 0.3 }}
>
  <div className={`w-3 h-3 rounded-full ${styles.fill}`} />
</motion.div>
```

### Pulsing Effect
```typescript
// Pulsing animation when active
animate={{
  scale: isOn ? [1, 1.05, 1] : 1,
  opacity: isOn ? [0.8, 1, 0.8] : 0.3
}}
transition={{
  duration: 2,
  repeat: isOn ? Infinity : 0,
  ease: "easeInOut"
}}
```

## Common Use Cases

### System Dashboard
```typescript
const SystemDashboard = () => {
  const [services, setServices] = useState({
    api: true,
    database: false,
    cache: true,
    monitoring: true
  });

  const toggleService = (service: string) => {
    setServices(prev => ({ ...prev, [service]: !prev[service] }));
  };

  return (
    <div className="grid grid-cols-2 gap-6">
      {Object.entries(services).map(([service, isActive]) => (
        <div key={service} className="text-center">
          <PowerButton 
            isOn={isActive}
            onClick={() => toggleService(service)}
            color={isActive ? 'green' : 'orange'}
            size={50}
          />
          <h3 className="mt-2 capitalize">{service}</h3>
          <p className={isActive ? 'text-green-500' : 'text-orange-500'}>
            {isActive ? 'Running' : 'Stopped'}
          </p>
        </div>
      ))}
    </div>
  );
};
```

### Settings Toggle
```typescript
const SettingsToggle = ({ label, isOn, onToggle, color = 'blue' }) => (
  <div className="flex items-center justify-between p-4 border rounded-lg">
    <div>
      <h4 className="font-medium">{label}</h4>
      <p className="text-sm text-gray-600">
        {isOn ? 'Enabled' : 'Disabled'}
      </p>
    </div>
    <PowerButton 
      isOn={isOn}
      onClick={onToggle}
      color={color}
      size={36}
    />
  </div>
);
```

### Gaming Control
```typescript
const GameControl = () => {
  const [gameState, setGameState] = useState({
    power: false,
    turbo: false,
    shield: false
  });

  return (
    <div className="gaming-panel">
      <div className="main-power">
        <PowerButton 
          isOn={gameState.power}
          onClick={() => setGameState(prev => ({ ...prev, power: !prev.power }))}
          color="cyan"
          size={100}
        />
        <p>POWER</p>
      </div>
      
      <div className="secondary-controls">
        <PowerButton 
          isOn={gameState.turbo}
          onClick={() => setGameState(prev => ({ ...prev, turbo: !prev.turbo }))}
          color="orange"
          size={50}
        />
        <PowerButton 
          isOn={gameState.shield}
          onClick={() => setGameState(prev => ({ ...prev, shield: !prev.shield }))}
          color="purple"
          size={50}
        />
      </div>
    </div>
  );
};
```

## Related Files
- **Parent components:** Settings panels, dashboards, control interfaces
- **Child components:** None (leaf component)
- **Shared utilities:** Framer Motion, Tailwind CSS

## Notes
- Uses Framer Motion for smooth animations
- Realistic power button appearance
- Customizable size and color
- Multi-layer visual effects
- Optimized for dark interfaces
- Accessible with proper button semantics
- Performance optimized with CSS animations
- Consistent with overall design system

---
*Auto-generated documentation - verify accuracy before use*
