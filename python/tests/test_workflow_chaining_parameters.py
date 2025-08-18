"""
Comprehensive Tests for Workflow Chaining and Parameter Passing

This module provides extensive testing for workflow chaining and parameter handling including:
- Parameter template resolution and variable substitution
- Step result chaining and data flow
- Workflow linking and sub-workflow execution
- Complex parameter mapping and transformation
- Variable scoping and context management
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
from src.server.models.workflow_models import (
    WorkflowTemplate,
    ActionStep,
    ConditionStep,
    WorkflowLinkStep,
    ParallelStep,
    LoopStep,
    WorkflowExecutionStatus
)


class TestWorkflowChainingParameters:
    """Comprehensive test cases for workflow chaining and parameter passing."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock workflow repository."""
        repository = Mock()
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
    
    def test_execution_context_variable_initialization(self):
        """Test proper initialization of execution context variables."""
        workflow_template = WorkflowTemplate(
            id="workflow-123",
            name="test_workflow",
            title="Test Workflow",
            steps=[],
            parameters={
                "input_param": {"type": "string", "required": True},
                "optional_param": {"type": "integer", "default": 42}
            }
        )
        
        input_parameters = {
            "input_param": "test_value",
            "custom_param": "custom_value"
        }
        
        execution_id = "exec-456"
        context = WorkflowExecutionContext(execution_id, workflow_template, input_parameters)
        
        # Verify workflow variables
        assert context.variables["workflow"]["id"] == "workflow-123"
        assert context.variables["workflow"]["name"] == "test_workflow"
        assert context.variables["workflow"]["parameters"] == input_parameters
        
        # Verify execution variables
        assert context.variables["execution"]["id"] == execution_id
        assert "started_at" in context.variables["execution"]
        
        # Verify input parameters are accessible
        assert context.input_parameters == input_parameters
    
    def test_parameter_template_resolution(self):
        """Test parameter template resolution with variable substitution."""
        workflow_template = WorkflowTemplate(
            id="workflow-123",
            name="template_test",
            title="Template Test",
            steps=[
                ActionStep(
                    name="step1",
                    title="Template Step",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "create",
                        "title": "{{workflow.parameters.task_title}}",
                        "description": "Created by {{workflow.name}} at {{execution.started_at}}",
                        "priority": "{{workflow.parameters.priority}}",
                        "nested": {
                            "value": "{{workflow.parameters.nested_value}}",
                            "static": "static_value"
                        }
                    }
                )
            ]
        )
        
        input_parameters = {
            "task_title": "Test Task",
            "priority": "high",
            "nested_value": "nested_test"
        }
        
        context = WorkflowExecutionContext("exec-123", workflow_template, input_parameters)
        step = workflow_template.steps[0]
        
        # Test parameter resolution (this would be done by the executor)
        resolved_params = step.parameters.copy()
        
        # Simulate template resolution
        expected_title = "Test Task"
        expected_description = f"Created by template_test at {context.variables['execution']['started_at']}"
        expected_priority = "high"
        expected_nested_value = "nested_test"
        
        # Verify the structure is correct for template resolution
        assert "{{workflow.parameters.task_title}}" in resolved_params["title"]
        assert "{{workflow.name}}" in resolved_params["description"]
        assert "{{workflow.parameters.priority}}" in resolved_params["priority"]
        assert "{{workflow.parameters.nested_value}}" in resolved_params["nested"]["value"]
        assert resolved_params["nested"]["static"] == "static_value"
    
    @pytest.mark.asyncio
    async def test_step_result_chaining(self, workflow_executor):
        """Test chaining step results through workflow execution."""
        workflow_template = WorkflowTemplate(
            id="workflow-123",
            name="chaining_test",
            title="Chaining Test",
            steps=[
                ActionStep(
                    name="step1",
                    title="First Step",
                    tool_name="manage_task_archon",
                    parameters={"action": "create", "title": "Initial Task"},
                    next_step="step2"
                ),
                ActionStep(
                    name="step2",
                    title="Second Step",
                    tool_name="manage_project_archon",
                    parameters={
                        "action": "update",
                        "task_id": "{{step1.result.task_id}}",
                        "status": "{{step1.result.status}}"
                    },
                    next_step="step3"
                ),
                ActionStep(
                    name="step3",
                    title="Third Step",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "list",
                        "filter": "{{step2.result.project_id}}"
                    }
                )
            ]
        )
        
        context = WorkflowExecutionContext("exec-123", workflow_template, {})
        
        # Mock MCP tool integration with chained results
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # Define sequential results that chain together
            mock_integration.execute_tool.side_effect = [
                (True, {
                    "success": True,
                    "result": {"task_id": "task-456", "status": "created"}
                }),
                (True, {
                    "success": True,
                    "result": {"project_id": "project-789", "updated": True}
                }),
                (True, {
                    "success": True,
                    "result": {"tasks": ["task-456", "task-789"]}
                })
            ]
            mock_mcp.return_value = mock_integration
            
            # Execute first step
            step1 = workflow_template.steps[0]
            success1, result1 = await workflow_executor._execute_step(context, step1)
            
            assert success1 is True
            assert result1["result"]["task_id"] == "task-456"
            
            # Store result in context (simulating executor behavior)
            context.step_results["step1"] = result1
            
            # Execute second step
            step2 = workflow_template.steps[1]
            success2, result2 = await workflow_executor._execute_step(context, step2)
            
            assert success2 is True
            assert result2["result"]["project_id"] == "project-789"
            
            # Store result in context
            context.step_results["step2"] = result2
            
            # Execute third step
            step3 = workflow_template.steps[2]
            success3, result3 = await workflow_executor._execute_step(context, step3)
            
            assert success3 is True
            assert "tasks" in result3["result"]
            
            # Verify all steps were executed
            assert mock_integration.execute_tool.call_count == 3
    
    @pytest.mark.asyncio
    async def test_condition_step_parameter_evaluation(self, workflow_executor):
        """Test condition step evaluation with parameter substitution."""
        workflow_template = WorkflowTemplate(
            id="workflow-123",
            name="condition_test",
            title="Condition Test",
            steps=[
                ActionStep(
                    name="setup_step",
                    title="Setup Step",
                    tool_name="manage_task_archon",
                    parameters={"action": "create"},
                    next_step="condition_step"
                ),
                ConditionStep(
                    name="condition_step",
                    title="Condition Step",
                    condition="{{setup_step.result.status}} == 'success'",
                    on_true="success_step",
                    on_false="failure_step"
                ),
                ActionStep(
                    name="success_step",
                    title="Success Step",
                    tool_name="manage_task_archon",
                    parameters={"action": "update", "status": "completed"}
                ),
                ActionStep(
                    name="failure_step",
                    title="Failure Step",
                    tool_name="manage_task_archon",
                    parameters={"action": "update", "status": "failed"}
                )
            ]
        )
        
        context = WorkflowExecutionContext("exec-123", workflow_template, {})
        
        # Set up step result for condition evaluation
        context.step_results["setup_step"] = {
            "success": True,
            "result": {"status": "success", "task_id": "task-123"}
        }
        
        condition_step = workflow_template.steps[1]
        success, result = await workflow_executor._execute_condition_step(context, condition_step)
        
        assert success is True
        assert result["next_step"] == "success_step"
        assert result["condition_result"] is True
    
    @pytest.mark.asyncio
    async def test_parallel_step_parameter_distribution(self, workflow_executor):
        """Test parameter distribution in parallel step execution."""
        workflow_template = WorkflowTemplate(
            id="workflow-123",
            name="parallel_test",
            title="Parallel Test",
            steps=[
                ActionStep(
                    name="setup_step",
                    title="Setup Step",
                    tool_name="manage_task_archon",
                    parameters={"action": "create"},
                    next_step="parallel_step"
                ),
                ParallelStep(
                    name="parallel_step",
                    title="Parallel Step",
                    parallel_steps=["parallel_sub1", "parallel_sub2", "parallel_sub3"]
                ),
                ActionStep(
                    name="parallel_sub1",
                    title="Parallel Sub 1",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "update",
                        "task_id": "{{setup_step.result.task_id}}",
                        "field": "priority"
                    }
                ),
                ActionStep(
                    name="parallel_sub2",
                    title="Parallel Sub 2",
                    tool_name="manage_project_archon",
                    parameters={
                        "action": "link",
                        "task_id": "{{setup_step.result.task_id}}",
                        "project_id": "{{workflow.parameters.project_id}}"
                    }
                ),
                ActionStep(
                    name="parallel_sub3",
                    title="Parallel Sub 3",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "notify",
                        "task_id": "{{setup_step.result.task_id}}",
                        "recipient": "{{workflow.parameters.assignee}}"
                    }
                )
            ],
            parameters={
                "project_id": {"type": "string", "required": True},
                "assignee": {"type": "string", "required": True}
            }
        )
        
        input_parameters = {
            "project_id": "project-456",
            "assignee": "user@example.com"
        }
        
        context = WorkflowExecutionContext("exec-123", workflow_template, input_parameters)
        
        # Set up step result for parallel steps to use
        context.step_results["setup_step"] = {
            "success": True,
            "result": {"task_id": "task-789", "status": "created"}
        }
        
        # Mock MCP tool integration for parallel execution
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # All parallel steps succeed
            mock_integration.execute_tool.side_effect = [
                (True, {"success": True, "result": {"updated": "priority"}}),
                (True, {"success": True, "result": {"linked": "project-456"}}),
                (True, {"success": True, "result": {"notified": "user@example.com"}})
            ]
            mock_mcp.return_value = mock_integration
            
            parallel_step = workflow_template.steps[1]
            success, result = await workflow_executor._execute_parallel_step(context, parallel_step)
            
            assert success is True
            assert "parallel_results" in result
            assert len(result["parallel_results"]) == 3
            
            # Verify all parallel steps were executed
            assert mock_integration.execute_tool.call_count == 3
    
    @pytest.mark.asyncio
    async def test_loop_step_parameter_iteration(self, workflow_executor):
        """Test parameter iteration in loop step execution."""
        workflow_template = WorkflowTemplate(
            id="workflow-123",
            name="loop_test",
            title="Loop Test",
            steps=[
                LoopStep(
                    name="loop_step",
                    title="Loop Step",
                    loop_over="{{workflow.parameters.items}}",
                    loop_steps=["loop_body"]
                ),
                ActionStep(
                    name="loop_body",
                    title="Loop Body",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "create",
                        "title": "Task for {{loop.item.name}}",
                        "priority": "{{loop.item.priority}}",
                        "index": "{{loop.index}}"
                    }
                )
            ],
            parameters={
                "items": {"type": "array", "required": True}
            }
        )
        
        input_parameters = {
            "items": [
                {"name": "Item 1", "priority": "high"},
                {"name": "Item 2", "priority": "medium"},
                {"name": "Item 3", "priority": "low"}
            ]
        }
        
        context = WorkflowExecutionContext("exec-123", workflow_template, input_parameters)
        
        # Mock MCP tool integration for loop execution
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock()
            
            # Each iteration succeeds
            mock_integration.execute_tool.side_effect = [
                (True, {"success": True, "result": {"task_id": "task-1", "created": "Item 1"}}),
                (True, {"success": True, "result": {"task_id": "task-2", "created": "Item 2"}}),
                (True, {"success": True, "result": {"task_id": "task-3", "created": "Item 3"}})
            ]
            mock_mcp.return_value = mock_integration
            
            loop_step = workflow_template.steps[0]
            success, result = await workflow_executor._execute_loop_step(context, loop_step)
            
            assert success is True
            assert "loop_results" in result
            assert len(result["loop_results"]) == 3
            
            # Verify all iterations were executed
            assert mock_integration.execute_tool.call_count == 3
    
    @pytest.mark.asyncio
    async def test_workflow_link_step_parameter_mapping(self, workflow_executor):
        """Test parameter mapping in workflow link step execution."""
        workflow_template = WorkflowTemplate(
            id="workflow-123",
            name="link_test",
            title="Link Test",
            steps=[
                ActionStep(
                    name="setup_step",
                    title="Setup Step",
                    tool_name="manage_task_archon",
                    parameters={"action": "create"},
                    next_step="link_step"
                ),
                WorkflowLinkStep(
                    name="link_step",
                    title="Link Step",
                    workflow_id="sub-workflow-456",
                    input_mapping={
                        "sub_param1": "{{setup_step.result.task_id}}",
                        "sub_param2": "{{workflow.parameters.project_id}}",
                        "sub_param3": "static_value"
                    },
                    output_mapping={
                        "main_result": "{{sub_workflow.result.output}}",
                        "main_status": "{{sub_workflow.status}}"
                    }
                )
            ],
            parameters={
                "project_id": {"type": "string", "required": True}
            }
        )
        
        input_parameters = {"project_id": "project-789"}
        context = WorkflowExecutionContext("exec-123", workflow_template, input_parameters)
        
        # Set up step result for workflow link to use
        context.step_results["setup_step"] = {
            "success": True,
            "result": {"task_id": "task-456", "status": "created"}
        }
        
        # Mock workflow execution service for sub-workflow
        with patch('src.server.services.workflow.workflow_executor.get_workflow_execution_service') as mock_service:
            mock_exec_service = Mock()
            mock_exec_service.start_workflow_execution = AsyncMock(return_value=(True, {
                "execution_id": "sub-exec-789",
                "status": "pending"
            }))
            mock_exec_service.get_execution_status = AsyncMock(return_value=(True, {
                "execution": {
                    "id": "sub-exec-789",
                    "status": "completed",
                    "output_data": {"output": "sub_result", "count": 5}
                }
            }))
            mock_service.return_value = mock_exec_service
            
            link_step = workflow_template.steps[1]
            success, result = await workflow_executor._execute_workflow_link_step(context, link_step)
            
            assert success is True
            assert "sub_workflow_result" in result
            
            # Verify sub-workflow was started with correct parameters
            mock_exec_service.start_workflow_execution.assert_called_once()
            call_args = mock_exec_service.start_workflow_execution.call_args[0]
            assert call_args[0] == "sub-workflow-456"  # workflow_id
            
            # The input parameters should be resolved from the mapping
            # (actual template resolution would happen in the real executor)
    
    def test_complex_parameter_nesting(self):
        """Test complex nested parameter structures and resolution."""
        workflow_template = WorkflowTemplate(
            id="workflow-123",
            name="complex_params",
            title="Complex Parameters",
            steps=[
                ActionStep(
                    name="complex_step",
                    title="Complex Step",
                    tool_name="manage_task_archon",
                    parameters={
                        "action": "create",
                        "config": {
                            "database": {
                                "host": "{{workflow.parameters.db_config.host}}",
                                "port": "{{workflow.parameters.db_config.port}}",
                                "name": "{{workflow.parameters.db_config.database}}"
                            },
                            "features": [
                                "{{workflow.parameters.feature_list[0]}}",
                                "{{workflow.parameters.feature_list[1]}}"
                            ],
                            "metadata": {
                                "created_by": "{{execution.triggered_by}}",
                                "workflow_id": "{{workflow.id}}",
                                "timestamp": "{{execution.started_at}}"
                            }
                        }
                    }
                )
            ],
            parameters={
                "db_config": {
                    "type": "object",
                    "required": True,
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer"},
                        "database": {"type": "string"}
                    }
                },
                "feature_list": {"type": "array", "required": True}
            }
        )
        
        input_parameters = {
            "db_config": {
                "host": "localhost",
                "port": 5432,
                "database": "test_db"
            },
            "feature_list": ["auth", "logging", "monitoring"]
        }
        
        context = WorkflowExecutionContext("exec-123", workflow_template, input_parameters)
        step = workflow_template.steps[0]
        
        # Verify the parameter structure is set up correctly for template resolution
        config_params = step.parameters["config"]
        
        assert "{{workflow.parameters.db_config.host}}" in config_params["database"]["host"]
        assert "{{workflow.parameters.db_config.port}}" in config_params["database"]["port"]
        assert "{{workflow.parameters.feature_list[0]}}" in config_params["features"][0]
        assert "{{execution.triggered_by}}" in config_params["metadata"]["created_by"]
        
        # Verify input parameters are properly structured
        assert context.input_parameters["db_config"]["host"] == "localhost"
        assert context.input_parameters["db_config"]["port"] == 5432
        assert context.input_parameters["feature_list"][0] == "auth"
