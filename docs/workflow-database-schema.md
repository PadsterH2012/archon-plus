# Workflow System Database Schema

## Overview

The Archon Workflow System database schema is designed to support dynamic workflow orchestration with the following key capabilities:

- **Reusable Workflow Templates**: Define workflows once, execute many times
- **Step-by-Step Execution Tracking**: Monitor progress at granular level
- **Version Control**: Track changes to workflow templates over time
- **Error Handling & Retry Logic**: Built-in resilience mechanisms
- **Integration Ready**: Seamless integration with existing Archon MCP tools

## Database Tables

### 1. `archon_workflow_templates`

**Purpose**: Stores reusable workflow definitions that can be executed multiple times.

**Key Fields**:
- `id`: UUID primary key
- `name`: Unique system name (snake_case, used for API calls)
- `title`: Human-readable display name
- `description`: Detailed workflow description
- `version`: Semantic version (e.g., "1.0.0")
- `status`: Workflow lifecycle status (`draft`, `active`, `deprecated`, `archived`)
- `category`: Grouping category (e.g., "infrastructure", "deployment")
- `tags`: JSONB array for flexible categorization
- `parameters`: JSONB schema defining input parameters
- `outputs`: JSONB schema defining expected outputs
- `steps`: JSONB array containing workflow step definitions
- `timeout_minutes`: Maximum execution time
- `max_retries`: Number of retry attempts for failed steps
- `created_by`: Creator identifier
- `is_public`: Whether workflow is available to all users

**Step Definition Structure** (in `steps` JSONB field):
```json
{
  "name": "create_vm",
  "title": "Create Virtual Machine",
  "type": "action",
  "tool_name": "manage_infrastructure",
  "parameters": {
    "action": "create_vm",
    "template": "{{workflow.parameters.vm_template}}",
    "name": "{{workflow.parameters.vm_name}}"
  },
  "on_success": "next",
  "on_failure": "retry",
  "retry_count": 3,
  "timeout_seconds": 300
}
```

### 2. `archon_workflow_executions`

**Purpose**: Tracks individual workflow execution instances with status and progress.

**Key Fields**:
- `id`: UUID primary key
- `workflow_template_id`: Reference to template being executed
- `triggered_by`: Agent/user who started the execution
- `trigger_context`: JSONB context (task ID, event data, etc.)
- `input_parameters`: JSONB actual input values
- `execution_context`: JSONB runtime variables and state
- `status`: Current execution status (`pending`, `running`, `paused`, `completed`, `failed`, `cancelled`)
- `current_step_index`: Index of currently executing step
- `total_steps`: Total number of steps in workflow
- `progress_percentage`: Calculated progress (0-100)
- `started_at`, `completed_at`, `paused_at`: Timing information
- `output_data`: JSONB final results
- `error_message`, `error_details`: Error information
- `execution_log`: JSONB array of log entries

**Execution Log Entry Structure**:
```json
{
  "timestamp": "2025-08-18T10:30:00Z",
  "level": "info",
  "step_index": 2,
  "step_name": "create_vm",
  "message": "VM creation started",
  "details": {"vm_id": "vm-12345"}
}
```

### 3. `archon_workflow_step_executions`

**Purpose**: Records detailed execution information for each step within a workflow run.

**Key Fields**:
- `id`: UUID primary key
- `workflow_execution_id`: Reference to parent execution
- `step_index`: Position of step in workflow
- `step_name`: Name of the step
- `step_type`: Type of step (`action`, `condition`, `workflow_link`, `parallel`, `loop`)
- `step_config`: JSONB snapshot of step configuration
- `status`: Step execution status (`pending`, `running`, `completed`, `failed`, `skipped`, `retrying`)
- `attempt_number`: Current retry attempt
- `max_attempts`: Maximum retry attempts
- `input_data`, `output_data`: JSONB step inputs and outputs
- `tool_name`: MCP tool used (for action steps)
- `tool_parameters`, `tool_result`: Tool execution details
- `sub_workflow_execution_id`: Reference to sub-workflow (for workflow_link steps)
- `error_message`, `error_details`: Error information

### 4. `archon_workflow_template_versions`

**Purpose**: Maintains complete version history for workflow templates.

