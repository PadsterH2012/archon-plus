# WorkflowBuilder

**File Path:** `archon-ui-main/src/components/workflow/WorkflowBuilder.tsx`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive workflow builder component combining form-based editing and visual designer with real-time validation, MCP tool integration, and advanced workflow creation capabilities.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| workflow | WorkflowTemplate | no | - | Existing workflow to edit |
| onSave | (workflow: Partial<WorkflowTemplate>) => void | no | - | Callback when workflow is saved |
| onCancel | () => void | no | - | Callback when editing is cancelled |
| onPreview | (workflow: Partial<WorkflowTemplate>) => void | no | - | Callback for workflow preview |
| onTest | (workflow: Partial<WorkflowTemplate>) => void | no | - | Callback for workflow testing |
| isLoading | boolean | no | false | Loading state for save operations |
| isDarkMode | boolean | no | false | Dark mode flag |
| initialTab | BuilderTab | no | 'metadata' | Initial tab to display |

## Dependencies

### Imports
```javascript
import React, { useState, useCallback, useEffect } from 'react';
import { Settings, Workflow, Eye, Play, Save, ArrowLeft, CheckCircle, AlertCircle, Info, Layers } from 'lucide-react';
import { Button } from '../ui/Button';
import { Tabs } from '../ui/Tabs';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import { WorkflowForm } from './WorkflowForm';
import { WorkflowDesigner } from './WorkflowDesigner';
import { WorkflowTemplate, MCPTool, WorkflowValidationResult, ValidationError } from './types/workflow.types';
```

### Exports
```javascript
export const WorkflowBuilder: React.FC<WorkflowBuilderProps>;
```

## Key Functions/Methods
- **loadTools**: Loads available MCP tools for workflow steps
- **handleWorkflowChange**: Updates workflow data and marks as unsaved
- **validateWorkflow**: Validates workflow structure and dependencies
- **handleSave**: Saves workflow with validation checks
- **handlePreview**: Triggers workflow preview
- **handleTest**: Initiates workflow testing
- **getValidationStatus**: Returns validation status with error/warning counts

## Usage Example
```javascript
import { WorkflowBuilder } from '../components/workflow/WorkflowBuilder';

<WorkflowBuilder
  workflow={existingWorkflow}
  initialTab="designer"
  onSave={handleSaveWorkflow}
  onCancel={handleCancelEdit}
  onPreview={handlePreviewWorkflow}
  onTest={handleTestWorkflow}
  isLoading={isSaving}
  isDarkMode={darkMode}
/>
```

## State Management
- **activeTab**: Current tab ('metadata' | 'designer' | 'validation')
- **workflowData**: Workflow template data being edited
- **availableTools**: Array of available MCP tools
- **validationResult**: Workflow validation results with errors/warnings
- **hasUnsavedChanges**: Boolean indicating unsaved changes

## Side Effects
- **MCP tools loading**: Loads available tools on component mount
- **Real-time validation**: Validates workflow when steps change
- **Unsaved changes tracking**: Tracks modifications for user feedback
- **Toast notifications**: Shows success/error messages for operations

## Related Files
- **Parent components:** WorkflowPage, WorkflowBuilderWrapper
- **Child components:** 
  - WorkflowForm
  - WorkflowDesigner
  - Tabs, Button, Card, Badge (UI components)
- **Shared utilities:** 
  - workflowService
  - useToast context
  - WorkflowTemplate types

## Notes
- Three-tab interface: Metadata, Designer, Validation
- Real-time workflow validation with error/warning display
- MCP tool integration for step creation
- Unsaved changes tracking with user warnings
- Comprehensive validation including dependency checks
- Visual designer for drag-and-drop workflow creation
- Form-based metadata editing
- Preview and testing capabilities
- Dark mode support
- Responsive design with proper loading states

---
*Auto-generated documentation - verify accuracy before use*
