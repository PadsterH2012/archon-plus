"""
Pydantic Models for Archon Workflow System

This module defines Pydantic models for:
- Workflow templates and their components
- Workflow executions and step tracking
- Workflow validation and serialization
- Integration with MCP tools and existing Archon systems
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from uuid import UUID

from pydantic import BaseModel, Field, validator, model_validator


# =====================================================
# ENUMS - Match database enum definitions
# =====================================================

class WorkflowStatus(str, Enum):
    """Workflow template lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class WorkflowStepType(str, Enum):
    """Types of workflow steps"""
    ACTION = "action"           # Execute MCP tool
    CONDITION = "condition"     # Conditional branching
    WORKFLOW_LINK = "workflow_link"  # Execute sub-workflow
    PARALLEL = "parallel"       # Execute steps concurrently
    LOOP = "loop"              # Iterate over collection


class WorkflowExecutionStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepExecutionStatus(str, Enum):
    """Individual step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


# =====================================================
# WORKFLOW STEP MODELS
# =====================================================

class WorkflowStepBase(BaseModel):
    """Base class for all workflow steps"""
    name: str = Field(..., description="Unique step name within workflow")
    title: str = Field(..., description="Human-readable step title")
    description: str = Field(default="", description="Step description")
    type: WorkflowStepType = Field(..., description="Type of workflow step")
    timeout_seconds: int = Field(default=300, description="Step timeout in seconds")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    retry_delay_seconds: int = Field(default=30, description="Delay between retries")
    on_success: str = Field(default="next", description="Next step on success")
    on_failure: str = Field(default="fail", description="Action on failure")
    
    @validator("name")
    def validate_name(cls, v):
        """Validate step name format"""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Step name must contain only alphanumeric characters, underscores, and hyphens")
        return v
    
    @validator("timeout_seconds", "retry_delay_seconds")
    def validate_positive_seconds(cls, v):
        """Validate positive time values"""
        if v <= 0:
            raise ValueError("Time values must be positive")
        return v
    
    @validator("retry_count")
    def validate_retry_count(cls, v):
        """Validate retry count"""
        if v < 0:
            raise ValueError("Retry count must be non-negative")
        return v


class ActionStep(WorkflowStepBase):
    """Step that executes an MCP tool"""
    type: Literal[WorkflowStepType.ACTION] = Field(default=WorkflowStepType.ACTION)
    tool_name: str = Field(..., description="Name of MCP tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters with variable substitution")
    
    @validator("tool_name")
    def validate_tool_name(cls, v):
        """Validate tool name is not empty"""
        if not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip()


class ConditionStep(WorkflowStepBase):
    """Step that provides conditional branching"""
    type: Literal[WorkflowStepType.CONDITION] = Field(default=WorkflowStepType.CONDITION)
    condition: str = Field(..., description="Condition expression to evaluate")
    on_true: str = Field(..., description="Step to execute if condition is true")
    on_false: str = Field(..., description="Step to execute if condition is false")
    
    @validator("condition")
    def validate_condition(cls, v):
        """Validate condition is not empty"""
        if not v.strip():
            raise ValueError("Condition cannot be empty")
        return v.strip()


class WorkflowLinkStep(WorkflowStepBase):
    """Step that executes a sub-workflow"""
    type: Literal[WorkflowStepType.WORKFLOW_LINK] = Field(default=WorkflowStepType.WORKFLOW_LINK)
    workflow_name: str = Field(..., description="Name of workflow to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters to pass to sub-workflow")
    
    @validator("workflow_name")
    def validate_workflow_name(cls, v):
        """Validate workflow name is not empty"""
        if not v.strip():
            raise ValueError("Workflow name cannot be empty")
        return v.strip()


class ParallelStep(WorkflowStepBase):
    """Step that executes multiple steps concurrently"""
    type: Literal[WorkflowStepType.PARALLEL] = Field(default=WorkflowStepType.PARALLEL)
    steps: List['WorkflowStep'] = Field(..., description="Steps to execute in parallel")
    wait_for_all: bool = Field(default=True, description="Wait for all steps to complete")
    
    @validator("steps")
    def validate_parallel_steps(cls, v):
        """Validate parallel steps"""
        if not v:
            raise ValueError("Parallel step must have at least one sub-step")
        return v


class LoopStep(WorkflowStepBase):
    """Step that iterates over a collection"""
    type: Literal[WorkflowStepType.LOOP] = Field(default=WorkflowStepType.LOOP)
    collection: str = Field(..., description="Collection to iterate over (variable reference)")
    item_variable: str = Field(..., description="Variable name for current item")
    steps: List['WorkflowStep'] = Field(..., description="Steps to execute for each item")
    max_iterations: int = Field(default=100, description="Maximum number of iterations")
    
    @validator("collection", "item_variable")
    def validate_loop_variables(cls, v):
        """Validate loop variables are not empty"""
        if not v.strip():
            raise ValueError("Loop variables cannot be empty")
        return v.strip()
    
    @validator("max_iterations")
    def validate_max_iterations(cls, v):
        """Validate max iterations is positive"""
        if v <= 0:
            raise ValueError("Max iterations must be positive")
        return v


# Union type for all step types
WorkflowStep = Union[ActionStep, ConditionStep, WorkflowLinkStep, ParallelStep, LoopStep]

# Update forward references
ParallelStep.model_rebuild()
LoopStep.model_rebuild()


# =====================================================
# WORKFLOW TEMPLATE MODEL
# =====================================================

class WorkflowTemplate(BaseModel):
    """Complete workflow template definition"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Workflow template UUID")
    name: str = Field(..., description="Unique workflow name (system identifier)")
    title: str = Field(..., description="Human-readable workflow title")
    description: str = Field(default="", description="Detailed workflow description")
    version: str = Field(default="1.0.0", description="Semantic version")
    status: WorkflowStatus = Field(default=WorkflowStatus.DRAFT, description="Workflow lifecycle status")
    
    # Categorization
    category: Optional[str] = Field(None, description="Workflow category")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    # Workflow Definition
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Input parameters schema")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Expected outputs schema")
    steps: List[WorkflowStep] = Field(..., description="Workflow steps")
    
    # Execution Settings
    timeout_minutes: int = Field(default=60, description="Maximum execution time")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay_seconds: int = Field(default=30, description="Delay between retries")
    
    # Permissions
    created_by: str = Field(default="system", description="Creator identifier")
    is_public: bool = Field(default=False, description="Whether workflow is public")
    allowed_assignees: List[str] = Field(default_factory=list, description="Allowed assignees")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator("name")
    def validate_name_format(cls, v):
        """Validate workflow name format"""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Workflow name must contain only alphanumeric characters, underscores, and hyphens")
        return v.lower()
    
    @validator("version")
    def validate_version_format(cls, v):
        """Validate semantic version format"""
        import re
        if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$', v):
            raise ValueError("Version must follow semantic versioning (e.g., '1.0.0' or '1.0.0-beta')")
        return v
    
    @validator("steps")
    def validate_steps_not_empty(cls, v):
        """Validate workflow has at least one step"""
        if not v:
            raise ValueError("Workflow must have at least one step")
        return v
    
    @validator("timeout_minutes")
    def validate_timeout_positive(cls, v):
        """Validate timeout is positive"""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v
    
    @model_validator(mode='before')
    @classmethod
    def validate_step_references(cls, values):
        """Validate step references are valid"""
        steps = values.get('steps', [])
        if not steps:
            return values
        
        step_names = {step.name for step in steps}
        
        for step in steps:
            # Validate on_success and on_failure references
            if step.on_success not in ["next", "end", "fail"] and step.on_success not in step_names:
                raise ValueError(f"Step '{step.name}' references unknown step '{step.on_success}' in on_success")
            
            if step.on_failure not in ["fail", "retry", "end"] and step.on_failure not in step_names:
                raise ValueError(f"Step '{step.name}' references unknown step '{step.on_failure}' in on_failure")
            
            # Validate condition step references
            if isinstance(step, ConditionStep):
                if step.on_true not in step_names and step.on_true not in ["end", "fail"]:
                    raise ValueError(f"Condition step '{step.name}' references unknown step '{step.on_true}' in on_true")
                if step.on_false not in step_names and step.on_false not in ["end", "fail"]:
                    raise ValueError(f"Condition step '{step.name}' references unknown step '{step.on_false}' in on_false")
        
        return values
    
    @validator("created_at", "updated_at", pre=True, always=True)
    def set_timestamps(cls, v):
        """Set default timestamps"""
        return v or datetime.now()


