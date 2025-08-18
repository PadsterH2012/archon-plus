"""
Workflow Execution Service

This service provides high-level workflow execution management that integrates
with the background task manager for long-running workflow executions.
It provides a clean interface for the API layer and handles execution monitoring.
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from ...config.logfire_config import get_logger, logfire
from ...services.background_task_manager import BackgroundTaskManager
from .workflow_executor import WorkflowExecutor, get_workflow_executor
from .workflow_repository import WorkflowRepository
from ...utils import get_supabase_client

logger = get_logger(__name__)


class WorkflowExecutionService:
    """High-level workflow execution service"""
    
    def __init__(
        self, 
        executor: Optional[WorkflowExecutor] = None,
        repository: Optional[WorkflowRepository] = None,
        task_manager: Optional[BackgroundTaskManager] = None
    ):
        """Initialize workflow execution service"""
        self.executor = executor or get_workflow_executor()
        self.repository = repository or WorkflowRepository(get_supabase_client())
        self.task_manager = task_manager or BackgroundTaskManager()
        
        # Track execution tasks
        self.execution_tasks: Dict[str, str] = {}  # execution_id -> task_id mapping

        # WebSocket manager for real-time updates (lazy loaded to avoid circular imports)
        self._websocket_manager = None

    @property
    def websocket_manager(self):
        """Get WebSocket manager instance (lazy loaded)."""
        if self._websocket_manager is None:
            try:
                from ...api_routes.workflow_websocket import get_workflow_websocket_manager
                self._websocket_manager = get_workflow_websocket_manager()
            except ImportError:
                # WebSocket manager not available
                self._websocket_manager = None
        return self._websocket_manager
    async def start_workflow_execution(
        self,
        workflow_template_id: str,
        input_parameters: Dict[str, Any],
        triggered_by: str = "api",
        trigger_context: Optional[Dict[str, Any]] = None,
        background: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Start workflow execution with optional background processing.
        
        Args:
            workflow_template_id: UUID of workflow template to execute
            input_parameters: Input parameters for the workflow
            triggered_by: Who triggered the execution
            trigger_context: Additional context for the execution
            background: Whether to run in background (default: True)
            
        Returns:
            Tuple of (success, result_dict)
        """
        try:
            logfire.info(
                f"Starting workflow execution service | template_id={workflow_template_id} | "
                f"triggered_by={triggered_by} | background={background}"
            )
            
            if background:
                # Start execution in background using task manager
                return await self._start_background_execution(
                    workflow_template_id,
                    input_parameters,
                    triggered_by,
                    trigger_context
                )
            else:
                # Start execution directly (blocking)
                return await self.executor.start_execution(
                    workflow_template_id,
                    input_parameters,
                    triggered_by,
                    trigger_context
                )
                
        except Exception as e:
            logfire.error(f"Error starting workflow execution | error={str(e)}")
            return False, {"error": f"Error starting workflow execution: {str(e)}"}
    
    async def _start_background_execution(
        self,
        workflow_template_id: str,
        input_parameters: Dict[str, Any],
        triggered_by: str,
        trigger_context: Optional[Dict[str, Any]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Start workflow execution in background using task manager"""
        try:
            # Create execution record first
            execution_data = {
                "workflow_template_id": workflow_template_id,
                "triggered_by": triggered_by,
                "trigger_context": trigger_context or {},
                "input_parameters": input_parameters,
                "status": "pending",
                "total_steps": 0  # Will be updated when template is loaded
            }
            
            exec_success, exec_result = await self.repository.create_workflow_execution(execution_data)
            if not exec_success:
                return False, exec_result
            
            execution = exec_result["execution"]
            execution_id = execution["id"]
            
            # Submit to background task manager
            task_id = await self.task_manager.submit_task(
                self._execute_workflow_background,
                (execution_id, workflow_template_id, input_parameters, triggered_by, trigger_context),
                task_id=f"workflow_execution_{execution_id}",
                progress_callback=self._execution_progress_callback
            )
            
            # Track the task
            self.execution_tasks[execution_id] = task_id
            
            logfire.info(
                f"Workflow execution submitted to background | execution_id={execution_id} | task_id={task_id}"
            )
            
            return True, {
                "execution_id": execution_id,
                "task_id": task_id,
                "status": "pending",
                "message": "Workflow execution started in background"
            }
            
        except Exception as e:
            logfire.error(f"Error starting background execution | error={str(e)}")
            return False, {"error": f"Error starting background execution: {str(e)}"}
    
    async def _execute_workflow_background(
        self,
        execution_id: str,
        workflow_template_id: str,
        input_parameters: Dict[str, Any],
        triggered_by: str,
        trigger_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute workflow in background task"""
        try:
            logfire.info(f"Starting background workflow execution | execution_id={execution_id}")
            
            # Use the executor to run the workflow
            success, result = await self.executor.start_execution(
                workflow_template_id,
                input_parameters,
                triggered_by,
                trigger_context
            )
            
            if success:
                # Wait for execution to complete
                await self._wait_for_execution_completion(execution_id)
                
                # Get final execution status
                final_success, final_result = self.repository.get_workflow_execution(execution_id)
                if final_success:
                    execution = final_result["execution"]
                    return {
                        "success": True,
                        "execution_id": execution_id,
                        "status": execution["status"],
                        "message": "Workflow execution completed"
                    }
                else:
                    return {
                        "success": False,
                        "execution_id": execution_id,
                        "error": "Failed to get final execution status"
                    }
            else:
                return {
                    "success": False,
                    "execution_id": execution_id,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            logfire.error(f"Error in background workflow execution | execution_id={execution_id} | error={str(e)}")
            
            # Update execution status to failed
            try:
                await self.repository.update_workflow_execution(
                    execution_id,
                    {
                        "status": "failed",
                        "error_message": str(e),
                        "completed_at": datetime.now().isoformat()
                    }
                )
            except Exception as update_error:
                logfire.error(f"Failed to update execution status | error={str(update_error)}")
            
            return {
                "success": False,
                "execution_id": execution_id,
                "error": str(e)
            }
    
    async def _wait_for_execution_completion(self, execution_id: str, timeout: int = 3600):
        """Wait for workflow execution to complete"""
        start_time = datetime.now()
        
        while True:
            # Check if execution is still active
            if execution_id not in self.executor.active_executions:
                break
            
            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout:
                logfire.warning(f"Workflow execution timeout | execution_id={execution_id}")
                break
            
            # Wait before checking again
            await asyncio.sleep(5)
    
    def _execution_progress_callback(self, progress: float, message: str = ""):
        """Callback for execution progress updates"""
        logfire.info(f"Workflow execution progress | progress={progress}% | message={message}")

        # Broadcast progress update via WebSocket if available
        if self.websocket_manager:
            # Extract execution_id from message if available
            execution_id = None
            if "execution_id=" in message:
                try:
                    execution_id = message.split("execution_id=")[1].split(" ")[0]
                except:
                    pass

            if execution_id:
                asyncio.create_task(self.websocket_manager.broadcast_to_execution(
                    execution_id,
                    {
                        "type": "progress_update",
                        "data": {
                            "progress_percentage": progress,
                            "message": message
                        }
                    }
                ))
    async def cancel_workflow_execution(self, execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Cancel a workflow execution"""
        try:
            logfire.info(f"Cancelling workflow execution | execution_id={execution_id}")
            
            # Cancel through executor first
            success, result = await self.executor.cancel_execution(execution_id)
            
            # Also cancel background task if it exists
            if execution_id in self.execution_tasks:
                task_id = self.execution_tasks[execution_id]
                try:
                    await self.task_manager.cancel_task(task_id)
                    del self.execution_tasks[execution_id]
                except Exception as e:
                    logfire.warning(f"Failed to cancel background task | task_id={task_id} | error={str(e)}")
            
            # Broadcast cancellation via WebSocket if successful
            if success and self.websocket_manager:
                asyncio.create_task(self.websocket_manager.broadcast_to_execution(
                    execution_id,
                    {
                        "type": "execution_update",
                        "data": {"status": "cancelled", "message": "Execution cancelled"}
                    }
                ))

            return success, result
            
        except Exception as e:
            logfire.error(f"Error cancelling workflow execution | execution_id={execution_id} | error={str(e)}")
            return False, {"error": f"Error cancelling execution: {str(e)}"}
    
    async def pause_workflow_execution(self, execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Pause a workflow execution"""
        try:
            logfire.info(f"Pausing workflow execution | execution_id={execution_id}")
            
            # Pause through executor
            success, result = await self.executor.pause_execution(execution_id)
            
            # Note: Background task manager doesn't support pause/resume,
            # but the executor handles pausing the workflow logic

            # Broadcast pause via WebSocket if successful
            if success and self.websocket_manager:
                asyncio.create_task(self.websocket_manager.broadcast_to_execution(
                    execution_id,
                    {
                        "type": "execution_update",
                        "data": {"status": "paused", "message": "Execution paused"}
                    }
                ))

            return success, result
            
        except Exception as e:
            logfire.error(f"Error pausing workflow execution | execution_id={execution_id} | error={str(e)}")
            return False, {"error": f"Error pausing execution: {str(e)}"}
    
    async def resume_workflow_execution(self, execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Resume a paused workflow execution"""
        try:
            logfire.info(f"Resuming workflow execution | execution_id={execution_id}")
            
            # Resume through executor
            success, result = await self.executor.resume_execution(execution_id)
            
            # Broadcast resume via WebSocket if successful
            if success and self.websocket_manager:
                asyncio.create_task(self.websocket_manager.broadcast_to_execution(
                    execution_id,
                    {
                        "type": "execution_update",
                        "data": {"status": "running", "message": "Execution resumed"}
                    }
                ))

            return success, result
            
        except Exception as e:
            logfire.error(f"Error resuming workflow execution | execution_id={execution_id} | error={str(e)}")
            return False, {"error": f"Error resuming execution: {str(e)}"}
    
    async def get_execution_status(self, execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Get detailed execution status including background task info"""
        try:
            # Get execution from repository
            success, result = self.repository.get_workflow_execution(execution_id)
            if not success:
                return success, result
            
            execution = result["execution"]
            
            # Add background task info if available
            if execution_id in self.execution_tasks:
                task_id = self.execution_tasks[execution_id]
                task_metadata = self.task_manager.get_task_metadata(task_id)
                if task_metadata:
                    execution["background_task"] = {
                        "task_id": task_id,
                        "status": task_metadata.get("status"),
                        "progress": task_metadata.get("progress"),
                        "started_at": task_metadata.get("started_at"),
                        "completed_at": task_metadata.get("completed_at")
                    }
            
            # Get step executions
            step_success, step_result = self.repository.list_step_executions(execution_id)
            step_executions = step_result.get("step_executions", []) if step_success else []
            
            return True, {
                "execution": execution,
                "step_executions": step_executions,
                "total_steps": len(step_executions)
            }
            
        except Exception as e:
            logfire.error(f"Error getting execution status | execution_id={execution_id} | error={str(e)}")
            return False, {"error": f"Error getting execution status: {str(e)}"}
    
    async def list_active_executions(self) -> List[Dict[str, Any]]:
        """List all active workflow executions"""
        try:
            active_executions = []
            
            # Get executions from executor
            for execution_id, context in self.executor.active_executions.items():
                execution_info = {
                    "execution_id": execution_id,
                    "workflow_name": context.workflow_template.name,
                    "current_step_index": context.current_step_index,
                    "total_steps": len(context.workflow_template.steps),
                    "is_paused": context.is_paused,
                    "is_cancelled": context.is_cancelled
                }
                
                # Add background task info if available
                if execution_id in self.execution_tasks:
                    task_id = self.execution_tasks[execution_id]
                    task_metadata = self.task_manager.get_task_metadata(task_id)
                    if task_metadata:
                        execution_info["background_task"] = {
                            "task_id": task_id,
                            "status": task_metadata.get("status"),
                            "progress": task_metadata.get("progress")
                        }
                
                active_executions.append(execution_info)
            
            return active_executions
            
        except Exception as e:
            logfire.error(f"Error listing active executions | error={str(e)}")
            return []
    
    async def cleanup_completed_executions(self):
        """Clean up completed execution tracking"""
        try:
            completed_tasks = []
            
            for execution_id, task_id in self.execution_tasks.items():
                task_metadata = self.task_manager.get_task_metadata(task_id)
                if task_metadata and task_metadata.get("status") in ["complete", "failed", "cancelled"]:
                    completed_tasks.append(execution_id)
            
            for execution_id in completed_tasks:
                del self.execution_tasks[execution_id]
                logfire.info(f"Cleaned up completed execution tracking | execution_id={execution_id}")
            
        except Exception as e:
            logfire.error(f"Error cleaning up completed executions | error={str(e)}")


# Global workflow execution service instance
_workflow_execution_service: Optional[WorkflowExecutionService] = None


def get_workflow_execution_service() -> WorkflowExecutionService:
    """Get or create the global workflow execution service instance"""
    global _workflow_execution_service
    
    if _workflow_execution_service is None:
        _workflow_execution_service = WorkflowExecutionService()
    
    return _workflow_execution_service
