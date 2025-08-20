"""
Pydantic Models for Archon Template Injection System

This module defines Pydantic models for:
- Workflow templates with placeholder expansion
- Template components for instruction building blocks
- Template assignments for hierarchy-level injection
- Template expansion results and metadata
- Integration with existing Archon task system
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, validator, model_validator


# =====================================================
# ENUMS - Match database enum definitions
# =====================================================

class TemplateInjectionType(str, Enum):
    """Template injection types for different scenarios"""
    WORKFLOW = "workflow"    # Complete workflow templates (e.g., workflow::default)
    SEQUENCE = "sequence"    # Ordered sequence of related actions
    ACTION = "action"        # Single atomic operation


class TemplateInjectionLevel(str, Enum):
    """Template injection levels in the hierarchy"""
    PROJECT = "project"      # Applied to all tasks in project
    MILESTONE = "milestone"  # Applied to milestone completion tasks
    PHASE = "phase"         # Applied to development phase tasks
    TASK = "task"           # Applied to individual tasks
    SUBTASK = "subtask"     # Applied to granular operations


class TemplateComponentType(str, Enum):
    """Template component types for building blocks"""
    ACTION = "action"       # Single atomic instruction (e.g., action::git_commit)
    GROUP = "group"         # Related set of instructions (e.g., group::testing_strategy)
    SEQUENCE = "sequence"   # Ordered workflow segment (e.g., sequence::deployment)


class TemplateHierarchyType(str, Enum):
    """Template hierarchy types for polymorphic references"""
    PROJECT = "project"
    MILESTONE = "milestone"
    PHASE = "phase"
    TASK = "task"
    SUBTASK = "subtask"


# =====================================================
# CORE TEMPLATE MODELS
# =====================================================

class WorkflowTemplate(BaseModel):
    """Workflow template definition with placeholder expansion"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Template UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Unique template name (e.g., workflow::default)")
    description: str = Field(default="", description="Template description")
    template_type: TemplateInjectionType = Field(
        default=TemplateInjectionType.WORKFLOW, description="Type of template"
    )
    injection_level: TemplateInjectionLevel = Field(
        default=TemplateInjectionLevel.TASK, description="Hierarchy level for injection"
    )
    
    # Template Content
    template_content: str = Field(..., min_length=1, description="Template with {{placeholder}} variables")
    user_task_position: int = Field(default=6, ge=1, description="Position where {{USER_TASK}} appears")
    
    # Metadata and Configuration
    estimated_duration: int = Field(default=30, ge=1, description="Total estimated duration in minutes")
    required_tools: List[str] = Field(default_factory=list, description="MCP tools needed for this template")
    applicable_phases: List[str] = Field(
        default_factory=lambda: ["development", "testing", "deployment"],
        description="Project phases where this template applies"
    )
    
    # Status and Versioning
    is_active: bool = Field(default=True, description="Whether template is active")
    version: str = Field(default="1.0.0", description="Semantic version")
    author: str = Field(default="archon-system", description="Template author")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator("name")
    def validate_name_format(cls, v):
        """Validate template name follows type::name format"""
        if not v.startswith(("workflow::", "sequence::", "action::")):
            raise ValueError("Template name must start with workflow::, sequence::, or action::")
        
        # Check for valid characters after prefix
        suffix = v.split("::", 1)[1] if "::" in v else ""
        if not suffix.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Template name suffix must contain only alphanumeric characters, underscores, and hyphens")
        
        return v.lower()
    
    @validator("template_content")
    def validate_template_content(cls, v):
        """Validate template content has required placeholders"""
        if "{{USER_TASK}}" not in v:
            raise ValueError("Template content must contain {{USER_TASK}} placeholder")
        
        # Check for valid placeholder format
        import re
        placeholders = re.findall(r'\{\{([^}]+)\}\}', v)
        for placeholder in placeholders:
            if not re.match(r'^[a-zA-Z0-9_:]+$', placeholder):
                raise ValueError(f"Invalid placeholder format: {{{{{placeholder}}}}}. Must contain only alphanumeric characters, underscores, and colons")
        
        return v
    
    @validator("version")
    def validate_version_format(cls, v):
        """Validate semantic version format"""
        import re
        if not re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$', v):
            raise ValueError("Version must follow semantic versioning (e.g., '1.0.0' or '1.0.0-beta')")
        return v


