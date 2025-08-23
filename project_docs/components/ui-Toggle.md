# Toggle Component

**File Path:** `archon-ui-main/src/components/ui/Toggle.tsx`
**Last Updated:** 2025-08-22

## Purpose
A switch/toggle component for binary state control with accent color theming, icon support, and smooth animations. Uses external CSS for advanced styling and animations.

## Props/Parameters

### ToggleProps Interface
```typescript
interface ToggleProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  accentColor?: 'purple' | 'green' | 'pink' | 'blue' | 'orange';
  icon?: React.ReactNode;
  disabled?: boolean;
}
```

### Props Details
- **checked** (boolean, required): Current toggle state
- **onCheckedChange** ((checked: boolean) => void, required): Callback when state changes
- **accentColor** ('purple' | 'green' | 'pink' | 'blue' | 'orange', default: 'blue'): Color theme
- **icon** (React.ReactNode, optional): Icon to display in toggle thumb
- **disabled** (boolean, default: false): Disable interaction

## Dependencies

### Imports
```typescript
import React from 'react';
import '../../styles/toggle.css';
```

### Exports
```typescript
export const Toggle: React.FC<ToggleProps>
```

## Key Functions/Methods

### Click Handler
```typescript
const handleClick = () => {
  if (!disabled) {
    onCheckedChange(!checked);
  }
};
```

### CSS Classes
```typescript
className={`
  toggle-switch
  ${checked ? 'toggle-checked' : ''}
  ${disabled ? 'toggle-disabled' : ''}
  toggle-${accentColor}
`}
```

## Usage Example
```typescript
import { Toggle } from '@/components/ui/Toggle';
import { useState } from 'react';
import { Moon, Sun, Bell, Wifi } from 'lucide-react';

// Basic toggle
const [isEnabled, setIsEnabled] = useState(false);

<Toggle 
  checked={isEnabled}
  onCheckedChange={setIsEnabled}
/>

// Toggle with icon
<Toggle 
  checked={darkMode}
  onCheckedChange={setDarkMode}
  icon={darkMode ? <Moon size={12} /> : <Sun size={12} />}
  accentColor="purple"
/>

// Settings toggles
<div className="space-y-4">
  <div className="flex items-center justify-between">
    <div>
      <h4 className="font-medium">Notifications</h4>
      <p className="text-sm text-gray-600">Receive push notifications</p>
    </div>
    <Toggle 
      checked={notifications}
      onCheckedChange={setNotifications}
      icon={<Bell size={12} />}
      accentColor="green"
    />
  </div>
  
  <div className="flex items-center justify-between">
    <div>
      <h4 className="font-medium">Auto-sync</h4>
      <p className="text-sm text-gray-600">Automatically sync data</p>
    </div>
    <Toggle 
      checked={autoSync}
      onCheckedChange={setAutoSync}
      icon={<Wifi size={12} />}
      accentColor="blue"
    />
  </div>
</div>

// Disabled toggle
<Toggle 
  checked={true}
  onCheckedChange={() => {}}
  disabled={true}
  accentColor="gray"
/>

// Color variants
<div className="flex space-x-4">
  <Toggle checked={true} onCheckedChange={() => {}} accentColor="purple" />
  <Toggle checked={true} onCheckedChange={() => {}} accentColor="green" />
  <Toggle checked={true} onCheckedChange={() => {}} accentColor="pink" />
  <Toggle checked={true} onCheckedChange={() => {}} accentColor="blue" />
  <Toggle checked={true} onCheckedChange={() => {}} accentColor="orange" />
</div>

// Form integration
<form className="space-y-4">
  <div className="flex items-center justify-between">
    <label htmlFor="email-notifications">Email Notifications</label>
    <Toggle 
      checked={formData.emailNotifications}
      onCheckedChange={(checked) => 
        setFormData(prev => ({ ...prev, emailNotifications: checked }))
      }
      accentColor="blue"
    />
  </div>
  
  <div className="flex items-center justify-between">
    <label htmlFor="public-profile">Public Profile</label>
    <Toggle 
      checked={formData.publicProfile}
      onCheckedChange={(checked) => 
        setFormData(prev => ({ ...prev, publicProfile: checked }))
      }
      accentColor="green"
    />
  </div>
</form>
```

