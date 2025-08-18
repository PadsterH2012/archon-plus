"""
Workflow Execution Engine

This module provides the core workflow execution engine that:
- Executes workflow templates step by step
- Manages execution state and progress tracking
- Handles different step types (action, condition, workflow_link, parallel, loop)
- Integrates with MCP tools for action execution
- Provides error handling and retry mechanisms
- Supports async execution for long-running workflows
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from ...config.logfire_config import get_logger, logfire
from ...models.workflow_models import (
    WorkflowTemplate,
    WorkflowExecution,
    WorkflowStepExecution,
    WorkflowStep,
    ActionStep,
    ConditionStep,
    WorkflowLinkStep,
    ParallelStep,
    LoopStep,
    WorkflowExecutionStatus,
    StepExecutionStatus,
    WorkflowStepType,
    create_execution_log_entry,
    calculate_workflow_progress,
    get_next_step_name,
    validate_workflow_template_data
)
from .workflow_repository import WorkflowRepository
from .mcp_tool_integration import get_mcp_workflow_integration
from ...utils import get_supabase_client

logger = get_logger(__name__)


class WorkflowExecutionContext:
    """Context for workflow execution with variable storage and state management"""
    
    def __init__(self, execution_id: str, workflow_template: WorkflowTemplate, input_parameters: Dict[str, Any]):
        self.execution_id = execution_id
        self.workflow_template = workflow_template
        self.input_parameters = input_parameters
        self.variables = {}
        self.step_results = {}
        self.current_step_index = 0
        self.execution_log = []
        self.is_cancelled = False
        self.is_paused = False
        
        # Initialize context variables
        self.variables.update({
            "workflow": {
                "id": workflow_template.id,
                "name": workflow_template.name,
                "parameters": input_parameters
            },
            "execution": {
                "id": execution_id,
                "started_at": datetime.now().isoformat()
            }
        })
    
    def add_log_entry(self, level: str, message: str, step_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Add entry to execution log"""
        log_entry = create_execution_log_entry(level, message, self.current_step_index, step_name, details)
        self.execution_log.append(log_entry)
        
        # Log to system logger as well
        if level == "error":
            logger.error(f"Workflow {self.execution_id} | {message}")
        elif level == "warning":
            logger.warning(f"Workflow {self.execution_id} | {message}")
        else:
            logger.info(f"Workflow {self.execution_id} | {message}")
    
    def set_step_result(self, step_name: str, result: Dict[str, Any]):
        """Store result from step execution"""
        self.step_results[step_name] = result
        self.variables["steps"] = self.step_results
    
    def substitute_variables(self, text: str) -> str:
        """Substitute variables in text using {{variable}} syntax"""
        if not isinstance(text, str):
            return text
        
        import re
        
        def replace_var(match):
            var_path = match.group(1).strip()
            try:
                # Navigate nested variables using dot notation
                value = self.variables
                for part in var_path.split('.'):
                    value = value[part]
                return str(value)
            except (KeyError, TypeError):
                logger.warning(f"Variable not found: {var_path}")
                return match.group(0)  # Return original if not found
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_var, text)
    
    def substitute_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute variables in parameter dictionary"""
        if not isinstance(params, dict):
            return params
        
        result = {}
        for key, value in params.items():
            if isinstance(value, str):
                result[key] = self.substitute_variables(value)
            elif isinstance(value, dict):
                result[key] = self.substitute_parameters(value)
            elif isinstance(value, list):
                result[key] = [self.substitute_variables(item) if isinstance(item, str) else item for item in value]
            else:
                result[key] = value
        
        return result


class WorkflowExecutor:
    """Core workflow execution engine"""
    
    def __init__(self, repository: Optional[WorkflowRepository] = None):
        """Initialize workflow executor"""
        self.repository = repository or WorkflowRepository(get_supabase_client())
        self.active_executions: Dict[str, WorkflowExecutionContext] = {}
        self._execution_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_execution(
        self, 
        workflow_template_id: str, 
        input_parameters: Dict[str, Any],
        triggered_by: str = "system",
        trigger_context: Dict[str, Any] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Start workflow execution.
        
        Args:
            workflow_template_id: UUID of workflow template to execute
            input_parameters: Input parameters for the workflow
            triggered_by: Who triggered the execution
            trigger_context: Additional context for the execution
            
        Returns:
            Tuple of (success, result_dict)
        """
        try:
            logfire.info(f"Starting workflow execution | template_id={workflow_template_id} | triggered_by={triggered_by}")
            
            # Get workflow template
            template_success, template_result = self.repository.get_workflow_template(workflow_template_id)
            if not template_success:
                return False, template_result
            
            template_data = template_result["template"]
            workflow_template = validate_workflow_template_data(template_data)
            
            # Create execution record
            execution_data = {
                "workflow_template_id": workflow_template_id,
                "triggered_by": triggered_by,
                "trigger_context": trigger_context or {},
                "input_parameters": input_parameters,
                "status": WorkflowExecutionStatus.PENDING.value,
                "total_steps": len(workflow_template.steps)
            }
            
            exec_success, exec_result = await self.repository.create_workflow_execution(execution_data)
            if not exec_success:
                return False, exec_result
            
            execution = exec_result["execution"]
            execution_id = execution["id"]
            
            # Create execution context
            context = WorkflowExecutionContext(execution_id, workflow_template, input_parameters)
            self.active_executions[execution_id] = context
            
            # Start execution in background
            task = asyncio.create_task(self._execute_workflow(context))
            self._execution_tasks[execution_id] = task
            
            logfire.info(f"Workflow execution started | execution_id={execution_id}")
            
            return True, {
                "execution_id": execution_id,
                "status": "pending",
                "message": "Workflow execution started"
            }
            
        except Exception as e:
            logfire.error(f"Error starting workflow execution | error={str(e)}")
            return False, {"error": f"Error starting workflow execution: {str(e)}"}
    
    async def _execute_workflow(self, context: WorkflowExecutionContext):
        """Execute workflow steps in sequence"""
        try:
            # Update execution status to running
            await self.repository.update_workflow_execution(
                context.execution_id,
                {
                    "status": WorkflowExecutionStatus.RUNNING,
                    "started_at": datetime.now().isoformat()
                }
            )
            
            context.add_log_entry("info", f"Starting workflow execution: {context.workflow_template.title}")
            
            # Execute steps
            step_names = [step.name for step in context.workflow_template.steps]
            current_step_name = step_names[0] if step_names else None
            
            while current_step_name and not context.is_cancelled:
                if context.is_paused:
                    await asyncio.sleep(1)  # Wait while paused
                    continue
                
                # Find step by name
                step = next((s for s in context.workflow_template.steps if s.name == current_step_name), None)
                if not step:
                    context.add_log_entry("error", f"Step not found: {current_step_name}")
                    break
                
                # Execute step
                step_success, step_result = await self._execute_step(context, step)
                
                # Update progress
                progress = calculate_workflow_progress(
                    context.current_step_index + 1,
                    len(context.workflow_template.steps)
                )
                
                await self.repository.update_workflow_execution(
                    context.execution_id,
                    {
                        "current_step_index": context.current_step_index + 1,
                        "progress_percentage": progress,
                        "execution_log": context.execution_log
                    }
                )
                
                # Determine next step
                if step_success:
                    current_step_name = get_next_step_name(step, step_result, step_names)
                else:
                    # Handle failure based on step configuration
                    if step.on_failure == "retry" and step_result.get("attempt_number", 1) < step.retry_count:
                        # Retry the same step
                        continue
                    elif step.on_failure == "fail":
                        context.add_log_entry("error", f"Workflow failed at step: {step.name}")
                        await self._complete_execution(context, WorkflowExecutionStatus.FAILED, step_result.get("error"))
                        return
                    else:
                        # Move to failure step or end
                        current_step_name = get_next_step_name(step, step_result, step_names)
                
                context.current_step_index += 1
            
            # Complete execution successfully
            if context.is_cancelled:
                await self._complete_execution(context, WorkflowExecutionStatus.CANCELLED)
            else:
                await self._complete_execution(context, WorkflowExecutionStatus.COMPLETED)
                
        except Exception as e:
            context.add_log_entry("error", f"Workflow execution failed: {str(e)}")
            await self._complete_execution(context, WorkflowExecutionStatus.FAILED, str(e))
    
    async def _execute_step(self, context: WorkflowExecutionContext, step: WorkflowStep) -> Tuple[bool, Dict[str, Any]]:
        """Execute a single workflow step"""
        try:
            context.add_log_entry("info", f"Executing step: {step.name}", step.name)
            
            # Create step execution record
            step_data = {
                "workflow_execution_id": context.execution_id,
                "step_index": context.current_step_index,
                "step_name": step.name,
                "step_type": step.type.value,
                "step_config": step.dict(),
                "status": StepExecutionStatus.RUNNING.value,
                "started_at": datetime.now().isoformat()
            }
            
            step_exec_success, step_exec_result = await self.repository.create_step_execution(step_data)
            if not step_exec_success:
                return False, {"error": "Failed to create step execution record"}
            
            step_execution_id = step_exec_result["step_execution"]["id"]
            
            # Execute based on step type
            if isinstance(step, ActionStep):
                result = await self._execute_action_step(context, step, step_execution_id)
            elif isinstance(step, ConditionStep):
                result = await self._execute_condition_step(context, step, step_execution_id)
            elif isinstance(step, WorkflowLinkStep):
                result = await self._execute_workflow_link_step(context, step, step_execution_id)
            elif isinstance(step, ParallelStep):
                result = await self._execute_parallel_step(context, step, step_execution_id)
            elif isinstance(step, LoopStep):
                result = await self._execute_loop_step(context, step, step_execution_id)
            else:
                result = (False, {"error": f"Unknown step type: {step.type}"})
            
            success, step_result = result
            
            # Update step execution record
            await self.repository.update_step_execution(
                step_execution_id,
                {
                    "status": StepExecutionStatus.COMPLETED.value if success else StepExecutionStatus.FAILED.value,
                    "completed_at": datetime.now().isoformat(),
                    "output_data": step_result,
                    "error_message": step_result.get("error") if not success else None
                }
            )
            
            # Store result in context
            context.set_step_result(step.name, step_result)
            
            if success:
                context.add_log_entry("info", f"Step completed successfully: {step.name}", step.name)
            else:
                context.add_log_entry("error", f"Step failed: {step.name} - {step_result.get('error', 'Unknown error')}", step.name)
            
            return success, step_result
            
        except Exception as e:
            error_msg = f"Error executing step {step.name}: {str(e)}"
            context.add_log_entry("error", error_msg, step.name)
            return False, {"error": error_msg}
    
    async def _execute_action_step(self, context: WorkflowExecutionContext, step: ActionStep, step_execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute an action step by calling MCP tool"""
        try:
            # Substitute variables in parameters
            substituted_params = context.substitute_parameters(step.parameters)

            context.add_log_entry("info", f"Calling tool: {step.tool_name}", step.name, {"parameters": substituted_params})

            # Use MCP workflow integration for tool execution
            mcp_integration = get_mcp_workflow_integration()

            # Execute the tool with full integration support
            success, result = await mcp_integration.execute_workflow_step(
                step.tool_name,
                substituted_params,
                context.variables,
                {
                    "execution_id": context.execution_id,
                    "step_name": step.name,
                    "step_index": context.current_step_index
                }
            )

            # Update step execution with tool details
            await self.repository.update_step_execution(
                step_execution_id,
                {
                    "tool_name": step.tool_name,
                    "tool_parameters": result.get("mapped_parameters", substituted_params),
                    "tool_result": result.get("tool_result", result)
                }
            )

            if success:
                context.add_log_entry("info", f"Tool execution completed: {step.tool_name}", step.name)
                return True, {
                    "success": True,
                    "result": result.get("tool_result", {}),
                    "tool_name": step.tool_name,
                    "execution_info": result.get("execution_info", {})
                }
            else:
                error_msg = result.get("error", "Unknown tool execution error")
                context.add_log_entry("error", f"Tool execution failed: {step.tool_name} - {error_msg}", step.name)
                return False, {
                    "success": False,
                    "error": error_msg,
                    "tool_name": step.tool_name,
                    "validation_errors": result.get("validation_errors", [])
                }

        except Exception as e:
            error_msg = f"Tool execution failed: {step.tool_name} - {str(e)}"
            context.add_log_entry("error", error_msg, step.name)
            return False, {"success": False, "error": error_msg, "tool_name": step.tool_name}
    
    async def _execute_condition_step(self, context: WorkflowExecutionContext, step: ConditionStep, step_execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute a condition step by evaluating the condition"""
        try:
            # Substitute variables in condition
            condition_expr = context.substitute_variables(step.condition)
            
            context.add_log_entry("info", f"Evaluating condition: {condition_expr}", step.name)
            
            # Simple condition evaluation (can be enhanced with safe eval)
            # For now, support basic comparisons
            condition_result = self._evaluate_condition(condition_expr)
            
            context.add_log_entry("info", f"Condition result: {condition_result}", step.name)
            
            return True, {"success": True, "condition_result": condition_result, "condition": condition_expr}
            
        except Exception as e:
            error_msg = f"Condition evaluation failed: {str(e)}"
            context.add_log_entry("error", error_msg, step.name)
            return False, {"success": False, "error": error_msg}
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Safely evaluate a condition expression"""
        # Simple condition evaluation - can be enhanced with a proper expression parser
        # For now, support basic string comparisons
        try:
            # Replace common operators
            condition = condition.replace(" == ", " == ").replace(" != ", " != ")
            
            # Very basic evaluation - in production, use a proper expression evaluator
            if " == " in condition:
                left, right = condition.split(" == ", 1)
                return left.strip().strip('"\'') == right.strip().strip('"\'')
            elif " != " in condition:
                left, right = condition.split(" != ", 1)
                return left.strip().strip('"\'') != right.strip().strip('"\'')
            elif condition.lower() in ["true", "1", "yes"]:
                return True
            elif condition.lower() in ["false", "0", "no"]:
                return False
            else:
                # Default to true for unknown conditions
                return True
                
        except Exception:
            # Default to true if evaluation fails
            return True
    
    async def _execute_workflow_link_step(self, context: WorkflowExecutionContext, step: WorkflowLinkStep, step_execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute a workflow link step by starting a sub-workflow"""
        try:
            # Substitute variables in parameters
            substituted_params = context.substitute_parameters(step.parameters)
            
            context.add_log_entry("info", f"Starting sub-workflow: {step.workflow_name}", step.name)
            
            # Find workflow template by name
            templates_success, templates_result = self.repository.list_workflow_templates(search=step.workflow_name, limit=1)
            if not templates_success or not templates_result["templates"]:
                return False, {"success": False, "error": f"Sub-workflow not found: {step.workflow_name}"}
            
            sub_template = templates_result["templates"][0]
            
            # Start sub-workflow execution
            sub_success, sub_result = await self.start_execution(
                sub_template["id"],
                substituted_params,
                triggered_by=f"workflow:{context.execution_id}",
                trigger_context={"parent_execution_id": context.execution_id, "parent_step": step.name}
            )
            
            if not sub_success:
                return False, {"success": False, "error": f"Failed to start sub-workflow: {sub_result.get('error')}"}
            
            sub_execution_id = sub_result["execution_id"]
            
            # Update step execution with sub-workflow reference
            await self.repository.update_step_execution(
                step_execution_id,
                {"sub_workflow_execution_id": sub_execution_id}
            )
            
            # Wait for sub-workflow completion (simplified - in production, use proper async waiting)
            # For now, return success immediately
            context.add_log_entry("info", f"Sub-workflow started: {sub_execution_id}", step.name)
            
            return True, {"success": True, "sub_workflow_execution_id": sub_execution_id}
            
        except Exception as e:
            error_msg = f"Sub-workflow execution failed: {str(e)}"
            context.add_log_entry("error", error_msg, step.name)
            return False, {"success": False, "error": error_msg}
    
    async def _execute_parallel_step(self, context: WorkflowExecutionContext, step: ParallelStep, step_execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute parallel steps concurrently"""
        try:
            context.add_log_entry("info", f"Starting parallel execution of {len(step.steps)} steps", step.name)
            
            # Execute all sub-steps concurrently
            tasks = []
            for i, sub_step in enumerate(step.steps):
                task = asyncio.create_task(self._execute_step(context, sub_step))
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            success_count = 0
            all_results = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    all_results.append((False, {"error": str(result)}))
                else:
                    success, step_result = result
                    all_results.append((success, step_result))
                    if success:
                        success_count += 1
            
            # Determine overall success based on wait_for_all setting
            overall_success = success_count == len(step.steps) if step.wait_for_all else success_count > 0
            
            context.add_log_entry("info", f"Parallel execution completed: {success_count}/{len(step.steps)} successful", step.name)
            
            return overall_success, {"success": overall_success, "results": all_results, "success_count": success_count}
            
        except Exception as e:
            error_msg = f"Parallel execution failed: {str(e)}"
            context.add_log_entry("error", error_msg, step.name)
            return False, {"success": False, "error": error_msg}
    
    async def _execute_loop_step(self, context: WorkflowExecutionContext, step: LoopStep, step_execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Execute loop step by iterating over collection"""
        try:
            # Get collection to iterate over
            collection_expr = context.substitute_variables(step.collection)
            
            # Simple collection parsing - in production, use proper expression evaluation
            if isinstance(collection_expr, str) and collection_expr.startswith('[') and collection_expr.endswith(']'):
                # Parse simple array syntax
                collection = json.loads(collection_expr)
            else:
                # Assume it's a single item
                collection = [collection_expr]
            
            context.add_log_entry("info", f"Starting loop over {len(collection)} items", step.name)
            
            results = []
            success_count = 0
            
            for i, item in enumerate(collection[:step.max_iterations]):
                # Set loop variable
                context.variables[step.item_variable] = item
                
                # Execute sub-steps for this iteration
                iteration_results = []
                for sub_step in step.steps:
                    success, result = await self._execute_step(context, sub_step)
                    iteration_results.append((success, result))
                    if success:
                        success_count += 1
                
                results.append(iteration_results)
            
            # Clean up loop variable
            if step.item_variable in context.variables:
                del context.variables[step.item_variable]
            
            context.add_log_entry("info", f"Loop completed: {len(results)} iterations", step.name)
            
            return True, {"success": True, "iterations": len(results), "results": results}
            
        except Exception as e:
            error_msg = f"Loop execution failed: {str(e)}"
            context.add_log_entry("error", error_msg, step.name)
            return False, {"success": False, "error": error_msg}
    
    async def _complete_execution(self, context: WorkflowExecutionContext, status: WorkflowExecutionStatus, error_message: Optional[str] = None):
        """Complete workflow execution with final status"""
        try:
            completion_data = {
                "status": status,
                "completed_at": datetime.now().isoformat(),
                "progress_percentage": 100.0 if status == WorkflowExecutionStatus.COMPLETED else context.current_step_index / len(context.workflow_template.steps) * 100,
                "execution_log": context.execution_log,
                "output_data": context.step_results
            }
            
            if error_message:
                completion_data["error_message"] = error_message
            
            await self.repository.update_workflow_execution(context.execution_id, completion_data)
            
            context.add_log_entry("info", f"Workflow execution completed with status: {status.value}")
            
            # Clean up
            if context.execution_id in self.active_executions:
                del self.active_executions[context.execution_id]
            if context.execution_id in self._execution_tasks:
                del self._execution_tasks[context.execution_id]
            
            logfire.info(f"Workflow execution completed | execution_id={context.execution_id} | status={status.value}")
            
        except Exception as e:
            logfire.error(f"Error completing workflow execution | execution_id={context.execution_id} | error={str(e)}")
    
    async def cancel_execution(self, execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Cancel a running workflow execution"""
        try:
            if execution_id in self.active_executions:
                context = self.active_executions[execution_id]
                context.is_cancelled = True
                context.add_log_entry("info", "Workflow execution cancelled by request")
                
                # Cancel the execution task
                if execution_id in self._execution_tasks:
                    self._execution_tasks[execution_id].cancel()
                
                return True, {"message": "Workflow execution cancelled"}
            else:
                # Update database directly if not in active executions
                await self.repository.update_workflow_execution(
                    execution_id,
                    {
                        "status": WorkflowExecutionStatus.CANCELLED,
                        "completed_at": datetime.now().isoformat(),
                        "error_message": "Execution cancelled by user request"
                    }
                )
                return True, {"message": "Workflow execution cancelled"}
                
        except Exception as e:
            logfire.error(f"Error cancelling workflow execution | execution_id={execution_id} | error={str(e)}")
            return False, {"error": f"Error cancelling execution: {str(e)}"}
    
    async def pause_execution(self, execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Pause a running workflow execution"""
        try:
            if execution_id in self.active_executions:
                context = self.active_executions[execution_id]
                context.is_paused = True
                context.add_log_entry("info", "Workflow execution paused")
                
                await self.repository.update_workflow_execution(
                    execution_id,
                    {
                        "status": WorkflowExecutionStatus.PAUSED,
                        "paused_at": datetime.now().isoformat()
                    }
                )
                
                return True, {"message": "Workflow execution paused"}
            else:
                return False, {"error": "Execution not found or not running"}
                
        except Exception as e:
            logfire.error(f"Error pausing workflow execution | execution_id={execution_id} | error={str(e)}")
            return False, {"error": f"Error pausing execution: {str(e)}"}
    
    async def resume_execution(self, execution_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Resume a paused workflow execution"""
        try:
            if execution_id in self.active_executions:
                context = self.active_executions[execution_id]
                context.is_paused = False
                context.add_log_entry("info", "Workflow execution resumed")
                
                await self.repository.update_workflow_execution(
                    execution_id,
                    {
                        "status": WorkflowExecutionStatus.RUNNING,
                        "paused_at": None
                    }
                )
                
                return True, {"message": "Workflow execution resumed"}
            else:
                return False, {"error": "Execution not found or not paused"}
                
        except Exception as e:
            logfire.error(f"Error resuming workflow execution | execution_id={execution_id} | error={str(e)}")
            return False, {"error": f"Error resuming execution: {str(e)}"}


# Global workflow executor instance
_workflow_executor: Optional[WorkflowExecutor] = None


def get_workflow_executor() -> WorkflowExecutor:
    """Get or create the global workflow executor instance"""
    global _workflow_executor
    
    if _workflow_executor is None:
        _workflow_executor = WorkflowExecutor()
    
    return _workflow_executor
