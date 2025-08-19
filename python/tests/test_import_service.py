"""
Tests for Project Import Service

This module tests the project import functionality including:
- Import file validation
- Data integrity verification
- Conflict detection and resolution
- Full and selective imports
- Rollback capabilities
"""

import json
import os
import tempfile
import zipfile
from unittest.mock import MagicMock, patch

import pytest

from src.server.services.projects.import_service import (
    ProjectImportService,
    ImportValidationError,
    ImportConflictError
)


class TestProjectImportService:
    """Test cases for ProjectImportService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.import_service = ProjectImportService(self.mock_supabase)

    def test_init(self):
        """Test service initialization"""
        assert self.import_service.supabase_client == self.mock_supabase

    def create_test_export_file(self, temp_dir: str, valid: bool = True) -> str:
        """Create a test export file for testing"""
        export_file = os.path.join(temp_dir, "test_export.zip")
        
        with zipfile.ZipFile(export_file, 'w') as zipf:
            if valid:
                # Create valid manifest
                manifest = {
                    "format_version": "1.0.0",
                    "archon_version": "2.0.0",
                    "export_timestamp": "2025-08-18T22:00:00Z",
                    "project_id": "test-project-id",
                    "project_title": "Test Project",
                    "compatibility": {"min_archon_version": "2.0.0"},
                    "data_integrity": {"checksums": {}}
                }
                zipf.writestr("manifest.json", json.dumps(manifest))
                
                # Create project data
                project_data = {
                    "id": "test-project-id",
                    "title": "Test Project",
                    "description": "Test Description"
                }
                zipf.writestr("project.json", json.dumps(project_data))
                
                # Create tasks data
                tasks_data = {"tasks": [], "statistics": {}}
                zipf.writestr("tasks.json", json.dumps(tasks_data))
            else:
                # Create invalid file
                zipf.writestr("invalid.txt", "not a valid export")
        
        return export_file

    def test_validate_export_package_valid(self):
        """Test validation of valid export package"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir, valid=True)
            
            result = self.import_service._validate_export_package(export_file)
            
            assert result["valid"] is True
            assert "manifest" in result

    def test_validate_export_package_invalid_zip(self):
        """Test validation of invalid ZIP file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_file = os.path.join(temp_dir, "invalid.txt")
            with open(invalid_file, 'w') as f:
                f.write("not a zip file")
            
            result = self.import_service._validate_export_package(invalid_file)
            
            assert result["valid"] is False
            assert "not a valid ZIP archive" in result["error"]

    def test_validate_export_package_missing_files(self):
        """Test validation when required files are missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir, valid=False)
            
            result = self.import_service._validate_export_package(export_file)
            
            assert result["valid"] is False
            assert "Missing required files" in result["error"]

    def test_extract_package_data_success(self):
        """Test successful package data extraction"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir, valid=True)
            
            result = self.import_service._extract_package_data(export_file)
            
            assert result is not None
            assert "manifest" in result
            assert "project" in result
            assert "tasks" in result

    def test_validate_data_integrity_no_checksums(self):
        """Test data integrity validation when no checksums are present"""
        package_data = {
            "manifest": {"data_integrity": {"checksums": {}}},
            "project": {"id": "test"},
            "tasks": {"tasks": []}
        }
        
        result = self.import_service._validate_data_integrity(package_data)
        
        assert result["valid"] is True
        assert "warning" in result

    def test_get_existing_project_success(self):
        """Test successful existing project retrieval"""
        mock_project = {"id": "test-id", "title": "Existing Project"}
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_project]
        
        result = self.import_service._get_existing_project("test-id")
        
        assert result == mock_project

    def test_get_existing_project_not_found(self):
        """Test existing project retrieval when project not found"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        result = self.import_service._get_existing_project("nonexistent-id")
        
        assert result is None

    def test_find_task_conflicts_exact_title_match(self):
        """Test task conflict detection with exact title match"""
        existing_tasks = [
            {"id": "existing-1", "title": "Duplicate Task", "description": "Existing task"}
        ]
        import_tasks = [
            {"title": "Duplicate Task", "description": "Import task"}
        ]
        
        conflicts = self.import_service._find_task_conflicts(existing_tasks, import_tasks)
        
        assert len(conflicts) == 1
        assert conflicts[0]["type"] == "task_title_duplicate"
        assert conflicts[0]["severity"] == "error"

    def test_find_task_conflicts_similarity(self):
        """Test task conflict detection with content similarity"""
        existing_tasks = [
            {"id": "existing-1", "title": "Similar Task", "description": "OAuth implementation"}
        ]
        import_tasks = [
            {"title": "OAuth Task", "description": "OAuth implementation details"}
        ]
        
        conflicts = self.import_service._find_task_conflicts(existing_tasks, import_tasks)
        
        assert len(conflicts) == 1
        assert conflicts[0]["type"] == "task_similarity"
        assert conflicts[0]["severity"] == "warning"

    def test_create_import_plan_full_import(self):
        """Test import plan creation for full import"""
        package_data = {
            "project": {"id": "test"},
            "tasks": {"tasks": [{"title": "Task 1"}, {"title": "Task 2"}]},
            "documents": {"documents": []}
        }
        
        plan = self.import_service._create_import_plan(
            package_data=package_data,
            import_type="full",
            target_project_id=None,
            selective_components=None,
            conflict_resolution="merge",
            conflict_analysis=None
        )
        
        assert plan["import_type"] == "full"
        assert plan["create_new_project"] is True
        assert "project" in plan["components_to_import"]
        assert "tasks" in plan["components_to_import"]
        assert plan["estimated_operations"] == 3  # 1 project + 2 tasks

    def test_create_import_plan_selective_import(self):
        """Test import plan creation for selective import"""
        package_data = {
            "project": {"id": "test"},
            "tasks": {"tasks": [{"title": "Task 1"}]},
            "documents": {"documents": []}
        }
        
        plan = self.import_service._create_import_plan(
            package_data=package_data,
            import_type="selective",
            target_project_id="existing-id",
            selective_components=["tasks"],
            conflict_resolution="merge",
            conflict_analysis=None
        )
        
        assert plan["import_type"] == "selective"
        assert plan["create_new_project"] is False
        assert plan["components_to_import"] == ["tasks"]

    def test_determine_conflict_resolution_strategies(self):
        """Test different conflict resolution strategies"""
        conflict = {"type": "task_title_duplicate", "severity": "error"}
        
        # Test different strategies
        assert self.import_service._determine_conflict_resolution(conflict, "fail") == "fail"
        assert self.import_service._determine_conflict_resolution(conflict, "skip") == "skip_import_item"
        assert self.import_service._determine_conflict_resolution(conflict, "overwrite") == "overwrite_existing"
        assert self.import_service._determine_conflict_resolution(conflict, "merge") == "rename_import_item"

    def test_resolve_task_conflicts_rename(self):
        """Test task conflict resolution with renaming"""
        task = {"title": "Duplicate Task", "description": "Test task"}
        import_plan = {
            "conflict_resolutions": [
                {
                    "conflict": {"import_task_title": "Duplicate Task", "type": "task_title_duplicate"},
                    "action": "rename_import_item"
                }
            ]
        }
        
        should_import, modified_task = self.import_service._resolve_task_conflicts(task, import_plan)
        
        assert should_import is True
        assert modified_task["title"] == "Duplicate Task (Imported)"

    def test_resolve_task_conflicts_skip(self):
        """Test task conflict resolution with skipping"""
        task = {"title": "Skip Task", "description": "Test task"}
        import_plan = {
            "conflict_resolutions": [
                {
                    "conflict": {"import_task_title": "Skip Task", "type": "task_title_duplicate"},
                    "action": "skip_import_item"
                }
            ]
        }
        
        should_import, modified_task = self.import_service._resolve_task_conflicts(task, import_plan)
        
        assert should_import is False

    def test_merge_arrays(self):
        """Test array merging functionality"""
        existing = [{"name": "item1"}, {"name": "item2"}]
        importing = [{"name": "item2"}, {"name": "item3"}]
        
        merged = self.import_service._merge_arrays(existing, importing)
        
        assert len(merged) == 3
        assert {"name": "item1"} in merged
        assert {"name": "item2"} in merged
        assert {"name": "item3"} in merged

    def test_validate_import_file_success(self):
        """Test successful import file validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir, valid=True)
            
            is_valid, result = self.import_service.validate_import_file(export_file)
            
            assert is_valid is True
            assert result["valid"] is True
            assert result["project_title"] == "Test Project"
            assert result["project_id"] == "test-project-id"

    def test_validate_import_file_invalid(self):
        """Test import file validation with invalid file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir, valid=False)
            
            is_valid, result = self.import_service.validate_import_file(export_file)
            
            assert is_valid is False
            assert "error" in result

    @patch.object(ProjectImportService, '_validate_export_package')
    @patch.object(ProjectImportService, '_extract_package_data')
    @patch.object(ProjectImportService, '_validate_data_integrity')
    def test_import_project_dry_run(self, mock_integrity, mock_extract, mock_validate):
        """Test dry run import"""
        # Mock successful validation
        mock_validate.return_value = {"valid": True}
        mock_extract.return_value = {"manifest": {}, "project": {"title": "Test"}, "tasks": {"tasks": []}}
        mock_integrity.return_value = {"valid": True}
        
        success, result = self.import_service.import_project(
            import_file_path="/fake/path.zip",
            dry_run=True
        )
        
        assert success is True
        assert result["dry_run"] is True
        assert "import_plan" in result

    def test_import_project_file_not_found(self):
        """Test import when file doesn't exist"""
        success, result = self.import_service.import_project("/nonexistent/file.zip")
        
        assert success is False
        assert "not found" in result["error"]
