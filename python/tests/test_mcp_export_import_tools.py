"""
Tests for MCP Export/Import Tools

This module tests the MCP tools for export/import and backup operations including:
- Tool parameter validation
- Tool execution and result handling
- Integration with export/import services
- Error handling and edge cases
"""

import json
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.mcp.modules.export_import_tools import (
    create_backup_archon,
    export_project_archon,
    import_project_archon,
    list_backup_schedules_archon,
    list_backups_archon,
    restore_backup_archon,
    schedule_backup_archon,
    validate_import_file_archon,
)
from src.mcp.modules.tool_handler import (
    ExportImportToolHandler,
    execute_export_import_tool,
    get_export_import_handler,
    validate_export_import_parameters,
)


class TestExportImportTools:
    """Test cases for export/import MCP tools"""

    @pytest.mark.asyncio
    @patch('src.mcp.modules.export_import_tools.ProjectExportService')
    async def test_export_project_archon_success(self, mock_export_service_class):
        """Test successful project export"""
        # Mock export service
        mock_export_service = AsyncMock()
        mock_export_service_class.return_value = mock_export_service
        mock_export_service.export_project.return_value = (True, {
            "export_id": "export-123",
            "file_path": "/tmp/export.zip",
            "file_size": 1024,
            "message": "Export completed"
        })
        
        result_json = await export_project_archon(
            project_id="test-project-id",
            export_type="full"
        )
        
        result = json.loads(result_json)
        assert result["success"] is True
        assert result["export_id"] == "export-123"
        assert result["file_path"] == "/tmp/export.zip"
        
        # Verify service was called correctly
        mock_export_service.export_project.assert_called_once_with(
            project_id="test-project-id",
            export_type="full",
            include_versions=True,
            include_sources=True,
            include_attachments=False,
            version_limit=None,
            exported_by="mcp_tool"
        )

    @pytest.mark.asyncio
    @patch('src.mcp.modules.export_import_tools.ProjectExportService')
    async def test_export_project_archon_failure(self, mock_export_service_class):
        """Test project export failure"""
        # Mock export service failure
        mock_export_service = AsyncMock()
        mock_export_service_class.return_value = mock_export_service
        mock_export_service.export_project.return_value = (False, {
            "error": "Project not found"
        })
        
        result_json = await export_project_archon(
            project_id="nonexistent-project"
        )
        
        result = json.loads(result_json)
        assert result["success"] is False
        assert "Project not found" in result["error"]

    @pytest.mark.asyncio
    @patch('src.mcp.modules.export_import_tools.ProjectImportService')
    async def test_import_project_archon_success(self, mock_import_service_class):
        """Test successful project import"""
        # Mock import service
        mock_import_service = AsyncMock()
        mock_import_service_class.return_value = mock_import_service
        mock_import_service.import_project.return_value = (True, {
            "project_id": "imported-project-123",
            "import_summary": {"tasks_imported": 5},
            "conflicts_resolved": [],
            "message": "Import completed"
        })
        
        result_json = await import_project_archon(
            import_file_path="/tmp/test_export.zip",
            import_type="full"
        )
        
        result = json.loads(result_json)
        assert result["success"] is True
        assert result["project_id"] == "imported-project-123"
        assert result["import_summary"]["tasks_imported"] == 5

    @pytest.mark.asyncio
    @patch('src.mcp.modules.export_import_tools.ProjectImportService')
    async def test_validate_import_file_archon_success(self, mock_import_service_class):
        """Test successful import file validation"""
        # Mock import service
        mock_import_service = AsyncMock()
        mock_import_service_class.return_value = mock_import_service
        mock_import_service.validate_import_file.return_value = (True, {
            "project_title": "Test Project",
            "project_id": "test-project-id",
            "task_count": 10,
            "document_count": 5
        })
        
        result_json = await validate_import_file_archon("/tmp/test_export.zip")
        
        result = json.loads(result_json)
        assert result["valid"] is True
        assert result["project_title"] == "Test Project"
        assert result["task_count"] == 10

    @pytest.mark.asyncio
    @patch('src.mcp.modules.export_import_tools.get_backup_manager')
    async def test_create_backup_archon_success(self, mock_get_backup_manager):
        """Test successful backup creation"""
        # Mock backup manager
        mock_backup_manager = AsyncMock()
        mock_get_backup_manager.return_value = mock_backup_manager
        mock_backup_manager.create_project_backup.return_value = (True, {
            "backup_id": "backup-123",
            "backup_metadata": {"project_id": "test-project"},
            "message": "Backup created"
        })
        
        result_json = await create_backup_archon(
            project_id="test-project-id",
            backup_type="full"
        )
        
        result = json.loads(result_json)
        assert result["success"] is True
        assert result["backup_id"] == "backup-123"

    @pytest.mark.asyncio
    @patch('src.mcp.modules.export_import_tools.get_backup_manager')
    async def test_restore_backup_archon_success(self, mock_get_backup_manager):
        """Test successful backup restoration"""
        # Mock backup manager
        mock_backup_manager = AsyncMock()
        mock_get_backup_manager.return_value = mock_backup_manager
        mock_backup_manager.restore_project_backup.return_value = (True, {
            "backup_id": "backup-123",
            "restored_project_id": "restored-project-456",
            "import_summary": {"tasks_imported": 8},
            "message": "Backup restored"
        })
        
        result_json = await restore_backup_archon(
            backup_id="backup-123",
            conflict_resolution="merge"
        )
        
        result = json.loads(result_json)
        assert result["success"] is True
        assert result["restored_project_id"] == "restored-project-456"

    @pytest.mark.asyncio
    @patch('src.mcp.modules.export_import_tools.get_backup_manager')
    async def test_list_backups_archon_success(self, mock_get_backup_manager):
        """Test successful backup listing"""
        # Mock backup manager
        mock_backup_manager = AsyncMock()
        mock_get_backup_manager.return_value = mock_backup_manager
        mock_backup_manager.storage_backend.list_backups.return_value = [
            {"backup_id": "backup-1", "project_id": "project-1"},
            {"backup_id": "backup-2", "project_id": "project-2"}
        ]
        
        result_json = await list_backups_archon()
        
        result = json.loads(result_json)
        assert result["success"] is True
        assert len(result["backups"]) == 2
        assert result["total_count"] == 2

    @pytest.mark.asyncio
    @patch('src.mcp.modules.export_import_tools.get_backup_scheduler')
    async def test_schedule_backup_archon_success(self, mock_get_backup_scheduler):
        """Test successful backup scheduling"""
        # Mock backup scheduler
        mock_scheduler = AsyncMock()
        mock_get_backup_scheduler.return_value = mock_scheduler
        mock_scheduler.create_schedule.return_value = (True, {
            "schedule_id": "schedule-123",
            "schedule": {"project_id": "test-project", "cron_expression": "0 2 * * *"},
            "message": "Schedule created"
        })
        
        result_json = await schedule_backup_archon(
            project_id="test-project-id",
            schedule_type="cron",
            cron_expression="0 2 * * *"
        )
        
        result = json.loads(result_json)
        assert result["success"] is True
        assert result["schedule_id"] == "schedule-123"

    @pytest.mark.asyncio
    @patch('src.mcp.modules.export_import_tools.get_backup_scheduler')
    async def test_list_backup_schedules_archon_success(self, mock_get_backup_scheduler):
        """Test successful backup schedule listing"""
        # Mock backup scheduler
        mock_scheduler = AsyncMock()
        mock_get_backup_scheduler.return_value = mock_scheduler
        mock_scheduler.list_schedules.return_value = (True, {
            "schedules": [
                {"schedule_id": "schedule-1", "project_id": "project-1"},
                {"schedule_id": "schedule-2", "project_id": "project-2"}
            ],
            "total_count": 2
        })
        
        result_json = await list_backup_schedules_archon()
        
        result = json.loads(result_json)
        assert result["success"] is True
        assert len(result["schedules"]) == 2


