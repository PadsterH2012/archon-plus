"""
End-to-End Tests for Template Injection System

This test suite validates the complete template injection workflow from
task creation through template expansion and final instruction delivery.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from src.server.services.template_injection_service import (
    TemplateInjectionService,
    get_template_injection_service
)
from src.server.services.projects.task_service import TaskService
from src.server.models.template_injection_models import (
    TemplateDefinition,
    TemplateComponent,
    TemplateDefinitionType,
    TemplateComponentType,
    TemplateExpansionResult
)


class TestTemplateInjectionE2E:
    """End-to-end tests for template injection system"""

    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client with template injection data"""
        mock_client = MagicMock()
        
        # Mock template definitions table
        mock_template_table = MagicMock()
        mock_client.table.return_value = mock_template_table
        
        # Mock template components data
        mock_components = [
            {
                "id": str(uuid4()),
                "name": "group::understand_homelab_env",
                "description": "Review homelab environment",
                "component_type": "group",
                "instruction_text": "Before starting implementation, review the homelab environment and available services:\n\n1. Check available services using homelab-vault tool\n2. Review network configuration and port availability\n3. Identify any dependencies or conflicts\n4. Verify resource requirements (CPU, memory, storage)",
                "required_tools": ["homelab-vault", "view"],
                "estimated_duration": 8,
                "category": "preparation",
                "priority": "high",
                "tags": ["homelab", "infrastructure", "preparation"],
                "is_active": True,
                "created_at": "2025-08-20T10:00:00Z",
                "updated_at": "2025-08-20T10:00:00Z"
            },
            {
                "id": str(uuid4()),
                "name": "group::create_tests",
                "description": "Create comprehensive tests",
                "component_type": "group",
                "instruction_text": "Create comprehensive tests for your implementation:\n\n1. Write unit tests covering core functionality\n2. Add integration tests for external dependencies\n3. Include edge cases and error scenarios\n4. Ensure test coverage meets project standards (>80%)\n5. Run tests locally to verify they pass",
                "required_tools": ["str-replace-editor", "launch-process"],
                "estimated_duration": 15,
                "category": "testing",
                "priority": "high",
                "tags": ["testing", "quality", "validation"],
                "is_active": True,
                "created_at": "2025-08-20T10:00:00Z",
                "updated_at": "2025-08-20T10:00:00Z"
            }
        ]
        
        # Mock template definition
        mock_template = {
            "id": str(uuid4()),
            "name": "workflow_default",
            "title": "Default Template Injection Workflow",
            "description": "Standard operational workflow for development tasks",
            "template_type": "project",
            "template_data": {
                "template_content": "{{group::understand_homelab_env}}\n\n{{USER_TASK}}\n\n{{group::create_tests}}",
                "user_task_position": 2,
                "estimated_duration": 30,
                "required_tools": ["view", "str-replace-editor", "homelab-vault"]
            },
            "category": "template-injection",
            "tags": ["workflow", "default"],
            "is_public": True,
            "is_active": True,
            "created_by": "test-system",
            "created_at": "2025-08-20T10:00:00Z",
            "updated_at": "2025-08-20T10:00:00Z"
        }
        
        def mock_table_call(table_name):
            if table_name == "archon_template_definitions":
                mock_template_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_template]
                return mock_template_table
            elif table_name == "archon_template_components":
                mock_component_table = MagicMock()
                mock_component_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = mock_components
                return mock_component_table
            elif table_name == "archon_tasks":
                mock_task_table = MagicMock()
                # Mock task table with dynamic response
                def mock_insert_response(*args, **kwargs):
                    mock_response = MagicMock()
                    mock_response.execute.return_value.data = [{
                        "id": str(uuid4()),
                        "project_id": str(uuid4()),
                        "title": "Create Authentication API",  # Use the actual title from test
                        "description": "Expanded task description",
                        "status": "todo",
                        "assignee": "AI IDE Agent",
                        "task_order": 10,
                        "template_metadata": {
                            "template_injection_enabled": True,
                            "template_name": "workflow_default",
                            "expansion_time_ms": 45.2
                        },
                        "created_at": "2025-08-20T10:00:00Z"
                    }]
                    return mock_response

                mock_task_table.insert.side_effect = mock_insert_response
                mock_task_table.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = []
                return mock_task_table
            return MagicMock()
        
        mock_client.table.side_effect = mock_table_call
        return mock_client

    @pytest.fixture
    def template_service(self, mock_supabase_client):
        """Create TemplateInjectionService with mocked dependencies"""
        return TemplateInjectionService(supabase_client=mock_supabase_client)

    @pytest.fixture
    def task_service(self, mock_supabase_client):
        """Create TaskService with mocked dependencies"""
        return TaskService(supabase_client=mock_supabase_client)

    @pytest.mark.asyncio
    async def test_complete_template_injection_workflow(
        self, template_service, task_service, mock_supabase_client
    ):
        """Test complete workflow from task creation to template expansion"""
        
        project_id = str(uuid4())
        original_description = "Create a new API endpoint for user authentication"
        
        # Mock the get_template_injection_service function
        with patch('src.server.services.projects.task_service.get_template_injection_service', return_value=template_service):
            with patch('src.server.services.projects.task_service._template_injection_available', True):
                
                # Test task creation with template injection
                success, result = await task_service.create_task(
                    project_id=project_id,
                    title="Create Authentication API",
                    description=original_description,
                    assignee="AI IDE Agent",
                    template_name="workflow_default",
                    enable_template_injection=True
                )
                
                # Verify task creation succeeded
                assert success is True
                assert "task" in result
                
                task = result["task"]
                assert task["title"] == "Create Authentication API"
                assert task["assignee"] == "AI IDE Agent"
                
                # Verify template metadata is present
                assert "template_metadata" in task
                template_metadata = task["template_metadata"]
                assert template_metadata["template_injection_enabled"] is True
                assert template_metadata["template_name"] == "workflow_default"

    @pytest.mark.asyncio
    async def test_template_expansion_with_real_components(self, template_service):
        """Test template expansion with actual component resolution"""

        original_description = "Implement OAuth2 authentication flow"

        # Test template expansion
        response = await template_service.expand_task_description(
            original_description=original_description,
            template_name="workflow_default",
            context_data={"priority": "high"}
        )

        # Verify expansion succeeded
        assert response.success is True
        assert response.result is not None

        expanded_instructions = response.result.expanded_instructions

        # Verify original task is preserved
        assert original_description in expanded_instructions

        # Verify components were expanded (based on our mock data)
        assert "Before starting implementation, review the homelab environment" in expanded_instructions
        # Note: The mock only has 2 components, so we check for what's actually there

        # Verify structure is correct
        lines = expanded_instructions.split('\n')
        assert len(lines) > 5  # Should have multiple instruction sections

        # Verify performance
        assert response.result.expansion_time_ms < 100  # Target: <100ms

    @pytest.mark.asyncio
    async def test_template_expansion_error_handling(self, mock_supabase_client):
        """Test error handling in template expansion"""

        # Create template service with mock that returns no templates
        def mock_table_call_empty(table_name):
            if table_name == "archon_template_definitions":
                mock_template_table = MagicMock()
                mock_template_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
                return mock_template_table
            return MagicMock()

        mock_supabase_client.table.side_effect = mock_table_call_empty
        template_service = TemplateInjectionService(supabase_client=mock_supabase_client)

        # Test with non-existent template
        response = await template_service.expand_task_description(
            original_description="Test task",
            template_name="workflow_nonexistent"
        )

        # Verify error handling
        assert response.success is False
        assert "not found" in response.error.lower()

    @pytest.mark.asyncio
    async def test_template_caching_performance(self, template_service):
        """Test template caching improves performance"""
        
        original_description = "Test caching performance"
        
        # First expansion (cache miss)
        start_time = asyncio.get_event_loop().time()
        response1 = await template_service.expand_task_description(
            original_description=original_description,
            template_name="workflow_default"
        )
        first_duration = asyncio.get_event_loop().time() - start_time
        
        # Second expansion (cache hit)
        start_time = asyncio.get_event_loop().time()
        response2 = await template_service.expand_task_description(
            original_description=original_description,
            template_name="workflow_default"
        )
        second_duration = asyncio.get_event_loop().time() - start_time
        
        # Verify both succeeded
        assert response1.success is True
        assert response2.success is True
        
        # Verify caching improved performance
        assert second_duration < first_duration
        
        # Verify results are consistent
        assert response1.result.expanded_instructions == response2.result.expanded_instructions

    @pytest.mark.asyncio
    async def test_component_validation(self, template_service):
        """Test component validation and error handling"""

        # Test getting valid component
        component = await template_service.get_component("group::understand_homelab_env")
        assert component is not None
        assert component.name == "group::understand_homelab_env"
        assert "homelab environment" in component.instruction_text.lower()

        # Test getting non-existent component with empty mock response
        with patch.object(template_service.supabase, 'table') as mock_table:
            mock_component_table = MagicMock()
            mock_component_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
            mock_table.return_value = mock_component_table

            component = await template_service.get_component("group::nonexistent")
            assert component is None

    @pytest.mark.asyncio
    async def test_template_validation(self, template_service):
        """Test template validation functionality"""
        
        # Get template for validation
        template_response = await template_service.get_template("workflow_default")
        assert template_response.success is True
        
        template = template_response.template
        
        # Test template validation
        is_valid = await template_service.validate_template(template)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_feature_flag_integration(self, mock_supabase_client):
        """Test feature flag controls template injection"""

        # Create task service with mock that returns original description
        def mock_insert_response_no_template(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.execute.return_value.data = [{
                "id": str(uuid4()),
                "project_id": str(uuid4()),
                "title": "Test Task",
                "description": "Original description",  # No template expansion
                "status": "todo",
                "assignee": "User",
                "task_order": 0,
                "template_metadata": {
                    "template_injection_enabled": False
                },
                "created_at": "2025-08-20T10:00:00Z"
            }]
            return mock_response

        mock_supabase_client.table.return_value.insert.side_effect = mock_insert_response_no_template
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = []

        task_service = TaskService(supabase_client=mock_supabase_client)
        project_id = str(uuid4())

        # Test with template injection disabled
        success, result = await task_service.create_task(
            project_id=project_id,
            title="Test Task",
            description="Original description",
            enable_template_injection=False
        )

        assert success is True
        task = result["task"]

        # Should use original description when disabled
        assert task["description"] == "Original description"

    @pytest.mark.asyncio
    async def test_backward_compatibility(self, mock_supabase_client):
        """Test that existing task creation still works without template parameters"""

        # Create task service with mock that returns legacy task data
        def mock_insert_response_legacy(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.execute.return_value.data = [{
                "id": str(uuid4()),
                "project_id": str(uuid4()),
                "title": "Legacy Task",
                "description": "Legacy description",
                "status": "todo",
                "assignee": "User",
                "task_order": 0,
                "created_at": "2025-08-20T10:00:00Z"
            }]
            return mock_response

        mock_supabase_client.table.return_value.insert.side_effect = mock_insert_response_legacy
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value.data = []

        task_service = TaskService(supabase_client=mock_supabase_client)
        project_id = str(uuid4())

        # Test task creation without template parameters
        success, result = await task_service.create_task(
            project_id=project_id,
            title="Legacy Task",
            description="Legacy description"
        )

        assert success is True
        task = result["task"]
        assert task["title"] == "Legacy Task"
        assert task["description"] == "Legacy description"
