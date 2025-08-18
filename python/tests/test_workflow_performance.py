"""
Performance Tests for Workflow Engine

This module provides performance testing for the workflow system including:
- Large workflow execution performance
- Memory usage and resource management
- Concurrent workflow execution
- Scalability testing with multiple steps
- Performance benchmarking and profiling
"""

import pytest
import asyncio
import time
import psutil
import os
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime
from typing import List

from src.server.services.workflow.workflow_executor import (
    WorkflowExecutor,
    WorkflowExecutionContext
)
from src.server.services.workflow.workflow_execution_service import WorkflowExecutionService
from src.server.models.workflow_models import (
    WorkflowTemplate,
    ActionStep,
    ParallelStep,
    LoopStep,
    WorkflowExecutionStatus
)


class TestWorkflowPerformance:
    """Performance test cases for workflow engine."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock workflow repository with fast responses."""
        repository = Mock()
        repository.create_workflow_execution = AsyncMock(return_value=(True, {
            "execution": {"id": "exec-123", "status": "pending"}
        }))
        repository.update_workflow_execution = AsyncMock(return_value=(True, {}))
        repository.create_step_execution = AsyncMock(return_value=(True, {
            "step_execution": {"id": "step-exec-123"}
        }))
        repository.update_step_execution = AsyncMock(return_value=(True, {}))
        repository.get_workflow_template = AsyncMock()
        return repository
    
    @pytest.fixture
    def fast_mock_mcp(self):
        """Mock MCP integration with fast responses."""
        with patch('src.server.services.workflow.workflow_executor.get_mcp_workflow_integration') as mock_mcp:
            mock_integration = Mock()
            mock_integration.execute_tool = AsyncMock(return_value=(True, {
                "success": True,
                "result": {"processed": True, "timestamp": datetime.now().isoformat()}
            }))
            mock_mcp.return_value = mock_integration
            yield mock_integration
    
    def create_large_sequential_workflow(self, step_count: int) -> WorkflowTemplate:
        """Create a workflow with many sequential steps."""
        steps = []
        for i in range(step_count):
            step = ActionStep(
                name=f"step_{i}",
                title=f"Step {i}",
                tool_name="manage_task_archon",
                parameters={
                    "action": "create",
                    "title": f"Task {i}",
                    "index": i
                },
                next_step=f"step_{i+1}" if i < step_count - 1 else "end"
            )
            steps.append(step)
        
        return WorkflowTemplate(
            id=str(uuid4()),
            name=f"large_workflow_{step_count}",
            title=f"Large Workflow with {step_count} Steps",
            steps=steps
        )
    
    def create_large_parallel_workflow(self, parallel_count: int) -> WorkflowTemplate:
        """Create a workflow with many parallel steps."""
        # Create parallel substeps
        parallel_steps = []
        for i in range(parallel_count):
            step = ActionStep(
                name=f"parallel_step_{i}",
                title=f"Parallel Step {i}",
                tool_name="manage_task_archon",
                parameters={
                    "action": "create",
                    "title": f"Parallel Task {i}",
                    "index": i
                }
            )
            parallel_steps.append(step)
        
        # Create main parallel step
        main_parallel = ParallelStep(
            name="main_parallel",
            title="Main Parallel Step",
            parallel_steps=[step.name for step in parallel_steps]
        )
        
        # Combine all steps
        all_steps = [main_parallel] + parallel_steps
        
        return WorkflowTemplate(
            id=str(uuid4()),
            name=f"parallel_workflow_{parallel_count}",
            title=f"Parallel Workflow with {parallel_count} Steps",
            steps=all_steps
        )
    
    def create_large_loop_workflow(self, loop_iterations: int) -> WorkflowTemplate:
        """Create a workflow with a large loop."""
        loop_body = ActionStep(
            name="loop_body",
            title="Loop Body Step",
            tool_name="manage_task_archon",
            parameters={
                "action": "create",
                "title": "Loop Task {{loop.index}}",
                "item": "{{loop.item}}"
            }
        )
        
        loop_step = LoopStep(
            name="main_loop",
            title="Main Loop Step",
            loop_over="{{workflow.parameters.items}}",
            loop_steps=["loop_body"]
        )
        
        return WorkflowTemplate(
            id=str(uuid4()),
            name=f"loop_workflow_{loop_iterations}",
            title=f"Loop Workflow with {loop_iterations} Iterations",
            steps=[loop_step, loop_body],
            parameters={
                "items": {"type": "array", "required": True}
            }
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_large_sequential_workflow_performance(self, mock_repository, fast_mock_mcp):
        """Test performance of large sequential workflow execution."""
        step_count = 100
        workflow_template = self.create_large_sequential_workflow(step_count)
        
        executor = WorkflowExecutor(repository=mock_repository)
        context = WorkflowExecutionContext("exec-123", workflow_template, {})
        
        # Measure execution time
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        # Execute workflow steps sequentially
        for i, step in enumerate(workflow_template.steps):
            success, result = await executor._execute_step(context, step)
            assert success is True
            context.step_results[step.name] = result
            
            # Update progress
            context.current_step_index = i + 1
        
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        # Performance assertions
        assert execution_time < 10.0  # Should complete within 10 seconds
        assert memory_usage < 50.0   # Should not use more than 50MB additional memory
        
        # Verify all steps were executed
        assert fast_mock_mcp.execute_tool.call_count == step_count
        assert len(context.step_results) == step_count
        
        print(f"Sequential workflow ({step_count} steps): {execution_time:.2f}s, {memory_usage:.2f}MB")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_large_parallel_workflow_performance(self, mock_repository, fast_mock_mcp):
        """Test performance of large parallel workflow execution."""
        parallel_count = 50
        workflow_template = self.create_large_parallel_workflow(parallel_count)
        
        executor = WorkflowExecutor(repository=mock_repository)
        context = WorkflowExecutionContext("exec-123", workflow_template, {})
        
        # Measure execution time
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        # Execute parallel step
        parallel_step = workflow_template.steps[0]  # Main parallel step
        success, result = await executor._execute_parallel_step(context, parallel_step)
        
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        # Performance assertions
        assert success is True
        assert execution_time < 5.0   # Parallel execution should be faster
        assert memory_usage < 100.0  # May use more memory for parallel execution
        
        # Verify all parallel steps were executed
        assert fast_mock_mcp.execute_tool.call_count == parallel_count
        
        print(f"Parallel workflow ({parallel_count} steps): {execution_time:.2f}s, {memory_usage:.2f}MB")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_large_loop_workflow_performance(self, mock_repository, fast_mock_mcp):
        """Test performance of workflow with large loop."""
        loop_iterations = 200
        workflow_template = self.create_large_loop_workflow(loop_iterations)
        
        # Create input parameters with many items
        input_parameters = {
            "items": [f"item_{i}" for i in range(loop_iterations)]
        }
        
        executor = WorkflowExecutor(repository=mock_repository)
        context = WorkflowExecutionContext("exec-123", workflow_template, input_parameters)
        
        # Measure execution time
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        # Execute loop step
        loop_step = workflow_template.steps[0]  # Main loop step
        success, result = await executor._execute_loop_step(context, loop_step)
        
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        # Performance assertions
        assert success is True
        assert execution_time < 15.0  # Should complete within 15 seconds
        assert memory_usage < 75.0   # Should not use excessive memory
        
        # Verify all loop iterations were executed
        assert fast_mock_mcp.execute_tool.call_count == loop_iterations
        
        print(f"Loop workflow ({loop_iterations} iterations): {execution_time:.2f}s, {memory_usage:.2f}MB")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_workflow_executions(self, mock_repository, fast_mock_mcp):
        """Test performance of multiple concurrent workflow executions."""
        workflow_count = 10
        steps_per_workflow = 20
        
        # Create multiple workflow templates
        workflows = []
        for i in range(workflow_count):
            workflow = self.create_large_sequential_workflow(steps_per_workflow)
            workflows.append(workflow)
        
        executor = WorkflowExecutor(repository=mock_repository)
        
        # Measure execution time
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        # Execute workflows concurrently
        async def execute_workflow(workflow_template):
            context = WorkflowExecutionContext(str(uuid4()), workflow_template, {})
            for step in workflow_template.steps:
                success, result = await executor._execute_step(context, step)
                assert success is True
                context.step_results[step.name] = result
            return context
        
        # Run all workflows concurrently
        tasks = [execute_workflow(workflow) for workflow in workflows]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        # Performance assertions
        assert len(results) == workflow_count
        assert execution_time < 20.0  # Should complete within 20 seconds
        assert memory_usage < 200.0  # Should not use excessive memory
        
        # Verify all steps were executed across all workflows
        total_expected_calls = workflow_count * steps_per_workflow
        assert fast_mock_mcp.execute_tool.call_count == total_expected_calls
        
        print(f"Concurrent workflows ({workflow_count} x {steps_per_workflow} steps): {execution_time:.2f}s, {memory_usage:.2f}MB")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_workflow_execution_service_performance(self, mock_repository, fast_mock_mcp):
        """Test performance of workflow execution service with background tasks."""
        workflow_template = self.create_large_sequential_workflow(50)
        
        # Mock task manager
        mock_task_manager = Mock()
        mock_task_manager.submit_task = AsyncMock(return_value="task-123")
        
        execution_service = WorkflowExecutionService(
            repository=mock_repository,
            task_manager=mock_task_manager
        )
        
        # Measure execution time for service operations
        start_time = time.time()
        
        # Start multiple background executions
        execution_count = 5
        execution_results = []
        
        for i in range(execution_count):
            success, result = await execution_service.start_workflow_execution(
                workflow_template.id,
                {"test_param": f"value_{i}"},
                "test_user",
                background=True
            )
            assert success is True
            execution_results.append(result)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertions
        assert execution_time < 2.0  # Service operations should be fast
        assert len(execution_results) == execution_count
        
        # Verify all executions were submitted to task manager
        assert mock_task_manager.submit_task.call_count == execution_count
        
        print(f"Execution service ({execution_count} background executions): {execution_time:.2f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_memory_cleanup_after_execution(self, mock_repository, fast_mock_mcp):
        """Test that memory is properly cleaned up after workflow execution."""
        workflow_template = self.create_large_sequential_workflow(100)
        
        executor = WorkflowExecutor(repository=mock_repository)
        
        # Measure initial memory
        initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        # Execute multiple workflows to test cleanup
        for i in range(5):
            execution_id = f"exec-{i}"
            context = WorkflowExecutionContext(execution_id, workflow_template, {})
            
            # Add to active executions
            executor.active_executions[execution_id] = context
            
            # Execute some steps
            for j, step in enumerate(workflow_template.steps[:10]):  # Execute first 10 steps
                success, result = await executor._execute_step(context, step)
                assert success is True
                context.step_results[step.name] = result
            
            # Complete execution (cleanup)
            await executor._complete_execution(context, WorkflowExecutionStatus.COMPLETED)
        
        # Measure final memory
        final_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be minimal after cleanup
        assert memory_growth < 20.0  # Should not grow by more than 20MB
        
        # Verify active executions were cleaned up
        assert len(executor.active_executions) == 0
        
        print(f"Memory cleanup test: {memory_growth:.2f}MB growth after 5 executions")
    
    @pytest.mark.performance
    def test_workflow_validation_performance(self):
        """Test performance of workflow validation for large workflows."""
        from src.server.models.workflow_validation import WorkflowValidator
        
        # Create a complex workflow for validation
        step_count = 500
        workflow_template = self.create_large_sequential_workflow(step_count)
        
        validator = WorkflowValidator()
        
        # Measure validation time
        start_time = time.time()
        
        result = validator.validate(workflow_template)
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        # Performance assertions
        assert validation_time < 5.0  # Validation should be fast even for large workflows
        assert result.is_valid is True
        
        print(f"Workflow validation ({step_count} steps): {validation_time:.2f}s")
