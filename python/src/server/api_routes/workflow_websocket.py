"""
Workflow WebSocket API for Real-time Execution Monitoring

Provides WebSocket endpoints for real-time workflow execution monitoring including:
- Live execution progress updates
- Step-by-step execution tracking
- Real-time log streaming
- Execution status changes
- Error notifications
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set, Any, Optional
from collections import defaultdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from ..config.logfire_config import get_logger, logfire
from ..services.workflow import get_workflow_execution_service
from ..utils import get_supabase_client

logger = get_logger(__name__)
router = APIRouter(prefix="/api/workflows", tags=["workflow-websocket"])


class WorkflowWebSocketManager:
    """
    WebSocket connection manager for workflow execution monitoring.
    
    Manages connections, subscriptions, and real-time broadcasting of workflow events.
    """
    
    def __init__(self):
        # execution_id -> set of websockets
        self.connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        # websocket -> set of execution_ids it's subscribed to
        self.subscriptions: Dict[WebSocket, Set[str]] = defaultdict(set)
        # Global subscribers (receive all execution updates)
        self.global_subscribers: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket, execution_id: Optional[str] = None):
        """Accept WebSocket connection and optionally subscribe to execution."""
        await websocket.accept()
        
        if execution_id:
            self.connections[execution_id].add(websocket)
            self.subscriptions[websocket].add(execution_id)
            logfire.info(f"WebSocket connected to execution | execution_id={execution_id}")
        else:
            self.global_subscribers.add(websocket)
            logfire.info("WebSocket connected as global subscriber")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection and clean up subscriptions."""
        # Remove from execution-specific connections
        for execution_id in self.subscriptions[websocket]:
            self.connections[execution_id].discard(websocket)
            if not self.connections[execution_id]:
                del self.connections[execution_id]
        
        # Remove from global subscribers
        self.global_subscribers.discard(websocket)
        
        # Clean up subscriptions
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        
        logfire.info("WebSocket disconnected and cleaned up")
    
    async def subscribe_to_execution(self, websocket: WebSocket, execution_id: str):
        """Subscribe existing WebSocket to execution updates."""
        self.connections[execution_id].add(websocket)
        self.subscriptions[websocket].add(execution_id)
        
        # Send current execution status
        try:
            execution_service = get_workflow_execution_service()
            success, result = await execution_service.get_execution_status(execution_id)
            
            if success:
                await websocket.send_json({
                    "type": "execution_update",
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "execution_id": execution_id
                })
        except Exception as e:
            logger.warning(f"Failed to send initial execution status | error={str(e)}")
        
        logfire.info(f"WebSocket subscribed to execution | execution_id={execution_id}")
    
    async def unsubscribe_from_execution(self, websocket: WebSocket, execution_id: str):
        """Unsubscribe WebSocket from execution updates."""
        self.connections[execution_id].discard(websocket)
        self.subscriptions[websocket].discard(execution_id)
        
        if not self.connections[execution_id]:
            del self.connections[execution_id]
        
        logfire.info(f"WebSocket unsubscribed from execution | execution_id={execution_id}")
    
    async def broadcast_to_execution(self, execution_id: str, message: Dict[str, Any]):
        """Broadcast message to all WebSockets subscribed to specific execution."""
        if execution_id not in self.connections:
            return
        
        disconnected = []
        message["execution_id"] = execution_id
        message["timestamp"] = datetime.now().isoformat()
        
        for websocket in self.connections[execution_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket | error={str(e)}")
                disconnected.append(websocket)
        
        # Clean up disconnected WebSockets
        for ws in disconnected:
            self.disconnect(ws)
        
        logfire.debug(f"Broadcasted to execution | execution_id={execution_id} | type={message.get('type')}")
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all global subscribers."""
        disconnected = []
        message["timestamp"] = datetime.now().isoformat()
        
        for websocket in self.global_subscribers:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to global subscriber | error={str(e)}")
                disconnected.append(websocket)
        
        # Clean up disconnected WebSockets
        for ws in disconnected:
            self.disconnect(ws)
        
        logfire.debug(f"Broadcasted to all subscribers | type={message.get('type')}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics for monitoring."""
        return {
            "total_connections": sum(len(connections) for connections in self.connections.values()) + len(self.global_subscribers),
            "execution_connections": len(self.connections),
            "global_subscribers": len(self.global_subscribers),
            "active_executions": list(self.connections.keys())
        }


# Global WebSocket manager instance
websocket_manager = WorkflowWebSocketManager()


@router.websocket("/executions/{execution_id}/stream")
async def workflow_execution_websocket(websocket: WebSocket, execution_id: str):
    """
    WebSocket endpoint for real-time workflow execution monitoring.
    
    Provides live updates for:
    - Execution status changes
    - Step progress updates
    - Real-time logs
    - Error notifications
    """
    await websocket_manager.connect(websocket, execution_id)
    
    try:
        logfire.info(f"WebSocket connection established | execution_id={execution_id}")
        
        # Send initial execution status if available
        try:
            execution_service = get_workflow_execution_service()
            success, result = await execution_service.get_execution_status(execution_id)
            
            if success:
                await websocket.send_json({
                    "type": "execution_update",
                    "data": result,
                    "timestamp": datetime.now().isoformat(),
                    "execution_id": execution_id
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Execution not found: {execution_id}"},
                    "timestamp": datetime.now().isoformat(),
                    "execution_id": execution_id
                })
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "data": {"message": f"Failed to get execution status: {str(e)}"},
                "timestamp": datetime.now().isoformat(),
                "execution_id": execution_id
            })
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client messages (heartbeat, subscription changes, etc.)
                message = await websocket.receive_text()
                
                try:
                    data = json.loads(message)
                    message_type = data.get("type")
                    
                    if message_type == "heartbeat":
                        await websocket.send_json({
                            "type": "heartbeat_response",
                            "timestamp": datetime.now().isoformat()
                        })
                    elif message_type == "subscribe":
                        new_execution_id = data.get("execution_id")
                        if new_execution_id:
                            await websocket_manager.subscribe_to_execution(websocket, new_execution_id)
                    elif message_type == "unsubscribe":
                        old_execution_id = data.get("execution_id")
                        if old_execution_id:
                            await websocket_manager.unsubscribe_from_execution(websocket, old_execution_id)
                    
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Invalid JSON message"},
                        "timestamp": datetime.now().isoformat()
                    })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message | error={str(e)}")
                break
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error | execution_id={execution_id} | error={str(e)}")
    finally:
        websocket_manager.disconnect(websocket)
        logfire.info(f"WebSocket connection closed | execution_id={execution_id}")


