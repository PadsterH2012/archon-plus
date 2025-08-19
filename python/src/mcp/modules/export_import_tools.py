"""
MCP Tools for Project Export/Import Operations

This module provides MCP tools for project export, import, backup management,
and restoration operations. These tools can be used in workflows and automation
to manage project portability and backup operations.
"""

import json
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from ...server.config.logfire_config import get_logger
from ...server.services.backup.backup_manager import get_backup_manager
from ...server.services.backup.backup_scheduler import get_backup_scheduler
from ...server.services.projects.export_service import ProjectExportService
from ...server.services.projects.import_service import ProjectImportService
from ...server.utils import get_supabase_client

logger = get_logger(__name__)


async def export_project_archon(
    project_id: str,
    export_type: str = "full",
    include_versions: bool = True,
    include_sources: bool = True,
    include_attachments: bool = False,
    version_limit: Optional[int] = None,
    exported_by: str = "mcp_tool"
) -> str:
    """
    Export a project to a portable package format.
    
    Args:
        project_id: UUID of the project to export
        export_type: Type of export ("full", "selective", "incremental")
        include_versions: Whether to include version history
        include_sources: Whether to include knowledge sources
        include_attachments: Whether to include file attachments
        version_limit: Maximum number of versions to include
        exported_by: User/system performing the export
        
    Returns:
        JSON string with export result including download information
    """
    try:
        logger.info(f"MCP tool: Exporting project | project_id={project_id} | type={export_type}")
        
        export_service = ProjectExportService()
        
        success, result = export_service.export_project(
            project_id=project_id,
            export_type=export_type,
            include_versions=include_versions,
            include_sources=include_sources,
            include_attachments=include_attachments,
            version_limit=version_limit,
            exported_by=exported_by
        )
        
        if success:
            return json.dumps({
                "success": True,
                "export_id": result["export_id"],
                "file_path": result["file_path"],
                "file_size": result.get("file_size"),
                "message": result["message"]
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"]
            })
            
    except Exception as e:
        logger.error(f"MCP tool export_project error | project_id={project_id} | error={str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Export failed: {str(e)}"
        })


async def import_project_archon(
    import_file_path: str,
    import_type: str = "full",
    conflict_resolution: str = "merge",
    target_project_id: Optional[str] = None,
    dry_run: bool = False,
    imported_by: str = "mcp_tool"
) -> str:
    """
    Import a project from an exported package file.
    
    Args:
        import_file_path: Path to the exported ZIP file
        import_type: Type of import ("full", "selective", "merge")
        conflict_resolution: How to handle conflicts ("merge", "overwrite", "skip", "fail")
        target_project_id: Optional existing project ID to import into
        dry_run: If True, validate but don't actually import
        imported_by: User/system performing the import
        
    Returns:
        JSON string with import result including project information
    """
    try:
        logger.info(f"MCP tool: Importing project | file={import_file_path} | type={import_type}")
        
        import_service = ProjectImportService()
        
        success, result = import_service.import_project(
            import_file_path=import_file_path,
            import_type=import_type,
            conflict_resolution=conflict_resolution,
            target_project_id=target_project_id,
            imported_by=imported_by,
            dry_run=dry_run
        )
        
        if success:
            return json.dumps({
                "success": True,
                "project_id": result.get("project_id"),
                "import_summary": result.get("import_summary"),
                "conflicts_resolved": result.get("conflicts_resolved"),
                "message": result["message"],
                "dry_run": dry_run
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"]
            })
            
    except Exception as e:
        logger.error(f"MCP tool import_project error | file={import_file_path} | error={str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Import failed: {str(e)}"
        })


async def validate_import_file_archon(import_file_path: str) -> str:
    """
    Validate an import file without performing the actual import.
    
    Args:
        import_file_path: Path to the exported ZIP file to validate
        
    Returns:
        JSON string with validation result and file metadata
    """
    try:
        logger.info(f"MCP tool: Validating import file | file={import_file_path}")
        
        import_service = ProjectImportService()
        
        is_valid, result = import_service.validate_import_file(import_file_path)
        
        return json.dumps({
            "valid": is_valid,
            "project_title": result.get("project_title"),
            "project_id": result.get("project_id"),
            "task_count": result.get("task_count"),
            "document_count": result.get("document_count"),
            "version_count": result.get("version_count"),
            "source_count": result.get("source_count"),
            "export_timestamp": result.get("export_timestamp"),
            "exported_by": result.get("exported_by"),
            "error": result.get("error")
        })
        
    except Exception as e:
        logger.error(f"MCP tool validate_import_file error | file={import_file_path} | error={str(e)}")
        return json.dumps({
            "valid": False,
            "error": f"Validation failed: {str(e)}"
        })


