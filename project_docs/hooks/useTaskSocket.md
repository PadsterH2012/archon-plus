# useTaskSocket

**File Path:** `archon-ui-main/src/hooks/useTaskSocket.ts`
**Last Updated:** 2025-01-22

## Purpose
React hook providing simplified real-time task synchronization via WebSocket with automatic connection management, handler registration, and cleanup.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| options | UseTaskSocketOptions | yes | - | Configuration object with project ID and event handlers |

### UseTaskSocketOptions Interface
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| projectId | string | yes | - | Project ID to connect to |
| onTaskCreated | (task: any) => void | no | - | Handler for task creation events |
| onTaskUpdated | (task: any) => void | no | - | Handler for task update events |
| onTaskDeleted | (task: any) => void | no | - | Handler for task deletion events |
| onTaskArchived | (task: any) => void | no | - | Handler for task archival events |
| onTasksReordered | (data: any) => void | no | - | Handler for task reordering events |
| onInitialTasks | (tasks: any[]) => void | no | - | Handler for initial task load |
| onConnectionStateChange | (state: WebSocketState) => void | no | - | Handler for connection state changes |

## Dependencies

### Imports
```javascript
import { useEffect, useRef, useCallback } from 'react';
import { taskSocketService, TaskSocketEvents } from '../services/taskSocketService';
import { WebSocketState } from '../services/socketIOService';
```

### Exports
```javascript
export function useTaskSocket(options: UseTaskSocketOptions);
export interface UseTaskSocketOptions;
```

## Key Functions/Methods
- **memoizedHandlers**: Memoized event handlers to prevent unnecessary re-registrations
- **initializeConnection**: Establishes WebSocket connection and registers handlers
- **Handler updates**: Updates event handlers without reconnecting
- **Project change handling**: Manages reconnection when project changes
- **Cleanup**: Unregisters handlers and disconnects on unmount

## Usage Example
```javascript
import { useTaskSocket } from '../hooks/useTaskSocket';

const { isConnected, connectionState } = useTaskSocket({
  projectId: selectedProject.id,
  onTaskCreated: (task) => {
    console.log('New task created:', task);
    setTasks(prev => [...prev, task]);
  },
  onTaskUpdated: (task) => {
    console.log('Task updated:', task);
    setTasks(prev => prev.map(t => t.id === task.id ? task : t));
  },
  onTaskDeleted: (task) => {
    console.log('Task deleted:', task);
    setTasks(prev => prev.filter(t => t.id !== task.id));
  },
  onConnectionStateChange: (state) => {
    console.log('Connection state:', state);
  }
});
```

## State Management
- **componentIdRef**: Unique component identifier for handler registration
- **currentProjectIdRef**: Reference to current project ID
- **isInitializedRef**: Boolean flag for initialization state

## Side Effects
- **Connection initialization**: Establishes WebSocket connection on mount
- **Handler registration**: Registers event handlers with task socket service
- **Project change handling**: Reconnects when project ID changes
- **Handler updates**: Updates handlers when callbacks change
- **Cleanup**: Unregisters handlers and disconnects on unmount

## Related Files
- **Parent components:** TasksTab
- **Child components:** None - this is a hook
- **Shared utilities:** 
  - taskSocketService
  - socketIOService
  - WebSocketState types

## Notes
- Simplified approach replacing complex optimistic updates pattern
- Automatic connection deduplication via singleton service
- Memoized handlers prevent unnecessary re-registrations
- Handles project changes with automatic reconnection
- Comprehensive cleanup on component unmount
- Unique component ID for handler isolation
- Prevents connection conflicts between multiple components
- Robust error handling with detailed logging
- Supports all task lifecycle events (CRUD + reordering)

---
*Auto-generated documentation - verify accuracy before use*
