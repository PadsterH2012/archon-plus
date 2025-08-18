"""
Tests for Workflow WebSocket API

Tests the real-time workflow execution monitoring WebSocket endpoints.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from src.server.api_routes.workflow_websocket import (
    WorkflowWebSocketManager,
    get_workflow_websocket_manager,
    router
)


class TestWorkflowWebSocketManager:
    """Test cases for WorkflowWebSocketManager."""
    
    @pytest.fixture
    def websocket_manager(self):
        """Create WorkflowWebSocketManager instance."""
        return WorkflowWebSocketManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket."""
        websocket = Mock(spec=WebSocket)
        websocket.accept = AsyncMock()
        websocket.send_json = AsyncMock()
        websocket.receive_text = AsyncMock()
        return websocket
    
    @pytest.mark.asyncio
    async def test_connect_to_execution(self, websocket_manager, mock_websocket):
        """Test connecting WebSocket to specific execution."""
        execution_id = "test-execution-123"
        
        await websocket_manager.connect(mock_websocket, execution_id)
        
        # Verify connection was accepted
        mock_websocket.accept.assert_called_once()
        
        # Verify websocket was added to execution connections
        assert execution_id in websocket_manager.connections
        assert mock_websocket in websocket_manager.connections[execution_id]
        assert mock_websocket in websocket_manager.subscriptions
        assert execution_id in websocket_manager.subscriptions[mock_websocket]
    
    @pytest.mark.asyncio
    async def test_connect_global_subscriber(self, websocket_manager, mock_websocket):
        """Test connecting WebSocket as global subscriber."""
        await websocket_manager.connect(mock_websocket)
        
        # Verify connection was accepted
        mock_websocket.accept.assert_called_once()
        
        # Verify websocket was added to global subscribers
        assert mock_websocket in websocket_manager.global_subscribers
    
    def test_disconnect(self, websocket_manager, mock_websocket):
        """Test disconnecting WebSocket and cleanup."""
        execution_id = "test-execution-123"
        
        # Setup connection
        websocket_manager.connections[execution_id].add(mock_websocket)
        websocket_manager.subscriptions[mock_websocket].add(execution_id)
        websocket_manager.global_subscribers.add(mock_websocket)
        
        # Disconnect
        websocket_manager.disconnect(mock_websocket)
        
        # Verify cleanup
        assert execution_id not in websocket_manager.connections
        assert mock_websocket not in websocket_manager.subscriptions
        assert mock_websocket not in websocket_manager.global_subscribers
    
    @pytest.mark.asyncio
    async def test_subscribe_to_execution(self, websocket_manager, mock_websocket):
        """Test subscribing existing WebSocket to execution."""
        execution_id = "test-execution-456"
        
        with patch('src.server.api_routes.workflow_websocket.get_workflow_execution_service') as mock_service:
            # Mock execution service
            mock_execution_service = Mock()
            mock_execution_service.get_execution_status = AsyncMock(return_value=(True, {
                "execution": {"id": execution_id, "status": "running"},
                "step_executions": []
            }))
            mock_service.return_value = mock_execution_service
            
            await websocket_manager.subscribe_to_execution(mock_websocket, execution_id)
            
            # Verify subscription
            assert execution_id in websocket_manager.connections
            assert mock_websocket in websocket_manager.connections[execution_id]
            
            # Verify initial status was sent
            mock_websocket.send_json.assert_called_once()
            call_args = mock_websocket.send_json.call_args[0][0]
            assert call_args["type"] == "execution_update"
            assert call_args["execution_id"] == execution_id
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_execution(self, websocket_manager, mock_websocket):
        """Test unsubscribing WebSocket from execution."""
        execution_id = "test-execution-789"
        
        # Setup subscription
        websocket_manager.connections[execution_id].add(mock_websocket)
        websocket_manager.subscriptions[mock_websocket].add(execution_id)
        
        await websocket_manager.unsubscribe_from_execution(mock_websocket, execution_id)
        
        # Verify unsubscription
        assert execution_id not in websocket_manager.connections
        assert execution_id not in websocket_manager.subscriptions[mock_websocket]
    
    @pytest.mark.asyncio
    async def test_broadcast_to_execution(self, websocket_manager, mock_websocket):
        """Test broadcasting message to execution subscribers."""
        execution_id = "test-execution-broadcast"
        message = {"type": "test_message", "data": {"test": "value"}}
        
        # Setup connection
        websocket_manager.connections[execution_id].add(mock_websocket)
        
        await websocket_manager.broadcast_to_execution(execution_id, message)
        
        # Verify message was sent
        mock_websocket.send_json.assert_called_once()
        sent_message = mock_websocket.send_json.call_args[0][0]
        assert sent_message["type"] == "test_message"
        assert sent_message["execution_id"] == execution_id
        assert "timestamp" in sent_message
    
    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, websocket_manager, mock_websocket):
        """Test broadcasting message to all global subscribers."""
        message = {"type": "global_message", "data": {"test": "value"}}
        
        # Setup global subscriber
        websocket_manager.global_subscribers.add(mock_websocket)
        
        await websocket_manager.broadcast_to_all(message)
        
        # Verify message was sent
        mock_websocket.send_json.assert_called_once()
        sent_message = mock_websocket.send_json.call_args[0][0]
        assert sent_message["type"] == "global_message"
        assert "timestamp" in sent_message
    
    @pytest.mark.asyncio
    async def test_broadcast_handles_disconnected_websockets(self, websocket_manager):
        """Test that broadcasting handles disconnected WebSockets gracefully."""
        execution_id = "test-execution-disconnect"
        
        # Create mock websockets - one working, one failing
        working_ws = Mock(spec=WebSocket)
        working_ws.send_json = AsyncMock()
        
        failing_ws = Mock(spec=WebSocket)
        failing_ws.send_json = AsyncMock(side_effect=Exception("Connection closed"))
        
        # Setup connections
        websocket_manager.connections[execution_id].add(working_ws)
        websocket_manager.connections[execution_id].add(failing_ws)
        websocket_manager.subscriptions[working_ws].add(execution_id)
        websocket_manager.subscriptions[failing_ws].add(execution_id)
        
        message = {"type": "test_message", "data": {"test": "value"}}
        
        await websocket_manager.broadcast_to_execution(execution_id, message)
        
        # Verify working websocket received message
        working_ws.send_json.assert_called_once()
        
        # Verify failing websocket was cleaned up
        assert failing_ws not in websocket_manager.connections[execution_id]
        assert failing_ws not in websocket_manager.subscriptions
    
    def test_get_connection_stats(self, websocket_manager, mock_websocket):
        """Test getting connection statistics."""
        execution_id = "test-execution-stats"
        
        # Setup connections
        websocket_manager.connections[execution_id].add(mock_websocket)
        websocket_manager.global_subscribers.add(mock_websocket)
        
        stats = websocket_manager.get_connection_stats()
        
        assert stats["total_connections"] == 2  # 1 execution + 1 global
        assert stats["execution_connections"] == 1
        assert stats["global_subscribers"] == 1
        assert execution_id in stats["active_executions"]


