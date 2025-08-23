# MCPPage

**File Path:** `archon-ui-main/src/pages/MCPPage.tsx`
**Last Updated:** 2025-01-22

## Purpose
Main dashboard for managing the MCP (Model Context Protocol) server with comprehensive server control, configuration management, real-time logging, and IDE integration support.

## Props/Parameters
No props required - this is a top-level page component.

## Dependencies

### Imports
```javascript
import { useState, useEffect, useRef } from 'react';
import { Play, Square, Copy, Clock, Server, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { motion } from 'framer-motion';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useStaggeredEntrance } from '../hooks/useStaggeredEntrance';
import { useToast } from '../contexts/ToastContext';
import { mcpServerService, ServerStatus, LogEntry, ServerConfig } from '../services/mcpServerService';
import { IDEGlobalRules } from '../components/settings/IDEGlobalRules';
```

### Exports
```javascript
export const MCPPage: React.FC;
```

## Key Functions/Methods
- **loadStatus**: Loads current MCP server status and uptime
- **loadConfiguration**: Loads server configuration for IDE setup
- **handleStartServer**: Starts the MCP server with status updates
- **handleStopServer**: Stops the MCP server and clears logs
- **handleClearLogs**: Clears server log history
- **handleCopyConfig**: Copies IDE-specific configuration to clipboard
- **generateCursorDeeplink**: Generates Cursor IDE deeplink for one-click setup
- **handleCursorOneClick**: Opens Cursor with pre-configured MCP settings
- **getConfigForIDE**: Returns IDE-specific configuration text
- **getIDEInstructions**: Returns setup instructions for each supported IDE
- **formatUptime**: Formats server uptime in human-readable format
- **formatLogEntry**: Formats log entries for display
- **getStatusIcon/getStatusColor**: Returns appropriate status indicators

## Usage Example
```javascript
import { MCPPage } from './pages/MCPPage';

// Used as a route component
<Route path="/mcp" component={MCPPage} />
```

## State Management
- **serverStatus**: ServerStatus object with status, uptime, and logs
- **config**: ServerConfig object with host, port, and connection details
- **logs**: Array of LogEntry objects for real-time log display
- **isLoading**: Boolean for initial loading state
- **isStarting/isStopping**: Boolean states for server control actions
- **selectedIDE**: Currently selected IDE for configuration display
- **activeTab**: Current tab ('server' | 'clients')

## Side Effects
- **Status polling**: Polls server status every 5 seconds
- **WebSocket logging**: Real-time log streaming when server is running
- **Auto-scroll logs**: Automatically scrolls to latest log entries
- **Configuration loading**: Loads server config when server starts

## Related Files
- **Parent components:** App routing system
- **Child components:** 
  - Card, Button (UI components)
  - IDEGlobalRules (settings component)
  - MCPClients (commented out - not implemented)
- **Shared utilities:** 
  - mcpServerService
  - useStaggeredEntrance hook
  - useToast context

## Notes
- Supports multiple IDEs: Windsurf, Cursor, Claude Code, Cline, Kiro, Augment
- Real-time server monitoring with automatic status updates
- One-click setup for Cursor IDE via deeplink
- Comprehensive logging with WebSocket streaming
- IDE-specific configuration generation
- Server control with proper loading states
- Historical log viewing (last 100 entries)
- Responsive design with animated transitions
- Tab-based interface for server control and client management

---
*Auto-generated documentation - verify accuracy before use*
