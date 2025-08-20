"""
Pydantic Models for Archon Template System

This module defines Pydantic models for:
- Template definitions and inheritance
- Template application and customization
- Template validation and serialization
- Integration with component and workflow systems
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator, model_validator


# =====================================================
# ENUMS - Match database enum definitions
# =====================================================

class TemplateType(str, Enum):
    """Types of templates in the system"""
    GLOBAL_DEFAULT = "global_default"
    INDUSTRY = "industry"
    TEAM = "team"
    PERSONAL = "personal"
    COMMUNITY = "community"


class TemplateStatus(str, Enum):
    """Template lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


# =====================================================
# TEMPLATE MODELS
# =====================================================

class TemplateDefinition(BaseModel):
    """Template definition with inheritance and workflow assignments"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Template UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Unique template name")
    title: str = Field(..., min_length=1, max_length=500, description="Human-readable template title")
    description: str = Field(default="", description="Template description")
    
    # Classification
    template_type: TemplateType = Field(default=TemplateType.PERSONAL, description="Type of template")
    status: TemplateStatus = Field(default=TemplateStatus.DRAFT, description="Template lifecycle status")
    
    # Inheritance
    parent_template_id: Optional[UUID] = Field(None, description="Parent template for inheritance")
    inheritance_rules: Dict[str, Any] = Field(default_factory=dict, description="Rules for inheriting from parent")
    
    # Template Content
    workflow_assignments: Dict[str, Any] = Field(default_factory=dict, description="Workflow assignments for components")
    component_templates: Dict[str, Any] = Field(default_factory=dict, description="Component template definitions")
    
    # Configuration
    is_active: bool = Field(default=True, description="Whether template is active")
    is_public: bool = Field(default=False, description="Whether template is publicly available")
    
    # Metadata
    created_by: str = Field(default="system", description="Creator identifier")
    usage_count: int = Field(default=0, description="Number of times template has been used")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator("name")
    def validate_name_format(cls, v):
        """Validate template name format"""
        if not v.strip():
            raise ValueError("Template name cannot be empty")
        
        # Allow alphanumeric, underscores, hyphens, and spaces
        cleaned = v.replace("_", "").replace("-", "").replace(" ", "")
        if not cleaned.isalnum():
            raise ValueError("Template name must contain only alphanumeric characters, underscores, hyphens, and spaces")
        return v.strip()
    
    @validator("title")
    def validate_title_not_empty(cls, v):
        """Validate title is not empty"""
        if not v.strip():
            raise ValueError("Template title cannot be empty")
        return v.strip()
    
    @validator("usage_count")
    def validate_usage_count_non_negative(cls, v):
        """Validate usage count is non-negative"""
        if v < 0:
            raise ValueError("Usage count must be non-negative")
        return v
    
    @validator("workflow_assignments")
    def validate_workflow_assignments(cls, v):
        """Validate workflow assignments structure"""
        if not isinstance(v, dict):
            raise ValueError("Workflow assignments must be a dictionary")
        
        # Validate structure: component_type -> workflow_name
        for component_type, workflow_data in v.items():
            if not isinstance(component_type, str):
                raise ValueError("Component type keys must be strings")
            
            if isinstance(workflow_data, str):
                # Simple workflow name assignment
                continue
            elif isinstance(workflow_data, dict):
                # Complex workflow assignment with parameters
                if "workflow_name" not in workflow_data:
                    raise ValueError(f"Workflow assignment for '{component_type}' must include 'workflow_name'")
            else:
                raise ValueError(f"Invalid workflow assignment format for '{component_type}'")
        
        return v
    
    @validator("component_templates")
    def validate_component_templates(cls, v):
        """Validate component templates structure"""
        if not isinstance(v, dict):
            raise ValueError("Component templates must be a dictionary")
        
        # Validate structure: component_type -> template_config
        for component_type, template_config in v.items():
            if not isinstance(component_type, str):
                raise ValueError("Component type keys must be strings")
            
            if not isinstance(template_config, dict):
                raise ValueError(f"Template config for '{component_type}' must be a dictionary")
            
            # Validate required fields in template config
            if "gates" in template_config and not isinstance(template_config["gates"], list):
                raise ValueError(f"Gates for '{component_type}' must be a list")
        
        return v
    
    @model_validator(mode='before')
    @classmethod
    def validate_no_self_inheritance(cls, values):
        """Validate template doesn't inherit from itself"""
        template_id = values.get('id')
        parent_id = values.get('parent_template_id')
        
        if template_id and parent_id and template_id == parent_id:
            raise ValueError("Template cannot inherit from itself")
        
        return values
    
    @validator("created_at", "updated_at", pre=True, always=True)
    def set_timestamps(cls, v):
        """Set default timestamps"""
        return v or datetime.now()


