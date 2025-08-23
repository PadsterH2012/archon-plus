# mcpServerService

**File Path:** `archon-ui-main/src/services/mcpServerService.ts`
**Last Updated:** 2025-01-22

## Purpose
Service for managing the Archon MCP (Model Context Protocol) server lifecycle including start/stop operations, configuration management, real-time logging, and tool execution.

## Props/Parameters
No props required - this is a service class with methods.

## Dependencies

### Imports
```javascript
import { z } from 'zod';
import { getWebSocketUrl } from '../config/api';
```

### Exports
```javascript
export const mcpServerService: MCPServerService;
export const getMCPTools: () => Promise<MCPTool[]>; // Legacy function
export interface ServerStatus;
export interface ServerResponse;
export interface LogEntry;
export interface ServerConfig;
export type MCPTool;
export type MCPParameter;
```

## Key Functions/Methods

### Server Management
- **startServer**: Starts the MCP server and returns status
- **stopServer**: Stops the MCP server gracefully
- **getStatus**: Gets current server status and uptime
- **getConfiguration**: Retrieves server configuration
- **updateConfiguration**: Updates server configuration

### Logging
- **getLogs**: Retrieves historical log entries with optional limit
- **clearLogs**: Clears all server logs
- **streamLogs**: Establishes WebSocket connection for real-time log streaming
- **disconnectLogs**: Closes WebSocket connection and cleans up

### Tool Management
- **getAvailableTools**: Gets available MCP tools from running server
- **callTool**: Executes specific MCP tool with parameters
- **makeMCPCall**: Internal method for MCP protocol communication

## Usage Example
```javascript
import { mcpServerService } from '../services/mcpServerService';

// Server control
const response = await mcpServerService.startServer();
const status = await mcpServerService.getStatus();
await mcpServerService.stopServer();

// Configuration
const config = await mcpServerService.getConfiguration();
await mcpServerService.updateConfiguration({ port: 8051 });

// Logging
const logs = await mcpServerService.getLogs({ limit: 100 });
mcpServerService.streamLogs((log) => {
  console.log('New log:', log);
}, { autoReconnect: true });

// Tool execution
const tools = await mcpServerService.getAvailableTools();
const result = await mcpServerService.callTool('manage_project', {
  action: 'list'
});
```

## State Management
- **logWebSocket**: WebSocket connection for real-time logs
- **reconnectTimeout**: Timeout for WebSocket reconnection
- **isReconnecting**: Boolean flag for reconnection state

## Side Effects
- **HTTP requests**: Makes API calls to MCP server endpoints
- **WebSocket management**: Handles real-time log streaming
- **Automatic reconnection**: Reconnects WebSocket on connection loss
- **Error handling**: Comprehensive error handling with retries

## Related Files
- **Parent components:** MCPPage, MCPClients
- **Child components:** None - this is a service layer
- **Shared utilities:** 
  - API configuration
  - WebSocket utilities
  - Zod validation schemas

## Notes
- Uses Zod schemas for MCP protocol validation
- WebSocket-based real-time log streaming with auto-reconnection
- Comprehensive error handling for all operations
- Support for MCP protocol tool discovery and execution
- Configuration management for server settings
- Legacy function support for backward compatibility
- Relative URLs for Vite proxy integration
- Automatic reconnection with configurable delays
- Type-safe API with TypeScript interfaces

---
*Auto-generated documentation - verify accuracy before use*
