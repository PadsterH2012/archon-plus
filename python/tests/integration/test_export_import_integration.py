"""
Integration Tests for Export/Import System

This module provides comprehensive integration tests for the complete export/import
system including end-to-end workflows, data integrity validation, performance testing,
and real-world scenario testing.
"""

import asyncio
import json
import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.server.services.backup.backup_manager import BackupManager, LocalBackupStorage
from src.server.services.backup.backup_scheduler import BackupScheduler
from src.server.services.projects.export_service import ProjectExportService
from src.server.services.projects.import_service import ProjectImportService


class TestExportImportIntegration:
    """Integration tests for complete export/import workflows"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create services
        self.export_service = ProjectExportService(self.mock_supabase)
        self.import_service = ProjectImportService(self.mock_supabase)
        
        # Create test project data
        self.test_project_data = {
            "id": "test-project-123",
            "title": "Integration Test Project",
            "description": "Test project for integration testing",
            "github_repo": "https://github.com/test/repo",
            "pinned": False,
            "docs": [
                {
                    "id": "doc-1",
                    "document_type": "prp",
                    "title": "Test PRP",
                    "content": {"goal": "Test goal", "why": ["Test reason"]},
                    "metadata": {"version": "1.0", "author": "test"}
                }
            ],
            "features": ["authentication", "api"],
            "data": {"config": "test"},
            "created_at": "2025-08-18T22:00:00Z",
            "updated_at": "2025-08-18T22:00:00Z"
        }
        
        self.test_tasks_data = [
            {
                "id": "task-1",
                "project_id": "test-project-123",
                "title": "Test Task 1",
                "description": "First test task",
                "status": "todo",
                "assignee": "User",
                "task_order": 1,
                "feature": "authentication",
                "sources": [],
                "code_examples": [],
                "created_at": "2025-08-18T22:00:00Z",
                "updated_at": "2025-08-18T22:00:00Z"
            },
            {
                "id": "task-2",
                "project_id": "test-project-123",
                "title": "Test Task 2",
                "description": "Second test task",
                "status": "doing",
                "assignee": "AI IDE Agent",
                "task_order": 2,
                "feature": "api",
                "sources": [],
                "code_examples": [],
                "created_at": "2025-08-18T22:00:00Z",
                "updated_at": "2025-08-18T22:00:00Z"
            }
        ]

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_full_export_import_cycle(self):
        """Test complete export and import cycle"""
        # Mock database responses for export
        self._mock_export_database_responses()
        
        # Perform export
        success, export_result = self.export_service.export_project(
            project_id="test-project-123",
            export_type="full",
            exported_by="integration_test"
        )
        
        assert success is True
        assert "export_id" in export_result
        assert "file_path" in export_result
        
        export_file_path = export_result["file_path"]
        assert os.path.exists(export_file_path)
        
        # Verify export file structure
        self._verify_export_file_structure(export_file_path)
        
        # Mock database responses for import
        self._mock_import_database_responses()
        
        # Perform import
        success, import_result = self.import_service.import_project(
            import_file_path=export_file_path,
            import_type="full",
            imported_by="integration_test"
        )
        
        assert success is True
        assert "project_id" in import_result
        assert "import_summary" in import_result
        
        # Verify import summary
        summary = import_result["import_summary"]
        assert summary["project_created"] is True
        assert summary["tasks_imported"] == 2
        assert summary["documents_imported"] == 1

    @pytest.mark.asyncio
    async def test_selective_export_import(self):
        """Test selective export and import"""
        # Mock database responses
        self._mock_export_database_responses()
        
        # Export only tasks
        success, export_result = self.export_service.export_project(
            project_id="test-project-123",
            export_type="selective",
            selective_components=["tasks"],
            exported_by="integration_test"
        )
        
        assert success is True
        export_file_path = export_result["file_path"]
        
        # Verify selective export contains only tasks
        with zipfile.ZipFile(export_file_path, 'r') as zipf:
            files = zipf.namelist()
            assert "manifest.json" in files
            assert "project.json" in files
            assert "tasks.json" in files
            assert "documents/" not in [f for f in files if f.startswith("documents/")]
        
        # Import selectively
        self._mock_import_database_responses()
        
        success, import_result = self.import_service.import_project(
            import_file_path=export_file_path,
            import_type="selective",
            selective_components=["tasks"],
            imported_by="integration_test"
        )
        
        assert success is True
        summary = import_result["import_summary"]
        assert summary["tasks_imported"] == 2
        assert summary["documents_imported"] == 0

    @pytest.mark.asyncio
    async def test_conflict_resolution_merge(self):
        """Test import with conflict resolution"""
        # Create export
        self._mock_export_database_responses()
        
        success, export_result = self.export_service.export_project(
            project_id="test-project-123",
            export_type="full",
            exported_by="integration_test"
        )
        
        assert success is True
        export_file_path = export_result["file_path"]
        
        # Mock existing project for conflict
        self._mock_import_database_responses_with_conflicts()
        
        # Import with merge conflict resolution
        success, import_result = self.import_service.import_project(
            import_file_path=export_file_path,
            import_type="merge",
            target_project_id="existing-project-456",
            conflict_resolution="merge",
            imported_by="integration_test"
        )
        
        assert success is True
        assert "conflicts_resolved" in import_result
        assert len(import_result["conflicts_resolved"]) > 0

    @pytest.mark.asyncio
    async def test_data_integrity_validation(self):
        """Test data integrity during export/import"""
        self._mock_export_database_responses()
        
        # Export project
        success, export_result = self.export_service.export_project(
            project_id="test-project-123",
            export_type="full",
            exported_by="integration_test"
        )
        
        assert success is True
        export_file_path = export_result["file_path"]
        
        # Validate export file integrity
        is_valid, validation_result = self.import_service.validate_import_file(export_file_path)
        
        assert is_valid is True
        assert validation_result["project_title"] == "Integration Test Project"
        assert validation_result["task_count"] == 2
        assert validation_result["document_count"] == 1

    @pytest.mark.asyncio
    async def test_large_project_export_import(self):
        """Test export/import with large project data"""
        # Create large project data
        large_tasks = []
        for i in range(100):
            large_tasks.append({
                "id": f"task-{i}",
                "project_id": "test-project-123",
                "title": f"Large Test Task {i}",
                "description": f"Description for task {i}" * 10,  # Make it larger
                "status": "todo",
                "assignee": "User",
                "task_order": i,
                "feature": "bulk_test",
                "sources": [],
                "code_examples": [],
                "created_at": "2025-08-18T22:00:00Z",
                "updated_at": "2025-08-18T22:00:00Z"
            })
        
        # Mock database responses with large data
        self._mock_export_database_responses(large_tasks)
        
        # Export large project
        success, export_result = self.export_service.export_project(
            project_id="test-project-123",
            export_type="full",
            exported_by="integration_test"
        )
        
        assert success is True
        export_file_path = export_result["file_path"]
        
        # Verify file size is reasonable
        file_size = os.path.getsize(export_file_path)
        assert file_size > 1024  # Should be larger than 1KB
        assert file_size < 10 * 1024 * 1024  # Should be less than 10MB
        
        # Import large project
        self._mock_import_database_responses()
        
        success, import_result = self.import_service.import_project(
            import_file_path=export_file_path,
            import_type="full",
            imported_by="integration_test"
        )
        
        assert success is True
        summary = import_result["import_summary"]
        assert summary["tasks_imported"] == 100

    @pytest.mark.asyncio
    async def test_version_history_export_import(self):
        """Test export/import with version history"""
        # Mock version history data
        version_history = [
            {
                "id": "version-1",
                "project_id": "test-project-123",
                "field_name": "docs",
                "version_number": 1,
                "content": {"test": "version 1"},
                "change_summary": "Initial version",
                "created_by": "test",
                "created_at": "2025-08-18T21:00:00Z"
            },
            {
                "id": "version-2",
                "project_id": "test-project-123",
                "field_name": "docs",
                "version_number": 2,
                "content": {"test": "version 2"},
                "change_summary": "Updated version",
                "created_by": "test",
                "created_at": "2025-08-18T22:00:00Z"
            }
        ]
        
        self._mock_export_database_responses(versions=version_history)
        
        # Export with version history
        success, export_result = self.export_service.export_project(
            project_id="test-project-123",
            export_type="full",
            include_versions=True,
            exported_by="integration_test"
        )
        
        assert success is True
        export_file_path = export_result["file_path"]
        
        # Verify versions are included
        with zipfile.ZipFile(export_file_path, 'r') as zipf:
            files = zipf.namelist()
            assert "versions.json" in files
            
            # Check version content
            versions_content = json.loads(zipf.read("versions.json"))
            assert len(versions_content["versions"]) == 2

    def _mock_export_database_responses(self, tasks=None, versions=None):
        """Mock database responses for export operations"""
        if tasks is None:
            tasks = self.test_tasks_data
        
        # Mock project query
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [self.test_project_data]
        
        # Mock tasks query
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = tasks
        
        # Mock versions query
        if versions:
            self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = versions
        else:
            self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        
        # Mock sources query
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    def _mock_import_database_responses(self):
        """Mock database responses for import operations"""
        # Mock project creation
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "imported-project-456"}
        ]
        
        # Mock task creation
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "imported-task-1"}, {"id": "imported-task-2"}
        ]

    def _mock_import_database_responses_with_conflicts(self):
        """Mock database responses for import with conflicts"""
        # Mock existing project
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": "existing-project-456",
                "title": "Existing Project",
                "description": "Existing description"
            }
        ]
        
        # Mock existing tasks with conflicts
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                "id": "existing-task-1",
                "title": "Test Task 1",  # Same title as import
                "description": "Existing task description"
            }
        ]

    def _verify_export_file_structure(self, export_file_path: str):
        """Verify the structure of an export file"""
        with zipfile.ZipFile(export_file_path, 'r') as zipf:
            files = zipf.namelist()
            
            # Check required files
            assert "manifest.json" in files
            assert "project.json" in files
            assert "tasks.json" in files
            
            # Verify manifest content
            manifest_content = json.loads(zipf.read("manifest.json"))
            assert "format_version" in manifest_content
            assert "export_timestamp" in manifest_content
            assert "project_id" in manifest_content
            assert "data_integrity" in manifest_content
            
            # Verify project content
            project_content = json.loads(zipf.read("project.json"))
            assert project_content["id"] == "test-project-123"
            assert project_content["title"] == "Integration Test Project"
            
            # Verify tasks content
            tasks_content = json.loads(zipf.read("tasks.json"))
            assert len(tasks_content["tasks"]) == 2
            assert tasks_content["tasks"][0]["title"] == "Test Task 1"


class TestBackupIntegration:
    """Integration tests for backup system"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = LocalBackupStorage(self.temp_dir)
        self.mock_supabase = MagicMock()
        self.backup_manager = BackupManager(
            storage_backend=self.storage,
            supabase_client=self.mock_supabase
        )

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_backup_creation_and_restoration(self):
        """Test complete backup and restoration cycle"""
        # Mock export service for backup creation
        with patch.object(self.backup_manager, 'export_service') as mock_export:
            mock_export.export_project.return_value = (True, {
                "file_path": self._create_test_export_file(),
                "export_id": "test-export-123"
            })
            
            # Create backup
            success, backup_result = await self.backup_manager.create_project_backup(
                project_id="test-project-123",
                backup_type="full",
                created_by="integration_test"
            )
            
            assert success is True
            assert "backup_id" in backup_result
            
            backup_id = backup_result["backup_id"]
            
            # Verify backup exists in storage
            backups = await self.storage.list_backups()
            assert len(backups) == 1
            assert backups[0]["backup_id"] == backup_id
            
            # Mock import service for restoration
            with patch('src.server.services.backup.backup_manager.ProjectImportService') as mock_import_class:
                mock_import_service = AsyncMock()
                mock_import_class.return_value = mock_import_service
                mock_import_service.import_project.return_value = (True, {
                    "project_id": "restored-project-789",
                    "import_summary": {"tasks_imported": 5}
                })
                
                # Restore backup
                success, restore_result = await self.backup_manager.restore_project_backup(
                    backup_id=backup_id,
                    restored_by="integration_test"
                )
                
                assert success is True
                assert restore_result["restored_project_id"] == "restored-project-789"

    def _create_test_export_file(self) -> str:
        """Create a test export file"""
        export_file = os.path.join(self.temp_dir, "test_export.zip")
        
        with zipfile.ZipFile(export_file, 'w') as zipf:
            # Create manifest
            manifest = {
                "format_version": "1.0.0",
                "export_timestamp": datetime.now().isoformat(),
                "project_id": "test-project-123"
            }
            zipf.writestr("manifest.json", json.dumps(manifest))
            
            # Create project data
            project_data = {"id": "test-project-123", "title": "Test Project"}
            zipf.writestr("project.json", json.dumps(project_data))
            
            # Create tasks data
            tasks_data = {"tasks": [], "statistics": {}}
            zipf.writestr("tasks.json", json.dumps(tasks_data))
        
        return export_file
