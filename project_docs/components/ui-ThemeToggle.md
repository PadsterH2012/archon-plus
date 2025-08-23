# ThemeToggle Component

**File Path:** `archon-ui-main/src/components/ui/ThemeToggle.tsx`
**Last Updated:** 2025-08-22

## Purpose
A theme toggle button component for switching between light and dark modes. Features accent color theming, glassmorphism design, and smooth icon transitions with proper accessibility support.

## Props/Parameters

### ThemeToggleProps Interface
```typescript
interface ThemeToggleProps {
  accentColor?: 'purple' | 'green' | 'pink' | 'blue';
}
```

### Props Details
- **accentColor** ('purple' | 'green' | 'pink' | 'blue', default: 'blue'): Color theme for borders and text

## Dependencies

### Imports
```typescript
import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
```

### Exports
```typescript
export const ThemeToggle: React.FC<ThemeToggleProps>
```

## Key Functions/Methods

### Theme Toggle Logic
```typescript
const { theme, setTheme } = useTheme();

const toggleTheme = () => {
  setTheme(theme === 'dark' ? 'light' : 'dark');
};
```

### Accent Color Configuration
```typescript
const accentColorMap = {
  purple: {
    border: 'border-purple-300 dark:border-purple-500/30',
    hover: 'hover:border-purple-400 dark:hover:border-purple-500/60',
    text: 'text-purple-600 dark:text-purple-500',
    bg: 'from-purple-100/80 to-purple-50/60 dark:from-white/10 dark:to-black/30'
  },
  green: {
    border: 'border-emerald-300 dark:border-emerald-500/30',
    hover: 'hover:border-emerald-400 dark:hover:border-emerald-500/60',
    text: 'text-emerald-600 dark:text-emerald-500',
    bg: 'from-emerald-100/80 to-emerald-50/60 dark:from-white/10 dark:to-black/30'
  },
  pink: {
    border: 'border-pink-300 dark:border-pink-500/30',
    hover: 'hover:border-pink-400 dark:hover:border-pink-500/60',
    text: 'text-pink-600 dark:text-pink-500',
    bg: 'from-pink-100/80 to-pink-50/60 dark:from-white/10 dark:to-black/30'
  },
  blue: {
    border: 'border-blue-300 dark:border-blue-500/30',
    hover: 'hover:border-blue-400 dark:hover:border-blue-500/60',
    text: 'text-blue-600 dark:text-blue-500',
    bg: 'from-blue-100/80 to-blue-50/60 dark:from-white/10 dark:to-black/30'
  }
};
```

## Usage Example
```typescript
import { ThemeToggle } from '@/components/ui/ThemeToggle';

// Basic theme toggle
<ThemeToggle />

// Theme toggle with accent color
<ThemeToggle accentColor="purple" />

// In header/navigation
<header className="flex items-center justify-between p-4">
  <h1>My App</h1>
  <div className="flex items-center space-x-4">
    <nav>...</nav>
    <ThemeToggle accentColor="blue" />
  </div>
</header>

// In settings panel
<div className="settings-section">
  <div className="flex items-center justify-between">
    <div>
      <h3 className="font-medium">Theme</h3>
      <p className="text-sm text-gray-600">Switch between light and dark mode</p>
    </div>
    <ThemeToggle accentColor="green" />
  </div>
</div>

// In sidebar
<aside className="sidebar">
  <nav>...</nav>
  <div className="mt-auto p-4">
    <ThemeToggle accentColor="pink" />
  </div>
</aside>

// Floating theme toggle
<div className="fixed bottom-4 right-4 z-50">
  <ThemeToggle accentColor="purple" />
</div>

// With tooltip (using external tooltip library)
<Tooltip content="Toggle theme">
  <ThemeToggle accentColor="blue" />
</Tooltip>

// In mobile menu
<div className="mobile-menu">
  <nav>...</nav>
  <div className="border-t pt-4">
    <div className="flex items-center justify-between">
      <span>Dark mode</span>
      <ThemeToggle accentColor="blue" />
    </div>
  </div>
</div>
```

