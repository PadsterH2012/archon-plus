# CollapsibleSettingsCard Component

**File Path:** `archon-ui-main/src/components/ui/CollapsibleSettingsCard.tsx`
**Last Updated:** 2025-08-22

## Purpose
An expandable settings card component with animated collapse/expand functionality, localStorage persistence, and flicker effects. Combines PowerButton for toggle control with smooth content animations.

## Props/Parameters

### CollapsibleSettingsCardProps Interface
```typescript
interface CollapsibleSettingsCardProps {
  title: string;
  icon: LucideIcon;
  accentColor?: 'purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange';
  children: React.ReactNode;
  defaultExpanded?: boolean;
  storageKey?: string;
}
```

### Props Details
- **title** (string, required): Card title displayed in header
- **icon** (LucideIcon, required): Icon component from lucide-react
- **accentColor** ('purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange', default: 'blue'): Color theme
- **children** (React.ReactNode, required): Card content to show/hide
- **defaultExpanded** (boolean, default: true): Initial expanded state
- **storageKey** (string, optional): localStorage key for state persistence

## Dependencies

### Imports
```typescript
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PowerButton } from './PowerButton';
import { LucideIcon } from 'lucide-react';
```

### Exports
```typescript
export const CollapsibleSettingsCard: React.FC<CollapsibleSettingsCardProps>
```

## Key Functions/Methods

### State Management
```typescript
const [isExpanded, setIsExpanded] = useState(defaultExpanded);
const [isFlickering, setIsFlickering] = useState(false);
```

### localStorage Persistence
```typescript
useEffect(() => {
  if (storageKey) {
    const saved = localStorage.getItem(`settings-card-${storageKey}`);
    if (saved !== null) {
      setIsExpanded(saved === 'true');
    }
  }
}, [storageKey]);
```

### Toggle with Flicker Animation
```typescript
const handleToggle = () => {
  if (isExpanded) {
    // Start flicker animation when collapsing
    setIsFlickering(true);
    setTimeout(() => {
      setIsExpanded(false);
      setIsFlickering(false);
      if (storageKey) {
        localStorage.setItem(`settings-card-${storageKey}`, 'false');
      }
    }, 300); // Duration of flicker animation
  } else {
    // No flicker when expanding
    setIsExpanded(true);
    if (storageKey) {
      localStorage.setItem(`settings-card-${storageKey}`, 'true');
    }
  }
};
```

### Icon Color Mapping
```typescript
const iconColorMap = {
  purple: 'text-purple-500 filter drop-shadow-[0_0_8px_rgba(168,85,247,0.8)]',
  green: 'text-green-500 filter drop-shadow-[0_0_8px_rgba(34,197,94,0.8)]',
  pink: 'text-pink-500 filter drop-shadow-[0_0_8px_rgba(236,72,153,0.8)]',
  blue: 'text-blue-500 filter drop-shadow-[0_0_8px_rgba(59,130,246,0.8)]',
  cyan: 'text-cyan-500 filter drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]',
  orange: 'text-orange-500 filter drop-shadow-[0_0_8px_rgba(249,115,22,0.8)]'
};
```

## Usage Example
```typescript
import { CollapsibleSettingsCard } from '@/components/ui/CollapsibleSettingsCard';
import { Settings, Database, Bell, Shield, Wifi, Monitor } from 'lucide-react';

// Basic settings card
<CollapsibleSettingsCard 
  title="General Settings"
  icon={Settings}
  accentColor="blue"
>
  <div className="space-y-4">
    <div>Setting content here...</div>
  </div>
</CollapsibleSettingsCard>

// Database configuration card
<CollapsibleSettingsCard 
  title="Database Configuration"
  icon={Database}
  accentColor="green"
  storageKey="database-config"
  defaultExpanded={false}
>
  <div className="space-y-4">
    <Input label="Host" placeholder="localhost" />
    <Input label="Port" placeholder="5432" />
    <Input label="Database Name" placeholder="myapp" />
    <Button>Test Connection</Button>
  </div>
</CollapsibleSettingsCard>

// Notification settings
<CollapsibleSettingsCard 
  title="Notifications"
  icon={Bell}
  accentColor="orange"
  storageKey="notifications"
>
  <div className="space-y-4">
    <div className="flex items-center justify-between">
      <span>Email notifications</span>
      <Toggle checked={emailNotifs} onCheckedChange={setEmailNotifs} />
    </div>
    <div className="flex items-center justify-between">
      <span>Push notifications</span>
      <Toggle checked={pushNotifs} onCheckedChange={setPushNotifs} />
    </div>
    <div className="flex items-center justify-between">
      <span>SMS notifications</span>
      <Toggle checked={smsNotifs} onCheckedChange={setSmsNotifs} />
    </div>
  </div>
</CollapsibleSettingsCard>

// Security settings
<CollapsibleSettingsCard 
  title="Security & Privacy"
  icon={Shield}
  accentColor="purple"
  storageKey="security"
>
  <div className="space-y-6">
    <div>
      <h4 className="font-medium mb-2">Two-Factor Authentication</h4>
      <Button variant="outline">Enable 2FA</Button>
    </div>
    
    <div>
      <h4 className="font-medium mb-2">API Keys</h4>
      <div className="space-y-2">
        <Input label="OpenAI API Key" type="password" />
        <Input label="Anthropic API Key" type="password" />
      </div>
    </div>
    
    <div>
      <h4 className="font-medium mb-2">Privacy Settings</h4>
      <div className="space-y-2">
        <Checkbox checked={analytics} onChange={setAnalytics}>
          Allow analytics
        </Checkbox>
        <Checkbox checked={crashReports} onChange={setCrashReports}>
          Send crash reports
        </Checkbox>
      </div>
    </div>
  </div>
</CollapsibleSettingsCard>

// Network settings
<CollapsibleSettingsCard 
  title="Network Configuration"
  icon={Wifi}
  accentColor="cyan"
  storageKey="network"
  defaultExpanded={false}
>
  <div className="space-y-4">
    <Select 
      label="Connection Type"
      options={[
        { value: 'auto', label: 'Automatic' },
        { value: 'manual', label: 'Manual' },
        { value: 'proxy', label: 'Proxy' }
      ]}
    />
    <Input label="Proxy URL" placeholder="http://proxy.example.com:8080" />
    <div className="flex space-x-2">
      <Button variant="outline">Test Connection</Button>
      <Button>Save Settings</Button>
    </div>
  </div>
</CollapsibleSettingsCard>

// Monitoring settings
<CollapsibleSettingsCard 
  title="System Monitoring"
  icon={Monitor}
  accentColor="pink"
  storageKey="monitoring"
>
  <div className="space-y-4">
    <div className="grid grid-cols-2 gap-4">
      <div>
        <label className="block text-sm font-medium mb-1">CPU Threshold</label>
        <Input type="number" placeholder="80" />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Memory Threshold</label>
        <Input type="number" placeholder="90" />
      </div>
    </div>
    
    <div>
      <label className="block text-sm font-medium mb-2">Alert Frequency</label>
      <Select 
        options={[
          { value: '1m', label: 'Every minute' },
          { value: '5m', label: 'Every 5 minutes' },
          { value: '15m', label: 'Every 15 minutes' },
          { value: '1h', label: 'Every hour' }
        ]}
      />
    </div>
  </div>
</CollapsibleSettingsCard>
```

