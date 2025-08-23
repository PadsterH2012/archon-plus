# GroupCreationModal

**File Path:** `archon-ui-main/src/components/knowledge-base/GroupCreationModal.tsx`
**Last Updated:** 2025-01-22

## Purpose
Modal component for creating knowledge base item groups from selected items with validation, preview, and batch update functionality.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| selectedItems | KnowledgeItem[] | yes | - | Array of selected knowledge items to group |
| onClose | () => void | yes | - | Callback when modal is closed |
| onSuccess | () => void | yes | - | Callback when group is successfully created |

## Dependencies

### Imports
```javascript
import { useState } from 'react';
import { X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Badge } from '../ui/Badge';
import { KnowledgeItem, knowledgeBaseService } from '../../services/knowledgeBaseService';
import { useToast } from '../../contexts/ToastContext';
```

### Exports
```javascript
export const GroupCreationModal: React.FC<GroupCreationModalProps>;
```

## Key Functions/Methods
- **handleCreateGroup**: Validates input and creates group by updating all selected items
- **Batch update**: Updates all selected items with the group name in parallel
- **Form validation**: Ensures group name is provided before creation
- **Keyboard handling**: Supports Enter key to submit form

## Usage Example
```javascript
import { GroupCreationModal } from '../components/knowledge-base/GroupCreationModal';

{showGroupModal && (
  <GroupCreationModal
    selectedItems={selectedKnowledgeItems}
    onClose={() => setShowGroupModal(false)}
    onSuccess={() => {
      setShowGroupModal(false);
      refreshKnowledgeItems();
      clearSelection();
    }}
  />
)}
```

## State Management
- **groupName**: String for the group name input
- **isLoading**: Boolean for group creation loading state

## Side Effects
- **Batch API calls**: Updates multiple knowledge items in parallel
- **Portal rendering**: Renders modal in document body using Framer Motion
- **Form submission**: Handles Enter key for quick submission
- **Success feedback**: Shows toast notification on successful creation

## Related Files
- **Parent components:** KnowledgeBasePage
- **Child components:** Card, Button, Input, Badge (UI components)
- **Shared utilities:** 
  - knowledgeBaseService
  - useToast context

## Notes
- Animated modal with Framer Motion spring transitions
- Batch update using Promise.all for performance
- Form validation prevents empty group names
- Selected items preview with badges showing titles
- Keyboard accessibility with Enter key support
- Loading states during group creation
- Comprehensive error handling with user feedback
- Click outside to close functionality
- Responsive design with proper spacing
- Success notification with item count

---
*Auto-generated documentation - verify accuracy before use*
