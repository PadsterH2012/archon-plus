# workflowService

**File Path:** `archon-ui-main/src/services/workflowService.ts`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive workflow management service providing complete workflow lifecycle operations including template management, execution control, MCP tool integration, and analytics.

## Props/Parameters
No props required - this is a service class with methods.

## Dependencies

### Imports
```javascript
import { 
  WorkflowTemplate, 
  WorkflowExecution, 
  StepExecution,
  WorkflowListResponse,
  ExecutionListResponse,
  WorkflowFilters,
  ExecutionFilters,
  WorkflowValidationResult,
  MCPTool
} from '../components/workflow/types/workflow.types';
```

### Exports
```javascript
export const workflowService: WorkflowService;
export default workflowService;
```

## Key Functions/Methods

### Workflow Template Operations
- **listWorkflows**: Lists workflow templates with filtering and pagination
- **getWorkflow**: Gets specific workflow template by ID with validation
- **createWorkflow**: Creates new workflow template
- **updateWorkflow**: Updates existing workflow template
- **deleteWorkflow**: Deletes workflow template
- **cloneWorkflow**: Creates copy of existing workflow with new name/title
- **validateWorkflow**: Validates workflow structure and dependencies

### Workflow Execution Operations
- **executeWorkflow**: Starts workflow execution with parameters
- **getExecutionStatus**: Gets execution status with step details
- **listExecutions**: Lists workflow executions with filtering
- **cancelExecution**: Cancels running workflow execution
- **pauseExecution**: Pauses running workflow execution
- **resumeExecution**: Resumes paused workflow execution

### Search and Discovery
- **searchWorkflows**: Searches workflows by query with filters
- **getCategories**: Gets available workflow categories
- **getExamples**: Gets workflow examples and templates
- **getExample**: Gets specific workflow example by name

### MCP Tool Integration
- **getMCPTools**: Gets available MCP tools with categorization
- **getMCPTool**: Gets specific MCP tool details
- **getMCPToolsByCategory**: Gets tools filtered by category
- **suggestMCPTools**: Suggests relevant tools based on description
- **validateWorkflowTools**: Validates tools used in workflow

### Utility Operations
- **checkHealth**: Performs health check on workflow service

## Usage Example
```javascript
import { workflowService } from '../services/workflowService';

// Workflow template management
const workflows = await workflowService.listWorkflows({ category: 'automation' });
const workflow = await workflowService.createWorkflow({
  name: 'data-processing',
  title: 'Data Processing Pipeline',
  description: 'Automated data processing workflow',
  steps: [...]
});

// Workflow execution
const execution = await workflowService.executeWorkflow(
  workflow.id,
  { input_data: 'sample.csv' },
  'user'
);

// Monitor execution
const status = await workflowService.getExecutionStatus(execution.execution_id);

// MCP tool integration
const tools = await workflowService.getMCPTools();
const suggestions = await workflowService.suggestMCPTools('process CSV data');

// Workflow validation
const validation = await workflowService.validateWorkflow(workflow.id);
```

## State Management
No state management - stateless service with methods

## Side Effects
- **HTTP requests**: Makes API calls to workflow management endpoints
- **Workflow execution**: Triggers and manages workflow executions
- **Tool discovery**: Discovers and validates MCP tools
- **Validation**: Validates workflow structure and tool compatibility

## Related Files
- **Parent components:** WorkflowPage, WorkflowBuilder, WorkflowExecutionDashboard
- **Child components:** None - this is a service layer
- **Shared utilities:** 
  - Workflow type definitions
  - API configuration

## Notes
- Comprehensive workflow lifecycle management
- Real-time execution control (start, pause, resume, cancel)
- MCP tool integration with discovery and validation
- Advanced search and filtering capabilities
- Workflow cloning and template management
- Example workflows and templates
- Health monitoring and status checks
- RESTful API design with proper HTTP methods
- Type-safe operations with TypeScript interfaces
- Error handling with detailed error messages

---
*Auto-generated documentation - verify accuracy before use*
