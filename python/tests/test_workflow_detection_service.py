"""
Tests for Workflow Detection Service

Tests the intelligent workflow suggestion and detection capabilities.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.server.services.workflow.workflow_detection_service import WorkflowDetectionService


class TestWorkflowDetectionService:
    """Test cases for WorkflowDetectionService."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client."""
        return Mock()
    
    @pytest.fixture
    def detection_service(self, mock_supabase_client):
        """Create WorkflowDetectionService instance with mocked dependencies."""
        with patch('src.server.services.workflow.workflow_detection_service.WorkflowRepository'):
            with patch('src.server.services.workflow.workflow_detection_service.get_mcp_workflow_integration'):
                service = WorkflowDetectionService(mock_supabase_client)
                return service
    
    @pytest.mark.asyncio
    async def test_detect_workflows_for_task_basic(self, detection_service):
        """Test basic workflow detection functionality."""
        # Mock the internal methods
        detection_service._get_keyword_based_suggestions = AsyncMock(return_value=[
            {
                "type": "keyword_pattern",
                "pattern_name": "documentation",
                "title": "Documentation creation and management workflows",
                "category": "documentation",
                "score": 2,
                "confidence": 0.5,
                "matched_keywords": ["document", "guide"],
                "suggestion_reason": "Matched 2 keywords: document, guide"
            }
        ])
        
        detection_service._get_mcp_workflow_suggestions = AsyncMock(return_value=[])
        detection_service._get_existing_workflow_suggestions = AsyncMock(return_value=[])
        
        # Test workflow detection
        result = await detection_service.detect_workflows_for_task(
            task_title="Create user documentation",
            task_description="Write comprehensive user guide for the application",
            project_id="test-project-123"
        )
        
        # Verify result structure
        assert result["task_title"] == "Create user documentation"
        assert result["task_description"] == "Write comprehensive user guide for the application"
        assert len(result["workflow_suggestions"]) == 1
        assert result["workflow_suggestions"][0]["pattern_name"] == "documentation"
        assert "detection_metadata" in result
        assert result["detection_metadata"]["keyword_matches"] == 1
    
    def test_calculate_text_similarity(self, detection_service):
        """Test text similarity calculation."""
        # Test identical texts
        similarity = detection_service._calculate_text_similarity("hello world", "hello world")
        assert similarity == 1.0
        
        # Test completely different texts
        similarity = detection_service._calculate_text_similarity("hello world", "foo bar")
        assert similarity == 0.0
        
        # Test partial similarity
        similarity = detection_service._calculate_text_similarity(
            "implement oauth authentication", 
            "create oauth system"
        )
        assert 0 < similarity < 1
        
        # Test empty strings
        similarity = detection_service._calculate_text_similarity("", "hello")
        assert similarity == 0.0
    
    def test_extract_workflow_parameters(self, detection_service):
        """Test parameter extraction from task text."""
        text = '''
        Implement OAuth2 with "Google Provider" and GitHub integration.
        Use https://developers.google.com/oauth2 documentation.
        Update src/auth/oauth.py and tests/test_oauth.py files.
        Technologies: react, python, docker
        '''
        
        parameters = detection_service._extract_workflow_parameters(text)
        
        # Check extracted parameters
        assert "urls" in parameters
        assert "https://developers.google.com/oauth2" in parameters["urls"]
        
        assert "files" in parameters
        assert "src/auth/oauth.py" in parameters["files"]
        assert "tests/test_oauth.py" in parameters["files"]
        
        assert "quoted_strings" in parameters
        assert "Google Provider" in parameters["quoted_strings"]
        
        assert "technologies" in parameters
        assert "react" in parameters["technologies"]
        assert "python" in parameters["technologies"]
        assert "docker" in parameters["technologies"]
    
    def test_deduplicate_and_rank_suggestions(self, detection_service):
        """Test suggestion deduplication and ranking."""
        suggestions = [
            {
                "type": "keyword_pattern",
                "pattern_name": "documentation",
                "score": 2,
                "confidence": 0.5
            },
            {
                "type": "mcp_workflow",
                "workflow_name": "project_research",
                "score": 3,
                "confidence": 0.8
            },
            {
                "type": "keyword_pattern",
                "pattern_name": "documentation",
                "score": 1,  # Lower score, should be filtered out
                "confidence": 0.3
            },
            {
                "type": "existing_workflow",
                "workflow_id": "workflow-123",
                "score": 2.5,
                "confidence": 0.7
            }
        ]
        
        result = detection_service._deduplicate_and_rank_suggestions(suggestions)
        
        # Should have 3 unique suggestions (documentation deduplicated)
        assert len(result) == 3
        
        # Should be ranked by score (highest first)
        assert result[0]["score"] == 3  # mcp_workflow
        assert result[1]["score"] == 2.5  # existing_workflow
        assert result[2]["score"] == 2  # keyword_pattern (higher score kept)
    
    def test_generate_binding_recommendations(self, detection_service):
        """Test workflow binding recommendations generation."""
        workflow_suggestions = [
            {
                "type": "mcp_workflow",
                "workflow_name": "project_research",
                "confidence": 0.9,
                "suggestion_reason": "High confidence MCP workflow"
            },
            {
                "type": "existing_workflow",
                "workflow_id": "workflow-123",
                "confidence": 0.7,
                "suggestion_reason": "Existing workflow match"
            },
            {
                "type": "keyword_pattern",
                "pattern_name": "documentation",
                "confidence": 0.4,
                "suggestion_reason": "Pattern-based suggestion"
            }
        ]
        
        recommendations = detection_service._generate_binding_recommendations(
            "Create documentation",
            "Write user guide",
            workflow_suggestions
        )
        
        # Should have 3 recommendations
        assert len(recommendations) == 3
        
        # High confidence should suggest auto-execution
        assert recommendations[0]["binding_type"] == "auto_execute"
        assert recommendations[0]["recommended_action"] == "auto_bind_and_execute"
        
        # Medium confidence should suggest preview
        assert recommendations[1]["binding_type"] == "suggest_with_preview"
        assert recommendations[1]["recommended_action"] == "show_preview_and_suggest"
        
        # Low confidence should suggest manual review
        assert recommendations[2]["binding_type"] == "manual_review"
        assert recommendations[2]["recommended_action"] == "suggest_for_manual_review"
        
        # Check execution notes are present
        assert "execution_notes" in recommendations[0]
        assert "execution_notes" in recommendations[1]
        assert "execution_notes" in recommendations[2]
    
    @pytest.mark.asyncio
    async def test_keyword_based_suggestions(self, detection_service):
        """Test keyword-based workflow suggestions."""
        text = "Create unit tests and integration tests for the authentication module"
        
        suggestions = await detection_service._get_keyword_based_suggestions(text)
        
        # Should find testing pattern
        testing_suggestions = [s for s in suggestions if s["pattern_name"] == "testing"]
        assert len(testing_suggestions) > 0
        
        testing_suggestion = testing_suggestions[0]
        assert testing_suggestion["category"] == "testing"
        assert testing_suggestion["score"] > 0
        assert "test" in testing_suggestion["matched_keywords"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, detection_service):
        """Test error handling in workflow detection."""
        # Mock methods to raise exceptions
        detection_service._get_keyword_based_suggestions = AsyncMock(side_effect=Exception("Test error"))
        detection_service._get_mcp_workflow_suggestions = AsyncMock(return_value=[])
        detection_service._get_existing_workflow_suggestions = AsyncMock(return_value=[])
        
        result = await detection_service.detect_workflows_for_task(
            task_title="Test task",
            task_description="Test description"
        )
        
        # Should return error result
        assert "error" in result
        assert result["workflow_suggestions"] == []
        assert result["extracted_parameters"] == {}
        assert result["binding_recommendations"] == []
