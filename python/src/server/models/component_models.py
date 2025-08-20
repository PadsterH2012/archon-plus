"""
Pydantic Models for Archon Component System

This module defines Pydantic models for:
- Component hierarchy and dependency management
- Component validation and serialization
- Integration with Archon project system
- Component lifecycle and status tracking
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator, model_validator


# =====================================================
# ENUMS - Match database enum definitions
# =====================================================

class ComponentType(str, Enum):
    """Types of components in the system"""
    FOUNDATION = "foundation"
    FEATURE = "feature"
    INTEGRATION = "integration"
    INFRASTRUCTURE = "infrastructure"
    TESTING = "testing"


class ComponentStatus(str, Enum):
    """Component lifecycle status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    GATES_PASSED = "gates_passed"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class DependencyType(str, Enum):
    """Types of component dependencies"""
    HARD = "hard"        # Must be completed before this component can start
    SOFT = "soft"        # Should be completed but not strictly required
    OPTIONAL = "optional"  # Nice to have but not required


# =====================================================
# COMPONENT MODELS
# =====================================================

class Component(BaseModel):
    """Component definition with dependencies and gates"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Component UUID")
    project_id: UUID = Field(..., description="Parent project UUID")
    name: str = Field(..., min_length=1, max_length=255, description="Unique component name within project")
    description: str = Field(default="", description="Component description")
    
    # Classification
    component_type: ComponentType = Field(default=ComponentType.FEATURE, description="Type of component")
    status: ComponentStatus = Field(default=ComponentStatus.NOT_STARTED, description="Current component status")
    
    # Dependencies and Gates
    dependencies: List[UUID] = Field(default_factory=list, description="List of component UUIDs this depends on")
    completion_gates: List[str] = Field(default_factory=list, description="Gates that must be passed for completion")
    
    # Context and Ordering
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Additional component context")
    order_index: int = Field(default=0, description="Display order within project")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator("name")
    def validate_name_format(cls, v):
        """Validate component name format"""
        if not v.strip():
            raise ValueError("Component name cannot be empty")
        
        # Allow alphanumeric, underscores, hyphens, and spaces
        cleaned = v.replace("_", "").replace("-", "").replace(" ", "")
        if not cleaned.isalnum():
            raise ValueError("Component name must contain only alphanumeric characters, underscores, hyphens, and spaces")
        return v.strip()
    
    @validator("completion_gates")
    def validate_completion_gates(cls, v):
        """Validate completion gates format"""
        valid_gates = {
            "architecture", "design", "implementation", "testing", 
            "integration", "documentation", "review", "deployment"
        }
        
        for gate in v:
            if not isinstance(gate, str) or not gate.strip():
                raise ValueError("Completion gates must be non-empty strings")
            if gate.lower() not in valid_gates:
                raise ValueError(f"Invalid completion gate '{gate}'. Valid gates: {', '.join(sorted(valid_gates))}")
        
        return v
    
    @validator("order_index")
    def validate_order_index(cls, v):
        """Validate order index is non-negative"""
        if v < 0:
            raise ValueError("Order index must be non-negative")
        return v
    
    @validator("created_at", "updated_at", pre=True, always=True)
    def set_timestamps(cls, v):
        """Set default timestamps"""
        return v or datetime.now()


class ComponentDependency(BaseModel):
    """Explicit component dependency relationship"""
    
    # Basic Information
    id: Optional[UUID] = Field(None, description="Dependency relationship UUID")
    component_id: UUID = Field(..., description="Component that has the dependency")
    depends_on_component_id: UUID = Field(..., description="Component that is depended upon")
    
    # Dependency Configuration
    dependency_type: DependencyType = Field(default=DependencyType.HARD, description="Type of dependency")
    gate_requirements: List[str] = Field(default_factory=list, description="Specific gates required from dependency")
    
    # Timestamps
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    
    @validator("gate_requirements")
    def validate_gate_requirements(cls, v):
        """Validate gate requirements format"""
        valid_gates = {
            "architecture", "design", "implementation", "testing", 
            "integration", "documentation", "review", "deployment"
        }
        
        for gate in v:
            if not isinstance(gate, str) or not gate.strip():
                raise ValueError("Gate requirements must be non-empty strings")
            if gate.lower() not in valid_gates:
                raise ValueError(f"Invalid gate requirement '{gate}'. Valid gates: {', '.join(sorted(valid_gates))}")
        
        return v
    
    @model_validator(mode='before')
    @classmethod
    def validate_no_self_dependency(cls, values):
        """Validate component doesn't depend on itself"""
        component_id = values.get('component_id')
        depends_on_id = values.get('depends_on_component_id')
        
        if component_id and depends_on_id and component_id == depends_on_id:
            raise ValueError("Component cannot depend on itself")
        
        return values
    
    @validator("created_at", pre=True, always=True)
    def set_created_at(cls, v):
        """Set default creation timestamp"""
        return v or datetime.now()


