"""
Tests for Template Injection System Pydantic Models

This module tests:
- Model validation and field constraints
- Enum value validation
- Template content validation
- Component name format validation
- Utility function behavior
"""

import pytest
from datetime import datetime
from uuid import uuid4, UUID
from pydantic import ValidationError

from python.src.server.models.template_injection_models import (
    # Enums
    TemplateInjectionType, TemplateInjectionLevel, TemplateComponentType, TemplateHierarchyType,

    # Core Models
    WorkflowTemplate, TemplateComponent, TemplateAssignment, TemplateExpansionResult,

    # Request Models
    CreateWorkflowTemplateRequest, CreateTemplateComponentRequest,
    CreateTemplateAssignmentRequest, TemplateExpansionRequest,

    # Utility Functions
    validate_template_placeholders, extract_template_placeholders,
    calculate_template_duration, validate_template_hierarchy_assignment
)


class TestEnums:
    """Test enum definitions and values"""
    
    def test_template_injection_type_enum(self):
        """Test TemplateInjectionType enum values"""
        assert TemplateInjectionType.WORKFLOW == "workflow"
        assert TemplateInjectionType.SEQUENCE == "sequence"
        assert TemplateInjectionType.ACTION == "action"

    def test_template_injection_level_enum(self):
        """Test TemplateInjectionLevel enum values"""
        assert TemplateInjectionLevel.PROJECT == "project"
        assert TemplateInjectionLevel.MILESTONE == "milestone"
        assert TemplateInjectionLevel.PHASE == "phase"
        assert TemplateInjectionLevel.TASK == "task"
        assert TemplateInjectionLevel.SUBTASK == "subtask"

    def test_template_component_type_enum(self):
        """Test TemplateComponentType enum values"""
        assert TemplateComponentType.ACTION == "action"
        assert TemplateComponentType.GROUP == "group"
        assert TemplateComponentType.SEQUENCE == "sequence"

    def test_template_hierarchy_type_enum(self):
        """Test TemplateHierarchyType enum values"""
        assert TemplateHierarchyType.PROJECT == "project"
        assert TemplateHierarchyType.MILESTONE == "milestone"
        assert TemplateHierarchyType.PHASE == "phase"
        assert TemplateHierarchyType.TASK == "task"
        assert TemplateHierarchyType.SUBTASK == "subtask"


class TestWorkflowTemplate:
    """Test WorkflowTemplate model validation"""
    
    def test_valid_workflow_template(self):
        """Test creating a valid workflow template"""
        template = WorkflowTemplate(
            name="workflow::test",
            description="Test workflow",
            template_content="{{group::test}}\n\n{{USER_TASK}}\n\n{{group::validate}}",
            user_task_position=2,
            estimated_duration=30,
            required_tools=["view", "str-replace-editor"],
            version="1.0.0"
        )
        
        assert template.name == "workflow::test"
        assert template.template_type == TemplateInjectionType.WORKFLOW
        assert template.injection_level == TemplateInjectionLevel.TASK
        assert "{{USER_TASK}}" in template.template_content
        assert template.user_task_position == 2
        assert template.estimated_duration == 30
        assert template.is_active is True
    
    def test_template_name_validation(self):
        """Test template name format validation"""
        # Valid names
        valid_names = ["workflow::default", "sequence::deployment", "action::commit"]
        for name in valid_names:
            template = WorkflowTemplate(
                name=name,
                template_content="{{USER_TASK}}"
            )
            assert template.name == name.lower()
        
        # Invalid names
        invalid_names = ["invalid", "workflow:", "::invalid", "workflow::invalid-chars!"]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                WorkflowTemplate(name=name, template_content="{{USER_TASK}}")
    
    def test_template_content_validation(self):
        """Test template content validation"""
        # Valid content with USER_TASK
        valid_content = "{{group::prep}}\n\n{{USER_TASK}}\n\n{{group::cleanup}}"
        template = WorkflowTemplate(
            name="workflow::test",
            template_content=valid_content
        )
        assert template.template_content == valid_content
        
        # Invalid content without USER_TASK
        with pytest.raises(ValidationError, match="must contain {{USER_TASK}} placeholder"):
            WorkflowTemplate(
                name="workflow::test",
                template_content="{{group::prep}}\n\n{{group::cleanup}}"
            )
        
        # Invalid placeholder format
        with pytest.raises(ValidationError, match="Invalid placeholder format"):
            WorkflowTemplate(
                name="workflow::test",
                template_content="{{invalid-placeholder!}}\n\n{{USER_TASK}}"
            )
    
    def test_version_validation(self):
        """Test semantic version validation"""
        # Valid versions
        valid_versions = ["1.0.0", "2.1.3", "1.0.0-beta", "3.2.1-alpha"]
        for version in valid_versions:
            template = WorkflowTemplate(
                name="workflow::test",
                template_content="{{USER_TASK}}",
                version=version
            )
            assert template.version == version
        
        # Invalid versions
        invalid_versions = ["1.0", "1.0.0.0", "invalid", "1.0.0-"]
        for version in invalid_versions:
            with pytest.raises(ValidationError, match="must follow semantic versioning"):
                WorkflowTemplate(
                    name="workflow::test",
                    template_content="{{USER_TASK}}",
                    version=version
                )


