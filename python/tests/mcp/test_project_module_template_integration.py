"""
Test template integration with TaskService and API.

This test validates that the TaskService correctly supports template
injection parameters and integrates with the TemplateInjectionService.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from src.server.services.projects.task_service import TaskService
from src.server.api_routes.projects_api import CreateTaskRequest


class TestTaskServiceTemplateIntegration:
    """Test template integration with TaskService"""

    @pytest.fixture
    def task_service(self):
        """Create TaskService instance for testing"""
        with patch('src.server.services.projects.task_service.get_supabase_client'):
            return TaskService()

    @pytest.fixture
    def sample_project_id(self):
        """Sample project ID for testing"""
        return str(uuid4())

    @pytest.mark.asyncio
    async def test_task_service_create_with_template_parameters(
        self, task_service, sample_project_id
    ):
        """Test task creation with template parameters"""

        # Mock the Supabase client
        mock_supabase_response = MagicMock()
        mock_supabase_response.data = [{
            "id": str(uuid4()),
            "project_id": sample_project_id,
            "title": "Test Task",
            "description": "Expanded task description with template",
            "status": "todo",
            "assignee": "AI IDE Agent",
            "task_order": 10,
            "created_at": "2025-08-20T10:00:00Z",
            "template_metadata": {
                "template_injection_enabled": True,
                "template_name": "workflow::default",
                "expansion_time_ms": 45.2,
                "template_context": {"priority": "high"},
                "preserve_original": True,
                "original_description": "Original task description"
            }
        }]

        # Mock template injection service
        mock_template_service = MagicMock()
        mock_expansion_result = MagicMock()
        mock_expansion_result.success = True
        mock_expansion_result.result = MagicMock()
        mock_expansion_result.result.expanded_instructions = "Expanded task description with template"
        mock_expansion_result.result.expansion_time_ms = 45.2
        mock_expansion_result.result.template_metadata = {"test": "metadata"}

        mock_template_service.expand_task_description = AsyncMock(return_value=mock_expansion_result)

        with patch.object(task_service.supabase_client, 'table') as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance
            mock_table_instance.insert.return_value.execute.return_value = mock_supabase_response
            mock_table_instance.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = []

            with patch('src.server.services.projects.task_service.get_template_injection_service', return_value=mock_template_service):
                with patch('src.server.services.projects.task_service._template_injection_available', True):
                    # Test task creation with template parameters
                    success, result = await task_service.create_task(
                        project_id=sample_project_id,
                        title="Test Task",
                        description="Original task description",
                        assignee="AI IDE Agent",
                        task_order=10,
                        template_name="workflow::default",
                        template_context={"priority": "high"},
                        preserve_original=True,
                        enable_template_injection=True
                    )

                    # Verify success
                    assert success is True
                    assert "task" in result

                    # Verify template expansion was called with correct parameters
                    mock_template_service.expand_task_description.assert_called_once()
                    call_args = mock_template_service.expand_task_description.call_args
                    assert call_args[1]["original_description"] == "Original task description"
                    assert call_args[1]["template_name"] == "workflow::default"
                    assert call_args[1]["context_data"] == {"priority": "high"}

    @pytest.mark.asyncio
    async def test_task_service_create_with_disabled_template(
        self, task_service, sample_project_id
    ):
        """Test task creation with disabled template injection"""

        # Mock the Supabase client
        mock_supabase_response = MagicMock()
        mock_supabase_response.data = [{
            "id": str(uuid4()),
            "project_id": sample_project_id,
            "title": "Test Task",
            "description": "Original task description",  # No template expansion
            "status": "todo",
            "assignee": "User",
            "task_order": 0,
            "created_at": "2025-08-20T10:00:00Z",
            "template_metadata": {
                "template_injection_enabled": False,
                "preserve_original": False
            }
        }]

        with patch.object(task_service.supabase_client, 'table') as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance
            mock_table_instance.insert.return_value.execute.return_value = mock_supabase_response
            mock_table_instance.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = []

            # Test task creation with disabled template
            success, result = await task_service.create_task(
                project_id=sample_project_id,
                title="Test Task",
                description="Original task description",
                enable_template_injection=False,
                preserve_original=False
            )

            # Verify success
            assert success is True
            assert "task" in result