class TestExportImportToolHandler:
    """Test cases for ExportImportToolHandler"""

    def setup_method(self):
        """Set up test fixtures"""
        self.handler = ExportImportToolHandler()

    @pytest.mark.asyncio
    async def test_handle_tool_call_success(self):
        """Test successful tool call handling"""
        with patch.object(self.handler.tool_mapping["export_project_archon"], '__call__') as mock_tool:
            mock_tool.return_value = json.dumps({
                "success": True,
                "export_id": "export-123",
                "message": "Export completed"
            })
            
            success, result = await self.handler.handle_tool_call(
                "export_project_archon",
                {"project_id": "test-project"}
            )
            
            assert success is True
            assert result["success"] is True
            assert result["result"]["export_id"] == "export-123"

    @pytest.mark.asyncio
    async def test_handle_tool_call_unknown_tool(self):
        """Test handling unknown tool"""
        success, result = await self.handler.handle_tool_call(
            "unknown_tool",
            {}
        )
        
        assert success is False
        assert "Unknown export/import tool" in result["error"]
        assert "available_tools" in result

    @pytest.mark.asyncio
    async def test_handle_tool_call_invalid_json(self):
        """Test handling tool that returns invalid JSON"""
        with patch.object(self.handler.tool_mapping["export_project_archon"], '__call__') as mock_tool:
            mock_tool.return_value = "invalid json"
            
            success, result = await self.handler.handle_tool_call(
                "export_project_archon",
                {"project_id": "test-project"}
            )
            
            assert success is False
            assert "invalid JSON" in result["error"]

    def test_get_available_tools(self):
        """Test getting available tools"""
        tools = self.handler.get_available_tools()
        
        assert "export_project_archon" in tools
        assert "import_project_archon" in tools
        assert "create_backup_archon" in tools
        assert len(tools) == 8

    def test_is_export_import_tool(self):
        """Test checking if tool is export/import tool"""
        assert self.handler.is_export_import_tool("export_project_archon") is True
        assert self.handler.is_export_import_tool("unknown_tool") is False


