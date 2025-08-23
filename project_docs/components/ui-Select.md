# Select Component

**File Path:** `archon-ui-main/src/components/ui/Select.tsx`
**Last Updated:** 2025-08-22

## Purpose
A styled dropdown select component with accent color theming, label support, and glassmorphism design. Provides consistent form select styling with focus effects and custom dropdown arrow.

## Props/Parameters

### SelectProps Interface
```typescript
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  accentColor?: 'purple' | 'green' | 'pink' | 'blue';
  label?: string;
  options: {
    value: string;
    label: string;
  }[];
}
```

### Props Details
- **accentColor** ('purple' | 'green' | 'pink' | 'blue', default: 'purple'): Focus color theme
- **label** (string, optional): Label text displayed above select
- **options** (Array<{value: string, label: string}>, required): Select options
- **...props**: All standard HTML select attributes (value, onChange, disabled, etc.)

## Dependencies

### Imports
```typescript
import React from 'react';
```

### Exports
```typescript
export const Select: React.FC<SelectProps>
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

### Custom Dropdown Arrow
```typescript
<svg width="12" height="12" viewBox="0 0 12 12" fill="none">
  <path d="M2.5 4.5L6 8L9.5 4.5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
</svg>
```

## Usage Example
```typescript
import { Select } from '@/components/ui/Select';
import { useState } from 'react';

// Basic select
const [selectedValue, setSelectedValue] = useState('');

<Select 
  options={[
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' }
  ]}
  value={selectedValue}
  onChange={(e) => setSelectedValue(e.target.value)}
/>

// Select with label
<Select 
  label="Choose Category"
  options={[
    { value: 'technical', label: 'Technical' },
    { value: 'business', label: 'Business' },
    { value: 'personal', label: 'Personal' }
  ]}
  value={category}
  onChange={(e) => setCategory(e.target.value)}
  accentColor="blue"
/>

// Status select with colors
<Select 
  label="Task Status"
  options={[
    { value: 'todo', label: 'To Do' },
    { value: 'doing', label: 'In Progress' },
    { value: 'review', label: 'In Review' },
    { value: 'done', label: 'Completed' }
  ]}
  value={status}
  onChange={(e) => setStatus(e.target.value)}
  accentColor="green"
/>

// Priority select
<Select 
  label="Priority Level"
  options={[
    { value: 'low', label: 'Low Priority' },
    { value: 'medium', label: 'Medium Priority' },
    { value: 'high', label: 'High Priority' },
    { value: 'urgent', label: 'Urgent' }
  ]}
  value={priority}
  onChange={(e) => setPriority(e.target.value)}
  accentColor="pink"
/>

// Disabled select
<Select 
  label="Disabled Field"
  options={[
    { value: 'disabled', label: 'Cannot Change' }
  ]}
  value="disabled"
  disabled={true}
  onChange={() => {}}
/>

// Form integration
<form className="space-y-4">
  <Select 
    label="Project Type"
    options={[
      { value: 'web', label: 'Web Application' },
      { value: 'mobile', label: 'Mobile App' },
      { value: 'api', label: 'API Service' },
      { value: 'library', label: 'Library/Package' }
    ]}
    value={formData.projectType}
    onChange={(e) => setFormData(prev => ({ ...prev, projectType: e.target.value }))}
    accentColor="purple"
    required
  />
  
  <Select 
    label="Team Size"
    options={[
      { value: '1', label: 'Solo (1 person)' },
      { value: '2-5', label: 'Small (2-5 people)' },
      { value: '6-15', label: 'Medium (6-15 people)' },
      { value: '16+', label: 'Large (16+ people)' }
    ]}
    value={formData.teamSize}
    onChange={(e) => setFormData(prev => ({ ...prev, teamSize: e.target.value }))}
    accentColor="blue"
  />
</form>
```

## State Management
No internal state management - controlled through props

## Side Effects
- Focus glow effects with accent color theming
- Smooth transitions on focus/blur
- Custom dropdown arrow styling

## Visual Features

### Container Styling
- **Backdrop Blur**: `backdrop-blur-md` for glassmorphism effect
- **Gradient Background**: Light/dark mode adaptive gradients
- **Border**: Subtle borders with focus enhancement
- **Border Radius**: `rounded-md` corners

### Focus Effects
- **Border Color**: Changes to accent color on focus
- **Glow Effect**: Colored shadow glow matching accent color
- **Smooth Transitions**: `transition-all duration-200`

### Custom Arrow
- **Positioning**: Absolute positioned on right side
- **Icon**: Custom SVG chevron down
- **Color**: Muted gray with theme adaptation
- **Pointer Events**: Disabled to allow click-through

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

### Option Styling
- **Light Mode**: White background for options
- **Dark Mode**: Dark zinc background for options
- **Contrast**: Proper text contrast in dropdown

## Accessibility Features
- Proper label association
- Focus indicators
- Keyboard navigation support
- Screen reader compatible
- Standard HTML select behavior

## Form Integration
```typescript
// With React Hook Form
import { useForm } from 'react-hook-form';

const { register, handleSubmit } = useForm();

<Select 
  label="Category"
  options={categoryOptions}
  {...register('category', { required: true })}
  accentColor="purple"
/>

// With controlled state
const [formData, setFormData] = useState({
  category: '',
  priority: 'medium'
});

<Select 
  label="Category"
  options={categoryOptions}
  value={formData.category}
  onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
  accentColor="blue"
/>
```

## Dynamic Options
```typescript
// Options from API
const [categories, setCategories] = useState([]);

useEffect(() => {
  fetchCategories().then(setCategories);
}, []);

<Select 
  label="Category"
  options={categories.map(cat => ({ value: cat.id, label: cat.name }))}
  value={selectedCategory}
  onChange={(e) => setSelectedCategory(e.target.value)}
/>

// Filtered options
const filteredOptions = allOptions.filter(option => 
  option.label.toLowerCase().includes(searchTerm.toLowerCase())
);

<Select 
  label="Filtered Options"
  options={filteredOptions}
  value={selectedValue}
  onChange={(e) => setSelectedValue(e.target.value)}
/>
```

## Related Files
- **Parent components:** Forms, modals, settings pages, filters
- **Child components:** None (uses native select)
- **Shared utilities:** Tailwind CSS classes, color system

## Notes
- Uses native HTML select for accessibility and mobile support
- Custom arrow replaces browser default styling
- Transparent background works with any parent background
- Consistent with overall design system
- Optimized for both light and dark themes
- Smooth transitions enhance user experience
- Flexible accent color system
- Supports all standard HTML select attributes

---
*Auto-generated documentation - verify accuracy before use*
