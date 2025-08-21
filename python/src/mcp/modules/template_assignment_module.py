"""
Template Assignment MCP Module

This module provides MCP tools for managing template assignments
at different hierarchy levels with inheritance resolution.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from mcp.server import Server
from server.services.template_assignment_service import (
    TemplateAssignmentService,
    HierarchyLevel,
    AssignmentScope
)
from server.services.template_resolver import TemplateResolver

logger = logging.getLogger(__name__)

# Initialize services
assignment_service = TemplateAssignmentService()
template_resolver = TemplateResolver()


def register_template_assignment_tools(app: Server):
    """Register template assignment MCP tools"""

    @app.tool()
    async def manage_template_assignment(
        action: str,
        template_name: Optional[str] = None,
        hierarchy_level: Optional[str] = None,
        entity_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        assignment_scope: str = "all",
        priority: int = 0,
        entity_type: Optional[str] = None,
        conditional_logic: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        effective_from: Optional[str] = None,
        effective_until: Optional[str] = None,
        is_active: Optional[bool] = None,
        assignments: Optional[List[Dict]] = None,
        created_by: str = "mcp_user"
    ) -> str:
        """
        Manage template assignments at different hierarchy levels
        
        Actions:
        - assign: Assign template to hierarchy level
        - list: List template assignments
        - get: Get specific assignment
        - update: Update assignment
        - remove: Remove assignment
        - bulk_assign: Assign multiple templates
        - validate: Validate assignments
        
        Args:
            action: Operation to perform
            template_name: Name of template to assign
            hierarchy_level: Level in hierarchy (global, project, milestone, phase, task)
            entity_id: ID of entity to assign to
            assignment_id: ID of assignment (for get/update/remove)
            assignment_scope: Scope of assignment (all, specific_types, conditional)
            priority: Priority for conflict resolution
            entity_type: Type of entity for specific_types scope
            conditional_logic: Logic for conditional assignments
            metadata: Additional metadata
            effective_from: When assignment becomes effective (ISO format)
            effective_until: When assignment expires (ISO format)
            is_active: Active status (for update)
            assignments: List of assignments for bulk operations
            created_by: Who created the assignment
            
        Returns:
            JSON string with operation results
        """
        try:
            if action == "assign":
                if not template_name or not hierarchy_level:
                    return json.dumps({
                        "success": False,
                        "error": "template_name and hierarchy_level are required for assign action"
                    })
                
                # Parse dates
                effective_from_dt = None
                effective_until_dt = None
                
                if effective_from:
                    try:
                        effective_from_dt = datetime.fromisoformat(effective_from.replace('Z', '+00:00'))
                    except ValueError:
                        return json.dumps({
                            "success": False,
                            "error": f"Invalid effective_from date format: {effective_from}"
                        })
                
                if effective_until:
                    try:
                        effective_until_dt = datetime.fromisoformat(effective_until.replace('Z', '+00:00'))
                    except ValueError:
                        return json.dumps({
                            "success": False,
                            "error": f"Invalid effective_until date format: {effective_until}"
                        })
                
                assignment = await assignment_service.assign_template(
                    template_name=template_name,
                    hierarchy_level=HierarchyLevel(hierarchy_level),
                    entity_id=UUID(entity_id) if entity_id else None,
                    assignment_scope=AssignmentScope(assignment_scope),
                    priority=priority,
                    entity_type=entity_type,
                    conditional_logic=conditional_logic,
                    metadata=metadata,
                    effective_from=effective_from_dt,
                    effective_until=effective_until_dt,
                    created_by=created_by
                )
                
                return json.dumps({
                    "success": True,
                    "assignment": {
                        "id": str(assignment.id),
                        "template_name": assignment.template_name,
                        "hierarchy_level": assignment.hierarchy_level.value,
                        "entity_id": str(assignment.entity_id) if assignment.entity_id else None,
                        "assignment_scope": assignment.assignment_scope.value,
                        "priority": assignment.priority,
                        "entity_type": assignment.entity_type,
                        "is_active": assignment.is_active,
                        "created_at": assignment.created_at.isoformat() if assignment.created_at else None
                    },
                    "message": f"Template assignment created: {template_name} -> {hierarchy_level}"
                })
            
            elif action == "list":
                assignments = await assignment_service.list_assignments(
                    hierarchy_level=HierarchyLevel(hierarchy_level) if hierarchy_level else None,
                    entity_id=UUID(entity_id) if entity_id else None,
                    template_name=template_name,
                    is_active=is_active if is_active is not None else True
                )
                
                return json.dumps({
                    "success": True,
                    "assignments": [
                        {
                            "id": str(assignment.id),
                            "template_name": assignment.template_name,
                            "hierarchy_level": assignment.hierarchy_level.value,
                            "entity_id": str(assignment.entity_id) if assignment.entity_id else None,
                            "assignment_scope": assignment.assignment_scope.value,
                            "priority": assignment.priority,
                            "entity_type": assignment.entity_type,
                            "is_active": assignment.is_active,
                            "effective_from": assignment.effective_from.isoformat() if assignment.effective_from else None,
                            "effective_until": assignment.effective_until.isoformat() if assignment.effective_until else None,
                            "created_at": assignment.created_at.isoformat() if assignment.created_at else None
                        }
                        for assignment in assignments
                    ],
                    "total": len(assignments)
                })
            
            elif action == "get":
                if not assignment_id:
                    return json.dumps({
                        "success": False,
                        "error": "assignment_id is required for get action"
                    })
                
                assignment = await assignment_service.get_assignment(UUID(assignment_id))
                
                if not assignment:
                    return json.dumps({
                        "success": False,
                        "error": f"Assignment not found: {assignment_id}"
                    })
                
                return json.dumps({
                    "success": True,
                    "assignment": {
                        "id": str(assignment.id),
                        "template_name": assignment.template_name,
                        "hierarchy_level": assignment.hierarchy_level.value,
                        "entity_id": str(assignment.entity_id) if assignment.entity_id else None,
                        "assignment_scope": assignment.assignment_scope.value,
                        "priority": assignment.priority,
                        "entity_type": assignment.entity_type,
                        "conditional_logic": assignment.conditional_logic,
                        "metadata": assignment.metadata,
                        "is_active": assignment.is_active,
                        "effective_from": assignment.effective_from.isoformat() if assignment.effective_from else None,
                        "effective_until": assignment.effective_until.isoformat() if assignment.effective_until else None,
                        "created_by": assignment.created_by,
                        "updated_by": assignment.updated_by,
                        "created_at": assignment.created_at.isoformat() if assignment.created_at else None,
                        "updated_at": assignment.updated_at.isoformat() if assignment.updated_at else None
                    }
                })
            
            elif action == "update":
                if not assignment_id:
                    return json.dumps({
                        "success": False,
                        "error": "assignment_id is required for update action"
                    })
                
                # Parse dates
                effective_from_dt = None
                effective_until_dt = None
                
                if effective_from:
                    try:
                        effective_from_dt = datetime.fromisoformat(effective_from.replace('Z', '+00:00'))
                    except ValueError:
                        return json.dumps({
                            "success": False,
                            "error": f"Invalid effective_from date format: {effective_from}"
                        })
                
                if effective_until:
                    try:
                        effective_until_dt = datetime.fromisoformat(effective_until.replace('Z', '+00:00'))
                    except ValueError:
                        return json.dumps({
                            "success": False,
                            "error": f"Invalid effective_until date format: {effective_until}"
                        })
                
                assignment = await assignment_service.update_assignment(
                    assignment_id=UUID(assignment_id),
                    template_name=template_name,
                    priority=priority if priority != 0 else None,
                    assignment_scope=AssignmentScope(assignment_scope) if assignment_scope != "all" else None,
                    entity_type=entity_type,
                    conditional_logic=conditional_logic,
                    metadata=metadata,
                    effective_from=effective_from_dt,
                    effective_until=effective_until_dt,
                    is_active=is_active,
                    updated_by=created_by
                )
                
                if not assignment:
                    return json.dumps({
                        "success": False,
                        "error": f"Assignment not found: {assignment_id}"
                    })
                
                return json.dumps({
                    "success": True,
                    "assignment": {
                        "id": str(assignment.id),
                        "template_name": assignment.template_name,
                        "hierarchy_level": assignment.hierarchy_level.value,
                        "entity_id": str(assignment.entity_id) if assignment.entity_id else None,
                        "assignment_scope": assignment.assignment_scope.value,
                        "priority": assignment.priority,
                        "is_active": assignment.is_active,
                        "updated_at": assignment.updated_at.isoformat() if assignment.updated_at else None
                    },
                    "message": f"Template assignment updated: {assignment_id}"
                })
            
            elif action == "remove":
                if not assignment_id:
                    return json.dumps({
                        "success": False,
                        "error": "assignment_id is required for remove action"
                    })
                
                success = await assignment_service.remove_assignment(UUID(assignment_id))
                
                if not success:
                    return json.dumps({
                        "success": False,
                        "error": f"Assignment not found: {assignment_id}"
                    })
                
                return json.dumps({
                    "success": True,
                    "message": f"Template assignment removed: {assignment_id}"
                })
            
            elif action == "bulk_assign":
                if not assignments:
                    return json.dumps({
                        "success": False,
                        "error": "assignments list is required for bulk_assign action"
                    })
                
                created_assignments = await assignment_service.assign_template_bulk(
                    assignments=assignments,
                    created_by=created_by
                )
                
                return json.dumps({
                    "success": True,
                    "assignments": [
                        {
                            "id": str(assignment.id),
                            "template_name": assignment.template_name,
                            "hierarchy_level": assignment.hierarchy_level.value,
                            "entity_id": str(assignment.entity_id) if assignment.entity_id else None
                        }
                        for assignment in created_assignments
                    ],
                    "total_created": len(created_assignments),
                    "message": f"Created {len(created_assignments)} template assignments"
                })
            
            elif action == "validate":
                # Validate all assignments
                all_assignments = await assignment_service.list_assignments(is_active=True)
                
                validation_results = []
                for assignment in all_assignments:
                    try:
                        # Basic validation - template exists
                        await assignment_service._validate_template_exists(assignment.template_name)
                        validation_results.append({
                            "assignment_id": str(assignment.id),
                            "template_name": assignment.template_name,
                            "valid": True,
                            "message": "Assignment is valid"
                        })
                    except Exception as e:
                        validation_results.append({
                            "assignment_id": str(assignment.id),
                            "template_name": assignment.template_name,
                            "valid": False,
                            "message": str(e)
                        })
                
                valid_count = sum(1 for result in validation_results if result["valid"])
                
                return json.dumps({
                    "success": True,
                    "validation_results": validation_results,
                    "total_assignments": len(validation_results),
                    "valid_assignments": valid_count,
                    "invalid_assignments": len(validation_results) - valid_count
                })
            
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown action: {action}. Supported actions: assign, list, get, update, remove, bulk_assign, validate"
                })
        
        except ValueError as e:
            return json.dumps({
                "success": False,
                "error": f"Invalid parameter: {str(e)}"
            })
        except Exception as e:
            logger.error(f"Template assignment operation failed: {e}")
            return json.dumps({
                "success": False,
                "error": f"Operation failed: {str(e)}"
            })

    @app.tool()
    async def resolve_template(
        entity_id: str,
        entity_type: str,
        project_id: Optional[str] = None,
        milestone_id: Optional[str] = None,
        phase_id: Optional[str] = None,
        context_data: Optional[Dict] = None,
        show_resolution_path: bool = False
    ) -> str:
        """
        Resolve template for an entity through inheritance hierarchy
        
        Args:
            entity_id: ID of the entity
            entity_type: Type of entity (task, project, etc.)
            project_id: ID of the project
            milestone_id: ID of the milestone
            phase_id: ID of the phase
            context_data: Additional context for resolution
            show_resolution_path: Include resolution path in response
            
        Returns:
            JSON string with resolved template information
        """
        try:
            resolution = await template_resolver.resolve_template(
                entity_id=UUID(entity_id),
                entity_type=entity_type,
                project_id=UUID(project_id) if project_id else None,
                milestone_id=UUID(milestone_id) if milestone_id else None,
                phase_id=UUID(phase_id) if phase_id else None,
                context_data=context_data or {}
            )
            
            result = {
                "success": True,
                "template_name": resolution.template_name,
                "hierarchy_level": resolution.hierarchy_level.value,
                "priority": resolution.priority,
                "cached": resolution.cached,
                "cache_hit": resolution.cache_hit
            }
            
            if show_resolution_path:
                result["resolution_path"] = resolution.resolution_path
            
            if resolution.assignment_id:
                result["assignment_id"] = str(resolution.assignment_id)
            
            return json.dumps(result)
        
        except Exception as e:
            logger.error(f"Template resolution failed: {e}")
            return json.dumps({
                "success": False,
                "error": f"Resolution failed: {str(e)}"
            })

    @app.tool()
    async def template_assignment_cache(
        action: str,
        entity_id: Optional[str] = None,
        hierarchy_level: Optional[str] = None
    ) -> str:
        """
        Manage template assignment cache
        
        Actions:
        - invalidate: Invalidate cache entries
        - cleanup: Clean up expired entries
        - stats: Get cache statistics
        
        Args:
            action: Cache operation to perform
            entity_id: Optional entity ID for invalidation
            hierarchy_level: Optional hierarchy level for invalidation
            
        Returns:
            JSON string with cache operation results
        """
        try:
            if action == "invalidate":
                count = await template_resolver.invalidate_cache(
                    entity_id=UUID(entity_id) if entity_id else None,
                    hierarchy_level=HierarchyLevel(hierarchy_level) if hierarchy_level else None
                )
                
                return json.dumps({
                    "success": True,
                    "invalidated_entries": count,
                    "message": f"Invalidated {count} cache entries"
                })
            
            elif action == "cleanup":
                count = await template_resolver.cleanup_expired_cache()
                
                return json.dumps({
                    "success": True,
                    "cleaned_entries": count,
                    "message": f"Cleaned up {count} expired cache entries"
                })
            
            elif action == "stats":
                stats = await template_resolver.get_cache_statistics()
                
                return json.dumps({
                    "success": True,
                    "cache_statistics": stats
                })
            
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown action: {action}. Supported actions: invalidate, cleanup, stats"
                })
        
        except Exception as e:
            logger.error(f"Cache operation failed: {e}")
            return json.dumps({
                "success": False,
                "error": f"Cache operation failed: {str(e)}"
            })
