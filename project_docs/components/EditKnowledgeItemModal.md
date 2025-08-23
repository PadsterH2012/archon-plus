# EditKnowledgeItemModal

**File Path:** `archon-ui-main/src/components/knowledge-base/EditKnowledgeItemModal.tsx`
**Last Updated:** 2025-01-22

## Purpose
Modal component for editing knowledge base item metadata including title, description, and group management with validation and error handling.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| item | KnowledgeItem | yes | - | Knowledge item to edit |
| onClose | () => void | yes | - | Callback when modal is closed |
| onUpdate | () => void | yes | - | Callback when item is successfully updated |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { X, Save, RefreshCw, Users, UserX } from 'lucide-react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { KnowledgeItem } from '../../services/knowledgeBaseService';
import { knowledgeBaseService } from '../../services/knowledgeBaseService';
import { useToast } from '../../contexts/ToastContext';
```

### Exports
```javascript
export const EditKnowledgeItemModal: React.FC<EditKnowledgeItemModalProps>;
```

## Key Functions/Methods
- **handleSubmit**: Validates and submits form data with optimized updates
- **handleRemoveFromGroup**: Removes item from group and handles group dissolution
- **handleKeyDown**: Handles escape key to close modal
- **Form validation**: Ensures title is required before submission

## Usage Example
```javascript
import { EditKnowledgeItemModal } from '../components/knowledge-base/EditKnowledgeItemModal';

{showEditModal && (
  <EditKnowledgeItemModal
    item={selectedItem}
    onClose={() => setShowEditModal(false)}
    onUpdate={() => {
      loadKnowledgeItems();
      setShowEditModal(false);
    }}
  />
)}
```

## State Management
- **formData**: Form state with title and description
- **isLoading**: Boolean for save operation loading state
- **isRemovingFromGroup**: Boolean for group removal operation
- **isInGroup**: Computed boolean indicating if item belongs to a group

## Side Effects
- **Keyboard handling**: Listens for escape key to close modal
- **Portal rendering**: Renders modal in document body using createPortal
- **Form validation**: Validates required fields before submission
- **Group management**: Handles group dissolution when removing items

## Related Files
- **Parent components:** KnowledgeItemCard
- **Child components:** Input, Button, Card (UI components)
- **Shared utilities:** 
  - knowledgeBaseService
  - useToast context

## Notes
- Renders as portal for proper z-index layering
- Optimized updates - only sends changed fields to API
- Smart group management - dissolves groups with ≤2 items
- Comprehensive error handling with user feedback
- Keyboard accessibility with escape key support
- Animated modal with Framer Motion
- Form validation prevents empty titles
- Loading states for all async operations
- Group removal with automatic cleanup

---
*Auto-generated documentation - verify accuracy before use*
