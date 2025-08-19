"""
Backup Management API endpoints for Archon

Handles:
- Manual backup creation and restoration
- Backup schedule management
- Backup listing and status monitoring
- Retention policy management
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..config.logfire_config import get_logger, logfire
from ..services.backup.backup_manager import get_backup_manager
from ..services.backup.backup_scheduler import get_backup_scheduler

logger = get_logger(__name__)

router = APIRouter(prefix="/api/backup", tags=["backup"])


# Request Models
class CreateBackupRequest(BaseModel):
    project_id: str
    backup_type: str = "full"
    compress: bool = True
    encrypt: bool = False

    class Config:
        schema_extra = {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "backup_type": "full",
                "compress": True,
                "encrypt": False
            }
        }


class RestoreBackupRequest(BaseModel):
    backup_id: str
    target_project_id: Optional[str] = None
    conflict_resolution: str = "merge"

    class Config:
        schema_extra = {
            "example": {
                "backup_id": "backup-123e4567-e89b-12d3-a456-426614174000",
                "target_project_id": None,
                "conflict_resolution": "merge"
            }
        }


class CreateScheduleRequest(BaseModel):
    project_id: str
    schedule_type: str = "cron"
    cron_expression: Optional[str] = None
    interval_minutes: Optional[int] = None
    backup_type: str = "full"
    enabled: bool = True

    class Config:
        schema_extra = {
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "schedule_type": "cron",
                "cron_expression": "0 2 * * *",
                "backup_type": "full",
                "enabled": True
            }
        }


class UpdateScheduleRequest(BaseModel):
    cron_expression: Optional[str] = None
    interval_minutes: Optional[int] = None
    backup_type: Optional[str] = None
    enabled: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "cron_expression": "0 3 * * *",
                "enabled": True
            }
        }


# Response Models
class BackupResponse(BaseModel):
    success: bool
    backup_id: Optional[str] = None
    backup_metadata: Optional[dict] = None
    message: str
    error: Optional[str] = None


class RestoreResponse(BaseModel):
    success: bool
    backup_id: Optional[str] = None
    restored_project_id: Optional[str] = None
    import_summary: Optional[dict] = None
    message: str
    error: Optional[str] = None


class ScheduleResponse(BaseModel):
    success: bool
    schedule_id: Optional[str] = None
    schedule: Optional[dict] = None
    message: str
    error: Optional[str] = None


# Backup Management Endpoints
@router.post("/create", response_model=BackupResponse)
async def create_backup(request: CreateBackupRequest):
    """Create a manual backup of a project."""
    try:
        logfire.info(f"Creating manual backup | project_id={request.project_id} | type={request.backup_type}")

        backup_manager = get_backup_manager()
        
        success, result = await backup_manager.create_project_backup(
            project_id=request.project_id,
            backup_type=request.backup_type,
            created_by="api_user",
            compress=request.compress,
            encrypt=request.encrypt
        )

        if success:
            logfire.info(f"Manual backup created | backup_id={result['backup_id']}")
            return BackupResponse(
                success=True,
                backup_id=result["backup_id"],
                backup_metadata=result["backup_metadata"],
                message=result["message"]
            )
        else:
            logfire.error(f"Manual backup failed | project_id={request.project_id} | error={result['error']}")
            return BackupResponse(
                success=False,
                message="Backup creation failed",
                error=result["error"]
            )

    except Exception as e:
        logfire.error(f"Backup creation endpoint error | project_id={request.project_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/restore", response_model=RestoreResponse)
async def restore_backup(request: RestoreBackupRequest):
    """Restore a project from a backup."""
    try:
        logfire.info(f"Restoring backup | backup_id={request.backup_id}")

        backup_manager = get_backup_manager()
        
        success, result = await backup_manager.restore_project_backup(
            backup_id=request.backup_id,
            target_project_id=request.target_project_id,
            conflict_resolution=request.conflict_resolution,
            restored_by="api_user"
        )

        if success:
            logfire.info(f"Backup restored | backup_id={request.backup_id} | project_id={result.get('restored_project_id')}")
            return RestoreResponse(
                success=True,
                backup_id=result["backup_id"],
                restored_project_id=result.get("restored_project_id"),
                import_summary=result.get("import_summary"),
                message=result["message"]
            )
        else:
            logfire.error(f"Backup restoration failed | backup_id={request.backup_id} | error={result['error']}")
            return RestoreResponse(
                success=False,
                backup_id=request.backup_id,
                message="Backup restoration failed",
                error=result["error"]
            )

    except Exception as e:
        logfire.error(f"Backup restoration endpoint error | backup_id={request.backup_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/list")
async def list_backups(project_id: Optional[str] = None):
    """List available backups."""
    try:
        backup_manager = get_backup_manager()
        backups = await backup_manager.storage_backend.list_backups()
        
        # Filter by project_id if provided
        if project_id:
            backups = [b for b in backups if b.get("project_id") == project_id]
        
        return {
            "success": True,
            "backups": backups,
            "total_count": len(backups)
        }

    except Exception as e:
        logfire.error(f"List backups error | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.delete("/delete/{backup_id}")
async def delete_backup(backup_id: str):
    """Delete a backup."""
    try:
        logfire.info(f"Deleting backup | backup_id={backup_id}")

        backup_manager = get_backup_manager()
        success = await backup_manager.storage_backend.delete_backup(backup_id)
        
        if success:
            return {"success": True, "message": "Backup deleted successfully"}
        else:
            return {"success": False, "error": "Failed to delete backup"}

    except Exception as e:
        logfire.error(f"Delete backup error | backup_id={backup_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# Schedule Management Endpoints
@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedule(request: CreateScheduleRequest):
    """Create a backup schedule."""
    try:
        logfire.info(f"Creating backup schedule | project_id={request.project_id} | type={request.schedule_type}")

        scheduler = get_backup_scheduler()
        
        success, result = await scheduler.create_schedule(
            project_id=request.project_id,
            schedule_type=request.schedule_type,
            cron_expression=request.cron_expression,
            interval_minutes=request.interval_minutes,
            backup_type=request.backup_type,
            enabled=request.enabled,
            created_by="api_user"
        )

        if success:
            logfire.info(f"Backup schedule created | schedule_id={result['schedule_id']}")
            return ScheduleResponse(
                success=True,
                schedule_id=result["schedule_id"],
                schedule=result["schedule"],
                message=result["message"]
            )
        else:
            logfire.error(f"Schedule creation failed | project_id={request.project_id} | error={result['error']}")
            return ScheduleResponse(
                success=False,
                message="Schedule creation failed",
                error=result["error"]
            )

    except Exception as e:
        logfire.error(f"Schedule creation endpoint error | project_id={request.project_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(schedule_id: str, request: UpdateScheduleRequest):
    """Update a backup schedule."""
    try:
        logfire.info(f"Updating backup schedule | schedule_id={schedule_id}")

        scheduler = get_backup_scheduler()
        
        # Convert request to dict, excluding None values
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        success, result = await scheduler.update_schedule(schedule_id, updates)

        if success:
            logfire.info(f"Backup schedule updated | schedule_id={schedule_id}")
            return ScheduleResponse(
                success=True,
                schedule_id=result["schedule_id"],
                schedule=result["schedule"],
                message=result["message"]
            )
        else:
            logfire.error(f"Schedule update failed | schedule_id={schedule_id} | error={result['error']}")
            return ScheduleResponse(
                success=False,
                message="Schedule update failed",
                error=result["error"]
            )

    except Exception as e:
        logfire.error(f"Schedule update endpoint error | schedule_id={schedule_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """Delete a backup schedule."""
    try:
        logfire.info(f"Deleting backup schedule | schedule_id={schedule_id}")

        scheduler = get_backup_scheduler()
        success, result = await scheduler.delete_schedule(schedule_id)
        
        if success:
            return {"success": True, "message": result["message"]}
        else:
            return {"success": False, "error": result["error"]}

    except Exception as e:
        logfire.error(f"Delete schedule error | schedule_id={schedule_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/schedules")
async def list_schedules(project_id: Optional[str] = None):
    """List backup schedules."""
    try:
        scheduler = get_backup_scheduler()
        success, result = await scheduler.list_schedules(project_id)
        
        if success:
            return result
        else:
            raise HTTPException(status_code=500, detail=result)

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"List schedules error | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.get("/schedules/{schedule_id}")
async def get_schedule(schedule_id: str):
    """Get a specific backup schedule."""
    try:
        scheduler = get_backup_scheduler()
        
        # Get schedule from database
        response = (
            scheduler.supabase_client.table("archon_backup_schedules")
            .select("*")
            .eq("id", schedule_id)
            .execute()
        )
        
        if response.data:
            return {"success": True, "schedule": response.data[0]}
        else:
            raise HTTPException(status_code=404, detail={"error": "Schedule not found"})

    except HTTPException:
        raise
    except Exception as e:
        logfire.error(f"Get schedule error | schedule_id={schedule_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


# Health and Status Endpoints
@router.get("/health")
async def backup_health():
    """Get backup system health status."""
    try:
        backup_manager = get_backup_manager()
        scheduler = get_backup_scheduler()
        
        # Get basic health metrics
        backups = await backup_manager.storage_backend.list_backups()
        success, schedules_result = await scheduler.list_schedules()
        
        schedules = schedules_result.get("schedules", []) if success else []
        active_schedules = len([s for s in schedules if s.get("enabled", False)])
        
        return {
            "success": True,
            "status": "healthy",
            "metrics": {
                "total_backups": len(backups),
                "total_schedules": len(schedules),
                "active_schedules": active_schedules,
                "scheduler_running": scheduler.is_running
            }
        }

    except Exception as e:
        logfire.error(f"Backup health check error | error={str(e)}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }
