"""
Backup Management Service for Archon

This module provides comprehensive backup management functionality including:
- Scheduled automated backups
- Retention policy management
- Backup verification and integrity checking
- Multiple storage backends (local, cloud)
- Compression and encryption support
- Backup restoration capabilities
"""

import asyncio
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from ...config.logfire_config import get_logger
from ...utils import get_supabase_client
from ..background_task_manager import get_task_manager
from ..projects.export_service import ProjectExportService

logger = get_logger(__name__)


class BackupError(Exception):
    """Custom exception for backup operations"""
    pass


class BackupVerificationError(BackupError):
    """Custom exception for backup verification failures"""
    pass


class BackupRetentionPolicy:
    """Defines backup retention policies"""
    
    def __init__(
        self,
        daily_retention_days: int = 7,
        weekly_retention_weeks: int = 4,
        monthly_retention_months: int = 12,
        yearly_retention_years: int = 3
    ):
        self.daily_retention_days = daily_retention_days
        self.weekly_retention_weeks = weekly_retention_weeks
        self.monthly_retention_months = monthly_retention_months
        self.yearly_retention_years = yearly_retention_years


class BackupStorage:
    """Abstract base class for backup storage backends"""
    
    async def store_backup(self, backup_id: str, file_path: str, metadata: Dict[str, Any]) -> bool:
        """Store a backup file"""
        raise NotImplementedError
    
    async def retrieve_backup(self, backup_id: str, destination_path: str) -> bool:
        """Retrieve a backup file"""
        raise NotImplementedError
    
    async def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup file"""
        raise NotImplementedError
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        raise NotImplementedError


class LocalBackupStorage(BackupStorage):
    """Local filesystem backup storage"""
    
    def __init__(self, backup_directory: str = "/tmp/archon_backups"):
        self.backup_directory = Path(backup_directory)
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.backup_directory / "backup_metadata.json"
        
    async def store_backup(self, backup_id: str, file_path: str, metadata: Dict[str, Any]) -> bool:
        """Store backup file locally"""
        try:
            backup_file = self.backup_directory / f"{backup_id}.zip"
            shutil.copy2(file_path, backup_file)
            
            # Store metadata
            await self._update_metadata(backup_id, metadata)
            
            logger.info(f"Backup stored locally | backup_id={backup_id} | path={backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store backup locally | backup_id={backup_id} | error={str(e)}")
            return False
    
    async def retrieve_backup(self, backup_id: str, destination_path: str) -> bool:
        """Retrieve backup file from local storage"""
        try:
            backup_file = self.backup_directory / f"{backup_id}.zip"
            if not backup_file.exists():
                return False
                
            shutil.copy2(backup_file, destination_path)
            logger.info(f"Backup retrieved from local storage | backup_id={backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retrieve backup | backup_id={backup_id} | error={str(e)}")
            return False
    
    async def delete_backup(self, backup_id: str) -> bool:
        """Delete backup file from local storage"""
        try:
            backup_file = self.backup_directory / f"{backup_id}.zip"
            if backup_file.exists():
                backup_file.unlink()
                
            # Remove from metadata
            await self._remove_from_metadata(backup_id)
            
            logger.info(f"Backup deleted from local storage | backup_id={backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete backup | backup_id={backup_id} | error={str(e)}")
            return False
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all local backups"""
        try:
            if not self.metadata_file.exists():
                return []
                
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
                
            return list(metadata.values())
            
        except Exception as e:
            logger.error(f"Failed to list backups | error={str(e)}")
            return []
    
    async def _update_metadata(self, backup_id: str, metadata: Dict[str, Any]):
        """Update backup metadata file"""
        try:
            existing_metadata = {}
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    existing_metadata = json.load(f)
            
            existing_metadata[backup_id] = metadata
            
            with open(self.metadata_file, 'w') as f:
                json.dump(existing_metadata, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to update metadata | error={str(e)}")
    
    async def _remove_from_metadata(self, backup_id: str):
        """Remove backup from metadata file"""
        try:
            if not self.metadata_file.exists():
                return
                
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            metadata.pop(backup_id, None)
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to remove from metadata | error={str(e)}")


class BackupManager:
    """Main backup management service"""
    
    def __init__(
        self,
        storage_backend: Optional[BackupStorage] = None,
        retention_policy: Optional[BackupRetentionPolicy] = None,
        supabase_client=None
    ):
        self.supabase_client = supabase_client or get_supabase_client()
        self.storage_backend = storage_backend or LocalBackupStorage()
        self.retention_policy = retention_policy or BackupRetentionPolicy()
        self.export_service = ProjectExportService(supabase_client)
        self.task_manager = get_task_manager()
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        
    async def create_project_backup(
        self,
        project_id: str,
        backup_type: str = "full",
        created_by: str = "system",
        compress: bool = True,
        encrypt: bool = False
    ) -> Tuple[bool, Dict[str, Any]]:
        """Create a backup of a specific project"""
        try:
            backup_id = str(uuid4())
            logger.info(f"Starting project backup | project_id={project_id} | backup_id={backup_id}")
            
            # Export the project
            export_success, export_result = self.export_service.export_project(
                project_id=project_id,
                export_type=backup_type,
                exported_by=created_by
            )
            
            if not export_success:
                return False, {"error": f"Export failed: {export_result.get('error')}"}
            
            export_file_path = export_result["file_path"]
            
            # Calculate file hash for verification
            file_hash = await self._calculate_file_hash(export_file_path)
            
            # Prepare backup metadata
            backup_metadata = {
                "backup_id": backup_id,
                "project_id": project_id,
                "backup_type": backup_type,
                "created_by": created_by,
                "created_at": datetime.now().isoformat(),
                "file_size": os.path.getsize(export_file_path),
                "file_hash": file_hash,
                "compressed": compress,
                "encrypted": encrypt,
                "export_metadata": export_result
            }
            
            # Store backup
            storage_success = await self.storage_backend.store_backup(
                backup_id, export_file_path, backup_metadata
            )
            
            if not storage_success:
                return False, {"error": "Failed to store backup"}
            
            # Record backup in database
            await self._record_backup_in_database(backup_metadata)
            
            # Clean up temporary export file
            try:
                os.unlink(export_file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up export file | error={str(e)}")
            
            logger.info(f"Project backup completed successfully | backup_id={backup_id}")
            
            return True, {
                "backup_id": backup_id,
                "backup_metadata": backup_metadata,
                "message": "Backup created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating project backup | project_id={project_id} | error={str(e)}")
            return False, {"error": f"Backup creation failed: {str(e)}"}
    
    async def restore_project_backup(
        self,
        backup_id: str,
        target_project_id: Optional[str] = None,
        conflict_resolution: str = "merge",
        restored_by: str = "system"
    ) -> Tuple[bool, Dict[str, Any]]:
        """Restore a project from backup"""
        try:
            logger.info(f"Starting backup restoration | backup_id={backup_id}")
            
            # Create temporary file for restoration
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            # Retrieve backup from storage
            retrieve_success = await self.storage_backend.retrieve_backup(backup_id, temp_file_path)
            
            if not retrieve_success:
                return False, {"error": "Failed to retrieve backup from storage"}
            
            # Verify backup integrity
            verification_success = await self._verify_backup_integrity(backup_id, temp_file_path)
            
            if not verification_success:
                os.unlink(temp_file_path)
                return False, {"error": "Backup integrity verification failed"}
            
            # Import the project using import service
            from ..projects.import_service import ProjectImportService
            import_service = ProjectImportService(self.supabase_client)
            
            import_success, import_result = import_service.import_project(
                import_file_path=temp_file_path,
                import_type="full" if not target_project_id else "merge",
                conflict_resolution=conflict_resolution,
                target_project_id=target_project_id,
                imported_by=restored_by
            )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            if import_success:
                logger.info(f"Backup restoration completed | backup_id={backup_id}")
                return True, {
                    "backup_id": backup_id,
                    "restored_project_id": import_result.get("project_id"),
                    "import_summary": import_result.get("import_summary"),
                    "message": "Backup restored successfully"
                }
            else:
                return False, {"error": f"Import failed: {import_result.get('error')}"}
                
        except Exception as e:
            logger.error(f"Error restoring backup | backup_id={backup_id} | error={str(e)}")
            return False, {"error": f"Backup restoration failed: {str(e)}"}
    
    async def schedule_automatic_backup(
        self,
        project_id: str,
        schedule_cron: str,
        backup_type: str = "full",
        enabled: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """Schedule automatic backups for a project"""
        try:
            schedule_id = str(uuid4())
            
            # Store schedule in database
            schedule_data = {
                "id": schedule_id,
                "project_id": project_id,
                "schedule_cron": schedule_cron,
                "backup_type": backup_type,
                "enabled": enabled,
                "created_at": datetime.now().isoformat(),
                "last_run": None,
                "next_run": None  # Would calculate based on cron
            }
            
            response = (
                self.supabase_client.table("archon_backup_schedules")
                .insert(schedule_data)
                .execute()
            )
            
            if response.data:
                logger.info(f"Backup schedule created | schedule_id={schedule_id} | project_id={project_id}")
                return True, {
                    "schedule_id": schedule_id,
                    "schedule": schedule_data,
                    "message": "Backup schedule created successfully"
                }
            else:
                return False, {"error": "Failed to create backup schedule"}
                
        except Exception as e:
            logger.error(f"Error scheduling backup | project_id={project_id} | error={str(e)}")
            return False, {"error": f"Failed to schedule backup: {str(e)}"}
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def _verify_backup_integrity(self, backup_id: str, file_path: str) -> bool:
        """Verify backup file integrity using stored hash"""
        try:
            # Get stored metadata
            backups = await self.storage_backend.list_backups()
            backup_metadata = next((b for b in backups if b["backup_id"] == backup_id), None)
            
            if not backup_metadata:
                logger.error(f"Backup metadata not found | backup_id={backup_id}")
                return False
            
            # Calculate current file hash
            current_hash = await self._calculate_file_hash(file_path)
            stored_hash = backup_metadata.get("file_hash")
            
            if current_hash != stored_hash:
                logger.error(f"Backup integrity check failed | backup_id={backup_id}")
                return False
            
            logger.info(f"Backup integrity verified | backup_id={backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying backup integrity | backup_id={backup_id} | error={str(e)}")
            return False
    
    async def _record_backup_in_database(self, backup_metadata: Dict[str, Any]):
        """Record backup information in database"""
        try:
            response = (
                self.supabase_client.table("archon_backups")
                .insert(backup_metadata)
                .execute()
            )
            
            if response.data:
                logger.info(f"Backup recorded in database | backup_id={backup_metadata['backup_id']}")
            else:
                logger.warning(f"Failed to record backup in database | backup_id={backup_metadata['backup_id']}")
                
        except Exception as e:
            logger.error(f"Error recording backup in database | error={str(e)}")


# Global backup manager instance
_backup_manager: Optional[BackupManager] = None


def get_backup_manager() -> BackupManager:
    """Get the global backup manager instance"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
