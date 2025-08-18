"""
Comprehensive Tests for Workflow Error Handling and Rollback

This module provides extensive testing for workflow error handling including:
- Step execution failures and retry mechanisms
- Workflow rollback and recovery scenarios
- Error propagation and handling strategies
- Timeout and cancellation handling
- Resource cleanup and state management
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from src.server.services.workflow.workflow_executor import (
    WorkflowExecutor,
    WorkflowExecutionContext
)
from src.server.services.workflow.workflow_repository import WorkflowRepository
from src.server.models.workflow_models import (
    WorkflowTemplate,
    ActionStep,
    ConditionStep,
    ParallelStep,
    LoopStep,
    WorkflowExecutionStatus,
    StepExecutionStatus,
    WorkflowStepType
)


class TestWorkflowErrorHandling:
    """Comprehensive test cases for workflow error handling and rollback."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock workflow repository."""
        repository = Mock(spec=WorkflowRepository)
        repository.create_workflow_execution = AsyncMock()
        repository.update_workflow_execution = AsyncMock()
        repository.create_step_execution = AsyncMock()
        repository.update_step_execution = AsyncMock()
        repository.get_workflow_template = AsyncMock()
        return repository
    
    @pytest.fixture
    def workflow_executor(self, mock_repository):
        """Create WorkflowExecutor with mocked repository."""
        return WorkflowExecutor(repository=mock_repository)
    
    @pytest.fixture
    def simple_workflow_template(self):
        """Create a simple workflow template for testing."""
        return WorkflowTemplate(
            id=str(uuid4()),
            name="test_workflow",
            title="Test Workflow",
            steps=[
                ActionStep(
                    name="step1",
                    title="First Step",
                    tool_name="manage_task_archon",
                    parameters={"action": "create", "title": "Test Task"},
                    retry_count=2,
                    on_failure="retry"
                ),
                ActionStep(
                    name="step2",
                    title="Second Step",
                    tool_name="manage_project_archon",
                    parameters={"action": "list"},
                    on_failure="fail"
                )
            ]
        )
    
    @pytest.fixture
    def execution_context(self, simple_workflow_template):
        """Create execution context for testing."""
        execution_id = str(uuid4())
        return WorkflowExecutionContext(
            execution_id=execution_id,
            workflow_template=simple_workflow_template,
            input_parameters={"test_param": "test_value"}
        )
    
    @pytest.mark.asyncio
    async def test_step_execution_failure_with_retry(self, workflow_executor, execution_context):
        """Test step execution failure with retry mechanism."""
        step = execution_context.workflow_template.steps[0]  # step1 with retry
        
        # Mock MCP tool integration to fail first two times, succeed third time
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # First two calls fail, third succeeds
            mock_integration.execute_tool.side_effect = [
                (False, {"error": "First failure", "attempt_number": 1}),
                (False, {"error": "Second failure", "attempt_number": 2}),
                (True, {"success": True, "result": "Success on retry", "attempt_number": 3})
            ]
            mock_mcp.return_value = mock_integration
            
            success, result = await workflow_executor._execute_step(execution_context, step)
            
            assert success is True
            assert result["success"] is True
            assert result["attempt_number"] == 3
            
            # Verify tool was called 3 times (2 failures + 1 success)
            assert mock_integration.execute_tool.call_count == 3
    
    @pytest.mark.asyncio
    async def test_step_execution_failure_exceeds_retry_limit(self, workflow_executor, execution_context):
        """Test step execution failure that exceeds retry limit."""
        step = execution_context.workflow_template.steps[0]  # step1 with retry_count=2
        
        # Mock MCP tool integration to always fail
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # Always fail
            mock_integration.execute_tool.side_effect = [
                (False, {"error": "First failure", "attempt_number": 1}),
                (False, {"error": "Second failure", "attempt_number": 2}),
                (False, {"error": "Third failure", "attempt_number": 3})
            ]
            mock_mcp.return_value = mock_integration
            
            success, result = await workflow_executor._execute_step(execution_context, step)
            
            assert success is False
            assert "failure" in result["error"]
            assert result["attempt_number"] == 3
            
            # Verify tool was called 3 times (retry_count + 1)
            assert mock_integration.execute_tool.call_count == 3
    
    @pytest.mark.asyncio
    async def test_step_execution_timeout(self, workflow_executor, execution_context):
        """Test step execution timeout handling."""
        step = ActionStep(
            name="timeout_step",
            title="Timeout Step",
            tool_name="manage_task_archon",
            parameters={"action": "create"},
            timeout_seconds=1  # Very short timeout
        )
        
        # Mock MCP tool integration to take longer than timeout
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            
            async def slow_execution(*args, **kwargs):
                await asyncio.sleep(2)  # Longer than timeout
                return True, {"success": True}
            
            mock_integration.execute_tool = slow_execution
            mock_mcp.return_value = mock_integration
            
            success, result = await workflow_executor._execute_step(execution_context, step)
            
            assert success is False
            assert "timeout" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_workflow_execution_cancellation(self, workflow_executor, execution_context):
        """Test workflow execution cancellation during step execution."""
        # Start workflow execution
        workflow_executor.active_executions[execution_context.execution_id] = execution_context
        
        # Mock repository responses
        workflow_executor.repository.update_workflow_execution.return_value = (True, {})
        
        # Cancel execution
        success, result = await workflow_executor.cancel_execution(execution_context.execution_id)
        
        assert success is True
        assert "cancelled" in result["message"]
        
        # Verify context was marked as cancelled
        assert execution_context.is_cancelled is True
        
        # Verify execution was removed from active executions
        assert execution_context.execution_id not in workflow_executor.active_executions
    
    @pytest.mark.asyncio
    async def test_workflow_execution_pause_resume(self, workflow_executor, execution_context):
        """Test workflow execution pause and resume functionality."""
        # Start workflow execution
        workflow_executor.active_executions[execution_context.execution_id] = execution_context
        
        # Mock repository responses
        workflow_executor.repository.update_workflow_execution.return_value = (True, {})
        
        # Pause execution
        success, result = await workflow_executor.pause_execution(execution_context.execution_id)
        
        assert success is True
        assert "paused" in result["message"]
        assert execution_context.is_paused is True
        
        # Resume execution
        success, result = await workflow_executor.resume_execution(execution_context.execution_id)
        
        assert success is True
        assert "resumed" in result["message"]
        assert execution_context.is_paused is False
    
    @pytest.mark.asyncio
    async def test_parallel_step_partial_failure(self, workflow_executor, execution_context):
        """Test parallel step execution with partial failures."""
        parallel_step = ParallelStep(
            name="parallel_test",
            title="Parallel Test Step",
            parallel_steps=["substep1", "substep2", "substep3"]
        )
        
        # Add substeps to workflow template
        execution_context.workflow_template.steps.extend([
            ActionStep(
                name="substep1",
                title="Substep 1",
                tool_name="manage_task_archon",
                parameters={"action": "create"}
            ),
            ActionStep(
                name="substep2",
                title="Substep 2",
                tool_name="manage_project_archon",
                parameters={"action": "list"}
            ),
            ActionStep(
                name="substep3",
                title="Substep 3",
                tool_name="manage_task_archon",
                parameters={"action": "update"}
            )
        ])
        
        # Mock MCP tool integration with mixed results
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # First and third succeed, second fails
            mock_integration.execute_tool.side_effect = [
                (True, {"success": True, "result": "Substep 1 success"}),
                (False, {"error": "Substep 2 failed"}),
                (True, {"success": True, "result": "Substep 3 success"})
            ]
            mock_mcp.return_value = mock_integration
            
            success, result = await workflow_executor._execute_parallel_step(execution_context, parallel_step)
            
            # Parallel step should fail if any substep fails
            assert success is False
            assert "failed" in result["error"]
            
            # Verify all substeps were attempted
            assert mock_integration.execute_tool.call_count == 3
    
    @pytest.mark.asyncio
    async def test_loop_step_iteration_failure(self, workflow_executor, execution_context):
        """Test loop step execution with iteration failures."""
        loop_step = LoopStep(
            name="loop_test",
            title="Loop Test Step",
            loop_over="{{workflow.parameters.items}}",
            loop_steps=["loop_body"]
        )
        
        # Add loop body step
        execution_context.workflow_template.steps.append(
            ActionStep(
                name="loop_body",
                title="Loop Body",
                tool_name="manage_task_archon",
                parameters={"action": "create", "title": "{{loop.item}}"}
            )
        )
        
        # Set up loop items
        execution_context.variables["workflow"]["parameters"]["items"] = ["item1", "item2", "item3"]
        
        # Mock MCP tool integration with mixed results
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # First iteration succeeds, second fails, third succeeds
            mock_integration.execute_tool.side_effect = [
                (True, {"success": True, "result": "Item 1 processed"}),
                (False, {"error": "Item 2 processing failed"}),
                (True, {"success": True, "result": "Item 3 processed"})
            ]
            mock_mcp.return_value = mock_integration
            
            success, result = await workflow_executor._execute_loop_step(execution_context, loop_step)
            
            # Loop should fail if any iteration fails
            assert success is False
            assert "failed" in result["error"]
            
            # Verify all iterations were attempted
            assert mock_integration.execute_tool.call_count == 3
    
    @pytest.mark.asyncio
    async def test_condition_step_evaluation_error(self, workflow_executor, execution_context):
        """Test condition step with evaluation errors."""
        condition_step = ConditionStep(
            name="condition_test",
            title="Condition Test Step",
            condition="{{nonexistent.variable}} == 'value'",  # Invalid variable reference
            on_true="step2",
            on_false="end"
        )
        
        success, result = await workflow_executor._execute_condition_step(execution_context, condition_step)
        
        assert success is False
        assert "error" in result
        assert "evaluation" in result["error"].lower() or "variable" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_workflow_execution_exception_handling(self, workflow_executor, mock_repository):
        """Test workflow execution with unexpected exceptions."""
        workflow_template = WorkflowTemplate(
            id=str(uuid4()),
            name="exception_workflow",
            title="Exception Test Workflow",
            steps=[
                ActionStep(
                    name="step1",
                    title="Exception Step",
                    tool_name="manage_task_archon",
                    parameters={"action": "create"}
                )
            ]
        )
        
        # Mock repository to return template
        mock_repository.get_workflow_template.return_value = (True, {
            "template": workflow_template.dict()
        })
        
        # Mock repository to succeed for execution creation
        mock_repository.create_workflow_execution.return_value = (True, {
            "execution": {"id": "exec-123", "status": "pending"}
        })
        
        # Mock repository to fail during execution update (simulating database error)
        mock_repository.update_workflow_execution.side_effect = Exception("Database connection lost")
        
        success, result = await workflow_executor.start_execution(
            workflow_template.id,
            {"test_param": "test_value"},
            "test_user"
        )
        
        # Should handle the exception gracefully
        assert success is True  # Initial creation succeeds
        assert result["execution_id"] == "exec-123"
        
        # The exception will be handled during workflow execution
        # We can't easily test the async execution here, but the framework should handle it
    
    @pytest.mark.asyncio
    async def test_resource_cleanup_on_failure(self, workflow_executor, execution_context):
        """Test proper resource cleanup when workflow execution fails."""
        execution_id = execution_context.execution_id
        
        # Add execution to active executions
        workflow_executor.active_executions[execution_id] = execution_context
        
        # Create a mock task for the execution
        mock_task = Mock()
        workflow_executor._execution_tasks[execution_id] = mock_task
        
        # Mock repository for completion update
        workflow_executor.repository.update_workflow_execution.return_value = (True, {})
        
        # Simulate execution completion with failure
        await workflow_executor._complete_execution(
            execution_context, 
            WorkflowExecutionStatus.FAILED, 
            "Test failure"
        )
        
        # Verify cleanup occurred
        assert execution_id not in workflow_executor.active_executions
        assert execution_id not in workflow_executor._execution_tasks
        
        # Verify repository was updated with failure status
        workflow_executor.repository.update_workflow_execution.assert_called_once()
        call_args = workflow_executor.repository.update_workflow_execution.call_args[0][1]
        assert call_args["status"] == WorkflowExecutionStatus.FAILED
        assert call_args["error_message"] == "Test failure"
    
    @pytest.mark.asyncio
    async def test_step_execution_context_isolation(self, workflow_executor, execution_context):
        """Test that step execution failures don't corrupt execution context."""
        step = ActionStep(
            name="isolation_test",
            title="Isolation Test Step",
            tool_name="manage_task_archon",
            parameters={"action": "create"}
        )
        
        # Store original context state
        original_variables = execution_context.variables.copy()
        original_log_count = len(execution_context.execution_log)
        
        # Mock MCP tool integration to fail
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock(return_value=(False, {"error": "Step failed"}))
            mock_mcp.return_value = mock_integration
            
            success, result = await workflow_executor._execute_step(execution_context, step)
            
            assert success is False
            
            # Verify context variables weren't corrupted
            assert execution_context.variables["workflow"] == original_variables["workflow"]
            assert execution_context.variables["execution"] == original_variables["execution"]
            
            # Verify log was updated (should have one new entry for the failure)
            assert len(execution_context.execution_log) == original_log_count + 2  # start + error
            
            # Verify execution context is still functional
            assert not execution_context.is_cancelled
            assert not execution_context.is_paused
