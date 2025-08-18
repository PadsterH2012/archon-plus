"""
Tests for Workflow API endpoints

This module tests the workflow API endpoints including:
- Workflow template CRUD operations
- Workflow execution management
- Search and discovery functionality
- Validation endpoints
- Error handling
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient

from src.server.main import app
from src.server.models.workflow_models import WorkflowStatus, WorkflowExecutionStatus


class TestWorkflowAPI:
    """Test workflow API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_workflow_data(self):
        """Sample workflow data for testing"""
        return {
            "name": "test_workflow",
            "title": "Test Workflow",
            "description": "A test workflow for API testing",
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
            "category": "testing",
            "tags": ["test", "api"]
        }
    
    @pytest.fixture
    def sample_execution_data(self):
        """Sample execution data for testing"""
        return {
            "workflow_template_id": str(uuid4()),
            "triggered_by": "test_user",
            "input_parameters": {"input_param": "test_value"},
            "trigger_context": {"source": "api_test"}
        }


class TestWorkflowTemplateEndpoints:
    """Test workflow template CRUD endpoints"""
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_list_workflows_success(self, mock_repo_class, client):
        """Test successful workflow listing"""
        # Mock repository response
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.list_workflow_templates.return_value = (True, {
            "templates": [
                {
                    "id": str(uuid4()),
                    "name": "workflow1",
                    "title": "Workflow 1",
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
            ],
            "count": 1
        })
        
        response = client.get("/api/workflows")
        
        assert response.status_code == 200
        data = response.json()
        assert "workflows" in data
        assert data["total_count"] == 1
        assert data["page"] == 1
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_list_workflows_with_filters(self, mock_repo_class, client):
        """Test workflow listing with filters"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.list_workflow_templates.return_value = (True, {
            "templates": [],
            "count": 0
        })
        
        response = client.get("/api/workflows?status=active&category=testing&search=test")
        
        assert response.status_code == 200
        # Verify filters were passed to repository
        mock_repo.list_workflow_templates.assert_called_once()
        call_args = mock_repo.list_workflow_templates.call_args
        assert call_args[1]["status"] == "active"
        assert call_args[1]["category"] == "testing"
        assert call_args[1]["search"] == "test"
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_create_workflow_success(self, mock_repo_class, client, sample_workflow_data):
        """Test successful workflow creation"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.create_workflow_template = AsyncMock(return_value=(True, {
            "template": {
                "id": str(uuid4()),
                "name": "test_workflow",
                "title": "Test Workflow",
                "status": "draft",
                "created_at": datetime.now().isoformat()
            }
        }))
        
        response = client.post("/api/workflows", json=sample_workflow_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "workflow" in data
        assert data["workflow"]["name"] == "test_workflow"
        assert "message" in data
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_create_workflow_validation_error(self, mock_repo_class, client):
        """Test workflow creation with validation error"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.create_workflow_template = AsyncMock(return_value=(False, {
            "error": "Validation failed: Workflow name contains invalid characters"
        }))
        
        invalid_data = {
            "name": "test workflow!",  # Invalid name
            "title": "Test Workflow",
            "steps": []
        }
        
        response = client.post("/api/workflows", json=invalid_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_get_workflow_success(self, mock_repo_class, client):
        """Test successful workflow retrieval"""
        workflow_id = str(uuid4())
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_workflow_template.return_value = (True, {
            "template": {
                "id": workflow_id,
                "name": "test_workflow",
                "title": "Test Workflow",
                "steps": [{"name": "step1", "type": "action", "tool_name": "test_tool"}],
                "created_at": datetime.now().isoformat()
            }
        })
        
        response = client.get(f"/api/workflows/{workflow_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "workflow" in data
        assert data["workflow"]["id"] == workflow_id
        # Should include validation result
        assert "validation_result" in data
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_get_workflow_not_found(self, mock_repo_class, client):
        """Test workflow retrieval when not found"""
        workflow_id = str(uuid4())
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_workflow_template.return_value = (False, {
            "error": f"Workflow template with ID {workflow_id} not found"
        })
        
        response = client.get(f"/api/workflows/{workflow_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_update_workflow_success(self, mock_repo_class, client):
        """Test successful workflow update"""
        workflow_id = str(uuid4())
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.update_workflow_template = AsyncMock(return_value=(True, {
            "template": {
                "id": workflow_id,
                "title": "Updated Title",
                "updated_at": datetime.now().isoformat()
            }
        }))
        
        update_data = {"title": "Updated Title", "description": "Updated description"}
        response = client.put(f"/api/workflows/{workflow_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "workflow" in data
        assert data["workflow"]["title"] == "Updated Title"
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_update_workflow_empty_data(self, mock_repo_class, client):
        """Test workflow update with no data"""
        workflow_id = str(uuid4())
        
        response = client.put(f"/api/workflows/{workflow_id}", json={})
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "No update data provided" in data["error"]
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_delete_workflow_success(self, mock_repo_class, client):
        """Test successful workflow deletion"""
        workflow_id = str(uuid4())
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.delete_workflow_template.return_value = (True, {
            "message": "Workflow deleted successfully"
        })
        
        response = client.delete(f"/api/workflows/{workflow_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted successfully" in data["message"]


class TestWorkflowValidationEndpoints:
    """Test workflow validation endpoints"""
    
    @patch('src.server.services.workflow.WorkflowRepository')
    @patch('src.server.models.workflow_validation.validate_workflow_template')
    def test_validate_workflow_success(self, mock_validate, mock_repo_class, client):
        """Test successful workflow validation"""
        workflow_id = str(uuid4())
        
        # Mock repository response
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_workflow_template.return_value = (True, {
            "template": {
                "id": workflow_id,
                "name": "test_workflow",
                "steps": [{"name": "step1", "type": "action", "tool_name": "test_tool"}]
            }
        })
        
        # Mock validation response
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.errors = []
        mock_validation_result.warnings = []
        mock_validation_result.info = []
        mock_validate.return_value = mock_validation_result
        
        response = client.post(f"/api/workflows/{workflow_id}/validate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert "errors" in data
        assert "warnings" in data
        assert "info" in data


class TestWorkflowExecutionEndpoints:
    """Test workflow execution endpoints"""
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_execute_workflow_success(self, mock_repo_class, client, sample_execution_data):
        """Test successful workflow execution"""
        workflow_id = str(uuid4())
        execution_id = str(uuid4())
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.create_workflow_execution = AsyncMock(return_value=(True, {
            "execution": {
                "id": execution_id,
                "workflow_template_id": workflow_id,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
        }))
        
        response = client.post(f"/api/workflows/{workflow_id}/execute", json=sample_execution_data)
        
        assert response.status_code == 202
        data = response.json()
        assert data["execution_id"] == execution_id
        assert data["status"] == "pending"
        assert "message" in data
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_get_execution_status_success(self, mock_repo_class, client):
        """Test successful execution status retrieval"""
        execution_id = str(uuid4())
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_workflow_execution.return_value = (True, {
            "execution": {
                "id": execution_id,
                "status": "running",
                "progress_percentage": 50.0,
                "current_step_index": 1,
                "created_at": datetime.now().isoformat()
            }
        })
        mock_repo.list_step_executions.return_value = (True, {
            "step_executions": [
                {
                    "id": str(uuid4()),
                    "step_index": 0,
                    "step_name": "step1",
                    "status": "completed"
                }
            ]
        })
        
        response = client.get(f"/api/workflows/executions/{execution_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "execution" in data
        assert data["execution"]["id"] == execution_id
        assert "step_executions" in data
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_list_executions_success(self, mock_repo_class, client):
        """Test successful execution listing"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.list_workflow_executions.return_value = (True, {
            "executions": [
                {
                    "id": str(uuid4()),
                    "status": "completed",
                    "triggered_by": "test_user",
                    "created_at": datetime.now().isoformat()
                }
            ],
            "count": 1
        })
        
        response = client.get("/api/workflows/executions")
        
        assert response.status_code == 200
        data = response.json()
        assert "executions" in data
        assert data["total_count"] == 1
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_cancel_execution_success(self, mock_repo_class, client):
        """Test successful execution cancellation"""
        execution_id = str(uuid4())
        
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.update_workflow_execution = AsyncMock(return_value=(True, {
            "execution": {
                "id": execution_id,
                "status": "cancelled",
                "updated_at": datetime.now().isoformat()
            }
        }))
        
        response = client.post(f"/api/workflows/executions/{execution_id}/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["execution_id"] == execution_id
        assert data["status"] == "cancelled"


class TestWorkflowSearchEndpoints:
    """Test workflow search and discovery endpoints"""
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_search_workflows_success(self, mock_repo_class, client):
        """Test successful workflow search"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.list_workflow_templates.return_value = (True, {
            "templates": [
                {
                    "id": str(uuid4()),
                    "name": "matching_workflow",
                    "title": "Matching Workflow",
                    "category": "testing"
                }
            ],
            "count": 1
        })
        
        search_data = {
            "query": "test",
            "category": "testing",
            "status": "active"
        }
        
        response = client.post("/api/workflows/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "workflows" in data
        assert data["total_count"] == 1
        assert data["query"] == "test"
    
    @patch('src.server.services.workflow.WorkflowRepository')
    def test_get_categories_success(self, mock_repo_class, client):
        """Test successful category retrieval"""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.list_workflow_templates.return_value = (True, {
            "templates": [
                {"category": "testing"},
                {"category": "deployment"},
                {"category": "testing"},  # Duplicate should be filtered
                {"category": None}  # None should be filtered
            ],
            "count": 4
        })
        
        response = client.get("/api/workflows/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 2  # Only unique, non-None categories
        assert "testing" in data["categories"]
        assert "deployment" in data["categories"]


class TestWorkflowExampleEndpoints:
    """Test workflow example endpoints"""
    
    def test_get_examples_success(self, client):
        """Test successful example retrieval"""
        response = client.get("/api/workflows/examples")
        
        assert response.status_code == 200
        data = response.json()
        assert "examples" in data
        assert data["total_count"] > 0
        
        # Check example structure
        if data["examples"]:
            example = data["examples"][0]
            assert "name" in example
            assert "title" in example
            assert "description" in example
            assert "complexity" in example
    
    def test_get_specific_example_success(self, client):
        """Test successful specific example retrieval"""
        response = client.get("/api/workflows/examples/project_setup")
        
        assert response.status_code == 200
        data = response.json()
        assert "example" in data
        assert data["name"] == "project_setup"
        assert data["example"]["name"] == "project_setup"
    
    def test_get_specific_example_not_found(self, client):
        """Test specific example retrieval when not found"""
        response = client.get("/api/workflows/examples/nonexistent_example")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestWorkflowHealthEndpoint:
    """Test workflow health endpoint"""
    
    def test_health_check(self, client):
        """Test workflow API health check"""
        response = client.get("/api/workflows/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "workflow-api"
        assert "timestamp" in data


if __name__ == "__main__":
    pytest.main([__file__])
