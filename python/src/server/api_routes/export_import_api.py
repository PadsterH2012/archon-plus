"""
Export/Import API endpoints for Archon

Handles:
- Project export operations with various options
- Project import operations with conflict resolution
- Export/import status tracking and progress monitoring
- File download and upload for project packages
"""

import os
import tempfile
from typing import Any, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..config.logfire_config import get_logger, logfire
from ..services.projects import ProjectExportService, ProjectImportService
from ..utils import get_supabase_client

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["export-import"])


# Request Models
class ExportProjectRequest(BaseModel):
    export_type: str = "full"  # "full", "selective", "incremental"
    include_versions: bool = True
    include_sources: bool = True
    include_attachments: bool = True
    version_limit: Optional[int] = None
    date_range: Optional[List[str]] = None  # [start_date, end_date]
    selective_components: Optional[List[str]] = None  # ["tasks", "documents", etc.]

    class Config:
        schema_extra = {
            "example": {
                "export_type": "full",
                "include_versions": True,
                "include_sources": True,
                "include_attachments": False,
                "version_limit": 50,
                "selective_components": ["tasks", "documents"]
            }
        }


class ImportProjectRequest(BaseModel):
    import_type: str = "full"  # "full", "selective", "merge"
    conflict_resolution: str = "merge"  # "merge", "overwrite", "skip", "fail"
    target_project_id: Optional[str] = None
    selective_components: Optional[List[str]] = None
    dry_run: bool = False

    class Config:
        schema_extra = {
            "example": {
                "import_type": "full",
                "conflict_resolution": "merge",
                "target_project_id": None,
                "selective_components": ["tasks"],
                "dry_run": False
            }
        }


class ValidateImportRequest(BaseModel):
    """Request model for import validation"""
    pass


# Response Models
class ExportResponse(BaseModel):
    success: bool
    export_id: Optional[str] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    message: str
    error: Optional[str] = None


class ImportResponse(BaseModel):
    success: bool
    project_id: Optional[str] = None
    import_summary: Optional[dict] = None
    conflicts_resolved: Optional[List[dict]] = None
    message: str
    error: Optional[str] = None


class ValidationResponse(BaseModel):
    valid: bool
    project_title: Optional[str] = None
    project_id: Optional[str] = None
    task_count: Optional[int] = None
    document_count: Optional[int] = None
    export_timestamp: Optional[str] = None
    exported_by: Optional[str] = None
    error: Optional[str] = None


# Export Endpoints
@router.post("/projects/{project_id}/export", response_model=ExportResponse)
async def export_project(project_id: str, request: ExportProjectRequest):
    """Export a project to a portable package format."""
    try:
        logfire.info(f"Starting project export | project_id={project_id} | type={request.export_type}")

        # Initialize export service
        export_service = ProjectExportService()

        # Prepare date range tuple if provided
        date_range = None
        if request.date_range and len(request.date_range) == 2:
            date_range = (request.date_range[0], request.date_range[1])

        # Perform export
        success, result = export_service.export_project(
            project_id=project_id,
            export_type=request.export_type,
            include_versions=request.include_versions,
            include_sources=request.include_sources,
            include_attachments=request.include_attachments,
            version_limit=request.version_limit,
            date_range=date_range,
            exported_by="api_user"
        )

        if success:
            # Generate download URL
            export_id = result["export_id"]
            download_url = f"/api/projects/exports/{export_id}/download"
            
            logfire.info(f"Project export completed | project_id={project_id} | export_id={export_id}")
            
            return ExportResponse(
                success=True,
                export_id=export_id,
                download_url=download_url,
                file_size=result.get("file_size"),
                message=result["message"]
            )
        else:
            logfire.error(f"Project export failed | project_id={project_id} | error={result['error']}")
            return ExportResponse(
                success=False,
                message="Export failed",
                error=result["error"]
            )

    except Exception as e:
        logfire.error(f"Export endpoint error | project_id={project_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/projects/exports/{export_id}/download")
