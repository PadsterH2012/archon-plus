"""Simple test configuration for Archon - Essential tests only."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set test environment
os.environ["TEST_MODE"] = "true"
os.environ["TESTING"] = "true"
# Set fake database credentials to prevent connection attempts
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "test-key"
# Set required port environment variables for ServiceDiscovery
os.environ.setdefault("ARCHON_SERVER_PORT", "8181")
os.environ.setdefault("ARCHON_MCP_PORT", "8051")
os.environ.setdefault("ARCHON_AGENTS_PORT", "8052")


@pytest.fixture(autouse=True)
def prevent_real_db_calls():
    """Automatically prevent any real database calls in all tests."""
    with patch("supabase.create_client") as mock_create:
        # Make create_client raise an error if called without our mock
        mock_create.side_effect = Exception("Real database calls are not allowed in tests!")
        yield


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    mock_client = MagicMock()

    # Mock table operations with chaining support
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_insert = MagicMock()
    mock_update = MagicMock()
    mock_delete = MagicMock()

    # Setup method chaining for select
    mock_select.execute.return_value.data = []
    mock_select.eq.return_value = mock_select
    mock_select.neq.return_value = mock_select
    mock_select.order.return_value = mock_select
    mock_select.limit.return_value = mock_select
    mock_table.select.return_value = mock_select

    # Setup method chaining for insert
    mock_insert.execute.return_value.data = [{"id": "test-id"}]
    mock_table.insert.return_value = mock_insert

    # Setup method chaining for update
    mock_update.execute.return_value.data = [{"id": "test-id"}]
    mock_update.eq.return_value = mock_update
    mock_table.update.return_value = mock_update

    # Setup method chaining for delete
    mock_delete.execute.return_value.data = []
    mock_delete.eq.return_value = mock_delete
    mock_table.delete.return_value = mock_delete

    # Make table() return the mock table
    mock_client.table.return_value = mock_table

    # Mock auth operations
    mock_client.auth = MagicMock()
    mock_client.auth.get_user.return_value = None

    # Mock storage operations
    mock_client.storage = MagicMock()

    return mock_client


@pytest.fixture
def client(mock_supabase_client):
    """FastAPI test client with mocked database."""
    # Patch all the ways Supabase client can be created
    with patch(
        "src.server.services.client_manager.create_client", return_value=mock_supabase_client
    ):
        with patch(
            "src.server.services.credential_service.create_client",
            return_value=mock_supabase_client,
        ):
            with patch(
                "src.server.services.client_manager.get_supabase_client",
                return_value=mock_supabase_client,
            ):
                with patch("supabase.create_client", return_value=mock_supabase_client):
                    # Import app after patching to ensure mocks are used
                    from src.server.main import app

                    return TestClient(app)


@pytest.fixture
def test_project():
    """Simple test project data."""
    return {"title": "Test Project", "description": "A test project for essential tests"}


@pytest.fixture
def test_task():
    """Simple test task data."""
    return {
        "title": "Test Task",
        "description": "A test task for essential tests",
        "status": "todo",
        "assignee": "User",
    }


@pytest.fixture
def test_knowledge_item():
    """Simple test knowledge item data."""
    return {
        "url": "https://example.com/test",
        "title": "Test Knowledge Item",
        "content": "This is test content for knowledge base",
        "source_id": "test-source",
    }


# Export/Import Testing Fixtures

@pytest.fixture
def temp_directory():
    """Provide a temporary directory for test files"""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    yield temp_dir

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_export_project_data():
    """Provide comprehensive project data for export testing"""
    return {
        "id": "export-test-project-123",
        "title": "Export Test Project",
        "description": "A comprehensive test project for export/import testing",
        "github_repo": "https://github.com/test/export-repo",
        "pinned": False,
        "docs": [
            {
                "id": "export-doc-1",
                "document_type": "prp",
                "title": "Export Test PRP",
                "content": {
                    "goal": "Test the export functionality thoroughly",
                    "why": ["Ensure data integrity", "Validate export format"],
                    "what": {
                        "description": "Complete export testing with all data types",
                        "success_criteria": ["All data exported", "Format validated"]
                    }
                },
                "metadata": {"version": "1.0", "author": "export_tester"}
            }
        ],
        "features": ["export", "testing"],
        "data": {"test_config": {"export_enabled": True}},
        "created_at": "2025-08-18T20:00:00Z",
        "updated_at": "2025-08-18T22:00:00Z"
    }


@pytest.fixture
def sample_export_tasks_data():
    """Provide comprehensive tasks data for export testing"""
    return [
        {
            "id": "export-task-1",
            "project_id": "export-test-project-123",
            "title": "Export Test Task 1",
            "description": "First task for export testing",
            "status": "done",
            "assignee": "AI IDE Agent",
            "task_order": 1,
            "feature": "export",
            "sources": [{"url": "test.com", "type": "docs"}],
            "code_examples": [{"file": "test.py", "function": "test"}],
            "created_at": "2025-08-18T20:30:00Z",
            "updated_at": "2025-08-18T21:45:00Z"
        },
        {
            "id": "export-task-2",
            "project_id": "export-test-project-123",
            "title": "Export Test Task 2",
            "description": "Second task for export testing",
            "status": "todo",
            "assignee": "User",
            "task_order": 2,
            "feature": "testing",
            "sources": [],
            "code_examples": [],
            "created_at": "2025-08-18T21:00:00Z",
            "updated_at": "2025-08-18T21:00:00Z"
        }
    ]


def create_test_export_file(temp_dir: str, project_data: dict, tasks_data: list) -> str:
    """Utility function to create a test export file"""
    import json
    import zipfile
    from datetime import datetime

    export_file = os.path.join(temp_dir, "test_export.zip")

    with zipfile.ZipFile(export_file, 'w') as zipf:
        # Create manifest
        manifest = {
            "format_version": "1.0.0",
            "export_timestamp": datetime.now().isoformat(),
            "project_id": project_data["id"],
            "exported_by": "test_user",
            "export_type": "full"
        }
        zipf.writestr("manifest.json", json.dumps(manifest, indent=2))

        # Create project data
        zipf.writestr("project.json", json.dumps(project_data, indent=2))

        # Create tasks data
        tasks_export = {
            "tasks": tasks_data,
            "statistics": {"total_tasks": len(tasks_data)}
        }
        zipf.writestr("tasks.json", json.dumps(tasks_export, indent=2))

    return export_file