class TestTemplateComponent:
    """Test TemplateComponent model validation"""
    
    def test_valid_template_component(self):
        """Test creating a valid template component"""
        component = TemplateComponent(
            name="group::test_component",
            description="Test component",
            component_type=ComponentType.GROUP,
            instruction_text="This is a test instruction.",
            required_tools=["view", "str-replace-editor"],
            estimated_duration=10,
            category="testing",
            priority="high",
            tags=["test", "validation"]
        )
        
        assert component.name == "group::test_component"
        assert component.component_type == TemplateComponentType.GROUP
        assert component.instruction_text == "This is a test instruction."
        assert component.estimated_duration == 10
        assert component.category == "testing"
        assert component.priority == "high"
        assert component.is_active is True
    
    def test_component_name_validation(self):
        """Test component name format validation"""
        # Valid names
        valid_names = ["group::test", "action::commit", "sequence::deploy"]
        for name in valid_names:
            component = TemplateComponent(
                name=name,
                instruction_text="Test instruction"
            )
            assert component.name == name.lower()
        
        # Invalid names
        invalid_names = ["invalid", "group:", "::invalid", "group::invalid-chars!"]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                TemplateComponent(name=name, instruction_text="Test instruction")
    
    def test_priority_validation(self):
        """Test priority value validation"""
        # Valid priorities
        valid_priorities = ["low", "medium", "high", "critical", "HIGH", "Medium"]
        for priority in valid_priorities:
            component = TemplateComponent(
                name="group::test",
                instruction_text="Test instruction",
                priority=priority
            )
            assert component.priority == priority.lower()
        
        # Invalid priority
        with pytest.raises(ValidationError, match="Priority must be one of"):
            TemplateComponent(
                name="group::test",
                instruction_text="Test instruction",
                priority="invalid"
            )


class TestTemplateAssignment:
    """Test TemplateAssignment model validation"""
    
    def test_valid_template_assignment(self):
        """Test creating a valid template assignment"""
        assignment = TemplateAssignment(
            hierarchy_type=TemplateHierarchyType.PROJECT,
            hierarchy_id=uuid4(),
            template_id=uuid4(),
            assignment_context={"condition": "development"},
            priority=10,
            assigned_by="test-user"
        )
        
        assert assignment.hierarchy_type == TemplateHierarchyType.PROJECT
        assert isinstance(assignment.hierarchy_id, UUID)
        assert isinstance(assignment.template_id, UUID)
        assert assignment.priority == 10
        assert assignment.assigned_by == "test-user"
        assert assignment.is_active is True


class TestTemplateExpansionResult:
    """Test TemplateExpansionResult model validation"""
    
    def test_valid_expansion_result(self):
        """Test creating a valid expansion result"""
        result = TemplateExpansionResult(
            original_task="Create a new feature",
            template_name="workflow::default",
            expanded_instructions="Step 1: Prep\n\nCreate a new feature\n\nStep 2: Test",
            expansion_time_ms=150,
            component_count=5,
            project_id=uuid4()
        )
        
        assert result.original_task == "Create a new feature"
        assert result.template_name == "workflow::default"
        assert result.expansion_time_ms == 150
        assert result.component_count == 5
        assert result.validation_passed is True
        assert isinstance(result.expanded_at, datetime)
    
    def test_expansion_time_validation(self):
        """Test expansion time validation"""
        # Valid expansion time
        result = TemplateExpansionResult(
            original_task="Test task",
            template_name="workflow::test",
            expanded_instructions="Expanded instructions",
            expansion_time_ms=5000
        )
        assert result.expansion_time_ms == 5000
        
        # Invalid expansion time (too high)
        with pytest.raises(ValidationError, match="unreasonably high"):
            TemplateExpansionResult(
                original_task="Test task",
                template_name="workflow::test",
                expanded_instructions="Expanded instructions",
                expansion_time_ms=15000  # > 10 seconds
            )


