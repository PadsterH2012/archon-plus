"""
Tests for Backup Management System

This module tests the backup functionality including:
- Backup creation and restoration
- Backup scheduling and automation
- Storage backend operations
- Retention policy enforcement
"""

import asyncio
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.server.services.backup.backup_manager import (
    BackupManager,
    BackupRetentionPolicy,
    LocalBackupStorage
)
from src.server.services.backup.backup_scheduler import BackupScheduler


class TestLocalBackupStorage:
    """Test cases for LocalBackupStorage"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = LocalBackupStorage(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_store_backup(self):
        """Test storing a backup file"""
        # Create a test file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test backup content")
            temp_file_path = temp_file.name

        try:
            # Store backup
            backup_id = "test-backup-123"
            metadata = {
                "backup_id": backup_id,
                "project_id": "test-project",
                "created_at": datetime.now().isoformat()
            }

            success = await self.storage.store_backup(backup_id, temp_file_path, metadata)
            
            assert success is True
            
            # Verify file exists
            backup_file = os.path.join(self.temp_dir, f"{backup_id}.zip")
            assert os.path.exists(backup_file)
            
            # Verify metadata
            backups = await self.storage.list_backups()
            assert len(backups) == 1
            assert backups[0]["backup_id"] == backup_id

        finally:
            os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_retrieve_backup(self):
        """Test retrieving a backup file"""
        # Create and store a backup first
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test backup content")
            temp_file_path = temp_file.name

        backup_id = "test-backup-456"
        metadata = {"backup_id": backup_id}
        
        await self.storage.store_backup(backup_id, temp_file_path, metadata)
        os.unlink(temp_file_path)

        # Retrieve backup
        with tempfile.NamedTemporaryFile(delete=False) as dest_file:
            dest_path = dest_file.name

        try:
            success = await self.storage.retrieve_backup(backup_id, dest_path)
            
            assert success is True
            assert os.path.exists(dest_path)
            
            # Verify content
            with open(dest_path, 'rb') as f:
                content = f.read()
            assert content == b"test backup content"

        finally:
            if os.path.exists(dest_path):
                os.unlink(dest_path)

    @pytest.mark.asyncio
    async def test_delete_backup(self):
        """Test deleting a backup file"""
        # Create and store a backup first
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test backup content")
            temp_file_path = temp_file.name

        backup_id = "test-backup-789"
        metadata = {"backup_id": backup_id}
        
        await self.storage.store_backup(backup_id, temp_file_path, metadata)
        os.unlink(temp_file_path)

        # Delete backup
        success = await self.storage.delete_backup(backup_id)
        
        assert success is True
        
        # Verify file is deleted
        backup_file = os.path.join(self.temp_dir, f"{backup_id}.zip")
        assert not os.path.exists(backup_file)
        
        # Verify metadata is removed
        backups = await self.storage.list_backups()
        assert len(backups) == 0


class TestBackupManager:
    """Test cases for BackupManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.mock_storage = AsyncMock(spec=LocalBackupStorage)
        self.mock_export_service = AsyncMock()
        
        self.backup_manager = BackupManager(
            storage_backend=self.mock_storage,
            supabase_client=self.mock_supabase
        )
        self.backup_manager.export_service = self.mock_export_service

    @pytest.mark.asyncio
    async def test_create_project_backup_success(self):
        """Test successful project backup creation"""
        # Mock export service
        self.mock_export_service.export_project.return_value = (True, {
            "file_path": "/tmp/test-export.zip",
            "export_id": "export-123"
        })
        
        # Mock storage
        self.mock_storage.store_backup.return_value = True
        
        # Mock file operations
        with patch('os.path.getsize', return_value=1024), \
             patch('os.unlink'), \
             patch.object(self.backup_manager, '_calculate_file_hash', return_value="abc123"), \
             patch.object(self.backup_manager, '_record_backup_in_database'):
            
            success, result = await self.backup_manager.create_project_backup(
                project_id="test-project-id",
                backup_type="full"
            )
        
        assert success is True
        assert "backup_id" in result
        assert result["backup_metadata"]["project_id"] == "test-project-id"
        
        # Verify export service was called
        self.mock_export_service.export_project.assert_called_once()
        
        # Verify storage was called
        self.mock_storage.store_backup.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_project_backup_export_failure(self):
        """Test backup creation when export fails"""
        # Mock export service failure
        self.mock_export_service.export_project.return_value = (False, {
            "error": "Export failed"
        })
        
        success, result = await self.backup_manager.create_project_backup(
            project_id="test-project-id"
        )
        
        assert success is False
        assert "Export failed" in result["error"]
        
        # Verify storage was not called
        self.mock_storage.store_backup.assert_not_called()

    @pytest.mark.asyncio
    async def test_restore_project_backup_success(self):
        """Test successful backup restoration"""
        # Mock storage retrieval
        self.mock_storage.retrieve_backup.return_value = True
        
        # Mock backup verification
        with patch.object(self.backup_manager, '_verify_backup_integrity', return_value=True), \
             patch('tempfile.NamedTemporaryFile'), \
             patch('os.unlink'):
            
            # Mock import service
            with patch('src.server.services.backup.backup_manager.ProjectImportService') as mock_import_class:
                mock_import_service = AsyncMock()
                mock_import_class.return_value = mock_import_service
                mock_import_service.import_project.return_value = (True, {
                    "project_id": "restored-project-id",
                    "import_summary": {"tasks_imported": 5}
                })
                
                success, result = await self.backup_manager.restore_project_backup(
                    backup_id="test-backup-id"
                )
        
        assert success is True
        assert result["restored_project_id"] == "restored-project-id"
        
        # Verify storage retrieval was called
        self.mock_storage.retrieve_backup.assert_called_once()

    @pytest.mark.asyncio
    async def test_restore_project_backup_retrieval_failure(self):
        """Test backup restoration when retrieval fails"""
        # Mock storage retrieval failure
        self.mock_storage.retrieve_backup.return_value = False
        
        success, result = await self.backup_manager.restore_project_backup(
            backup_id="test-backup-id"
        )
        
        assert success is False
        assert "Failed to retrieve backup" in result["error"]

    @pytest.mark.asyncio
    async def test_schedule_automatic_backup(self):
        """Test scheduling automatic backups"""
        # Mock database response
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "schedule-123"}
        ]
        
        success, result = await self.backup_manager.schedule_automatic_backup(
            project_id="test-project-id",
            schedule_cron="0 2 * * *"
        )
        
        assert success is True
        assert "schedule_id" in result
        assert result["schedule"]["project_id"] == "test-project-id"
        
        # Verify database call
        self.mock_supabase.table.assert_called_with("archon_backup_schedules")