**Key Fields**:
- `id`: UUID primary key
- `workflow_template_id`: Reference to template
- `version_number`: Incremental version number
- `version_tag`: Semantic version tag (e.g., "1.0.0")
- `template_snapshot`: JSONB complete template data at this version
- `change_summary`: Human-readable description of changes
- `change_type`: Type of change (`create`, `update`, `major`, `minor`, `patch`)
- `breaking_changes`: Boolean flag for breaking changes
- `created_by`: Who made the changes

## Workflow Step Types

### 1. Action Steps
Execute MCP tools with parameters:
```json
{
  "type": "action",
  "tool_name": "manage_task_archon",
  "parameters": {
    "action": "create",
    "project_id": "{{context.project_id}}",
    "title": "Deploy application"
  }
}
```

### 2. Condition Steps
Conditional branching based on data:
```json
{
  "type": "condition",
  "condition": "{{previous_step.output.status}} == 'success'",
  "on_true": "deploy_step",
  "on_false": "rollback_step"
}
```

### 3. Workflow Link Steps
Execute sub-workflows:
```json
{
  "type": "workflow_link",
  "workflow_name": "backup_database",
  "parameters": {
    "database_id": "{{context.database_id}}"
  }
}
```

### 4. Parallel Steps
Execute multiple steps concurrently:
```json
{
  "type": "parallel",
  "steps": [
    {"type": "action", "tool_name": "backup_data"},
    {"type": "action", "tool_name": "notify_users"}
  ]
}
```

### 5. Loop Steps
Iterate over collections:
```json
{
  "type": "loop",
  "collection": "{{workflow.parameters.servers}}",
  "item_variable": "server",
  "steps": [
    {
      "type": "action",
      "tool_name": "deploy_to_server",
      "parameters": {"server": "{{server}}"}
    }
  ]
}
```

## Indexing Strategy

**Performance Optimizations**:
- Templates: Indexed by name, status, category, tags (GIN)
- Executions: Indexed by template_id, status, triggered_by, started_at
- Step Executions: Indexed by execution_id, step_index, status, tool_name
- Versions: Indexed by template_id, version_number

## Security & Access Control

**Row Level Security (RLS)**:
- Public read access for all workflow data
- Service role has full access for system operations
- Future: User-based access control for private workflows

## Integration Points

**Existing Archon Systems**:
- **Projects**: Workflows can be triggered from project tasks
- **Tasks**: Task creation can automatically suggest relevant workflows
- **MCP Tools**: All existing tools can be used in workflow steps
- **Version Control**: Workflow templates use same versioning patterns as documents

## Example Workflow Template

```json
{
  "name": "vm_deployment",
  "title": "Virtual Machine Deployment",
  "description": "Complete VM deployment with backup and monitoring setup",
  "category": "infrastructure",
  "parameters": {
    "vm_name": {"type": "string", "required": true},
    "vm_template": {"type": "string", "default": "ubuntu-22.04"},
    "backup_enabled": {"type": "boolean", "default": true}
  },
  "steps": [
    {
      "name": "check_resources",
      "type": "action",
      "tool_name": "check_infrastructure_capacity",
      "parameters": {"template": "{{workflow.parameters.vm_template}}"}
    },
    {
      "name": "create_vm",
      "type": "action",
      "tool_name": "create_virtual_machine",
      "parameters": {
        "name": "{{workflow.parameters.vm_name}}",
        "template": "{{workflow.parameters.vm_template}}"
      }
    },
    {
      "name": "setup_backup",
      "type": "condition",
      "condition": "{{workflow.parameters.backup_enabled}} == true",
      "on_true": {
        "type": "workflow_link",
        "workflow_name": "setup_vm_backup",
        "parameters": {"vm_id": "{{steps.create_vm.output.vm_id}}"}
      }
    },
    {
      "name": "update_cmdb",
      "type": "action",
      "tool_name": "update_configuration_database",
      "parameters": {
        "vm_id": "{{steps.create_vm.output.vm_id}}",
        "status": "deployed"
      }
    }
  ]
}
```

## Migration Instructions

1. **Apply Migration**: Run `migration/add_workflow_system.sql` in Supabase SQL Editor
2. **Verify Tables**: Check that all 4 tables are created with proper constraints
3. **Test Permissions**: Verify RLS policies allow expected access
4. **Rollback Available**: Use `migration/rollback_workflow_system.sql` if needed

## Next Steps

After database schema is deployed:
1. Implement Pydantic models for type safety
2. Create repository layer for data access
3. Build workflow execution engine
4. Add API endpoints for workflow management
5. Integrate with existing MCP tools