class TestUtilityFunctions:
    """Test utility functions for template processing"""

    def test_validate_template_placeholders(self):
        """Test template placeholder validation"""
        template_content = "{{group::prep}}\n\n{{USER_TASK}}\n\n{{group::cleanup}}"
        available_components = ["group::prep", "group::cleanup", "group::other"]

        # Valid template
        errors = validate_template_placeholders(template_content, available_components)
        assert errors == []

        # Template with missing component
        template_content_invalid = "{{group::prep}}\n\n{{USER_TASK}}\n\n{{group::missing}}"
        errors = validate_template_placeholders(template_content_invalid, available_components)
        assert len(errors) == 1
        assert "group::missing" in errors[0]

    def test_extract_template_placeholders(self):
        """Test placeholder extraction from template content"""
        template_content = "{{group::prep}}\n\n{{USER_TASK}}\n\n{{group::cleanup}}"
        placeholders = extract_template_placeholders(template_content)

        expected = ["group::prep", "USER_TASK", "group::cleanup"]
        assert placeholders == expected

        # Empty template
        assert extract_template_placeholders("No placeholders here") == []

        # Single placeholder
        assert extract_template_placeholders("{{single::placeholder}}") == ["single::placeholder"]

    def test_calculate_template_duration(self):
        """Test template duration calculation"""
        template_content = "{{group::prep}}\n\n{{USER_TASK}}\n\n{{group::cleanup}}"
        component_durations = {
            "group::prep": 10,
            "group::cleanup": 5
        }

        total_duration = calculate_template_duration(template_content, component_durations)
        assert total_duration == 15  # 10 + 5, USER_TASK not counted

        # With missing component (should use default 5 minutes)
        template_content_missing = "{{group::prep}}\n\n{{USER_TASK}}\n\n{{group::missing}}"
        total_duration = calculate_template_duration(template_content_missing, component_durations)
        assert total_duration == 15  # 10 + 5 (default for missing)

        # Empty template
        assert calculate_template_duration("{{USER_TASK}}", {}) == 0

    def test_validate_template_hierarchy_assignment(self):
        """Test template hierarchy assignment validation"""
        project_id = uuid4()

        # Valid assignments
        assert validate_template_hierarchy_assignment(
            TemplateHierarchyType.PROJECT, project_id, TemplateInjectionLevel.PROJECT
        ) is True

        assert validate_template_hierarchy_assignment(
            TemplateHierarchyType.TASK, project_id, TemplateInjectionLevel.TASK
        ) is True

        assert validate_template_hierarchy_assignment(
            TemplateHierarchyType.TASK, project_id, TemplateInjectionLevel.SUBTASK
        ) is True

        # Invalid assignments
        assert validate_template_hierarchy_assignment(
            TemplateHierarchyType.PROJECT, project_id, TemplateInjectionLevel.SUBTASK
        ) is False

        assert validate_template_hierarchy_assignment(
            TemplateHierarchyType.SUBTASK, project_id, TemplateInjectionLevel.PROJECT
        ) is False


class TestRequestModels:
    """Test request model validation"""

    def test_create_workflow_template_request(self):
        """Test workflow template creation request"""
        request = CreateWorkflowTemplateRequest(
            name="workflow::test",
            description="Test workflow",
            template_content="{{group::prep}}\n\n{{USER_TASK}}\n\n{{group::cleanup}}",
            user_task_position=2,
            estimated_duration=45,
            required_tools=["view", "str-replace-editor"],
            version="1.0.0"
        )

        assert request.name == "workflow::test"
        assert request.template_type == TemplateInjectionType.WORKFLOW
        assert request.injection_level == TemplateInjectionLevel.TASK
        assert request.user_task_position == 2
        assert request.estimated_duration == 45

    def test_create_template_component_request(self):
        """Test template component creation request"""
        request = CreateTemplateComponentRequest(
            name="group::test",
            description="Test component",
            component_type=TemplateComponentType.GROUP,
            instruction_text="Test instruction text",
            required_tools=["view"],
            estimated_duration=8,
            category="testing",
            priority="high",
            tags=["test", "validation"]
        )

        assert request.name == "group::test"
        assert request.component_type == TemplateComponentType.GROUP
        assert request.instruction_text == "Test instruction text"
        assert request.estimated_duration == 8
        assert request.category == "testing"
        assert request.priority == "high"

    def test_template_expansion_request(self):
        """Test template expansion request"""
        project_id = uuid4()
        task_id = uuid4()

        request = TemplateExpansionRequest(
            original_task="Create a new feature",
            template_name="workflow::default",
            project_id=project_id,
            task_id=task_id,
            context_data={"phase": "development"}
        )

        assert request.original_task == "Create a new feature"
        assert request.template_name == "workflow::default"
        assert request.project_id == project_id
        assert request.task_id == task_id
        assert request.context_data == {"phase": "development"}


if __name__ == "__main__":
    pytest.main([__file__])
