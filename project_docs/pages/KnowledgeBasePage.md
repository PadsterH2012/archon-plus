# KnowledgeBasePage

**File Path:** `archon-ui-main/src/pages/KnowledgeBasePage.tsx`
**Last Updated:** 2025-01-22

## Purpose
Main page component for managing knowledge base items including crawling URLs, uploading documents, viewing/filtering items, and tracking crawl progress with real-time updates.

## Props/Parameters
No props required - this is a top-level page component.

## Dependencies

### Imports
```javascript
import { useEffect, useState, useRef, useMemo, Component, ErrorInfo, ReactNode } from 'react';
import { Search, Grid, Plus, Upload, Link as LinkIcon, Brain, Filter, BoxIcon, List, BookOpen, CheckSquare, AlertTriangle, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { TagInput } from '../components/ui/TagInput';
import { GlassCrawlDepthSelector } from '../components/ui/GlassCrawlDepthSelector';
import { useStaggeredEntrance } from '../hooks/useStaggeredEntrance';
import { useToast } from '../contexts/ToastContext';
import { knowledgeBaseService, KnowledgeItem, KnowledgeItemMetadata } from '../services/knowledgeBaseService';
import { knowledgeSocketIO } from '../services/socketIOService';
import { CrawlingProgressCard } from '../components/knowledge-base/CrawlingProgressCard';
import { CrawlProgressData, crawlProgressService } from '../services/crawlProgressService';
import { WebSocketState } from '../services/socketIOService';
import { KnowledgeTable } from '../components/knowledge-base/KnowledgeTable';
import { KnowledgeItemCard } from '../components/knowledge-base/KnowledgeItemCard';
import { GroupedKnowledgeItemCard } from '../components/knowledge-base/GroupedKnowledgeItemCard';
import { KnowledgeGridSkeleton, KnowledgeTableSkeleton } from '../components/knowledge-base/KnowledgeItemSkeleton';
import { GroupCreationModal } from '../components/knowledge-base/GroupCreationModal';
```

### Exports
```javascript
export default KnowledgeBasePageWithErrorBoundary;
```

## Key Functions/Methods
- **extractDomain**: Extracts clean domain name from URL, removing www and handling subdomains
- **loadKnowledgeItems**: Loads all knowledge items from API with pagination
- **handleAddKnowledge**: Opens the add knowledge modal
- **toggleSelectionMode**: Toggles bulk selection mode for items
- **toggleItemSelection**: Handles individual item selection with shift-click support
- **selectAll/deselectAll**: Bulk selection operations
- **deleteSelectedItems**: Deletes multiple selected items
- **handleRefreshItem**: Refreshes a single knowledge item by re-crawling
- **handleDeleteItem**: Deletes a single item or grouped items
- **handleProgressComplete**: Handles crawl completion events
- **handleProgressError**: Handles crawl error events
- **handleProgressUpdate**: Updates crawl progress in real-time
- **handleRetryProgress**: Retries failed crawl operations
- **handleStopCrawl**: Cancels active crawl operations
- **handleStartCrawl**: Initiates new crawl with progress tracking

## Usage Example
```javascript
import KnowledgeBasePage from './pages/KnowledgeBasePage';

// Used as a route component
<Route path="/knowledge-base" component={KnowledgeBasePage} />
```

## State Management
- **viewMode**: 'grid' | 'table' - Display mode for knowledge items
- **searchQuery**: String for filtering items
- **isAddModalOpen**: Boolean for add knowledge modal visibility
- **isGroupModalOpen**: Boolean for group creation modal visibility
- **typeFilter**: 'all' | 'technical' | 'business' - Filter by knowledge type
- **knowledgeItems**: Array of KnowledgeItem objects
- **progressItems**: Array of CrawlProgressData for active crawls
- **loading**: Boolean for loading state
- **totalItems**: Number of total items for pagination
- **currentPage**: Current page number
- **selectedItems**: Set of selected item IDs for bulk operations
- **isSelectionMode**: Boolean for bulk selection mode
- **lastSelectedIndex**: Number for shift-click range selection

## Side Effects
- **Initial load**: Loads knowledge items via REST API on mount
- **Active crawls**: Restores active crawls from localStorage on mount
- **WebSocket**: Connects to real-time progress updates for crawls
- **Keyboard shortcuts**: Ctrl/Cmd+A for select all, Escape to exit selection mode
- **LocalStorage**: Persists active crawl progress data

## Related Files
- **Parent components:** App routing system
- **Child components:** 
  - CrawlingProgressCard
  - KnowledgeTable
  - KnowledgeItemCard
  - GroupedKnowledgeItemCard
  - KnowledgeItemSkeleton components
  - GroupCreationModal
  - AddKnowledgeModal (internal component)
- **Shared utilities:** 
  - knowledgeBaseService
  - knowledgeSocketIO
  - crawlProgressService
  - useStaggeredEntrance hook
  - useToast context

## Notes
- Includes error boundary wrapper for crash protection
- Uses client-side filtering for better performance
- Supports both URL crawling and file upload
- Real-time progress tracking via WebSocket
- Bulk operations with keyboard shortcuts
- Automatic retry mechanism for failed operations
- Persistent crawl state across page refreshes

---
*Auto-generated documentation - verify accuracy before use*
