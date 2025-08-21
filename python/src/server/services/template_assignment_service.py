"""
Template Assignment Service

This service manages template assignments at different hierarchy levels
(Global, Project, Milestone, Phase, Task) with inheritance resolution.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID, uuid4
from dataclasses import dataclass
from enum import Enum

from server.config.database import get_database_connection

logger = logging.getLogger(__name__)


class HierarchyLevel(Enum):
    """Hierarchy levels for template assignment"""
    GLOBAL = "global"
    PROJECT = "project"
    MILESTONE = "milestone"
    PHASE = "phase"
    TASK = "task"


class AssignmentScope(Enum):
    """Scope of template assignment"""
    ALL = "all"
    SPECIFIC_TYPES = "specific_types"
    CONDITIONAL = "conditional"


@dataclass
class TemplateAssignment:
    """Template assignment data structure"""
    id: Optional[UUID]
    entity_id: Optional[UUID]
    template_name: str
    hierarchy_level: HierarchyLevel
    assignment_scope: AssignmentScope
    priority: int
    inheritance_enabled: bool
    entity_type: Optional[str] = None
    conditional_logic: Optional[Dict] = None
    metadata: Optional[Dict] = None
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None
    is_active: bool = True
    created_by: str = "system"
    updated_by: str = "system"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class TemplateResolution:
    """Template resolution result"""
    template_name: str
    hierarchy_level: HierarchyLevel
    assignment_id: Optional[UUID]
    priority: int
    resolution_path: List[Dict]
    cached: bool = False
    cache_hit: bool = False


class TemplateAssignmentService:
    """
    Service for managing template assignments and inheritance resolution
    """

    def __init__(self, db_connection=None):
        """Initialize the template assignment service"""
        self.db_connection = db_connection
        self._cache_ttl_minutes = 30
        self._max_cache_entries = 10000

    async def _get_db_connection(self):
        """Get database connection"""
        if self.db_connection is None:
            self.db_connection = await get_database_connection()
        return self.db_connection

    async def assign_template(
        self,
        template_name: str,
        hierarchy_level: HierarchyLevel,
        entity_id: Optional[UUID] = None,
        assignment_scope: AssignmentScope = AssignmentScope.ALL,
        priority: int = 0,
        entity_type: Optional[str] = None,
        conditional_logic: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        effective_from: Optional[datetime] = None,
        effective_until: Optional[datetime] = None,
        created_by: str = "system"
    ) -> TemplateAssignment:
        """
        Assign a template to a hierarchy level
        
        Args:
            template_name: Name of template to assign
            hierarchy_level: Level in hierarchy to assign to
            entity_id: ID of entity (project, milestone, etc.)
            assignment_scope: Scope of assignment
            priority: Priority for conflict resolution
            entity_type: Type of entity for specific_types scope
            conditional_logic: Logic for conditional assignments
            metadata: Additional metadata
            effective_from: When assignment becomes effective
            effective_until: When assignment expires
            created_by: Who created the assignment
            
        Returns:
            Created template assignment
        """
        db = await self._get_db_connection()
        
        # Validate template exists
        await self._validate_template_exists(template_name)
        
        # Validate assignment
        await self._validate_assignment(
            template_name, hierarchy_level, entity_id, assignment_scope, entity_type
        )
        
        assignment_id = uuid4()
        now = datetime.utcnow()
        
        query = """
        INSERT INTO archon_template_assignments (
            id, entity_id, template_name, hierarchy_level, assignment_scope,
            priority, inheritance_enabled, entity_type, conditional_logic,
            metadata, effective_from, effective_until, is_active,
            created_by, updated_by, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17
        ) RETURNING *
        """
        
        result = await db.fetchrow(
            query,
            assignment_id,
            entity_id,
            template_name,
            hierarchy_level.value,
            assignment_scope.value,
            priority,
            True,  # inheritance_enabled
            entity_type,
            json.dumps(conditional_logic) if conditional_logic else None,
            json.dumps(metadata) if metadata else None,
            effective_from or now,
            effective_until,
            True,  # is_active
            created_by,
            created_by,  # updated_by
            now,
            now
        )
        
        # Invalidate cache for affected entities
        await self._invalidate_cache(entity_id, hierarchy_level)
        
        logger.info(f"Template assignment created: {template_name} -> {hierarchy_level.value}")
        
        return self._row_to_assignment(result)

    async def list_assignments(
        self,
        hierarchy_level: Optional[HierarchyLevel] = None,
        entity_id: Optional[UUID] = None,
        template_name: Optional[str] = None,
        is_active: bool = True,
        include_expired: bool = False
    ) -> List[TemplateAssignment]:
        """
        List template assignments with optional filtering
        
        Args:
            hierarchy_level: Filter by hierarchy level
            entity_id: Filter by entity ID
            template_name: Filter by template name
            is_active: Filter by active status
            include_expired: Include expired assignments
            
        Returns:
            List of template assignments
        """
        db = await self._get_db_connection()
        
        conditions = ["1=1"]
        params = []
        param_count = 0
        
        if hierarchy_level:
            param_count += 1
            conditions.append(f"hierarchy_level = ${param_count}")
            params.append(hierarchy_level.value)
        
        if entity_id:
            param_count += 1
            conditions.append(f"entity_id = ${param_count}")
            params.append(entity_id)
        
        if template_name:
            param_count += 1
            conditions.append(f"template_name = ${param_count}")
            params.append(template_name)
        
        if is_active is not None:
            param_count += 1
            conditions.append(f"is_active = ${param_count}")
            params.append(is_active)
        
        if not include_expired:
            conditions.append("(effective_until IS NULL OR effective_until > NOW())")
        
        query = f"""
        SELECT * FROM archon_template_assignments
        WHERE {' AND '.join(conditions)}
        ORDER BY hierarchy_level, priority DESC, created_at ASC
        """
        
        results = await db.fetch(query, *params)
        return [self._row_to_assignment(row) for row in results]

    async def get_assignment(self, assignment_id: UUID) -> Optional[TemplateAssignment]:
        """
        Get a specific template assignment
        
        Args:
            assignment_id: ID of assignment to retrieve
            
        Returns:
            Template assignment or None if not found
        """
        db = await self._get_db_connection()
        
        query = "SELECT * FROM archon_template_assignments WHERE id = $1"
        result = await db.fetchrow(query, assignment_id)
        
        return self._row_to_assignment(result) if result else None

    async def update_assignment(
        self,
        assignment_id: UUID,
        template_name: Optional[str] = None,
        priority: Optional[int] = None,
        assignment_scope: Optional[AssignmentScope] = None,
        entity_type: Optional[str] = None,
        conditional_logic: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        effective_from: Optional[datetime] = None,
        effective_until: Optional[datetime] = None,
        is_active: Optional[bool] = None,
        updated_by: str = "system"
    ) -> Optional[TemplateAssignment]:
        """
        Update a template assignment
        
        Args:
            assignment_id: ID of assignment to update
            template_name: New template name
            priority: New priority
            assignment_scope: New assignment scope
            entity_type: New entity type
            conditional_logic: New conditional logic
            metadata: New metadata
            effective_from: New effective from date
            effective_until: New effective until date
            is_active: New active status
            updated_by: Who updated the assignment
            
        Returns:
            Updated template assignment or None if not found
        """
        db = await self._get_db_connection()
        
        # Get current assignment
        current = await self.get_assignment(assignment_id)
        if not current:
            return None
        
        # Build update query
        updates = []
        params = []
        param_count = 0
        
        if template_name is not None:
            await self._validate_template_exists(template_name)
            param_count += 1
            updates.append(f"template_name = ${param_count}")
            params.append(template_name)
        
        if priority is not None:
            param_count += 1
            updates.append(f"priority = ${param_count}")
            params.append(priority)
        
        if assignment_scope is not None:
            param_count += 1
            updates.append(f"assignment_scope = ${param_count}")
            params.append(assignment_scope.value)
        
        if entity_type is not None:
            param_count += 1
            updates.append(f"entity_type = ${param_count}")
            params.append(entity_type)
        
        if conditional_logic is not None:
            param_count += 1
            updates.append(f"conditional_logic = ${param_count}")
            params.append(json.dumps(conditional_logic))
        
        if metadata is not None:
            param_count += 1
            updates.append(f"metadata = ${param_count}")
            params.append(json.dumps(metadata))
        
        if effective_from is not None:
            param_count += 1
            updates.append(f"effective_from = ${param_count}")
            params.append(effective_from)
        
        if effective_until is not None:
            param_count += 1
            updates.append(f"effective_until = ${param_count}")
            params.append(effective_until)
        
        if is_active is not None:
            param_count += 1
            updates.append(f"is_active = ${param_count}")
            params.append(is_active)
        
        if not updates:
            return current
        
        # Add updated_by and updated_at
        param_count += 1
        updates.append(f"updated_by = ${param_count}")
        params.append(updated_by)
        
        param_count += 1
        updates.append(f"updated_at = ${param_count}")
        params.append(datetime.utcnow())
        
        # Add assignment_id for WHERE clause
        param_count += 1
        params.append(assignment_id)
        
        query = f"""
        UPDATE archon_template_assignments 
        SET {', '.join(updates)}
        WHERE id = ${param_count}
        RETURNING *
        """
        
        result = await db.fetchrow(query, *params)
        
        if result:
            # Invalidate cache
            await self._invalidate_cache(current.entity_id, current.hierarchy_level)
            logger.info(f"Template assignment updated: {assignment_id}")
        
        return self._row_to_assignment(result) if result else None

    async def remove_assignment(self, assignment_id: UUID) -> bool:
        """
        Remove a template assignment
        
        Args:
            assignment_id: ID of assignment to remove
            
        Returns:
            True if assignment was removed, False if not found
        """
        db = await self._get_db_connection()
        
        # Get assignment for cache invalidation
        assignment = await self.get_assignment(assignment_id)
        if not assignment:
            return False
        
        query = "DELETE FROM archon_template_assignments WHERE id = $1"
        result = await db.execute(query, assignment_id)
        
        if result == "DELETE 1":
            # Invalidate cache
            await self._invalidate_cache(assignment.entity_id, assignment.hierarchy_level)
            logger.info(f"Template assignment removed: {assignment_id}")
            return True
        
        return False

    async def assign_template_bulk(
        self,
        assignments: List[Dict[str, Any]],
        created_by: str = "system"
    ) -> List[TemplateAssignment]:
        """
        Assign multiple templates in bulk
        
        Args:
            assignments: List of assignment dictionaries
            created_by: Who created the assignments
            
        Returns:
            List of created template assignments
        """
        results = []
        
        for assignment_data in assignments:
            try:
                assignment = await self.assign_template(
                    template_name=assignment_data["template_name"],
                    hierarchy_level=HierarchyLevel(assignment_data["hierarchy_level"]),
                    entity_id=assignment_data.get("entity_id"),
                    assignment_scope=AssignmentScope(assignment_data.get("assignment_scope", "all")),
                    priority=assignment_data.get("priority", 0),
                    entity_type=assignment_data.get("entity_type"),
                    conditional_logic=assignment_data.get("conditional_logic"),
                    metadata=assignment_data.get("metadata"),
                    effective_from=assignment_data.get("effective_from"),
                    effective_until=assignment_data.get("effective_until"),
                    created_by=created_by
                )
                results.append(assignment)
            except Exception as e:
                logger.error(f"Failed to create bulk assignment: {e}")
                # Continue with other assignments
        
        return results

    async def _validate_template_exists(self, template_name: str) -> None:
        """Validate that template exists and is active"""
        db = await self._get_db_connection()
        
        query = """
        SELECT id FROM archon_template_definitions 
        WHERE name = $1 AND is_active = true
        """
        result = await db.fetchrow(query, template_name)
        
        if not result:
            raise ValueError(f"Template '{template_name}' not found or not active")

    async def _validate_assignment(
        self,
        template_name: str,
        hierarchy_level: HierarchyLevel,
        entity_id: Optional[UUID],
        assignment_scope: AssignmentScope,
        entity_type: Optional[str]
    ) -> None:
        """Validate assignment parameters"""
        
        # Global assignments should not have entity_id
        if hierarchy_level == HierarchyLevel.GLOBAL and entity_id is not None:
            raise ValueError("Global assignments cannot have entity_id")
        
        # Non-global assignments should have entity_id (except for specific_types scope)
        if (hierarchy_level != HierarchyLevel.GLOBAL and 
            assignment_scope != AssignmentScope.SPECIFIC_TYPES and 
            entity_id is None):
            raise ValueError(f"{hierarchy_level.value} assignments require entity_id")
        
        # Specific types scope requires entity_type
        if assignment_scope == AssignmentScope.SPECIFIC_TYPES and not entity_type:
            raise ValueError("specific_types scope requires entity_type")

    async def _invalidate_cache(
        self, 
        entity_id: Optional[UUID], 
        hierarchy_level: HierarchyLevel
    ) -> None:
        """Invalidate template assignment cache"""
        db = await self._get_db_connection()
        
        query = "SELECT invalidate_template_assignment_cache($1, $2)"
        await db.fetchval(query, entity_id, hierarchy_level.value)

    def _row_to_assignment(self, row) -> TemplateAssignment:
        """Convert database row to TemplateAssignment"""
        return TemplateAssignment(
            id=row["id"],
            entity_id=row["entity_id"],
            template_name=row["template_name"],
            hierarchy_level=HierarchyLevel(row["hierarchy_level"]),
            assignment_scope=AssignmentScope(row["assignment_scope"]),
            priority=row["priority"],
            inheritance_enabled=row["inheritance_enabled"],
            entity_type=row["entity_type"],
            conditional_logic=json.loads(row["conditional_logic"]) if row["conditional_logic"] else None,
            metadata=json.loads(row["metadata"]) if row["metadata"] else None,
            effective_from=row["effective_from"],
            effective_until=row["effective_until"],
            is_active=row["is_active"],
            created_by=row["created_by"],
            updated_by=row["updated_by"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def _generate_context_hash(self, context_data: Dict) -> str:
        """Generate hash for context data"""
        context_str = json.dumps(context_data, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()[:16]
