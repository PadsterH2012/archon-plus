"""
Tests for Project Export Service

This module tests the project export functionality including:
- Full project export with all data
- Selective export options
- Data integrity verification
- Export format validation
"""

import json
import os
import tempfile
import zipfile
from unittest.mock import MagicMock, patch

import pytest

from src.server.services.projects.export_service import ProjectExportService


class TestProjectExportService:
    """Test cases for ProjectExportService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.export_service = ProjectExportService(self.mock_supabase)

    def test_init(self):
        """Test service initialization"""
        assert self.export_service.supabase_client == self.mock_supabase

    def test_get_project_data_success(self):
        """Test successful project data retrieval"""
        # Mock project data
        mock_project = {
            "id": "test-project-id",
            "title": "Test Project",
            "description": "Test Description",
            "created_at": "2025-08-18T10:00:00Z",
            "updated_at": "2025-08-18T20:00:00Z",
            "docs": [],
            "features": [],
            "data": []
        }
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_project]
        
        result = self.export_service._get_project_data("test-project-id")
        
        assert result == mock_project
        self.mock_supabase.table.assert_called_with("archon_projects")

    def test_get_project_data_not_found(self):
        """Test project data retrieval when project not found"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        result = self.export_service._get_project_data("nonexistent-id")
        
        assert result is None

    def test_get_tasks_data_success(self):
        """Test successful tasks data retrieval"""
        mock_tasks = [
            {
                "id": "task-1",
                "project_id": "test-project-id",
                "title": "Test Task",
                "status": "completed",
                "task_order": 1
            }
        ]
        
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = mock_tasks
        
        result = self.export_service._get_tasks_data("test-project-id")
        
        assert result == mock_tasks
        self.mock_supabase.table.assert_called_with("archon_tasks")

    def test_prepare_project_data(self):
        """Test project data preparation for export"""
        input_data = {
            "id": "test-id",
            "title": "Test Project",
            "description": "Test Description",
            "github_repo": "https://github.com/test/repo",
            "pinned": True,
            "created_at": "2025-08-18T10:00:00Z",
            "updated_at": "2025-08-18T20:00:00Z",
            "prd": {"goal": "Test goal"},
            "features": [{"name": "feature1"}],
            "data": [{"type": "config"}]
        }
        
        result = self.export_service._prepare_project_data(input_data)
        
        assert result["id"] == "test-id"
        assert result["title"] == "Test Project"
        assert result["metadata"]["status"] == "active"
        assert result["prd"] == {"goal": "Test goal"}

    def test_prepare_tasks_data_with_hierarchy(self):
        """Test tasks data preparation with hierarchy"""
        tasks_data = [
            {
                "id": "task-1",
                "parent_task_id": None,
                "status": "done",
                "archived": False
            },
            {
                "id": "task-2",
                "parent_task_id": "task-1",
                "status": "doing",
                "archived": False
            },
            {
                "id": "task-3",
                "parent_task_id": None,
                "status": "todo",
                "archived": True
            }
        ]
        
        result = self.export_service._prepare_tasks_data(tasks_data)
        
        assert result["statistics"]["total_tasks"] == 3
        assert result["statistics"]["completed_tasks"] == 1
        assert result["statistics"]["in_progress_tasks"] == 1
        assert result["statistics"]["todo_tasks"] == 1
        assert result["statistics"]["archived_tasks"] == 1
        
        assert "task-1" in result["task_hierarchy"]["root_tasks"]
        assert "task-3" in result["task_hierarchy"]["root_tasks"]
        assert result["task_hierarchy"]["parent_child_map"]["task-1"] == ["task-2"]

    def test_prepare_documents_data(self):
        """Test documents data preparation"""
        documents_data = [
            {
                "id": "doc-1",
                "document_type": "prp",
                "title": "Test Document",
                "status": "approved",
                "version": "1.0",
                "author": "test-author",
                "created_at": "2025-08-18T10:00:00Z",
                "updated_at": "2025-08-18T20:00:00Z",
                "content": {"goal": "Test goal"},
                "tags": ["test"]
            }
        ]
        
        result = self.export_service._prepare_documents_data(documents_data)
        
        assert result["total_documents"] == 1
        assert result["documents"][0]["id"] == "doc-1"
        assert result["documents"][0]["content"] == {"goal": "Test goal"}
        assert "size_bytes" in result["documents"][0]

    def test_prepare_versions_data(self):
        """Test version history data preparation"""
        versions_data = [
            {
                "id": "version-1",
                "created_at": "2025-08-18T10:00:00Z",
                "field_name": "docs"
            },
            {
                "id": "version-2",
                "created_at": "2025-08-18T20:00:00Z",
                "field_name": "features"
            }
        ]
        
        result = self.export_service._prepare_versions_data(versions_data)
        
        assert result["total_versions"] == 2
        assert result["version_summary"]["earliest_version"] == "2025-08-18T10:00:00Z"
        assert result["version_summary"]["latest_version"] == "2025-08-18T20:00:00Z"
        assert "docs" in result["version_summary"]["field_types"]
        assert "features" in result["version_summary"]["field_types"]

    def test_prepare_sources_data(self):
        """Test knowledge sources data preparation"""
        sources_data = [
            {
                "id": "source-1",
                "linked_at": "2025-08-18T10:00:00Z",
                "created_by": "user1"
            },
            {
                "id": "source-2",
                "linked_at": "2025-08-18T20:00:00Z",
                "created_by": "user2"
            }
        ]
        
        result = self.export_service._prepare_sources_data(sources_data)
        
        assert result["total_sources"] == 2
        assert result["source_summary"]["linked_at_range"]["earliest"] == "2025-08-18T10:00:00Z"
        assert result["source_summary"]["linked_at_range"]["latest"] == "2025-08-18T20:00:00Z"
        assert "user1" in result["source_summary"]["created_by"]
        assert "user2" in result["source_summary"]["created_by"]

    def test_generate_checksums(self):
        """Test checksum generation for data integrity"""
        export_data = {
            "project": {"id": "test-id", "title": "Test"},
            "tasks": {"tasks": [], "statistics": {}}
        }
        
        result = self.export_service._generate_checksums(export_data)
        
        assert "project.json" in result
        assert "tasks.json" in result
        assert len(result["project.json"]) == 64  # SHA-256 hex length
        assert len(result["tasks.json"]) == 64

    def test_create_export_manifest(self):
        """Test export manifest creation"""
        manifest = self.export_service._create_export_manifest(
            project_id="test-id",
            project_title="Test Project",
            export_type="full",
            include_versions=True,
            include_sources=True,
            include_attachments=False,
            version_limit=10,
            date_range=("2025-01-01", "2025-12-31"),
            exported_by="test-user"
        )
        
        assert manifest["format_version"] == "1.0.0"
        assert manifest["project_id"] == "test-id"
        assert manifest["project_title"] == "Test Project"
        assert manifest["export_type"] == "full"
        assert manifest["exported_by"] == "test-user"
        assert manifest["export_options"]["include_versions"] is True
        assert manifest["export_options"]["version_limit"] == 10

    @patch('tempfile.TemporaryDirectory')
    @patch('zipfile.ZipFile')
    @patch('os.makedirs')
    @patch('builtins.open')
    @patch('json.dump')
    @patch('os.path.getsize')
    @patch('os.rename')
    def test_create_export_package_success(self, mock_rename, mock_getsize, mock_json_dump, 
                                         mock_open, mock_makedirs, mock_zipfile, mock_tempdir):
        """Test successful export package creation"""
        # Mock temporary directory
        mock_tempdir.return_value.__enter__.return_value = "/tmp/test"
        mock_getsize.return_value = 1024
        
        manifest = {"format_version": "1.0.0"}
        export_data = {
            "project": {"id": "test"},
            "tasks": {"tasks": []},
            "documents": {"documents": []},
            "versions": {"versions": []},
            "sources": {"sources": []}
        }
        
        result = self.export_service._create_export_package(manifest, export_data, "test-id")
        
        assert result["success"] is True
        assert "export_id" in result
        assert "file_path" in result
        assert result["file_size"] == 1024

    def test_list_exports_placeholder(self):
        """Test export listing (placeholder implementation)"""
        success, result = self.export_service.list_exports()
        
        assert success is True
        assert result["exports"] == []
        assert "placeholder" in result["message"]

    def test_get_export_status_placeholder(self):
        """Test export status retrieval (placeholder implementation)"""
        success, result = self.export_service.get_export_status("test-export-id")
        
        assert success is True
        assert result["export_id"] == "test-export-id"
        assert result["status"] == "completed"
        assert "placeholder" in result["message"]

    @patch.object(ProjectExportService, '_get_project_data')
    def test_export_project_not_found(self, mock_get_project):
        """Test export when project is not found"""
        mock_get_project.return_value = None
        
        success, result = self.export_service.export_project("nonexistent-id")
        
        assert success is False
        assert "not found" in result["error"]

    @patch.object(ProjectExportService, '_get_project_data')
    @patch.object(ProjectExportService, '_get_tasks_data')
    @patch.object(ProjectExportService, '_get_documents_data')
    @patch.object(ProjectExportService, '_get_versions_data')
    @patch.object(ProjectExportService, '_get_sources_data')
    @patch.object(ProjectExportService, '_create_export_package')
    def test_export_project_success(self, mock_create_package, mock_get_sources, 
                                  mock_get_versions, mock_get_docs, mock_get_tasks, mock_get_project):
        """Test successful project export"""
        # Mock all data retrieval methods
        mock_get_project.return_value = {"id": "test-id", "title": "Test Project", "docs": []}
        mock_get_tasks.return_value = []
        mock_get_docs.return_value = []
        mock_get_versions.return_value = []
        mock_get_sources.return_value = []
        mock_create_package.return_value = {
            "success": True,
            "export_id": "export-123",
            "file_path": "/tmp/export.zip",
            "file_size": 1024
        }
        
        success, result = self.export_service.export_project("test-id")
        
        assert success is True
        assert result["export_id"] == "export-123"
        assert result["file_path"] == "/tmp/export.zip"
        assert "successfully" in result["message"]
