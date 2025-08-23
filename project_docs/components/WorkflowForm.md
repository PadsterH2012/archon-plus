# WorkflowForm

**File Path:** `archon-ui-main/src/components/workflow/WorkflowForm.tsx`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive form component for creating and editing workflow metadata with validation, parameter management, and integration with the visual workflow designer.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| workflow | WorkflowTemplate | no | - | Existing workflow to edit |
| onSave | (workflow: Partial<WorkflowTemplate>) => void | no | - | Callback when workflow is saved |
| onCancel | () => void | no | - | Callback when editing is cancelled |
| isLoading | boolean | no | false | Loading state for save operations |
| availableTools | MCPTool[] | no | [] | Available MCP tools for workflow steps |
| isDarkMode | boolean | no | false | Dark mode flag |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect, useCallback } from 'react';
import { Save, X, Plus, Trash2, Settings, Info, Tag, Clock, RefreshCw, Eye, Play } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import { WorkflowTemplate, WorkflowFormProps, WorkflowStatus, WorkflowParameter, WorkflowOutput, MCPTool } from './types/workflow.types';
```

### Exports
```javascript
export const WorkflowForm: React.FC<WorkflowFormProps>;
```

## Key Functions/Methods
- **loadCategories**: Loads available workflow categories from API
- **validateForm**: Validates form data and returns validation errors
- **handleSubmit**: Handles form submission with validation
- **handleInputChange**: Updates form data and clears validation errors
- **addTag/removeTag**: Manages workflow tags
- **addParameter/removeParameter/updateParameter**: Manages workflow parameters
- **addOutput/removeOutput/updateOutput**: Manages workflow outputs

## Usage Example
```javascript
import { WorkflowForm } from '../components/workflow/WorkflowForm';

<WorkflowForm
  workflow={existingWorkflow}
  onSave={handleSaveWorkflow}
  onCancel={handleCancelEdit}
  isLoading={isSaving}
  availableTools={mcpTools}
  isDarkMode={darkMode}
/>
```

## State Management
- **formData**: Partial<WorkflowTemplate> containing form data
- **categories**: Array of available workflow categories
- **newTag**: String for new tag input
- **newParameterKey/newParameterType**: New parameter creation state
- **newOutputKey**: String for new output creation
- **validationErrors**: Record of field validation errors

## Side Effects
- **Categories loading**: Loads workflow categories on component mount
- **Form validation**: Real-time validation with error display
- **Parameter/output management**: Dynamic addition and removal of workflow parameters and outputs

## Related Files
- **Parent components:** WorkflowBuilder
- **Child components:** 
  - Button, Input, Card, Badge (UI components)
- **Shared utilities:** 
  - workflowService
  - useToast context
  - WorkflowTemplate types

## Notes
- Comprehensive workflow metadata editing
- Real-time form validation with error display
- Dynamic parameter and output management
- Tag management with duplicate prevention
- Category selection from API-loaded categories
- Workflow status management (draft, active, deprecated)
- Version control and public/private settings
- Timeout and retry configuration
- Name validation with specific format requirements
- Integration with workflow service for categories
- Dark mode support
- Responsive form layout with proper spacing

---
*Auto-generated documentation - verify accuracy before use*
