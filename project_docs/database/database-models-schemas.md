# Database Models & Schemas Documentation

**File Path:** `python/src/server/models/` directory
**Last Updated:** 2025-08-22

## Purpose
Comprehensive documentation of all Pydantic models and schemas used in the Archon Plus system. These models provide data validation, serialization, and type safety for database operations, API requests/responses, and internal data structures.

## Props/Parameters
All models use Pydantic BaseModel with field validation and type hints

## Dependencies

### Imports
```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from uuid import UUID
from pydantic import BaseModel, Field, validator, model_validator
```

### Exports
```python
# Workflow Models
from .workflow_models import (
    WorkflowTemplate, WorkflowExecution, WorkflowStepExecution,
    WorkflowStatus, WorkflowStepType, WorkflowExecutionStatus,
    ActionStep, ConditionStep, WorkflowLinkStep, ParallelStep, LoopStep
)

# Component Models
from .component_models import (
    ComponentHierarchy, ComponentDependency, ComponentMetadata
)

# Template Models  
from .template_models import (
    TemplateDefinition, TemplateComponent, TemplateAssignment
)

# Template Injection Models
from .template_injection_models import (
    TemplateInjectionTemplate, TemplateComponent, TemplateAssignment
)

# MCP Models
from .models import (
    MCPToolDefinition, MCPToolExecution, MCPClientConfiguration
)
```

## Key Models Overview

### 1. Workflow Models (`workflow_models.py`)
**Purpose:** Complete workflow orchestration system with templates, executions, and step tracking

#### Core Enums
- `WorkflowStatus`: draft, active, deprecated, archived
- `WorkflowStepType`: action, condition, workflow_link, parallel, loop
- `WorkflowExecutionStatus`: pending, running, paused, completed, failed, cancelled
- `StepExecutionStatus`: pending, running, completed, failed, skipped, retrying

#### Primary Models

**WorkflowTemplate**
```python
class WorkflowTemplate(BaseModel):
    id: Optional[UUID]
    name: str  # Unique system identifier
    title: str  # Human-readable title
    description: str = ""
    version: str = "1.0.0"  # Semantic versioning
    status: WorkflowStatus = WorkflowStatus.DRAFT
    category: Optional[str]
    tags: List[str] = []
    parameters: Dict[str, Any] = {}  # Input schema
    outputs: Dict[str, Any] = {}     # Output schema
    steps: List[WorkflowStep]        # Workflow steps
    timeout_minutes: int = 60
    max_retries: int = 3
    retry_delay_seconds: int = 30
    created_by: str = "system"
    is_public: bool = False
    allowed_assignees: List[str] = []
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

**WorkflowExecution**
```python
class WorkflowExecution(BaseModel):
    id: Optional[UUID]
    workflow_template_id: UUID
    triggered_by: str
    trigger_context: Dict[str, Any] = {}
    input_parameters: Dict[str, Any] = {}
    execution_context: Dict[str, Any] = {}
    status: WorkflowExecutionStatus = WorkflowExecutionStatus.PENDING
    current_step_index: int = 0
    total_steps: int = 0
    progress_percentage: float = 0.0  # 0-100
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    paused_at: Optional[datetime]
    output_data: Dict[str, Any] = {}
    error_message: Optional[str]
    error_details: Dict[str, Any] = {}
    execution_log: List[Dict[str, Any]] = []
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

#### Step Types

**ActionStep** - Executes MCP tools
```python
class ActionStep(WorkflowStepBase):
    type: Literal[WorkflowStepType.ACTION]
    tool_name: str  # MCP tool to execute
    parameters: Dict[str, Any] = {}  # Tool parameters with variable substitution
```

**ConditionStep** - Conditional branching
```python
class ConditionStep(WorkflowStepBase):
    type: Literal[WorkflowStepType.CONDITION]
    condition: str  # Condition expression
    on_true: str    # Step if condition is true
    on_false: str   # Step if condition is false
```

**WorkflowLinkStep** - Execute sub-workflows
```python
class WorkflowLinkStep(WorkflowStepBase):
    type: Literal[WorkflowStepType.WORKFLOW_LINK]
    workflow_name: str  # Sub-workflow to execute
    parameters: Dict[str, Any] = {}  # Parameters to pass
```

