# CrawlingProgressCard

**File Path:** `archon-ui-main/src/components/knowledge-base/CrawlingProgressCard.tsx`
**Last Updated:** 2025-01-22

## Purpose
Real-time progress card component for displaying crawling and document upload operations with detailed progress steps, logs, and control actions.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| progressData | CrawlProgressData | yes | - | Progress data object containing status, percentage, logs, etc. |
| onComplete | (data: CrawlProgressData) => void | yes | - | Callback when operation completes successfully |
| onError | (error: string) => void | yes | - | Callback when operation encounters an error |
| onProgress | (data: CrawlProgressData) => void | no | - | Callback for progress updates |
| onRetry | () => void | no | - | Callback when retry action is triggered |
| onDismiss | () => void | no | - | Callback when dismiss action is triggered |
| onStop | () => void | no | - | Callback when stop action is triggered |

## Dependencies

### Imports
```javascript
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronDown, ChevronUp, AlertTriangle, CheckCircle, Clock, Globe, 
  FileText, RotateCcw, X, Search, Download, Cpu, Database, Code, Zap, Square 
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { CrawlProgressData } from '../../services/crawlProgressService';
import { useTerminalScroll } from '../../hooks/useTerminalScroll';
import { knowledgeBaseService } from '../../services/knowledgeBaseService';
```

### Exports
```javascript
export const CrawlingProgressCard: React.FC<CrawlingProgressCardProps>;
```

## Key Functions/Methods
- **handleStopCrawl**: Stops active crawl operation with optimistic UI updates
- **getProgressSteps**: Calculates progress steps based on operation type (crawl vs upload)
- **getStatusColor**: Returns appropriate color scheme for current status
- **formatDuration**: Formats elapsed time in human-readable format
- **getEstimatedTimeRemaining**: Calculates estimated completion time

## Usage Example
```javascript
import { CrawlingProgressCard } from '../components/knowledge-base/CrawlingProgressCard';

<CrawlingProgressCard
  progressData={progressItem}
  onComplete={handleProgressComplete}
  onError={handleProgressError}
  onProgress={handleProgressUpdate}
  onRetry={() => handleRetryProgress(progressItem.progressId)}
  onDismiss={() => handleDismissProgress(progressItem.progressId)}
  onStop={() => handleStopProgress(progressItem.progressId)}
/>
```

## State Management
- **showDetailedProgress**: Boolean for detailed progress view visibility
- **showLogs**: Boolean for logs panel visibility
- **isStopping**: Boolean for stop operation loading state

## Side Effects
- **Auto-scrolling logs**: Uses useTerminalScroll hook for automatic log scrolling
- **Optimistic UI updates**: Immediately updates UI when stop action is triggered
- **Real-time updates**: Responds to progress data changes from parent component

## Related Files
- **Parent components:** KnowledgeBasePage
- **Child components:** Card, Button (UI components)
- **Shared utilities:** 
  - CrawlProgressData from crawlProgressService
  - useTerminalScroll hook
  - knowledgeBaseService

## Notes
- Supports both URL crawling and document upload progress tracking
- Different progress steps for different operation types
- Real-time log display with auto-scrolling
- Animated progress indicators with Framer Motion
- Comprehensive error handling and retry mechanisms
- Optimistic UI updates for better user experience
- Responsive design with collapsible sections
- Status-based color coding for visual feedback

---
*Auto-generated documentation - verify accuracy before use*
