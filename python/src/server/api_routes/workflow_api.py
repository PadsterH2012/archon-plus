"""
Workflow API endpoints for Archon

Handles:
- Workflow template management (CRUD operations)
- Workflow execution control and monitoring
- Workflow catalog browsing and search
- Real-time execution progress tracking
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Import unified logging
from ..config.logfire_config import get_logger, logfire
from ..models.workflow_models import (
    WorkflowStatus,
    WorkflowExecutionStatus,
    CreateWorkflowTemplateRequest,
    UpdateWorkflowTemplateRequest,
    ExecuteWorkflowRequest,
    WorkflowExecutionResponse
)
from ..models.workflow_validation import validate_workflow_template
from ..services.workflow import (
    WorkflowRepository,
    get_workflow_executor,
    get_workflow_execution_service,
    MCPToolRegistry,
    get_mcp_workflow_integration
)
from ..utils import get_supabase_client

logger = get_logger(__name__)
router = APIRouter(prefix="/api/workflows", tags=["workflows"])


# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class WorkflowListResponse(BaseModel):
    """Response model for workflow list endpoint"""
    workflows: List[Dict[str, Any]]
    total_count: int
    page: int
    per_page: int
    has_more: bool


class WorkflowDetailResponse(BaseModel):
    """Response model for workflow detail endpoint"""
    workflow: Dict[str, Any]
    validation_result: Optional[Dict[str, Any]] = None


class WorkflowValidationResponse(BaseModel):
    """Response model for workflow validation endpoint"""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    info: List[Dict[str, Any]]


class WorkflowSearchRequest(BaseModel):
    """Request model for workflow search"""
    query: str = Field(..., description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    status: Optional[WorkflowStatus] = Field(None, description="Filter by status")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    is_public: Optional[bool] = Field(None, description="Filter by public/private")


# =====================================================
# WORKFLOW TEMPLATE ENDPOINTS
# =====================================================

@router.get("", response_model=WorkflowListResponse)
async def list_workflows(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by workflow status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    search: Optional[str] = Query(None, description="Search in name, title, description")
):
    """
    List workflow templates with filtering and pagination.
    
    Returns paginated list of workflow templates with optional filtering by:
    - Status (draft, active, deprecated, archived)
    - Category (e.g., deployment, testing, automation)
    - Creator
    - Public/private visibility
    - Search terms
    """
    try:
        logfire.info(
            f"Listing workflows | page={page} | per_page={per_page} | "
            f"status={status} | category={category} | search={search}"
        )
        
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Use repository to get workflows
        repository = WorkflowRepository(get_supabase_client())
        success, result = repository.list_workflow_templates(
            status=status,
            category=category,
            created_by=created_by,
            is_public=is_public,
            search=search,
            limit=per_page,
            offset=offset
        )
        
        if not success:
            logfire.error(f"Failed to list workflows | error={result.get('error')}")
            raise HTTPException(status_code=500, detail=result)
        
        workflows = result["templates"]
        count = result["count"]
        
        # Calculate if there are more pages
        has_more = count == per_page  # If we got a full page, there might be more
        
        logfire.info(f"Listed {count} workflows | page={page} | has_more={has_more}")
        
        return WorkflowListResponse(
            workflows=workflows,
            total_count=count,
            page=page,
            per_page=per_page,
            has_more=has_more
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error listing workflows | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("", status_code=201)
async def create_workflow(request: CreateWorkflowTemplateRequest):
    """
    Create a new workflow template.
    
    Creates a new workflow template with validation and automatic version control.
    The workflow will be validated before creation to ensure it's well-formed.
    """
    try:
        logfire.info(f"Creating workflow | name={request.name} | title={request.title}")
        
        # Convert request to dict for repository
        workflow_data = request.dict()
        
        # Use repository to create workflow
        repository = WorkflowRepository(get_supabase_client())
        success, result = await repository.create_workflow_template(workflow_data)
        
        if not success:
            logfire.error(f"Failed to create workflow | error={result.get('error')}")
            raise HTTPException(status_code=400, detail=result)
        
        created_workflow = result["template"]
        
        logfire.info(
            f"Workflow created successfully | id={created_workflow['id']} | name={created_workflow['name']}"
        )
        
        return {
            "message": "Workflow created successfully",
            "workflow": created_workflow
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error creating workflow | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/categories")
async def get_workflow_categories():
    """
    Get all available workflow categories.

    Returns a list of all categories used by workflow templates,
    useful for filtering and organization.
    """
    try:
        logfire.info("Getting workflow categories")

        # Use repository to get all workflows and extract categories
        repository = WorkflowRepository(get_supabase_client())
        success, result = repository.list_workflow_templates(limit=1000, offset=0)

        if not success:
            logfire.error(f"Failed to get workflows for categories | error={result.get('error')}")
            raise HTTPException(status_code=500, detail=result)

        workflows = result["templates"]

        # Extract unique categories
        categories = set()
        for workflow in workflows:
            if workflow.get("category"):
                categories.add(workflow["category"])

        categories_list = sorted(list(categories))

        logfire.info(f"Found {len(categories_list)} workflow categories")

        return {
            "categories": categories_list,
            "total_count": len(categories_list)
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error getting workflow categories | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/tools")
async def get_available_mcp_tools():
    """
    Get all available MCP tools for workflow integration.

    Returns comprehensive information about all MCP tools that can be
    used in workflow steps, including their parameters and examples.
    """
    try:
        logfire.info("Getting available MCP tools")

        tools = []
        for tool_name, tool_info in MCPToolRegistry.AVAILABLE_TOOLS.items():
            tools.append({
                "name": tool_name,
                "category": tool_info.get("category"),
                "description": tool_info.get("description"),
                "parameters": tool_info.get("parameters", {}),
                "returns": tool_info.get("returns"),
                "example": tool_info.get("example", {})
            })

        # Group by category
        tools_by_category = {}
        for tool in tools:
            category = tool["category"] or "unknown"
            if category not in tools_by_category:
                tools_by_category[category] = []
            tools_by_category[category].append(tool)

        logfire.info(f"Retrieved {len(tools)} MCP tools across {len(tools_by_category)} categories")

        return {
            "tools": tools,
            "tools_by_category": tools_by_category,
            "total_count": len(tools),
            "categories": list(tools_by_category.keys())
        }

    except Exception as e:
        logfire.error(f"Error getting MCP tools | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/{workflow_id}", response_model=WorkflowDetailResponse)
async def get_workflow(workflow_id: str):
    """
    Get a specific workflow template by ID.
    
    Returns detailed information about a workflow template including
    its steps, parameters, and current validation status.
    """
    try:
        logfire.info(f"Getting workflow | id={workflow_id}")
        
        # Use repository to get workflow
        repository = WorkflowRepository(get_supabase_client())
        success, result = repository.get_workflow_template(workflow_id)
        
        if not success:
            if "not found" in result.get("error", "").lower():
                logfire.warning(f"Workflow not found | id={workflow_id}")
                raise HTTPException(status_code=404, detail=result)
            else:
                logfire.error(f"Failed to get workflow | error={result.get('error')}")
                raise HTTPException(status_code=500, detail=result)
        
        workflow = result["template"]
        
        # Optionally validate the workflow and include validation results
        validation_result = None
        try:
            from ..models.workflow_models import validate_workflow_template_data
            template = validate_workflow_template_data(workflow)
            validation = validate_workflow_template(template)
            
            validation_result = {
                "is_valid": validation.is_valid,
                "errors": [{"code": e.code, "message": e.message, "step_name": e.step_name} for e in validation.errors],
                "warnings": [{"code": w.code, "message": w.message, "step_name": w.step_name} for w in validation.warnings],
                "info": [{"code": i.code, "message": i.message, "step_name": i.step_name} for i in validation.info]
            }
        except Exception as validation_error:
            logfire.warning(f"Workflow validation failed | id={workflow_id} | error={str(validation_error)}")
        
        logfire.info(f"Retrieved workflow | id={workflow_id} | name={workflow['name']}")
        
        return WorkflowDetailResponse(
            workflow=workflow,
            validation_result=validation_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error getting workflow | id={workflow_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.put("/{workflow_id}")
async def update_workflow(workflow_id: str, request: UpdateWorkflowTemplateRequest):
    """
    Update a workflow template.
    
    Updates an existing workflow template with new data. Only provided fields
    will be updated. A new version will be created if significant changes are made.
    """
    try:
        logfire.info(f"Updating workflow | id={workflow_id}")
        
        # Convert request to dict, excluding None values
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail={"error": "No update data provided"})
        
        # Use repository to update workflow
        repository = WorkflowRepository(get_supabase_client())
        success, result = await repository.update_workflow_template(
            workflow_id, 
            update_data,
            updated_by="api_user"  # TODO: Get from authentication context
        )
        
        if not success:
            if "not found" in result.get("error", "").lower():
                logfire.warning(f"Workflow not found for update | id={workflow_id}")
                raise HTTPException(status_code=404, detail=result)
            else:
                logfire.error(f"Failed to update workflow | error={result.get('error')}")
                raise HTTPException(status_code=400, detail=result)
        
        updated_workflow = result["template"]
        
        logfire.info(
            f"Workflow updated successfully | id={workflow_id} | name={updated_workflow['name']}"
        )
        
        return {
            "message": "Workflow updated successfully",
            "workflow": updated_workflow
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error updating workflow | id={workflow_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """
    Delete a workflow template.
    
    Permanently deletes a workflow template and all associated data.
    This action cannot be undone.
    """
    try:
        logfire.info(f"Deleting workflow | id={workflow_id}")
        
        # Use repository to delete workflow
        repository = WorkflowRepository(get_supabase_client())
        success, result = repository.delete_workflow_template(workflow_id)
        
        if not success:
            if "not found" in result.get("error", "").lower():
                logfire.warning(f"Workflow not found for deletion | id={workflow_id}")
                raise HTTPException(status_code=404, detail=result)
            else:
                logfire.error(f"Failed to delete workflow | error={result.get('error')}")
                raise HTTPException(status_code=500, detail=result)
        
        logfire.info(f"Workflow deleted successfully | id={workflow_id}")
        
        return {"message": "Workflow deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error deleting workflow | id={workflow_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# =====================================================
# WORKFLOW VALIDATION ENDPOINTS
# =====================================================

@router.post("/{workflow_id}/validate", response_model=WorkflowValidationResponse)
async def validate_workflow(workflow_id: str):
    """
    Validate a workflow template.
    
    Performs comprehensive validation of a workflow template including:
    - Structural validation
    - Step dependency checking
    - Parameter validation
    - Circular reference detection
    - Performance analysis
    """
    try:
        logfire.info(f"Validating workflow | id={workflow_id}")
        
        # Get workflow first
        repository = WorkflowRepository(get_supabase_client())
        success, result = repository.get_workflow_template(workflow_id)
        
        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result)
            else:
                raise HTTPException(status_code=500, detail=result)
        
        workflow_data = result["template"]
        
        # Validate the workflow
        from ..models.workflow_models import validate_workflow_template_data
        template = validate_workflow_template_data(workflow_data)
        validation = validate_workflow_template(template)
        
        logfire.info(
            f"Workflow validation completed | id={workflow_id} | "
            f"valid={validation.is_valid} | errors={len(validation.errors)} | "
            f"warnings={len(validation.warnings)}"
        )
        
        return WorkflowValidationResponse(
            is_valid=validation.is_valid,
            errors=[
                {
                    "code": e.code,
                    "message": e.message,
                    "step_name": e.step_name,
                    "field": e.field,
                    "suggestion": e.suggestion
                }
                for e in validation.errors
            ],
            warnings=[
                {
                    "code": w.code,
                    "message": w.message,
                    "step_name": w.step_name,
                    "field": w.field,
                    "suggestion": w.suggestion
                }
                for w in validation.warnings
            ],
            info=[
                {
                    "code": i.code,
                    "message": i.message,
                    "step_name": i.step_name,
                    "field": i.field,
                    "suggestion": i.suggestion
                }
                for i in validation.info
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error validating workflow | id={workflow_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# =====================================================
# WORKFLOW SEARCH AND DISCOVERY ENDPOINTS
# =====================================================

@router.post("/search")
async def search_workflows(request: WorkflowSearchRequest):
    """
    Search workflow templates.
    
    Advanced search functionality for finding workflows based on:
    - Text search in name, title, description
    - Category filtering
    - Status filtering
    - Creator filtering
    - Public/private visibility
    """
    try:
        logfire.info(f"Searching workflows | query={request.query} | category={request.category}")
        
        # Use repository to search workflows
        repository = WorkflowRepository(get_supabase_client())
        success, result = repository.list_workflow_templates(
            status=request.status.value if request.status else None,
            category=request.category,
            created_by=request.created_by,
            is_public=request.is_public,
            search=request.query,
            limit=50,  # Default search limit
            offset=0
        )
        
        if not success:
            logfire.error(f"Failed to search workflows | error={result.get('error')}")
            raise HTTPException(status_code=500, detail=result)
        
        workflows = result["templates"]
        count = result["count"]
        
        logfire.info(f"Found {count} workflows matching search | query={request.query}")
        
        return {
            "workflows": workflows,
            "total_count": count,
            "query": request.query
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error searching workflows | query={request.query} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})





# =====================================================
# WORKFLOW EXAMPLES ENDPOINTS
# =====================================================

@router.get("/examples")
async def get_workflow_examples():
    """
    Get example workflow templates.
    
    Returns a collection of pre-built example workflows that demonstrate
    various workflow patterns and use cases.
    """
    try:
        logfire.info("Getting workflow examples")
        
        from ..models.workflow_examples import EXAMPLE_WORKFLOWS, list_example_workflows
        from ..models.mcp_workflow_examples import get_all_mcp_example_workflows
        
        examples = []

        # Add standard examples
        for name in list_example_workflows():
            workflow = EXAMPLE_WORKFLOWS[name]
            examples.append({
                "name": workflow.name,
                "title": workflow.title,
                "description": workflow.description,
                "category": workflow.category,
                "tags": workflow.tags,
                "step_count": len(workflow.steps),
                "complexity": "simple" if len(workflow.steps) <= 3 else "moderate" if len(workflow.steps) <= 6 else "complex",
                "type": "standard"
            })

        # Add MCP integration examples
        mcp_examples = get_all_mcp_example_workflows()
        for name, workflow in mcp_examples.items():
            examples.append({
                "name": workflow.name,
                "title": workflow.title,
                "description": workflow.description,
                "category": workflow.category,
                "tags": workflow.tags,
                "step_count": len(workflow.steps),
                "complexity": "simple" if len(workflow.steps) <= 3 else "moderate" if len(workflow.steps) <= 6 else "complex",
                "type": "mcp_integration"
            })

        logfire.info(f"Retrieved {len(examples)} workflow examples ({len(mcp_examples)} MCP examples)")

        return {
            "examples": examples,
            "total_count": len(examples),
            "standard_count": len(EXAMPLE_WORKFLOWS),
            "mcp_count": len(mcp_examples)
        }
        
    except Exception as e:
        logfire.error(f"Error getting workflow examples | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/examples/{example_name}")
async def get_workflow_example(example_name: str):
    """
    Get a specific workflow example by name.
    
    Returns the complete workflow template for a specific example,
    which can be used as a starting point for creating new workflows.
    """
    try:
        logfire.info(f"Getting workflow example | name={example_name}")
        
        from ..models.workflow_examples import get_example_workflow
        from ..models.mcp_workflow_examples import get_mcp_example_workflow, list_mcp_example_workflows
        
        try:
            # Try standard examples first
            try:
                workflow = get_example_workflow(example_name)
                workflow_type = "standard"
            except KeyError:
                # Try MCP examples
                if example_name in list_mcp_example_workflows():
                    workflow = get_mcp_example_workflow(example_name)
                    workflow_type = "mcp_integration"
                else:
                    logfire.warning(f"Workflow example not found | name={example_name}")
                    raise HTTPException(status_code=404, detail={"error": f"Example workflow '{example_name}' not found"})

            # Convert to dict for response
            workflow_dict = workflow.dict()

            logfire.info(f"Retrieved workflow example | name={example_name} | title={workflow.title}")

            return {
                "example": workflow_dict,
                "name": example_name,
                "type": workflow_type
            }

        except HTTPException:
            raise

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error getting workflow example | name={example_name} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# =====================================================
# MCP TOOL INTEGRATION ENDPOINTS
# =====================================================




@router.get("/tools/{tool_name}")
async def get_mcp_tool_info(tool_name: str):
    """
    Get detailed information about a specific MCP tool.

    Returns comprehensive information about the tool including
    parameters, examples, and usage guidelines.
    """
    try:
        logfire.info(f"Getting MCP tool info | tool={tool_name}")

        tool_info = MCPToolRegistry.get_tool_info(tool_name)
        if not tool_info:
            logfire.warning(f"MCP tool not found | tool={tool_name}")
            raise HTTPException(status_code=404, detail={"error": f"MCP tool '{tool_name}' not found"})

        logfire.info(f"Retrieved MCP tool info | tool={tool_name} | category={tool_info.get('category')}")

        return {
            "tool": {
                "name": tool_name,
                "category": tool_info.get("category"),
                "description": tool_info.get("description"),
                "parameters": tool_info.get("parameters", {}),
                "returns": tool_info.get("returns"),
                "example": tool_info.get("example", {})
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error getting MCP tool info | tool={tool_name} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/tools/categories/{category}")
async def get_mcp_tools_by_category(category: str):
    """
    Get all MCP tools in a specific category.

    Returns all tools that belong to the specified category,
    useful for discovering tools for specific use cases.
    """
    try:
        logfire.info(f"Getting MCP tools by category | category={category}")

        tool_names = MCPToolRegistry.list_tools_by_category(category)
        if not tool_names:
            logfire.warning(f"No tools found in category | category={category}")
            return {
                "tools": [],
                "category": category,
                "total_count": 0
            }

        tools = []
        for tool_name in tool_names:
            tool_info = MCPToolRegistry.get_tool_info(tool_name)
            if tool_info:
                tools.append({
                    "name": tool_name,
                    "description": tool_info.get("description"),
                    "parameters": tool_info.get("parameters", {}),
                    "example": tool_info.get("example", {})
                })

        logfire.info(f"Retrieved {len(tools)} tools in category | category={category}")

        return {
            "tools": tools,
            "category": category,
            "total_count": len(tools)
        }

    except Exception as e:
        logfire.error(f"Error getting tools by category | category={category} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/tools/suggest")
async def suggest_mcp_tools(request: Dict[str, str]):
    """
    Get MCP tool suggestions based on step description.

    Analyzes the provided step description and suggests the most
    relevant MCP tools that could be used for that step.
    """
    try:
        step_description = request.get("description", "")
        if not step_description:
            raise HTTPException(status_code=400, detail={"error": "Step description is required"})

        logfire.info(f"Getting tool suggestions | description={step_description}")

        integration = get_mcp_workflow_integration()
        suggestions = integration.get_tool_suggestions(step_description)

        logfire.info(f"Generated {len(suggestions)} tool suggestions")

        return {
            "suggestions": suggestions,
            "description": step_description,
            "total_count": len(suggestions)
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error getting tool suggestions | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/{workflow_id}/validate-tools")
async def validate_workflow_mcp_tools(workflow_id: str):
    """
    Validate all MCP tools used in a workflow.

    Checks that all tools referenced in the workflow steps exist
    and have valid parameter configurations.
    """
    try:
        logfire.info(f"Validating workflow MCP tools | workflow_id={workflow_id}")

        # Get workflow template
        repository = WorkflowRepository(get_supabase_client())
        success, result = repository.get_workflow_template(workflow_id)

        if not success:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result)
            else:
                raise HTTPException(status_code=500, detail=result)

        workflow_data = result["template"]

        # Extract workflow steps for validation
        workflow_steps = []
        for step in workflow_data.get("steps", []):
            if step.get("type") == "action":
                workflow_steps.append({
                    "name": step.get("name"),
                    "type": "action",
                    "tool_name": step.get("tool_name"),
                    "parameters": step.get("parameters", {})
                })

        # Validate tools
        integration = get_mcp_workflow_integration()
        validation_result = integration.validate_workflow_tools(workflow_steps)

        logfire.info(
            f"Workflow tool validation completed | workflow_id={workflow_id} | "
            f"valid={validation_result['valid']} | errors={len(validation_result['errors'])}"
        )

        return {
            "workflow_id": workflow_id,
            "validation": validation_result,
            "steps_validated": len(workflow_steps)
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error validating workflow tools | workflow_id={workflow_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# =====================================================
# WORKFLOW EXECUTION ENDPOINTS
# =====================================================

@router.post("/{workflow_id}/execute", status_code=202)
async def execute_workflow(workflow_id: str, request: ExecuteWorkflowRequest):
    """
    Execute a workflow template.

    Starts execution of a workflow template with provided parameters.
    Returns immediately with execution ID for tracking progress.
    """
    try:
        logfire.info(f"Starting workflow execution | workflow_id={workflow_id} | triggered_by={request.triggered_by}")

        # Use workflow execution service to start execution
        execution_service = get_workflow_execution_service()
        success, result = await execution_service.start_workflow_execution(
            workflow_id,
            request.input_parameters,
            request.triggered_by,
            request.trigger_context,
            background=True  # Run in background by default
        )

        if not success:
            logfire.error(f"Failed to start workflow execution | error={result.get('error')}")
            raise HTTPException(status_code=400, detail=result)

        execution_id = result["execution_id"]

        logfire.info(f"Workflow execution started | execution_id={execution_id} | workflow_id={workflow_id}")

        return {
            "message": "Workflow execution started",
            "execution_id": execution_id,
            "status": result["status"],
            "workflow_id": workflow_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error executing workflow | workflow_id={workflow_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """
    Get workflow execution status and progress.

    Returns detailed information about a workflow execution including
    current status, progress, step details, and any errors.
    """
    try:
        logfire.info(f"Getting execution status | execution_id={execution_id}")

        # Get execution details using execution service
        execution_service = get_workflow_execution_service()
        success, result = await execution_service.get_execution_status(execution_id)

        if not success:
            if "not found" in result.get("error", "").lower():
                logfire.warning(f"Execution not found | execution_id={execution_id}")
                raise HTTPException(status_code=404, detail=result)
            else:
                logfire.error(f"Failed to get execution | error={result.get('error')}")
                raise HTTPException(status_code=500, detail=result)

        execution = result["execution"]
        step_executions = result["step_executions"]

        logfire.info(
            f"Retrieved execution status | execution_id={execution_id} | "
            f"status={execution['status']} | progress={execution['progress_percentage']}%"
        )

        return {
            "execution": execution,
            "step_executions": step_executions,
            "total_steps": result["total_steps"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error getting execution status | execution_id={execution_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/executions")
async def list_executions(
    workflow_id: Optional[str] = Query(None, description="Filter by workflow template ID"),
    status: Optional[str] = Query(None, description="Filter by execution status"),
    triggered_by: Optional[str] = Query(None, description="Filter by who triggered the execution"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    List workflow executions with filtering.

    Returns paginated list of workflow executions with optional filtering.
    """
    try:
        logfire.info(
            f"Listing executions | workflow_id={workflow_id} | status={status} | "
            f"triggered_by={triggered_by} | page={page}"
        )

        # Calculate offset for pagination
        offset = (page - 1) * per_page

        # Use repository to get executions
        repository = WorkflowRepository(get_supabase_client())
        success, result = repository.list_workflow_executions(
            workflow_template_id=workflow_id,
            status=status,
            triggered_by=triggered_by,
            limit=per_page,
            offset=offset
        )

        if not success:
            logfire.error(f"Failed to list executions | error={result.get('error')}")
            raise HTTPException(status_code=500, detail=result)

        executions = result["executions"]
        count = result["count"]

        logfire.info(f"Listed {count} executions | page={page}")

        return {
            "executions": executions,
            "total_count": count,
            "page": page,
            "per_page": per_page,
            "has_more": count == per_page
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error listing executions | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """
    Cancel a running workflow execution.

    Attempts to gracefully cancel a workflow execution that is currently
    running or pending. The execution status will be updated to 'cancelled'.
    """
    try:
        logfire.info(f"Cancelling execution | execution_id={execution_id}")

        # Use workflow execution service to cancel execution
        execution_service = get_workflow_execution_service()
        success, result = await execution_service.cancel_workflow_execution(execution_id)

        if not success:
            logfire.error(f"Failed to cancel execution | error={result.get('error')}")
            raise HTTPException(status_code=500, detail=result)

        logfire.info(f"Execution cancelled successfully | execution_id={execution_id}")

        return {
            "message": "Execution cancelled successfully",
            "execution_id": execution_id,
            "status": "cancelled"
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error cancelling execution | execution_id={execution_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/executions/{execution_id}/pause")
async def pause_execution(execution_id: str):
    """
    Pause a running workflow execution.

    Pauses a workflow execution that is currently running. The execution
    can be resumed later using the resume endpoint.
    """
    try:
        logfire.info(f"Pausing execution | execution_id={execution_id}")

        # Use workflow execution service to pause execution
        execution_service = get_workflow_execution_service()
        success, result = await execution_service.pause_workflow_execution(execution_id)

        if not success:
            logfire.error(f"Failed to pause execution | error={result.get('error')}")
            raise HTTPException(status_code=400, detail=result)

        logfire.info(f"Execution paused successfully | execution_id={execution_id}")

        return {
            "message": "Execution paused successfully",
            "execution_id": execution_id,
            "status": "paused"
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error pausing execution | execution_id={execution_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/executions/{execution_id}/resume")
async def resume_execution(execution_id: str):
    """
    Resume a paused workflow execution.

    Resumes a workflow execution that was previously paused. The execution
    will continue from where it was paused.
    """
    try:
        logfire.info(f"Resuming execution | execution_id={execution_id}")

        # Use workflow execution service to resume execution
        execution_service = get_workflow_execution_service()
        success, result = await execution_service.resume_workflow_execution(execution_id)

        if not success:
            logfire.error(f"Failed to resume execution | error={result.get('error')}")
            raise HTTPException(status_code=400, detail=result)

        logfire.info(f"Execution resumed successfully | execution_id={execution_id}")

        return {
            "message": "Execution resumed successfully",
            "execution_id": execution_id,
            "status": "running"
        }

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Error resuming execution | execution_id={execution_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# =====================================================
# HEALTH CHECK ENDPOINT
# =====================================================

@router.get("/health")
async def workflow_health():
    """Workflow API health check."""
    result = {
        "status": "healthy",
        "service": "workflow-api",
        "timestamp": datetime.now().isoformat(),
    }
    return result
