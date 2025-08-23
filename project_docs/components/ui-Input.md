# Input Component

**File Path:** `archon-ui-main/src/components/ui/Input.tsx`
**Last Updated:** 2025-08-22

## Purpose
A styled input field component with accent color theming, icon support, and label functionality. Provides consistent form input styling with focus effects and glassmorphism design.

## Props/Parameters

### InputProps Interface
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  accentColor?: 'purple' | 'green' | 'pink' | 'blue';
  icon?: React.ReactNode;
  label?: string;
}
```

### Props Details
- **accentColor** ('purple' | 'green' | 'pink' | 'blue', default: 'purple'): Focus color theme
- **icon** (React.ReactNode, optional): Icon to display before input text
- **label** (string, optional): Label text displayed above input
- **...props**: All standard HTML input attributes (type, placeholder, value, onChange, etc.)

## Dependencies

### Imports
```typescript
import React from 'react';
```

### Exports
```typescript
export const Input: React.FC<InputProps>
```

## Key Functions/Methods

### Accent Color Mapping
```typescript
const accentColorMap = {
  purple: 'focus-within:border-purple-500 focus-within:shadow-[0_0_15px_rgba(168,85,247,0.5)]',
  green: 'focus-within:border-emerald-500 focus-within:shadow-[0_0_15px_rgba(16,185,129,0.5)]',
  pink: 'focus-within:border-pink-500 focus-within:shadow-[0_0_15px_rgba(236,72,153,0.5)]',
  blue: 'focus-within:border-blue-500 focus-within:shadow-[0_0_15px_rgba(59,130,246,0.5)]'
};
```

## Usage Example
```typescript
import { Input } from '@/components/ui/Input';
import { Search, User, Mail, Lock } from 'lucide-react';

// Basic input
<Input 
  type="text"
  placeholder="Enter your name"
  value={name}
  onChange={(e) => setName(e.target.value)}
/>

// Input with label
<Input 
  label="Email Address"
  type="email"
  placeholder="you@example.com"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  accentColor="blue"
/>

// Input with icon
<Input 
  icon={<Search size={16} />}
  placeholder="Search..."
  value={searchTerm}
  onChange={(e) => setSearchTerm(e.target.value)}
  accentColor="purple"
/>

// Password input with icon and label
<Input 
  label="Password"
  type="password"
  icon={<Lock size={16} />}
  placeholder="Enter password"
  value={password}
  onChange={(e) => setPassword(e.target.value)}
  accentColor="green"
/>

// User input with custom styling
<Input 
  label="Username"
  icon={<User size={16} />}
  placeholder="Choose username"
  value={username}
  onChange={(e) => setUsername(e.target.value)}
  accentColor="pink"
  className="font-mono"
/>

// Email input with validation
<Input 
  label="Contact Email"
  type="email"
  icon={<Mail size={16} />}
  placeholder="contact@company.com"
  value={contactEmail}
  onChange={(e) => setContactEmail(e.target.value)}
  accentColor="blue"
  required
/>
```

## State Management
No internal state management - controlled through props

## Side Effects
- Focus glow effects with accent color theming
- Smooth transitions on focus/blur
- Icon color changes based on focus state

## Visual Features

### Container Styling
- **Backdrop Blur**: `backdrop-blur-md` for glassmorphism effect
- **Gradient Background**: Light/dark mode adaptive gradients
- **Border**: Subtle borders with focus enhancement
- **Padding**: Consistent `px-3 py-2` spacing
- **Border Radius**: `rounded-md` corners

### Focus Effects
- **Border Color**: Changes to accent color on focus
- **Glow Effect**: Colored shadow glow matching accent color
- **Smooth Transitions**: `transition-all duration-200`

### Icon Integration
- **Positioning**: Left-aligned with proper spacing
- **Color**: Muted gray with focus state changes
- **Size**: Flexible icon sizing (typically 16px)

### Label Styling
- **Typography**: Small, medium weight text
- **Color**: Adaptive for light/dark modes
- **Spacing**: Proper margin below label

## Theme Support

### Light Mode
- White/light backgrounds with transparency
- Gray borders and text
- Bright accent colors on focus

### Dark Mode
- Dark backgrounds with white transparency
- Zinc borders and text colors
- Enhanced glow effects

## Accessibility Features
- Proper label association
- Focus indicators
- Keyboard navigation support
- Screen reader compatible
- ARIA attributes inherited from HTML input

## Form Integration
```typescript
// With React Hook Form
import { useForm } from 'react-hook-form';

const { register, handleSubmit } = useForm();

<Input 
  label="Full Name"
  {...register('fullName', { required: true })}
  placeholder="Enter your full name"
  accentColor="purple"
/>

// With controlled state
const [formData, setFormData] = useState({
  email: '',
  password: ''
});

<Input 
  label="Email"
  type="email"
  value={formData.email}
  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
  accentColor="blue"
/>
```

## Related Files
- **Parent components:** Forms, modals, settings pages
- **Child components:** Icon components (lucide-react)
- **Shared utilities:** Tailwind CSS classes, color system

## Notes
- Uses focus-within for container-level focus effects
- Supports all standard HTML input types
- Icon and input are properly aligned
- Transparent background works with any parent background
- Consistent with overall design system
- Optimized for both light and dark themes
- Smooth transitions enhance user experience
- Flexible accent color system

---
*Auto-generated documentation - verify accuracy before use*
