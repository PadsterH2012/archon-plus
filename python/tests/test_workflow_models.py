"""
Tests for Workflow System Pydantic Models

This module tests:
- Model validation and serialization
- Field constraints and validators
- Step type validation
- Workflow template validation
- Error handling and edge cases
"""

import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from src.server.models.workflow_models import (
    # Enums
    WorkflowStatus,
    WorkflowStepType,
    WorkflowExecutionStatus,
    StepExecutionStatus,

    # Step Models
    ActionStep,
    ConditionStep,
    WorkflowLinkStep,
    ParallelStep,
    LoopStep,

    # Main Models
    WorkflowTemplate,
    WorkflowExecution,
    WorkflowStepExecution,
    WorkflowTemplateVersion,

    # Request Models
    CreateWorkflowTemplateRequest,
    ExecuteWorkflowRequest,
)


class TestWorkflowStepModels:
    """Test workflow step model validation"""

    def test_action_step_valid(self):
        """Test valid action step creation"""
        step = ActionStep(
            name="test_action",
            title="Test Action",
            tool_name="manage_task_archon",
            parameters={"action": "create", "title": "Test Task"}
        )

        assert step.name == "test_action"
        assert step.type == WorkflowStepType.ACTION
        assert step.tool_name == "manage_task_archon"
        assert step.timeout_seconds == 300  # default

    def test_action_step_invalid_name(self):
        """Test action step with invalid name"""
        with pytest.raises(ValidationError) as exc_info:
            ActionStep(
                name="test action!",  # Invalid characters
                title="Test Action",
                tool_name="test_tool"
            )

        assert "alphanumeric characters" in str(exc_info.value)

    def test_action_step_empty_tool_name(self):
        """Test action step with empty tool name"""
        with pytest.raises(ValidationError) as exc_info:
            ActionStep(
                name="test_action",
                title="Test Action",
                tool_name=""  # Empty tool name
            )

        assert "cannot be empty" in str(exc_info.value)

    def test_condition_step_valid(self):
        """Test valid condition step creation"""
        step = ConditionStep(
            name="check_status",
            title="Check Status",
            condition="{{previous_step.output.status}} == 'success'",
            on_true="next_step",
            on_false="error_step"
        )

        assert step.type == WorkflowStepType.CONDITION
        assert step.condition == "{{previous_step.output.status}} == 'success'"

    def test_workflow_link_step_valid(self):
        """Test valid workflow link step creation"""
        step = WorkflowLinkStep(
            name="backup_workflow",
            title="Run Backup",
            workflow_name="database_backup",
            parameters={"database_id": "{{context.db_id}}"}
        )

        assert step.type == WorkflowStepType.WORKFLOW_LINK
        assert step.workflow_name == "database_backup"

    def test_parallel_step_valid(self):
        """Test valid parallel step creation"""
        sub_steps = [
            ActionStep(name="step1", title="Step 1", tool_name="tool1"),
            ActionStep(name="step2", title="Step 2", tool_name="tool2")
        ]

        step = ParallelStep(
            name="parallel_tasks",
            title="Parallel Tasks",
            steps=sub_steps
        )

        assert step.type == WorkflowStepType.PARALLEL
        assert len(step.steps) == 2
        assert step.wait_for_all is True  # default

    def test_parallel_step_empty_steps(self):
        """Test parallel step with no sub-steps"""
        with pytest.raises(ValidationError) as exc_info:
            ParallelStep(
                name="parallel_tasks",
                title="Parallel Tasks",
                steps=[]  # Empty steps
            )

        assert "at least one sub-step" in str(exc_info.value)

    def test_loop_step_valid(self):
        """Test valid loop step creation"""
        sub_steps = [
            ActionStep(name="process_item", title="Process Item", tool_name="process_tool")
        ]

        step = LoopStep(
            name="process_all",
            title="Process All Items",
            collection="{{workflow.parameters.items}}",
            item_variable="item",
            steps=sub_steps
        )

        assert step.type == WorkflowStepType.LOOP
        assert step.collection == "{{workflow.parameters.items}}"
        assert step.max_iterations == 100  # default


