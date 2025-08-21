"""
Template Management API Routes

Provides REST API endpoints for template injection system management.
These endpoints support the Components tab in the frontend UI.
"""

import json
import logfire
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..database.supabase_client import get_supabase_client
from ..services.credential_service import get_credential

router = APIRouter(prefix="/api/template-management", tags=["template-management"])


@router.get("/health")
async def template_management_health():
    """Template management API health check."""
    try:
        # Check if template injection is enabled
        template_injection_enabled = await get_credential("TEMPLATE_INJECTION_ENABLED")
        
        return {
            "status": "healthy",
            "service": "template-management-api",
            "template_injection_enabled": template_injection_enabled == "true",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logfire.error(f"Template management health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/components")
async def list_template_components(
    filter_by: Optional[str] = Query(None, description="Filter type: name, type, category, priority"),
    filter_value: Optional[str] = Query(None, description="Filter value"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page")
):
    """List template components with filtering and pagination."""
    try:
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table("archon_template_components").select("*")
        
        # Apply filters
        if filter_by and filter_value:
            if filter_by == "name":
                query = query.ilike("name", f"%{filter_value}%")
            elif filter_by == "type":
                query = query.eq("component_type", filter_value)
            elif filter_by == "category":
                query = query.eq("category", filter_value)
            elif filter_by == "priority":
                query = query.eq("priority", filter_value)
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)
        
        # Order by name
        query = query.order("name")
        
        result = query.execute()
        
        # Get total count for pagination
        count_result = supabase.table("archon_template_components").select("id", count="exact").execute()
        total_count = count_result.count
        
        return {
            "success": True,
            "components": result.data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": (total_count + per_page - 1) // per_page
            }
        }
        
    except Exception as e:
        logfire.error(f"Failed to list template components: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/components/{component_id}")
async def get_template_component(component_id: str):
    """Get a specific template component by ID."""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("archon_template_components").select("*").eq("id", component_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Component not found")
        
        return {
            "success": True,
            "component": result.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Failed to get template component {component_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates(
    filter_by: Optional[str] = Query(None, description="Filter type: name, type, category"),
    filter_value: Optional[str] = Query(None, description="Filter value"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page")
):
    """List template definitions with filtering and pagination."""
    try:
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table("archon_template_definitions").select("*")
        
        # Apply filters
        if filter_by and filter_value:
            if filter_by == "name":
                query = query.ilike("name", f"%{filter_value}%")
            elif filter_by == "type":
                query = query.eq("template_type", filter_value)
            elif filter_by == "category":
                query = query.eq("category", filter_value)
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)
        
        # Order by name
        query = query.order("name")
        
        result = query.execute()
        
        # Get total count for pagination
        count_result = supabase.table("archon_template_definitions").select("id", count="exact").execute()
        total_count = count_result.count
        
        return {
            "success": True,
            "templates": result.data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": (total_count + per_page - 1) // per_page
            }
        }
        
    except Exception as e:
        logfire.error(f"Failed to list templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID."""
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("archon_template_definitions").select("*").eq("id", template_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "template": result.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Failed to get template {template_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/test")
async def test_template_expansion(request: Dict[str, Any]):
    """Test template expansion with sample content."""
    try:
        template_name = request.get("template_name", "workflow_default")
        original_description = request.get("original_description", "Test task")
        context_data = request.get("context_data", {})
        
        # For now, return a mock response since we don't have the full expansion logic
        # This can be enhanced later with actual template expansion
        
        return {
            "success": True,
            "result": {
                "expanded_description": f"{{{{group::understand_homelab_env}}}}\n\n{original_description}\n\n{{{{group::send_task_to_review}}}}",
                "expansion_time_ms": 50,
                "component_count": 2,
                "validation_errors": [],
                "template_name": template_name,
                "context_data": context_data
            }
        }
        
    except Exception as e:
        logfire.error(f"Failed to test template expansion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assignments")
async def list_template_assignments(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    is_active: bool = Query(True, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page")
):
    """List template assignments with filtering."""
    try:
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table("archon_template_assignments").select("*")
        
        # Apply filters
        if project_id:
            query = query.eq("entity_id", project_id)
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1)
        
        # Order by priority desc, then created_at
        query = query.order("priority", desc=True).order("created_at")
        
        result = query.execute()
        
        return {
            "success": True,
            "assignments": result.data
        }
        
    except Exception as e:
        logfire.error(f"Failed to list template assignments: {e}")
        raise HTTPException(status_code=500, detail=str(e))