async def download_export(export_id: str):
    """Download an exported project package."""
    try:
        logfire.info(f"Download requested | export_id={export_id}")

        # For now, we'll look for the file in /tmp
        # In production, this would use proper file storage
        export_files = [f for f in os.listdir("/tmp") if f.startswith("project-export-") and export_id in f]
        
        if not export_files:
            raise HTTPException(status_code=404, detail={"error": "Export file not found"})
        
        file_path = os.path.join("/tmp", export_files[0])
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail={"error": "Export file not found"})

        logfire.info(f"Serving export file | export_id={export_id} | file_path={file_path}")
        
        return FileResponse(
            path=file_path,
            filename=export_files[0],
            media_type="application/zip"
        )

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Download error | export_id={export_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/projects/{project_id}/export/status")
async def get_export_status(project_id: str):
    """Get the status of project export operations."""
    try:
        export_service = ProjectExportService()
        
        # This would typically query an exports tracking table
        # For now, return placeholder status
        success, result = export_service.get_export_status(project_id)
        
        if success:
            return result
        else:
            raise HTTPException(status_code=404, detail=result)

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Export status error | project_id={project_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# Import Endpoints
@router.post("/projects/import", response_model=ImportResponse)
async def import_project(
    file: UploadFile = File(...),
    import_type: str = Form("full"),
    conflict_resolution: str = Form("merge"),
    target_project_id: Optional[str] = Form(None),
    selective_components: Optional[str] = Form(None),  # JSON string
    dry_run: bool = Form(False)
):
    """Import a project from an uploaded package file."""
    try:
        logfire.info(f"Starting project import | filename={file.filename} | type={import_type}")

        # Validate file type
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail={"error": "Only ZIP files are supported"})

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Initialize import service
            import_service = ProjectImportService()

            # Parse selective components if provided
            selective_components_list = None
            if selective_components:
                import json
                selective_components_list = json.loads(selective_components)

            # Perform import
            success, result = import_service.import_project(
                import_file_path=temp_file_path,
                import_type=import_type,
                conflict_resolution=conflict_resolution,
                target_project_id=target_project_id,
                selective_components=selective_components_list,
                imported_by="api_user",
                dry_run=dry_run
            )

            if success:
                logfire.info(f"Project import completed | filename={file.filename} | project_id={result.get('project_id')}")
                
                return ImportResponse(
                    success=True,
                    project_id=result.get("project_id"),
                    import_summary=result.get("import_summary"),
                    conflicts_resolved=result.get("conflicts_resolved"),
                    message=result["message"]
                )
            else:
                logfire.error(f"Project import failed | filename={file.filename} | error={result['error']}")
                return ImportResponse(
                    success=False,
                    message="Import failed",
                    error=result["error"]
                )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Import endpoint error | filename={file.filename} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/projects/import/validate", response_model=ValidationResponse)
async def validate_import_file(file: UploadFile = File(...)):
    """Validate an import file without performing the actual import."""
    try:
        logfire.info(f"Validating import file | filename={file.filename}")

        # Validate file type
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail={"error": "Only ZIP files are supported"})

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Initialize import service
            import_service = ProjectImportService()

            # Validate file
            is_valid, result = import_service.validate_import_file(temp_file_path)

            if is_valid:
                logfire.info(f"Import file validation successful | filename={file.filename}")
                
                return ValidationResponse(
                    valid=True,
                    project_title=result.get("project_title"),
                    project_id=result.get("project_id"),
                    task_count=result.get("task_count"),
                    document_count=result.get("document_count"),
                    export_timestamp=result.get("export_timestamp"),
                    exported_by=result.get("exported_by")
                )
            else:
                logfire.warning(f"Import file validation failed | filename={file.filename} | error={result['error']}")
                return ValidationResponse(
                    valid=False,
                    error=result["error"]
                )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Validation endpoint error | filename={file.filename} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# List and Status Endpoints
@router.get("/projects/exports")
async def list_exports(project_id: Optional[str] = None):
    """List available project exports."""
    try:
        export_service = ProjectExportService()
        success, result = export_service.list_exports(project_id)
        
        if success:
            return result
        else:
            raise HTTPException(status_code=500, detail=result)

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"List exports error | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})