# =====================================================
# WORKFLOW EXECUTION MODELS
# =====================================================

class WorkflowExecution(BaseModel):
    """Workflow execution instance"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Execution UUID")
    workflow_template_id: UUID = Field(..., description="Template being executed")
    
    # Execution Context
    triggered_by: str = Field(..., description="Agent/user who triggered execution")
    trigger_context: Dict[str, Any] = Field(default_factory=dict, description="Trigger context")
    input_parameters: Dict[str, Any] = Field(default_factory=dict, description="Input values")
    execution_context: Dict[str, Any] = Field(default_factory=dict, description="Runtime context")
    
    # Status and Progress
    status: WorkflowExecutionStatus = Field(default=WorkflowExecutionStatus.PENDING)
    current_step_index: int = Field(default=0, description="Current step index")
    total_steps: int = Field(default=0, description="Total number of steps")
    progress_percentage: float = Field(default=0.0, description="Progress percentage")
    
    # Timing
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")
    paused_at: Optional[datetime] = Field(None, description="Execution pause time")
    
    # Results
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Execution outputs")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed error info")
    execution_log: List[Dict[str, Any]] = Field(default_factory=list, description="Execution log")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator("progress_percentage")
    def validate_progress_range(cls, v):
        """Validate progress is between 0 and 100"""
        if not 0 <= v <= 100:
            raise ValueError("Progress percentage must be between 0 and 100")
        return v
    
    @validator("current_step_index")
    def validate_step_index_non_negative(cls, v):
        """Validate step index is non-negative"""
        if v < 0:
            raise ValueError("Step index must be non-negative")
        return v
    
    @validator("created_at", "updated_at", pre=True, always=True)
    def set_timestamps(cls, v):
        """Set default timestamps"""
        return v or datetime.now()


class WorkflowStepExecution(BaseModel):
    """Individual step execution within a workflow"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Step execution UUID")
    workflow_execution_id: UUID = Field(..., description="Parent execution UUID")
    
    # Step Identification
    step_index: int = Field(..., description="Step position in workflow")
    step_name: str = Field(..., description="Step name")
    step_type: WorkflowStepType = Field(..., description="Step type")
    step_config: Dict[str, Any] = Field(default_factory=dict, description="Step configuration snapshot")
    
    # Execution Details
    status: StepExecutionStatus = Field(default=StepExecutionStatus.PENDING)
    attempt_number: int = Field(default=1, description="Current attempt number")
    max_attempts: int = Field(default=1, description="Maximum attempts")
    
    # Timing
    started_at: Optional[datetime] = Field(None, description="Step start time")
    completed_at: Optional[datetime] = Field(None, description="Step completion time")
    
    # Data
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Step input data")
    output_data: Dict[str, Any] = Field(default_factory=dict, description="Step output data")
    
    # Error Handling
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed error info")
    
    # Tool Execution (for action steps)
    tool_name: Optional[str] = Field(None, description="MCP tool name")
    tool_parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    tool_result: Dict[str, Any] = Field(default_factory=dict, description="Tool execution result")
    
    # Sub-workflow (for workflow_link steps)
    sub_workflow_execution_id: Optional[UUID] = Field(None, description="Sub-workflow execution ID")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator("step_index")
    def validate_step_index_non_negative(cls, v):
        """Validate step index is non-negative"""
        if v < 0:
            raise ValueError("Step index must be non-negative")
        return v
    
    @validator("attempt_number", "max_attempts")
    def validate_attempts_positive(cls, v):
        """Validate attempt numbers are positive"""
        if v <= 0:
            raise ValueError("Attempt numbers must be positive")
        return v
    
    @validator("created_at", "updated_at", pre=True, always=True)
    def set_timestamps(cls, v):
        """Set default timestamps"""
        return v or datetime.now()