**ParallelStep** - Concurrent execution
```python
class ParallelStep(WorkflowStepBase):
    type: Literal[WorkflowStepType.PARALLEL]
    steps: List[WorkflowStep]  # Steps to execute in parallel
    wait_for_all: bool = True  # Wait for all to complete
```

**LoopStep** - Iteration over collections
```python
class LoopStep(WorkflowStepBase):
    type: Literal[WorkflowStepType.LOOP]
    collection: str  # Collection variable reference
    item_variable: str  # Current item variable name
    steps: List[WorkflowStep]  # Steps for each iteration
    max_iterations: int = 100  # Safety limit
```

#### Validation Rules

**Name Validation:**
- Alphanumeric characters, underscores, hyphens only
- Converted to lowercase for consistency

**Version Validation:**
- Semantic versioning format (e.g., "1.0.0", "2.1.0-beta")
- Regex pattern: `^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$`

**Step Reference Validation:**
- `on_success`/`on_failure` must reference valid steps or special values ("next", "end", "fail")
- Condition steps validate `on_true`/`on_false` references
- Prevents circular references and orphaned steps

**Progress Validation:**
- Progress percentage: 0-100 range
- Step indexes: non-negative integers
- Timeout values: positive integers

#### Utility Functions

**parse_workflow_step()** - Parse raw step data into typed step objects
**validate_workflow_template_data()** - Validate complete template data
**create_execution_log_entry()** - Standardized logging format
**calculate_workflow_progress()** - Progress calculation with step completion
**get_next_step_name()** - Determine next step based on execution result

---

## Usage Example
```python
# Create workflow template
template = WorkflowTemplate(
    name="deploy_application",
    title="Deploy Application to Production",
    description="Complete deployment workflow with validation",
    steps=[
        ActionStep(
            name="validate_code",
            title="Validate Code Quality",
            tool_name="run_tests",
            parameters={"test_suite": "full"}
        ),
        ConditionStep(
            name="check_tests",
            title="Check Test Results",
            condition="{{validate_code.success}} == true",
            on_true="deploy_staging",
            on_false="notify_failure"
        ),
        ActionStep(
            name="deploy_staging",
            title="Deploy to Staging",
            tool_name="deploy_service",
            parameters={"environment": "staging"}
        )
    ],
    timeout_minutes=30,
    max_retries=2
)

# Execute workflow
execution = WorkflowExecution(
    workflow_template_id=template.id,
    triggered_by="CI/CD Pipeline",
    input_parameters={"branch": "main", "version": "1.2.0"},
    trigger_context={"commit_sha": "abc123", "pr_number": 456}
)
```

## State Management
Models use Pydantic's built-in state management with automatic validation on field assignment

## Side Effects
- Automatic timestamp setting on creation/update
- Validation errors raised on invalid data
- Type coercion for compatible types

## Related Files
- **Parent components:** Database tables (archon_workflow_templates, archon_workflow_executions)
- **Child components:** Workflow services, API endpoints, execution engine
- **Shared utilities:** Validation helpers, serialization utilities

## Notes
- All models support JSON serialization/deserialization
- Comprehensive field validation prevents invalid data
- Union types enable polymorphic step definitions
- Forward reference resolution for recursive structures
- Automatic timestamp management with timezone awareness
- Extensive validation for workflow integrity and step references

---

### 2. Component Models (`component_models.py`)
**Purpose:** Component hierarchy and dependency management system

#### Core Enums
- `ComponentType`: foundation, feature, integration, infrastructure, testing
- `ComponentStatus`: not_started, in_progress, gates_passed, completed, blocked
- `DependencyType`: hard, soft, optional

#### Primary Models

**Component**
```python
class Component(BaseModel):
    id: Optional[UUID]
    project_id: UUID  # Parent project
    name: str  # Unique within project
    description: str = ""
    component_type: ComponentType = ComponentType.FEATURE
    status: ComponentStatus = ComponentStatus.NOT_STARTED
    dependencies: List[UUID] = []  # Component UUIDs this depends on
    completion_gates: List[str] = []  # Gates for completion
    context_data: Dict[str, Any] = {}
    order_index: int = 0  # Display order
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

**ComponentDependency**
```python
class ComponentDependency(BaseModel):
    id: Optional[UUID]
    component_id: UUID  # Component with dependency
    depends_on_component_id: UUID  # Component depended upon
    dependency_type: DependencyType = DependencyType.HARD
    gate_requirements: List[str] = []  # Specific gates required
    created_at: Optional[datetime]
