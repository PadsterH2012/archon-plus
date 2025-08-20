"""
Template Management MCP Tools

This module provides MCP tools for template system management:
- Template CRUD operations with inheritance support
- Template application to components with customizations
- Template inheritance resolution and conflict detection
- Integration with TemplateService backend
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


def register_template_tools(mcp: FastMCP):
    """Register template management tools with the MCP server."""

    @mcp.tool()
    async def manage_template(
        action: str,
        template_id: str = None,
        name: str = None,
        title: str = None,
        description: str = None,
        template_type: str = None,
        parent_template_id: str = None,
        workflow_assignments: Dict[str, Any] = None,
        component_templates: Dict[str, Any] = None,
        inheritance_rules: Dict[str, Any] = None,
        is_public: bool = None,
        filter_by: str = None,
        filter_value: str = None,
        include_inheritance: bool = True,
        page: int = 1,
        per_page: int = 50,
    ) -> str:
        """
        Unified tool for template lifecycle management with inheritance resolution.

        🎯 TEMPLATE INHERITANCE SYSTEM:
        Templates support 3-level inheritance hierarchy:
        - Global → Industry → Team → Project templates
        - Child templates override parent configurations
        - Automatic conflict detection and resolution
        - Template customization tracking

        ⚡ PERFORMANCE OPTIMIZED:
        - Template resolution caching (1 hour TTL)
        - Inheritance chain caching (1 hour TTL)
        - Efficient conflict detection algorithms
        - <50ms template resolution time

        Args:
            action: Template operation - "create" | "list" | "get" | "update" | "delete" | "resolve"
                   - create: Create new template with inheritance validation
                   - list: Retrieve templates with filtering and pagination
                   - get: Fetch complete template details with inheritance
                   - update: Modify template properties with validation
                   - delete: Remove template (checks for dependents)
                   - resolve: Resolve template inheritance chain

            template_id: UUID of the template (required for get/update/delete/resolve operations)

            name: Template name (required for create, optional for update)
                  Should be unique and descriptive (e.g., "OAuth2-API-Template", "React-Dashboard-Base")

            title: Human-readable template title (required for create, optional for update)

            description: Detailed template description (for create/update)

            template_type: Template type - "global_default" | "industry" | "team" | "personal" | "community"
                          - global_default: System-wide base templates
                          - industry: Industry-specific templates (e.g., fintech, healthcare)
                          - team: Team-specific templates
                          - personal: User-specific templates
                          - community: Shared community templates

            parent_template_id: UUID of parent template for inheritance
                               Automatically validated for circular inheritance

            workflow_assignments: Workflow configuration as JSON object
                                 Maps workflow names to agent assignments and configurations

            component_templates: Component template definitions as JSON object
                                Maps component types to template configurations

            inheritance_rules: Inheritance behavior rules as JSON object
                              Controls how child templates override parent configurations

            is_public: Whether template is publicly accessible (default: False)

            filter_by: List filtering type - "type" | "status" | "public"
            filter_value: Value for the filter

            include_inheritance: Include inheritance chain information (default: True)

            page: Page number for pagination (default: 1)
            per_page: Items per page (default: 50, max: 100)

        Returns:
            JSON string with template operation results:
            - success: Boolean indicating operation success
            - template/templates: Template object(s) with complete metadata
            - inheritance_chain: Inheritance information (if include_inheritance=True)
            - resolved_config: Resolved template configuration (for resolve action)
            - conflicts: Detected conflicts in inheritance chain
            - pagination: Pagination info for list operations
            - message: Human-readable status message
            - error: Error description (if success=false)

        🎯 COMPREHENSIVE EXAMPLES:

        Create Global Base Template:
            manage_template(
                action="create",
                name="web-api-base",
                title="Web API Base Template",
                description="Foundation template for RESTful API projects with authentication, logging, and testing",
                template_type="global_default",
                workflow_assignments={
                    "setup": {"agent": "prp-executor", "priority": "high"},
                    "development": {"agent": "AI IDE Agent", "parallel": True},
                    "testing": {"agent": "prp-validator", "gates": ["unit_tests", "integration_tests"]},
                    "deployment": {"agent": "prp-executor", "environment": "staging"}
                },
                component_templates={
                    "foundation": {
                        "database": {"type": "PostgreSQL", "migrations": True},
                        "authentication": {"type": "JWT", "providers": ["local", "oauth2"]},
                        "logging": {"level": "info", "format": "structured"}
                    },
                    "feature": {
                        "api_endpoints": {"versioning": "v1", "documentation": "OpenAPI"},
                        "validation": {"input": "pydantic", "output": "serializers"}
                    }
                },
                inheritance_rules={
                    "override_policy": "child_wins",
                    "merge_arrays": True,
                    "preserve_parent_metadata": True
                },
                is_public=True
            )

        Create Industry-Specific Template:
            manage_template(
                action="create",
                name="fintech-api-template",
                title="FinTech API Template",
                description="Financial services API template with compliance, security, and audit requirements",
                template_type="industry",
                parent_template_id="web-api-base-uuid",
                workflow_assignments={
                    "compliance_review": {"agent": "prp-validator", "required": True},
                    "security_audit": {"agent": "security-specialist", "gates": ["penetration_test", "code_review"]}
                },
                component_templates={
                    "foundation": {
                        "security": {"encryption": "AES-256", "key_management": "HSM"},
                        "compliance": {"standards": ["PCI-DSS", "SOX"], "audit_logging": True}
                    },
                    "feature": {
                        "payment_processing": {"providers": ["stripe", "plaid"], "fraud_detection": True},
                        "reporting": {"formats": ["PDF", "CSV"], "scheduling": True}
                    }
                },
                is_public=False
            )

        List Templates by Type:
            manage_template(
                action="list",
                filter_by="type",
                filter_value="industry",
                include_inheritance=True,
                per_page=25
            )

        Get Template with Inheritance:
            manage_template(
                action="get",
                template_id="tmpl-123e4567-e89b-12d3-a456-426614174000",
                include_inheritance=True
            )

        Resolve Template Inheritance:
            manage_template(
                action="resolve",
                template_id="tmpl-123e4567-e89b-12d3-a456-426614174000"
            )
            # Returns: Complete resolved configuration with inheritance applied

        Update Template Configuration:
            manage_template(
                action="update",
                template_id="tmpl-123e4567-e89b-12d3-a456-426614174000",
                workflow_assignments={
                    "deployment": {"agent": "prp-executor", "environment": "production", "approval_required": True}
                },
                component_templates={
                    "infrastructure": {
                        "monitoring": {"provider": "datadog", "alerts": True},
                        "scaling": {"auto_scaling": True, "max_instances": 10}
                    }
                }
            )

        Delete Template (with dependency check):
            manage_template(
                action="delete",
                template_id="tmpl-123e4567-e89b-12d3-a456-426614174000"
            )
            # Note: Will fail if other templates inherit from this one
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

                # Validate template_type
                valid_types = ["global_default", "industry", "team", "personal", "community"]
                if template_type and template_type not in valid_types:
                    return json.dumps({
                        "success": False,
                        "error": f"template_type must be one of: {', '.join(valid_types)}"
                    })

                # Build create request
                create_data = {
                    "name": name,
                    "title": title,
                    "description": description or "",
                    "template_type": template_type or "personal",
                    "parent_template_id": parent_template_id,
                    "workflow_assignments": workflow_assignments or {},
                    "component_templates": component_templates or {},
                    "inheritance_rules": inheritance_rules or {},
                    "is_public": is_public if is_public is not None else False
                }

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        urljoin(api_url, "/api/templates"),
                        json=create_data
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
                # Build query parameters
                params = {
                    "include_inheritance": include_inheritance,
                    "page": page,
                    "per_page": min(per_page, 100)  # Cap at 100
                }

                if filter_by and filter_value:
                    params["filter_by"] = filter_by
                    params["filter_value"] = filter_value

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, "/api/templates"),
                        params=params
                    )

                    if response.status_code == 200:
                        result = response.json()
                        templates = result.get("templates", [])
                        pagination_info = result.get("pagination")

                        return json.dumps({
                            "success": True,
                            "templates": templates,
                            "pagination": pagination_info,
                            "total_count": len(templates) if pagination_info is None else pagination_info.get("total", len(templates))
                        })
                    else:
                        return json.dumps({
                            "success": False,
                            "error": "Failed to list templates"
                        })

            elif action == "get":
                if not template_id:
                    return json.dumps({
                        "success": False,
                        "error": "template_id is required for get action"
                    })

                params = {"include_inheritance": include_inheritance}

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, f"/api/templates/{template_id}"),
                        params=params
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "template": result.get("template"),
                            "inheritance_chain": (
                                result.get("inheritance_chain", []) if include_inheritance else []
                            )
                        })
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": f"Template {template_id} not found"
                        })
                    else:
                        return json.dumps({
                            "success": False,
                            "error": "Failed to get template"
                        })

            elif action == "resolve":
                if not template_id:
                    return json.dumps({
                        "success": False,
                        "error": "template_id is required for resolve action"
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        urljoin(api_url, f"/api/templates/{template_id}/resolve")
                    )

                    if response.status_code == 200:
                        result = response.json()
                        return json.dumps({
                            "success": True,
                            "resolved_config": result.get("resolved_config"),
                            "inheritance_chain": result.get("inheritance_chain", []),
                            "conflicts": result.get("conflicts", {}),
                            "message": "Template inheritance resolved successfully"
                        })
                    elif response.status_code == 404:
                        return json.dumps({
                            "success": False,
                            "error": f"Template {template_id} not found"
                        })
                    else:
                        return json.dumps({
                            "success": False,
                            "error": "Failed to resolve template inheritance"
                        })

            elif action == "update":
                if not template_id:
                    return json.dumps({
                        "success": False,
                        "error": "template_id is required for update action"
                    })

                # Validate template_type if provided
                if template_type:
                    valid_types = ["global_default", "industry", "team", "personal", "community"]
                    if template_type not in valid_types:
                        return json.dumps({
                            "success": False,
                            "error": f"template_type must be one of: {', '.join(valid_types)}"
                        })

                # Build update data (only include provided fields)
                update_data = {}
                if name is not None:
                    update_data["name"] = name
                if title is not None:
                    update_data["title"] = title
                if description is not None:
                    update_data["description"] = description
                if template_type is not None:
                    update_data["template_type"] = template_type
                if parent_template_id is not None:
                    update_data["parent_template_id"] = parent_template_id
                if workflow_assignments is not None:
                    update_data["workflow_assignments"] = workflow_assignments
                if component_templates is not None:
                    update_data["component_templates"] = component_templates
                if inheritance_rules is not None:
                    update_data["inheritance_rules"] = inheritance_rules
                if is_public is not None:
                    update_data["is_public"] = is_public

                if not update_data:
                    return json.dumps({
                        "success": False,
                        "error": "At least one field must be provided for update"
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.put(
                        urljoin(api_url, f"/api/templates/{template_id}"),
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
                            "error": f"Template {template_id} not found"
                        })
                    else:
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Failed to update template: {error_detail}"
                        })

            elif action == "delete":
                if not template_id:
                    return json.dumps({
                        "success": False,
                        "error": "template_id is required for delete action"
                    })

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.delete(
                        urljoin(api_url, f"/api/templates/{template_id}")
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
                            "error": f"Template {template_id} not found"
                        })
                    elif response.status_code == 400:
                        # Inheritance validation error
                        error_detail = response.text
                        return json.dumps({
                            "success": False,
                            "error": f"Cannot delete template: {error_detail}"
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
                    "error": f"Unknown action: {action}. Supported actions: "
                             f"create, list, get, update, delete, resolve"
                })

        except Exception as e:
            logger.error(f"Error in manage_template: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    @mcp.tool()
    async def apply_template(
        template_id: str,
        project_id: str = None,
        component_id: str = None,
        customizations: Dict[str, Any] = None,
        preview_only: bool = False,
        applied_by: str = "AI IDE Agent",
    ) -> str:
        """
        Apply a template to a project or component with customizations.

        🎯 TEMPLATE APPLICATION SYSTEM:
        Templates can be applied to projects or individual components with:
        - Inheritance resolution and conflict detection
        - Customization support for overriding template defaults
        - Preview mode for validation before application
        - Application tracking and audit trail

        Args:
            template_id: UUID of the template to apply (required)

            project_id: UUID of the project to apply template to
                       Required if component_id is not provided

            component_id: UUID of the component to apply template to
                         Required if project_id is not provided

            customizations: Custom overrides for template configuration
                          JSON object with same structure as template configuration
                          Overrides are merged with resolved template configuration

            preview_only: If True, returns preview without applying (default: False)
                         Useful for validation and conflict detection

            applied_by: Identifier of who/what is applying the template

        Returns:
            JSON string with application results:
            - success: Boolean indicating operation success
            - application: Application record (if not preview_only)
            - preview: Preview of resolved configuration (if preview_only=True)
            - conflicts: Any conflicts detected during resolution
            - customizations_applied: Summary of customizations applied
            - message: Human-readable status message
            - error: Error description (if success=false)

        Examples:
            Apply Template to Project:
                apply_template(
                    template_id="tmpl-123e4567-e89b-12d3-a456-426614174000",
                    project_id="proj-456e7890-e12b-34c5-a678-901234567890",
                    customizations={
                        "workflow_assignments": {
                            "deployment": {"environment": "production", "approval_required": True}
                        },
                        "component_templates": {
                            "infrastructure": {
                                "database": {"instance_type": "db.r5.large", "backup_retention": 30}
                            }
                        }
                    },
                    applied_by="project-manager"
                )

            Preview Template Application:
                apply_template(
                    template_id="tmpl-123e4567-e89b-12d3-a456-426614174000",
                    component_id="comp-789a0123-b45c-67d8-e901-234567890123",
                    preview_only=True
                )

            Apply Template to Component:
                apply_template(
                    template_id="tmpl-123e4567-e89b-12d3-a456-426614174000",
                    component_id="comp-789a0123-b45c-67d8-e901-234567890123",
                    customizations={
                        "completion_gates": ["custom_validation", "performance_test"],
                        "context_data": {
                            "custom_config": {"timeout": 30, "retries": 3}
                        }
                    }
                )
        """
        try:
            api_url = get_api_url()
            timeout = httpx.Timeout(30.0, connect=5.0)

            if not template_id:
                return json.dumps({
                    "success": False,
                    "error": "template_id is required"
                })

            if not project_id and not component_id:
                return json.dumps({
                    "success": False,
                    "error": "Either project_id or component_id must be provided"
                })

            if project_id and component_id:
                return json.dumps({
                    "success": False,
                    "error": "Cannot specify both project_id and component_id"
                })

            # Build application request
            apply_data = {
                "template_id": template_id,
                "customizations": customizations or {},
                "preview_only": preview_only,
                "applied_by": applied_by
            }

            if project_id:
                apply_data["project_id"] = project_id
            if component_id:
                apply_data["component_id"] = component_id

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    urljoin(api_url, "/api/templates/apply"),
                    json=apply_data
                )

                if response.status_code == 200:
                    result = response.json()
                    return json.dumps({
                        "success": True,
                        **result,
                        "message": result.get(
                            "message",
                            ("Template applied successfully" if not preview_only
                             else "Template preview generated")
                        )
                    })
                elif response.status_code == 404:
                    return json.dumps({
                        "success": False,
                        "error": "Template, project, or component not found"
                    })
                else:
                    error_detail = response.text
                    return json.dumps({
                        "success": False,
                        "error": f"Failed to apply template: {error_detail}"
                    })

        except Exception as e:
            logger.error(f"Error in apply_template: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    logger.info("✓ Template Module registered with 2 tools")