# =====================================================
# REQUEST/RESPONSE MODELS FOR API
# =====================================================

class CreateComponentRequest(BaseModel):
    """Request model for creating components"""
    project_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    component_type: ComponentType = ComponentType.FEATURE
    dependencies: List[UUID] = []
    completion_gates: List[str] = []
    context_data: Dict[str, Any] = {}
    order_index: int = 0


class UpdateComponentRequest(BaseModel):
    """Request model for updating components"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    component_type: Optional[ComponentType] = None
    status: Optional[ComponentStatus] = None
    dependencies: Optional[List[UUID]] = None
    completion_gates: Optional[List[str]] = None
    context_data: Optional[Dict[str, Any]] = None
    order_index: Optional[int] = None


class CreateComponentDependencyRequest(BaseModel):
    """Request model for creating component dependencies"""
    component_id: UUID
    depends_on_component_id: UUID
    dependency_type: DependencyType = DependencyType.HARD
    gate_requirements: List[str] = []


class ComponentResponse(BaseModel):
    """Response model for component operations"""
    success: bool
    component: Optional[Component] = None
    message: str
    error: Optional[str] = None


class ComponentDependencyResponse(BaseModel):
    """Response model for component dependency operations"""
    success: bool
    dependency: Optional[ComponentDependency] = None
    message: str
    error: Optional[str] = None


# =====================================================
# UTILITY FUNCTIONS AND HELPERS
# =====================================================

def validate_component_hierarchy(components: List[Component]) -> List[str]:
    """
    Validate component hierarchy for circular dependencies.
    
    Args:
        components: List of components to validate
        
    Returns:
        List of validation error messages
    """
    errors = []
    component_map = {comp.id: comp for comp in components if comp.id}
    
    def has_circular_dependency(component_id: UUID, visited: set, path: set) -> bool:
        """Check for circular dependencies using DFS"""
        if component_id in path:
            return True
        if component_id in visited:
            return False
            
        visited.add(component_id)
        path.add(component_id)
        
        component = component_map.get(component_id)
        if component:
            for dep_id in component.dependencies:
                if has_circular_dependency(dep_id, visited, path):
                    return True
        
        path.remove(component_id)
        return False
    
    visited = set()
    for component in components:
        if component.id and component.id not in visited:
            if has_circular_dependency(component.id, visited, set()):
                errors.append(f"Circular dependency detected involving component '{component.name}'")
    
    return errors


def get_component_execution_order(components: List[Component]) -> List[Component]:
    """
    Get components in dependency-resolved execution order.
    
    Args:
        components: List of components to order
        
    Returns:
        Components ordered by dependencies (topological sort)
    """
    component_map = {comp.id: comp for comp in components if comp.id}
    in_degree = {comp.id: 0 for comp in components if comp.id}
    
    # Calculate in-degrees
    for component in components:
        if component.id:
            for dep_id in component.dependencies:
                if dep_id in in_degree:
                    in_degree[component.id] += 1
    
    # Topological sort
    queue = [comp_id for comp_id, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        current_id = queue.pop(0)
        current_component = component_map[current_id]
        result.append(current_component)
        
        # Update in-degrees for dependent components
        for component in components:
            if component.id and current_id in component.dependencies:
                in_degree[component.id] -= 1
                if in_degree[component.id] == 0:
                    queue.append(component.id)
    
    return result
