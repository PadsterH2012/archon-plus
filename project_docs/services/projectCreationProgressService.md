# projectCreationProgressService

**File Path:** `archon-ui-main/src/services/projectCreationProgressService.ts`
**Last Updated:** 2025-01-22

## Purpose
Specialized streaming service for real-time project creation progress monitoring using Socket.IO with automatic reconnection and comprehensive progress tracking.

## Props/Parameters
No props required - this is a service class with methods.

## Dependencies

### Imports
```javascript
import type { Project } from '../types/project';
import { createWebSocketService, WebSocketService, WebSocketState } from './socketIOService';
```

### Exports
```javascript
export const projectCreationProgressService: ProjectCreationProgressService;
export interface ProjectCreationProgressData;
export interface StreamProgressOptions;
```

## Key Functions/Methods
- **streamProgress**: Streams project creation progress using Socket.IO
- **disconnect**: Disconnects from current progress stream
- **getConnectionState**: Gets current WebSocket connection state
- **isConnected**: Checks if currently connected to progress stream

## Usage Example
```javascript
import { projectCreationProgressService } from '../services/projectCreationProgressService';

// Stream project creation progress
await projectCreationProgressService.streamProgress(
  progressId,
  (progressData) => {
    console.log('Progress:', progressData.percentage + '%');
    console.log('Status:', progressData.status);
    console.log('Current Step:', progressData.currentStep);
    
    if (progressData.status === 'completed') {
      console.log('Project created:', progressData.project);
    }
    
    if (progressData.status === 'error') {
      console.error('Creation failed:', progressData.error);
    }
  },
  {
    autoReconnect: true,
    reconnectDelay: 5000
  }
);

// Disconnect when done
projectCreationProgressService.disconnect();
```

## State Management
- **wsService**: WebSocket service instance for Socket.IO connection
- **currentProgressId**: ID of currently monitored progress
- **progressCallback**: Callback function for progress updates
- **isReconnecting**: Boolean indicating reconnection state

## Side Effects
- **Socket.IO connection**: Establishes WebSocket connection for real-time updates
- **Automatic reconnection**: Reconnects on connection loss with configurable delay
- **Progress streaming**: Receives and processes project creation progress events
- **Error handling**: Handles connection errors and progress errors

## Related Files
- **Parent components:** ProjectPage, project creation workflows
- **Child components:** None - this is a service layer
- **Shared utilities:** 
  - socketIOService
  - Project types

## Notes
- Specialized for project creation progress streaming
- Built on top of socketIOService for WebSocket management
- Supports multiple progress event types (project_progress, project_completed, project_error)
- Automatic reconnection with configurable attempts and delays
- Comprehensive progress data including percentage, status, steps, ETA, and logs
- Real-time streaming with Socket.IO for low latency updates
- Error handling for both connection and progress errors
- Singleton pattern for global progress monitoring
- Integration with project creation workflows
- Detailed logging for debugging and monitoring

---
*Auto-generated documentation - verify accuracy before use*
