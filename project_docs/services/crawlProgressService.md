# crawlProgressService

**File Path:** `archon-ui-main/src/services/crawlProgressService.ts`
**Last Updated:** 2025-01-22

## Purpose
Service for managing real-time crawl and upload progress tracking via Socket.IO with automatic reconnection, subscription management, and comprehensive progress monitoring.

## Props/Parameters
No props required - this is a service class with methods.

## Dependencies

### Imports
```javascript
import { knowledgeSocketIO, WebSocketService } from './socketIOService';
```

### Exports
```javascript
export const crawlProgressService: CrawlProgressService;
export interface CrawlProgressData;
export interface WorkerProgress;
export interface BatchProgress;
export interface ProgressStep;
export type ProgressCallback = (data: CrawlProgressData) => void;
```

## Key Functions/Methods

### Progress Streaming
- **streamProgress**: Subscribes to progress updates for a specific operation
- **streamProgressEnhanced**: Enhanced streaming with multiple callback types
- **stopProgress**: Stops progress streaming and cleans up subscriptions
- **stopAllProgress**: Stops all active progress streams

### Connection Management
- **connect**: Establishes Socket.IO connection with retry logic
- **disconnect**: Closes connection and cleans up subscriptions
- **reconnect**: Reconnects to Socket.IO server
- **waitForConnection**: Waits for connection establishment with timeout

### Progress Utilities
- **getProgressSteps**: Returns progress steps for different operation types
- **calculateOverallProgress**: Calculates overall progress from multiple workers
- **formatDuration**: Formats duration in human-readable format
- **saveProgressToStorage/loadProgressFromStorage**: Persists progress data
- **clearProgressFromStorage**: Clears stored progress data

## Usage Example
```javascript
import { crawlProgressService } from '../services/crawlProgressService';

// Start progress streaming
await crawlProgressService.streamProgress(
  progressId,
  (data) => {
    console.log('Progress update:', data);
    updateProgressUI(data);
  },
  {
    autoReconnect: true,
    reconnectDelay: 2000,
    connectionTimeout: 10000
  }
);

// Enhanced streaming with multiple callbacks
await crawlProgressService.streamProgressEnhanced(progressId, {
  onMessage: (data) => console.log('Progress:', data),
  onComplete: (data) => console.log('Completed:', data),
  onError: (error) => console.error('Error:', error),
  onReconnect: () => console.log('Reconnected')
});

// Stop specific progress stream
crawlProgressService.stopProgress(progressId);

// Get progress steps for UI
const steps = crawlProgressService.getProgressSteps('crawl');
```

## State Management
- **activeSubscriptions**: Map of active progress subscriptions
- **messageHandlers**: Map of progress message handlers
- **isConnected**: Boolean connection state
- **connectionPromise**: Promise for connection establishment

## Side Effects
- **Socket.IO connection**: Manages WebSocket connection for real-time updates
- **Automatic reconnection**: Reconnects on connection loss
- **Local storage**: Persists progress data across page refreshes
- **Subscription cleanup**: Cleans up subscriptions on disconnect

## Related Files
- **Parent components:** KnowledgeBasePage, CrawlingProgressCard
- **Child components:** None - this is a service layer
- **Shared utilities:** 
  - socketIOService
  - WebSocketService

## Notes
- Uses Socket.IO for reliable real-time communication
- Automatic reconnection with configurable delays
- Subscription management prevents memory leaks
- Supports both crawl and document upload progress
- Comprehensive worker progress tracking
- Batch progress monitoring for large operations
- Local storage persistence for progress recovery
- Enhanced streaming with multiple callback types
- Connection timeout handling
- Detailed logging for debugging

---
*Auto-generated documentation - verify accuracy before use*
