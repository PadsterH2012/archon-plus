# Checkbox Component

**File Path:** `archon-ui-main/src/components/ui/Checkbox.tsx`
**Last Updated:** 2025-08-22

## Purpose
An animated checkbox component with support for checked, unchecked, and indeterminate states. Features smooth animations, glow effects, and accessibility support for form interactions.

## Props/Parameters

### CheckboxProps Interface
```typescript
interface CheckboxProps {
  checked: boolean;
  onChange?: (checked: boolean) => void;
  indeterminate?: boolean;
  disabled?: boolean;
  className?: string;
}
```

### Props Details
- **checked** (boolean, required): Current checked state
- **onChange** ((checked: boolean) => void, optional): Callback when state changes
- **indeterminate** (boolean, default: false): Show indeterminate state (partial selection)
- **disabled** (boolean, default: false): Disable interaction
- **className** (string, default: ''): Additional CSS classes

## Dependencies

### Imports
```typescript
import { useState, useEffect } from 'react';
import { Check, Minus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
```

### Exports
```typescript
export const Checkbox
```

## Key Functions/Methods

### State Management
```typescript
const [isChecked, setIsChecked] = useState(checked);

useEffect(() => {
  setIsChecked(checked);
}, [checked]);
```

### Click Handler
```typescript
const handleClick = () => {
  if (!disabled && onChange) {
    const newChecked = !isChecked;
    setIsChecked(newChecked);
    onChange(newChecked);
  }
};
```

## Usage Example
```typescript
import { Checkbox } from '@/components/ui/Checkbox';
import { useState } from 'react';

// Basic checkbox
const [isChecked, setIsChecked] = useState(false);

<Checkbox 
  checked={isChecked}
  onChange={setIsChecked}
/>

// Checkbox with label
<div className="flex items-center space-x-2">
  <Checkbox 
    checked={acceptTerms}
    onChange={setAcceptTerms}
  />
  <label className="text-sm">I accept the terms and conditions</label>
</div>

// Indeterminate checkbox (for "select all" scenarios)
const [selectedItems, setSelectedItems] = useState<string[]>([]);
const allItems = ['item1', 'item2', 'item3'];
const isIndeterminate = selectedItems.length > 0 && selectedItems.length < allItems.length;
const isAllSelected = selectedItems.length === allItems.length;

<Checkbox 
  checked={isAllSelected}
  indeterminate={isIndeterminate}
  onChange={(checked) => {
    if (checked) {
      setSelectedItems(allItems);
    } else {
      setSelectedItems([]);
    }
  }}
/>

// Disabled checkbox
<Checkbox 
  checked={true}
  disabled={true}
  onChange={() => {}}
/>

// Custom styled checkbox
<Checkbox 
  checked={isEnabled}
  onChange={setIsEnabled}
  className="border-2 border-purple-500"
/>

// Form integration
<form className="space-y-4">
  <div className="flex items-center space-x-2">
    <Checkbox 
      checked={formData.newsletter}
      onChange={(checked) => setFormData(prev => ({ ...prev, newsletter: checked }))}
    />
    <label>Subscribe to newsletter</label>
  </div>
  
  <div className="flex items-center space-x-2">
    <Checkbox 
      checked={formData.notifications}
      onChange={(checked) => setFormData(prev => ({ ...prev, notifications: checked }))}
    />
    <label>Enable notifications</label>
  </div>
</form>
```

## State Management
- Internal state synchronized with props
- Controlled component pattern
- State updates trigger onChange callback

## Side Effects
- Smooth scale and opacity animations
- Glow effect when checked/indeterminate
- Focus ring for accessibility

## Visual Features

### Base Styling
- **Size**: 20px × 20px (`w-5 h-5`)
- **Shape**: Rounded corners (`rounded-md`)
- **Background**: Glassmorphism with backdrop blur
- **Border**: Adaptive border colors

### Animation System
```typescript
// Framer Motion animations
<motion.div
  initial={{ scale: 0, opacity: 0 }}
  animate={{ scale: 1, opacity: 1 }}
  exit={{ scale: 0, opacity: 0 }}
  transition={{ duration: 0.15 }}
>
```

### State Indicators
- **Unchecked**: Empty with border
- **Checked**: Blue checkmark icon
- **Indeterminate**: Blue minus icon
- **Disabled**: 50% opacity

### Visual Effects
- **Glow Effect**: Blue glow when checked/indeterminate
- **Hover State**: Border color change on hover
- **Focus State**: Focus ring for keyboard navigation
- **Smooth Transitions**: 200ms transitions

## Theme Support

### Light Mode
- White/transparent background
- Gray borders
- Blue accent for checked state

### Dark Mode
- Dark/transparent background
- Zinc borders
- Blue accent for checked state

## Accessibility Features
- **Button Role**: Proper semantic button element
- **Focus Management**: Keyboard navigation support
- **Focus Ring**: Visible focus indicator
- **Disabled State**: Proper disabled attribute
- **ARIA Support**: Screen reader compatible

## Animation Details

### Check/Uncheck Animation
- Scale from 0 to 1 on check
- Opacity fade in/out
- 150ms duration with smooth easing

### Icon Switching
- AnimatePresence for smooth transitions
- Different keys for checked/indeterminate states
- Prevents layout shift during transitions

## Common Use Cases

### Form Validation
```typescript
const [errors, setErrors] = useState<string[]>([]);

<div className="space-y-2">
  <div className="flex items-center space-x-2">
    <Checkbox 
      checked={acceptTerms}
      onChange={setAcceptTerms}
    />
    <label>I accept the terms and conditions *</label>
  </div>
  {!acceptTerms && errors.includes('terms') && (
    <p className="text-red-500 text-sm">You must accept the terms</p>
  )}
</div>
```

### Select All Pattern
```typescript
const SelectAllExample = () => {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const allItems = ['Option 1', 'Option 2', 'Option 3'];
  
  const isIndeterminate = selectedItems.length > 0 && selectedItems.length < allItems.length;
  const isAllSelected = selectedItems.length === allItems.length;
  
  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-2 border-b pb-2">
        <Checkbox 
          checked={isAllSelected}
          indeterminate={isIndeterminate}
          onChange={(checked) => {
            setSelectedItems(checked ? allItems : []);
          }}
        />
        <label className="font-medium">Select All</label>
      </div>
      
      {allItems.map(item => (
        <div key={item} className="flex items-center space-x-2 ml-4">
          <Checkbox 
            checked={selectedItems.includes(item)}
            onChange={(checked) => {
              if (checked) {
                setSelectedItems(prev => [...prev, item]);
              } else {
                setSelectedItems(prev => prev.filter(i => i !== item));
              }
            }}
          />
          <label>{item}</label>
        </div>
      ))}
    </div>
  );
};
```

## Related Files
- **Parent components:** Forms, settings, task lists, modals
- **Child components:** Check and Minus icons from lucide-react
- **Shared utilities:** Framer Motion, Tailwind CSS

## Notes
- Uses Framer Motion for smooth animations
- Supports both controlled and uncontrolled patterns
- Indeterminate state useful for hierarchical selections
- Glassmorphism design consistent with other components
- Optimized for both light and dark themes
- Keyboard accessible with proper focus management
- Performance optimized with minimal re-renders

---
*Auto-generated documentation - verify accuracy before use*
