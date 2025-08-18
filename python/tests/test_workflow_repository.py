"""
Tests for Workflow Repository

This module tests the workflow repository data access layer including:
- CRUD operations for workflow templates
- Workflow execution management
- Step execution tracking
- Version management
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from src.server.services.workflow.workflow_repository import WorkflowRepository
from src.server.models.workflow_models import (
    WorkflowStatus,
    WorkflowExecutionStatus,
    StepExecutionStatus,
    WorkflowStepType
)


class TestWorkflowRepository:
    """Test workflow repository operations"""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Create a mock Supabase client"""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        return mock_client
    
    @pytest.fixture
    def workflow_repository(self, mock_supabase_client):
        """Create workflow repository with mock client"""
        return WorkflowRepository(supabase_client=mock_supabase_client)
    
    @pytest.fixture
    def sample_template_data(self):
        """Sample workflow template data"""
        return {
            "name": "test_workflow",
            "title": "Test Workflow",
            "description": "A test workflow",
            "steps": [
                {
                    "name": "step1",
                    "title": "Step 1",
                    "type": "action",
                    "tool_name": "test_tool",
                    "parameters": {"param1": "value1"}
                }
            ],
            "parameters": {"input_param": {"type": "string", "required": True}},
            "category": "testing"
        }
    
    @pytest.fixture
    def sample_execution_data(self):
        """Sample workflow execution data"""
        return {
            "workflow_template_id": str(uuid4()),
            "triggered_by": "test_user",
            "input_parameters": {"input_param": "test_value"},
            "total_steps": 1
        }
    
    @pytest.fixture
    def sample_step_data(self):
        """Sample step execution data"""
        return {
            "workflow_execution_id": str(uuid4()),
            "step_index": 0,
            "step_name": "step1",
            "step_type": "action",
            "step_config": {"tool_name": "test_tool"},
            "tool_name": "test_tool",
            "tool_parameters": {"param1": "value1"}
        }


