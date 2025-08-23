# TagInput Component

**File Path:** `archon-ui-main/src/components/ui/TagInput.tsx`
**Last Updated:** 2025-08-22

## Purpose
A tag input component with autocomplete suggestions, keyboard navigation, and tag management. Allows users to add, remove, and manage tags with a smooth user experience and accessibility features.

## Props/Parameters

### TagInputProps Interface
```typescript
interface TagInputProps {
  tags: string[];
  onTagsChange: (tags: string[]) => void;
  availableTags?: string[];
  placeholder?: string;
  accentColor?: 'blue' | 'purple' | 'pink' | 'green' | 'orange' | 'red';
  disabled?: boolean;
  className?: string;
}
```

### Props Details
- **tags** (string[], required): Current array of tags
- **onTagsChange** ((tags: string[]) => void, required): Callback when tags change
- **availableTags** (string[], default: []): Available tags for autocomplete
- **placeholder** (string, default: "Add tags..."): Input placeholder text
- **accentColor** ('blue' | 'purple' | 'pink' | 'green' | 'orange' | 'red', default: 'purple'): Color theme
- **disabled** (boolean, default: false): Disable input interaction
- **className** (string, default: ''): Additional CSS classes

## Dependencies

### Imports
```typescript
import React, { useState, useEffect, useRef } from 'react';
import { X, Plus } from 'lucide-react';
import { Badge } from './Badge';
import { Input } from './Input';
```

### Exports
```typescript
export const TagInput: React.FC<TagInputProps>
```

## Key Functions/Methods

### State Management
```typescript
const [inputValue, setInputValue] = useState('');
const [showSuggestions, setShowSuggestions] = useState(false);
const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
```

### Suggestion Filtering
```typescript
useEffect(() => {
  if (inputValue.trim()) {
    const filtered = availableTags.filter(tag => 
      tag.toLowerCase().includes(inputValue.toLowerCase()) &&
      !tags.includes(tag)
    );
    setFilteredSuggestions(filtered);
    setShowSuggestions(filtered.length > 0);
  } else {
    setFilteredSuggestions([]);
    setShowSuggestions(false);
  }
  setSelectedSuggestionIndex(-1);
}, [inputValue, availableTags, tags]);
```

### Tag Management
```typescript
const addTag = (tag: string) => {
  const trimmedTag = tag.trim();
  if (trimmedTag && !tags.includes(trimmedTag)) {
    onTagsChange([...tags, trimmedTag]);
  }
  setInputValue('');
  setShowSuggestions(false);
  setSelectedSuggestionIndex(-1);
};

const removeTag = (tagToRemove: string) => {
  onTagsChange(tags.filter(tag => tag !== tagToRemove));
};
```

### Keyboard Navigation
```typescript
const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    if (selectedSuggestionIndex >= 0 && filteredSuggestions[selectedSuggestionIndex]) {
      addTag(filteredSuggestions[selectedSuggestionIndex]);
    } else if (inputValue.trim()) {
      addTag(inputValue);
    }
  } else if (e.key === 'ArrowDown') {
    e.preventDefault();
    setSelectedSuggestionIndex(prev => 
      prev < filteredSuggestions.length - 1 ? prev + 1 : prev
    );
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    setSelectedSuggestionIndex(prev => prev > 0 ? prev - 1 : -1);
  } else if (e.key === 'Escape') {
    setShowSuggestions(false);
    setSelectedSuggestionIndex(-1);
  } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
    // Remove last tag if input is empty
    removeTag(tags[tags.length - 1]);
  }
};
```

## Usage Example
```typescript
import { TagInput } from '@/components/ui/TagInput';
import { useState } from 'react';

// Basic tag input
const [tags, setTags] = useState<string[]>([]);

<TagInput 
  tags={tags}
  onTagsChange={setTags}
  placeholder="Add tags..."
/>

// Tag input with autocomplete
const availableTags = ['React', 'TypeScript', 'JavaScript', 'CSS', 'HTML', 'Node.js'];
const [projectTags, setProjectTags] = useState<string[]>(['React']);

<TagInput 
  tags={projectTags}
  onTagsChange={setProjectTags}
  availableTags={availableTags}
  placeholder="Add technology tags..."
  accentColor="blue"
/>

// Category tagging
const categories = ['Frontend', 'Backend', 'Database', 'DevOps', 'Testing', 'Documentation'];
const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

<TagInput 
  tags={selectedCategories}
  onTagsChange={setSelectedCategories}
  availableTags={categories}
  placeholder="Select categories..."
  accentColor="green"
/>

// Skills tagging
const skillOptions = ['JavaScript', 'Python', 'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask'];
const [skills, setSkills] = useState<string[]>([]);

<TagInput 
  tags={skills}
  onTagsChange={setSkills}
  availableTags={skillOptions}
  placeholder="Add your skills..."
  accentColor="purple"
/>

// Project labels
const [labels, setLabels] = useState<string[]>(['bug', 'high-priority']);

<TagInput 
  tags={labels}
  onTagsChange={setLabels}
  availableTags={['bug', 'feature', 'enhancement', 'documentation', 'high-priority', 'low-priority']}
  placeholder="Add labels..."
  accentColor="orange"
/>

// Disabled state
<TagInput 
  tags={['readonly', 'tags']}
  onTagsChange={() => {}}
  disabled={true}
  placeholder="Cannot edit tags"
/>

// Form integration
<form className="space-y-4">
  <div>
    <label className="block text-sm font-medium mb-2">Project Tags</label>
    <TagInput 
      tags={formData.tags}
      onTagsChange={(newTags) => setFormData(prev => ({ ...prev, tags: newTags }))}
      availableTags={predefinedTags}
      placeholder="Add relevant tags..."
      accentColor="blue"
    />
  </div>
</form>
```