class TemplateApplication(BaseModel):
    """Record of template application to a project"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Application UUID")
    project_id: UUID = Field(..., description="Project where template was applied")
    template_id: UUID = Field(..., description="Template that was applied")
    
    # Application Details
    applied_at: Optional[datetime] = Field(None, description="When template was applied")
    applied_by: str = Field(default="system", description="Who applied the template")
    customizations: Dict[str, Any] = Field(default_factory=dict, description="Customizations made during application")
    
    @validator("applied_at", pre=True, always=True)
    def set_applied_at(cls, v):
        """Set default application timestamp"""
        return v or datetime.now()


# =====================================================
# REQUEST/RESPONSE MODELS FOR API
# =====================================================

class CreateTemplateDefinitionRequest(BaseModel):
    """Request model for creating template definitions"""
    name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    template_type: TemplateType = TemplateType.PERSONAL
    parent_template_id: Optional[UUID] = None
    workflow_assignments: Dict[str, Any] = {}
    component_templates: Dict[str, Any] = {}
    inheritance_rules: Dict[str, Any] = {}
    is_public: bool = False


class UpdateTemplateDefinitionRequest(BaseModel):
    """Request model for updating template definitions"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    template_type: Optional[TemplateType] = None
    status: Optional[TemplateStatus] = None
    parent_template_id: Optional[UUID] = None
    workflow_assignments: Optional[Dict[str, Any]] = None
    component_templates: Optional[Dict[str, Any]] = None
    inheritance_rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class ApplyTemplateRequest(BaseModel):
    """Request model for applying templates to projects"""
    project_id: UUID
    template_id: UUID
    customizations: Dict[str, Any] = {}
    applied_by: str = "system"


class TemplateDefinitionResponse(BaseModel):
    """Response model for template definition operations"""
    success: bool
    template: Optional[TemplateDefinition] = None
    message: str
    error: Optional[str] = None


class TemplateApplicationResponse(BaseModel):
    """Response model for template application operations"""
    success: bool
    application: Optional[TemplateApplication] = None
    message: str
    error: Optional[str] = None


# =====================================================
# UTILITY FUNCTIONS AND HELPERS
# =====================================================

def validate_template_inheritance_chain(templates: List[TemplateDefinition]) -> List[str]:
    """
    Validate template inheritance chain for circular dependencies.
    
    Args:
        templates: List of templates to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    template_map = {tmpl.id: tmpl for tmpl in templates if tmpl.id}
    
    def has_circular_inheritance(template_id: UUID, visited: set, path: set) -> bool:
        """Check for circular inheritance using DFS"""
        if template_id in path:
            return True
        if template_id in visited:
            return False
            
        visited.add(template_id)
        path.add(template_id)
        
        template = template_map.get(template_id)
        if template and template.parent_template_id:
            if has_circular_inheritance(template.parent_template_id, visited, path):
                return True
        
        path.remove(template_id)
        return False
    
    visited = set()
    for template in templates:
        if template.id and template.id not in visited:
            if has_circular_inheritance(template.id, visited, set()):
                errors.append(f"Circular inheritance detected involving template '{template.name}'")
    
    return errors


def resolve_template_inheritance(template: TemplateDefinition, template_map: Dict[UUID, TemplateDefinition]) -> Dict[str, Any]:
    """
    Resolve template inheritance to get final configuration.
    
    Args:
        template: Template to resolve
        template_map: Map of all available templates
        
    Returns:
        Resolved template configuration
    """
    resolved_config = {
        "workflow_assignments": {},
        "component_templates": {},
        "inheritance_rules": {}
    }
    
    # Collect inheritance chain
    inheritance_chain = []
    current = template
    visited = set()
    
    while current and current.id not in visited:
        inheritance_chain.append(current)
        visited.add(current.id)
        
        if current.parent_template_id:
            current = template_map.get(current.parent_template_id)
        else:
            break
    
    # Apply inheritance from root to leaf
    for tmpl in reversed(inheritance_chain):
        # Merge workflow assignments
        resolved_config["workflow_assignments"].update(tmpl.workflow_assignments)
        
        # Merge component templates
        for comp_type, comp_config in tmpl.component_templates.items():
            if comp_type not in resolved_config["component_templates"]:
                resolved_config["component_templates"][comp_type] = {}
            resolved_config["component_templates"][comp_type].update(comp_config)
        
        # Apply inheritance rules
        resolved_config["inheritance_rules"].update(tmpl.inheritance_rules)
    
    return resolved_config
