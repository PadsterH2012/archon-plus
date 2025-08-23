# KnowledgeItemCard

**File Path:** `archon-ui-main/src/components/knowledge-base/KnowledgeItemCard.tsx`
**Last Updated:** 2025-01-22

## Purpose
Card component for displaying individual knowledge base items with interactive features including code viewing, editing, deletion, and selection capabilities.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| item | KnowledgeItem | yes | - | Knowledge item data to display |
| onDelete | (sourceId: string) => void | yes | - | Callback when delete action is triggered |
| onUpdate | () => void | no | - | Callback when item is updated |
| onRefresh | (sourceId: string) => void | no | - | Callback when refresh action is triggered |
| isSelectionMode | boolean | no | false | Whether card is in selection mode |
| isSelected | boolean | no | false | Whether card is currently selected |
| onToggleSelection | (event: React.MouseEvent) => void | no | - | Callback when selection is toggled |

## Dependencies

### Imports
```javascript
import { useState } from 'react';
import { Link as LinkIcon, Upload, Trash2, RefreshCw, Code, FileText, Brain, BoxIcon, Pencil } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Checkbox } from '../ui/Checkbox';
import { KnowledgeItem, knowledgeBaseService } from '../../services/knowledgeBaseService';
import { useCardTilt } from '../../hooks/useCardTilt';
import { CodeViewerModal, CodeExample } from '../code/CodeViewerModal';
import { EditKnowledgeItemModal } from './EditKnowledgeItemModal';
import '../../styles/card-animations.css';
```

### Exports
```javascript
export const KnowledgeItemCard: React.FC<KnowledgeItemCardProps>;
```

## Key Functions/Methods
- **guessLanguageFromTitle**: Determines programming language from item title for syntax highlighting
- **TagsDisplay**: Internal component for displaying tags with overflow handling
- **DeleteConfirmModal**: Internal component for delete confirmation dialog
- **handleCodeExamplesClick**: Fetches and displays code examples for the item
- **handleEditClick**: Opens edit modal for the item
- **handleDeleteClick**: Shows delete confirmation modal

## Usage Example
```javascript
import { KnowledgeItemCard } from '../components/knowledge-base/KnowledgeItemCard';

<KnowledgeItemCard
  item={knowledgeItem}
  onDelete={handleDelete}
  onUpdate={handleUpdate}
  onRefresh={handleRefresh}
  isSelectionMode={isSelectionMode}
  isSelected={selectedItems.has(item.id)}
  onToggleSelection={(e) => toggleItemSelection(item.id, index, e)}
/>
```

## State Management
- **showDeleteModal**: Boolean for delete confirmation modal visibility
- **showCodeModal**: Boolean for code viewer modal visibility
- **showEditModal**: Boolean for edit modal visibility
- **codeExamples**: Array of CodeExample objects for display
- **loadingCodeExamples**: Boolean for code examples loading state

## Side Effects
- **Code examples fetch**: Loads code examples from API when code button is clicked
- **Card tilt effect**: Uses useCardTilt hook for interactive tilt animation

## Related Files
- **Parent components:** KnowledgeBasePage, KnowledgeTable
- **Child components:** 
  - TagsDisplay (internal)
  - DeleteConfirmModal (internal)
  - CodeViewerModal
  - EditKnowledgeItemModal
  - Card, Badge, Checkbox (UI components)
- **Shared utilities:** 
  - knowledgeBaseService
  - useCardTilt hook

## Notes
- Supports both URL and file-based knowledge items
- Displays up to 4 tags with overflow tooltip for additional tags
- Interactive card tilt effect for enhanced UX
- Code examples viewing with syntax highlighting
- Inline editing capabilities
- Selection mode for bulk operations
- Responsive design with proper spacing and typography

---
*Auto-generated documentation - verify accuracy before use*
