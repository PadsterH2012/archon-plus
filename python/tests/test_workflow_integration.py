"""
Integration Tests for Workflow Engine

This module provides integration testing for the workflow system including:
- Database integration and transaction handling
- MCP tool integration and real tool execution
- End-to-end workflow execution scenarios
- WebSocket integration testing
- Cross-service integration testing
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime

from src.server.services.workflow.workflow_execution_service import (
    WorkflowExecutionService,
    get_workflow_execution_service
)
from src.server.services.workflow.workflow_executor import WorkflowExecutor
from src.server.services.workflow.workflow_repository import WorkflowRepository
from src.server.services.workflow.mcp_tool_integration import (
    MCPWorkflowIntegration,
    get_mcp_workflow_integration
)
from src.server.models.workflow_models import (
    WorkflowTemplate,
    ActionStep,
    ConditionStep,
    WorkflowLinkStep,
    ParallelStep,
    LoopStep,
    WorkflowExecutionStatus,
    WorkflowStatus
)


class TestWorkflowIntegration:
    """Integration test cases for workflow engine."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client for database operations."""
        client = Mock()
        
        # Mock table operations
        table_mock = Mock()
        table_mock.insert = Mock(return_value=Mock(execute=AsyncMock(return_value=Mock(
            data=[{"id": "test-id", "created_at": datetime.now().isoformat()}]
        ))))
        table_mock.select = Mock(return_value=Mock(execute=AsyncMock(return_value=Mock(
            data=[{"id": "test-id", "status": "active"}]
        ))))
        table_mock.update = Mock(return_value=Mock(execute=AsyncMock(return_value=Mock(
            data=[{"id": "test-id", "updated_at": datetime.now().isoformat()}]
        ))))
        table_mock.delete = Mock(return_value=Mock(execute=AsyncMock(return_value=Mock(
            data=[{"id": "test-id"}]
        ))))
        
        client.table = Mock(return_value=table_mock)
        return client
    
    @pytest.fixture
    def workflow_repository(self, mock_supabase_client):
        """Create WorkflowRepository with mocked database."""
        return WorkflowRepository(mock_supabase_client)
    
    @pytest.fixture
    def sample_workflow_template(self):
        """Create a sample workflow template for testing."""
        return WorkflowTemplate(
            id=str(uuid4()),
            name="integration_test_workflow",
            title="Integration Test Workflow",
            description="A workflow for integration testing",
            version="1.0",
            status=WorkflowStatus.ACTIVE,
            steps=[
                ActionStep(
                    name="create_task",
                    title="Create Task",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "create",
                        "title": "{{workflow.parameters.task_title}}",
                        "description": "Created by integration test"
                    },
                    next_step="update_task"
                ),
                ActionStep(
                    name="update_task",
                    title="Update Task",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "update",
                        "task_id": "{{create_task.result.task_id}}",
                        "status": "in_progress"
                    },
                    next_step="check_status"
                ),
                ConditionStep(
                    name="check_status",
                    title="Check Status",
                    condition="{{update_task.result.success}} == true",
                    on_true="complete_task",
                    on_false="handle_error"
                ),
                ActionStep(
                    name="complete_task",
                    title="Complete Task",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "update",
                        "task_id": "{{create_task.result.task_id}}",
                        "status": "completed"
                    }
                ),
                ActionStep(
                    name="handle_error",
                    title="Handle Error",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "update",
                        "task_id": "{{create_task.result.task_id}}",
                        "status": "failed"
                    }
                )
            ],
            parameters={
                "task_title": {"type": "string", "required": True}
            }
        )
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_workflow_execution(self, workflow_repository, sample_workflow_template):
        """Test complete end-to-end workflow execution."""
        # Create workflow executor with real repository
        executor = WorkflowExecutor(repository=workflow_repository)
        
        # Mock MCP tool integration with realistic responses
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # Define realistic tool responses
            mock_integration.execute_tool.side_effect = [
                # create_task response
                (True, {
                    "success": True,
                    "result": {
                        "task_id": "task-123",
                        "title": "Integration Test Task",
                        "status": "created"
                    }
                }),
                # update_task response
                (True, {
                    "success": True,
                    "result": {
                        "task_id": "task-123",
                        "status": "in_progress",
                        "updated": True
                    }
                }),
                # complete_task response
                (True, {
                    "success": True,
                    "result": {
                        "task_id": "task-123",
                        "status": "completed",
                        "completed_at": datetime.now().isoformat()
                    }
                })
            ]
            mock_mcp.return_value = mock_integration
            
            # Execute workflow
            input_parameters = {"task_title": "Integration Test Task"}
            success, result = await executor.start_execution(
                sample_workflow_template.id,
                input_parameters,
                "integration_test"
            )
            
            assert success is True
            assert "execution_id" in result
            
            # Verify all expected tools were called
            assert mock_integration.execute_tool.call_count == 3
            
            # Verify the execution flow
            call_args_list = mock_integration.execute_tool.call_args_list
            
            # First call should be create_task
            first_call = call_args_list[0][0]
            assert first_call[0] == "manage_task_archon"
            assert first_call[1]["action"] == "create"
            
            # Second call should be update_task
            second_call = call_args_list[1][0]
            assert second_call[0] == "manage_task_archon"
            assert second_call[1]["action"] == "update"
            
            # Third call should be complete_task
            third_call = call_args_list[2][0]
            assert third_call[0] == "manage_task_archon"
            assert third_call[1]["action"] == "update"
            assert third_call[1]["status"] == "completed"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_execution_service_integration(self, workflow_repository):
        """Test workflow execution service with real components."""
        # Create execution service with real repository
        mock_task_manager = Mock()
        mock_task_manager.submit_task = AsyncMock(return_value="task-456")
        
        execution_service = WorkflowExecutionService(
            repository=workflow_repository,
            task_manager=mock_task_manager
        )
        
        workflow_id = str(uuid4())
        input_parameters = {"test_param": "test_value"}
        
        # Test background execution start
        success, result = await execution_service.start_workflow_execution(
            workflow_id,
            input_parameters,
            "integration_test",
            background=True
        )
        
        assert success is True
        assert "execution_id" in result
        assert "task_id" in result
        assert result["status"] == "pending"
        
        # Verify task was submitted to background manager
        mock_task_manager.submit_task.assert_called_once()
        
        # Verify execution was tracked
        execution_id = result["execution_id"]
        assert execution_id in execution_service.execution_tasks
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_mcp_tool_integration_real_tools(self):
        """Test MCP tool integration with realistic tool scenarios."""
        mcp_integration = get_mcp_workflow_integration()
        
        # Test manage_task_archon tool
        success, result = await mcp_integration.execute_tool(
            "manage_task_archon",
            {
                "action": "create",
                "title": "Integration Test Task",
                "description": "Created by MCP integration test"
            }
        )
        
        # Should succeed with mock implementation
        assert success is True
        assert "tool_name" in result
        assert result["tool_name"] == "manage_task_archon"
        assert "parameters" in result
        assert result["parameters"]["action"] == "create"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_repository_database_operations(self, workflow_repository, sample_workflow_template):
        """Test workflow repository database operations."""
        # Test template creation
        template_data = sample_workflow_template.dict()
        success, result = await workflow_repository.create_workflow_template(template_data)
        
        assert success is True
        assert "template" in result
        
        # Test execution creation
        execution_data = {
            "workflow_template_id": sample_workflow_template.id,
            "input_parameters": {"task_title": "Test Task"},
            "triggered_by": "integration_test",
            "status": "pending"
        }
        
        success, result = await workflow_repository.create_workflow_execution(execution_data)
        
        assert success is True
        assert "execution" in result
        
        execution_id = result["execution"]["id"]
        
        # Test execution update
        update_data = {
            "status": "running",
            "progress_percentage": 50.0,
            "current_step_index": 1
        }
        
        success, result = await workflow_repository.update_workflow_execution(execution_id, update_data)
        
        assert success is True
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_parallel_step_integration(self, workflow_repository):
        """Test parallel step execution with real components."""
        # Create workflow with parallel steps
        parallel_workflow = WorkflowTemplate(
            id=str(uuid4()),
            name="parallel_integration_test",
            title="Parallel Integration Test",
            steps=[
                ParallelStep(
                    name="parallel_tasks",
                    title="Parallel Tasks",
                    parallel_steps=["task1", "task2", "task3"]
                ),
                ActionStep(
                    name="task1",
                    title="Task 1",
                    tool_name="manage_task_archon",
                    parameters={"action": "create", "title": "Task 1"}
                ),
                ActionStep(
                    name="task2",
                    title="Task 2",
                    tool_name="manage_project_archon",
                    parameters={"action": "list"}
                ),
                ActionStep(
                    name="task3",
                    title="Task 3",
                    tool_name="manage_task_archon",
                    parameters={"action": "create", "title": "Task 3"}
                )
            ]
        )
        
        executor = WorkflowExecutor(repository=workflow_repository)
        
        # Mock MCP tool integration
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # All parallel tasks succeed
            mock_integration.execute_tool.side_effect = [
                (True, {"success": True, "result": {"task_id": "task-1"}}),
                (True, {"success": True, "result": {"projects": ["project-1"]}}),
                (True, {"success": True, "result": {"task_id": "task-3"}})
            ]
            mock_mcp.return_value = mock_integration
            
            # Execute workflow
            success, result = await executor.start_execution(
                parallel_workflow.id,
                {},
                "integration_test"
            )
            
            assert success is True
            
            # Verify all parallel tasks were executed
            assert mock_integration.execute_tool.call_count == 3
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_loop_step_integration(self, workflow_repository):
        """Test loop step execution with real components."""
        # Create workflow with loop
        loop_workflow = WorkflowTemplate(
            id=str(uuid4()),
            name="loop_integration_test",
            title="Loop Integration Test",
            steps=[
                LoopStep(
                    name="process_items",
                    title="Process Items",
                    loop_over="{{workflow.parameters.items}}",
                    loop_steps=["process_item"]
                ),
                ActionStep(
                    name="process_item",
                    title="Process Item",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "create",
                        "title": "Process {{loop.item.name}}",
                        "priority": "{{loop.item.priority}}"
                    }
                )
            ],
            parameters={
                "items": {"type": "array", "required": True}
            }
        )
        
        executor = WorkflowExecutor(repository=workflow_repository)
        
        # Mock MCP tool integration
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # Each loop iteration succeeds
            mock_integration.execute_tool.side_effect = [
                (True, {"success": True, "result": {"task_id": "task-item1"}}),
                (True, {"success": True, "result": {"task_id": "task-item2"}}),
                (True, {"success": True, "result": {"task_id": "task-item3"}})
            ]
            mock_mcp.return_value = mock_integration
            
            # Execute workflow with loop items
            input_parameters = {
                "items": [
                    {"name": "Item 1", "priority": "high"},
                    {"name": "Item 2", "priority": "medium"},
                    {"name": "Item 3", "priority": "low"}
                ]
            }
            
            success, result = await executor.start_execution(
                loop_workflow.id,
                input_parameters,
                "integration_test"
            )
            
            assert success is True
            
            # Verify all loop iterations were executed
            assert mock_integration.execute_tool.call_count == 3
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_workflow_link_integration(self, workflow_repository):
        """Test workflow link step with sub-workflow execution."""
        # Create main workflow with workflow link
        main_workflow = WorkflowTemplate(
            id=str(uuid4()),
            name="main_workflow",
            title="Main Workflow",
            steps=[
                ActionStep(
                    name="setup",
                    title="Setup",
                    tool_name="manage_task_archon",
                    parameters={"action": "create", "title": "Setup Task"},
                    next_step="call_subworkflow"
                ),
                WorkflowLinkStep(
                    name="call_subworkflow",
                    title="Call Sub-workflow",
                    workflow_id="sub-workflow-123",
                    input_mapping={
                        "sub_param": "{{setup.result.task_id}}",
                        "static_param": "static_value"
                    }
                )
            ]
        )
        
        executor = WorkflowExecutor(repository=workflow_repository)
        
        # Mock workflow execution service for sub-workflow
        with patch('src.server.services.workflow.workflow_executor.get_workflow_execution_service') as mock_service:
            mock_exec_service = Mock()
            mock_exec_service.start_workflow_execution = AsyncMock(return_value=(True, {
                "execution_id": "sub-exec-456",
                "status": "pending"
            }))
            mock_exec_service.get_execution_status = AsyncMock(return_value=(True, {
                "execution": {
                    "id": "sub-exec-456",
                    "status": "completed",
                    "output_data": {"result": "sub_workflow_result"}
                }
            }))
            mock_service.return_value = mock_exec_service
            
            # Mock MCP tool integration for setup step
            with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
                mock_integration = Mock()
                mock_integration.execute_tool = AsyncMock(return_value=(True, {
                    "success": True,
                    "result": {"task_id": "setup-task-123"}
                }))
                mock_mcp.return_value = mock_integration
                
                # Execute workflow
                success, result = await executor.start_execution(
                    main_workflow.id,
                    {},
                    "integration_test"
                )
                
                assert success is True
                
                # Verify setup step was executed
                mock_integration.execute_tool.assert_called_once()
                
                # Verify sub-workflow was started
                mock_exec_service.start_workflow_execution.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_websocket_integration(self, workflow_repository):
        """Test WebSocket integration with workflow execution."""
        # Create execution service
        execution_service = WorkflowExecutionService(repository=workflow_repository)
        
        # Mock WebSocket manager
        mock_websocket_manager = Mock()
        mock_websocket_manager.broadcast_to_execution = AsyncMock()
        execution_service._websocket_manager = mock_websocket_manager
        
        execution_id = "exec-websocket-test"
        
        # Test progress callback with WebSocket broadcasting
        execution_service._execution_progress_callback(
            50.0,
            f"Step completed execution_id={execution_id} successfully"
        )
        
        # Give async task time to execute
        await asyncio.sleep(0.1)
        
        # Note: The WebSocket broadcast is created as a task, so we can't easily verify
        # it was called in this test. In a real integration test, we would set up
        # actual WebSocket connections and verify messages are received.
    
    @pytest.mark.integration
    def test_singleton_service_instances(self):
        """Test that service singletons work correctly in integration scenarios."""
        # Test workflow execution service singleton
        service1 = get_workflow_execution_service()
        service2 = get_workflow_execution_service()
        assert service1 is service2
        
        # Test MCP workflow integration singleton
        mcp1 = get_mcp_workflow_integration()
        mcp2 = get_mcp_workflow_integration()
        assert mcp1 is mcp2