```

#### Validation Rules
- **Name Format:** Alphanumeric, underscores, hyphens, spaces allowed
- **Completion Gates:** Must be from valid set (architecture, design, implementation, testing, integration, documentation, review, deployment)
- **Self-Dependency Prevention:** Component cannot depend on itself
- **Order Index:** Non-negative integers only

---

### 3. Template Injection Models (`template_injection_models.py`)
**Purpose:** Dynamic template injection system for workflow enhancement

#### Core Enums
- `TemplateComponentType`: action, group, sequence
- `TemplateInjectionLevel`: project, milestone, phase, task, subtask
- `TemplateDefinitionType`: project, task, component
- `HierarchyType`: project, milestone, phase, task, subtask

#### Primary Models

**TemplateComponent**
```python
class TemplateComponent(BaseModel):
    id: Optional[UUID]
    name: str  # Format: type::name (e.g., "group::understand_homelab_env")
    description: str = ""
    component_type: TemplateComponentType = TemplateComponentType.GROUP
    instruction_text: str  # Full expanded instruction text
    required_tools: List[str] = []  # MCP tools needed
    estimated_duration: int = 5  # Minutes
    input_requirements: Dict[str, Any] = {}
    output_expectations: Dict[str, Any] = {}
    validation_criteria: List[str] = []
    category: str = "general"
    priority: str = "medium"  # low, medium, high, critical
    tags: List[str] = []
    is_active: bool = True
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

**TemplateDefinition**
```python
class TemplateDefinition(BaseModel):
    id: Optional[UUID]
    name: str  # Unique template name
    description: str = ""
    template_type: TemplateDefinitionType = TemplateDefinitionType.TASK
    template_content: str  # Template with {{placeholder}} variables
    user_task_position: int = 6  # Where {{USER_TASK}} appears
    estimated_duration: int = 30  # Total duration in minutes
    required_tools: List[str] = []
    applicable_phases: List[str] = []  # Development phases
    is_active: bool = True
    version: str = "1.0.0"
    author: str = "archon-system"
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

**TemplateAssignment**
```python
class TemplateAssignment(BaseModel):
    id: Optional[UUID]
    hierarchy_type: HierarchyType  # What level this applies to
    hierarchy_id: UUID  # Reference to project/task/etc
    template_definition_id: UUID  # Template to apply
    assignment_context: Dict[str, Any] = {}
    priority: int = 0  # Conflict resolution priority
    conditional_logic: Dict[str, Any] = {}
    is_active: bool = True
    assigned_at: Optional[datetime]
    assigned_by: str = "system"
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

#### Validation Rules
- **Component Name Format:** Must follow `type::name` pattern (e.g., `group::understand_homelab_env`)
- **Priority Levels:** Must be one of: low, medium, high, critical
- **Duration Validation:** Positive integers only
- **Template Content:** Must contain valid placeholder syntax
- **Hierarchy Uniqueness:** One template per hierarchy level

---

### 4. Template Models (`template_models.py`)
**Purpose:** Legacy template system for component definitions

#### Primary Models

**TemplateDefinition** (Legacy)
```python
class TemplateDefinition(BaseModel):
    id: Optional[UUID]
    name: str  # Template identifier
    description: str = ""
    template_content: str  # Template content
    variables: List[str] = []  # Template variables
    category: str = "general"
    is_active: bool = True
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

---

### 5. MCP Models (`models.py`)
**Purpose:** Model Context Protocol integration models

#### Primary Models

**MCPToolDefinition**
```python
class MCPToolDefinition(BaseModel):
    name: str  # Tool name
    description: str  # Tool description
    parameters: Dict[str, Any] = {}  # Tool parameters schema
    required_parameters: List[str] = []
    optional_parameters: List[str] = []
    return_type: str = "object"
    examples: List[Dict[str, Any]] = []
```

**MCPToolExecution**
```python
class MCPToolExecution(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}
    execution_id: Optional[UUID]
    status: str = "pending"  # pending, running, completed, failed
    result: Dict[str, Any] = {}
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

**MCPClientConfiguration**
```python
class MCPClientConfiguration(BaseModel):
    client_name: str
    server_url: str
    authentication: Dict[str, Any] = {}
    timeout_seconds: int = 30
    retry_attempts: int = 3
    is_active: bool = True
```

---
*Auto-generated documentation - verify accuracy before use*
