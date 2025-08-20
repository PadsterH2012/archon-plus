"""
Pydantic Models for Archon Template Injection System

This module defines Pydantic models that match the existing Archon database structure:
- Template components (using existing archon_template_components table)
- Template definitions (using existing archon_template_definitions table)
- Template assignments (using existing archon_template_assignments table)
- Template expansion results and metadata
- Integration with existing Archon task system
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# =====================================================
# ENUMS - Match existing database enum definitions
# =====================================================

class TemplateComponentType(str, Enum):
    """Template component types (matches existing template_component_type enum)"""
    ACTION = "action"       # Single atomic instruction (e.g., action::git_commit)
    GROUP = "group"         # Related set of instructions (e.g., group::testing_strategy)
    SEQUENCE = "sequence"   # Ordered workflow segment (e.g., sequence::deployment)


class TemplateInjectionLevel(str, Enum):
    """Template injection levels in the hierarchy (matches template_injection_level enum)"""
    PROJECT = "project"      # Applied to all tasks in project
    MILESTONE = "milestone"  # Applied to milestone completion tasks
    PHASE = "phase"         # Applied to development phase tasks
    TASK = "task"           # Applied to individual tasks
    SUBTASK = "subtask"     # Applied to granular operations


class TemplateDefinitionType(str, Enum):
    """Template definition types (matches existing template_type_enum)"""
    PROJECT = "project"     # Project-level templates
    TASK = "task"          # Task-level templates
    COMPONENT = "component" # Component templates


class HierarchyType(str, Enum):
    """Hierarchy types for template assignments (matches existing hierarchy_type_enum)"""
    PROJECT = "project"
    MILESTONE = "milestone"
    PHASE = "phase"
    TASK = "task"
    SUBTASK = "subtask"


# =====================================================
# CORE TEMPLATE MODELS - Match existing database structure
# =====================================================

class TemplateComponent(BaseModel):
    """Template component model (matches archon_template_components table)"""

    # Basic Information
    id: Optional[UUID] = Field(None, description="Component UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Unique component name (e.g., group::understand_homelab_env)")
    description: str = Field(default="", description="Component description")
    component_type: TemplateComponentType = Field(default=TemplateComponentType.GROUP, description="Type of component")

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

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v):
        """Validate component name follows type::name format"""
        import re
        if not re.match(r'^(action|group|sequence)::[a-zA-Z0-9_]+$', v):
            raise ValueError("Component name must follow format: type::name (e.g., group::understand_homelab_env)")
        return v.lower()

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority is one of allowed values"""
        allowed_priorities = ["low", "medium", "high", "critical"]
        if v.lower() not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(allowed_priorities)}")
        return v.lower()


class TemplateDefinition(BaseModel):
    """Template definition model (matches archon_template_definitions table)"""

    # Basic Information
    id: Optional[UUID] = Field(None, description="Template UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Unique template name (e.g., workflow_default)")
    title: str = Field(..., min_length=1, description="Human-readable template title")
    description: str = Field(default="", description="Template description")
    template_type: TemplateDefinitionType = Field(default=TemplateDefinitionType.PROJECT, description="Type of template")

    # Template Content and Configuration
    template_data: Dict[str, Any] = Field(..., description="Template configuration and content as JSONB")
    parent_template_id: Optional[UUID] = Field(None, description="Parent template for inheritance")
    inheritance_level: int = Field(default=0, ge=0, le=3, description="Inheritance level (0-3)")

    # Categorization
    category: str = Field(default="general", description="Template category")
    tags: List[str] = Field(default_factory=list, description="Template tags")

    # Status and Access
    is_public: bool = Field(default=True, description="Whether template is publicly accessible")
    is_active: bool = Field(default=True, description="Whether template is active")

    # Metadata
    created_by: str = Field(..., description="Creator of the template")

    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v):
        """Validate template name follows database constraint (lowercase, alphanumeric, underscores, hyphens only)"""
        import re
        if not re.match(r'^[a-z0-9_-]+$', v):
            raise ValueError("Template name must contain only lowercase letters, numbers, underscores, and hyphens")
        return v





