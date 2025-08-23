# MCPClients

**File Path:** `archon-ui-main/src/components/mcp/MCPClients.tsx`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive MCP client management interface providing client discovery, connection management, tool testing, and real-time status monitoring for Model Context Protocol clients.

## Props/Parameters
No props required - this is a standalone component.

## Dependencies

### Imports
```javascript
import React, { useState, memo, useEffect } from 'react';
import { Plus, Settings, Trash2, X } from 'lucide-react';
import { ClientCard } from './ClientCard';
import { ToolTestingPanel } from './ToolTestingPanel';
import { Button } from '../ui/Button';
import { mcpClientService, MCPClient, MCPClientConfig } from '../../services/mcpClientService';
import { useToast } from '../../contexts/ToastContext';
import { DeleteConfirmModal } from '../../pages/ProjectPage';
```

### Exports
```javascript
export const MCPClients: React.FC;
export interface Client;
export interface Tool;
export interface ToolParameter;
```

## Key Functions/Methods
- **refreshClientStatuses**: Updates client connection statuses without loading state
- **loadAllClients**: Loads all clients including Archon default and database clients
- **convertDbClientToClient**: Converts database client format to UI client format
- **loadTools**: Loads available tools for connected clients
- **handleAddClient**: Creates new MCP client with configuration
- **handleSelectClient**: Selects client and opens tool testing panel
- **handleEditClient**: Opens client edit drawer
- **handleDeleteClient**: Initiates client deletion with confirmation
- **refreshClients**: Refreshes client list after connection changes
- **confirmDeleteClient**: Executes client deletion after confirmation

## Usage Example
```javascript
import { MCPClients } from '../components/mcp/MCPClients';

// Used within MCPPage
<MCPClients />
```

## State Management
- **clients**: Array of Client objects with real-time status updates
- **isLoading**: Boolean for initial loading state
- **error**: Error message string for display
- **selectedClient**: Currently selected client for tool testing
- **isPanelOpen**: Boolean for tool testing panel visibility
- **isAddClientModalOpen**: Boolean for add client modal
- **editClient**: Client being edited in drawer
- **isEditDrawerOpen**: Boolean for edit drawer visibility
- **showDeleteConfirm**: Boolean for delete confirmation modal
- **clientToDelete**: Client marked for deletion

## Side Effects
- **Periodic status checks**: Updates client statuses every 10 seconds
- **Tool loading**: Loads tools for connected clients automatically
- **Real-time updates**: Monitors client connection states
- **Client management**: Creates, updates, and deletes MCP clients

## Related Files
- **Parent components:** MCPPage
- **Child components:** 
  - ClientCard
  - ToolTestingPanel
  - AddClientModal (internal)
  - EditClientDrawer (internal)
  - DeleteConfirmModal
- **Shared utilities:** 
  - mcpClientService
  - useToast context

## Notes
- Includes hardcoded Archon default client for built-in tools
- Supports HTTP-based MCP client connections
- Real-time status monitoring with periodic updates
- Comprehensive client lifecycle management (CRUD operations)
- Tool discovery and testing capabilities
- Connection state management (connect/disconnect)
- Form validation for client configuration
- Error handling with user-friendly messages
- Responsive design with modal and drawer interfaces
- Memoized component for performance optimization

---
*Auto-generated documentation - verify accuracy before use*
