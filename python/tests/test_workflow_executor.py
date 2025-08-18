"""
Tests for Workflow Executor

This module tests the workflow execution engine including:
- Workflow execution lifecycle
- Step execution for different step types
- Error handling and retry mechanisms
- Progress tracking and state management
- MCP tool integration
- Parallel and loop execution
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from src.server.services.workflow.workflow_executor import (
    WorkflowExecutor,
    WorkflowExecutionContext,
    get_workflow_executor
)
from src.server.models.workflow_models import (
    WorkflowTemplate,
    ActionStep,
    ConditionStep,
    WorkflowLinkStep,
    ParallelStep,
    LoopStep,
    WorkflowExecutionStatus,
    StepExecutionStatus,
    WorkflowStepType
)


class TestWorkflowExecutionContext:
    """Test workflow execution context"""
    
    @pytest.fixture
    def sample_template(self):
        """Sample workflow template"""
        return WorkflowTemplate(
            id=str(uuid4()),
            name="test_workflow",
            title="Test Workflow",
            description="Test workflow for execution",
            steps=[
                ActionStep(
                    name="step1",
                    title="Step 1",
                    type=WorkflowStepType.ACTION,
                    tool_name="test_tool",
                    parameters={"param1": "{{workflow.parameters.input_param}}"}
                )
            ],
            parameters={"input_param": {"type": "string", "required": True}}
        )
    
    def test_context_initialization(self, sample_template):
        """Test context initialization"""
        execution_id = str(uuid4())
        input_params = {"input_param": "test_value"}
        
        context = WorkflowExecutionContext(execution_id, sample_template, input_params)
        
        assert context.execution_id == execution_id
        assert context.workflow_template == sample_template
        assert context.input_parameters == input_params
        assert context.current_step_index == 0
        assert not context.is_cancelled
        assert not context.is_paused
        assert "workflow" in context.variables
        assert "execution" in context.variables
    
    def test_variable_substitution(self, sample_template):
        """Test variable substitution"""
        execution_id = str(uuid4())
        input_params = {"input_param": "test_value"}
        
        context = WorkflowExecutionContext(execution_id, sample_template, input_params)
        
        # Test simple substitution
        result = context.substitute_variables("Hello {{workflow.parameters.input_param}}")
        assert result == "Hello test_value"
        
        # Test nested substitution
        context.variables["custom"] = {"nested": "nested_value"}
        result = context.substitute_variables("Value: {{custom.nested}}")
        assert result == "Value: nested_value"
        
        # Test missing variable
        result = context.substitute_variables("Missing: {{missing.var}}")
        assert result == "Missing: {{missing.var}}"  # Should return original
    
    def test_parameter_substitution(self, sample_template):
        """Test parameter dictionary substitution"""
        execution_id = str(uuid4())
        input_params = {"input_param": "test_value"}
        
        context = WorkflowExecutionContext(execution_id, sample_template, input_params)
        
        params = {
            "action": "create",
            "title": "{{workflow.parameters.input_param}}",
            "nested": {
                "value": "{{workflow.parameters.input_param}}"
            },
            "list": ["item1", "{{workflow.parameters.input_param}}"]
        }
        
        result = context.substitute_parameters(params)
        
        assert result["action"] == "create"
        assert result["title"] == "test_value"
        assert result["nested"]["value"] == "test_value"
        assert result["list"] == ["item1", "test_value"]
    
    def test_step_result_storage(self, sample_template):
        """Test step result storage"""
        execution_id = str(uuid4())
        input_params = {"input_param": "test_value"}
        
        context = WorkflowExecutionContext(execution_id, sample_template, input_params)
        
        step_result = {"success": True, "result": "step_output"}
        context.set_step_result("step1", step_result)
        
        assert context.step_results["step1"] == step_result
        assert context.variables["steps"]["step1"] == step_result
    
    def test_log_entry_addition(self, sample_template):
        """Test log entry addition"""
        execution_id = str(uuid4())
        input_params = {"input_param": "test_value"}
        
        context = WorkflowExecutionContext(execution_id, sample_template, input_params)
        
        context.add_log_entry("info", "Test message", "step1", {"detail": "test"})
        
        assert len(context.execution_log) == 1
        log_entry = context.execution_log[0]
        assert log_entry["level"] == "info"
        assert log_entry["message"] == "Test message"
        assert log_entry["step_name"] == "step1"


class TestWorkflowExecutor:
    """Test workflow executor"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock workflow repository"""
        repo = Mock()
        repo.get_workflow_template = Mock()
        repo.create_workflow_execution = AsyncMock()
        repo.update_workflow_execution = AsyncMock()
        repo.create_step_execution = AsyncMock()
        repo.update_step_execution = AsyncMock()
        repo.list_workflow_templates = Mock()
        return repo
    
    @pytest.fixture
    def workflow_executor(self, mock_repository):
        """Create workflow executor with mock repository"""
        return WorkflowExecutor(repository=mock_repository)
    
    @pytest.fixture
    def sample_template_data(self):
        """Sample workflow template data"""
        return {
            "id": str(uuid4()),
            "name": "test_workflow",
            "title": "Test Workflow",
            "description": "Test workflow",
            "steps": [
                {
                    "name": "step1",
                    "title": "Step 1",
                    "type": "action",
                    "tool_name": "test_tool",
                    "parameters": {"param1": "value1"}
                }
            ],
            "parameters": {"input_param": {"type": "string", "required": True}}
        }
    
    @pytest.mark.asyncio
    async def test_start_execution_success(self, workflow_executor, mock_repository, sample_template_data):
        """Test successful workflow execution start"""
        template_id = sample_template_data["id"]
        input_params = {"input_param": "test_value"}
        
        # Mock repository responses
        mock_repository.get_workflow_template.return_value = (True, {"template": sample_template_data})
        mock_repository.create_workflow_execution.return_value = (True, {
            "execution": {
                "id": str(uuid4()),
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
        })
        
        success, result = await workflow_executor.start_execution(
            template_id,
            input_params,
            "test_user"
        )
        
        assert success is True
        assert "execution_id" in result
        assert result["status"] == "pending"
        assert "message" in result
        
        # Verify repository calls
        mock_repository.get_workflow_template.assert_called_once_with(template_id)
        mock_repository.create_workflow_execution.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_execution_template_not_found(self, workflow_executor, mock_repository):
        """Test workflow execution start with template not found"""
        template_id = str(uuid4())
        input_params = {"input_param": "test_value"}
        
        # Mock repository response for template not found
        mock_repository.get_workflow_template.return_value = (False, {"error": "Template not found"})
        
        success, result = await workflow_executor.start_execution(
            template_id,
            input_params,
            "test_user"
        )
        
        assert success is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_cancel_execution_active(self, workflow_executor):
        """Test cancelling an active execution"""
        execution_id = str(uuid4())
        
        # Create mock context
        mock_context = Mock()
        mock_context.is_cancelled = False
        mock_context.add_log_entry = Mock()
        workflow_executor.active_executions[execution_id] = mock_context
        
        # Create mock task
        mock_task = Mock()
        mock_task.cancel = Mock()
        workflow_executor._execution_tasks[execution_id] = mock_task
        
        success, result = await workflow_executor.cancel_execution(execution_id)
        
        assert success is True
        assert "message" in result
        assert mock_context.is_cancelled is True
        mock_context.add_log_entry.assert_called_once()
        mock_task.cancel.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_pause_execution(self, workflow_executor, mock_repository):
        """Test pausing an execution"""
        execution_id = str(uuid4())
        
        # Create mock context
        mock_context = Mock()
        mock_context.is_paused = False
        mock_context.add_log_entry = Mock()
        workflow_executor.active_executions[execution_id] = mock_context
        
        mock_repository.update_workflow_execution.return_value = (True, {})
        
        success, result = await workflow_executor.pause_execution(execution_id)
        
        assert success is True
        assert "message" in result
        assert mock_context.is_paused is True
        mock_context.add_log_entry.assert_called_once()
        mock_repository.update_workflow_execution.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_resume_execution(self, workflow_executor, mock_repository):
        """Test resuming an execution"""
        execution_id = str(uuid4())
        
        # Create mock context
        mock_context = Mock()
        mock_context.is_paused = True
        mock_context.add_log_entry = Mock()
        workflow_executor.active_executions[execution_id] = mock_context
        
        mock_repository.update_workflow_execution.return_value = (True, {})
        
        success, result = await workflow_executor.resume_execution(execution_id)
        
        assert success is True
        assert "message" in result
        assert mock_context.is_paused is False
        mock_context.add_log_entry.assert_called_once()
        mock_repository.update_workflow_execution.assert_called_once()


class TestStepExecution:
    """Test individual step execution"""
    
    @pytest.fixture
    def mock_context(self):
        """Mock execution context"""
        context = Mock()
        context.execution_id = str(uuid4())
        context.current_step_index = 0
        context.add_log_entry = Mock()
        context.set_step_result = Mock()
        context.substitute_parameters = Mock(side_effect=lambda x: x)
        return context
    
    @pytest.fixture
    def workflow_executor(self):
        """Create workflow executor for step testing"""
        mock_repo = Mock()
        mock_repo.create_step_execution = AsyncMock(return_value=(True, {"step_execution": {"id": str(uuid4())}}))
        mock_repo.update_step_execution = AsyncMock(return_value=(True, {}))
        return WorkflowExecutor(repository=mock_repo)
    
    @pytest.mark.asyncio
    @patch('src.server.services.workflow.workflow_executor.get_mcp_client')
    async def test_execute_action_step_success(self, mock_get_mcp_client, workflow_executor, mock_context):
        """Test successful action step execution"""
        # Mock MCP client
        mock_mcp_client = Mock()
        mock_mcp_client.call_tool = AsyncMock(return_value={"success": True, "result": "tool_output"})
        mock_get_mcp_client.return_value = mock_mcp_client
        
        # Create action step
        step = ActionStep(
            name="test_step",
            title="Test Step",
            type=WorkflowStepType.ACTION,
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        
        success, result = await workflow_executor._execute_action_step(mock_context, step, str(uuid4()))
        
        assert success is True
        assert result["success"] is True
        assert "result" in result
        assert result["tool_name"] == "test_tool"
        
        # Verify MCP client was called
        mock_mcp_client.call_tool.assert_called_once_with("test_tool", param1="value1")
    
    @pytest.mark.asyncio
    @patch('src.server.services.workflow.workflow_executor.get_mcp_client')
    async def test_execute_action_step_failure(self, mock_get_mcp_client, workflow_executor, mock_context):
        """Test action step execution failure"""
        # Mock MCP client to raise exception
        mock_mcp_client = Mock()
        mock_mcp_client.call_tool = AsyncMock(side_effect=Exception("Tool execution failed"))
        mock_get_mcp_client.return_value = mock_mcp_client
        
        # Create action step
        step = ActionStep(
            name="test_step",
            title="Test Step",
            type=WorkflowStepType.ACTION,
            tool_name="test_tool",
            parameters={"param1": "value1"}
        )
        
        success, result = await workflow_executor._execute_action_step(mock_context, step, str(uuid4()))
        
        assert success is False
        assert result["success"] is False
        assert "error" in result
        assert "Tool execution failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_condition_step(self, workflow_executor, mock_context):
        """Test condition step execution"""
        # Mock variable substitution
        mock_context.substitute_variables.return_value = "true"
        
        # Create condition step
        step = ConditionStep(
            name="test_condition",
            title="Test Condition",
            type=WorkflowStepType.CONDITION,
            condition="{{workflow.parameters.enabled}} == true"
        )
        
        success, result = await workflow_executor._execute_condition_step(mock_context, step, str(uuid4()))
        
        assert success is True
        assert result["success"] is True
        assert result["condition_result"] is True
        assert "condition" in result
    
    def test_evaluate_condition_simple(self, workflow_executor):
        """Test simple condition evaluation"""
        # Test equality
        assert workflow_executor._evaluate_condition("test == test") is True
        assert workflow_executor._evaluate_condition("test == other") is False
        
        # Test inequality
        assert workflow_executor._evaluate_condition("test != other") is True
        assert workflow_executor._evaluate_condition("test != test") is False
        
        # Test boolean values
        assert workflow_executor._evaluate_condition("true") is True
        assert workflow_executor._evaluate_condition("false") is False
        assert workflow_executor._evaluate_condition("1") is True
        assert workflow_executor._evaluate_condition("0") is False
    
    @pytest.mark.asyncio
    async def test_execute_parallel_step(self, workflow_executor, mock_context):
        """Test parallel step execution"""
        # Create sub-steps
        sub_step1 = ActionStep(
            name="sub1",
            title="Sub Step 1",
            type=WorkflowStepType.ACTION,
            tool_name="tool1",
            parameters={}
        )
        sub_step2 = ActionStep(
            name="sub2",
            title="Sub Step 2",
            type=WorkflowStepType.ACTION,
            tool_name="tool2",
            parameters={}
        )
        
        # Create parallel step
        parallel_step = ParallelStep(
            name="parallel_test",
            title="Parallel Test",
            type=WorkflowStepType.PARALLEL,
            steps=[sub_step1, sub_step2],
            wait_for_all=True
        )
        
        # Mock step execution
        with patch.object(workflow_executor, '_execute_step') as mock_execute:
            mock_execute.return_value = (True, {"success": True})
            
            success, result = await workflow_executor._execute_parallel_step(mock_context, parallel_step, str(uuid4()))
            
            assert success is True
            assert result["success"] is True
            assert result["success_count"] == 2
            assert len(result["results"]) == 2
            
            # Verify both sub-steps were executed
            assert mock_execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_loop_step(self, workflow_executor, mock_context):
        """Test loop step execution"""
        # Mock variable substitution for collection
        mock_context.substitute_variables.return_value = '["item1", "item2", "item3"]'
        
        # Create sub-step
        sub_step = ActionStep(
            name="loop_sub",
            title="Loop Sub Step",
            type=WorkflowStepType.ACTION,
            tool_name="loop_tool",
            parameters={"item": "{{loop_item}}"}
        )
        
        # Create loop step
        loop_step = LoopStep(
            name="loop_test",
            title="Loop Test",
            type=WorkflowStepType.LOOP,
            collection="{{workflow.parameters.items}}",
            item_variable="loop_item",
            steps=[sub_step],
            max_iterations=10
        )
        
        # Mock step execution
        with patch.object(workflow_executor, '_execute_step') as mock_execute:
            mock_execute.return_value = (True, {"success": True})
            
            success, result = await workflow_executor._execute_loop_step(mock_context, loop_step, str(uuid4()))
            
            assert success is True
            assert result["success"] is True
            assert result["iterations"] == 3
            assert len(result["results"]) == 3
            
            # Verify sub-step was executed for each iteration
            assert mock_execute.call_count == 3


class TestWorkflowExecutorGlobal:
    """Test global workflow executor instance"""
    
    def test_get_workflow_executor_singleton(self):
        """Test that get_workflow_executor returns singleton"""
        executor1 = get_workflow_executor()
        executor2 = get_workflow_executor()
        
        assert executor1 is executor2
        assert isinstance(executor1, WorkflowExecutor)


if __name__ == "__main__":
    pytest.main([__file__])
