"""
Data Integrity Validation Tests for Export/Import System

This module provides comprehensive data integrity testing including:
- Checksum validation
- Data consistency verification
- Corruption detection
- Round-trip data preservation
"""

import hashlib
import json
import os
import tempfile
import zipfile
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

from src.server.services.projects.export_service import ProjectExportService
from src.server.services.projects.import_service import ProjectImportService


class TestDataIntegrity:
    """Data integrity validation tests"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.export_service = ProjectExportService(self.mock_supabase)
        self.import_service = ProjectImportService(self.mock_supabase)
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_checksum_validation_success(self):
        """Test successful checksum validation"""
        # Create test data
        project_data, tasks_data = self._create_test_data()
        self._mock_export_database_responses(project_data, tasks_data)
        
        # Export project
        success, export_result = self.export_service.export_project(
            project_id="integrity-test-1",
            export_type="full",
            exported_by="integrity_test"
        )
        
        assert success is True
        export_file = export_result["file_path"]
        
        # Validate checksums
        is_valid, validation_result = self.import_service.validate_import_file(export_file)
        
        assert is_valid is True
        assert "project_title" in validation_result

    @pytest.mark.asyncio
    async def test_checksum_validation_corruption_detection(self):
        """Test detection of file corruption through checksums"""
        # Create test data
        project_data, tasks_data = self._create_test_data()
        self._mock_export_database_responses(project_data, tasks_data)
        
        # Export project
        success, export_result = self.export_service.export_project(
            project_id="integrity-test-2",
            export_type="full",
            exported_by="integrity_test"
        )
        
        assert success is True
        export_file = export_result["file_path"]
        
        # Corrupt the export file
        corrupted_file = self._corrupt_export_file(export_file)
        
        # Validate corrupted file
        is_valid, validation_result = self.import_service.validate_import_file(corrupted_file)
        
        # Should detect corruption
        assert is_valid is False
        assert "error" in validation_result

    @pytest.mark.asyncio
    async def test_round_trip_data_preservation(self):
        """Test that data is preserved through export/import cycle"""
        # Create comprehensive test data
        original_project_data, original_tasks_data = self._create_comprehensive_test_data()
        self._mock_export_database_responses(original_project_data, original_tasks_data)
        
        # Export project
        success, export_result = self.export_service.export_project(
            project_id="round-trip-test",
            export_type="full",
            exported_by="integrity_test"
        )
        
        assert success is True
        export_file = export_result["file_path"]
        
        # Extract and verify exported data
        exported_data = self._extract_export_data(export_file)
        
        # Verify project data preservation
        self._verify_project_data_integrity(original_project_data, exported_data["project"])
        
        # Verify tasks data preservation
        self._verify_tasks_data_integrity(original_tasks_data, exported_data["tasks"]["tasks"])
        
        # Verify metadata preservation
        self._verify_metadata_integrity(exported_data["manifest"])

    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters"""
        # Create data with special characters
        project_data = {
            "id": "unicode-test",
            "title": "Test Project with Unicode: 测试项目 🚀 émojis",
            "description": "Description with special chars: <>&\"'`\n\t\r",
            "docs": [
                {
                    "id": "unicode-doc",
                    "title": "Unicode Document: 日本語 العربية русский",
                    "content": {
                        "text": "Content with emojis: 🎉🔥💯 and symbols: ∑∆∞≠≤≥"
                    }
                }
            ]
        }
        
        tasks_data = [
            {
                "id": "unicode-task",
                "project_id": "unicode-test",
                "title": "Task with Unicode: 中文任务",
                "description": "Description: Ñoño piñata jalapeño café résumé naïve"
            }
        ]
        
        self._mock_export_database_responses(project_data, tasks_data)
        
        # Export and import
        success, export_result = self.export_service.export_project(
            project_id="unicode-test",
            export_type="full",
            exported_by="unicode_test"
        )
        
        assert success is True
        
        # Verify Unicode preservation
        exported_data = self._extract_export_data(export_result["file_path"])
        
        assert exported_data["project"]["title"] == project_data["title"]
        assert exported_data["project"]["description"] == project_data["description"]
        assert exported_data["tasks"]["tasks"][0]["title"] == tasks_data[0]["title"]

    @pytest.mark.asyncio
    async def test_large_data_integrity(self):
        """Test data integrity with large datasets"""
        # Create large dataset
        project_data = {
            "id": "large-data-test",
            "title": "Large Data Test Project",
            "description": "x" * 10000,  # Large description
            "docs": [
                {
                    "id": f"large-doc-{i}",
                    "title": f"Large Document {i}",
                    "content": {"text": "y" * 5000}  # Large content
                }
                for i in range(50)
            ]
        }
        
        tasks_data = [
            {
                "id": f"large-task-{i}",
                "project_id": "large-data-test",
                "title": f"Large Task {i}",
                "description": "z" * 2000  # Large description
            }
            for i in range(1000)
        ]
        
        self._mock_export_database_responses(project_data, tasks_data)
        
        # Export project
        success, export_result = self.export_service.export_project(
            project_id="large-data-test",
            export_type="full",
            exported_by="large_data_test"
        )
        
        assert success is True
        
        # Verify data integrity
        exported_data = self._extract_export_data(export_result["file_path"])
        
        # Check that all data is preserved
        assert len(exported_data["project"]["docs"]) == 50
        assert len(exported_data["tasks"]["tasks"]) == 1000
        
        # Verify content integrity
        assert exported_data["project"]["description"] == project_data["description"]
        assert exported_data["tasks"]["tasks"][0]["description"] == tasks_data[0]["description"]

    @pytest.mark.asyncio
    async def test_nested_data_structure_integrity(self):
        """Test integrity of complex nested data structures"""
        # Create complex nested data
        complex_project_data = {
            "id": "nested-test",
            "title": "Nested Data Test",
            "docs": [
                {
                    "id": "complex-doc",
                    "content": {
                        "sections": [
                            {
                                "title": "Section 1",
                                "subsections": [
                                    {
                                        "title": "Subsection 1.1",
                                        "items": [
                                            {"type": "text", "value": "Text item"},
                                            {"type": "list", "items": ["Item 1", "Item 2", "Item 3"]},
                                            {"type": "object", "data": {"key1": "value1", "key2": {"nested": "value"}}}
                                        ]
                                    }
                                ]
                            }
                        ],
                        "metadata": {
                            "tags": ["tag1", "tag2"],
                            "properties": {
                                "prop1": True,
                                "prop2": 42,
                                "prop3": None,
                                "prop4": [1, 2, 3]
                            }
                        }
                    }
                }
            ]
        }
        
        self._mock_export_database_responses(complex_project_data, [])
        
        # Export and verify
        success, export_result = self.export_service.export_project(
            project_id="nested-test",
            export_type="full",
            exported_by="nested_test"
        )
        
        assert success is True
        
        # Verify nested structure preservation
        exported_data = self._extract_export_data(export_result["file_path"])
        original_content = complex_project_data["docs"][0]["content"]
        exported_content = exported_data["project"]["docs"][0]["content"]
        
        # Deep comparison of nested structures
        assert exported_content["sections"][0]["title"] == original_content["sections"][0]["title"]
        assert exported_content["sections"][0]["subsections"][0]["items"][2]["data"]["key2"]["nested"] == "value"
        assert exported_content["metadata"]["properties"]["prop1"] is True
        assert exported_content["metadata"]["properties"]["prop2"] == 42
        assert exported_content["metadata"]["properties"]["prop3"] is None

    def test_export_file_format_validation(self):
        """Test validation of export file format structure"""
        # Create test data
        project_data, tasks_data = self._create_test_data()
        self._mock_export_database_responses(project_data, tasks_data)
        
        # Export project
        success, export_result = self.export_service.export_project(
            project_id="format-test",
            export_type="full",
            exported_by="format_test"
        )
        
        assert success is True
        export_file = export_result["file_path"]
        
        # Validate ZIP file structure
        with zipfile.ZipFile(export_file, 'r') as zipf:
            files = zipf.namelist()
            
            # Check required files
            required_files = ["manifest.json", "project.json", "tasks.json"]
            for required_file in required_files:
                assert required_file in files
            
            # Validate JSON structure
            for json_file in required_files:
                content = zipf.read(json_file)
                try:
                    json.loads(content.decode('utf-8'))
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON in {json_file}")

    def _create_test_data(self) -> tuple:
        """Create basic test data"""
        project_data = {
            "id": "integrity-test",
            "title": "Data Integrity Test Project",
            "description": "Test project for data integrity validation",
            "docs": [
                {
                    "id": "test-doc-1",
                    "title": "Test Document",
                    "content": {"text": "Test content"}
                }
            ],
            "created_at": datetime.now().isoformat()
        }
        
        tasks_data = [
            {
                "id": "test-task-1",
                "project_id": "integrity-test",
                "title": "Test Task",
                "description": "Test task description",
                "status": "todo"
            }
        ]
        
        return project_data, tasks_data

    def _create_comprehensive_test_data(self) -> tuple:
        """Create comprehensive test data for round-trip testing"""
        project_data = {
            "id": "comprehensive-test",
            "title": "Comprehensive Test Project",
            "description": "Complete test project with all data types",
            "github_repo": "https://github.com/test/repo",
            "pinned": True,
            "docs": [
                {
                    "id": "comprehensive-doc",
                    "document_type": "prp",
                    "title": "Comprehensive Document",
                    "content": {
                        "goal": "Test comprehensive data",
                        "sections": ["section1", "section2"],
                        "metadata": {"version": "1.0", "author": "test"}
                    },
                    "metadata": {"tags": ["test", "comprehensive"]}
                }
            ],
            "features": ["feature1", "feature2"],
            "data": {"config": {"setting1": True, "setting2": 42}},
            "created_at": "2025-08-18T22:00:00Z",
            "updated_at": "2025-08-18T22:30:00Z"
        }
        
        tasks_data = [
            {
                "id": "comprehensive-task-1",
                "project_id": "comprehensive-test",
                "title": "Comprehensive Task 1",
                "description": "First comprehensive test task",
                "status": "todo",
                "assignee": "User",
                "task_order": 1,
                "feature": "feature1",
                "sources": [{"url": "test.com", "type": "docs"}],
                "code_examples": [{"file": "test.py", "function": "test_func"}],
                "created_at": "2025-08-18T22:00:00Z",
                "updated_at": "2025-08-18T22:15:00Z"
            },
            {
                "id": "comprehensive-task-2",
                "project_id": "comprehensive-test",
                "title": "Comprehensive Task 2",
                "description": "Second comprehensive test task",
                "status": "doing",
                "assignee": "AI IDE Agent",
                "task_order": 2,
                "feature": "feature2",
                "sources": [],
                "code_examples": [],
                "created_at": "2025-08-18T22:05:00Z",
                "updated_at": "2025-08-18T22:20:00Z"
            }
        ]
        
        return project_data, tasks_data

    def _mock_export_database_responses(self, project_data: Dict, tasks_data: List[Dict]):
        """Mock database responses for export"""
        # Mock project query
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [project_data]
        
        # Mock tasks query
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = tasks_data
        
        # Mock empty responses for versions and sources
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []

    def _extract_export_data(self, export_file: str) -> Dict[str, Any]:
        """Extract data from export file"""
        with zipfile.ZipFile(export_file, 'r') as zipf:
            manifest = json.loads(zipf.read("manifest.json").decode('utf-8'))
            project = json.loads(zipf.read("project.json").decode('utf-8'))
            tasks = json.loads(zipf.read("tasks.json").decode('utf-8'))
            
            return {
                "manifest": manifest,
                "project": project,
                "tasks": tasks
            }

    def _verify_project_data_integrity(self, original: Dict, exported: Dict):
        """Verify project data integrity"""
        # Check basic fields
        assert exported["id"] == original["id"]
        assert exported["title"] == original["title"]
        assert exported["description"] == original["description"]
        
        # Check optional fields
        if "github_repo" in original:
            assert exported["github_repo"] == original["github_repo"]
        if "pinned" in original:
            assert exported["pinned"] == original["pinned"]
        
        # Check complex fields
        if "docs" in original:
            assert len(exported["docs"]) == len(original["docs"])
            for i, doc in enumerate(original["docs"]):
                assert exported["docs"][i]["id"] == doc["id"]
                assert exported["docs"][i]["title"] == doc["title"]

    def _verify_tasks_data_integrity(self, original: List[Dict], exported: List[Dict]):
        """Verify tasks data integrity"""
        assert len(exported) == len(original)
        
        for i, task in enumerate(original):
            exported_task = exported[i]
            assert exported_task["id"] == task["id"]
            assert exported_task["title"] == task["title"]
            assert exported_task["description"] == task["description"]
            assert exported_task["status"] == task["status"]

    def _verify_metadata_integrity(self, manifest: Dict):
        """Verify export metadata integrity"""
        required_fields = ["format_version", "export_timestamp", "project_id"]
        for field in required_fields:
            assert field in manifest
        
        # Verify format version
        assert manifest["format_version"] == "1.0.0"
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(manifest["export_timestamp"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Invalid timestamp format in manifest")

    def _corrupt_export_file(self, original_file: str) -> str:
        """Create a corrupted version of an export file"""
        corrupted_file = os.path.join(self.temp_dir, "corrupted_export.zip")
        
        # Copy original file
        import shutil
        shutil.copy2(original_file, corrupted_file)
        
        # Corrupt the file by modifying some bytes
        with open(corrupted_file, 'r+b') as f:
            f.seek(100)  # Seek to position 100
            f.write(b'\x00\x00\x00\x00')  # Write some null bytes
        
        return corrupted_file


class TestExportImportEdgeCases:
    """Edge case testing for export/import system"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_supabase = MagicMock()
        self.export_service = ProjectExportService(self.mock_supabase)
        self.import_service = ProjectImportService(self.mock_supabase)
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_empty_project_export_import(self):
        """Test export/import of completely empty project"""
        # Create empty project
        empty_project = {
            "id": "empty-project",
            "title": "Empty Project",
            "description": "",
            "docs": [],
            "features": [],
            "data": {}
        }

        self._mock_export_database_responses(empty_project, [])

        # Export empty project
        success, export_result = self.export_service.export_project(
            project_id="empty-project",
            export_type="full",
            exported_by="edge_case_test"
        )

        assert success is True

        # Verify export file structure
        exported_data = self._extract_export_data(export_result["file_path"])
        assert exported_data["project"]["title"] == "Empty Project"
        assert len(exported_data["tasks"]["tasks"]) == 0

    @pytest.mark.asyncio
    async def test_null_and_none_values(self):
        """Test handling of null and None values"""
        project_with_nulls = {
            "id": "null-test-project",
            "title": "Project with Nulls",
            "description": None,
            "github_repo": None,
            "docs": [
                {
                    "id": "null-doc",
                    "title": "Document with Nulls",
                    "content": {
                        "text": None,
                        "metadata": None,
                        "sections": []
                    },
                    "metadata": None
                }
            ]
        }

        tasks_with_nulls = [
            {
                "id": "null-task",
                "project_id": "null-test-project",
                "title": "Task with Nulls",
                "description": None,
                "assignee": None,
                "sources": None,
                "code_examples": None
            }
        ]

        self._mock_export_database_responses(project_with_nulls, tasks_with_nulls)

        # Export and verify null handling
        success, export_result = self.export_service.export_project(
            project_id="null-test-project",
            export_type="full",
            exported_by="null_test"
        )

        assert success is True

        # Verify nulls are preserved
        exported_data = self._extract_export_data(export_result["file_path"])
        assert exported_data["project"]["description"] is None
        assert exported_data["tasks"]["tasks"][0]["description"] is None

    def _mock_export_database_responses(self, project_data, tasks_data):
        """Mock database responses for export"""
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [project_data]
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = tasks_data

    def _extract_export_data(self, export_file: str):
        """Extract data from export file"""
        with zipfile.ZipFile(export_file, 'r') as zipf:
            project = json.loads(zipf.read("project.json").decode('utf-8'))
            tasks = json.loads(zipf.read("tasks.json").decode('utf-8'))

            return {"project": project, "tasks": tasks}
