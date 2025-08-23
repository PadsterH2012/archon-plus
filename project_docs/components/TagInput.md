# TagInput

**File Path:** `archon-ui-main/src/components/ui/TagInput.tsx`
**Last Updated:** 2025-01-22

## Purpose
Enhanced tag input component with autocomplete suggestions, keyboard navigation, and visual tag management for knowledge base items.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tags | string[] | yes | - | Current array of tags |
| onTagsChange | (tags: string[]) => void | yes | - | Callback when tags array changes |
| availableTags | string[] | no | [] | Array of existing tags for autocomplete |
| placeholder | string | no | "Add tags..." | Input placeholder text |
| accentColor | 'blue' \| 'purple' \| 'pink' \| 'green' \| 'orange' \| 'red' | no | "purple" | Color scheme for tags and suggestions |
| disabled | boolean | no | false | Whether input is disabled |
| className | string | no | "" | Additional CSS classes |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect, useRef } from 'react';
import { X, Plus } from 'lucide-react';
import { Badge } from './Badge';
import { Input } from './Input';
```

### Exports
```javascript
export const TagInput: React.FC<TagInputProps>;
```

## Key Functions/Methods
- **handleInputChange**: Updates input value and triggers suggestion filtering
- **addTag**: Adds new tag to the array if not already present
- **removeTag**: Removes tag from the array
- **handleKeyDown**: Handles keyboard navigation (Enter, ArrowUp, ArrowDown, Escape)
- **handleSuggestionClick**: Adds tag when suggestion is clicked
- **handleInputFocus**: Shows suggestions when input gains focus
- **handleInputBlur**: Hides suggestions when input loses focus (with delay)

## Usage Example
```javascript
import { TagInput } from '../components/ui/TagInput';

const [tags, setTags] = useState<string[]>(['documentation', 'api']);
const [availableTags, setAvailableTags] = useState<string[]>(['documentation', 'api', 'tutorial', 'guide']);

<TagInput
  tags={tags}
  onTagsChange={setTags}
  availableTags={availableTags}
  placeholder="Add tags..."
  accentColor="purple"
/>
```

## State Management
- **inputValue**: Current input field value
- **showSuggestions**: Boolean for suggestions dropdown visibility
- **filteredSuggestions**: Array of filtered suggestion tags
- **selectedSuggestionIndex**: Index of currently selected suggestion for keyboard navigation

## Side Effects
- **Suggestion filtering**: Filters available tags based on input value and excludes already selected tags
- **Keyboard navigation**: Supports arrow keys for suggestion selection and Enter to add tags
- **Auto-hide suggestions**: Hides suggestions on blur with delay to allow clicks

## Related Files
- **Parent components:** KnowledgeBasePage (in AddKnowledgeModal)
- **Child components:** Badge, Input (UI components)
- **Shared utilities:** None

## Notes
- Prevents duplicate tags from being added
- Supports keyboard navigation with arrow keys
- Autocomplete suggestions exclude already selected tags
- Visual feedback for selected suggestions
- Responsive design with proper spacing
- Includes debug logging for troubleshooting
- Handles edge cases like empty input and no suggestions
- Delayed blur handling to allow suggestion clicks

---
*Auto-generated documentation - verify accuracy before use*