async def create_backup_archon(
    project_id: str,
    backup_type: str = "full",
    compress: bool = True,
    encrypt: bool = False,
    created_by: str = "mcp_tool"
) -> str:
    """
    Create a backup of a specific project.
    
    Args:
        project_id: UUID of the project to backup
        backup_type: Type of backup ("full", "selective", "incremental")
        compress: Whether to compress the backup
        encrypt: Whether to encrypt the backup
        created_by: User/system creating the backup
        
    Returns:
        JSON string with backup result including backup ID and metadata
    """
    try:
        logger.info(f"MCP tool: Creating backup | project_id={project_id} | type={backup_type}")
        
        backup_manager = get_backup_manager()
        
        success, result = await backup_manager.create_project_backup(
            project_id=project_id,
            backup_type=backup_type,
            created_by=created_by,
            compress=compress,
            encrypt=encrypt
        )
        
        if success:
            return json.dumps({
                "success": True,
                "backup_id": result["backup_id"],
                "backup_metadata": result["backup_metadata"],
                "message": result["message"]
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"]
            })
            
    except Exception as e:
        logger.error(f"MCP tool create_backup error | project_id={project_id} | error={str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Backup creation failed: {str(e)}"
        })


async def restore_backup_archon(
    backup_id: str,
    target_project_id: Optional[str] = None,
    conflict_resolution: str = "merge",
    restored_by: str = "mcp_tool"
) -> str:
    """
    Restore a project from a backup.
    
    Args:
        backup_id: UUID of the backup to restore
        target_project_id: Optional existing project ID to restore into
        conflict_resolution: How to handle conflicts ("merge", "overwrite", "skip", "fail")
        restored_by: User/system performing the restoration
        
    Returns:
        JSON string with restoration result including project information
    """
    try:
        logger.info(f"MCP tool: Restoring backup | backup_id={backup_id}")
        
        backup_manager = get_backup_manager()
        
        success, result = await backup_manager.restore_project_backup(
            backup_id=backup_id,
            target_project_id=target_project_id,
            conflict_resolution=conflict_resolution,
            restored_by=restored_by
        )
        
        if success:
            return json.dumps({
                "success": True,
                "backup_id": result["backup_id"],
                "restored_project_id": result.get("restored_project_id"),
                "import_summary": result.get("import_summary"),
                "message": result["message"]
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"]
            })
            
    except Exception as e:
        logger.error(f"MCP tool restore_backup error | backup_id={backup_id} | error={str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Backup restoration failed: {str(e)}"
        })


async def list_backups_archon(project_id: Optional[str] = None) -> str:
    """
    List available backups, optionally filtered by project.
    
    Args:
        project_id: Optional project ID to filter backups
        
    Returns:
        JSON string with list of available backups and metadata
    """
    try:
        logger.info(f"MCP tool: Listing backups | project_id={project_id}")
        
        backup_manager = get_backup_manager()
        
        backups = await backup_manager.storage_backend.list_backups()
        
        # Filter by project_id if provided
        if project_id:
            backups = [b for b in backups if b.get("project_id") == project_id]
        
        return json.dumps({
            "success": True,
            "backups": backups,
            "total_count": len(backups),
            "filtered_by_project": project_id is not None
        })
        
    except Exception as e:
        logger.error(f"MCP tool list_backups error | project_id={project_id} | error={str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to list backups: {str(e)}"
        })


async def schedule_backup_archon(
    project_id: str,
    schedule_type: str = "cron",
    cron_expression: Optional[str] = None,
    interval_minutes: Optional[int] = None,
    backup_type: str = "full",
    enabled: bool = True,
    created_by: str = "mcp_tool"
) -> str:
    """
    Schedule automatic backups for a project.
    
    Args:
        project_id: UUID of the project to schedule backups for
        schedule_type: Type of schedule ("cron" or "interval")
        cron_expression: Cron expression for cron-based schedules
        interval_minutes: Interval in minutes for interval-based schedules
        backup_type: Type of backup to create ("full", "selective", "incremental")
        enabled: Whether the schedule should be enabled
        created_by: User/system creating the schedule
        
    Returns:
        JSON string with schedule creation result
    """
    try:
        logger.info(f"MCP tool: Scheduling backup | project_id={project_id} | type={schedule_type}")
        
        scheduler = get_backup_scheduler()
        
        success, result = await scheduler.create_schedule(
            project_id=project_id,
            schedule_type=schedule_type,
            cron_expression=cron_expression,
            interval_minutes=interval_minutes,
            backup_type=backup_type,
            enabled=enabled,
            created_by=created_by
        )
        
        if success:
            return json.dumps({
                "success": True,
                "schedule_id": result["schedule_id"],
                "schedule": result["schedule"],
                "message": result["message"]
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"]
            })
            
    except Exception as e:
        logger.error(f"MCP tool schedule_backup error | project_id={project_id} | error={str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Backup scheduling failed: {str(e)}"
        })


async def list_backup_schedules_archon(project_id: Optional[str] = None) -> str:
    """
    List backup schedules, optionally filtered by project.
    
    Args:
        project_id: Optional project ID to filter schedules
        
    Returns:
        JSON string with list of backup schedules
    """
    try:
        logger.info(f"MCP tool: Listing backup schedules | project_id={project_id}")
        
        scheduler = get_backup_scheduler()
        
        success, result = await scheduler.list_schedules(project_id)
        
        if success:
            return json.dumps({
                "success": True,
                "schedules": result["schedules"],
                "total_count": result["total_count"],
                "filtered_by_project": project_id is not None
            })
        else:
            return json.dumps({
                "success": False,
                "error": result["error"]
            })
            
    except Exception as e:
        logger.error(f"MCP tool list_backup_schedules error | project_id={project_id} | error={str(e)}")
        return json.dumps({
            "success": False,
            "error": f"Failed to list backup schedules: {str(e)}"
        })
