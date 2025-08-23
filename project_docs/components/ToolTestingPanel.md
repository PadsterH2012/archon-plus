# ToolTestingPanel

**File Path:** `archon-ui-main/src/components/mcp/ToolTestingPanel.tsx`
**Last Updated:** 2025-01-22

## Purpose
Interactive panel for testing MCP tools with terminal-style output, parameter input forms, resizable interface, and real-time execution feedback.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| client | Client \| null | yes | - | MCP client containing tools to test |
| isOpen | boolean | yes | - | Whether panel is open |
| onClose | () => void | yes | - | Callback when panel is closed |

## Dependencies

### Imports
```javascript
import React, { useEffect, useState, useRef } from 'react';
import { X, Play, ChevronDown, TerminalSquare, Copy, Check, MinusCircle, Maximize2, Minimize2, Hammer, GripHorizontal } from 'lucide-react';
import { Client, Tool } from './MCPClients';
import { Button } from '../ui/Button';
import { mcpClientService } from '../../services/mcpClientService';
```

### Exports
```javascript
export const ToolTestingPanel: React.FC<ToolTestingPanelProps>;
```

## Key Functions/Methods
- **handleToolSelect**: Selects tool and resets parameter values
- **handleParamChange**: Updates parameter values for tool execution
- **addTypingLine**: Adds terminal output with typing animation effect
- **addInstantLine**: Adds terminal output without animation
- **convertParameterValues**: Converts string inputs to proper parameter types
- **executeTool**: Executes selected tool via MCP client service
- **validateParameters**: Validates required parameters before execution
- **executeSelectedTool**: Main execution handler with validation
- **copyTerminalOutput**: Copies terminal content to clipboard
- **handleResizeStart/toggleMaximize**: Panel resizing and maximizing
- **clearTerminal**: Clears terminal output

## Usage Example
```javascript
import { ToolTestingPanel } from '../components/mcp/ToolTestingPanel';

<ToolTestingPanel
  client={selectedMCPClient}
  isOpen={showToolPanel}
  onClose={() => setShowToolPanel(false)}
/>
```

## State Management
- **selectedTool**: Currently selected tool for testing
- **terminalOutput**: Array of terminal lines with typing states
- **paramValues**: Record of parameter name to value mappings
- **isCopied**: Boolean for copy feedback state
- **panelHeight**: Current panel height for resizing
- **isResizing/isMaximized**: Panel state flags
- **isExecuting**: Boolean for tool execution state

## Side Effects
- **Tool selection**: Resets parameters when client or tool changes
- **Auto-scroll**: Automatically scrolls terminal to bottom on new output
- **Resizing**: Handles mouse events for panel resizing
- **Typing animation**: Simulates terminal typing with intervals
- **Parameter validation**: Validates required parameters before execution

## Related Files
- **Parent components:** MCPClients
- **Child components:** Button (UI component)
- **Shared utilities:** 
  - mcpClientService
  - Client and Tool type definitions

## Notes
- Terminal-style interface with typing animations
- Resizable panel with maximize/minimize functionality
- Parameter type conversion (string, number, boolean, array, object)
- Real-time tool execution with MCP protocol
- Comprehensive error handling and validation
- Copy terminal output to clipboard
- Auto-scroll terminal for better UX
- Parameter form generation based on tool schema
- Visual feedback for all user interactions
- Responsive design with proper spacing

---
*Auto-generated documentation - verify accuracy before use*
