# mcpClientService

**File Path:** `archon-ui-main/src/services/mcpClientService.ts`
**Last Updated:** 2025-01-22

## Purpose
Universal MCP client service for managing Model Context Protocol clients, tool discovery, execution, and connection management with comprehensive CRUD operations.

## Props/Parameters
No props required - this is a service class with methods.

## Dependencies

### Imports
```javascript
import { z } from 'zod';
import { getApiUrl } from '../config/api';
```

### Exports
```javascript
export const mcpClientService: MCPClientService;
export interface MCPClientConfig;
export interface MCPClient;
export interface MCPClientTool;
export interface ToolCallRequest;
export interface ClientStatus;
export type MCPTool;
export type MCPParameter;
```

## Key Functions/Methods

### Client Management
- **getClients**: Retrieves all MCP clients
- **createClient**: Creates new MCP client with configuration
- **getClient**: Gets single client by ID
- **updateClient**: Updates client configuration
- **deleteClient**: Deletes client and cleans up resources

### Connection Management
- **connectClient**: Connects client to MCP server
- **disconnectClient**: Disconnects client from server
- **getClientStatus**: Gets current connection status
- **testClientConfig**: Tests client configuration before creation
- **connectMultipleClients**: Connects multiple clients in parallel
- **getAllClientStatuses**: Gets status for all clients
- **autoConnectClients**: Connects all clients with auto_connect enabled

### Tool Operations
- **getClientTools**: Gets available tools for specific client
- **callClientTool**: Executes tool via MCP protocol
- **getAllAvailableTools**: Gets tools from all clients and Archon
- **discoverClientTools**: Discovers tools from client server

### Archon Integration
- **createArchonClient**: Creates default Archon MCP client
- **getOrCreateArchonClient**: Gets existing or creates new Archon client

## Usage Example
```javascript
import { mcpClientService } from '../services/mcpClientService';

// Client management
const clients = await mcpClientService.getClients();
const client = await mcpClientService.createClient({
  name: "Custom MCP Server",
  transport_type: "http",
  connection_config: {
    url: "http://localhost:8052/mcp"
  },
  auto_connect: true
});

// Connection management
await mcpClientService.connectClient(client.id);
const status = await mcpClientService.getClientStatus(client.id);

// Tool operations
const tools = await mcpClientService.getClientTools(client.id);
const result = await mcpClientService.callClientTool({
  client_id: client.id,
  tool_name: "manage_project",
  arguments: { action: "list" }
});

// Archon integration
const archonClient = await mcpClientService.getOrCreateArchonClient();
```

## State Management
No state management - stateless service with methods

## Side Effects
- **HTTP requests**: Makes API calls to MCP client management endpoints
- **Client connections**: Manages MCP server connections
- **Tool discovery**: Discovers and caches available tools
- **Error handling**: Comprehensive error handling with detailed messages

## Related Files
- **Parent components:** MCPPage, MCPClients, ToolTestingPanel
- **Child components:** None - this is a service layer
- **Shared utilities:** 
  - API configuration
  - Zod validation schemas

## Notes
- Supports only HTTP transport type for MCP clients
- Comprehensive Zod schema validation for MCP protocol
- Parallel operations for multiple client management
- Auto-connect functionality for seamless startup
- Default Archon client creation and management
- Environment variable configuration support
- Type-safe API with TypeScript interfaces
- RESTful API design with proper HTTP methods
- Error handling with detailed error messages

---
*Auto-generated documentation - verify accuracy before use*