@router.websocket("/executions/stream")
async def workflow_global_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for monitoring all workflow executions.
    
    Provides global updates for all workflow executions.
    """
    await websocket_manager.connect(websocket)
    
    try:
        logfire.info("Global workflow WebSocket connection established")
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "data": {"message": "Connected to global workflow monitoring"},
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle client messages
        while True:
            try:
                message = await websocket.receive_text()
                
                try:
                    data = json.loads(message)
                    message_type = data.get("type")
                    
                    if message_type == "heartbeat":
                        await websocket.send_json({
                            "type": "heartbeat_response",
                            "timestamp": datetime.now().isoformat()
                        })
                    elif message_type == "subscribe_all":
                        # Already subscribed to all as global subscriber
                        await websocket.send_json({
                            "type": "subscribed_all",
                            "timestamp": datetime.now().isoformat()
                        })
                    elif message_type == "get_stats":
                        stats = websocket_manager.get_connection_stats()
                        await websocket.send_json({
                            "type": "connection_stats",
                            "data": stats,
                            "timestamp": datetime.now().isoformat()
                        })
                
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "Invalid JSON message"},
                        "timestamp": datetime.now().isoformat()
                    })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling global WebSocket message | error={str(e)}")
                break
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Global WebSocket error | error={str(e)}")
    finally:
        websocket_manager.disconnect(websocket)
        logfire.info("Global workflow WebSocket connection closed")


# Export the websocket manager for use by workflow execution services
def get_workflow_websocket_manager() -> WorkflowWebSocketManager:
    """Get the global workflow WebSocket manager instance."""
    return websocket_manager