class TestBackupScheduler:
    """Test cases for BackupScheduler"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.mock_backup_manager = AsyncMock()
        
        self.scheduler = BackupScheduler(self.mock_supabase)
        self.scheduler.backup_manager = self.mock_backup_manager

    @pytest.mark.asyncio
    async def test_create_schedule_cron(self):
        """Test creating a cron-based schedule"""
        # Mock database response
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "schedule-123"}
        ]
        
        success, result = await self.scheduler.create_schedule(
            project_id="test-project-id",
            schedule_type="cron",
            cron_expression="0 2 * * *",
            backup_type="full"
        )
        
        assert success is True
        assert "schedule_id" in result
        assert result["schedule"]["cron_expression"] == "0 2 * * *"

    @pytest.mark.asyncio
    async def test_create_schedule_invalid_cron(self):
        """Test creating schedule with invalid cron expression"""
        success, result = await self.scheduler.create_schedule(
            project_id="test-project-id",
            schedule_type="cron",
            cron_expression="invalid cron",
            backup_type="full"
        )
        
        assert success is False
        assert "Invalid cron expression" in result["error"]

    @pytest.mark.asyncio
    async def test_create_schedule_interval(self):
        """Test creating an interval-based schedule"""
        # Mock database response
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "schedule-456"}
        ]
        
        success, result = await self.scheduler.create_schedule(
            project_id="test-project-id",
            schedule_type="interval",
            interval_minutes=60,
            backup_type="incremental"
        )
        
        assert success is True
        assert result["schedule"]["interval_minutes"] == 60

    @pytest.mark.asyncio
    async def test_update_schedule(self):
        """Test updating a schedule"""
        # Mock existing schedule
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": "schedule-123",
                "cron_expression": "0 2 * * *",
                "schedule_type": "cron"
            }
        ]
        
        # Mock update response
        self.mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": "schedule-123",
                "cron_expression": "0 3 * * *",
                "schedule_type": "cron"
            }
        ]
        
        success, result = await self.scheduler.update_schedule(
            schedule_id="schedule-123",
            updates={"cron_expression": "0 3 * * *"}
        )
        
        assert success is True
        assert result["schedule"]["cron_expression"] == "0 3 * * *"

    @pytest.mark.asyncio
    async def test_delete_schedule(self):
        """Test deleting a schedule"""
        # Mock delete response
        self.mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            {"id": "schedule-123"}
        ]
        
        success, result = await self.scheduler.delete_schedule("schedule-123")
        
        assert success is True
        assert "deleted successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_list_schedules(self):
        """Test listing schedules"""
        # Mock database response
        self.mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
            {"id": "schedule-1", "project_id": "project-1"},
            {"id": "schedule-2", "project_id": "project-2"}
        ]
        
        success, result = await self.scheduler.list_schedules()
        
        assert success is True
        assert len(result["schedules"]) == 2
        assert result["total_count"] == 2

    def test_calculate_next_run_cron(self):
        """Test calculating next run time for cron schedule"""
        next_run = self.scheduler._calculate_next_run(
            schedule_type="cron",
            cron_expression="0 2 * * *"
        )
        
        assert next_run is not None
        assert isinstance(next_run, datetime)

    def test_calculate_next_run_interval(self):
        """Test calculating next run time for interval schedule"""
        next_run = self.scheduler._calculate_next_run(
            schedule_type="interval",
            interval_minutes=60
        )
        
        assert next_run is not None
        assert isinstance(next_run, datetime)
        
        # Should be approximately 60 minutes from now
        now = datetime.now()
        expected = now + timedelta(minutes=60)
        assert abs((next_run - expected).total_seconds()) < 60  # Within 1 minute tolerance


class TestBackupRetentionPolicy:
    """Test cases for BackupRetentionPolicy"""

    def test_default_policy(self):
        """Test default retention policy values"""
        policy = BackupRetentionPolicy()
        
        assert policy.daily_retention_days == 7
        assert policy.weekly_retention_weeks == 4
        assert policy.monthly_retention_months == 12
        assert policy.yearly_retention_years == 3

    def test_custom_policy(self):
        """Test custom retention policy values"""
        policy = BackupRetentionPolicy(
            daily_retention_days=14,
            weekly_retention_weeks=8,
            monthly_retention_months=24,
            yearly_retention_years=5
        )
        
        assert policy.daily_retention_days == 14
        assert policy.weekly_retention_weeks == 8
        assert policy.monthly_retention_months == 24
        assert policy.yearly_retention_years == 5
