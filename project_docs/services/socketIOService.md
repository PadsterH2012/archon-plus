# socketIOService

**File Path:** `archon-ui-main/src/services/socketIOService.ts`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive WebSocket service using Socket.IO for reliable real-time communication with automatic reconnection, message deduplication, and typed event handling.

## Props/Parameters
No props required - this is a service class with configurable options.

## Dependencies

### Imports
```javascript
import { io, Socket } from 'socket.io-client';
```

### Exports
```javascript
export class WebSocketService;
export enum WebSocketState;
export interface WebSocketConfig;
export interface WebSocketMessage;
export const knowledgeSocketIO: WebSocketService;
export const taskUpdateSocketIO: WebSocketService;
export const projectListSocketIO: WebSocketService;
```

## Key Functions/Methods

### Connection Management
- **connect**: Establishes Socket.IO connection with promise-based handling
- **disconnect**: Gracefully closes connection and cleans up resources
- **reconnect**: Manually triggers reconnection
- **waitForConnection**: Waits for connection establishment with timeout

### Message Handling
- **on**: Registers message handlers for specific event types
- **off**: Unregisters message handlers
- **send**: Sends messages with optional acknowledgment
- **emit**: Emits events to server

### State Management
- **onStateChange**: Registers state change handlers
- **isConnected**: Checks if currently connected
- **getState**: Returns current connection state

### Utility Functions
- **parseEndpoint**: Extracts session ID and room from endpoint
- **isDuplicateMessage**: Checks for message deduplication
- **notifyStateChange/Error**: Internal notification methods

## Usage Example
```javascript
import { knowledgeSocketIO, WebSocketState } from '../services/socketIOService';

// Connect to knowledge base updates
await knowledgeSocketIO.connect('/knowledge-progress');

// Register message handlers
knowledgeSocketIO.on('progress_update', (message) => {
  console.log('Progress update:', message.data);
  updateProgressUI(message.data);
});

// Register state change handler
knowledgeSocketIO.onStateChange((state) => {
  console.log('Connection state:', state);
  if (state === WebSocketState.CONNECTED) {
    console.log('Connected to knowledge updates');
  }
});

// Send message with acknowledgment
await knowledgeSocketIO.send({
  type: 'subscribe',
  data: { progressId: 'crawl-123' }
});

// Disconnect when done
knowledgeSocketIO.disconnect();
```

## State Management
- **socket**: Socket.IO client instance
- **config**: Service configuration options
- **sessionId**: Current session identifier
- **messageHandlers**: Map of event type to handler arrays
- **errorHandlers**: Array of error handlers
- **stateChangeHandlers**: Array of state change handlers
- **connectionPromise**: Promise for connection establishment
- **lastMessages**: Map for message deduplication

## Side Effects
- **Socket.IO connection**: Manages WebSocket connection lifecycle
- **Automatic reconnection**: Reconnects on connection loss with exponential backoff
- **Message deduplication**: Prevents duplicate message processing
- **Heartbeat/keepalive**: Maintains connection health
- **Room management**: Handles Socket.IO room subscriptions

## Related Files
- **Parent components:** All real-time features (knowledge base, tasks, projects)
- **Child components:** None - this is a service layer
- **Shared utilities:** 
  - Socket.IO client library
  - WebSocket state enums

## Notes
- Uses Socket.IO for enhanced reliability over raw WebSockets
- Automatic reconnection with exponential backoff
- Message deduplication within 100ms window
- Promise-based connection establishment
- Typed message handlers for type safety
- Support for Socket.IO rooms and namespaces
- Built-in heartbeat and keepalive mechanisms
- Comprehensive error handling and recovery
- Singleton instances for different feature areas
- Vite proxy integration for development

---
*Auto-generated documentation - verify accuracy before use*
