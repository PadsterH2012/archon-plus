# KnowledgeTable

**File Path:** `archon-ui-main/src/components/knowledge-base/KnowledgeTable.tsx`
**Last Updated:** 2025-01-22

## Purpose
Table component for displaying knowledge base items in a structured format with grouping by domain, status indicators, and action buttons for management operations.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| items | KnowledgeItem[] | yes | - | Array of knowledge items to display |
| onDelete | (sourceId: string) => void | yes | - | Callback function when delete action is triggered |

## Dependencies

### Imports
```javascript
import React, { useState } from 'react';
import { KnowledgeItem, KnowledgeItemMetadata } from '../../services/knowledgeBaseService';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Link as LinkIcon, Upload, Trash2, RefreshCw, X, Globe, BoxIcon, Brain } from 'lucide-react';
import { format } from 'date-fns';
```

### Exports
```javascript
export const KnowledgeTable: React.FC<KnowledgeTableProps>;
```

## Key Functions/Methods
- **extractDomain**: Extracts clean domain name from URL for grouping
- **groupItemsByDomain**: Groups knowledge items by domain, keeping file uploads separate
- **getFrequencyDisplay**: Returns display information for update frequency (icon, text, color)

## Usage Example
```javascript
import { KnowledgeTable } from '../components/knowledge-base/KnowledgeTable';

<KnowledgeTable 
  items={knowledgeItems}
  onDelete={handleDeleteItem}
/>
```

## State Management
- **statusColorMap**: Static mapping of status values to color schemes
- **groupedItems**: Computed grouped items from input items

## Side Effects
No side effects - pure display component

## Related Files
- **Parent components:** KnowledgeBasePage
- **Child components:** 
  - GroupedKnowledgeTableRow (internal component)
  - Card, Badge (UI components)
- **Shared utilities:** 
  - knowledgeBaseService types
  - date-fns for formatting

## Notes
- Groups URL-based items by domain for better organization
- File uploads remain ungrouped and display individually
- Supports status indicators with color coding
- Displays update frequency with appropriate icons
- Responsive table design with horizontal scrolling
- Merges tags from grouped items to show comprehensive tag list

---
*Auto-generated documentation - verify accuracy before use*