class TemplateAssignment(BaseModel):
    """Template assignment model (matches archon_template_assignments table)"""

    # Basic Information
    id: Optional[UUID] = Field(None, description="Assignment UUID")

    # Polymorphic Reference
    hierarchy_type: HierarchyType = Field(..., description="Type of hierarchy level")
    hierarchy_id: UUID = Field(..., description="UUID of the hierarchy entity")

    # Template Assignment
    template_id: Optional[UUID] = Field(None, description="UUID of the assigned template")

    # Assignment Configuration
    assignment_context: Dict[str, Any] = Field(default_factory=dict, description="Conditions and context for assignment")
    priority: int = Field(default=0, description="Priority for conflict resolution (higher = more priority)")
    conditional_logic: Dict[str, Any] = Field(default_factory=dict, description="Conditions for when this assignment applies")
    injection_level: TemplateInjectionLevel = Field(default=TemplateInjectionLevel.TASK, description="Template injection level")

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
    
    @field_validator("expansion_time_ms")
    @classmethod
    def validate_expansion_time(cls, v):
        """Validate expansion time is reasonable"""
        if v > 10000:  # 10 seconds
            raise ValueError("Expansion time seems unreasonably high (>10 seconds)")
        return v


# =====================================================
# REQUEST/RESPONSE MODELS FOR API
# =====================================================

class CreateTemplateDefinitionRequest(BaseModel):
    """Request model for creating template definitions"""
    name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1)
    description: str = ""
    template_type: TemplateDefinitionType = TemplateDefinitionType.PROJECT
    template_data: Dict[str, Any] = Field(..., description="Template configuration and content")
    parent_template_id: Optional[UUID] = None
    inheritance_level: int = Field(default=0, ge=0, le=3)
    category: str = "general"
    tags: List[str] = []
    is_public: bool = True
    created_by: str = "archon-system"


class UpdateTemplateDefinitionRequest(BaseModel):
    """Request model for updating template definitions"""
    title: Optional[str] = None
    description: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    parent_template_id: Optional[UUID] = None
    inheritance_level: Optional[int] = Field(None, ge=0, le=3)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


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
    hierarchy_type: HierarchyType
    hierarchy_id: UUID
    template_id: UUID
    assignment_context: Dict[str, Any] = {}
    priority: int = 0
    conditional_logic: Dict[str, Any] = {}
    injection_level: TemplateInjectionLevel = TemplateInjectionLevel.TASK
    assigned_by: str = "system"


class TemplateExpansionRequest(BaseModel):
    """Request model for template expansion"""
    original_task: str = Field(..., min_length=1)
    template_name: str = Field(..., min_length=1)
    project_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    context_data: Dict[str, Any] = {}


class TemplateDefinitionResponse(BaseModel):
    """Response model for template definition operations"""
    success: bool
    template: Optional[TemplateDefinition] = None
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
    hierarchy_type: HierarchyType,
    hierarchy_id: UUID,  # noqa: ARG001 - Reserved for future validation
    template_injection_level: TemplateInjectionLevel
) -> bool:
    """
    Validate that template injection level is compatible with hierarchy type

    Args:
        hierarchy_type: Type of hierarchy entity
        hierarchy_id: UUID of hierarchy entity (reserved for future validation)
        template_injection_level: Template's intended injection level

    Returns:
        True if assignment is valid, False otherwise
    """
    # Define valid combinations
    valid_combinations = {
        HierarchyType.PROJECT: [TemplateInjectionLevel.PROJECT, TemplateInjectionLevel.TASK],
        HierarchyType.MILESTONE: [TemplateInjectionLevel.MILESTONE, TemplateInjectionLevel.TASK],
        HierarchyType.PHASE: [TemplateInjectionLevel.PHASE, TemplateInjectionLevel.TASK],
        HierarchyType.TASK: [TemplateInjectionLevel.TASK, TemplateInjectionLevel.SUBTASK],
        HierarchyType.SUBTASK: [TemplateInjectionLevel.SUBTASK]
    }

    return template_injection_level in valid_combinations.get(hierarchy_type, [])