class TemplateComponent(BaseModel):
    """Template component for instruction building blocks"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Component UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Unique component name (e.g., group::understand_homelab_env)")
    description: str = Field(default="", description="Component description")
    component_type: TemplateComponentType = Field(
        default=TemplateComponentType.GROUP, description="Type of component"
    )
    
    # Component Content
    instruction_text: str = Field(..., min_length=1, description="Full expanded instruction text")
    
    # Requirements and Metadata
    required_tools: List[str] = Field(default_factory=list, description="MCP tools needed (e.g., ['homelab-vault', 'view'])")
    estimated_duration: int = Field(default=5, ge=1, description="Estimated duration in minutes")
    input_requirements: Dict[str, Any] = Field(default_factory=dict, description="What context/data this component needs")
    output_expectations: Dict[str, Any] = Field(default_factory=dict, description="What this component should produce")
    validation_criteria: List[str] = Field(default_factory=list, description="How to verify successful completion")
    
    # Categorization and Metadata
    category: str = Field(default="general", max_length=100, description="Component category (e.g., 'documentation', 'testing')")
    priority: str = Field(default="medium", description="Priority level (low, medium, high, critical)")
    tags: List[str] = Field(default_factory=list, description="Flexible tagging for search and organization")
    
    # Status
    is_active: bool = Field(default=True, description="Whether component is active")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator("name")
    def validate_name_format(cls, v):
        """Validate component name follows type::name format"""
        import re
        if not re.match(r'^(action|group|sequence)::[a-zA-Z0-9_]+$', v):
            raise ValueError("Component name must follow format: type::name (e.g., group::understand_homelab_env)")
        return v.lower()
    
    @validator("priority")
    def validate_priority(cls, v):
        """Validate priority is one of allowed values"""
        allowed_priorities = ["low", "medium", "high", "critical"]
        if v.lower() not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(allowed_priorities)}")
        return v.lower()


class TemplateAssignment(BaseModel):
    """Template assignment for hierarchy-level injection"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Assignment UUID")
    
    # Polymorphic Reference
    hierarchy_type: TemplateHierarchyType = Field(..., description="Type of hierarchy level")
    hierarchy_id: UUID = Field(..., description="UUID of the hierarchy entity")
    
    # Template Assignment
    template_id: UUID = Field(..., description="UUID of the assigned template")
    
    # Assignment Configuration
    assignment_context: Dict[str, Any] = Field(default_factory=dict, description="Conditions and context for assignment")
    priority: int = Field(default=0, description="Priority for conflict resolution (higher = more priority)")
    conditional_logic: Dict[str, Any] = Field(default_factory=dict, description="Conditions for when this assignment applies")
    
    # Status and Metadata
    is_active: bool = Field(default=True, description="Whether assignment is active")
    assigned_at: Optional[datetime] = Field(None, description="When assignment was created")
    assigned_by: str = Field(default="system", description="User or system that made the assignment")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class TemplateExpansionResult(BaseModel):
    """Result of template expansion operation"""
    
    # Original Data
    original_task: str = Field(..., description="Original user task description")
    template_name: str = Field(..., description="Name of template used for expansion")
    
    # Expansion Results
    expanded_instructions: str = Field(..., description="Fully expanded instruction set")
    template_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about template expansion")
    
    # Performance Metrics
    expansion_time_ms: int = Field(..., ge=0, description="Time taken for expansion in milliseconds")
    component_count: int = Field(default=0, ge=0, description="Number of components expanded")
    
    # Validation Results
    validation_passed: bool = Field(default=True, description="Whether expansion validation passed")
    validation_warnings: List[str] = Field(default_factory=list, description="Any validation warnings")
    
    # Context
    project_id: Optional[UUID] = Field(None, description="Project context for expansion")
    task_id: Optional[UUID] = Field(None, description="Task context for expansion")
    
    # Timestamp
    expanded_at: datetime = Field(default_factory=datetime.now, description="When expansion was performed")
    
    @validator("expansion_time_ms")
    def validate_expansion_time(cls, v):
        """Validate expansion time is reasonable"""
        if v > 10000:  # 10 seconds
            raise ValueError("Expansion time seems unreasonably high (>10 seconds)")
        return v


# =====================================================
# REQUEST/RESPONSE MODELS FOR API
# =====================================================

class CreateWorkflowTemplateRequest(BaseModel):
    """Request model for creating workflow templates"""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    template_type: TemplateInjectionType = TemplateInjectionType.WORKFLOW
    injection_level: TemplateInjectionLevel = TemplateInjectionLevel.TASK
    template_content: str = Field(..., min_length=1)
    user_task_position: int = Field(default=6, ge=1)
    estimated_duration: int = Field(default=30, ge=1)
    required_tools: List[str] = []
    applicable_phases: List[str] = ["development", "testing", "deployment"]
    version: str = "1.0.0"
    author: str = "archon-system"


class UpdateWorkflowTemplateRequest(BaseModel):
    """Request model for updating workflow templates"""
    description: Optional[str] = None
    template_content: Optional[str] = None
    user_task_position: Optional[int] = Field(None, ge=1)
    estimated_duration: Optional[int] = Field(None, ge=1)
    required_tools: Optional[List[str]] = None
    applicable_phases: Optional[List[str]] = None
    is_active: Optional[bool] = None
    version: Optional[str] = None


class CreateTemplateComponentRequest(BaseModel):
    """Request model for creating template components"""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    component_type: TemplateComponentType = TemplateComponentType.GROUP
    instruction_text: str = Field(..., min_length=1)
    required_tools: List[str] = []
    estimated_duration: int = Field(default=5, ge=1)
    input_requirements: Dict[str, Any] = {}
    output_expectations: Dict[str, Any] = {}
    validation_criteria: List[str] = []
    category: str = "general"
    priority: str = "medium"
    tags: List[str] = []


