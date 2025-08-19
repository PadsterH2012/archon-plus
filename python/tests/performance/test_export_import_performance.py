"""
Performance Tests for Export/Import System

This module provides performance testing for the export/import system including
benchmarks for large datasets, memory usage analysis, and scalability testing.
"""

import asyncio
import json
import os
import tempfile
import time
import zipfile
from datetime import datetime
from typing import Dict, List
from unittest.mock import MagicMock

import pytest

from src.server.services.projects.export_service import ProjectExportService
from src.server.services.projects.import_service import ProjectImportService


class TestExportImportPerformance:
    """Performance tests for export/import operations"""

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

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_export_performance_small_project(self):
        """Test export performance with small project (< 100 tasks)"""
        # Create small project data
        project_data, tasks_data = self._create_test_data(
            task_count=50,
            document_count=10,
            version_count=20
        )
        
        self._mock_database_responses(project_data, tasks_data)
        
        # Measure export time
        start_time = time.time()
        
        success, result = self.export_service.export_project(
            project_id="perf-test-small",
            export_type="full",
            exported_by="performance_test"
        )
        
        end_time = time.time()
        export_time = end_time - start_time
        
        assert success is True
        assert export_time < 5.0  # Should complete in under 5 seconds
        
        # Verify file size is reasonable
        file_size = os.path.getsize(result["file_path"])
        assert file_size < 1024 * 1024  # Should be under 1MB
        
        print(f"Small project export: {export_time:.2f}s, {file_size} bytes")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_export_performance_medium_project(self):
        """Test export performance with medium project (100-1000 tasks)"""
        # Create medium project data
        project_data, tasks_data = self._create_test_data(
            task_count=500,
            document_count=50,
            version_count=100
        )
        
        self._mock_database_responses(project_data, tasks_data)
        
        # Measure export time
        start_time = time.time()
        
        success, result = self.export_service.export_project(
            project_id="perf-test-medium",
            export_type="full",
            exported_by="performance_test"
        )
        
        end_time = time.time()
        export_time = end_time - start_time
        
        assert success is True
        assert export_time < 15.0  # Should complete in under 15 seconds
        
        # Verify file size is reasonable
        file_size = os.path.getsize(result["file_path"])
        assert file_size < 10 * 1024 * 1024  # Should be under 10MB
        
        print(f"Medium project export: {export_time:.2f}s, {file_size} bytes")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_export_performance_large_project(self):
        """Test export performance with large project (1000+ tasks)"""
        # Create large project data
        project_data, tasks_data = self._create_test_data(
            task_count=2000,
            document_count=100,
            version_count=200
        )
        
        self._mock_database_responses(project_data, tasks_data)
        
        # Measure export time
        start_time = time.time()
        
        success, result = self.export_service.export_project(
            project_id="perf-test-large",
            export_type="full",
            exported_by="performance_test"
        )
        
        end_time = time.time()
        export_time = end_time - start_time
        
        assert success is True
        assert export_time < 30.0  # Should complete in under 30 seconds
        
        # Verify file size is reasonable
        file_size = os.path.getsize(result["file_path"])
        assert file_size < 50 * 1024 * 1024  # Should be under 50MB
        
        print(f"Large project export: {export_time:.2f}s, {file_size} bytes")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_import_performance_benchmarks(self):
        """Test import performance with various file sizes"""
        # Test different import scenarios
        scenarios = [
            {"name": "small", "task_count": 50, "max_time": 5.0},
            {"name": "medium", "task_count": 500, "max_time": 15.0},
            {"name": "large", "task_count": 1000, "max_time": 25.0}
        ]
        
        for scenario in scenarios:
            # Create test export file
            export_file = self._create_test_export_file(
                task_count=scenario["task_count"],
                project_name=f"perf-test-{scenario['name']}"
            )
            
            # Mock import database responses
            self._mock_import_database_responses()
            
            # Measure import time
            start_time = time.time()
            
            success, result = self.import_service.import_project(
                import_file_path=export_file,
                import_type="full",
                imported_by="performance_test"
            )
            
            end_time = time.time()
            import_time = end_time - start_time
            
            assert success is True
            assert import_time < scenario["max_time"]
            
            print(f"{scenario['name']} project import: {import_time:.2f}s")

    @pytest.mark.performance
    def test_export_file_compression_efficiency(self):
        """Test compression efficiency of export files"""
        # Create test data with varying content
        scenarios = [
            {"name": "text_heavy", "description_length": 1000},
            {"name": "minimal", "description_length": 50},
            {"name": "structured", "description_length": 200}
        ]
        
        compression_ratios = []
        
        for scenario in scenarios:
            # Create project data
            project_data, tasks_data = self._create_test_data(
                task_count=100,
                description_length=scenario["description_length"]
            )
            
            self._mock_database_responses(project_data, tasks_data)
            
            # Export project
            success, result = self.export_service.export_project(
                project_id=f"compression-test-{scenario['name']}",
                export_type="full",
                exported_by="performance_test"
            )
            
            assert success is True
            
            # Analyze compression
            compressed_size = os.path.getsize(result["file_path"])
            
            # Calculate uncompressed size by reading ZIP contents
            uncompressed_size = 0
            with zipfile.ZipFile(result["file_path"], 'r') as zipf:
                for info in zipf.infolist():
                    uncompressed_size += info.file_size
            
            compression_ratio = compressed_size / uncompressed_size if uncompressed_size > 0 else 1
            compression_ratios.append(compression_ratio)
            
            print(f"{scenario['name']}: {compressed_size} bytes compressed, "
                  f"{uncompressed_size} bytes uncompressed, "
                  f"ratio: {compression_ratio:.2f}")
        
        # Verify reasonable compression
        avg_compression = sum(compression_ratios) / len(compression_ratios)
        assert avg_compression < 0.8  # Should achieve at least 20% compression

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_export_operations(self):
        """Test performance with concurrent export operations"""
        # Create multiple project datasets
        project_ids = []
        for i in range(5):
            project_id = f"concurrent-test-{i}"
            project_ids.append(project_id)
            
            project_data, tasks_data = self._create_test_data(
                task_count=100,
                project_id=project_id
            )
            
            # Mock database responses for this project
            self._mock_database_responses(project_data, tasks_data)
        
        # Run concurrent exports
        start_time = time.time()
        
        tasks = []
        for project_id in project_ids:
            task = self.export_service.export_project(
                project_id=project_id,
                export_type="full",
                exported_by="concurrent_test"
            )
            tasks.append(task)
        
        # Wait for all exports to complete
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all exports succeeded
        for success, result in results:
            assert success is True
        
        # Should complete faster than sequential execution
        assert total_time < 15.0  # Should complete in under 15 seconds
        
        print(f"Concurrent exports ({len(project_ids)} projects): {total_time:.2f}s")

    @pytest.mark.performance
    def test_memory_usage_large_export(self):
        """Test memory usage during large export operations"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large project data
        project_data, tasks_data = self._create_test_data(
            task_count=5000,  # Very large dataset
            document_count=200,
            version_count=500
        )
        
        self._mock_database_responses(project_data, tasks_data)
        
        # Perform export
        success, result = self.export_service.export_project(
            project_id="memory-test-large",
            export_type="full",
            exported_by="memory_test"
        )
        
        # Get peak memory usage
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        
        assert success is True
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024
        
        print(f"Memory increase during large export: {memory_increase / 1024 / 1024:.2f} MB")

    def _create_test_data(
        self, 
        task_count: int, 
        document_count: int = 10, 
        version_count: int = 20,
        description_length: int = 100,
        project_id: str = "perf-test-project"
    ) -> tuple:
        """Create test project and task data"""
        project_data = {
            "id": project_id,
            "title": f"Performance Test Project ({task_count} tasks)",
            "description": "Test project for performance testing",
            "docs": [
                {
                    "id": f"doc-{i}",
                    "document_type": "spec",
                    "title": f"Test Document {i}",
                    "content": {"text": "x" * description_length},
                    "metadata": {"version": "1.0"}
                }
                for i in range(document_count)
            ],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        tasks_data = [
            {
                "id": f"task-{i}",
                "project_id": project_id,
                "title": f"Performance Test Task {i}",
                "description": "x" * description_length,
                "status": "todo",
                "assignee": "User",
                "task_order": i,
                "feature": f"feature-{i % 10}",
                "sources": [],
                "code_examples": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            for i in range(task_count)
        ]
        
        return project_data, tasks_data

    def _mock_database_responses(self, project_data: Dict, tasks_data: List[Dict]):
        """Mock database responses for performance tests"""
        # Mock project query
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [project_data]
        
        # Mock tasks query
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = tasks_data
        
        # Mock empty responses for other queries
        self.mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []

    def _mock_import_database_responses(self):
        """Mock database responses for import operations"""
        # Mock project creation
        self.mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "imported-project-perf"}
        ]

    def _create_test_export_file(self, task_count: int, project_name: str) -> str:
        """Create a test export file for import performance testing"""
        export_file = os.path.join(self.temp_dir, f"{project_name}_export.zip")
        
        # Create tasks data
        tasks = [
            {
                "id": f"task-{i}",
                "project_id": "test-project",
                "title": f"Test Task {i}",
                "description": f"Description for task {i}",
                "status": "todo",
                "assignee": "User",
                "task_order": i
            }
            for i in range(task_count)
        ]
        
        with zipfile.ZipFile(export_file, 'w') as zipf:
            # Create manifest
            manifest = {
                "format_version": "1.0.0",
                "export_timestamp": datetime.now().isoformat(),
                "project_id": "test-project"
            }
            zipf.writestr("manifest.json", json.dumps(manifest))
            
            # Create project data
            project_data = {"id": "test-project", "title": project_name}
            zipf.writestr("project.json", json.dumps(project_data))
            
            # Create tasks data
            tasks_data = {"tasks": tasks, "statistics": {"total_tasks": len(tasks)}}
            zipf.writestr("tasks.json", json.dumps(tasks_data))
        
        return export_file