class TestWorkflowTemplateOperations:
    """Test workflow template CRUD operations"""
    
    @pytest.mark.asyncio
    async def test_create_workflow_template_success(self, workflow_repository, sample_template_data):
        """Test successful workflow template creation"""
        # Mock successful database response
        mock_response = Mock()
        mock_response.data = [{
            "id": str(uuid4()),
            "name": "test_workflow",
            "title": "Test Workflow",
            "description": "A test workflow",
            "version": "1.0.0",
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **sample_template_data
        }]
        
        workflow_repository.supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        # Mock version creation
        with patch.object(workflow_repository, '_create_template_version', return_value=True):
            success, result = await workflow_repository.create_workflow_template(sample_template_data)
        
        assert success is True
        assert "template" in result
        assert result["template"]["name"] == "test_workflow"
        
        # Verify database call
        workflow_repository.supabase_client.table.assert_called_with("archon_workflow_templates")
    
    @pytest.mark.asyncio
    async def test_create_workflow_template_validation_error(self, workflow_repository):
        """Test workflow template creation with validation error"""
        invalid_data = {
            "name": "test workflow!",  # Invalid name with special characters
            "title": "Test Workflow",
            "steps": []  # Empty steps
        }
        
        success, result = await workflow_repository.create_workflow_template(invalid_data)
        
        assert success is False
        assert "error" in result
    
    def test_list_workflow_templates_success(self, workflow_repository):
        """Test successful workflow template listing"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "name": "workflow1",
                "title": "Workflow 1",
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid4()),
                "name": "workflow2", 
                "title": "Workflow 2",
                "status": "draft",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        # Setup mock chain
        mock_table = workflow_repository.supabase_client.table.return_value
        mock_table.select.return_value.order.return_value.range.return_value.execute.return_value = mock_response
        
        success, result = workflow_repository.list_workflow_templates()
        
        assert success is True
        assert "templates" in result
        assert len(result["templates"]) == 2
        assert result["count"] == 2
    
    def test_list_workflow_templates_with_filters(self, workflow_repository):
        """Test workflow template listing with filters"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = []
        
        # Setup mock chain
        mock_table = workflow_repository.supabase_client.table.return_value
        mock_select = mock_table.select.return_value
        mock_eq = mock_select.eq.return_value
        mock_eq.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_response
        
        success, result = workflow_repository.list_workflow_templates(
            status="active",
            category="testing"
        )
        
        assert success is True
        assert "templates" in result
        
        # Verify filters were applied
        mock_select.eq.assert_called()
    
    def test_get_workflow_template_success(self, workflow_repository):
        """Test successful workflow template retrieval"""
        template_id = str(uuid4())
        
        # Mock database response
        mock_response = Mock()
        mock_response.data = [{
            "id": template_id,
            "name": "test_workflow",
            "title": "Test Workflow",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }]
        
        # Setup mock chain
        mock_table = workflow_repository.supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
        
        success, result = workflow_repository.get_workflow_template(template_id)
        
        assert success is True
        assert "template" in result
        assert result["template"]["id"] == template_id
    
    def test_get_workflow_template_not_found(self, workflow_repository):
        """Test workflow template retrieval when not found"""
        template_id = str(uuid4())
        
        # Mock empty database response
        mock_response = Mock()
        mock_response.data = []
        
        # Setup mock chain
        mock_table = workflow_repository.supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_response
        
        success, result = workflow_repository.get_workflow_template(template_id)
        
        assert success is False
        assert "error" in result
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_update_workflow_template_success(self, workflow_repository):
        """Test successful workflow template update"""
        template_id = str(uuid4())
        
        # Mock get_workflow_template call
        with patch.object(workflow_repository, 'get_workflow_template') as mock_get:
            mock_get.return_value = (True, {
                "template": {
                    "id": template_id,
                    "name": "test_workflow",
                    "title": "Old Title",
                    "steps": []
                }
            })
            
            # Mock database update response
            mock_response = Mock()
            mock_response.data = [{
                "id": template_id,
                "title": "New Title",
                "updated_at": datetime.now().isoformat()
            }]
            
            # Setup mock chain
            mock_table = workflow_repository.supabase_client.table.return_value
            mock_table.update.return_value.eq.return_value.execute.return_value = mock_response
            
            # Mock version creation
            with patch.object(workflow_repository, '_create_template_version', return_value=True):
                with patch.object(workflow_repository, '_should_create_version', return_value=True):
                    success, result = await workflow_repository.update_workflow_template(
                        template_id, 
                        {"title": "New Title"}
                    )
        
        assert success is True
        assert "template" in result
    
    def test_delete_workflow_template_success(self, workflow_repository):
        """Test successful workflow template deletion"""
        template_id = str(uuid4())
        
        # Mock get_workflow_template call
        with patch.object(workflow_repository, 'get_workflow_template') as mock_get:
            mock_get.return_value = (True, {"template": {"id": template_id}})
            
            # Mock database delete response
            mock_response = Mock()
            mock_response.data = [{"id": template_id}]
            
            # Setup mock chain
            mock_table = workflow_repository.supabase_client.table.return_value
            mock_table.delete.return_value.eq.return_value.execute.return_value = mock_response
            
            success, result = workflow_repository.delete_workflow_template(template_id)
        
        assert success is True
        assert "message" in result


