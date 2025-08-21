"""
Template Resolver Service

This service resolves template assignments through the inheritance hierarchy
with caching for optimal performance.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID

from server.config.database import get_database_connection
from server.services.template_assignment_service import (
    HierarchyLevel, 
    TemplateResolution,
    TemplateAssignmentService
)

logger = logging.getLogger(__name__)


class TemplateResolver:
    """
    Service for resolving template assignments through inheritance hierarchy
    """

    def __init__(self, db_connection=None):
        """Initialize the template resolver"""
        self.db_connection = db_connection
        self.assignment_service = TemplateAssignmentService(db_connection)
        self._cache_ttl_minutes = 30
        self._performance_target_ms = 10

    async def _get_db_connection(self):
        """Get database connection"""
        if self.db_connection is None:
            self.db_connection = await get_database_connection()
        return self.db_connection

    async def resolve_template(
        self,
        entity_id: UUID,
        entity_type: str,
        project_id: Optional[UUID] = None,
        milestone_id: Optional[UUID] = None,
        phase_id: Optional[UUID] = None,
        context_data: Optional[Dict] = None
    ) -> TemplateResolution:
        """
        Resolve template for an entity through inheritance hierarchy
        
        Args:
            entity_id: ID of the entity (task, etc.)
            entity_type: Type of entity (task, feature, etc.)
            project_id: ID of the project
            milestone_id: ID of the milestone
            phase_id: ID of the phase
            context_data: Additional context for resolution
            
        Returns:
            Template resolution result
        """
        start_time = datetime.utcnow()
        context_data = context_data or {}
        
        # Generate cache key
        context_hash = self._generate_context_hash({
            "entity_id": str(entity_id),
            "entity_type": entity_type,
            "project_id": str(project_id) if project_id else None,
            "milestone_id": str(milestone_id) if milestone_id else None,
            "phase_id": str(phase_id) if phase_id else None,
            "context": context_data
        })
        
        # Check cache first
        cached_result = await self._get_cached_resolution(
            entity_id, entity_type, HierarchyLevel.TASK, context_hash
        )
        
        if cached_result:
            resolution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.debug(f"Template resolution cache hit: {resolution_time:.1f}ms")
            return cached_result
        
        # Resolve through hierarchy
        resolution = await self._resolve_through_hierarchy(
            entity_id, entity_type, project_id, milestone_id, phase_id, context_data
        )
        
        # Cache the result
        await self._cache_resolution(
            entity_id, entity_type, HierarchyLevel.TASK, context_hash, resolution
        )
        
        resolution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(f"Template resolved: {resolution.template_name} in {resolution_time:.1f}ms")
        
        # Log performance warning if too slow
        if resolution_time > self._performance_target_ms:
            logger.warning(f"Template resolution slow: {resolution_time:.1f}ms > {self._performance_target_ms}ms")
        
        return resolution

    async def _resolve_through_hierarchy(
        self,
        entity_id: UUID,
        entity_type: str,
        project_id: Optional[UUID],
        milestone_id: Optional[UUID],
        phase_id: Optional[UUID],
        context_data: Dict
    ) -> TemplateResolution:
        """
        Resolve template through inheritance hierarchy using database function
        """
        db = await self._get_db_connection()
        
        # Use the database function for efficient resolution
        query = """
        SELECT * FROM resolve_template_inheritance($1, $2, $3, $4)
        """
        
        result = await db.fetchrow(
            query,
            entity_id,
            entity_type,
            project_id,
            json.dumps(context_data)
        )
        
        if result:
            return TemplateResolution(
                template_name=result["template_name"],
                hierarchy_level=HierarchyLevel(result["hierarchy_level"]),
                assignment_id=result["assignment_id"],
                priority=result["priority"],
                resolution_path=result["resolution_path"],
                cached=False,
                cache_hit=False
            )
        
        # Fallback to default template
        return TemplateResolution(
            template_name="workflow_default",
            hierarchy_level=HierarchyLevel.GLOBAL,
            assignment_id=None,
            priority=0,
            resolution_path=[{
                "level": "global",
                "assignment_id": None,
                "template_name": "workflow_default",
                "priority": 0,
                "source": "fallback"
            }],
            cached=False,
            cache_hit=False
        )

    async def resolve_template_for_task(
        self,
        task_id: UUID,
        project_id: UUID,
        context_data: Optional[Dict] = None
    ) -> TemplateResolution:
        """
        Convenience method to resolve template for a task
        
        Args:
            task_id: ID of the task
            project_id: ID of the project
            context_data: Additional context
            
        Returns:
            Template resolution result
        """
        return await self.resolve_template(
            entity_id=task_id,
            entity_type="task",
            project_id=project_id,
            context_data=context_data
        )

    async def resolve_template_for_project(
        self,
        project_id: UUID,
        context_data: Optional[Dict] = None
    ) -> TemplateResolution:
        """
        Resolve default template for a project
        
        Args:
            project_id: ID of the project
            context_data: Additional context
            
        Returns:
            Template resolution result
        """
        return await self.resolve_template(
            entity_id=project_id,
            entity_type="project",
            project_id=project_id,
            context_data=context_data
        )

    async def get_resolution_path(
        self,
        entity_id: UUID,
        entity_type: str,
        project_id: Optional[UUID] = None,
        context_data: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Get the full resolution path showing how template was resolved
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of entity
            project_id: ID of the project
            context_data: Additional context
            
        Returns:
            List of resolution steps
        """
        resolution = await self.resolve_template(
            entity_id=entity_id,
            entity_type=entity_type,
            project_id=project_id,
            context_data=context_data
        )
        
        return resolution.resolution_path

    async def validate_template_resolution(
        self,
        entity_id: UUID,
        entity_type: str,
        expected_template: str,
        project_id: Optional[UUID] = None,
        context_data: Optional[Dict] = None
    ) -> bool:
        """
        Validate that template resolution returns expected template
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of entity
            expected_template: Expected template name
            project_id: ID of the project
            context_data: Additional context
            
        Returns:
            True if resolution matches expected template
        """
        resolution = await self.resolve_template(
            entity_id=entity_id,
            entity_type=entity_type,
            project_id=project_id,
            context_data=context_data
        )
        
        return resolution.template_name == expected_template

    async def _get_cached_resolution(
        self,
        entity_id: UUID,
        entity_type: str,
        hierarchy_level: HierarchyLevel,
        context_hash: str
    ) -> Optional[TemplateResolution]:
        """
        Get cached template resolution
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of entity
            hierarchy_level: Hierarchy level
            context_hash: Hash of context data
            
        Returns:
            Cached resolution or None
        """
        db = await self._get_db_connection()
        
        query = """
        SELECT * FROM archon_template_assignment_cache
        WHERE entity_id = $1 
          AND entity_type = $2 
          AND hierarchy_level = $3 
          AND context_hash = $4
          AND expires_at > NOW()
        """
        
        result = await db.fetchrow(
            query, entity_id, entity_type, hierarchy_level.value, context_hash
        )
        
        if result:
            # Update cache hit count
            await db.execute(
                """
                UPDATE archon_template_assignment_cache 
                SET cache_hit_count = cache_hit_count + 1,
                    last_accessed_at = NOW()
                WHERE id = $1
                """,
                result["id"]
            )
            
            return TemplateResolution(
                template_name=result["resolved_template_name"],
                hierarchy_level=HierarchyLevel(result["hierarchy_level"]),
                assignment_id=None,  # Not stored in cache
                priority=0,  # Not stored in cache
                resolution_path=result["resolution_path"],
                cached=True,
                cache_hit=True
            )
        
        return None

    async def _cache_resolution(
        self,
        entity_id: UUID,
        entity_type: str,
        hierarchy_level: HierarchyLevel,
        context_hash: str,
        resolution: TemplateResolution
    ) -> None:
        """
        Cache template resolution result
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of entity
            hierarchy_level: Hierarchy level
            context_hash: Hash of context data
            resolution: Resolution to cache
        """
        db = await self._get_db_connection()
        
        query = "SELECT cache_template_resolution($1, $2, $3, $4, $5, $6, $7, $8)"
        
        await db.fetchval(
            query,
            entity_id,
            entity_type,
            hierarchy_level.value,
            context_hash,
            resolution.template_name,
            json.dumps(resolution.resolution_path),
            json.dumps({}),  # assignment_metadata
            self._cache_ttl_minutes
        )

    async def invalidate_cache(
        self,
        entity_id: Optional[UUID] = None,
        hierarchy_level: Optional[HierarchyLevel] = None
    ) -> int:
        """
        Invalidate template resolution cache
        
        Args:
            entity_id: Optional entity ID to filter by
            hierarchy_level: Optional hierarchy level to filter by
            
        Returns:
            Number of cache entries invalidated
        """
        db = await self._get_db_connection()
        
        query = "SELECT invalidate_template_assignment_cache($1, $2)"
        result = await db.fetchval(
            query,
            entity_id,
            hierarchy_level.value if hierarchy_level else None
        )
        
        logger.info(f"Invalidated {result} cache entries")
        return result

    async def cleanup_expired_cache(self) -> int:
        """
        Clean up expired cache entries
        
        Returns:
            Number of entries cleaned up
        """
        db = await self._get_db_connection()
        
        query = "SELECT cleanup_expired_template_cache()"
        result = await db.fetchval(query)
        
        if result > 0:
            logger.info(f"Cleaned up {result} expired cache entries")
        
        return result

    async def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache performance statistics
        
        Returns:
            Cache statistics
        """
        db = await self._get_db_connection()
        
        query = """
        SELECT 
            COUNT(*) as total_entries,
            COUNT(*) FILTER (WHERE expires_at > NOW()) as active_entries,
            COUNT(*) FILTER (WHERE expires_at <= NOW()) as expired_entries,
            AVG(cache_hit_count) as avg_hit_count,
            MAX(cache_hit_count) as max_hit_count,
            COUNT(DISTINCT entity_type) as entity_types,
            COUNT(DISTINCT hierarchy_level) as hierarchy_levels
        FROM archon_template_assignment_cache
        """
        
        result = await db.fetchrow(query)
        
        return {
            "total_entries": result["total_entries"],
            "active_entries": result["active_entries"],
            "expired_entries": result["expired_entries"],
            "avg_hit_count": float(result["avg_hit_count"]) if result["avg_hit_count"] else 0,
            "max_hit_count": result["max_hit_count"],
            "entity_types": result["entity_types"],
            "hierarchy_levels": result["hierarchy_levels"],
            "cache_ttl_minutes": self._cache_ttl_minutes
        }

    def _generate_context_hash(self, context_data: Dict) -> str:
        """Generate hash for context data"""
        context_str = json.dumps(context_data, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()[:16]


# Global instance for easy access
template_resolver = TemplateResolver()


async def resolve_template_for_task(
    task_id: UUID,
    project_id: UUID,
    context_data: Optional[Dict] = None
) -> str:
    """
    Convenience function to resolve template name for a task
    
    Args:
        task_id: ID of the task
        project_id: ID of the project
        context_data: Additional context
        
    Returns:
        Template name
    """
    resolution = await template_resolver.resolve_template_for_task(
        task_id, project_id, context_data
    )
    return resolution.template_name