## State Management
- Internal state for input value and suggestions
- External state control via tags prop
- Suggestion filtering and selection state

## Side Effects
- Real-time suggestion filtering
- Keyboard navigation state updates
- Tag addition/removal callbacks

## Visual Features

### Tag Display
- Uses Badge component for consistent tag styling
- Remove button (X icon) on each tag
- Color coordination with accent color
- Responsive tag wrapping

### Input Integration
- Uses Input component for consistent styling
- Placeholder text support
- Focus management
- Accent color theming

### Suggestion Dropdown
- Filtered autocomplete suggestions
- Keyboard navigation highlighting
- Click-to-select functionality
- Automatic show/hide based on input

### Keyboard Navigation
- **Enter**: Add current input or selected suggestion
- **Arrow Up/Down**: Navigate suggestions
- **Escape**: Close suggestions
- **Backspace**: Remove last tag when input is empty

## Accessibility Features
- **Keyboard Navigation**: Full keyboard support for all interactions
- **Focus Management**: Proper focus handling between input and suggestions
- **Screen Reader Support**: Accessible tag management
- **ARIA Attributes**: Proper labeling for assistive technology

## Advanced Features

### Duplicate Prevention
```typescript
if (trimmedTag && !tags.includes(trimmedTag)) {
  onTagsChange([...tags, trimmedTag]);
}
```

### Smart Filtering
```typescript
const filtered = availableTags.filter(tag => 
  tag.toLowerCase().includes(inputValue.toLowerCase()) &&
  !tags.includes(tag) // Exclude already selected tags
);
```

### Backspace Tag Removal
```typescript
else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
  removeTag(tags[tags.length - 1]);
}
```

## Common Use Cases

### Project Tagging
```typescript
const ProjectTagging = () => {
  const [project, setProject] = useState({
    name: '',
    tags: []
  });
  
  const techTags = ['React', 'Vue', 'Angular', 'Node.js', 'Python', 'Django'];
  
  return (
    <div className="space-y-4">
      <Input 
        label="Project Name"
        value={project.name}
        onChange={(e) => setProject(prev => ({ ...prev, name: e.target.value }))}
      />
      
      <div>
        <label className="block text-sm font-medium mb-2">Technologies</label>
        <TagInput 
          tags={project.tags}
          onTagsChange={(tags) => setProject(prev => ({ ...prev, tags }))}
          availableTags={techTags}
          placeholder="Add technologies used..."
          accentColor="blue"
        />
      </div>
    </div>
  );
};
```

### Content Categorization
```typescript
const ContentEditor = () => {
  const [content, setContent] = useState({
    title: '',
    body: '',
    categories: [],
    tags: []
  });
  
  return (
    <form className="space-y-6">
      <Input 
        label="Title"
        value={content.title}
        onChange={(e) => setContent(prev => ({ ...prev, title: e.target.value }))}
      />
      
      <TagInput 
        tags={content.categories}
        onTagsChange={(categories) => setContent(prev => ({ ...prev, categories }))}
        availableTags={['Technology', 'Business', 'Design', 'Marketing']}
        placeholder="Select categories..."
        accentColor="green"
      />
      
      <TagInput 
        tags={content.tags}
        onTagsChange={(tags) => setContent(prev => ({ ...prev, tags }))}
        placeholder="Add custom tags..."
        accentColor="purple"
      />
    </form>
  );
};
```

## Related Files
- **Parent components:** Forms, content editors, project management, settings
- **Child components:** Badge, Input, X and Plus icons from lucide-react
- **Shared utilities:** React hooks, Tailwind CSS

## Notes
- Combines Badge and Input components for consistent styling
- Prevents duplicate tag addition
- Supports both predefined and custom tags
- Keyboard navigation enhances accessibility
- Real-time filtering for better UX
- Consistent with overall design system
- Optimized for both light and dark themes
- Performance optimized with proper state management

---
*Auto-generated documentation - verify accuracy before use*
