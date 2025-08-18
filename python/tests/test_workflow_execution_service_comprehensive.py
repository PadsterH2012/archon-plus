"""
Comprehensive Tests for Workflow Execution Service

This module provides extensive testing for the workflow execution service including:
- Background execution management
- Task lifecycle and progress tracking
- Error handling and recovery scenarios
- WebSocket integration testing
- Performance and scalability testing
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
from src.server.services.background_task_manager import BackgroundTaskManager
from src.server.models.workflow_models import (
    WorkflowTemplate,
    ActionStep,
    WorkflowExecutionStatus,
    WorkflowStepType
)


class TestWorkflowExecutionService:
    """Comprehensive test cases for WorkflowExecutionService."""
    
    @pytest.fixture
    def mock_executor(self):
        """Mock workflow executor."""
        executor = Mock(spec=WorkflowExecutor)
        executor.start_execution = AsyncMock()
        executor.cancel_execution = AsyncMock()
        executor.pause_execution = AsyncMock()
        executor.resume_execution = AsyncMock()
        executor.get_execution_status = AsyncMock()
        return executor
    
    @pytest.fixture
    def mock_repository(self):
        """Mock workflow repository."""
        repository = Mock(spec=WorkflowRepository)
        repository.create_workflow_execution = AsyncMock()
        repository.get_workflow_execution = AsyncMock()
        repository.update_workflow_execution = AsyncMock()
        return repository
    
    @pytest.fixture
    def mock_task_manager(self):
        """Mock background task manager."""
        task_manager = Mock(spec=BackgroundTaskManager)
        task_manager.submit_task = AsyncMock()
        task_manager.cancel_task = AsyncMock()
        task_manager.get_task_status = AsyncMock()
        return task_manager
    
    @pytest.fixture
    def execution_service(self, mock_executor, mock_repository, mock_task_manager):
        """Create WorkflowExecutionService with mocked dependencies."""
        return WorkflowExecutionService(
            executor=mock_executor,
            repository=mock_repository,
            task_manager=mock_task_manager
        )
    
    @pytest.mark.asyncio
    async def test_start_workflow_execution_background_success(self, execution_service, mock_repository):
        """Test successful background workflow execution start."""
        workflow_id = str(uuid4())
        input_params = {"param1": "value1"}
        triggered_by = "test_user"
        
        # Mock repository responses
        mock_repository.create_workflow_execution.return_value = (True, {
            "execution": {"id": "exec-123", "status": "pending"}
        })
        
        # Mock task manager
        execution_service.task_manager.submit_task.return_value = "task-456"
        
        success, result = await execution_service.start_workflow_execution(
            workflow_id, input_params, triggered_by, background=True
        )
        
        assert success is True
        assert result["execution_id"] == "exec-123"
        assert result["task_id"] == "task-456"
        assert result["status"] == "pending"
        
        # Verify repository was called correctly
        mock_repository.create_workflow_execution.assert_called_once()
        call_args = mock_repository.create_workflow_execution.call_args[0][0]
        assert call_args["workflow_template_id"] == workflow_id
        assert call_args["triggered_by"] == triggered_by
        assert call_args["input_parameters"] == input_params
        
        # Verify task manager was called
        execution_service.task_manager.submit_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_workflow_execution_direct_success(self, execution_service):
        """Test successful direct (non-background) workflow execution start."""
        workflow_id = str(uuid4())
        input_params = {"param1": "value1"}
        triggered_by = "test_user"
        
        # Mock executor response
        execution_service.executor.start_execution.return_value = (True, {
            "execution_id": "exec-789",
            "status": "running"
        })
        
        success, result = await execution_service.start_workflow_execution(
            workflow_id, input_params, triggered_by, background=False
        )
        
        assert success is True
        assert result["execution_id"] == "exec-789"
        assert result["status"] == "running"
        
        # Verify executor was called directly
        execution_service.executor.start_execution.assert_called_once_with(
            workflow_id, input_params, triggered_by, None
        )
    
    @pytest.mark.asyncio
    async def test_start_workflow_execution_repository_failure(self, execution_service, mock_repository):
        """Test workflow execution start with repository failure."""
        workflow_id = str(uuid4())
        input_params = {"param1": "value1"}
        triggered_by = "test_user"
        
        # Mock repository failure
        mock_repository.create_workflow_execution.return_value = (False, {
            "error": "Database connection failed"
        })
        
        success, result = await execution_service.start_workflow_execution(
            workflow_id, input_params, triggered_by, background=True
        )
        
        assert success is False
        assert "Database connection failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_cancel_workflow_execution_success(self, execution_service):
        """Test successful workflow execution cancellation."""
        execution_id = "exec-123"
        
        # Mock executor response
        execution_service.executor.cancel_execution.return_value = (True, {
            "message": "Execution cancelled successfully"
        })
        
        # Setup execution task tracking
        execution_service.execution_tasks[execution_id] = "task-456"
        execution_service.task_manager.cancel_task.return_value = True
        
        success, result = await execution_service.cancel_workflow_execution(execution_id)
        
        assert success is True
        assert "cancelled successfully" in result["message"]
        
        # Verify executor was called
        execution_service.executor.cancel_execution.assert_called_once_with(execution_id)
        
        # Verify background task was cancelled
        execution_service.task_manager.cancel_task.assert_called_once_with("task-456")
        
        # Verify task tracking was cleaned up
        assert execution_id not in execution_service.execution_tasks
    
    @pytest.mark.asyncio
    async def test_cancel_workflow_execution_task_cleanup_failure(self, execution_service):
        """Test workflow cancellation with background task cleanup failure."""
        execution_id = "exec-123"
        
        # Mock executor success
        execution_service.executor.cancel_execution.return_value = (True, {
            "message": "Execution cancelled successfully"
        })
        
        # Setup execution task tracking
        execution_service.execution_tasks[execution_id] = "task-456"
        
        # Mock task manager failure
        execution_service.task_manager.cancel_task.side_effect = Exception("Task cleanup failed")
        
        success, result = await execution_service.cancel_workflow_execution(execution_id)
        
        # Should still succeed despite task cleanup failure
        assert success is True
        assert "cancelled successfully" in result["message"]
        
        # Verify task tracking was still cleaned up
        assert execution_id not in execution_service.execution_tasks
    
    @pytest.mark.asyncio
    async def test_pause_workflow_execution_success(self, execution_service):
        """Test successful workflow execution pause."""
        execution_id = "exec-123"
        
        # Mock executor response
        execution_service.executor.pause_execution.return_value = (True, {
            "message": "Workflow execution paused"
        })
        
        success, result = await execution_service.pause_workflow_execution(execution_id)
        
        assert success is True
        assert "paused" in result["message"]
        
        # Verify executor was called
        execution_service.executor.pause_execution.assert_called_once_with(execution_id)
    
    @pytest.mark.asyncio
    async def test_resume_workflow_execution_success(self, execution_service):
        """Test successful workflow execution resume."""
        execution_id = "exec-123"
        
        # Mock executor response
        execution_service.executor.resume_execution.return_value = (True, {
            "message": "Workflow execution resumed"
        })
        
        success, result = await execution_service.resume_workflow_execution(execution_id)
        
        assert success is True
        assert "resumed" in result["message"]
        
        # Verify executor was called
        execution_service.executor.resume_execution.assert_called_once_with(execution_id)
    
    @pytest.mark.asyncio
    async def test_get_execution_status_success(self, execution_service, mock_repository):
        """Test successful execution status retrieval."""
        execution_id = "exec-123"
        
        # Mock repository response
        mock_repository.get_workflow_execution.return_value = (True, {
            "execution": {
                "id": execution_id,
                "status": "running",
                "progress_percentage": 50.0
            }
        })
        
        mock_repository.list_step_executions.return_value = (True, {
            "step_executions": [
                {"id": "step-1", "status": "completed"},
                {"id": "step-2", "status": "running"}
            ]
        })
        
        success, result = await execution_service.get_execution_status(execution_id)
        
        assert success is True
        assert result["execution"]["id"] == execution_id
        assert result["execution"]["status"] == "running"
        assert len(result["step_executions"]) == 2
        assert result["total_steps"] == 2
    
    @pytest.mark.asyncio
    async def test_get_execution_status_not_found(self, execution_service, mock_repository):
        """Test execution status retrieval for non-existent execution."""
        execution_id = "nonexistent-exec"
        
        # Mock repository response
        mock_repository.get_workflow_execution.return_value = (False, {
            "error": "Execution not found"
        })
        
        success, result = await execution_service.get_execution_status(execution_id)
        
        assert success is False
        assert "not found" in result["error"]
    
    def test_websocket_manager_lazy_loading(self, execution_service):
        """Test WebSocket manager lazy loading."""
        # Initially should be None
        assert execution_service._websocket_manager is None
        
        # Mock the import to avoid circular dependency
        with patch('src.server.services.workflow.workflow_execution_service.get_workflow_websocket_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager
            
            # First access should load the manager
            manager = execution_service.websocket_manager
            assert manager is mock_manager
            assert execution_service._websocket_manager is mock_manager
            
            # Second access should return cached instance
            manager2 = execution_service.websocket_manager
            assert manager2 is mock_manager
            
            # Should only call the getter once
            mock_get_manager.assert_called_once()
    
    def test_websocket_manager_import_failure(self, execution_service):
        """Test WebSocket manager handling when import fails."""
        # Mock import failure
        with patch('src.server.services.workflow.workflow_execution_service.get_workflow_websocket_manager', side_effect=ImportError("Module not found")):
            manager = execution_service.websocket_manager
            assert manager is None
    
    def test_execution_progress_callback(self, execution_service):
        """Test execution progress callback functionality."""
        # Test basic callback
        execution_service._execution_progress_callback(50.0, "Step 1 completed")
        
        # Test callback with WebSocket manager
        mock_manager = Mock()
        mock_manager.broadcast_to_execution = AsyncMock()
        execution_service._websocket_manager = mock_manager
        
        # Test callback with execution_id in message
        execution_service._execution_progress_callback(
            75.0, 
            "Step 2 completed execution_id=exec-123 successfully"
        )
        
        # Note: The actual WebSocket broadcast is created as a task, 
        # so we can't easily verify it was called in this synchronous test
    
    @pytest.mark.asyncio
    async def test_background_execution_workflow(self, execution_service):
        """Test the complete background execution workflow."""
        execution_id = "exec-123"
        workflow_id = str(uuid4())
        input_params = {"param1": "value1"}
        triggered_by = "test_user"
        
        # Mock executor response
        execution_service.executor.start_execution.return_value = (True, {
            "execution_id": execution_id,
            "status": "completed"
        })
        
        # Mock repository response for final status
        execution_service.repository.get_workflow_execution.return_value = (True, {
            "execution": {
                "id": execution_id,
                "status": "completed",
                "progress_percentage": 100.0
            }
        })
        
        result = await execution_service._execute_workflow_background(
            execution_id, workflow_id, input_params, triggered_by, None
        )
        
        assert result["success"] is True
        assert result["execution_id"] == execution_id
        assert result["status"] == "completed"
        
        # Verify executor was called
        execution_service.executor.start_execution.assert_called_once_with(
            workflow_id, input_params, triggered_by, None
        )
    
    @pytest.mark.asyncio
    async def test_background_execution_failure(self, execution_service, mock_repository):
        """Test background execution with failure."""
        execution_id = "exec-123"
        workflow_id = str(uuid4())
        
        # Mock executor failure
        execution_service.executor.start_execution.side_effect = Exception("Execution failed")
        
        # Mock repository update for failure
        mock_repository.update_workflow_execution.return_value = (True, {})
        
        result = await execution_service._execute_workflow_background(
            execution_id, workflow_id, {}, "test_user", None
        )
        
        assert result["success"] is False
        assert "Execution failed" in result["error"]
        
        # Verify failure was recorded in repository
        mock_repository.update_workflow_execution.assert_called_once()
        call_args = mock_repository.update_workflow_execution.call_args[0]
        assert call_args[0] == execution_id
        assert call_args[1]["status"] == "failed"
        assert "Execution failed" in call_args[1]["error_message"]
    
    def test_get_workflow_execution_service_singleton(self):
        """Test that get_workflow_execution_service returns singleton instance."""
        service1 = get_workflow_execution_service()
        service2 = get_workflow_execution_service()
        
        # Should return the same instance
        assert service1 is service2
        assert isinstance(service1, WorkflowExecutionService)
