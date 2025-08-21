"""
Performance Tests for Template Injection System

This test suite validates performance targets and benchmarks for the
template injection system under various load conditions.
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from src.server.services.template_injection_service import TemplateInjectionService
from src.server.services.projects.task_service import TaskService


class TestTemplateInjectionPerformance:
    """Performance tests for template injection system"""

    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client optimized for performance testing"""
        mock_client = MagicMock()
        
        # Mock template definition
        mock_template = {
            "id": str(uuid4()),
            "name": "workflow_default",
            "title": "Default Template Injection Workflow",
            "template_type": "project",
            "template_data": {
                "template_content": "{{group::prep}}\n\n{{USER_TASK}}\n\n{{group::test}}\n\n{{group::deploy}}",
                "user_task_position": 2,
                "estimated_duration": 30
            },
            "is_active": True,
            "created_at": "2025-08-20T10:00:00Z"
        }
        
        # Mock components
        mock_components = [
            {
                "id": str(uuid4()),
                "name": "group::prep",
                "instruction_text": "Prepare for implementation by reviewing requirements and dependencies.",
                "component_type": "group",
                "estimated_duration": 5,
                "is_active": True
            },
            {
                "id": str(uuid4()),
                "name": "group::test",
                "instruction_text": "Create and run comprehensive tests to validate implementation.",
                "component_type": "group",
                "estimated_duration": 10,
                "is_active": True
            },
            {
                "id": str(uuid4()),
                "name": "group::deploy",
                "instruction_text": "Deploy and validate the implementation in target environment.",
                "component_type": "group",
                "estimated_duration": 8,
                "is_active": True
            }
        ]
        
        def mock_table_call(table_name):
            if table_name == "archon_template_definitions":
                mock_template_table = MagicMock()
                mock_template_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_template]
                return mock_template_table
            elif table_name == "archon_template_components":
                mock_component_table = MagicMock()
                # Return specific component based on query
                def mock_component_query(*args, **kwargs):
                    mock_query = MagicMock()
                    mock_query.eq.return_value.eq.return_value.execute.return_value.data = mock_components
                    return mock_query
                mock_component_table.select.return_value = mock_component_query()
                return mock_component_table
            return MagicMock()
        
        mock_client.table.side_effect = mock_table_call
        return mock_client

    @pytest.fixture
    def template_service(self, mock_supabase_client):
        """Create TemplateInjectionService for performance testing"""
        return TemplateInjectionService(supabase_client=mock_supabase_client)

    @pytest.mark.asyncio
    async def test_template_expansion_performance_target(self, template_service):
        """Test that template expansion meets <100ms target"""
        
        original_description = "Implement user authentication system"
        
        # Measure expansion time
        start_time = time.time()
        response = await template_service.expand_task_description(
            original_description=original_description,
            template_name="workflow_default"
        )
        duration_ms = (time.time() - start_time) * 1000
        
        # Verify success and performance target
        assert response.success is True
        assert duration_ms < 100, f"Template expansion took {duration_ms:.2f}ms, target is <100ms"
        
        # Verify expansion time is reported correctly
        assert response.result.expansion_time_ms < 100

    @pytest.mark.asyncio
    async def test_concurrent_template_expansions(self, template_service):
        """Test performance under concurrent load"""
        
        async def expand_template(task_id):
            """Single template expansion task"""
            start_time = time.time()
            response = await template_service.expand_task_description(
                original_description=f"Task {task_id}: Implement feature",
                template_name="workflow_default"
            )
            duration = (time.time() - start_time) * 1000
            return response.success, duration
        
        # Run 20 concurrent expansions
        concurrent_tasks = 20
        tasks = [expand_template(i) for i in range(concurrent_tasks)]
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        successes = [r[0] for r in results]
        durations = [r[1] for r in results]
        
        # Verify all succeeded
        assert all(successes), "Some template expansions failed under concurrent load"
        
        # Verify performance under load
        avg_duration = statistics.mean(durations)
        max_duration = max(durations)
        
        assert avg_duration < 150, f"Average duration {avg_duration:.2f}ms exceeds target under load"
        assert max_duration < 300, f"Max duration {max_duration:.2f}ms too high under load"
        
        print(f"Concurrent performance: avg={avg_duration:.2f}ms, max={max_duration:.2f}ms")

    @pytest.mark.asyncio
    async def test_template_caching_performance(self, template_service):
        """Test caching performance improvement"""
        
        original_description = "Test caching performance"
        
        # First expansion (cache miss)
        start_time = time.time()
        response1 = await template_service.expand_task_description(
            original_description=original_description,
            template_name="workflow_default"
        )
        first_duration = (time.time() - start_time) * 1000
        
        # Second expansion (cache hit)
        start_time = time.time()
        response2 = await template_service.expand_task_description(
            original_description=original_description,
            template_name="workflow_default"
        )
        second_duration = (time.time() - start_time) * 1000
        
        # Verify both succeeded
        assert response1.success is True
        assert response2.success is True
        
        # Verify caching improved performance significantly
        improvement_ratio = first_duration / second_duration
        assert improvement_ratio > 2, f"Cache only improved performance by {improvement_ratio:.2f}x"
        
        print(f"Cache performance: first={first_duration:.2f}ms, second={second_duration:.2f}ms, improvement={improvement_ratio:.2f}x")

    @pytest.mark.asyncio
    async def test_task_creation_overhead(self, mock_supabase_client):
        """Test task creation performance overhead with template injection"""
        
        task_service = TaskService(supabase_client=mock_supabase_client)
        template_service = TemplateInjectionService(supabase_client=mock_supabase_client)
        project_id = str(uuid4())
        
        # Mock task creation response
        mock_task_response = {
            "id": str(uuid4()),
            "project_id": project_id,
            "title": "Test Task",
            "description": "Expanded description",
            "status": "todo",
            "created_at": "2025-08-20T10:00:00Z"
        }
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [mock_task_response]
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = []
        
        with patch('src.server.services.projects.task_service.get_template_injection_service', return_value=template_service):
            with patch('src.server.services.projects.task_service._template_injection_available', True):
                
                # Test task creation with template injection
                start_time = time.time()
                success, result = await task_service.create_task(
                    project_id=project_id,
                    title="Performance Test Task",
                    description="Test template injection overhead",
                    template_name="workflow_default",
                    enable_template_injection=True
                )
                duration_with_template = (time.time() - start_time) * 1000
                
                assert success is True
                
                # Test task creation without template injection
                start_time = time.time()
                success, result = await task_service.create_task(
                    project_id=project_id,
                    title="Performance Test Task",
                    description="Test without template injection",
                    enable_template_injection=False
                )
                duration_without_template = (time.time() - start_time) * 1000
                
                assert success is True
                
                # Calculate overhead
                overhead = duration_with_template - duration_without_template
                
                # Verify overhead is within target (<50ms)
                assert overhead < 50, f"Template injection overhead {overhead:.2f}ms exceeds 50ms target"
                
                print(f"Task creation overhead: {overhead:.2f}ms (with template: {duration_with_template:.2f}ms, without: {duration_without_template:.2f}ms)")

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, template_service):
        """Test memory usage doesn't grow excessively under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many template expansions
        for i in range(100):
            await template_service.expand_task_description(
                original_description=f"Task {i}: Implement feature",
                template_name="workflow_default"
            )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Verify memory growth is reasonable (<50MB for 100 expansions)
        assert memory_growth < 50, f"Memory grew by {memory_growth:.2f}MB, which is excessive"
        
        print(f"Memory usage: initial={initial_memory:.2f}MB, final={final_memory:.2f}MB, growth={memory_growth:.2f}MB")

    @pytest.mark.asyncio
    async def test_cache_efficiency(self, template_service):
        """Test cache hit ratio and efficiency"""
        
        # Clear any existing cache
        template_service._template_cache.clear()
        template_service._component_cache.clear()
        
        # Track cache operations
        cache_hits = 0
        cache_misses = 0
        
        # Patch cache methods to track hits/misses
        original_get_cached_template = template_service._get_cached_template
        original_cache_template = template_service._cache_template
        
        def track_cache_get(template_name):
            nonlocal cache_hits, cache_misses
            result = original_get_cached_template(template_name)
            if result:
                cache_hits += 1
            else:
                cache_misses += 1
            return result
        
        template_service._get_cached_template = track_cache_get
        
        # Perform repeated expansions
        for i in range(10):
            await template_service.expand_task_description(
                original_description=f"Task {i}",
                template_name="workflow_default"
            )
        
        # Calculate cache efficiency
        total_requests = cache_hits + cache_misses
        hit_ratio = cache_hits / total_requests if total_requests > 0 else 0
        
        # Verify cache is working effectively
        assert hit_ratio > 0.5, f"Cache hit ratio {hit_ratio:.2f} is too low"
        
        print(f"Cache efficiency: {cache_hits} hits, {cache_misses} misses, hit ratio: {hit_ratio:.2f}")

    @pytest.mark.asyncio
    async def test_large_template_performance(self, mock_supabase_client):
        """Test performance with large templates and many components"""
        
        # Create a large template with many components
        large_template_content = "\n\n".join([
            f"{{{{group::component_{i}}}}}" for i in range(20)
        ]) + "\n\n{{USER_TASK}}\n\n" + "\n\n".join([
            f"{{{{group::post_component_{i}}}}}" for i in range(10)
        ])
        
        mock_large_template = {
            "id": str(uuid4()),
            "name": "workflow_large",
            "template_data": {
                "template_content": large_template_content,
                "user_task_position": 21
            },
            "is_active": True
        }
        
        # Mock many components
        mock_components = []
        for i in range(30):
            component_name = f"group::component_{i}" if i < 20 else f"group::post_component_{i-20}"
            mock_components.append({
                "id": str(uuid4()),
                "name": component_name,
                "instruction_text": f"Component {i} instruction text with detailed steps and requirements.",
                "component_type": "group",
                "is_active": True
            })
        
        # Update mock to return large template
        def mock_table_call(table_name):
            if table_name == "archon_template_definitions":
                mock_template_table = MagicMock()
                mock_template_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_large_template]
                return mock_template_table
            elif table_name == "archon_template_components":
                mock_component_table = MagicMock()
                mock_component_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = mock_components
                return mock_component_table
            return MagicMock()
        
        mock_supabase_client.table.side_effect = mock_table_call
        
        template_service = TemplateInjectionService(supabase_client=mock_supabase_client)
        
        # Test expansion performance with large template
        start_time = time.time()
        response = await template_service.expand_task_description(
            original_description="Test large template performance",
            template_name="workflow_large"
        )
        duration_ms = (time.time() - start_time) * 1000
        
        # Verify success and reasonable performance even with large template
        assert response.success is True
        assert duration_ms < 500, f"Large template expansion took {duration_ms:.2f}ms, should be <500ms"
        
        # Verify all components were expanded
        expanded_text = response.result.expanded_instructions
        assert "Component 0 instruction" in expanded_text
        assert "Component 19 instruction" in expanded_text
        assert "Component 9 instruction" in expanded_text  # post_component_9
        
        print(f"Large template performance: {duration_ms:.2f}ms for 30 components")
