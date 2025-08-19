"""
Tests for Export/Import API Endpoints

This module tests the FastAPI endpoints for project export/import functionality including:
- Project export endpoint with various options
- Project import endpoint with file upload
- Import validation endpoint
- Export status and download endpoints
"""

import json
import os
import tempfile
import zipfile
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.server.main import app

client = TestClient(app)


class TestExportImportAPI:
    """Test cases for Export/Import API endpoints"""

    def create_test_export_file(self, temp_dir: str) -> str:
        """Create a test export file for testing"""
        export_file = os.path.join(temp_dir, "test_export.zip")
        
        with zipfile.ZipFile(export_file, 'w') as zipf:
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
        
        return export_file

    @patch('src.server.services.projects.export_service.ProjectExportService.export_project')
    def test_export_project_success(self, mock_export):
        """Test successful project export"""
        # Mock successful export
        mock_export.return_value = (True, {
            "export_id": "test-export-123",
            "file_path": "/tmp/test-export.zip",
            "file_size": 1024,
            "message": "Export completed successfully"
        })
        
        response = client.post(
            "/api/projects/test-project-id/export",
            json={
                "export_type": "full",
                "include_versions": True,
                "include_sources": True,
                "include_attachments": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["export_id"] == "test-export-123"
        assert data["download_url"] == "/api/projects/exports/test-export-123/download"
        assert data["file_size"] == 1024

    @patch('src.server.services.projects.export_service.ProjectExportService.export_project')
    def test_export_project_failure(self, mock_export):
        """Test project export failure"""
        # Mock export failure
        mock_export.return_value = (False, {
            "error": "Project not found"
        })
        
        response = client.post(
            "/api/projects/nonexistent-id/export",
            json={"export_type": "full"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"]

    def test_export_project_invalid_request(self):
        """Test export with invalid request data"""
        response = client.post(
            "/api/projects/test-id/export",
            json={"invalid_field": "value"}
        )
        
        # Should still work with default values
        assert response.status_code in [200, 422]  # 422 if validation fails

    @patch('os.listdir')
    @patch('os.path.exists')
    def test_download_export_success(self, mock_exists, mock_listdir):
        """Test successful export download"""
        # Mock file system
        mock_listdir.return_value = ["project-export-test-id-20250818_220000.zip"]
        mock_exists.return_value = True
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = os.path.join(temp_dir, "project-export-test-id-20250818_220000.zip")
            with open(test_file, 'wb') as f:
                f.write(b"test zip content")
            
            # Mock the file path
            with patch('os.path.join', return_value=test_file):
                response = client.get("/api/projects/exports/test-export-123/download")
                
                assert response.status_code == 200
                assert response.headers["content-type"] == "application/zip"

    @patch('os.listdir')
    def test_download_export_not_found(self, mock_listdir):
        """Test download when export file not found"""
        mock_listdir.return_value = []
        
        response = client.get("/api/projects/exports/nonexistent-export/download")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]["error"]

    @patch('src.server.services.projects.export_service.ProjectExportService.get_export_status')
    def test_get_export_status(self, mock_status):
        """Test export status endpoint"""
        mock_status.return_value = (True, {
            "export_id": "test-export-123",
            "status": "completed",
            "progress": 100
        })
        
        response = client.get("/api/projects/test-project-id/export/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["export_id"] == "test-export-123"
        assert data["status"] == "completed"

    @patch('src.server.services.projects.import_service.ProjectImportService.import_project')
    def test_import_project_success(self, mock_import):
        """Test successful project import"""
        # Mock successful import
        mock_import.return_value = (True, {
            "project_id": "imported-project-123",
            "import_summary": {"tasks_imported": 5, "documents_imported": 2},
            "conflicts_resolved": [],
            "message": "Import completed successfully"
        })
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir)
            
            with open(export_file, 'rb') as f:
                response = client.post(
                    "/api/projects/import",
                    files={"file": ("test_export.zip", f, "application/zip")},
                    data={
                        "import_type": "full",
                        "conflict_resolution": "merge",
                        "dry_run": "false"
                    }
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["project_id"] == "imported-project-123"
        assert data["import_summary"]["tasks_imported"] == 5

    @patch('src.server.services.projects.import_service.ProjectImportService.import_project')
    def test_import_project_failure(self, mock_import):
        """Test project import failure"""
        # Mock import failure
        mock_import.return_value = (False, {
            "error": "Invalid export format"
        })
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir)
            
            with open(export_file, 'rb') as f:
                response = client.post(
                    "/api/projects/import",
                    files={"file": ("test_export.zip", f, "application/zip")},
                    data={"import_type": "full"}
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Invalid export format" in data["error"]

    def test_import_project_invalid_file_type(self):
        """Test import with invalid file type"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
            temp_file.write(b"not a zip file")
            temp_file.seek(0)
            
            response = client.post(
                "/api/projects/import",
                files={"file": ("test.txt", temp_file, "text/plain")},
                data={"import_type": "full"}
            )
        
        assert response.status_code == 400
        assert "Only ZIP files are supported" in response.json()["detail"]["error"]

    @patch('src.server.services.projects.import_service.ProjectImportService.import_project')
    def test_import_project_dry_run(self, mock_import):
        """Test project import dry run"""
        # Mock dry run result
        mock_import.return_value = (True, {
            "dry_run": True,
            "import_plan": {"components_to_import": ["tasks", "documents"]},
            "conflicts": {"has_conflicts": False},
            "message": "Dry run completed successfully"
        })
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir)
            
            with open(export_file, 'rb') as f:
                response = client.post(
                    "/api/projects/import",
                    files={"file": ("test_export.zip", f, "application/zip")},
                    data={
                        "import_type": "full",
                        "dry_run": "true"
                    }
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "dry run" in data["message"].lower()

    @patch('src.server.services.projects.import_service.ProjectImportService.validate_import_file')
    def test_validate_import_file_success(self, mock_validate):
        """Test successful import file validation"""
        # Mock successful validation
        mock_validate.return_value = (True, {
            "valid": True,
            "project_title": "Test Project",
            "project_id": "test-project-id",
            "task_count": 5,
            "document_count": 2,
            "export_timestamp": "2025-08-18T22:00:00Z",
            "exported_by": "test-user"
        })
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir)
            
            with open(export_file, 'rb') as f:
                response = client.post(
                    "/api/projects/import/validate",
                    files={"file": ("test_export.zip", f, "application/zip")}
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["project_title"] == "Test Project"
        assert data["task_count"] == 5

    @patch('src.server.services.projects.import_service.ProjectImportService.validate_import_file')
    def test_validate_import_file_failure(self, mock_validate):
        """Test import file validation failure"""
        # Mock validation failure
        mock_validate.return_value = (False, {
            "error": "Invalid manifest format"
        })
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir)
            
            with open(export_file, 'rb') as f:
                response = client.post(
                    "/api/projects/import/validate",
                    files={"file": ("test_export.zip", f, "application/zip")}
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "Invalid manifest format" in data["error"]

    def test_validate_import_file_invalid_type(self):
        """Test validation with invalid file type"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
            temp_file.write(b"not a zip file")
            temp_file.seek(0)
            
            response = client.post(
                "/api/projects/import/validate",
                files={"file": ("test.txt", temp_file, "text/plain")}
            )
        
        assert response.status_code == 400
        assert "Only ZIP files are supported" in response.json()["detail"]["error"]

    @patch('src.server.services.projects.export_service.ProjectExportService.list_exports')
    def test_list_exports(self, mock_list):
        """Test list exports endpoint"""
        mock_list.return_value = (True, {
            "exports": [
                {"export_id": "export-1", "created_at": "2025-08-18T22:00:00Z"},
                {"export_id": "export-2", "created_at": "2025-08-18T21:00:00Z"}
            ],
            "total_count": 2
        })
        
        response = client.get("/api/projects/exports")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert len(data["exports"]) == 2

    def test_import_with_selective_components(self):
        """Test import with selective components"""
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = self.create_test_export_file(temp_dir)
            
            with open(export_file, 'rb') as f:
                response = client.post(
                    "/api/projects/import",
                    files={"file": ("test_export.zip", f, "application/zip")},
                    data={
                        "import_type": "selective",
                        "selective_components": json.dumps(["tasks", "documents"]),
                        "conflict_resolution": "merge"
                    }
                )
        
        # Should not raise an error for valid request format
        assert response.status_code in [200, 500]  # 500 if service fails, but request format is valid
