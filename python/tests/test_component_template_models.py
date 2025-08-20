"""
Tests for Component and Template Pydantic Models

This module tests:
- Component model validation and serialization
- Template model validation and inheritance
- Dependency validation and circular dependency detection
- Model integration with existing workflow patterns
"""

import pytest
from datetime import datetime
from uuid import uuid4, UUID
from pydantic import ValidationError

from src.server.models.component_models import (
    Component, ComponentDependency, ComponentType, ComponentStatus, DependencyType,
    CreateComponentRequest, UpdateComponentRequest, CreateComponentDependencyRequest,
    validate_component_hierarchy, get_component_execution_order
)

from src.server.models.template_models import (
    TemplateDefinition, TemplateApplication, TemplateType, TemplateStatus,
    CreateTemplateDefinitionRequest, UpdateTemplateDefinitionRequest, ApplyTemplateRequest,
    validate_template_inheritance_chain, resolve_template_inheritance
)


class TestComponentModels:
    """Test component model validation and functionality"""

    def test_component_creation_valid(self):
        """Test valid component creation"""
        project_id = uuid4()
        
        component = Component(
            project_id=project_id,
            name="test_component",
            description="A test component",
            component_type=ComponentType.FEATURE,
            completion_gates=["design", "implementation", "testing"]
        )
        
        assert component.project_id == project_id
        assert component.name == "test_component"
        assert component.component_type == ComponentType.FEATURE
        assert component.status == ComponentStatus.NOT_STARTED  # default
        assert len(component.completion_gates) == 3
        assert component.order_index == 0  # default
        assert isinstance(component.created_at, datetime)

    def test_component_name_validation(self):
        """Test component name validation"""
        project_id = uuid4()
        
        # Valid names
        valid_names = ["test_component", "test-component", "test component", "TestComponent123"]
        for name in valid_names:
            component = Component(project_id=project_id, name=name)
            assert component.name == name.strip()
        
        # Invalid names
        with pytest.raises(ValidationError):
            Component(project_id=project_id, name="")
        
        with pytest.raises(ValidationError):
            Component(project_id=project_id, name="   ")
        
        with pytest.raises(ValidationError):
            Component(project_id=project_id, name="test@component")

    def test_completion_gates_validation(self):
        """Test completion gates validation"""
        project_id = uuid4()
        
        # Valid gates
        valid_gates = ["architecture", "design", "implementation", "testing"]
        component = Component(
            project_id=project_id,
            name="test",
            completion_gates=valid_gates
        )
        assert component.completion_gates == valid_gates
        
        # Invalid gates
        with pytest.raises(ValidationError):
            Component(
                project_id=project_id,
                name="test",
                completion_gates=["invalid_gate"]
            )
        
        with pytest.raises(ValidationError):
            Component(
                project_id=project_id,
                name="test",
                completion_gates=[""]
            )

    def test_component_dependency_creation(self):
        """Test component dependency creation"""
        comp1_id = uuid4()
        comp2_id = uuid4()
        
        dependency = ComponentDependency(
            component_id=comp1_id,
            depends_on_component_id=comp2_id,
            dependency_type=DependencyType.HARD,
            gate_requirements=["design", "implementation"]
        )
        
        assert dependency.component_id == comp1_id
        assert dependency.depends_on_component_id == comp2_id
        assert dependency.dependency_type == DependencyType.HARD
        assert len(dependency.gate_requirements) == 2

    def test_component_dependency_self_validation(self):
        """Test component dependency self-reference validation"""
        comp_id = uuid4()
        
        with pytest.raises(ValidationError):
            ComponentDependency(
                component_id=comp_id,
                depends_on_component_id=comp_id
            )

    def test_circular_dependency_detection(self):
        """Test circular dependency detection"""
        project_id = uuid4()
        comp1_id = uuid4()
        comp2_id = uuid4()
        comp3_id = uuid4()
        
        # Create components with circular dependency: 1 -> 2 -> 3 -> 1
        components = [
            Component(id=comp1_id, project_id=project_id, name="comp1", dependencies=[comp2_id]),
            Component(id=comp2_id, project_id=project_id, name="comp2", dependencies=[comp3_id]),
            Component(id=comp3_id, project_id=project_id, name="comp3", dependencies=[comp1_id])
        ]
        
        errors = validate_component_hierarchy(components)
        assert len(errors) > 0
        assert "circular dependency" in errors[0].lower()

    def test_component_execution_order(self):
        """Test component execution order calculation"""
        project_id = uuid4()
        comp1_id = uuid4()
        comp2_id = uuid4()
        comp3_id = uuid4()
        
        # Create components: comp1 depends on comp2, comp2 depends on comp3
        components = [
            Component(id=comp1_id, project_id=project_id, name="comp1", dependencies=[comp2_id]),
            Component(id=comp2_id, project_id=project_id, name="comp2", dependencies=[comp3_id]),
            Component(id=comp3_id, project_id=project_id, name="comp3", dependencies=[])
        ]
        
        ordered = get_component_execution_order(components)
        
        # Should be ordered: comp3, comp2, comp1
        assert len(ordered) == 3
        assert ordered[0].name == "comp3"
        assert ordered[1].name == "comp2"
        assert ordered[2].name == "comp1"