class TestWorkflowExecutionOperations:
    """Test workflow execution operations"""
    
    @pytest.mark.asyncio
    async def test_create_workflow_execution_success(self, workflow_repository, sample_execution_data):
        """Test successful workflow execution creation"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = [{
            "id": str(uuid4()),
            "status": "pending",
            "current_step_index": 0,
            "progress_percentage": 0.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **sample_execution_data
        }]
        
        workflow_repository.supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        success, result = await workflow_repository.create_workflow_execution(sample_execution_data)
        
        assert success is True
        assert "execution" in result
        assert result["execution"]["status"] == "pending"
        
        # Verify database call
        workflow_repository.supabase_client.table.assert_called_with("archon_workflow_executions")
    
    def test_list_workflow_executions_success(self, workflow_repository):
        """Test successful workflow execution listing"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "status": "running",
                "triggered_by": "user1",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        # Setup mock chain
        mock_table = workflow_repository.supabase_client.table.return_value
        mock_table.select.return_value.order.return_value.range.return_value.execute.return_value = mock_response
        
        success, result = workflow_repository.list_workflow_executions()
        
        assert success is True
        assert "executions" in result
        assert len(result["executions"]) == 1
    
    @pytest.mark.asyncio
    async def test_update_workflow_execution_success(self, workflow_repository):
        """Test successful workflow execution update"""
        execution_id = str(uuid4())
        
        # Mock database response
        mock_response = Mock()
        mock_response.data = [{
            "id": execution_id,
            "status": "completed",
            "progress_percentage": 100.0,
            "updated_at": datetime.now().isoformat()
        }]
        
        # Setup mock chain
        mock_table = workflow_repository.supabase_client.table.return_value
        mock_table.update.return_value.eq.return_value.execute.return_value = mock_response
        
        success, result = await workflow_repository.update_workflow_execution(
            execution_id,
            {"status": WorkflowExecutionStatus.COMPLETED, "progress_percentage": 100.0}
        )
        
        assert success is True
        assert "execution" in result
        assert result["execution"]["status"] == "completed"


class TestStepExecutionOperations:
    """Test step execution operations"""
    
    @pytest.mark.asyncio
    async def test_create_step_execution_success(self, workflow_repository, sample_step_data):
        """Test successful step execution creation"""
        # Mock database response
        mock_response = Mock()
        mock_response.data = [{
            "id": str(uuid4()),
            "status": "pending",
            "attempt_number": 1,
            "max_attempts": 1,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **sample_step_data
        }]
        
        workflow_repository.supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        success, result = await workflow_repository.create_step_execution(sample_step_data)
        
        assert success is True
        assert "step_execution" in result
        assert result["step_execution"]["status"] == "pending"
        
        # Verify database call
        workflow_repository.supabase_client.table.assert_called_with("archon_workflow_step_executions")
    
    def test_list_step_executions_success(self, workflow_repository):
        """Test successful step execution listing"""
        execution_id = str(uuid4())
        
        # Mock database response
        mock_response = Mock()
        mock_response.data = [
            {
                "id": str(uuid4()),
                "workflow_execution_id": execution_id,
                "step_index": 0,
                "step_name": "step1",
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        # Setup mock chain
        mock_table = workflow_repository.supabase_client.table.return_value
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        success, result = workflow_repository.list_step_executions(execution_id)
        
        assert success is True
        assert "step_executions" in result
        assert len(result["step_executions"]) == 1


class TestHelperMethods:
    """Test repository helper methods"""
    
    def test_format_template_response(self, workflow_repository):
        """Test template response formatting"""
        template_data = {
            "id": str(uuid4()),
            "name": "test_workflow",
            "title": "Test Workflow",
            "description": "Test description",
            "version": "1.0.0",
            "status": "active",
            "timeout_minutes": 60,
            "max_retries": 3,
            "created_by": "test_user",
            "is_public": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        formatted = workflow_repository._format_template_response(template_data)
        
        assert formatted["id"] == template_data["id"]
        assert formatted["name"] == template_data["name"]
        assert formatted["title"] == template_data["title"]
        assert "tags" in formatted  # Should have default empty list
        assert "parameters" in formatted  # Should have default empty dict
    
    def test_should_create_version(self, workflow_repository):
        """Test version creation logic"""
        old_template = {
            "steps": [{"name": "step1", "type": "action"}],
            "parameters": {"param1": "value1"},
            "status": "draft"
        }
        
        # Test with significant change (steps modified)
        new_template_significant = {
            "steps": [{"name": "step1", "type": "action"}, {"name": "step2", "type": "action"}],
            "parameters": {"param1": "value1"},
            "status": "draft"
        }
        
        assert workflow_repository._should_create_version(old_template, new_template_significant) is True
        
        # Test with non-significant change (title modified)
        new_template_minor = {
            "steps": [{"name": "step1", "type": "action"}],
            "parameters": {"param1": "value1"},
            "status": "draft",
            "title": "New Title"  # Non-significant field
        }
        
        assert workflow_repository._should_create_version(old_template, new_template_minor) is False


if __name__ == "__main__":
    pytest.main([__file__])
