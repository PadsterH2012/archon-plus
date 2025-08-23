# GroupedKnowledgeItemCard

**File Path:** `archon-ui-main/src/components/knowledge-base/GroupedKnowledgeItemCard.tsx`
**Last Updated:** 2025-01-22

## Purpose
Advanced card component for displaying grouped knowledge base items with card shuffling animations, aggregated statistics, and interactive features for managing multiple related items.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| groupedItem | GroupedKnowledgeItem | yes | - | Grouped knowledge item data |
| onDelete | (sourceId: string) => void | yes | - | Callback when delete action is triggered |
| onUpdate | () => void | no | - | Callback when item is updated |
| onRefresh | (sourceId: string) => void | no | - | Callback when refresh action is triggered |

## Dependencies

### Imports
```javascript
import { useState, useMemo } from 'react';
import { Link as LinkIcon, Upload, Trash2, RefreshCw, Code, FileText, Brain, BoxIcon, Globe, ChevronRight, Pencil } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { KnowledgeItem, KnowledgeItemMetadata } from '../../services/knowledgeBaseService';
import { useCardTilt } from '../../hooks/useCardTilt';
import { CodeViewerModal, CodeExample } from '../code/CodeViewerModal';
import { EditKnowledgeItemModal } from './EditKnowledgeItemModal';
```

### Exports
```javascript
export const GroupedKnowledgeItemCard: React.FC<GroupedKnowledgeItemCardProps>;
```

## Key Functions/Methods
- **guessLanguageFromTitle**: Determines programming language from item title for syntax highlighting
- **TagsDisplay**: Internal component for displaying tags with overflow tooltip
- **DeleteConfirmModal**: Internal component for delete confirmation dialog
- **getCardColor**: Returns appropriate color scheme based on source type and knowledge type
- **getSourceIconColor/getTypeIconColor**: Returns icon colors matching card theme
- **shuffleToNextCard**: Animates to next card in grouped items
- **renderCardContent**: Renders card content for active item
- **handleDelete/handleRefresh**: Action handlers for card operations

## Usage Example
```javascript
import { GroupedKnowledgeItemCard } from '../components/knowledge-base/GroupedKnowledgeItemCard';

<GroupedKnowledgeItemCard
  groupedItem={groupedKnowledgeItem}
  onDelete={handleDelete}
  onUpdate={handleUpdate}
  onRefresh={handleRefresh}
/>
```

## State Management
- **showDeleteConfirm**: Boolean for delete confirmation modal
- **showTooltip/showCodeTooltip/showPageTooltip**: Tooltip visibility states
- **isRemoving**: Boolean for removal animation state
- **activeCardIndex**: Index of currently displayed card in group
- **isShuffling**: Boolean for card shuffle animation state
- **showCodeModal/showEditModal**: Modal visibility states

## Side Effects
- **Card tilt effect**: Uses useCardTilt hook for interactive animations (disabled for grouped items)
- **Card shuffling**: Animated transitions between grouped items
- **Aggregated statistics**: Calculates total word count and code examples from all items
- **Code examples aggregation**: Combines code examples from all grouped items

## Related Files
- **Parent components:** KnowledgeBasePage, KnowledgeTable
- **Child components:** 
  - TagsDisplay (internal)
  - DeleteConfirmModal (internal)
  - CodeViewerModal
  - EditKnowledgeItemModal
  - Card, Badge (UI components)
- **Shared utilities:** 
  - useCardTilt hook
  - KnowledgeItem types

## Notes
- Supports both single and grouped knowledge items
- Card shuffling animation for browsing grouped items
- Aggregated statistics (total word count, code examples)
- Color-coded by source type (URL: blue/cyan, File: green/orange)
- Knowledge type indicators (Technical: BoxIcon, Business: Brain)
- Interactive tilt effects disabled for grouped items to prevent conflicts
- Comprehensive tag display with overflow handling
- Code examples aggregation from all grouped items
- Status-based styling with proper visual feedback
- Responsive design with proper spacing and typography

---
*Auto-generated documentation - verify accuracy before use*
