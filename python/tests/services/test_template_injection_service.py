"""
Tests for TemplateInjectionService

Comprehensive test suite for template expansion, caching, and error handling.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from src.server.services.template_injection_service import (
    TemplateInjectionService,
    TemplateNotFoundError,
    ComponentNotFoundError,
    TemplateExpansionError,
    get_template_injection_service
)
from src.server.models.template_injection_models import (
    TemplateDefinition,
    TemplateComponent,
    TemplateDefinitionType,
    TemplateComponentType,
    TemplateExpansionResult
)


class TestTemplateInjectionService:
    """Test TemplateInjectionService functionality"""

    @pytest.fixture
    def mock_supabase_client(self):
        """Create mock Supabase client"""
        mock_client = Mock()
        mock_client.table.return_value = mock_client
        mock_client.select.return_value = mock_client
        mock_client.eq.return_value = mock_client
        mock_client.execute.return_value = Mock(data=[])
        return mock_client

    @pytest.fixture
    def mock_threading_service(self):
        """Create mock threading service"""
        mock_service = Mock()
        mock_service.run_io_bound = AsyncMock()
        return mock_service

    @pytest.fixture
    def service(self, mock_supabase_client, mock_threading_service):
        """Create TemplateInjectionService instance with mocked dependencies"""
        with patch('src.server.services.template_injection_service.get_supabase_client', return_value=mock_supabase_client):
            with patch('src.server.services.template_injection_service.get_threading_service', return_value=mock_threading_service):
                service = TemplateInjectionService(mock_supabase_client)
                # Configure the mock to return the operation result directly
                mock_threading_service.run_io_bound.side_effect = lambda op: op()
                return service

    @pytest.fixture
    def sample_template(self):
        """Create sample template definition"""
        return TemplateDefinition(
            id=uuid4(),
            name="workflow_default",
            title="Default Workflow Template",
            template_type=TemplateDefinitionType.PROJECT,
            template_data={
                "template_content": "{{group::understand_homelab_env}}\n\n{{group::guidelines_coding}}\n\n{{USER_TASK}}\n\n{{group::create_tests}}",
                "user_task_position": 3,
                "estimated_duration": 45,
                "required_tools": ["view", "str-replace-editor"]
            },
            created_by="test-user"
        )

    @pytest.fixture
    def sample_component(self):
        """Create sample template component"""
        return TemplateComponent(
            id=uuid4(),
            name="group::understand_homelab_env",
            component_type=TemplateComponentType.GROUP,
            instruction_text="Review homelab environment and available services before starting implementation.",
            estimated_duration=8,
            category="preparation"
        )

    @pytest.mark.asyncio
    async def test_expand_task_description_success(self, service, sample_template, sample_component):
        """Test successful task description expansion"""
        # Mock template retrieval
        service.get_template = AsyncMock(return_value=Mock(
            success=True,
            template=sample_template
        ))
        
        # Mock component retrieval
        service.get_component = AsyncMock(return_value=sample_component)
        
        # Test expansion
        result = await service.expand_task_description(
            original_description="Implement OAuth2 authentication",
            template_name="workflow_default"
        )
        
        assert result.success is True
        assert result.result is not None
        assert result.result.original_task == "Implement OAuth2 authentication"
        assert "Implement OAuth2 authentication" in result.result.expanded_instructions
        assert "Review homelab environment" in result.result.expanded_instructions
        assert result.result.template_name == "workflow_default"
        assert result.result.expansion_time_ms >= 0

    @pytest.mark.asyncio
    async def test_expand_task_description_template_not_found(self, service):
        """Test expansion with non-existent template"""
        # Mock template not found
        service.get_template = AsyncMock(return_value=Mock(
            success=False,
            template=None
        ))
        
        result = await service.expand_task_description(
            original_description="Test task",
            template_name="non_existent_template"
        )
        
        assert result.success is False
        assert "not found" in result.error

    @pytest.mark.asyncio
    async def test_expand_task_description_caching(self, service, sample_template, sample_component):
        """Test that expansion results are cached"""
        # Mock template and component retrieval
        service.get_template = AsyncMock(return_value=Mock(
            success=True,
            template=sample_template
        ))
        service.get_component = AsyncMock(return_value=sample_component)
        
        # First call
        result1 = await service.expand_task_description(
            original_description="Test task",
            template_name="workflow_default"
        )
        
        # Second call with same parameters
        result2 = await service.expand_task_description(
            original_description="Test task",
            template_name="workflow_default"
        )
        
        assert result1.success is True
        assert result2.success is True
        assert result2.message.endswith("(cached)")

    @pytest.mark.asyncio
    async def test_get_template_success(self, service, mock_supabase_client, sample_template):
        """Test successful template retrieval"""
        # Mock database response
        mock_supabase_client.execute.return_value = Mock(data=[sample_template.model_dump()])
        
        result = await service.get_template("workflow_default")
        
        assert result.success is True
        assert result.template is not None
        assert result.template.name == "workflow_default"

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, service, mock_supabase_client):
        """Test template retrieval when template doesn't exist"""
        # Mock empty database response
        mock_supabase_client.execute.return_value = Mock(data=[])
        
        result = await service.get_template("non_existent")
        
        assert result.success is False
        assert "not found" in result.error

    @pytest.mark.asyncio
    async def test_get_template_caching(self, service, mock_supabase_client, sample_template):
        """Test that templates are cached"""
        # Mock database response
        mock_supabase_client.execute.return_value = Mock(data=[sample_template.model_dump()])
        
        # First call
        result1 = await service.get_template("workflow_default")
        
        # Second call should use cache
        result2 = await service.get_template("workflow_default")
        
        assert result1.success is True
        assert result2.success is True
        # Database should only be called once
        assert mock_supabase_client.execute.call_count == 1

    @pytest.mark.asyncio
    async def test_get_component_success(self, service, mock_supabase_client, sample_component):
        """Test successful component retrieval"""
        # Mock database response
        mock_supabase_client.execute.return_value = Mock(data=[sample_component.model_dump()])
        
        result = await service.get_component("group::understand_homelab_env")
        
        assert result is not None
        assert result.name == "group::understand_homelab_env"

    @pytest.mark.asyncio
    async def test_get_component_not_found(self, service, mock_supabase_client):
        """Test component retrieval when component doesn't exist"""
        # Mock empty database response
        mock_supabase_client.execute.return_value = Mock(data=[])
        
        result = await service.get_component("non_existent")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_expand_placeholders_success(self, service, sample_component):
        """Test successful placeholder expansion"""
        # Mock component retrieval
        service.get_component = AsyncMock(return_value=sample_component)
        
        template_content = "{{group::understand_homelab_env}}\n\n{{USER_TASK}}\n\nNext steps..."
        
        result = await service.expand_placeholders(template_content, {})
        
        assert "Review homelab environment" in result
        assert "{{USER_TASK}}" in result  # Should remain unexpanded
        assert "Next steps..." in result

    @pytest.mark.asyncio
    async def test_expand_placeholders_missing_component(self, service):
        """Test placeholder expansion with missing component"""
        # Mock component not found
        service.get_component = AsyncMock(return_value=None)
        
        template_content = "{{group::missing_component}}\n\n{{USER_TASK}}"
        
        result = await service.expand_placeholders(template_content, {})
        
        # Should leave placeholder as-is when component not found
        assert "{{group::missing_component}}" in result
        assert "{{USER_TASK}}" in result

    def test_insert_user_task(self, service):
        """Test user task insertion"""
        template_content = "Step 1: Prepare\n\n{{USER_TASK}}\n\nStep 3: Validate"
        user_task = "Implement OAuth2 authentication"
        
        result = service._insert_user_task(template_content, user_task, 2)
        
        assert "Implement OAuth2 authentication" in result
        assert "{{USER_TASK}}" not in result
        assert "Step 1: Prepare" in result
        assert "Step 3: Validate" in result

    @pytest.mark.asyncio
    async def test_validate_template_success(self, service, sample_template, sample_component):
        """Test successful template validation"""
        # Mock component retrieval
        service.get_component = AsyncMock(return_value=sample_component)
        
        result = await service.validate_template(sample_template)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_template_missing_user_task(self, service):
        """Test template validation with missing USER_TASK placeholder"""
        template = TemplateDefinition(
            name="invalid_template",
            title="Invalid Template",
            template_type=TemplateDefinitionType.PROJECT,
            template_data={
                "template_content": "{{group::test}}\n\nNo user task placeholder"
            },
            created_by="test-user"
        )
        
        result = await service.validate_template(template)
        
        assert result is False

    def test_cache_operations(self, service):
        """Test cache operations"""
        # Test cache stats
        stats = service.get_cache_stats()
        assert "template_cache_size" in stats
        assert "component_cache_size" in stats
        assert "expansion_cache_size" in stats
        
        # Test cache clearing
        service.clear_cache()
        stats_after_clear = service.get_cache_stats()
        assert stats_after_clear["template_cache_size"] == 0
        assert stats_after_clear["component_cache_size"] == 0
        assert stats_after_clear["expansion_cache_size"] == 0

    def test_singleton_service(self):
        """Test singleton service getter"""
        with patch('src.server.services.template_injection_service.get_supabase_client'):
            with patch('src.server.services.template_injection_service.get_threading_service'):
                service1 = get_template_injection_service()
                service2 = get_template_injection_service()
                
                assert service1 is service2