class TestParameterValidation:
    """Test cases for parameter validation"""

    def test_validate_export_project_parameters_valid(self):
        """Test valid export project parameters"""
        is_valid, result = validate_export_import_parameters(
            "export_project_archon",
            {"project_id": "test-project", "export_type": "full"}
        )
        
        assert is_valid is True
        assert "successfully" in result["message"]

    def test_validate_export_project_parameters_missing_project_id(self):
        """Test export project parameters missing project_id"""
        is_valid, result = validate_export_import_parameters(
            "export_project_archon",
            {"export_type": "full"}
        )
        
        assert is_valid is False
        assert "Missing required parameter: project_id" in result["validation_errors"]

    def test_validate_export_project_parameters_invalid_export_type(self):
        """Test export project parameters with invalid export_type"""
        is_valid, result = validate_export_import_parameters(
            "export_project_archon",
            {"project_id": "test-project", "export_type": "invalid"}
        )
        
        assert is_valid is False
        assert "export_type must be one of" in result["validation_errors"][0]

    def test_validate_import_project_parameters_valid(self):
        """Test valid import project parameters"""
        is_valid, result = validate_export_import_parameters(
            "import_project_archon",
            {"import_file_path": "/tmp/test.zip", "import_type": "full"}
        )
        
        assert is_valid is True

    def test_validate_schedule_backup_parameters_cron_missing_expression(self):
        """Test schedule backup parameters with cron type but missing expression"""
        is_valid, result = validate_export_import_parameters(
            "schedule_backup_archon",
            {"project_id": "test-project", "schedule_type": "cron"}
        )
        
        assert is_valid is False
        assert "cron_expression required" in result["validation_errors"][0]

    def test_validate_unknown_tool(self):
        """Test validation of unknown tool"""
        is_valid, result = validate_export_import_parameters(
            "unknown_tool",
            {}
        )
        
        assert is_valid is False
        assert "Unknown export/import tool" in result["error"]


@pytest.mark.asyncio
async def test_execute_export_import_tool_integration():
    """Test integration of execute_export_import_tool function"""
    with patch('src.mcp.modules.tool_handler.get_export_import_handler') as mock_get_handler:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler
        mock_handler.handle_tool_call.return_value = (True, {"success": True, "result": "test"})
        
        success, result = await execute_export_import_tool(
            "export_project_archon",
            {"project_id": "test-project"}
        )
        
        assert success is True
        assert result["success"] is True
