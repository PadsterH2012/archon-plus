"""
Tests for Template Injection MCP Tools

Test suite for template injection MCP tools functionality.
"""

import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from src.mcp.modules.template_injection_module import register_template_injection_tools


class TestTemplateInjectionMCPTools:
    """Test Template Injection MCP tools"""

    @pytest.fixture
    def mock_mcp(self):
        """Create mock FastMCP instance"""
        mock_mcp = Mock()
        mock_mcp.tool = Mock()
        return mock_mcp

    @pytest.fixture
    def mock_context(self):
        """Create mock MCP context"""
        return Mock()

    @pytest.fixture
    def sample_template_data(self):
        """Create sample template data"""
        return {
            "template_content": "{{group::understand_homelab_env}}\n\n{{USER_TASK}}\n\n{{group::send_task_to_review}}",
            "user_task_position": 2,
            "estimated_duration": 30,
            "required_tools": ["view", "manage_task_archon-prod"],
            "version": "1.0.0"
        }

    @pytest.fixture
    def sample_component_data(self):
        """Create sample component data"""
        return {
            "name": "group::test_component",
            "description": "Test component for validation",
            "component_type": "group",
            "instruction_text": "This is a test component instruction",
            "required_tools": ["view", "str-replace-editor"],
            "estimated_duration": 5,
            "category": "testing",
            "priority": "medium",
            "tags": ["test", "validation"]
        }

    def test_register_template_injection_tools(self, mock_mcp):
        """Test that template injection tools are registered correctly"""
        register_template_injection_tools(mock_mcp)

        # Verify that tools were registered
        assert mock_mcp.tool.call_count == 3

        # Just verify that the registration function was called the expected number of times
        # The actual tool registration is handled by the FastMCP framework
        assert mock_mcp.tool.call_count == 3

    @pytest.mark.asyncio
    async def test_manage_template_injection_create_success(self, mock_mcp, mock_context, sample_template_data):
        """Test successful template creation"""
        # Register tools to get the actual function
        register_template_injection_tools(mock_mcp)
        manage_template_injection = None
        
        for call in mock_mcp.tool.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__') and 'manage_template_injection' in call[0][0].__name__:
                manage_template_injection = call[0][0]
                break
        
        assert manage_template_injection is not None, "manage_template_injection tool not found"

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "template": {
                "id": str(uuid4()),
                "name": "test_template",
                "title": "Test Template",
                "template_data": sample_template_data
            },
            "message": "Template created successfully"
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await manage_template_injection(
                ctx=mock_context,
                action="create",
                name="test_template",
                title="Test Template",
                description="Test template description",
                template_type="project",
                template_data=sample_template_data
            )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "template" in result_data
        assert result_data["template"]["name"] == "test_template"

    @pytest.mark.asyncio
    async def test_manage_template_injection_create_missing_name(self, mock_mcp, mock_context):
        """Test template creation with missing name"""
        register_template_injection_tools(mock_mcp)
        manage_template_injection = None
        
        for call in mock_mcp.tool.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__') and 'manage_template_injection' in call[0][0].__name__:
                manage_template_injection = call[0][0]
                break

        result = await manage_template_injection(
            ctx=mock_context,
            action="create",
            title="Test Template",
            template_data={"test": "data"}
        )

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "name is required" in result_data["error"]

    @pytest.mark.asyncio
    async def test_manage_template_injection_list_success(self, mock_mcp, mock_context):
        """Test successful template listing"""
        register_template_injection_tools(mock_mcp)
        manage_template_injection = None
        
        for call in mock_mcp.tool.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__') and 'manage_template_injection' in call[0][0].__name__:
                manage_template_injection = call[0][0]
                break

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "templates": [
                {"id": str(uuid4()), "name": "template1", "title": "Template 1"},
                {"id": str(uuid4()), "name": "template2", "title": "Template 2"}
            ],
            "pagination": {"total": 2, "page": 1, "per_page": 50}
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await manage_template_injection(
                ctx=mock_context,
                action="list"
            )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "templates" in result_data
        assert len(result_data["templates"]) == 2

    @pytest.mark.asyncio
    async def test_expand_template_preview_success(self, mock_mcp, mock_context):
        """Test successful template expansion preview"""
        register_template_injection_tools(mock_mcp)
        expand_template_preview = None
        
        for call in mock_mcp.tool.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__') and 'expand_template_preview' in call[0][0].__name__:
                expand_template_preview = call[0][0]
                break

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "expansion": {
                "original_task": "Implement OAuth2 authentication",
                "expanded_instructions": "Step 1: Review homelab environment\n\nImplement OAuth2 authentication\n\nStep 3: Send task to review",
                "template_name": "workflow_default",
                "expansion_time_ms": 25
            },
            "message": "Template expansion preview completed"
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await expand_template_preview(
                ctx=mock_context,
                original_description="Implement OAuth2 authentication",
                template_name="workflow_default"
            )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "expansion" in result_data
        assert result_data["expansion"]["original_task"] == "Implement OAuth2 authentication"

    @pytest.mark.asyncio
    async def test_expand_template_preview_missing_description(self, mock_mcp, mock_context):
        """Test template expansion preview with missing description"""
        register_template_injection_tools(mock_mcp)
        expand_template_preview = None
        
        for call in mock_mcp.tool.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__') and 'expand_template_preview' in call[0][0].__name__:
                expand_template_preview = call[0][0]
                break

        result = await expand_template_preview(
            ctx=mock_context,
            original_description="",
            template_name="workflow_default"
        )

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "original_description is required" in result_data["error"]

    @pytest.mark.asyncio
    async def test_manage_template_components_create_success(self, mock_mcp, mock_context, sample_component_data):
        """Test successful component creation"""
        register_template_injection_tools(mock_mcp)
        manage_template_components = None
        
        for call in mock_mcp.tool.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__') and 'manage_template_components' in call[0][0].__name__:
                manage_template_components = call[0][0]
                break

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "component": {
                "id": str(uuid4()),
                **sample_component_data
            },
            "message": "Component created successfully"
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await manage_template_components(
                ctx=mock_context,
                action="create",
                **sample_component_data
            )

        result_data = json.loads(result)
        assert result_data["success"] is True
        assert "component" in result_data
        assert result_data["component"]["name"] == sample_component_data["name"]

    @pytest.mark.asyncio
    async def test_manage_template_components_invalid_action(self, mock_mcp, mock_context):
        """Test component management with invalid action"""
        register_template_injection_tools(mock_mcp)
        manage_template_components = None
        
        for call in mock_mcp.tool.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__') and 'manage_template_components' in call[0][0].__name__:
                manage_template_components = call[0][0]
                break

        result = await manage_template_components(
            ctx=mock_context,
            action="invalid_action"
        )

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "not yet implemented" in result_data["error"]

    @pytest.mark.asyncio
    async def test_http_error_handling(self, mock_mcp, mock_context):
        """Test HTTP error handling in MCP tools"""
        register_template_injection_tools(mock_mcp)
        manage_template_injection = None
        
        for call in mock_mcp.tool.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__') and 'manage_template_injection' in call[0][0].__name__:
                manage_template_injection = call[0][0]
                break

        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            result = await manage_template_injection(
                ctx=mock_context,
                action="create",
                name="test_template",
                title="Test Template",
                template_data={"test": "data"}
            )

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "Failed to create template" in result_data["error"]

    @pytest.mark.asyncio
    async def test_exception_handling(self, mock_mcp, mock_context):
        """Test exception handling in MCP tools"""
        register_template_injection_tools(mock_mcp)
        manage_template_injection = None
        
        for call in mock_mcp.tool.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__') and 'manage_template_injection' in call[0][0].__name__:
                manage_template_injection = call[0][0]
                break

        # Mock exception during HTTP call
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.side_effect = Exception("Connection error")
            
            result = await manage_template_injection(
                ctx=mock_context,
                action="create",
                name="test_template",
                title="Test Template",
                template_data={"test": "data"}
            )

        result_data = json.loads(result)
        assert result_data["success"] is False
        assert "Connection error" in result_data["error"]