# =====================================================
# WORKFLOW TEMPLATE VERSION MODEL
# =====================================================

class WorkflowTemplateVersion(BaseModel):
    """Workflow template version for change tracking"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Version UUID")
    workflow_template_id: UUID = Field(..., description="Template UUID")
    
    # Version Information
    version_number: int = Field(..., description="Incremental version number")
    version_tag: str = Field(..., description="Semantic version tag")
    
    # Content
    template_snapshot: Dict[str, Any] = Field(..., description="Complete template snapshot")
    
    # Change Information
    change_summary: Optional[str] = Field(None, description="Summary of changes")
    change_type: str = Field(default="update", description="Type of change")
    breaking_changes: bool = Field(default=False, description="Whether changes are breaking")
    
    # Audit
    created_by: str = Field(default="system", description="Who made the changes")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    
    @validator("version_number")
    def validate_version_number_positive(cls, v):
        """Validate version number is positive"""
        if v <= 0:
            raise ValueError("Version number must be positive")
        return v
    
    @validator("created_at", pre=True, always=True)
    def set_created_at(cls, v):
        """Set default creation timestamp"""
        return v or datetime.now()


# =====================================================
# REQUEST/RESPONSE MODELS FOR API
# =====================================================

class CreateWorkflowTemplateRequest(BaseModel):
    """Request model for creating workflow templates"""
    name: str
    title: str
    description: str = ""
    category: Optional[str] = None
    tags: List[str] = []
    parameters: Dict[str, Any] = {}
    outputs: Dict[str, Any] = {}
    steps: List[Dict[str, Any]]  # Raw step data, will be validated
    timeout_minutes: int = 60
    max_retries: int = 3
    is_public: bool = False


class UpdateWorkflowTemplateRequest(BaseModel):
    """Request model for updating workflow templates"""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    timeout_minutes: Optional[int] = None
    max_retries: Optional[int] = None
    status: Optional[WorkflowStatus] = None
    is_public: Optional[bool] = None


class ExecuteWorkflowRequest(BaseModel):
    """Request model for executing workflows"""
    workflow_template_id: UUID
    input_parameters: Dict[str, Any] = {}
    trigger_context: Dict[str, Any] = {}
    triggered_by: str = "system"


class WorkflowExecutionResponse(BaseModel):
    """Response model for workflow execution operations"""
    success: bool
    execution: Optional[WorkflowExecution] = None
    message: str
    error: Optional[str] = None


# =====================================================
# UTILITY FUNCTIONS AND HELPERS
# =====================================================

def parse_workflow_step(step_data: Dict[str, Any]) -> WorkflowStep:
    """
    Parse raw step data into appropriate WorkflowStep subclass.

    Args:
        step_data: Raw step data dictionary

    Returns:
        Parsed WorkflowStep instance

    Raises:
        ValueError: If step type is unknown or data is invalid
    """
    step_type = step_data.get("type")

    if step_type == WorkflowStepType.ACTION:
        return ActionStep(**step_data)
    if step_type == WorkflowStepType.CONDITION:
        return ConditionStep(**step_data)
    if step_type == WorkflowStepType.WORKFLOW_LINK:
        return WorkflowLinkStep(**step_data)
    if step_type == WorkflowStepType.PARALLEL:
        # Parse nested steps for parallel execution
        if "steps" in step_data:
            step_data["steps"] = [parse_workflow_step(sub_step) for sub_step in step_data["steps"]]
        return ParallelStep(**step_data)
    if step_type == WorkflowStepType.LOOP:
        # Parse nested steps for loop execution
        if "steps" in step_data:
            step_data["steps"] = [parse_workflow_step(sub_step) for sub_step in step_data["steps"]]
        return LoopStep(**step_data)

    raise ValueError(f"Unknown workflow step type: {step_type}")


def validate_workflow_template_data(template_data: Dict[str, Any]) -> WorkflowTemplate:
    """
    Validate and parse raw workflow template data.

    Args:
        template_data: Raw template data dictionary

    Returns:
        Validated WorkflowTemplate instance

    Raises:
        ValidationError: If template data is invalid
    """
    # Parse steps if they exist
    if "steps" in template_data and isinstance(template_data["steps"], list):
        parsed_steps = []
        for step_data in template_data["steps"]:
            if isinstance(step_data, dict):
                parsed_steps.append(parse_workflow_step(step_data))
            else:
                parsed_steps.append(step_data)  # Already parsed
        template_data["steps"] = parsed_steps

    return WorkflowTemplate(**template_data)


def create_execution_log_entry(
    level: str,
    message: str,
    step_index: Optional[int] = None,
    step_name: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized execution log entry.

    Args:
        level: Log level (info, warning, error, debug)
        message: Log message
        step_index: Optional step index
        step_name: Optional step name
        details: Optional additional details

    Returns:
        Formatted log entry dictionary
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message
    }

    if step_index is not None:
        log_entry["step_index"] = step_index

    if step_name:
        log_entry["step_name"] = step_name

    if details:
        log_entry["details"] = details

    return log_entry


def calculate_workflow_progress(
    current_step_index: int,
    total_steps: int,
    step_executions: Optional[List[WorkflowStepExecution]] = None
) -> float:
    """
    Calculate workflow execution progress percentage.

    Args:
        current_step_index: Current step being executed
        total_steps: Total number of steps in workflow
        step_executions: Optional list of step executions for detailed progress

    Returns:
        Progress percentage (0.0 to 100.0)
    """
    if total_steps <= 0:
        return 0.0

    if step_executions:
        # Calculate based on completed steps
        completed_steps = sum(
            1 for step_exec in step_executions
            if step_exec.status == StepExecutionStatus.COMPLETED
        )
        return min(100.0, (completed_steps / total_steps) * 100.0)

    # Calculate based on current step index
    return min(100.0, (current_step_index / total_steps) * 100.0)


def get_next_step_name(
    current_step: WorkflowStep,
    execution_result: Dict[str, Any],
    step_names: List[str]
) -> Optional[str]:
    """
    Determine the next step name based on current step and execution result.

    Args:
        current_step: Current workflow step
        execution_result: Result of step execution
        step_names: List of all step names in workflow

    Returns:
        Next step name or None if workflow should end
    """
    success = execution_result.get("success", False)

    if isinstance(current_step, ConditionStep):
        # Evaluate condition for conditional steps
        condition_result = execution_result.get("condition_result", False)
        next_step = current_step.on_true if condition_result else current_step.on_false
    else:
        # Use success/failure routing for other steps
        next_step = current_step.on_success if success else current_step.on_failure

    # Handle special step names
    if next_step in ["end", "fail"]:
        return None
    if next_step == "next":
        # Find next step in sequence
        try:
            current_index = step_names.index(current_step.name)
            if current_index + 1 < len(step_names):
                return step_names[current_index + 1]
            return None  # End of workflow
        except ValueError:
            return None
    if next_step in step_names:
        return next_step

    # Invalid step reference
    return None
