# WorkflowPage

**File Path:** `archon-ui-main/src/pages/WorkflowPage.tsx`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive workflow management page providing workflow creation, execution, monitoring, and analytics with advanced routing and real-time execution tracking.

## Props/Parameters
No props required - this is a top-level page component with routing.

## Dependencies

### Imports
```javascript
import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Workflow, Activity, Plus, History, GitBranch, Users, Clock, BarChart3, Edit, Copy, Trash2, Info, X } from 'lucide-react';
import { WorkflowBuilder } from '../components/workflow/WorkflowBuilder';
import { WorkflowExecutionDashboard } from '../components/workflow/WorkflowExecutionDashboard';
import { WorkflowAnalytics } from '../components/workflow/WorkflowAnalytics';
import { WorkflowScheduler } from '../components/workflow/WorkflowScheduler';
import { workflowService } from '../services/workflowService';
```

### Exports
```javascript
export default WorkflowPage;
export const WorkflowBuilderWrapper: React.FC;
export const SimpleWorkflowDashboard: React.FC;
```

## Key Functions/Methods

### WorkflowBuilderWrapper
- **handleSave**: Saves workflow (create or update) and navigates back to dashboard
- **handleCancel**: Cancels workflow editing and returns to dashboard

### SimpleWorkflowDashboard
- **executeWorkflow**: Executes workflow with real-time status tracking
- **createMCPWorkflow**: Creates MCP-specific workflows
- **handleEditWorkflow**: Opens workflow in metadata editing mode
- **handleDesignWorkflow**: Opens workflow in visual designer mode
- **handleCloneWorkflow**: Creates copy of existing workflow
- **handleDeleteWorkflow**: Deletes workflow with confirmation
- **handleShowWorkflowInfo**: Shows detailed workflow information modal

## Usage Example
```javascript
import WorkflowPage from './pages/WorkflowPage';

// Used as a route component with nested routing
<Route path="/workflows/*" element={<WorkflowPage />} />

// Nested routes within WorkflowPage:
// /workflows - Main dashboard
// /workflows/builder - Workflow builder
// /workflows/executions - Execution dashboard
// /workflows/analytics - Analytics dashboard
// /workflows/scheduler - Scheduling interface
```

## State Management

### WorkflowBuilderWrapper
- **workflow**: Workflow data passed via route state
- **initialTab**: Initial tab for workflow builder

### SimpleWorkflowDashboard
- **workflows**: Array of workflow templates
- **loading**: Boolean for loading state
- **error**: Error message string
- **executing**: ID of currently executing workflow
- **showCreateForm**: Boolean for create form visibility
- **recentExecutions**: Array of recent execution data
- **showMCPWorkflowForm**: Boolean for MCP workflow form
- **selectedWorkflowInfo**: Selected workflow for info modal

## Side Effects
- **API connection test**: Tests workflow API on component mount
- **Workflow execution**: Real-time execution with status updates
- **Navigation**: Route-based navigation between workflow features
- **Recent executions**: Tracks and displays last 5 executions

## Related Files
- **Parent components:** App routing system
- **Child components:** 
  - WorkflowBuilder
  - WorkflowExecutionDashboard
  - WorkflowAnalytics
  - WorkflowScheduler
  - Various workflow forms and modals
- **Shared utilities:** 
  - workflowService
  - React Router for navigation

## Notes
- Advanced routing with nested routes for different workflow features
- Real-time workflow execution with progress tracking
- MCP (Model Context Protocol) workflow integration
- Workflow cloning and template management
- Recent executions tracking with status updates
- Comprehensive CRUD operations for workflows
- Modal-based workflow information display
- Navigation state management for workflow editing
- Error handling with user-friendly alerts
- Responsive design with proper loading states

---
*Auto-generated documentation - verify accuracy before use*