## State Management
- Uses ThemeContext for global theme state
- No internal state management
- Theme persistence handled by context

## Side Effects
- Theme changes affect entire application
- Icon transitions based on current theme
- Smooth color transitions on theme switch

## Visual Features

### Icon System
- **Light Mode**: Shows Moon icon (switch to dark)
- **Dark Mode**: Shows Sun icon (switch to light)
- **Icon Size**: 20px (w-5 h-5)
- **Smooth Transitions**: Icons change instantly with theme

### Glassmorphism Design
- **Backdrop Blur**: `backdrop-blur-md` for depth effect
- **Gradient Background**: Adaptive gradients for light/dark modes
- **Border Styling**: Accent-colored borders with hover effects
- **Shadow Effects**: Subtle shadows for depth

### Hover Effects
- **Border Enhancement**: Brighter border colors on hover
- **Smooth Transitions**: 300ms transition duration
- **Color Coordination**: Hover effects match accent color

## Theme Support

### Light Mode
- Light gradient backgrounds
- Colored borders and text
- Subtle shadows

### Dark Mode
- Dark gradient backgrounds
- Reduced opacity borders
- Enhanced shadows for depth

### Accent Color Variants
- **Purple**: Purple-themed borders and text
- **Green**: Emerald-themed styling
- **Pink**: Pink-themed styling  
- **Blue**: Blue-themed styling (default)

## Accessibility Features
- **ARIA Label**: Descriptive label indicating current action
- **Button Semantics**: Proper button element
- **Keyboard Support**: Standard button keyboard behavior
- **Focus Indicators**: Visible focus states
- **Screen Reader Support**: Clear action description

### ARIA Implementation
```typescript
aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
```

## Integration with ThemeContext

### Context Usage
```typescript
const { theme, setTheme } = useTheme();
```

### Theme Context Requirements
The component expects a ThemeContext that provides:
- `theme`: Current theme ('light' | 'dark')
- `setTheme`: Function to update theme

### Example ThemeContext Setup
```typescript
// ThemeContext.tsx
const ThemeContext = createContext({
  theme: 'light' as 'light' | 'dark',
  setTheme: (theme: 'light' | 'dark') => {}
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  useEffect(() => {
    // Apply theme to document
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

## Common Integration Patterns

### Header Integration
```typescript
const Header = () => (
  <header className="flex items-center justify-between p-4 border-b">
    <Logo />
    <nav className="flex items-center space-x-4">
      <NavLinks />
      <ThemeToggle accentColor="blue" />
    </nav>
  </header>
);
```

### Settings Panel Integration
```typescript
const AppearanceSettings = () => (
  <div className="space-y-4">
    <h2 className="text-lg font-semibold">Appearance</h2>
    
    <div className="flex items-center justify-between p-4 border rounded-lg">
      <div>
        <h3 className="font-medium">Theme</h3>
        <p className="text-sm text-gray-600">Choose your preferred theme</p>
      </div>
      <ThemeToggle accentColor="purple" />
    </div>
  </div>
);
```

### Mobile Menu Integration
```typescript
const MobileMenu = ({ isOpen }) => (
  <div className={`mobile-menu ${isOpen ? 'open' : 'closed'}`}>
    <nav>...</nav>
    
    <div className="border-t pt-4 mt-4">
      <div className="flex items-center justify-between">
        <span className="font-medium">Dark Mode</span>
        <ThemeToggle accentColor="green" />
      </div>
    </div>
  </div>
);
```

## Related Files
- **Parent components:** Headers, sidebars, settings panels, mobile menus
- **Child components:** Sun and Moon icons from lucide-react
- **Shared utilities:** ThemeContext, Tailwind CSS classes

## Notes
- Requires ThemeContext to be set up in app root
- Icons automatically reflect current theme state
- Consistent with overall design system
- Optimized for both light and dark themes
- Keyboard accessible with proper ARIA support
- Smooth transitions enhance user experience
- Flexible accent color system
- Compact design suitable for various layouts

---
*Auto-generated documentation - verify accuracy before use*