class TestWorkflowTemplate:
    """Test workflow template model validation"""

    def test_workflow_template_valid(self):
        """Test valid workflow template creation"""
        steps = [
            ActionStep(name="step1", title="Step 1", tool_name="tool1"),
            ActionStep(name="step2", title="Step 2", tool_name="tool2")
        ]

        template = WorkflowTemplate(
            name="test_workflow",
            title="Test Workflow",
            description="A test workflow",
            steps=steps,
            parameters={"param1": {"type": "string", "required": True}},
            category="testing"
        )

        assert template.name == "test_workflow"
        assert template.status == WorkflowStatus.DRAFT  # default
        assert len(template.steps) == 2
        assert template.version == "1.0.0"  # default

    def test_workflow_template_invalid_name(self):
        """Test workflow template with invalid name"""
        steps = [ActionStep(name="step1", title="Step 1", tool_name="tool1")]

        with pytest.raises(ValidationError) as exc_info:
            WorkflowTemplate(
                name="Test Workflow!",  # Invalid characters
                title="Test Workflow",
                steps=steps
            )

        assert "alphanumeric characters" in str(exc_info.value)

    def test_workflow_template_invalid_version(self):
        """Test workflow template with invalid version"""
        steps = [ActionStep(name="step1", title="Step 1", tool_name="tool1")]

        with pytest.raises(ValidationError) as exc_info:
            WorkflowTemplate(
                name="test_workflow",
                title="Test Workflow",
                version="invalid_version",  # Invalid format
                steps=steps
            )

        assert "semantic versioning" in str(exc_info.value)

    def test_workflow_template_empty_steps(self):
        """Test workflow template with no steps"""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowTemplate(
                name="test_workflow",
                title="Test Workflow",
                steps=[]  # Empty steps
            )

        assert "at least one step" in str(exc_info.value)

    def test_workflow_template_invalid_step_references(self):
        """Test workflow template with invalid step references"""
        steps = [
            ActionStep(
                name="step1",
                title="Step 1",
                tool_name="tool1",
                on_success="nonexistent_step"  # Invalid reference
            )
        ]

        with pytest.raises(ValidationError) as exc_info:
            WorkflowTemplate(
                name="test_workflow",
                title="Test Workflow",
                steps=steps
            )

        assert "unknown step" in str(exc_info.value)

    def test_workflow_template_valid_step_references(self):
        """Test workflow template with valid step references"""
        steps = [
            ActionStep(
                name="step1",
                title="Step 1",
                tool_name="tool1",
                on_success="step2"  # Valid reference
            ),
            ActionStep(
                name="step2",
                title="Step 2",
                tool_name="tool2",
                on_success="end"  # Valid built-in reference
            )
        ]

        template = WorkflowTemplate(
            name="test_workflow",
            title="Test Workflow",
            steps=steps
        )

        assert len(template.steps) == 2

    def test_workflow_template_condition_step_references(self):
        """Test workflow template with condition step references"""
        steps = [
            ConditionStep(
                name="check_condition",
                title="Check Condition",
                condition="{{test}} == true",
                on_true="success_step",
                on_false="failure_step"
            ),
            ActionStep(name="success_step", title="Success", tool_name="success_tool"),
            ActionStep(name="failure_step", title="Failure", tool_name="failure_tool")
        ]

        template = WorkflowTemplate(
            name="test_workflow",
            title="Test Workflow",
            steps=steps
        )

        assert len(template.steps) == 3


class TestWorkflowExecution:
    """Test workflow execution model validation"""

    def test_workflow_execution_valid(self):
        """Test valid workflow execution creation"""
        execution = WorkflowExecution(
            workflow_template_id=uuid4(),
            triggered_by="test_user",
            input_parameters={"param1": "value1"},
            total_steps=3
        )

        assert execution.status == WorkflowExecutionStatus.PENDING  # default
        assert execution.current_step_index == 0  # default
        assert execution.progress_percentage == 0.0  # default
        assert execution.triggered_by == "test_user"

    def test_workflow_execution_invalid_progress(self):
        """Test workflow execution with invalid progress"""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowExecution(
                workflow_template_id=uuid4(),
                triggered_by="test_user",
                progress_percentage=150.0  # Invalid range
            )

        assert "between 0 and 100" in str(exc_info.value)

    def test_workflow_execution_negative_step_index(self):
        """Test workflow execution with negative step index"""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowExecution(
                workflow_template_id=uuid4(),
                triggered_by="test_user",
                current_step_index=-1  # Invalid negative
            )

        assert "non-negative" in str(exc_info.value)


class TestWorkflowStepExecution:
    """Test workflow step execution model validation"""

    def test_step_execution_valid(self):
        """Test valid step execution creation"""
        step_execution = WorkflowStepExecution(
            workflow_execution_id=uuid4(),
            step_index=0,
            step_name="test_step",
            step_type=WorkflowStepType.ACTION,
            tool_name="test_tool"
        )

        assert step_execution.status == StepExecutionStatus.PENDING  # default
        assert step_execution.attempt_number == 1  # default
        assert step_execution.max_attempts == 1  # default

    def test_step_execution_invalid_attempts(self):
        """Test step execution with invalid attempt numbers"""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowStepExecution(
                workflow_execution_id=uuid4(),
                step_index=0,
                step_name="test_step",
                step_type=WorkflowStepType.ACTION,
                attempt_number=0  # Invalid zero
            )

        assert "must be positive" in str(exc_info.value)


class TestRequestModels:
    """Test API request model validation"""

    def test_create_workflow_request_valid(self):
        """Test valid create workflow request"""
        request = CreateWorkflowTemplateRequest(
            name="test_workflow",
            title="Test Workflow",
            description="A test workflow",
            steps=[
                {
                    "name": "step1",
                    "title": "Step 1",
                    "type": "action",
                    "tool_name": "test_tool"
                }
            ]
        )

        assert request.name == "test_workflow"
        assert request.timeout_minutes == 60  # default
        assert len(request.steps) == 1

    def test_execute_workflow_request_valid(self):
        """Test valid execute workflow request"""
        request = ExecuteWorkflowRequest(
            workflow_template_id=uuid4(),
            input_parameters={"param1": "value1"},
            triggered_by="test_user"
        )

        assert request.triggered_by == "test_user"
        assert request.input_parameters == {"param1": "value1"}


