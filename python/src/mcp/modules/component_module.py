"""
Component Management MCP Tools

This module provides MCP tools for component hierarchy management:
- Component CRUD operations
- Dependency management and validation
- Component status tracking and lifecycle management
- Integration with ComponentService backend
"""

import json
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from fastmcp import FastMCP
from urllib.parse import urljoin

from ...config.logfire_config import get_logger
from ...config.api import get_api_url

logger = get_logger(__name__)


def register_component_tools(mcp: FastMCP):
    """Register component management tools with the MCP server."""

    @mcp.tool()
    async def manage_component(
        action: str,
        project_id: str = None,
        component_id: str = None,
        name: str = None,
        description: str = None,
        component_type: str = None,
        status: str = None,
        dependencies: List[str] = None,
        completion_gates: List[str] = None,
        context_data: Dict[str, Any] = None,
        order_index: int = None,
        filter_by: str = None,
        filter_value: str = None,
        include_dependencies: bool = True,
        page: int = 1,
        per_page: int = 50,
    ) -> str:
        """
        Unified tool for component lifecycle management with dependency validation.

        🏗️ COMPONENT HIERARCHY MANAGEMENT:
        Components form the building blocks of Archon projects with:
        - Hierarchical dependency relationships
        - Automatic circular dependency detection
        - Completion gate validation
        - Status lifecycle tracking
        - Template-based configuration

        ⚡ PERFORMANCE OPTIMIZED:
        - Multi-level caching for <100ms operations
        - Efficient dependency graph resolution
        - Batch operations for bulk updates
        - Smart cache invalidation

        Args:
            action: Component operation - "create" | "list" | "get" | "update" | "delete"
                   - create: Create new component with dependency validation
                   - list: Retrieve components with filtering and pagination
                   - get: Fetch complete component details with dependencies
                   - update: Modify component properties with validation
                   - delete: Remove component (checks for dependents)

            project_id: UUID of the project (required for create/list operations)

            component_id: UUID of the component (required for get/update/delete operations)

            name: Component name (required for create, optional for update)
                  Should be descriptive and specific (e.g., "OAuth2 Authentication", "User Dashboard API")

            description: Detailed component description (for create/update)

            component_type: Component type - "foundation" | "feature" | "integration" | "infrastructure" | "testing"
                           - foundation: Core system components
                           - feature: User-facing functionality
                           - integration: External service connections
                           - infrastructure: Deployment and operations
                           - testing: Quality assurance components

            status: Component status - "not_started" | "in_progress" | "gates_passed" | "completed" | "blocked"

            dependencies: List of component UUIDs this component depends on
                         Automatically validated for circular dependencies

            completion_gates: List of gates that must pass for completion
                            Examples: ["tests_passing", "code_review_approved", "dependencies_completed"]

            context_data: Additional component context as JSON object
                         Can include configuration, requirements, or custom metadata

            order_index: Display order within project (integer, default: 0)

            filter_by: List filtering type - "status" | "type" | "project"
            filter_value: Value for the filter

            include_dependencies: Include dependency information in responses (default: True)

            page: Page number for pagination (default: 1)
            per_page: Items per page (default: 50, max: 100)

        Returns:
            JSON string with component operation results:
            - success: Boolean indicating operation success
            - component/components: Component object(s) with complete metadata
            - dependencies: Dependency information (if include_dependencies=True)
            - pagination: Pagination info for list operations
            - message: Human-readable status message
            - error: Error description (if success=false)

        🏗️ COMPREHENSIVE EXAMPLES:

        Create Foundation Component:
            manage_component(
                action="create",
                project_id="550e8400-e29b-41d4-a716-446655440000",
                name="Database Schema",
                description="Core database schema with user management, authentication, and audit tables",
                component_type="foundation",
                completion_gates=["schema_validated", "migrations_tested", "performance_benchmarked"],
                context_data={
                    "database_type": "PostgreSQL",
                    "schema_version": "1.0",
                    "tables": ["users", "sessions", "audit_log"],
                    "performance_requirements": {
                        "max_query_time": "100ms",
                        "concurrent_users": 1000
                    }
                },
                order_index=1
            )

        Create Feature Component with Dependencies:
            manage_component(
                action="create",
                project_id="550e8400-e29b-41d4-a716-446655440000",
                name="User Authentication API",
                description="RESTful API for user registration, login, and session management",
                component_type="feature",
                dependencies=["database-schema-uuid"],
                completion_gates=["api_tests_passing", "security_review_approved", "documentation_complete"],
                context_data={
                    "api_version": "v1",
                    "endpoints": ["/auth/register", "/auth/login", "/auth/logout"],
                    "security_requirements": ["JWT tokens", "Rate limiting", "Input validation"]
                },
                order_index=10
            )

        List Components by Status:
            manage_component(
                action="list",
                project_id="550e8400-e29b-41d4-a716-446655440000",
                filter_by="status",
                filter_value="in_progress",
                include_dependencies=True,
                per_page=25
            )

        Get Component with Dependencies:
            manage_component(
                action="get",
                component_id="comp-123e4567-e89b-12d3-a456-426614174000",
                include_dependencies=True
            )

        Update Component Status:
            manage_component(
                action="update",
                component_id="comp-123e4567-e89b-12d3-a456-426614174000",
                status="gates_passed",
                context_data={
                    "completion_notes": "All tests passing, security review approved",
                    "next_steps": ["Deploy to staging", "Performance testing"]
                }
            )

        Delete Component (with dependency check):
            manage_component(
                action="delete",
                component_id="comp-123e4567-e89b-12d3-a456-426614174000"
            )
            # Note: Will fail if other components depend on this one
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            if action == "create":
                if not project_id:
                    return json.dumps({
                        "success": False,
                        "error": "project_id is required for create action"
                    })
                
                if not name:
                    return json.dumps({
                        "success": False,
                        "error": "name is required for create action"
                    })

                # Validate component_type
                valid_types = ["foundation", "feature", "integration", "infrastructure", "testing"]
                if component_type and component_type not in valid_types:
                    return json.dumps({
                        "success": False,
                        "error": f"component_type must be one of: {', '.join(valid_types)}"
                    })

                # Build create request
                create_data = {
                    "project_id": project_id,
                    "name": name,
                    "description": description or "",
                    "component_type": component_type or "feature",
                    "dependencies": dependencies or [],
                    "completion_gates": completion_gates or [],
                    "context_data": context_data or {},
                    "order_index": order_index or 0
                }

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(api_url, "/api/components"),
                        json=create_data
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "component": result.get("component"),
                            "message": result.get("message", "Component created successfully")
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to create component: {error_detail}"
                        })

            elif action == "list":
                if not project_id:
                    return json.dumps({
                        "success": False,
                        "error": "project_id is required for list action"
                    })

                # Build query parameters
                params = {
                    "project_id": project_id,
                    "include_dependencies": include_dependencies,
                    "page": page,
                    "per_page": min(per_page, 100)  # Cap at 100
                }

                if filter_by and filter_value:
                    params["filter_by"] = filter_by
                    params["filter_value"] = filter_value

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, "/api/components"),
                        params=params
                    )

                    if response.status_code == 200:
                        result = response.json()
                        components = result.get("components", [])
                        pagination_info = result.get("pagination")

                        return json.dumps({
                            "success": True,
                            "components": components,
                            "pagination": pagination_info,
                            "total_count": len(components) if pagination_info is None else pagination_info.get("total", len(components))
                        })
                    else:
                        return json.dumps({
                            "success": False,
                            "error": "Failed to list components"
                        })

            elif action == "get":
                if not component_id:
                    return json.dumps({
                        "success": False,
                        "error": "component_id is required for get action"
                    })

                params = {"include_dependencies": include_dependencies}

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, f"/api/components/{component_id}"),
                        params=params
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "component": result.get("component"),
                            "dependencies": result.get("dependencies", []) if include_dependencies else []
                        })
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": f"Component {component_id} not found"
                        })
                    else:
                        return json.dumps({
                            "success": False,
                            "error": "Failed to get component"
                        })

            elif action == "update":
                if not component_id:
                    return json.dumps({
                        "success": False,
                        "error": "component_id is required for update action"
                    })

                # Validate component_type if provided
                if component_type:
                    valid_types = [
                        "foundation", "feature", "integration", "infrastructure", "testing"
                    ]
                    if component_type not in valid_types:
                        return json.dumps({
                            "success": False,
                            "error": f"component_type must be one of: {', '.join(valid_types)}"
                        })

                # Validate status if provided
                if status:
                    valid_statuses = [
                        "not_started", "in_progress", "gates_passed", "completed", "blocked"
                    ]
                    if status not in valid_statuses:
                        return json.dumps({
                            "success": False,
                            "error": f"status must be one of: {', '.join(valid_statuses)}"
                        })

                # Build update data (only include provided fields)
                update_data = {}
                if name is not None:
                    update_data["name"] = name
                if description is not None:
                    update_data["description"] = description
                if component_type is not None:
                    update_data["component_type"] = component_type
                if status is not None:
                    update_data["status"] = status
                if dependencies is not None:
                    update_data["dependencies"] = dependencies
                if completion_gates is not None:
                    update_data["completion_gates"] = completion_gates
                if context_data is not None:
                    update_data["context_data"] = context_data
                if order_index is not None:
                    update_data["order_index"] = order_index

                if not update_data:
                    return json.dumps({
                        "success": False,
                        "error": "At least one field must be provided for update"
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.put(
                        urljoin(api_url, f"/api/components/{component_id}"),
                        json=update_data
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "component": result.get("component"),
                            "message": result.get("message", "Component updated successfully")
                        })
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": f"Component {component_id} not found"
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to update component: {error_detail}"
                        })

            elif action == "delete":
                if not component_id:
                    return json.dumps({
                        "success": False,
                        "error": "component_id is required for delete action"
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.delete(
                        urljoin(api_url, f"/api/components/{component_id}")
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "message": result.get("message", "Component deleted successfully")
                        })
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": f"Component {component_id} not found"
                        })
                    elif response.status_code == 400:
                        # Dependency validation error
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Cannot delete component: {error_detail}"
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to delete component: {error_detail}"
                        })

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown action: {action}. Supported actions: "
                             f"create, list, get, update, delete"
                })

        except Exception as e:
            logger.error(f"Error in manage_component: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    logger.info("✓ Component Module registered with 1 tool")
