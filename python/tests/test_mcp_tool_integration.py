"""
Tests for MCP Tool Integration

This module tests the MCP tool integration system including:
- Tool registry and discovery
- Parameter validation and mapping
- Tool execution with error handling
- Workflow integration
- Example workflow validation
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from src.server.services.workflow.mcp_tool_integration import (
    MCPToolRegistry,
    MCPToolExecutor,
    MCPToolMapper,
    MCPWorkflowIntegration,
    get_mcp_workflow_integration
)
from src.server.models.mcp_workflow_examples import (
    create_project_research_workflow,
    create_task_automation_workflow,
    create_health_monitoring_workflow,
    get_mcp_example_workflow,
    list_mcp_example_workflows
)


class TestMCPToolRegistry:
    """Test MCP tool registry functionality"""
    
    def test_get_tool_info_existing(self):
        """Test getting info for existing tool"""
        tool_info = MCPToolRegistry.get_tool_info("perform_rag_query_archon")
        
        assert tool_info is not None
        assert tool_info["category"] == "rag"
        assert "description" in tool_info
        assert "parameters" in tool_info
        assert "query" in tool_info["parameters"]
        assert tool_info["parameters"]["query"]["required"] is True
    
    def test_get_tool_info_nonexistent(self):
        """Test getting info for non-existent tool"""
        tool_info = MCPToolRegistry.get_tool_info("nonexistent_tool")
        assert tool_info is None
    
    def test_list_tools_by_category(self):
        """Test listing tools by category"""
        rag_tools = MCPToolRegistry.list_tools_by_category("rag")
        
        assert len(rag_tools) > 0
        assert "perform_rag_query_archon" in rag_tools
        assert "search_code_examples_archon" in rag_tools
        assert "get_available_sources_archon" in rag_tools
    
    def test_list_tools_by_category_project(self):
        """Test listing project management tools"""
        project_tools = MCPToolRegistry.list_tools_by_category("project")
        
        assert len(project_tools) > 0
        assert "manage_project_archon" in project_tools
        assert "manage_task_archon" in project_tools
        assert "manage_document_archon" in project_tools
    
    def test_validate_tool_exists(self):
        """Test tool existence validation"""
        assert MCPToolRegistry.validate_tool_exists("perform_rag_query_archon") is True
        assert MCPToolRegistry.validate_tool_exists("manage_task_archon") is True
        assert MCPToolRegistry.validate_tool_exists("nonexistent_tool") is False
    
    def test_get_all_categories(self):
        """Test getting all tool categories"""
        categories = MCPToolRegistry.get_all_categories()
        
        assert "rag" in categories
        assert "project" in categories
        assert "system" in categories
        assert len(categories) >= 3


class TestMCPToolExecutor:
    """Test MCP tool executor functionality"""
    
    @pytest.fixture
    def tool_executor(self):
        """Create tool executor for testing"""
        return MCPToolExecutor()
    
    @pytest.mark.asyncio
    @patch('src.server.services.workflow.mcp_tool_integration.get_mcp_client')
    async def test_execute_tool_success(self, mock_get_mcp_client, tool_executor):
        """Test successful tool execution"""
        # Mock MCP client
        mock_mcp_client = Mock()
        mock_mcp_client.call_tool = AsyncMock(return_value={"success": True, "results": []})
        mock_get_mcp_client.return_value = mock_mcp_client
        
        # Execute tool
        success, result = await tool_executor.execute_tool(
            "get_available_sources_archon",
            {}
        )
        
        assert success is True
        assert result["success"] is True
        assert result["tool_name"] == "get_available_sources_archon"
        assert "result" in result
        assert "executed_at" in result
        
        # Verify MCP client was called
        mock_mcp_client.call_tool.assert_called_once_with("get_available_sources_archon")
    
    @pytest.mark.asyncio
    async def test_execute_tool_unknown(self, tool_executor):
        """Test execution of unknown tool"""
        success, result = await tool_executor.execute_tool(
            "unknown_tool",
            {}
        )
        
        assert success is False
        assert "Unknown MCP tool" in result["error"]
        assert "available_tools" in result
    
    @pytest.mark.asyncio
    async def test_execute_tool_validation_error(self, tool_executor):
        """Test tool execution with parameter validation error"""
        # Try to execute tool with missing required parameter
        success, result = await tool_executor.execute_tool(
            "perform_rag_query_archon",
            {}  # Missing required 'query' parameter
        )
        
        assert success is False
        assert "Parameter validation failed" in result["error"]
        assert "validation_errors" in result
        assert any("Missing required parameter: query" in error for error in result["validation_errors"])
    
    def test_validate_parameters_success(self, tool_executor):
        """Test successful parameter validation"""
        tool_info = MCPToolRegistry.get_tool_info("perform_rag_query_archon")
        
        success, result = tool_executor._validate_parameters(
            "perform_rag_query_archon",
            {"query": "test query", "match_count": 5},
            tool_info
        )
        
        assert success is True
        assert "validated successfully" in result["message"]
    
    def test_validate_parameters_missing_required(self, tool_executor):
        """Test parameter validation with missing required parameter"""
        tool_info = MCPToolRegistry.get_tool_info("perform_rag_query_archon")
        
        success, result = tool_executor._validate_parameters(
            "perform_rag_query_archon",
            {"match_count": 5},  # Missing required 'query'
            tool_info
        )
        
        assert success is False
        assert "Parameter validation failed" in result["error"]
        assert "Missing required parameter: query" in result["validation_errors"]
    
    def test_validate_parameters_wrong_type(self, tool_executor):
        """Test parameter validation with wrong parameter type"""
        tool_info = MCPToolRegistry.get_tool_info("perform_rag_query_archon")
        
        success, result = tool_executor._validate_parameters(
            "perform_rag_query_archon",
            {"query": "test", "match_count": "not_an_integer"},
            tool_info
        )
        
        assert success is False
        assert "Parameter validation failed" in result["error"]
        assert any("must be an integer" in error for error in result["validation_errors"])
    
    def test_clean_parameters(self, tool_executor):
        """Test parameter cleaning with defaults"""
        tool_info = MCPToolRegistry.get_tool_info("perform_rag_query_archon")
        
        cleaned = tool_executor._clean_parameters(
            {"query": "test", "match_count": None},
            tool_info
        )
        
        assert cleaned["query"] == "test"
        assert cleaned["match_count"] == 5  # Default value
    
    def test_process_tool_result_json(self, tool_executor):
        """Test processing JSON tool result"""
        result = tool_executor._process_tool_result(
            "test_tool",
            '{"success": true, "data": []}',
            {}
        )
        
        assert result["result_type"] == "json"
        assert "raw_result" in result
        assert "parsed_result" in result
        assert result["parsed_result"]["success"] is True
    
    def test_process_tool_result_string(self, tool_executor):
        """Test processing string tool result"""
        result = tool_executor._process_tool_result(
            "test_tool",
            "simple string result",
            {}
        )
        
        assert result["result_type"] == "string"
        assert result["raw_result"] == "simple string result"


class TestMCPToolMapper:
    """Test MCP tool parameter mapping"""
    
    def test_map_parameters_direct_match(self):
        """Test parameter mapping with direct matches"""
        mapped = MCPToolMapper.map_parameters(
            {"query": "test query", "match_count": 5},
            "perform_rag_query_archon"
        )
        
        assert mapped["query"] == "test query"
        assert mapped["match_count"] == 5
    
    def test_map_parameters_with_defaults(self):
        """Test parameter mapping with default values"""
        mapped = MCPToolMapper.map_parameters(
            {"query": "test query"},
            "perform_rag_query_archon"
        )
        
        assert mapped["query"] == "test query"
        assert mapped["match_count"] == 5  # Default value
    
    def test_map_parameters_unknown_tool(self):
        """Test parameter mapping for unknown tool"""
        original_params = {"param1": "value1", "param2": "value2"}
        mapped = MCPToolMapper.map_parameters(
            original_params,
            "unknown_tool"
        )
        
        # Should return original parameters unchanged
        assert mapped == original_params
    
    def test_find_parameter_alias(self):
        """Test parameter alias finding"""
        tool_params = {"task_id": {}, "project_id": {}, "title": {}}
        
        # Test direct match
        assert MCPToolMapper._find_parameter_alias("task_id", tool_params) == "task_id"
        
        # Test alias match
        assert MCPToolMapper._find_parameter_alias("id", tool_params) == "task_id"
        
        # Test no match
        assert MCPToolMapper._find_parameter_alias("unknown_param", tool_params) is None


class TestMCPWorkflowIntegration:
    """Test high-level MCP workflow integration"""
    
    @pytest.fixture
    def integration(self):
        """Create MCP workflow integration for testing"""
        return MCPWorkflowIntegration()
    
    @pytest.mark.asyncio
    @patch('src.server.services.workflow.mcp_tool_integration.get_mcp_client')
    async def test_execute_workflow_step_success(self, mock_get_mcp_client, integration):
        """Test successful workflow step execution"""
        # Mock MCP client
        mock_mcp_client = Mock()
        mock_mcp_client.call_tool = AsyncMock(return_value={"sources": ["source1", "source2"]})
        mock_get_mcp_client.return_value = mock_mcp_client
        
        success, result = await integration.execute_workflow_step(
            "get_available_sources_archon",
            {},
            {"workflow": {"parameters": {}}},
            {"execution_id": str(uuid4())}
        )
        
        assert success is True
        assert result["success"] is True
        assert result["tool_name"] == "get_available_sources_archon"
        assert "tool_result" in result
        assert "execution_info" in result
    
    @pytest.mark.asyncio
    async def test_execute_workflow_step_failure(self, integration):
        """Test workflow step execution failure"""
        success, result = await integration.execute_workflow_step(
            "unknown_tool",
            {},
            {},
            {}
        )
        
        assert success is False
        assert result["success"] is False
        assert "error" in result
    
    def test_get_tool_suggestions(self, integration):
        """Test tool suggestions based on description"""
        suggestions = integration.get_tool_suggestions("search for code examples")
        
        assert len(suggestions) > 0
        # Should suggest code search tools
        tool_names = [s["tool_name"] for s in suggestions]
        assert any("search_code_examples" in name for name in tool_names)
    
    def test_get_tool_suggestions_rag(self, integration):
        """Test tool suggestions for RAG queries"""
        suggestions = integration.get_tool_suggestions("query knowledge base for information")
        
        assert len(suggestions) > 0
        tool_names = [s["tool_name"] for s in suggestions]
        assert any("perform_rag_query" in name for name in tool_names)
    
    def test_validate_workflow_tools_valid(self, integration):
        """Test workflow tool validation with valid tools"""
        workflow_steps = [
            {
                "name": "step1",
                "type": "action",
                "tool_name": "perform_rag_query_archon",
                "parameters": {"query": "test"}
            },
            {
                "name": "step2",
                "type": "action",
                "tool_name": "manage_task_archon",
                "parameters": {"action": "create", "project_id": "uuid"}
            }
        ]
        
        result = integration.validate_workflow_tools(workflow_steps)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert "rag" in result["tool_summary"]
        assert "project" in result["tool_summary"]
    
    def test_validate_workflow_tools_invalid(self, integration):
        """Test workflow tool validation with invalid tools"""
        workflow_steps = [
            {
                "name": "step1",
                "type": "action",
                "tool_name": "unknown_tool",
                "parameters": {}
            }
        ]
        
        result = integration.validate_workflow_tools(workflow_steps)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "Unknown tool 'unknown_tool'" in result["errors"][0]


class TestMCPExampleWorkflows:
    """Test MCP example workflows"""
    
    def test_create_project_research_workflow(self):
        """Test project research workflow creation"""
        workflow = create_project_research_workflow()
        
        assert workflow.name == "project_research_workflow"
        assert workflow.category == "research"
        assert len(workflow.steps) > 0
        
        # Check that it uses MCP tools
        action_steps = [step for step in workflow.steps if hasattr(step, 'tool_name')]
        assert len(action_steps) > 0
        
        # Verify it uses actual MCP tools
        for step in action_steps:
            assert MCPToolRegistry.validate_tool_exists(step.tool_name)
    
    def test_create_task_automation_workflow(self):
        """Test task automation workflow creation"""
        workflow = create_task_automation_workflow()
        
        assert workflow.name == "task_automation_workflow"
        assert workflow.category == "project_management"
        assert len(workflow.steps) > 0
        
        # Should use task management tools
        action_steps = [step for step in workflow.steps if hasattr(step, 'tool_name')]
        tool_names = [step.tool_name for step in action_steps]
        assert "manage_task_archon" in tool_names
    
    def test_create_health_monitoring_workflow(self):
        """Test health monitoring workflow creation"""
        workflow = create_health_monitoring_workflow()
        
        assert workflow.name == "health_monitoring_workflow"
        assert workflow.category == "monitoring"
        assert len(workflow.steps) > 0
        
        # Should use health check tools
        action_steps = [step for step in workflow.steps if hasattr(step, 'tool_name')]
        tool_names = [step.tool_name for step in action_steps]
        assert "health_check_archon" in tool_names
        assert "session_info_archon" in tool_names
    
    def test_get_mcp_example_workflow(self):
        """Test getting specific example workflow"""
        workflow = get_mcp_example_workflow("project_research_workflow")
        assert workflow.name == "project_research_workflow"
        
        with pytest.raises(KeyError):
            get_mcp_example_workflow("nonexistent_workflow")
    
    def test_list_mcp_example_workflows(self):
        """Test listing example workflows"""
        workflows = list_mcp_example_workflows()
        
        assert len(workflows) >= 3
        assert "project_research_workflow" in workflows
        assert "task_automation_workflow" in workflows
        assert "health_monitoring_workflow" in workflows
    
    def test_validate_all_example_workflows(self):
        """Test that all example workflows use valid MCP tools"""
        integration = MCPWorkflowIntegration()
        
        for workflow_name in list_mcp_example_workflows():
            workflow = get_mcp_example_workflow(workflow_name)
            
            # Convert workflow steps to validation format
            workflow_steps = []
            for step in workflow.steps:
                if hasattr(step, 'tool_name'):
                    workflow_steps.append({
                        "name": step.name,
                        "type": "action",
                        "tool_name": step.tool_name,
                        "parameters": step.parameters
                    })
            
            if workflow_steps:  # Only validate if there are action steps
                result = integration.validate_workflow_tools(workflow_steps)
                assert result["valid"] is True, f"Workflow {workflow_name} has invalid tools: {result['errors']}"


class TestGlobalIntegration:
    """Test global integration instance"""
    
    def test_get_mcp_workflow_integration_singleton(self):
        """Test that global integration returns singleton"""
        integration1 = get_mcp_workflow_integration()
        integration2 = get_mcp_workflow_integration()
        
        assert integration1 is integration2
        assert isinstance(integration1, MCPWorkflowIntegration)


if __name__ == "__main__":
    pytest.main([__file__])