class TestModelSerialization:
    """Test model serialization and deserialization"""

    def test_workflow_template_serialization(self):
        """Test workflow template JSON serialization"""
        steps = [
            ActionStep(name="step1", title="Step 1", tool_name="tool1")
        ]

        template = WorkflowTemplate(
            name="test_workflow",
            title="Test Workflow",
            steps=steps
        )

        # Test serialization
        json_data = template.dict()
        assert json_data["name"] == "test_workflow"
        assert json_data["steps"][0]["type"] == "action"

        # Test deserialization
        new_template = WorkflowTemplate(**json_data)
        assert new_template.name == template.name
        assert len(new_template.steps) == len(template.steps)

    def test_step_polymorphic_serialization(self):
        """Test polymorphic step serialization"""
        action_step = ActionStep(name="action", title="Action", tool_name="tool")
        condition_step = ConditionStep(
            name="condition",
            title="Condition",
            condition="test",
            on_true="next",
            on_false="end"
        )

        # Serialize both step types
        action_dict = action_step.dict()
        condition_dict = condition_step.dict()

        assert action_dict["type"] == "action"
        assert "tool_name" in action_dict

        assert condition_dict["type"] == "condition"
        assert "condition" in condition_dict
        assert "on_true" in condition_dict


class TestWorkflowValidation:
    """Test workflow validation functionality"""

    def test_valid_workflow_passes_validation(self):
        """Test that a valid workflow passes all validation"""
        from src.server.models.workflow_validation import validate_workflow_template

        steps = [
            ActionStep(
                name="step1",
                title="Step 1",
                tool_name="manage_task_archon",
                parameters={"action": "create", "title": "{{workflow.parameters.task_title}}"}
            ),
            ActionStep(
                name="step2",
                title="Step 2",
                tool_name="manage_project_archon",
                parameters={"action": "list"}
            )
        ]

        template = WorkflowTemplate(
            name="test_workflow",
            title="Test Workflow",
            steps=steps,
            parameters={"task_title": {"type": "string", "required": True}}
        )

        result = validate_workflow_template(template)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_circular_reference_detection(self):
        """Test detection of circular references"""
        from src.server.models.workflow_validation import validate_workflow_template

        steps = [
            ActionStep(
                name="step1",
                title="Step 1",
                tool_name="test_tool",
                on_success="step2"
            ),
            ActionStep(
                name="step2",
                title="Step 2",
                tool_name="test_tool",
                on_success="step1"  # Creates circular reference
            )
        ]

        template = WorkflowTemplate(
            name="circular_workflow",
            title="Circular Workflow",
            steps=steps
        )

        result = validate_workflow_template(template)
        assert not result.is_valid
        assert any(error.code == "CIRCULAR_REFERENCE" for error in result.errors)

    def test_missing_step_reference_validation(self):
        """Test validation of missing step references"""
        from src.server.models.workflow_validation import validate_workflow_template

        steps = [
            ActionStep(
                name="step1",
                title="Step 1",
                tool_name="test_tool",
                on_success="nonexistent_step"  # Invalid reference
            )
        ]

        template = WorkflowTemplate(
            name="invalid_ref_workflow",
            title="Invalid Reference Workflow",
            steps=steps
        )

        result = validate_workflow_template(template)
        assert not result.is_valid
        assert any(error.code == "INVALID_SUCCESS_REFERENCE" for error in result.errors)

    def test_unused_parameter_warning(self):
        """Test warning for unused parameters"""
        from src.server.models.workflow_validation import validate_workflow_template

        steps = [
            ActionStep(
                name="step1",
                title="Step 1",
                tool_name="test_tool"
                # Not using the declared parameter
            )
        ]

        template = WorkflowTemplate(
            name="unused_param_workflow",
            title="Unused Parameter Workflow",
            steps=steps,
            parameters={"unused_param": {"type": "string"}}  # Declared but not used
        )

        result = validate_workflow_template(template)
        assert any(warning.code == "UNUSED_PARAMETER" for warning in result.warnings)

    def test_undeclared_parameter_error(self):
        """Test error for undeclared parameters"""
        from src.server.models.workflow_validation import validate_workflow_template

        steps = [
            ActionStep(
                name="step1",
                title="Step 1",
                tool_name="test_tool",
                parameters={"value": "{{workflow.parameters.undeclared_param}}"}  # Using undeclared param
            )
        ]

        template = WorkflowTemplate(
            name="undeclared_param_workflow",
            title="Undeclared Parameter Workflow",
            steps=steps
            # No parameters declared
        )

        result = validate_workflow_template(template)
        assert not result.is_valid
        assert any(error.code == "UNDECLARED_PARAMETER" for error in result.errors)


if __name__ == "__main__":
    pytest.main([__file__])
