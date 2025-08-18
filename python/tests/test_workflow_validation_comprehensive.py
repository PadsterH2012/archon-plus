"""
Comprehensive Tests for Workflow Validation

This module provides extensive testing for workflow validation including:
- Structural validation and dependency checking
- Circular reference detection
- Parameter and tool configuration validation
- Performance and complexity analysis
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch

from src.server.models.workflow_validation import (
    WorkflowValidator,
    ValidationResult,
    validate_workflow_template
)
from src.server.models.workflow_models import (
    WorkflowTemplate,
    ActionStep,
    ConditionStep,
    WorkflowLinkStep,
    ParallelStep,
    LoopStep,
    WorkflowStepType,
    WorkflowStatus
)


class TestWorkflowValidator:
    """Comprehensive test cases for WorkflowValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create WorkflowValidator instance."""
        return WorkflowValidator()
    
    def test_valid_simple_workflow(self, validator):
        """Test validation of a simple valid workflow."""
        steps = [
            ActionStep(
                name="step1",
                title="First Step",
                tool_name="manage_task_archon",
                parameters={"action": "create", "title": "Test Task"}
            ),
            ActionStep(
                name="step2",
                title="Second Step",
                tool_name="manage_project_archon",
                parameters={"action": "list"}
            )
        ]
        
        workflow = WorkflowTemplate(
            name="simple_workflow",
            title="Simple Test Workflow",
            steps=steps,
            parameters={"task_title": {"type": "string", "required": True}}
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_empty_workflow_validation(self, validator):
        """Test validation of workflow with no steps."""
        workflow = WorkflowTemplate(
            name="empty_workflow",
            title="Empty Workflow",
            steps=[],
            parameters={}
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "EMPTY_WORKFLOW" for error in result.errors)
    
    def test_duplicate_step_names(self, validator):
        """Test validation with duplicate step names."""
        steps = [
            ActionStep(
                name="duplicate_step",
                title="First Step",
                tool_name="manage_task_archon",
                parameters={"action": "create"}
            ),
            ActionStep(
                name="duplicate_step",  # Duplicate name
                title="Second Step",
                tool_name="manage_project_archon",
                parameters={"action": "list"}
            )
        ]
        
        workflow = WorkflowTemplate(
            name="duplicate_names_workflow",
            title="Workflow with Duplicate Names",
            steps=steps
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "DUPLICATE_STEP_NAME" for error in result.errors)
    
    def test_circular_reference_detection(self, validator):
        """Test detection of circular references in workflow steps."""
        steps = [
            ConditionStep(
                name="step1",
                title="First Step",
                condition="{{step3.result}} == 'success'",  # References step3
                on_true="step2",
                on_false="end"
            ),
            ActionStep(
                name="step2",
                title="Second Step",
                tool_name="manage_task_archon",
                parameters={"action": "create"},
                next_step="step3"
            ),
            ActionStep(
                name="step3",
                title="Third Step",
                tool_name="manage_project_archon",
                parameters={"action": "list"},
                next_step="step1"  # Creates circular reference
            )
        ]
        
        workflow = WorkflowTemplate(
            name="circular_workflow",
            title="Workflow with Circular Reference",
            steps=steps
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "CIRCULAR_REFERENCE" for error in result.errors)
    
    def test_invalid_step_references(self, validator):
        """Test validation with invalid step references."""
        steps = [
            ActionStep(
                name="step1",
                title="First Step",
                tool_name="manage_task_archon",
                parameters={"action": "create"},
                next_step="nonexistent_step"  # Invalid reference
            ),
            ConditionStep(
                name="step2",
                title="Condition Step",
                condition="{{step1.result}} == 'success'",
                on_true="another_nonexistent_step",  # Invalid reference
                on_false="end"
            )
        ]
        
        workflow = WorkflowTemplate(
            name="invalid_refs_workflow",
            title="Workflow with Invalid References",
            steps=steps
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "INVALID_STEP_REFERENCE" for error in result.errors)
        # Should have at least 2 errors for the invalid references
        invalid_ref_errors = [e for e in result.errors if e.code == "INVALID_STEP_REFERENCE"]
        assert len(invalid_ref_errors) >= 2
    
    def test_parameter_validation(self, validator):
        """Test parameter validation and template usage."""
        steps = [
            ActionStep(
                name="step1",
                title="Step with Parameters",
                tool_name="manage_task_archon",
                parameters={
                    "action": "create",
                    "title": "{{workflow.parameters.task_title}}",  # Valid parameter
                    "description": "{{workflow.parameters.nonexistent_param}}"  # Invalid parameter
                }
            )
        ]
        
        workflow = WorkflowTemplate(
            name="param_workflow",
            title="Workflow with Parameters",
            steps=steps,
            parameters={
                "task_title": {"type": "string", "required": True}
                # nonexistent_param is not defined
            }
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "UNDEFINED_PARAMETER" for error in result.errors)
    
    def test_required_parameter_validation(self, validator):
        """Test validation of required parameters."""
        workflow = WorkflowTemplate(
            name="required_param_workflow",
            title="Workflow with Required Parameters",
            steps=[
                ActionStep(
                    name="step1",
                    title="Step 1",
                    tool_name="manage_task_archon",
                    parameters={"action": "create"}
                )
            ],
            parameters={
                "required_param": {"type": "string", "required": True},
                "optional_param": {"type": "string", "required": False}
            }
        )
        
        result = validator.validate(workflow)
        
        # Should pass validation (required parameters are defined)
        assert result.is_valid is True
    
    def test_action_step_validation(self, validator):
        """Test specific validation for action steps."""
        steps = [
            ActionStep(
                name="invalid_action",
                title="Invalid Action Step",
                tool_name="",  # Empty tool name
                parameters={}
            ),
            ActionStep(
                name="valid_action",
                title="Valid Action Step",
                tool_name="manage_task_archon",
                parameters={"action": "create"}
            )
        ]
        
        workflow = WorkflowTemplate(
            name="action_validation_workflow",
            title="Action Step Validation",
            steps=steps
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "EMPTY_TOOL_NAME" for error in result.errors)
    
    def test_condition_step_validation(self, validator):
        """Test specific validation for condition steps."""
        steps = [
            ConditionStep(
                name="invalid_condition",
                title="Invalid Condition Step",
                condition="",  # Empty condition
                on_true="step2",
                on_false="end"
            ),
            ConditionStep(
                name="missing_branches",
                title="Missing Branches",
                condition="{{step1.result}} == 'success'",
                on_true="",  # Empty on_true
                on_false=""  # Empty on_false
            ),
            ActionStep(
                name="step2",
                title="Target Step",
                tool_name="manage_task_archon",
                parameters={"action": "list"}
            )
        ]
        
        workflow = WorkflowTemplate(
            name="condition_validation_workflow",
            title="Condition Step Validation",
            steps=steps
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "EMPTY_CONDITION" for error in result.errors)
        assert any(error.code == "EMPTY_CONDITION_BRANCH" for error in result.errors)
    
    def test_parallel_step_validation(self, validator):
        """Test specific validation for parallel steps."""
        steps = [
            ParallelStep(
                name="invalid_parallel",
                title="Invalid Parallel Step",
                parallel_steps=[]  # Empty parallel steps
            ),
            ParallelStep(
                name="valid_parallel",
                title="Valid Parallel Step",
                parallel_steps=["step2", "step3"]
            ),
            ActionStep(
                name="step2",
                title="Parallel Step 1",
                tool_name="manage_task_archon",
                parameters={"action": "create"}
            ),
            ActionStep(
                name="step3",
                title="Parallel Step 2",
                tool_name="manage_project_archon",
                parameters={"action": "list"}
            )
        ]
        
        workflow = WorkflowTemplate(
            name="parallel_validation_workflow",
            title="Parallel Step Validation",
            steps=steps
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "EMPTY_PARALLEL_STEPS" for error in result.errors)
    
    def test_loop_step_validation(self, validator):
        """Test specific validation for loop steps."""
        steps = [
            LoopStep(
                name="invalid_loop",
                title="Invalid Loop Step",
                loop_over="",  # Empty loop_over
                loop_steps=[]  # Empty loop steps
            ),
            LoopStep(
                name="valid_loop",
                title="Valid Loop Step",
                loop_over="{{workflow.parameters.items}}",
                loop_steps=["step2"]
            ),
            ActionStep(
                name="step2",
                title="Loop Body Step",
                tool_name="manage_task_archon",
                parameters={"action": "create"}
            )
        ]
        
        workflow = WorkflowTemplate(
            name="loop_validation_workflow",
            title="Loop Step Validation",
            steps=steps,
            parameters={
                "items": {"type": "array", "required": True}
            }
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "EMPTY_LOOP_CONDITION" for error in result.errors)
        assert any(error.code == "EMPTY_LOOP_STEPS" for error in result.errors)
    
    def test_workflow_link_step_validation(self, validator):
        """Test specific validation for workflow link steps."""
        steps = [
            WorkflowLinkStep(
                name="invalid_link",
                title="Invalid Workflow Link",
                workflow_id="",  # Empty workflow ID
                input_mapping={}
            ),
            WorkflowLinkStep(
                name="valid_link",
                title="Valid Workflow Link",
                workflow_id="workflow-123",
                input_mapping={"param1": "{{workflow.parameters.value1}}"}
            )
        ]
        
        workflow = WorkflowTemplate(
            name="link_validation_workflow",
            title="Workflow Link Validation",
            steps=steps,
            parameters={
                "value1": {"type": "string", "required": True}
            }
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is False
        assert any(error.code == "EMPTY_WORKFLOW_ID" for error in result.errors)
    
    def test_performance_analysis(self, validator):
        """Test performance analysis for complex workflows."""
        # Create a workflow with many steps to trigger performance warnings
        steps = []
        for i in range(25):  # Create 25 steps (should trigger complexity warning)
            steps.append(ActionStep(
                name=f"step_{i}",
                title=f"Step {i}",
                tool_name="manage_task_archon",
                parameters={"action": "list"},
                next_step=f"step_{i+1}" if i < 24 else "end"
            ))
        
        workflow = WorkflowTemplate(
            name="complex_workflow",
            title="Complex Workflow",
            steps=steps
        )
        
        result = validator.validate(workflow)
        
        # Should be valid but have performance warnings
        assert result.is_valid is True
        assert any(warning.code == "HIGH_COMPLEXITY" for warning in result.warnings)
    
    def test_long_timeout_warning(self, validator):
        """Test warning for steps with very long timeouts."""
        steps = [
            ActionStep(
                name="long_timeout_step",
                title="Step with Long Timeout",
                tool_name="manage_task_archon",
                parameters={"action": "create"},
                timeout_seconds=7200  # 2 hours - should trigger warning
            )
        ]
        
        workflow = WorkflowTemplate(
            name="timeout_workflow",
            title="Workflow with Long Timeout",
            steps=steps
        )
        
        result = validator.validate(workflow)
        
        assert result.is_valid is True
        assert any(warning.code == "LONG_STEP_TIMEOUT" for warning in result.warnings)
    
    def test_tool_compatibility_validation(self, validator):
        """Test tool compatibility validation."""
        steps = [
            ActionStep(
                name="unknown_tool_step",
                title="Step with Unknown Tool",
                tool_name="nonexistent_tool",
                parameters={"action": "create"}
            ),
            ActionStep(
                name="known_tool_step",
                title="Step with Known Tool",
                tool_name="manage_task_archon",
                parameters={"action": "create"}
            )
        ]
        
        workflow = WorkflowTemplate(
            name="tool_compatibility_workflow",
            title="Tool Compatibility Test",
            steps=steps
        )
        
        result = validator.validate(workflow)
        
        # Should have warnings about unknown tools
        assert any(warning.code == "UNKNOWN_TOOL" for warning in result.warnings)
    
    def test_validate_workflow_template_function(self):
        """Test the standalone validate_workflow_template function."""
        workflow = WorkflowTemplate(
            name="test_workflow",
            title="Test Workflow",
            steps=[
                ActionStep(
                    name="step1",
                    title="Test Step",
                    tool_name="manage_task_archon",
                    parameters={"action": "create"}
                )
            ]
        )
        
        result = validate_workflow_template(workflow)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
