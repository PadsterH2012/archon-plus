# ClientCard

**File Path:** `archon-ui-main/src/components/mcp/ClientCard.tsx`
**Last Updated:** 2025-01-22

## Purpose
Interactive card component for MCP clients with bioluminescent effects, connection management, and detailed client information display with flip animations.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| client | Client | yes | - | MCP client data to display |
| onSelect | () => void | yes | - | Callback when client is selected |
| onEdit | (client: Client) => void | no | - | Callback when edit action is triggered |
| onDelete | (client: Client) => void | no | - | Callback when delete action is triggered |
| onConnectionChange | () => void | no | - | Callback when connection state changes |

## Dependencies

### Imports
```javascript
import React, { useEffect, useState, useRef } from 'react';
import { Server, Activity, Clock, ChevronRight, Hammer, Settings, Trash2, Plug, PlugZap } from 'lucide-react';
import { Client } from './MCPClients';
import { mcpClientService } from '../../services/mcpClientService';
import { useToast } from '../../contexts/ToastContext';
```

### Exports
```javascript
export const ClientCard: React.FC<ClientCardProps>;
```

## Key Functions/Methods
- **createBioluminescentOrganism**: Creates animated bioluminescent particles for Archon clients
- **spawnOrganismsTowardMouse**: Spawns particles that move toward mouse cursor
- **handleMouseEnter/Move/Leave**: Mouse event handlers for particle effects
- **createAmbientGlow**: Creates ambient particle effects when not hovering
- **toggleFlip**: Flips card to show detailed information
- **handleEdit**: Opens edit modal for client configuration
- **handleConnect**: Connects/disconnects client with loading states
- **handleDelete**: Initiates client deletion

## Usage Example
```javascript
import { ClientCard } from '../components/mcp/ClientCard';

<ClientCard
  client={mcpClient}
  onSelect={() => setSelectedClient(mcpClient)}
  onEdit={openEditModal}
  onDelete={confirmDelete}
  onConnectionChange={refreshClients}
/>
```

## State Management
- **isFlipped**: Boolean for card flip animation state
- **isHovered**: Boolean for hover state tracking
- **isConnecting**: Boolean for connection operation loading
- **particlesRef**: Ref for particle effect container

## Side Effects
- **Bioluminescent effects**: Creates animated particles for Archon clients
- **Mouse tracking**: Tracks mouse movement for particle interactions
- **Connection management**: Handles client connect/disconnect operations
- **Ambient animations**: Creates background particle effects

## Related Files
- **Parent components:** MCPClients
- **Child components:** None - uses Lucide icons
- **Shared utilities:** 
  - mcpClientService
  - useToast context
  - Client type definitions

## Notes
- Special bioluminescent effects for Archon clients
- Status-based color coding (online: cyan/blue, offline: gray, error: pink)
- Interactive flip animation to show detailed information
- Mouse-responsive particle effects with ambient background
- Connection state management with loading indicators
- Responsive design with proper hover states
- Comprehensive error handling for connection operations
- Visual feedback for all user interactions
- Particle cleanup to prevent memory leaks

---
*Auto-generated documentation - verify accuracy before use*