class UpdateTemplateComponentRequest(BaseModel):
    """Request model for updating template components"""
    description: Optional[str] = None
    instruction_text: Optional[str] = None
    required_tools: Optional[List[str]] = None
    estimated_duration: Optional[int] = Field(None, ge=1)
    input_requirements: Optional[Dict[str, Any]] = None
    output_expectations: Optional[Dict[str, Any]] = None
    validation_criteria: Optional[List[str]] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class CreateTemplateAssignmentRequest(BaseModel):
    """Request model for creating template assignments"""
    hierarchy_type: TemplateHierarchyType
    hierarchy_id: UUID
    template_id: UUID
    assignment_context: Dict[str, Any] = {}
    priority: int = 0
    conditional_logic: Dict[str, Any] = {}
    assigned_by: str = "system"


class TemplateExpansionRequest(BaseModel):
    """Request model for template expansion"""
    original_task: str = Field(..., min_length=1)
    template_name: str = Field(..., min_length=1)
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    context_data: Dict[str, Any] = {}


class WorkflowTemplateResponse(BaseModel):
    """Response model for workflow template operations"""
    success: bool
    template: Optional[WorkflowTemplate] = None
    message: str
    error: Optional[str] = None


class TemplateComponentResponse(BaseModel):
    """Response model for template component operations"""
    success: bool
    component: Optional[TemplateComponent] = None
    message: str
    error: Optional[str] = None


class TemplateAssignmentResponse(BaseModel):
    """Response model for template assignment operations"""
    success: bool
    assignment: Optional[TemplateAssignment] = None
    message: str
    error: Optional[str] = None


class TemplateExpansionResponse(BaseModel):
    """Response model for template expansion operations"""
    success: bool
    result: Optional[TemplateExpansionResult] = None
    message: str
    error: Optional[str] = None


# =====================================================
# UTILITY FUNCTIONS AND HELPERS
# =====================================================

def validate_template_placeholders(template_content: str, available_components: List[str]) -> List[str]:
    """
    Validate that all placeholders in template content reference existing components

    Args:
        template_content: Template content with {{placeholder}} variables
        available_components: List of available component names

    Returns:
        List of validation errors (empty if valid)
    """
    import re

    errors = []
    placeholders = re.findall(r'\{\{([^}]+)\}\}', template_content)

    for placeholder in placeholders:
        if placeholder == "USER_TASK":
            continue  # USER_TASK is a special placeholder

        if placeholder not in available_components:
            errors.append(f"Template references unknown component: {{{{{placeholder}}}}}")

    return errors


def extract_template_placeholders(template_content: str) -> List[str]:
    """
    Extract all placeholders from template content

    Args:
        template_content: Template content with {{placeholder}} variables

    Returns:
        List of placeholder names (without braces)
    """
    import re
    return re.findall(r'\{\{([^}]+)\}\}', template_content)


def calculate_template_duration(template_content: str, component_durations: Dict[str, int]) -> int:
    """
    Calculate total estimated duration for a template based on component durations

    Args:
        template_content: Template content with {{placeholder}} variables
        component_durations: Mapping of component names to duration in minutes

    Returns:
        Total estimated duration in minutes
    """
    placeholders = extract_template_placeholders(template_content)
    total_duration = 0

    for placeholder in placeholders:
        if placeholder == "USER_TASK":
            continue  # USER_TASK duration is variable

        duration = component_durations.get(placeholder, 5)  # Default 5 minutes
        total_duration += duration

    return total_duration


def validate_template_hierarchy_assignment(
    hierarchy_type: TemplateHierarchyType,
    hierarchy_id: UUID,
    template_injection_level: TemplateInjectionLevel
) -> bool:
    """
    Validate that template injection level is compatible with hierarchy type

    Args:
        hierarchy_type: Type of hierarchy entity
        hierarchy_id: UUID of hierarchy entity
        template_injection_level: Template's intended injection level

    Returns:
        True if assignment is valid, False otherwise
    """
    # Define valid combinations
    valid_combinations = {
        TemplateHierarchyType.PROJECT: [TemplateInjectionLevel.PROJECT, TemplateInjectionLevel.TASK],
        TemplateHierarchyType.MILESTONE: [TemplateInjectionLevel.MILESTONE, TemplateInjectionLevel.TASK],
        TemplateHierarchyType.PHASE: [TemplateInjectionLevel.PHASE, TemplateInjectionLevel.TASK],
        TemplateHierarchyType.TASK: [TemplateInjectionLevel.TASK, TemplateInjectionLevel.SUBTASK],
        TemplateHierarchyType.SUBTASK: [TemplateInjectionLevel.SUBTASK]
    }

    return template_injection_level in valid_combinations.get(hierarchy_type, [])
