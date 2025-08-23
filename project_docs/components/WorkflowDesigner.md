# WorkflowDesigner

**File Path:** `archon-ui-main/src/components/workflow/WorkflowDesigner.tsx`
**Last Updated:** 2025-01-22

## Purpose
Visual drag-and-drop workflow designer interface built with React Flow for node-based workflow creation with multiple step types and real-time validation.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| workflow | WorkflowTemplate | no | - | Existing workflow to edit |
| onSave | (workflow: Partial<WorkflowTemplate>) => void | no | - | Callback when workflow is saved |
| onCancel | () => void | no | - | Callback when editing is cancelled |
| onPreview | (workflow: Partial<WorkflowTemplate>) => void | no | - | Callback for workflow preview |
| onTest | (workflow: Partial<WorkflowTemplate>) => void | no | - | Callback for workflow testing |
| isLoading | boolean | no | false | Loading state for operations |
| isDarkMode | boolean | no | false | Dark mode flag |

## Dependencies

### Imports
```javascript
import React, { useState, useCallback, useMemo, useRef } from 'react';
import '@xyflow/react/dist/style.css';
import { ReactFlow, Node, Edge, Controls, Background, MarkerType, NodeChange, EdgeChange, Connection, applyNodeChanges, applyEdgeChanges, addEdge, Handle, Position, NodeProps, ConnectionLineType, useReactFlow, ReactFlowProvider } from '@xyflow/react';
import { Zap, GitBranch, RotateCcw, Link, List, Plus, Save, Play, Eye, Settings, Trash2, Copy, Download, Upload, Grid, Layers } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import { WorkflowTemplate, WorkflowStep, WorkflowStepType, MCPTool, AccentColor } from './types/workflow.types';
```

### Exports
```javascript
export const WorkflowDesigner: React.FC<WorkflowDesignerProps>;
```

## Key Functions/Methods
- **StandardNode**: Standardized node component for most step types
- **ActionNode**: Node for action steps using standard shape
- **ConditionNode**: Diamond-shaped node for conditional logic
- **ParallelNode**: Node for parallel execution steps
- **LoopNode**: Node for loop/iteration steps
- **WorkflowLinkNode**: Node for linking to other workflows
- **loadTools**: Loads available MCP tools for step creation
- **onNodesChange/onEdgesChange**: Handles React Flow node and edge changes
- **onConnect**: Handles new connections between nodes
- **handleAddStep**: Adds new step node to canvas
- **onNodeClick**: Handles node selection
- **convertToWorkflowSteps**: Converts visual nodes back to workflow steps
- **handleSave/handlePreview**: Saves or previews workflow

## Usage Example
```javascript
import { WorkflowDesigner } from '../components/workflow/WorkflowDesigner';

<WorkflowDesigner
  workflow={existingWorkflow}
  onSave={handleSaveWorkflow}
  onCancel={handleCancelEdit}
  onPreview={handlePreviewWorkflow}
  onTest={handleTestWorkflow}
  isLoading={isSaving}
  isDarkMode={darkMode}
/>
```

## State Management
- **nodes**: Array of React Flow nodes representing workflow steps
- **edges**: Array of React Flow edges representing connections
- **selectedNode**: Currently selected node for editing
- **availableTools**: Array of available MCP tools
- **workflowData**: Workflow template data being edited

## Side Effects
- **MCP tools loading**: Loads available tools on component mount
- **Workflow conversion**: Converts existing workflow to visual nodes
- **Real-time updates**: Updates workflow data as nodes change
- **Node validation**: Validates nodes and shows error states

## Related Files
- **Parent components:** WorkflowBuilder
- **Child components:** 
  - StandardNode, ActionNode, ConditionNode, ParallelNode, LoopNode, WorkflowLinkNode (internal)
  - Button, Card, Badge (UI components)
  - React Flow components
- **Shared utilities:** 
  - workflowService
  - useToast context
  - WorkflowTemplate types

## Notes
- Built with React Flow for professional node-based editing
- Multiple node types: Action, Condition, Parallel, Loop, Workflow Link
- Drag-and-drop interface with visual connections
- Real-time validation with error indicators
- MCP tool integration for step creation
- Standardized node shapes with consistent styling
- Dark mode support with proper theming
- Node selection and editing capabilities
- Conversion between visual representation and workflow data
- Responsive design with proper controls and background

---
*Auto-generated documentation - verify accuracy before use*