class TestWorkflowWebSocketEndpoints:
    """Test cases for WebSocket endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_workflow_websocket_manager(self):
        """Test getting the global WebSocket manager instance."""
        manager1 = get_workflow_websocket_manager()
        manager2 = get_workflow_websocket_manager()
        
        # Should return the same instance (singleton pattern)
        assert manager1 is manager2
        assert isinstance(manager1, WorkflowWebSocketManager)
    
    def test_websocket_router_included(self):
        """Test that WebSocket router is properly configured."""
        # Check that router has the expected prefix and tags
        assert router.prefix == "/api/workflows"
        assert "workflow-websocket" in router.tags
        
        # Check that WebSocket routes are registered
        websocket_routes = [route for route in router.routes if hasattr(route, 'path')]
        websocket_paths = [route.path for route in websocket_routes]
        
        assert "/executions/{execution_id}/stream" in websocket_paths
        assert "/executions/stream" in websocket_paths


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality."""
    
    @pytest.mark.asyncio
    async def test_websocket_message_format(self, websocket_manager, mock_websocket):
        """Test that WebSocket messages follow expected format."""
        execution_id = "test-execution-format"
        websocket_manager.connections[execution_id].add(mock_websocket)
        
        # Test different message types
        test_messages = [
            {"type": "execution_update", "data": {"status": "running"}},
            {"type": "step_completed", "data": {"step_name": "test_step"}},
            {"type": "progress_update", "data": {"progress_percentage": 50.0}},
            {"type": "execution_completed", "data": {"status": "completed"}}
        ]
        
        for message in test_messages:
            await websocket_manager.broadcast_to_execution(execution_id, message)
            
            # Verify message format
            sent_message = mock_websocket.send_json.call_args[0][0]
            assert "type" in sent_message
            assert "data" in sent_message
            assert "timestamp" in sent_message
            assert "execution_id" in sent_message
            assert sent_message["execution_id"] == execution_id
            
            mock_websocket.send_json.reset_mock()
    
    @pytest.mark.asyncio
    async def test_multiple_subscribers_same_execution(self, websocket_manager):
        """Test multiple WebSockets subscribing to same execution."""
        execution_id = "test-execution-multiple"
        
        # Create multiple mock websockets
        websockets = []
        for i in range(3):
            ws = Mock(spec=WebSocket)
            ws.send_json = AsyncMock()
            websockets.append(ws)
            websocket_manager.connections[execution_id].add(ws)
        
        message = {"type": "test_broadcast", "data": {"test": "multiple"}}
        await websocket_manager.broadcast_to_execution(execution_id, message)
        
        # Verify all websockets received the message
        for ws in websockets:
            ws.send_json.assert_called_once()
            sent_message = ws.send_json.call_args[0][0]
            assert sent_message["type"] == "test_broadcast"