class TestTemplateModels:
    """Test template model validation and functionality"""

    def test_template_definition_creation(self):
        """Test valid template definition creation"""
        template = TemplateDefinition(
            name="test_template",
            title="Test Template",
            description="A test template",
            template_type=TemplateType.PERSONAL,
            workflow_assignments={
                "feature": "feature_workflow",
                "integration": {
                    "workflow_name": "integration_workflow",
                    "parameters": {"timeout": 300}
                }
            },
            component_templates={
                "feature": {
                    "gates": ["design", "implementation"],
                    "default_status": "not_started"
                }
            }
        )
        
        assert template.name == "test_template"
        assert template.title == "Test Template"
        assert template.template_type == TemplateType.PERSONAL
        assert template.status == TemplateStatus.DRAFT  # default
        assert template.is_active is True  # default
        assert template.usage_count == 0  # default

    def test_template_name_validation(self):
        """Test template name validation"""
        # Valid names
        valid_names = ["test_template", "test-template", "test template", "TestTemplate123"]
        for name in valid_names:
            template = TemplateDefinition(name=name, title="Test")
            assert template.name == name.strip()
        
        # Invalid names
        with pytest.raises(ValidationError):
            TemplateDefinition(name="", title="Test")
        
        with pytest.raises(ValidationError):
            TemplateDefinition(name="   ", title="Test")

    def test_workflow_assignments_validation(self):
        """Test workflow assignments validation"""
        # Valid assignments
        valid_assignments = {
            "feature": "feature_workflow",
            "integration": {
                "workflow_name": "integration_workflow",
                "parameters": {"timeout": 300}
            }
        }
        
        template = TemplateDefinition(
            name="test",
            title="Test",
            workflow_assignments=valid_assignments
        )
        assert template.workflow_assignments == valid_assignments
        
        # Invalid assignments - missing workflow_name
        with pytest.raises(ValidationError):
            TemplateDefinition(
                name="test",
                title="Test",
                workflow_assignments={
                    "feature": {"parameters": {"timeout": 300}}
                }
            )

    def test_template_inheritance_validation(self):
        """Test template inheritance validation"""
        template_id = uuid4()
        
        # Self-inheritance should fail
        with pytest.raises(ValidationError):
            TemplateDefinition(
                id=template_id,
                name="test",
                title="Test",
                parent_template_id=template_id
            )

    def test_circular_inheritance_detection(self):
        """Test circular inheritance detection"""
        tmpl1_id = uuid4()
        tmpl2_id = uuid4()
        tmpl3_id = uuid4()
        
        # Create templates with circular inheritance: 1 -> 2 -> 3 -> 1
        templates = [
            TemplateDefinition(id=tmpl1_id, name="tmpl1", title="Template 1", parent_template_id=tmpl2_id),
            TemplateDefinition(id=tmpl2_id, name="tmpl2", title="Template 2", parent_template_id=tmpl3_id),
            TemplateDefinition(id=tmpl3_id, name="tmpl3", title="Template 3", parent_template_id=tmpl1_id)
        ]
        
        errors = validate_template_inheritance_chain(templates)
        assert len(errors) > 0
        assert "circular inheritance" in errors[0].lower()

    def test_template_inheritance_resolution(self):
        """Test template inheritance resolution"""
        parent_id = uuid4()
        child_id = uuid4()
        
        parent = TemplateDefinition(
            id=parent_id,
            name="parent",
            title="Parent Template",
            workflow_assignments={"feature": "parent_workflow"},
            component_templates={"feature": {"gates": ["design"]}}
        )
        
        child = TemplateDefinition(
            id=child_id,
            name="child",
            title="Child Template",
            parent_template_id=parent_id,
            workflow_assignments={"integration": "child_workflow"},
            component_templates={"feature": {"gates": ["design", "implementation"]}}
        )
        
        template_map = {parent_id: parent, child_id: child}
        resolved = resolve_template_inheritance(child, template_map)
        
        # Should have both parent and child workflow assignments
        assert "feature" in resolved["workflow_assignments"]
        assert "integration" in resolved["workflow_assignments"]
        
        # Child should override parent component templates
        assert resolved["component_templates"]["feature"]["gates"] == ["design", "implementation"]


class TestRequestResponseModels:
    """Test request and response models"""

    def test_create_component_request(self):
        """Test create component request validation"""
        project_id = uuid4()
        
        request = CreateComponentRequest(
            project_id=project_id,
            name="test_component",
            component_type=ComponentType.FEATURE,
            completion_gates=["design", "testing"]
        )
        
        assert request.project_id == project_id
        assert request.name == "test_component"
        assert request.component_type == ComponentType.FEATURE

    def test_create_template_request(self):
        """Test create template request validation"""
        request = CreateTemplateDefinitionRequest(
            name="test_template",
            title="Test Template",
            template_type=TemplateType.TEAM,
            workflow_assignments={"feature": "test_workflow"}
        )
        
        assert request.name == "test_template"
        assert request.title == "Test Template"
        assert request.template_type == TemplateType.TEAM