## State Management
- Internal state for expanded/collapsed status
- Internal state for flicker animation
- localStorage persistence for user preferences

## Side Effects
- localStorage read/write operations
- Flicker animation timing
- Content height animations

## Visual Features

### Header Design
- **Icon with Glow**: Colored icon with drop shadow effect
- **Title**: Large, semibold text
- **PowerButton**: Toggle control with color coordination

### Flicker Animation
```typescript
animate={isFlickering ? {
  opacity: [1, 0.3, 1, 0.5, 1, 0.2, 1],
} : {}}
transition={{
  duration: 0.3,
  times: [0, 0.1, 0.2, 0.3, 0.6, 0.8, 1],
}}
```

### Content Animation
```typescript
<motion.div
  initial={{ height: 0, opacity: 0 }}
  animate={{ height: 'auto', opacity: 1 }}
  exit={{ height: 0, opacity: 0 }}
  transition={{
    height: { duration: 0.3, ease: 'easeInOut' },
    opacity: { duration: 0.2, ease: 'easeInOut' }
  }}
>
```

### Color Coordination
- Icon color matches accent color
- PowerButton color matches accent color
- Consistent theming throughout

## Accessibility Features
- **Semantic Structure**: Proper heading hierarchy
- **Keyboard Navigation**: PowerButton is keyboard accessible
- **Screen Reader Support**: Clear content structure
- **Focus Management**: Proper focus handling

## localStorage Integration

### Storage Key Format
```typescript
`settings-card-${storageKey}`
```

### Persistence Logic
- Saves expanded state when toggled
- Loads saved state on component mount
- Falls back to defaultExpanded if no saved state

## Animation System

### Expand Animation
- Height: 0 → auto
- Opacity: 0 → 1
- Duration: 300ms

### Collapse Animation
- Flicker effect first (300ms)
- Then height: auto → 0
- Opacity: 1 → 0

### Flicker Effect
- 7-step opacity animation
- Creates power-down effect
- Only on collapse, not expand

## Common Use Cases

### Settings Panel
```typescript
const SettingsPanel = () => (
  <div className="space-y-6">
    <CollapsibleSettingsCard 
      title="Account Settings"
      icon={User}
      accentColor="blue"
      storageKey="account"
    >
      <AccountSettings />
    </CollapsibleSettingsCard>
    
    <CollapsibleSettingsCard 
      title="Appearance"
      icon={Palette}
      accentColor="purple"
      storageKey="appearance"
    >
      <AppearanceSettings />
    </CollapsibleSettingsCard>
    
    <CollapsibleSettingsCard 
      title="Advanced"
      icon={Settings}
      accentColor="orange"
      storageKey="advanced"
      defaultExpanded={false}
    >
      <AdvancedSettings />
    </CollapsibleSettingsCard>
  </div>
);
```

### Configuration Wizard
```typescript
const ConfigWizard = () => (
  <div className="max-w-2xl mx-auto space-y-4">
    <CollapsibleSettingsCard 
      title="Step 1: Basic Setup"
      icon={Play}
      accentColor="green"
      storageKey="step1"
    >
      <BasicSetupForm />
    </CollapsibleSettingsCard>
    
    <CollapsibleSettingsCard 
      title="Step 2: Database Configuration"
      icon={Database}
      accentColor="blue"
      storageKey="step2"
      defaultExpanded={false}
    >
      <DatabaseConfigForm />
    </CollapsibleSettingsCard>
  </div>
);
```

## Related Files
- **Parent components:** Settings pages, configuration panels, dashboards
- **Child components:** PowerButton, form components, icons
- **Shared utilities:** Framer Motion, localStorage, Tailwind CSS

## Notes
- Combines PowerButton for consistent toggle control
- localStorage persistence enhances user experience
- Flicker animation provides visual feedback
- Smooth height animations for content
- Icon glow effects match accent colors
- Optimized for settings and configuration interfaces
- Accessible with proper semantic structure
- Performance optimized with AnimatePresence

---
*Auto-generated documentation - verify accuracy before use*