## State Management
No internal state management - controlled through props

## Side Effects
- Smooth sliding animations via CSS
- Color transitions based on accent color
- Icon animations when provided

## Visual Features

### CSS Classes Structure
- **toggle-switch**: Base toggle styling
- **toggle-checked**: Applied when checked=true
- **toggle-disabled**: Applied when disabled=true
- **toggle-{color}**: Color-specific styling

### Animation System
- Smooth thumb sliding animation
- Background color transitions
- Icon fade/scale animations
- Disabled state opacity changes

### Thumb Design
- Circular thumb that slides left/right
- Icon container within thumb
- Smooth transitions between states

## Theme Support
- Color-specific CSS classes for each accent color
- Light/dark mode compatibility through CSS variables
- Consistent with overall design system

## Accessibility Features
- **Switch Role**: Proper ARIA switch role
- **Checked State**: `aria-checked` attribute
- **Keyboard Support**: Standard button keyboard behavior
- **Disabled State**: Proper disabled attribute
- **Focus Management**: Keyboard navigation support

## CSS Styling (External)
The component relies on external CSS file `toggle.css` for styling:

```css
/* Example CSS structure (not the actual file) */
.toggle-switch {
  /* Base toggle styling */
}

.toggle-switch.toggle-checked {
  /* Checked state styling */
}

.toggle-switch.toggle-disabled {
  /* Disabled state styling */
}

.toggle-purple {
  /* Purple accent color */
}

.toggle-thumb {
  /* Thumb styling and animations */
}

.toggle-icon {
  /* Icon container styling */
}
```

## Common Use Cases

### Settings Panel
```typescript
const SettingsPanel = () => {
  const [settings, setSettings] = useState({
    darkMode: false,
    notifications: true,
    autoSave: true,
    publicProfile: false
  });

  const updateSetting = (key: string, value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium">Dark Mode</h3>
          <p className="text-sm text-gray-600">Switch to dark theme</p>
        </div>
        <Toggle 
          checked={settings.darkMode}
          onCheckedChange={(checked) => updateSetting('darkMode', checked)}
          icon={settings.darkMode ? <Moon size={12} /> : <Sun size={12} />}
          accentColor="purple"
        />
      </div>
      
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-medium">Notifications</h3>
          <p className="text-sm text-gray-600">Receive app notifications</p>
        </div>
        <Toggle 
          checked={settings.notifications}
          onCheckedChange={(checked) => updateSetting('notifications', checked)}
          accentColor="green"
        />
      </div>
    </div>
  );
};
```

### Feature Flags
```typescript
const FeatureToggle = ({ feature, enabled, onToggle, disabled = false }) => (
  <div className="flex items-center justify-between p-4 border rounded-lg">
    <div>
      <h4 className="font-medium">{feature.name}</h4>
      <p className="text-sm text-gray-600">{feature.description}</p>
    </div>
    <Toggle 
      checked={enabled}
      onCheckedChange={onToggle}
      disabled={disabled}
      accentColor="blue"
    />
  </div>
);
```

### Quick Actions
```typescript
const QuickActions = () => (
  <div className="flex items-center space-x-4">
    <div className="flex items-center space-x-2">
      <span className="text-sm">Auto-save</span>
      <Toggle 
        checked={autoSave}
        onCheckedChange={setAutoSave}
        accentColor="green"
      />
    </div>
    
    <div className="flex items-center space-x-2">
      <span className="text-sm">Live preview</span>
      <Toggle 
        checked={livePreview}
        onCheckedChange={setLivePreview}
        accentColor="blue"
      />
    </div>
  </div>
);
```

## Related Files
- **Parent components:** Settings pages, forms, toolbars, feature panels
- **Child components:** Icon components (lucide-react)
- **Shared utilities:** External CSS file, Tailwind CSS

## Notes
- Relies on external CSS file for advanced styling
- Supports icon integration within toggle thumb
- Consistent with overall design system
- Optimized for both light and dark themes
- Keyboard accessible with proper ARIA attributes
- Smooth animations enhance user experience
- Color system matches other components
- Performance optimized with CSS animations

---
*Auto-generated documentation - verify accuracy before use*
