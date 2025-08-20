"""
Tests for TaskService Template Injection Integration

Test suite for template injection functionality in TaskService.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from src.server.services.projects.task_service import TaskService
from src.server.models.template_injection_models import (
    TemplateExpansionResult,
    TemplateExpansionResponse
)


class TestTaskServiceTemplateInjection:
    """Test TaskService template injection functionality"""

    @pytest.fixture
    def mock_supabase_client(self):
        """Create mock Supabase client"""
        mock_client = Mock()
        mock_client.table.return_value = mock_client
        mock_client.select.return_value = mock_client
        mock_client.eq.return_value = mock_client
        mock_client.gte.return_value = mock_client
        mock_client.insert.return_value = mock_client
        mock_client.update.return_value = mock_client
        mock_client.execute.return_value = Mock(data=[])
        return mock_client

    @pytest.fixture
    def task_service(self, mock_supabase_client):
        """Create TaskService instance with mocked dependencies"""
        return TaskService(mock_supabase_client)

    @pytest.fixture
    def mock_template_service(self):
        """Create mock template injection service"""
        mock_service = Mock()
        mock_service.expand_task_description = AsyncMock()
        return mock_service

    @pytest.fixture
    def sample_expansion_result(self):
        """Create sample template expansion result"""
        return TemplateExpansionResult(
            original_task="Implement OAuth2 authentication",
            template_name="workflow_default",
            expanded_instructions="Step 1: Review homelab environment\n\nImplement OAuth2 authentication\n\nStep 3: Create tests",
            expansion_time_ms=25,
            template_metadata={
                "template_id": str(uuid4()),
                "user_task_position": 2,
                "estimated_duration": 45,
                "required_tools": ["view", "str-replace-editor"]
            }
        )

    @pytest.mark.asyncio
    async def test_create_task_with_template_injection_enabled(
        self, task_service, mock_supabase_client, mock_template_service, sample_expansion_result
    ):
        """Test task creation with template injection enabled"""
        # Mock successful template expansion
        mock_template_service.expand_task_description.return_value = TemplateExpansionResponse(
            success=True,
            result=sample_expansion_result,
            message="Template expansion completed successfully"
        )

        # Mock successful task creation
        created_task = {
            "id": str(uuid4()),
            "project_id": "test-project-id",
            "title": "Test Task",
            "description": sample_expansion_result.expanded_instructions,
            "status": "todo",
            "assignee": "AI IDE Agent",
            "task_order": 0,
            "created_at": "2025-08-20T10:00:00Z"
        }
        mock_supabase_client.execute.return_value = Mock(data=[created_task])

        # Patch template injection service
        with patch('src.server.services.projects.task_service.get_template_injection_service', return_value=mock_template_service):
            with patch('src.server.services.projects.task_service._template_injection_available', True):
                # Create task with template injection enabled
                success, result = await task_service.create_task(
                    project_id="test-project-id",
                    title="Test Task",
                    description="Implement OAuth2 authentication",
                    assignee="AI IDE Agent",
                    enable_template_injection=True
                )

        assert success is True
        assert result["task"]["description"] == sample_expansion_result.expanded_instructions
        
        # Verify template service was called
        mock_template_service.expand_task_description.assert_called_once()
        call_args = mock_template_service.expand_task_description.call_args
        assert call_args[1]["original_description"] == "Implement OAuth2 authentication"
        assert call_args[1]["template_name"] == "workflow_default"

    @pytest.mark.asyncio
    async def test_create_task_with_template_injection_disabled(
        self, task_service, mock_supabase_client
    ):
        """Test task creation with template injection disabled"""
        # Mock successful task creation
        created_task = {
            "id": str(uuid4()),
            "project_id": "test-project-id",
            "title": "Test Task",
            "description": "Implement OAuth2 authentication",
            "status": "todo",
            "assignee": "AI IDE Agent",
            "task_order": 0,
            "created_at": "2025-08-20T10:00:00Z"
        }
        mock_supabase_client.execute.return_value = Mock(data=[created_task])

        # Create task with template injection disabled
        success, result = await task_service.create_task(
            project_id="test-project-id",
            title="Test Task",
            description="Implement OAuth2 authentication",
            assignee="AI IDE Agent",
            enable_template_injection=False
        )

        assert success is True
        assert result["task"]["description"] == "Implement OAuth2 authentication"  # Original description

    @pytest.mark.asyncio
    async def test_create_task_template_expansion_failure(
        self, task_service, mock_supabase_client, mock_template_service
    ):
        """Test task creation when template expansion fails"""
        # Mock failed template expansion
        mock_template_service.expand_task_description.return_value = TemplateExpansionResponse(
            success=False,
            result=None,
            message="Template expansion failed",
            error="Template not found"
        )

        # Mock successful task creation
        created_task = {
            "id": str(uuid4()),
            "project_id": "test-project-id",
            "title": "Test Task",
            "description": "Implement OAuth2 authentication",  # Should fallback to original
            "status": "todo",
            "assignee": "AI IDE Agent",
            "task_order": 0,
            "created_at": "2025-08-20T10:00:00Z"
        }
        mock_supabase_client.execute.return_value = Mock(data=[created_task])

        # Patch template injection service
        with patch('src.server.services.projects.task_service.get_template_injection_service', return_value=mock_template_service):
            with patch('src.server.services.projects.task_service._template_injection_available', True):
                # Create task with template injection enabled but expansion fails
                success, result = await task_service.create_task(
                    project_id="test-project-id",
                    title="Test Task",
                    description="Implement OAuth2 authentication",
                    assignee="AI IDE Agent",
                    enable_template_injection=True
                )

        assert success is True
        assert result["task"]["description"] == "Implement OAuth2 authentication"  # Fallback to original

    @pytest.mark.asyncio
    async def test_create_task_template_service_exception(
        self, task_service, mock_supabase_client, mock_template_service
    ):
        """Test task creation when template service raises exception"""
        # Mock template service exception
        mock_template_service.expand_task_description.side_effect = Exception("Service unavailable")

        # Mock successful task creation
        created_task = {
            "id": str(uuid4()),
            "project_id": "test-project-id",
            "title": "Test Task",
            "description": "Implement OAuth2 authentication",  # Should fallback to original
            "status": "todo",
            "assignee": "AI IDE Agent",
            "task_order": 0,
            "created_at": "2025-08-20T10:00:00Z"
        }
        mock_supabase_client.execute.return_value = Mock(data=[created_task])

        # Patch template injection service
        with patch('src.server.services.projects.task_service.get_template_injection_service', return_value=mock_template_service):
            with patch('src.server.services.projects.task_service._template_injection_available', True):
                # Create task with template injection enabled but service throws exception
                success, result = await task_service.create_task(
                    project_id="test-project-id",
                    title="Test Task",
                    description="Implement OAuth2 authentication",
                    assignee="AI IDE Agent",
                    enable_template_injection=True
                )

        assert success is True
        assert result["task"]["description"] == "Implement OAuth2 authentication"  # Fallback to original

    def test_is_template_injection_enabled_explicit_override(self, task_service):
        """Test template injection feature flag with explicit override"""
        # Explicit True override
        assert task_service._is_template_injection_enabled(True, "any-project") is True
        
        # Explicit False override
        assert task_service._is_template_injection_enabled(False, "any-project") is False

    def test_is_template_injection_enabled_global_flag(self, task_service):
        """Test template injection feature flag with global environment variable"""
        with patch.dict('os.environ', {'TEMPLATE_INJECTION_ENABLED': 'true'}):
            assert task_service._is_template_injection_enabled(None, "any-project") is True
        
        with patch.dict('os.environ', {'TEMPLATE_INJECTION_ENABLED': 'false'}):
            assert task_service._is_template_injection_enabled(None, "any-project") is False

    def test_is_template_injection_enabled_per_project(self, task_service):
        """Test template injection feature flag with per-project control"""
        with patch.dict('os.environ', {
            'TEMPLATE_INJECTION_ENABLED': 'true',
            'TEMPLATE_INJECTION_PROJECTS': 'project-1,project-2,project-3'
        }):
            assert task_service._is_template_injection_enabled(None, "project-1") is True
            assert task_service._is_template_injection_enabled(None, "project-2") is True
            assert task_service._is_template_injection_enabled(None, "project-4") is False

    def test_is_template_injection_enabled_no_project_restrictions(self, task_service):
        """Test template injection feature flag with no project restrictions"""
        with patch.dict('os.environ', {
            'TEMPLATE_INJECTION_ENABLED': 'true',
            'TEMPLATE_INJECTION_PROJECTS': ''
        }):
            assert task_service._is_template_injection_enabled(None, "any-project") is True
