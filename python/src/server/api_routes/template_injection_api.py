"""
Template Injection API Routes

Provides REST API endpoints for template injection management that MCP tools expect.
These endpoints bridge the MCP tools with the existing template management services.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from ..utils import get_supabase_client
from ..services.template_injection_service import TemplateInjectionService
# from ..services.template_assignment_service import TemplateAssignmentService  # TODO: Fix import issues

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/template-injection", tags=["template-injection"])


# Request/Response Models
class CreateTemplateRequest(BaseModel):
    name: str = Field(..., description="Unique template name")
    title: str = Field(..., description="Human-readable template title")
    description: Optional[str] = Field(None, description="Template description")
    template_type: str = Field("project", description="Template type")
    template_data: Dict[str, Any] = Field(..., description="Template configuration")
    category: str = Field("general", description="Template category")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    is_public: bool = Field(True, description="Whether template is public")
    created_by: str = Field("AI IDE Agent", description="Creator identifier")


class UpdateTemplateRequest(BaseModel):
    title: Optional[str] = Field(None, description="Human-readable template title")
    description: Optional[str] = Field(None, description="Template description")
    template_type: Optional[str] = Field(None, description="Template type")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Template configuration")
    category: Optional[str] = Field(None, description="Template category")
    tags: Optional[List[str]] = Field(None, description="Template tags")
    is_public: Optional[bool] = Field(None, description="Whether template is public")


class CreateComponentRequest(BaseModel):
    name: str = Field(..., description="Component name (format: type::name)")
    description: str = Field("", description="Component description")
    component_type: str = Field("group", description="Component type")
    instruction_text: Optional[str] = Field(None, description="Instruction text")
    required_tools: List[str] = Field(default_factory=list, description="Required tools")
    estimated_duration: int = Field(5, description="Estimated duration in minutes")
    category: str = Field("general", description="Component category")
    priority: str = Field("medium", description="Priority level")
    tags: List[str] = Field(default_factory=list, description="Component tags")


class UpdateComponentRequest(BaseModel):
    description: Optional[str] = Field(None, description="Component description")
    component_type: Optional[str] = Field(None, description="Component type")
    instruction_text: Optional[str] = Field(None, description="Instruction text")
    required_tools: Optional[List[str]] = Field(None, description="Required tools")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration")
    category: Optional[str] = Field(None, description="Component category")
    priority: Optional[str] = Field(None, description="Priority level")
    tags: Optional[List[str]] = Field(None, description="Component tags")


class ExpandPreviewRequest(BaseModel):
    original_description: str = Field(..., description="Original task description")
    template_name: str = Field("workflow_default", description="Template to use")
    project_id: Optional[str] = Field(None, description="Project UUID for context")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Context data")


# Template Endpoints
@router.post("/templates")
async def create_template(
    request: CreateTemplateRequest,
    supabase=Depends(get_supabase_client)
):
    """Create a new template definition."""
    try:
        # Insert into archon_template_definitions table
        result = supabase.table("archon_template_definitions").insert({
            "name": request.name,
            "title": request.title,
            "description": request.description,
            "template_type": request.template_type,
            "template_data": request.template_data,
            "category": request.category,
            "tags": request.tags,
            "is_public": request.is_public,
            "created_by": request.created_by
        }).execute()

        if result.data:
            return {
                "success": True,
                "template": result.data[0],
                "message": "Template created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create template")

    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    filter_name: Optional[str] = Query(None, description="Filter by name"),
    filter_type: Optional[str] = Query(None, description="Filter by type"),
    filter_category: Optional[str] = Query(None, description="Filter by category"),
    filter_created_by: Optional[str] = Query(None, description="Filter by creator"),
    supabase=Depends(get_supabase_client)
):
    """List template definitions with filtering and pagination."""
    try:
        query = supabase.table("archon_template_definitions").select("*")

        # Apply filters
        if filter_name:
            query = query.ilike("name", f"%{filter_name}%")
        if filter_type:
            query = query.eq("template_type", filter_type)
        if filter_category:
            query = query.eq("category", filter_category)
        if filter_created_by:
            query = query.eq("created_by", filter_created_by)

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        return {
            "success": True,
            "templates": result.data or [],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": len(result.data) if result.data else 0
            },
            "message": f"Found {len(result.data) if result.data else 0} templates"
        }

    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    supabase=Depends(get_supabase_client)
):
    """Get a specific template by ID."""
    try:
        result = supabase.table("archon_template_definitions").select("*").eq("id", template_id).execute()

        if result.data:
            return {
                "success": True,
                "template": result.data[0],
                "message": "Template retrieved successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/templates/{template_id}")
async def update_template(
    template_id: str,
    request: UpdateTemplateRequest,
    supabase=Depends(get_supabase_client)
):
    """Update a template definition."""
    try:
        # Build update data from non-None fields
        update_data = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        result = supabase.table("archon_template_definitions").update(update_data).eq("id", template_id).execute()

        if result.data:
            return {
                "success": True,
                "template": result.data[0],
                "message": "Template updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    supabase=Depends(get_supabase_client)
):
    """Delete a template definition."""
    try:
        result = supabase.table("archon_template_definitions").delete().eq("id", template_id).execute()

        if result.data:
            return {
                "success": True,
                "message": "Template deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/validate")
async def validate_template(
    template_id: str,
    supabase=Depends(get_supabase_client)
):
    """Validate a template definition."""
    try:
        # Get the template
        result = supabase.table("archon_template_definitions").select("*").eq("id", template_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Template not found")

        template = result.data[0]

        # Basic validation
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Validate template_data structure
        template_data = template.get("template_data", {})
        if not isinstance(template_data, dict):
            validation_results["valid"] = False
            validation_results["errors"].append("template_data must be a dictionary")

        # Validate required fields
        if not template.get("name"):
            validation_results["valid"] = False
            validation_results["errors"].append("Template name is required")

        if not template.get("title"):
            validation_results["valid"] = False
            validation_results["errors"].append("Template title is required")

        return {
            "success": True,
            "validation": validation_results,
            "message": "Template validation completed"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Component Endpoints
@router.post("/components")
async def create_component(
    request: CreateComponentRequest,
    supabase=Depends(get_supabase_client)
):
    """Create a new template component."""
    try:
        # Insert into archon_template_components table
        result = supabase.table("archon_template_components").insert({
            "name": request.name,
            "description": request.description,
            "component_type": request.component_type,
            "instruction_text": request.instruction_text,
            "required_tools": request.required_tools,
            "estimated_duration": request.estimated_duration,
            "category": request.category,
            "priority": request.priority,
            "tags": request.tags
        }).execute()

        if result.data:
            return {
                "success": True,
                "component": result.data[0],
                "message": "Component created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create component")

    except Exception as e:
        logger.error(f"Error creating component: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/components")
async def list_components(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    filter_name: Optional[str] = Query(None, description="Filter by name"),
    filter_type: Optional[str] = Query(None, description="Filter by type"),
    filter_category: Optional[str] = Query(None, description="Filter by category"),
    filter_priority: Optional[str] = Query(None, description="Filter by priority"),
    supabase=Depends(get_supabase_client)
):
    """List template components with filtering and pagination."""
    try:
        query = supabase.table("archon_template_components").select("*")

        # Apply filters
        if filter_name:
            query = query.ilike("name", f"%{filter_name}%")
        if filter_type:
            query = query.eq("component_type", filter_type)
        if filter_category:
            query = query.eq("category", filter_category)
        if filter_priority:
            query = query.eq("priority", filter_priority)

        # Apply pagination
        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)

        result = query.execute()

        return {
            "success": True,
            "components": result.data or [],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": len(result.data) if result.data else 0
            },
            "message": f"Found {len(result.data) if result.data else 0} components"
        }

    except Exception as e:
        logger.error(f"Error listing components: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/components/{component_id}")
async def get_component(
    component_id: str,
    supabase=Depends(get_supabase_client)
):
    """Get a specific component by ID."""
    try:
        result = supabase.table("archon_template_components").select("*").eq("id", component_id).execute()

        if result.data:
            return {
                "success": True,
                "component": result.data[0],
                "message": "Component retrieved successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Component not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting component: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/components/{component_id}")
async def update_component(
    component_id: str,
    request: UpdateComponentRequest,
    supabase=Depends(get_supabase_client)
):
    """Update a template component."""
    try:
        # Build update data from non-None fields
        update_data = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        result = supabase.table("archon_template_components").update(update_data).eq("id", component_id).execute()

        if result.data:
            return {
                "success": True,
                "component": result.data[0],
                "message": "Component updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Component not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating component: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/components/{component_id}")
async def delete_component(
    component_id: str,
    supabase=Depends(get_supabase_client)
):
    """Delete a template component."""
    try:
        result = supabase.table("archon_template_components").delete().eq("id", component_id).execute()

        if result.data:
            return {
                "success": True,
                "message": "Component deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Component not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting component: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/components/{component_id}/validate")
async def validate_component(
    component_id: str,
    supabase=Depends(get_supabase_client)
):
    """Validate a template component."""
    try:
        # Get the component
        result = supabase.table("archon_template_components").select("*").eq("id", component_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Component not found")

        component = result.data[0]

        # Basic validation
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # Validate required fields
        if not component.get("name"):
            validation_results["valid"] = False
            validation_results["errors"].append("Component name is required")

        # Validate component type
        valid_types = ["action", "group", "sequence"]
        if component.get("component_type") not in valid_types:
            validation_results["valid"] = False
            validation_results["errors"].append(f"component_type must be one of: {', '.join(valid_types)}")

        # Validate priority
        valid_priorities = ["low", "medium", "high", "critical"]
        if component.get("priority") not in valid_priorities:
            validation_results["valid"] = False
            validation_results["errors"].append(f"priority must be one of: {', '.join(valid_priorities)}")

        return {
            "success": True,
            "validation": validation_results,
            "message": "Component validation completed"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating component: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Template Expansion Endpoint
@router.post("/expand-preview")
async def expand_template_preview(
    request: ExpandPreviewRequest,
    supabase=Depends(get_supabase_client)
):
    """Preview template expansion without creating a task."""
    try:
        # Use the existing TemplateInjectionService
        service = TemplateInjectionService(supabase)

        expansion_result = await service.expand_template(
            original_description=request.original_description,
            template_name=request.template_name,
            project_id=request.project_id,
            context_data=request.context_data
        )

        return {
            "success": True,
            "expansion": expansion_result,
            "message": "Template expansion preview completed"
        }

    except Exception as e:
        logger.error(f"Error expanding template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
