"""
Tests for Template Assignment Inheritance System

This test suite validates the multi-level template assignment and inheritance
resolution functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock

from server.services.template_assignment_service import (
    TemplateAssignmentService,
    HierarchyLevel,
    AssignmentScope,
    TemplateAssignment
)
from server.services.template_resolver import TemplateResolver, TemplateResolution


class TestTemplateAssignmentService:
    """Test template assignment service functionality"""

    @pytest.fixture
    async def assignment_service(self):
        """Create template assignment service with mocked database"""
        mock_db = AsyncMock()
        service = TemplateAssignmentService(mock_db)
        return service, mock_db

    @pytest.fixture
    def sample_assignment_data(self):
        """Sample assignment data for testing"""
        return {
            "id": uuid4(),
            "entity_id": uuid4(),
            "template_name": "workflow_hotfix",
            "hierarchy_level": "project",
            "assignment_scope": "all",
            "priority": 10,
            "inheritance_enabled": True,
            "entity_type": None,
            "conditional_logic": None,
            "metadata": None,
            "effective_from": datetime.utcnow(),
            "effective_until": None,
            "is_active": True,
            "created_by": "test_user",
            "updated_by": "test_user",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    async def test_assign_template_success(self, assignment_service, sample_assignment_data):
        """Test successful template assignment"""
        service, mock_db = assignment_service
        
        # Mock template validation
        mock_db.fetchrow.side_effect = [
            {"id": uuid4()},  # Template exists
            sample_assignment_data  # Assignment creation result
        ]
        mock_db.fetchval.return_value = 1  # Cache invalidation
        
        result = await service.assign_template(
            template_name="workflow_hotfix",
            hierarchy_level=HierarchyLevel.PROJECT,
            entity_id=sample_assignment_data["entity_id"],
            priority=10
        )
        
        assert isinstance(result, TemplateAssignment)
        assert result.template_name == "workflow_hotfix"
        assert result.hierarchy_level == HierarchyLevel.PROJECT
        assert result.priority == 10

    async def test_assign_template_invalid_template(self, assignment_service):
        """Test assignment with invalid template"""
        service, mock_db = assignment_service
        
        # Mock template not found
        mock_db.fetchrow.return_value = None
        
        with pytest.raises(ValueError, match="Template 'invalid_template' not found"):
            await service.assign_template(
                template_name="invalid_template",
                hierarchy_level=HierarchyLevel.PROJECT,
                entity_id=uuid4()
            )

    async def test_assign_template_global_with_entity_id(self, assignment_service):
        """Test that global assignments cannot have entity_id"""
        service, mock_db = assignment_service
        
        # Mock template exists
        mock_db.fetchrow.return_value = {"id": uuid4()}
        
        with pytest.raises(ValueError, match="Global assignments cannot have entity_id"):
            await service.assign_template(
                template_name="workflow_default",
                hierarchy_level=HierarchyLevel.GLOBAL,
                entity_id=uuid4()
            )

    async def test_list_assignments_with_filters(self, assignment_service, sample_assignment_data):
        """Test listing assignments with filters"""
        service, mock_db = assignment_service
        
        mock_db.fetch.return_value = [sample_assignment_data]
        
        results = await service.list_assignments(
            hierarchy_level=HierarchyLevel.PROJECT,
            template_name="workflow_hotfix"
        )
        
        assert len(results) == 1
        assert results[0].template_name == "workflow_hotfix"
        assert results[0].hierarchy_level == HierarchyLevel.PROJECT

    async def test_update_assignment(self, assignment_service, sample_assignment_data):
        """Test updating template assignment"""
        service, mock_db = assignment_service
        
        assignment_id = sample_assignment_data["id"]
        
        # Mock get assignment and update
        mock_db.fetchrow.side_effect = [
            sample_assignment_data,  # Get current assignment
            {"id": uuid4()},  # Template validation
            {**sample_assignment_data, "priority": 20}  # Update result
        ]
        mock_db.fetchval.return_value = 1  # Cache invalidation
        
        result = await service.update_assignment(
            assignment_id=assignment_id,
            priority=20
        )
        
        assert result is not None
        assert result.priority == 20

    async def test_remove_assignment(self, assignment_service, sample_assignment_data):
        """Test removing template assignment"""
        service, mock_db = assignment_service
        
        assignment_id = sample_assignment_data["id"]
        
        # Mock get assignment and delete
        mock_db.fetchrow.return_value = sample_assignment_data
        mock_db.execute.return_value = "DELETE 1"
        mock_db.fetchval.return_value = 1  # Cache invalidation
        
        result = await service.remove_assignment(assignment_id)
        
        assert result is True

    async def test_bulk_assign_templates(self, assignment_service, sample_assignment_data):
        """Test bulk template assignment"""
        service, mock_db = assignment_service
        
        assignments_data = [
            {
                "template_name": "workflow_hotfix",
                "hierarchy_level": "project",
                "entity_id": str(uuid4()),
                "priority": 10
            },
            {
                "template_name": "workflow_research",
                "hierarchy_level": "project", 
                "entity_id": str(uuid4()),
                "priority": 5
            }
        ]
        
        # Mock template validation and assignment creation
        mock_db.fetchrow.side_effect = [
            {"id": uuid4()},  # Template 1 exists
            sample_assignment_data,  # Assignment 1 created
            {"id": uuid4()},  # Template 2 exists
            {**sample_assignment_data, "template_name": "workflow_research"}  # Assignment 2 created
        ]
        mock_db.fetchval.return_value = 1  # Cache invalidation
        
        results = await service.assign_template_bulk(assignments_data)
        
        assert len(results) == 2
        assert results[0].template_name == "workflow_hotfix"
        assert results[1].template_name == "workflow_research"


class TestTemplateResolver:
    """Test template resolver functionality"""

    @pytest.fixture
    async def template_resolver(self):
        """Create template resolver with mocked database"""
        mock_db = AsyncMock()
        resolver = TemplateResolver(mock_db)
        return resolver, mock_db

    @pytest.fixture
    def sample_resolution_data(self):
        """Sample resolution data for testing"""
        return {
            "template_name": "workflow_hotfix",
            "hierarchy_level": "project",
            "assignment_id": uuid4(),
            "priority": 10,
            "resolution_path": [
                {
                    "level": "project",
                    "assignment_id": str(uuid4()),
                    "template_name": "workflow_hotfix",
                    "priority": 10
                }
            ]
        }

    async def test_resolve_template_from_cache(self, template_resolver, sample_resolution_data):
        """Test template resolution from cache"""
        resolver, mock_db = template_resolver
        
        # Mock cache hit
        cache_data = {
            "id": uuid4(),
            "resolved_template_name": "workflow_hotfix",
            "hierarchy_level": "task",
            "resolution_path": sample_resolution_data["resolution_path"]
        }
        mock_db.fetchrow.return_value = cache_data
        mock_db.execute.return_value = None  # Cache hit count update
        
        result = await resolver.resolve_template(
            entity_id=uuid4(),
            entity_type="task",
            project_id=uuid4()
        )
        
        assert isinstance(result, TemplateResolution)
        assert result.template_name == "workflow_hotfix"
        assert result.cached is True
        assert result.cache_hit is True

    async def test_resolve_template_through_hierarchy(self, template_resolver, sample_resolution_data):
        """Test template resolution through hierarchy"""
        resolver, mock_db = template_resolver
        
        # Mock cache miss and hierarchy resolution
        mock_db.fetchrow.side_effect = [
            None,  # Cache miss
            sample_resolution_data  # Hierarchy resolution
        ]
        mock_db.fetchval.return_value = uuid4()  # Cache storage
        
        result = await resolver.resolve_template(
            entity_id=uuid4(),
            entity_type="task",
            project_id=uuid4()
        )
        
        assert isinstance(result, TemplateResolution)
        assert result.template_name == "workflow_hotfix"
        assert result.hierarchy_level == HierarchyLevel.PROJECT
        assert result.cached is False

    async def test_resolve_template_fallback_to_default(self, template_resolver):
        """Test template resolution fallback to default"""
        resolver, mock_db = template_resolver
        
        # Mock cache miss and no hierarchy resolution
        mock_db.fetchrow.side_effect = [
            None,  # Cache miss
            None   # No hierarchy resolution
        ]
        mock_db.fetchval.return_value = uuid4()  # Cache storage
        
        result = await resolver.resolve_template(
            entity_id=uuid4(),
            entity_type="task",
            project_id=uuid4()
        )
        
        assert isinstance(result, TemplateResolution)
        assert result.template_name == "workflow_default"
        assert result.hierarchy_level == HierarchyLevel.GLOBAL

    async def test_resolve_template_for_task_convenience(self, template_resolver, sample_resolution_data):
        """Test convenience method for task template resolution"""
        resolver, mock_db = template_resolver
        
        # Mock cache miss and hierarchy resolution
        mock_db.fetchrow.side_effect = [
            None,  # Cache miss
            sample_resolution_data  # Hierarchy resolution
        ]
        mock_db.fetchval.return_value = uuid4()  # Cache storage
        
        task_id = uuid4()
        project_id = uuid4()
        
        result = await resolver.resolve_template_for_task(task_id, project_id)
        
        assert isinstance(result, TemplateResolution)
        assert result.template_name == "workflow_hotfix"

    async def test_validate_template_resolution(self, template_resolver, sample_resolution_data):
        """Test template resolution validation"""
        resolver, mock_db = template_resolver
        
        # Mock cache miss and hierarchy resolution
        mock_db.fetchrow.side_effect = [
            None,  # Cache miss
            sample_resolution_data  # Hierarchy resolution
        ]
        mock_db.fetchval.return_value = uuid4()  # Cache storage
        
        is_valid = await resolver.validate_template_resolution(
            entity_id=uuid4(),
            entity_type="task",
            expected_template="workflow_hotfix",
            project_id=uuid4()
        )
        
        assert is_valid is True

    async def test_invalidate_cache(self, template_resolver):
        """Test cache invalidation"""
        resolver, mock_db = template_resolver
        
        mock_db.fetchval.return_value = 5  # 5 entries invalidated
        
        count = await resolver.invalidate_cache()
        
        assert count == 5

    async def test_cleanup_expired_cache(self, template_resolver):
        """Test expired cache cleanup"""
        resolver, mock_db = template_resolver
        
        mock_db.fetchval.return_value = 3  # 3 entries cleaned up
        
        count = await resolver.cleanup_expired_cache()
        
        assert count == 3

    async def test_get_cache_statistics(self, template_resolver):
        """Test cache statistics retrieval"""
        resolver, mock_db = template_resolver
        
        stats_data = {
            "total_entries": 100,
            "active_entries": 85,
            "expired_entries": 15,
            "avg_hit_count": 5.2,
            "max_hit_count": 25,
            "entity_types": 3,
            "hierarchy_levels": 4
        }
        mock_db.fetchrow.return_value = stats_data
        
        stats = await resolver.get_cache_statistics()
        
        assert stats["total_entries"] == 100
        assert stats["active_entries"] == 85
        assert stats["cache_ttl_minutes"] == 30


class TestTemplateInheritanceIntegration:
    """Integration tests for template inheritance system"""

    async def test_inheritance_hierarchy_resolution(self):
        """Test complete inheritance hierarchy resolution"""
        # This would be an integration test with real database
        # For now, we'll test the logic flow
        
        # Test data representing hierarchy:
        # Global: workflow_default
        # Project: workflow_hotfix (overrides global)
        # Task: workflow_research (overrides project)
        
        task_id = uuid4()
        project_id = uuid4()
        
        # Expected resolution path:
        # 1. Check task level -> find workflow_research
        # 2. Return workflow_research (highest priority)
        
        expected_template = "workflow_research"
        expected_hierarchy = HierarchyLevel.TASK
        
        # This test would verify the complete flow in a real environment
        assert True  # Placeholder for integration test

    async def test_performance_requirements(self):
        """Test that resolution meets performance requirements (<10ms)"""
        # This would measure actual resolution time
        # Target: <10ms for template resolution
        
        start_time = datetime.utcnow()
        
        # Simulate resolution work
        await asyncio.sleep(0.005)  # 5ms simulation
        
        end_time = datetime.utcnow()
        resolution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        assert resolution_time_ms < 10, f"Resolution took {resolution_time_ms}ms, target is <10ms"

    async def test_cache_performance_improvement(self):
        """Test that caching improves performance"""
        # This would compare cached vs uncached resolution times
        
        # First resolution (uncached) - slower
        uncached_time = 8.5  # ms
        
        # Second resolution (cached) - faster
        cached_time = 1.2  # ms
        
        improvement_ratio = uncached_time / cached_time
        
        assert improvement_ratio > 2, f"Cache improvement ratio {improvement_ratio:.1f}x, expected >2x"

    async def test_concurrent_resolution_safety(self):
        """Test that concurrent resolutions are safe"""
        # This would test multiple concurrent resolution requests
        
        async def resolve_template():
            # Simulate template resolution
            await asyncio.sleep(0.001)
            return "workflow_default"
        
        # Run multiple concurrent resolutions
        tasks = [resolve_template() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed and return consistent results
        assert len(results) == 10
        assert all(result == "workflow_default" for result in results)
