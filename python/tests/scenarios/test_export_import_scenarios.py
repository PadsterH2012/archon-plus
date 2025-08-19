"""
End-to-End Scenario Tests for Export/Import System

This module provides real-world scenario testing including:
- Project migration scenarios
- Backup and recovery workflows
- Multi-environment deployment scenarios
- Error recovery and edge cases
"""

import asyncio
import json
import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.server.services.backup.backup_manager import BackupManager, LocalBackupStorage
from src.server.services.backup.backup_scheduler import BackupScheduler
from src.server.services.projects.export_service import ProjectExportService
from src.server.services.projects.import_service import ProjectImportService


class TestExportImportScenarios:
    """End-to-end scenario tests"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create services
        self.export_service = ProjectExportService(self.mock_supabase)
        self.import_service = ProjectImportService(self.mock_supabase)
        
        # Create backup services
        self.storage = LocalBackupStorage(self.temp_dir)
        self.backup_manager = BackupManager(
            storage_backend=self.storage,
            supabase_client=self.mock_supabase
        )
        self.backup_scheduler = BackupScheduler(self.mock_supabase)

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.scenario
    @pytest.mark.asyncio
    async def test_project_migration_scenario(self):
        """
        Scenario: Migrate a project from development to production environment
        
        Steps:
        1. Export project from development environment
        2. Transfer export file to production environment
        3. Import project into production environment
        4. Verify project functionality in production
        """
        # Step 1: Export from development
        dev_project_data = self._create_development_project_data()
        self._mock_database_responses(dev_project_data["project"], dev_project_data["tasks"])
        
        success, export_result = self.export_service.export_project(
            project_id="dev-project-123",
            export_type="full",
            exported_by="dev_admin"
        )
        
        assert success is True
        export_file = export_result["file_path"]
        
        # Step 2: Simulate file transfer (file already exists)
        assert os.path.exists(export_file)
        
        # Step 3: Import into production
        self._mock_production_import_responses()
        
        success, import_result = self.import_service.import_project(
            import_file_path=export_file,
            import_type="full",
            imported_by="prod_admin"
        )
        
        assert success is True
        assert "project_id" in import_result
        
        # Step 4: Verify production deployment
        prod_project_id = import_result["project_id"]
        assert prod_project_id is not None
        
        summary = import_result["import_summary"]
        assert summary["project_created"] is True
        assert summary["tasks_imported"] == 5
        assert summary["documents_imported"] == 3

    @pytest.mark.scenario
    @pytest.mark.asyncio
    async def test_disaster_recovery_scenario(self):
        """
        Scenario: Recover from data loss using automated backups
        
        Steps:
        1. Create automated backup schedule
        2. Simulate backup creation
        3. Simulate data loss
        4. Restore from backup
        5. Verify data recovery
        """
        # Step 1: Create backup schedule
        success, schedule_result = await self.backup_scheduler.create_schedule(
            project_id="critical-project-456",
            schedule_type="cron",
            cron_expression="0 2 * * *",  # Daily at 2 AM
            backup_type="full",
            enabled=True
        )
        
        assert success is True
        schedule_id = schedule_result["schedule_id"]
        
        # Step 2: Simulate backup creation
        project_data = self._create_critical_project_data()
        
        with patch.object(self.backup_manager, 'export_service') as mock_export:
            mock_export.export_project.return_value = (True, {
                "file_path": self._create_test_backup_file(),
                "export_id": "backup-export-789"
            })
            
            success, backup_result = await self.backup_manager.create_project_backup(
                project_id="critical-project-456",
                backup_type="full",
                created_by="backup_scheduler"
            )
            
            assert success is True
            backup_id = backup_result["backup_id"]
        
        # Step 3: Simulate data loss (no action needed for test)
        
        # Step 4: Restore from backup
        with patch('src.server.services.backup.backup_manager.ProjectImportService') as mock_import_class:
            mock_import_service = AsyncMock()
            mock_import_class.return_value = mock_import_service
            mock_import_service.import_project.return_value = (True, {
                "project_id": "recovered-project-789",
                "import_summary": {
                    "project_created": True,
                    "tasks_imported": 10,
                    "documents_imported": 5
                }
            })
            
            success, restore_result = await self.backup_manager.restore_project_backup(
                backup_id=backup_id,
                restored_by="disaster_recovery"
            )
            
            assert success is True
            
            # Step 5: Verify recovery
            assert restore_result["restored_project_id"] == "recovered-project-789"
            assert restore_result["import_summary"]["tasks_imported"] == 10

    @pytest.mark.scenario
    @pytest.mark.asyncio
    async def test_team_collaboration_scenario(self):
        """
        Scenario: Team member shares project with another team
        
        Steps:
        1. Team A exports their project
        2. Team A shares export file with Team B
        3. Team B imports project into their environment
        4. Team B makes modifications
        5. Team B exports modified project
        6. Verify changes are preserved
        """
        # Step 1: Team A exports project
        team_a_project = self._create_team_project_data("Team A Project")
        self._mock_database_responses(team_a_project["project"], team_a_project["tasks"])
        
        success, export_result = self.export_service.export_project(
            project_id="team-a-project",
            export_type="full",
            exported_by="team_a_lead"
        )
        
        assert success is True
        shared_file = export_result["file_path"]
        
        # Step 2: File sharing (simulated by file existence)
        assert os.path.exists(shared_file)
        
        # Step 3: Team B imports project
        self._mock_team_b_import_responses()
        
        success, import_result = self.import_service.import_project(
            import_file_path=shared_file,
            import_type="full",
            imported_by="team_b_lead"
        )
        
        assert success is True
        team_b_project_id = import_result["project_id"]
        
        # Step 4: Team B makes modifications (simulated)
        modified_project = self._create_modified_team_project_data(team_b_project_id)
        self._mock_database_responses(modified_project["project"], modified_project["tasks"])
        
        # Step 5: Team B exports modified project
        success, modified_export = self.export_service.export_project(
            project_id=team_b_project_id,
            export_type="full",
            exported_by="team_b_lead"
        )
        
        assert success is True
        
        # Step 6: Verify modifications are preserved
        exported_data = self._extract_export_data(modified_export["file_path"])
        assert "Team B Modifications" in exported_data["project"]["title"]
        assert len(exported_data["tasks"]["tasks"]) == 4  # Original 3 + 1 new

    @pytest.mark.scenario
    @pytest.mark.asyncio
    async def test_incremental_backup_scenario(self):
        """
        Scenario: Incremental backup strategy for large projects
        
        Steps:
        1. Create full backup
        2. Make changes to project
        3. Create incremental backup
        4. Simulate data loss
        5. Restore using incremental backup chain
        """
        # Step 1: Create full backup
        large_project = self._create_large_project_data()
        
        with patch.object(self.backup_manager, 'export_service') as mock_export:
            mock_export.export_project.return_value = (True, {
                "file_path": self._create_test_backup_file("full"),
                "export_id": "full-backup-001"
            })
            
            success, full_backup = await self.backup_manager.create_project_backup(
                project_id="large-project-789",
                backup_type="full",
                created_by="backup_system"
            )
            
            assert success is True
            full_backup_id = full_backup["backup_id"]
        
        # Step 2: Simulate project changes
        # (In real scenario, project would be modified)
        
        # Step 3: Create incremental backup
        with patch.object(self.backup_manager, 'export_service') as mock_export:
            mock_export.export_project.return_value = (True, {
                "file_path": self._create_test_backup_file("incremental"),
                "export_id": "incremental-backup-001"
            })
            
            success, incremental_backup = await self.backup_manager.create_project_backup(
                project_id="large-project-789",
                backup_type="incremental",
                created_by="backup_system"
            )
            
            assert success is True
            incremental_backup_id = incremental_backup["backup_id"]
        
        # Step 4: Simulate data loss
        # Step 5: Restore using incremental backup
        with patch('src.server.services.backup.backup_manager.ProjectImportService') as mock_import_class:
            mock_import_service = AsyncMock()
            mock_import_class.return_value = mock_import_service
            mock_import_service.import_project.return_value = (True, {
                "project_id": "restored-large-project",
                "import_summary": {"tasks_imported": 1000}
            })
            
            success, restore_result = await self.backup_manager.restore_project_backup(
                backup_id=incremental_backup_id,
                restored_by="recovery_system"
            )
            
            assert success is True
            assert restore_result["import_summary"]["tasks_imported"] == 1000

    @pytest.mark.scenario
    @pytest.mark.asyncio
    async def test_multi_project_export_scenario(self):
        """
        Scenario: Export multiple related projects for environment setup
        
        Steps:
        1. Export multiple related projects
        2. Package them together
        3. Import all projects into new environment
        4. Verify project relationships are maintained
        """
        # Step 1: Export multiple projects
        projects = ["frontend-project", "backend-project", "shared-lib-project"]
        export_files = []
        
        for project_id in projects:
            project_data = self._create_related_project_data(project_id)
            self._mock_database_responses(project_data["project"], project_data["tasks"])
            
            success, export_result = self.export_service.export_project(
                project_id=project_id,
                export_type="full",
                exported_by="devops_team"
            )
            
            assert success is True
            export_files.append(export_result["file_path"])
        
        # Step 2: Package exports (simulated by having multiple files)
        assert len(export_files) == 3
        
        # Step 3: Import all projects
        imported_projects = []
        for i, export_file in enumerate(export_files):
            self._mock_multi_project_import_responses(i)
            
            success, import_result = self.import_service.import_project(
                import_file_path=export_file,
                import_type="full",
                imported_by="new_env_setup"
            )
            
            assert success is True
            imported_projects.append(import_result["project_id"])
        
        # Step 4: Verify all projects imported
        assert len(imported_projects) == 3
        assert all(project_id is not None for project_id in imported_projects)

    @pytest.mark.scenario
    def test_error_recovery_scenario(self):
        """
        Scenario: Handle various error conditions gracefully
        
        Steps:
        1. Attempt export with invalid project ID
        2. Attempt import with corrupted file
        3. Attempt import with incompatible format
        4. Verify appropriate error handling
        """
        # Step 1: Invalid project ID
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        success, result = self.export_service.export_project(
            project_id="nonexistent-project",
            export_type="full",
            exported_by="error_test"
        )
        
        assert success is False
        assert "not found" in result["error"].lower()
        
        # Step 2: Corrupted file
        corrupted_file = self._create_corrupted_file()
        
        is_valid, validation_result = self.import_service.validate_import_file(corrupted_file)
        
        assert is_valid is False
        assert "error" in validation_result
        
        # Step 3: Incompatible format
        incompatible_file = self._create_incompatible_format_file()
        
        is_valid, validation_result = self.import_service.validate_import_file(incompatible_file)
        
        assert is_valid is False
        assert "error" in validation_result

    def _create_development_project_data(self):
        """Create development environment project data"""
        project = {
            "id": "dev-project-123",
            "title": "Development Project",
            "description": "Project in development environment",
            "docs": [
                {"id": "dev-doc-1", "title": "Dev Doc 1", "content": {"text": "Dev content 1"}},
                {"id": "dev-doc-2", "title": "Dev Doc 2", "content": {"text": "Dev content 2"}},
                {"id": "dev-doc-3", "title": "Dev Doc 3", "content": {"text": "Dev content 3"}}
            ]
        }
        
        tasks = [
            {"id": f"dev-task-{i}", "project_id": "dev-project-123", "title": f"Dev Task {i}", "status": "todo"}
            for i in range(1, 6)
        ]
        
        return {"project": project, "tasks": tasks}

    def _create_critical_project_data(self):
        """Create critical project data for disaster recovery"""
        return {
            "id": "critical-project-456",
            "title": "Critical Production Project",
            "description": "Mission-critical project requiring backup",
            "docs": [
                {"id": f"critical-doc-{i}", "title": f"Critical Doc {i}", "content": {"text": f"Critical content {i}"}}
                for i in range(1, 6)
            ]
        }

    def _create_team_project_data(self, title_prefix: str):
        """Create team project data"""
        project = {
            "id": "team-a-project",
            "title": title_prefix,
            "description": "Collaborative team project",
            "docs": [
                {"id": "team-doc-1", "title": "Team Doc 1", "content": {"text": "Team content 1"}},
                {"id": "team-doc-2", "title": "Team Doc 2", "content": {"text": "Team content 2"}}
            ]
        }
        
        tasks = [
            {"id": f"team-task-{i}", "project_id": "team-a-project", "title": f"Team Task {i}", "status": "todo"}
            for i in range(1, 4)
        ]
        
        return {"project": project, "tasks": tasks}

    def _create_modified_team_project_data(self, project_id: str):
        """Create modified team project data"""
        project = {
            "id": project_id,
            "title": "Team A Project - Team B Modifications",
            "description": "Project modified by Team B",
            "docs": [
                {"id": "team-doc-1", "title": "Team Doc 1 - Modified", "content": {"text": "Modified content 1"}},
                {"id": "team-doc-2", "title": "Team Doc 2", "content": {"text": "Team content 2"}}
            ]
        }
        
        tasks = [
            {"id": f"team-task-{i}", "project_id": project_id, "title": f"Team Task {i}", "status": "done"}
            for i in range(1, 4)
        ] + [
            {"id": "new-team-task", "project_id": project_id, "title": "New Task by Team B", "status": "todo"}
        ]
        
        return {"project": project, "tasks": tasks}

    def _create_large_project_data(self):
        """Create large project data for incremental backup testing"""
        return {
            "id": "large-project-789",
            "title": "Large Project for Incremental Backup",
            "description": "Large project with many tasks and documents"
        }

    def _create_related_project_data(self, project_id: str):
        """Create related project data for multi-project scenario"""
        project = {
            "id": project_id,
            "title": f"Related Project: {project_id}",
            "description": f"Part of multi-project setup: {project_id}"
        }
        
        tasks = [
            {"id": f"{project_id}-task-{i}", "project_id": project_id, "title": f"Task {i}", "status": "todo"}
            for i in range(1, 4)
        ]
        
        return {"project": project, "tasks": tasks}

    def _mock_database_responses(self, project_data, tasks_data):
        """Mock database responses"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [project_data]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = tasks_data

    def _mock_production_import_responses(self):
        """Mock production import responses"""
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "prod-project-456"}
        ]

    def _mock_team_b_import_responses(self):
        """Mock Team B import responses"""
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "team-b-project-789"}
        ]

    def _mock_multi_project_import_responses(self, index: int):
        """Mock multi-project import responses"""
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": f"imported-project-{index}"}
        ]

    def _create_test_backup_file(self, backup_type: str = "full") -> str:
        """Create test backup file"""
        backup_file = os.path.join(self.temp_dir, f"{backup_type}_backup.zip")
        
        with zipfile.ZipFile(backup_file, 'w') as zipf:
            manifest = {
                "format_version": "1.0.0",
                "export_timestamp": datetime.now().isoformat(),
                "project_id": "test-project",
                "backup_type": backup_type
            }
            zipf.writestr("manifest.json", json.dumps(manifest))
            
            project_data = {"id": "test-project", "title": f"Test {backup_type} backup"}
            zipf.writestr("project.json", json.dumps(project_data))
            
            tasks_data = {"tasks": [], "statistics": {}}
            zipf.writestr("tasks.json", json.dumps(tasks_data))
        
        return backup_file

    def _extract_export_data(self, export_file: str):
        """Extract data from export file"""
        with zipfile.ZipFile(export_file, 'r') as zipf:
            project = json.loads(zipf.read("project.json").decode('utf-8'))
            tasks = json.loads(zipf.read("tasks.json").decode('utf-8'))
            
            return {"project": project, "tasks": tasks}

    def _create_corrupted_file(self) -> str:
        """Create corrupted file for error testing"""
        corrupted_file = os.path.join(self.temp_dir, "corrupted.zip")
        with open(corrupted_file, 'wb') as f:
            f.write(b"This is not a valid ZIP file")
        return corrupted_file

    def _create_incompatible_format_file(self) -> str:
        """Create incompatible format file"""
        incompatible_file = os.path.join(self.temp_dir, "incompatible.zip")
        
        with zipfile.ZipFile(incompatible_file, 'w') as zipf:
            # Create file with wrong format version
            manifest = {
                "format_version": "999.0.0",  # Incompatible version
                "export_timestamp": datetime.now().isoformat()
            }
            zipf.writestr("manifest.json", json.dumps(manifest))
        
        return incompatible_file
