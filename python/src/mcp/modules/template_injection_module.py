"""
Template Injection MCP Tools

This module provides MCP tools for the Template Injection System:
- Template management with CRUD operations
- Component management and validation
- Template expansion preview and testing
- Integration with TemplateInjectionService backend
"""

import json
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from mcp.server.fastmcp import Context, FastMCP

# Import service discovery for HTTP calls
from src.server.config.service_discovery import get_api_url

logger = logging.getLogger(__name__)


def register_template_injection_tools(mcp: FastMCP):
    """Register template injection management tools with the MCP server."""

    @mcp.tool()
    async def manage_template_injection(
        ctx: Context,
        action: str,
        template_id: str = None,
        name: str = None,
        title: str = None,
        description: str = None,
        template_type: str = None,
        template_data: Dict[str, Any] = None,
        category: str = "general",
        tags: List[str] = None,
        is_public: bool = True,
        created_by: str = "AI IDE Agent",
        filter_by: str = None,
        filter_value: str = None,
        page: int = 1,
        per_page: int = 50,
    ) -> str:
        """
        Unified tool for template injection lifecycle management.

        🎯 TEMPLATE INJECTION MANAGEMENT:
        Manage workflow templates that inject standardized operational procedures
        around user tasks while preserving original intent.

        Actions:
        - create: Create new template with validation
        - list: List templates with filtering options
        - get: Get template details with expansion preview
        - update: Update template properties and content
        - delete: Delete template with dependency checking
        - validate: Validate template content and component references

        Args:
            action: Operation to perform (create, list, get, update, delete, validate)
            template_id: Template UUID (required for get, update, delete, validate)
            name: Template name (required for create, must be unique)
            title: Human-readable template title (required for create)
            description: Template description
            template_type: Template type (project, task, component)
            template_data: Template configuration and content as JSON
            category: Template category for organization
            tags: List of tags for categorization
            is_public: Whether template is publicly accessible
            created_by: Creator identifier
            filter_by: Filter type for list (name, type, category, created_by)
            filter_value: Filter value for list
            page: Page number for pagination
            per_page: Items per page (max 100)

        Returns:
            JSON string with operation results

        Examples:
            Create Default Workflow Template:
                manage_template_injection(
                    action="create",
                    name="workflow_default",
                    title="Default Template Injection Workflow",
                    description="Standard operational workflow for development tasks",
                    template_type="project",
                    template_data={
                        "template_content": "{{group::understand_homelab_env}}\\n\\n{{USER_TASK}}\\n\\n{{group::send_task_to_review}}",
                        "user_task_position": 2,
                        "estimated_duration": 30,
                        "required_tools": ["view", "manage_task_archon-prod"]
                    },
                    category="template-injection",
                    tags=["workflow", "default", "operational"]
                )

            List All Templates:
                manage_template_injection(action="list")

            Get Template Details:
                manage_template_injection(
                    action="get",
                    template_id="template-uuid"
                )

            Update Template:
                manage_template_injection(
                    action="update",
                    template_id="template-uuid",
                    description="Updated description",
                    template_data={"estimated_duration": 45}
                )

            Validate Template:
                manage_template_injection(
                    action="validate",
                    template_id="template-uuid"
                )

            Delete Template:
                manage_template_injection(
                    action="delete",
                    template_id="template-uuid"
                )
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            if action == "create":
                if not name:
                    return json.dumps({
                        "success": False,
                        "error": "name is required for create action"
                    })
                
                if not title:
                    return json.dumps({
                        "success": False,
                        "error": "title is required for create action"
                    })

                if not template_data:
                    return json.dumps({
                        "success": False,
                        "error": "template_data is required for create action"
                    })

                # Validate template_type
                valid_types = ["project", "task", "component"]
                if template_type and template_type not in valid_types:
                    return json.dumps({
                        "success": False,
                        "error": f"template_type must be one of: {', '.join(valid_types)}"
                    })

                # Call TemplateInjectionService to create template
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(api_url, "/api/template-injection/templates"),
                        json={
                            "name": name,
                            "title": title,
                            "description": description or "",
                            "template_type": template_type or "project",
                            "template_data": template_data,
                            "category": category,
                            "tags": tags or [],
                            "is_public": is_public,
                            "created_by": created_by
                        }
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "template": result.get("template"),
                            "message": result.get("message", "Template created successfully")
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to create template: {error_detail}"
                        })

            elif action == "list":
                params = {
                    "page": page,
                    "per_page": min(per_page, 100)
                }
                
                if filter_by and filter_value:
                    params[f"filter_{filter_by}"] = filter_value

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, "/api/template-injection/templates"),
                        params=params
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "templates": result.get("templates", []),
                            "pagination": result.get("pagination", {}),
                            "message": f"Found {len(result.get('templates', []))} templates"
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to list templates: {error_detail}"
                        })

            elif action == "get":
                if not template_id:
                    return json.dumps({
                        "success": False,
                        "error": "template_id is required for get action"
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, f"/api/template-injection/templates/{template_id}")
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "template": result.get("template"),
                            "message": "Template retrieved successfully"
                        })
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": "Template not found"
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to get template: {error_detail}"
                        })

            elif action == "update":
                if not template_id:
                    return json.dumps({
                        "success": False,
                        "error": "template_id is required for update action"
                    })

                update_data = {}
                if title is not None:
                    update_data["title"] = title
                if description is not None:
                    update_data["description"] = description
                if template_data is not None:
                    update_data["template_data"] = template_data
                if category is not None:
                    update_data["category"] = category
                if tags is not None:
                    update_data["tags"] = tags
                if is_public is not None:
                    update_data["is_public"] = is_public

                if not update_data:
                    return json.dumps({
                        "success": False,
                        "error": "At least one field must be provided for update"
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.put(
                        urljoin(api_url, f"/api/template-injection/templates/{template_id}"),
                        json=update_data
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "template": result.get("template"),
                            "message": result.get("message", "Template updated successfully")
                        })
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": "Template not found"
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to update template: {error_detail}"
                        })

            elif action == "validate":
                if not template_id:
                    return json.dumps({
                        "success": False,
                        "error": "template_id is required for validate action"
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(api_url, f"/api/template-injection/templates/{template_id}/validate")
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "validation": result.get("validation"),
                            "message": result.get("message", "Template validation completed")
                        })
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": "Template not found"
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to validate template: {error_detail}"
                        })

            elif action == "delete":
                if not template_id:
                    return json.dumps({
                        "success": False,
                        "error": "template_id is required for delete action"
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.delete(
                        urljoin(api_url, f"/api/template-injection/templates/{template_id}")
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "message": result.get("message", "Template deleted successfully")
                        })
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": "Template not found"
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to delete template: {error_detail}"
                        })

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown action: {action}. Valid actions: create, list, get, update, delete, validate"
                })

        except Exception as e:
            logger.error(f"Error in manage_template_injection: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.tool()
    async def expand_template_preview(
        ctx: Context,
        original_description: str,
        template_name: str = "workflow_default",
        project_id: str = None,
        context_data: Dict[str, Any] = None,
    ) -> str:
        """
        Preview template expansion without creating a task.

        🎯 TEMPLATE EXPANSION PREVIEW:
        Test template expansion with sample user tasks to validate
        template content and component references before deployment.

        Args:
            original_description: Original user task description to expand
            template_name: Template to use for expansion (default: workflow_default)
            project_id: Optional project UUID for context
            context_data: Optional context data for expansion

        Returns:
            JSON string with expansion preview results

        Examples:
            Preview Default Template:
                expand_template_preview(
                    original_description="Implement OAuth2 authentication",
                    template_name="workflow_default"
                )

            Preview with Project Context:
                expand_template_preview(
                    original_description="Create REST API endpoint",
                    template_name="workflow_default",
                    project_id="project-uuid",
                    context_data={"environment": "production"}
                )
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            if not original_description:
                return json.dumps({
                    "success": False,
                    "error": "original_description is required"
                })

            # Call TemplateInjectionService to expand template
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    urljoin(api_url, "/api/template-injection/expand-preview"),
                    json={
                        "original_description": original_description,
                        "template_name": template_name,
                        "project_id": project_id,
                        "context_data": context_data or {}
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        "expansion": result.get("expansion"),
                        "message": result.get("message", "Template expansion preview completed")
                    })
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"Failed to expand template: {error_detail}"
                    })

        except Exception as e:
            logger.error(f"Error in expand_template_preview: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.tool()
    async def manage_template_components(
        ctx: Context,
        action: str,
        component_id: str = None,
        name: str = None,
        description: str = None,
        component_type: str = None,
        instruction_text: str = None,
        required_tools: List[str] = None,
        estimated_duration: int = None,
        category: str = None,
        priority: str = None,
        tags: List[str] = None,
        filter_by: str = None,
        filter_value: str = None,
        page: int = 1,
        per_page: int = 50,
    ) -> str:
        """
        Unified tool for template component management.

        🎯 COMPONENT MANAGEMENT:
        Manage template components that provide reusable instruction blocks
        for building comprehensive operational workflows.

        Actions:
        - create: Create new component with validation
        - list: List components with filtering options
        - get: Get component details
        - update: Update component properties
        - delete: Delete component with dependency checking
        - validate: Validate component instruction and tool references

        Args:
            action: Operation to perform (create, list, get, update, delete, validate)
            component_id: Component UUID (required for get, update, delete, validate)
            name: Component name (required for create, format: type::name)
            description: Component description
            component_type: Component type (action, group, sequence)
            instruction_text: Full instruction text for the component
            required_tools: List of MCP tools needed for this component
            estimated_duration: Estimated duration in minutes
            category: Component category for organization
            priority: Priority level (low, medium, high, critical)
            tags: List of tags for categorization
            filter_by: Filter type for list (name, type, category, priority)
            filter_value: Filter value for list
            page: Page number for pagination
            per_page: Items per page (max 100)

        Returns:
            JSON string with operation results

        Examples:
            Create Component:
                manage_template_components(
                    action="create",
                    name="group::understand_homelab_env",
                    description="Review homelab environment and available services",
                    component_type="group",
                    instruction_text="Before starting implementation, review the homelab...",
                    required_tools=["view", "homelab-vault"],
                    estimated_duration=8,
                    category="preparation",
                    priority="high",
                    tags=["homelab", "infrastructure", "preparation"]
                )

            List Components by Category:
                manage_template_components(
                    action="list",
                    filter_by="category",
                    filter_value="testing"
                )

            Get Component Details:
                manage_template_components(
                    action="get",
                    component_id="component-uuid"
                )

            Update Component:
                manage_template_components(
                    action="update",
                    component_id="component-uuid",
                    estimated_duration=10,
                    priority="critical"
                )

            Validate Component:
                manage_template_components(
                    action="validate",
                    component_id="component-uuid"
                )

            Delete Component:
                manage_template_components(
                    action="delete",
                    component_id="component-uuid"
                )
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            if action == "create":
                if not name:
                    return json.dumps({
                        "success": False,
                        "error": "name is required for create action"
                    })

                if not instruction_text:
                    return json.dumps({
                        "success": False,
                        "error": "instruction_text is required for create action"
                    })

                # Validate component_type
                valid_types = ["action", "group", "sequence"]
                if component_type and component_type not in valid_types:
                    return json.dumps({
                        "success": False,
                        "error": f"component_type must be one of: {', '.join(valid_types)}"
                    })

                # Validate priority
                valid_priorities = ["low", "medium", "high", "critical"]
                if priority and priority not in valid_priorities:
                    return json.dumps({
                        "success": False,
                        "error": f"priority must be one of: {', '.join(valid_priorities)}"
                    })

                # Call TemplateInjectionService to create component
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(api_url, "/api/template-injection/components"),
                        json={
                            "name": name,
                            "description": description or "",
                            "component_type": component_type or "group",
                            "instruction_text": instruction_text,
                            "required_tools": required_tools or [],
                            "estimated_duration": estimated_duration or 5,
                            "category": category or "general",
                            "priority": priority or "medium",
                            "tags": tags or []
                        }
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
                params = {
                    "page": page,
                    "per_page": min(per_page, 100)
                }

                if filter_by and filter_value:
                    params[f"filter_{filter_by}"] = filter_value

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, "/api/template-injection/components"),
                        params=params
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "components": result.get("components", []),
                            "pagination": result.get("pagination", {}),
                            "message": f"Found {len(result.get('components', []))} components"
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to list components: {error_detail}"
                        })

            # Additional actions (get, update, delete, validate) would follow similar patterns
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Action '{action}' not yet implemented. Available: create, list"
                })

        except Exception as e:
            logger.error(f"Error in manage_template_components: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
