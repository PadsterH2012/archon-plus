"""
Tests for MCP Server Log Reading

This module tests the MCP server log reading functionality including:
- Docker Compose mode log reading
- Docker Swarm mode log reading
- Log reader task management
- Error handling for missing containers/services
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from collections import deque

from src.server.api_routes.mcp_api import MCPServerManager


class TestMCPServerLogReading:
    """Test MCP server log reading functionality"""

    @pytest.fixture
    def mock_docker_client(self):
        """Create a mock Docker client"""
        client = Mock()
        client.containers = Mock()
        client.services = Mock()
        return client

    @pytest.fixture
    def mcp_manager_compose(self, mock_docker_client):
        """Create MCP manager for Docker Compose mode"""
        with patch('src.server.api_routes.mcp_api.docker.from_env', return_value=mock_docker_client):
            with patch.dict('os.environ', {'SERVICE_DISCOVERY_MODE': 'docker_compose'}):
                manager = MCPServerManager()
                manager.is_swarm_mode = False
                manager.container_name = "test-container"
                manager.docker_client = mock_docker_client
                return manager

    @pytest.fixture
    def mcp_manager_swarm(self, mock_docker_client):
        """Create MCP manager for Docker Swarm mode"""
        with patch('src.server.api_routes.mcp_api.docker.from_env', return_value=mock_docker_client):
            with patch.dict('os.environ', {'SERVICE_DISCOVERY_MODE': 'docker_swarm'}):
                manager = MCPServerManager()
                manager.is_swarm_mode = True
                manager.container_name = "test-service"
                manager.docker_client = mock_docker_client
                return manager

    def test_log_reader_active_check(self, mcp_manager_compose):
        """Test log reader active status check"""
        # No task - should be False
        assert not mcp_manager_compose._is_log_reader_active()
        
        # Mock active task
        mock_task = Mock()
        mock_task.done.return_value = False
        mcp_manager_compose.log_reader_task = mock_task
        assert mcp_manager_compose._is_log_reader_active()
        
        # Mock completed task
        mock_task.done.return_value = True
        assert not mcp_manager_compose._is_log_reader_active()

    @pytest.mark.asyncio
    async def test_ensure_log_reader_compose_mode(self, mcp_manager_compose):
        """Test ensuring log reader runs in Docker Compose mode"""
        # Mock container
        mock_container = Mock()
        mcp_manager_compose.container = mock_container
        
        with patch.object(mcp_manager_compose, '_read_container_logs') as mock_read_logs:
            mock_read_logs.return_value = AsyncMock()
            
            await mcp_manager_compose._ensure_log_reader_running()
            
            # Should have created a log reader task
            assert mcp_manager_compose.log_reader_task is not None
            assert not mcp_manager_compose.log_reader_task.done()

    @pytest.mark.asyncio
    async def test_ensure_log_reader_swarm_mode(self, mcp_manager_swarm):
        """Test ensuring log reader runs in Docker Swarm mode"""
        # Mock service
        mock_service = Mock()
        mcp_manager_swarm.service = mock_service
        
        with patch.object(mcp_manager_swarm, '_read_container_logs') as mock_read_logs:
            mock_read_logs.return_value = AsyncMock()
            
            await mcp_manager_swarm._ensure_log_reader_running()
            
            # Should have created a log reader task
            assert mcp_manager_swarm.log_reader_task is not None
            assert not mcp_manager_swarm.log_reader_task.done()

    @pytest.mark.asyncio
    async def test_ensure_log_reader_no_container_or_service(self, mcp_manager_compose):
        """Test ensuring log reader when no container or service available"""
        # No container or service
        mcp_manager_compose.container = None
        mcp_manager_compose.service = None
        
        await mcp_manager_compose._ensure_log_reader_running()
        
        # Should not have created a log reader task
        assert mcp_manager_compose.log_reader_task is None

    @pytest.mark.asyncio
    async def test_read_container_logs_compose_mode(self, mcp_manager_compose):
        """Test reading logs in Docker Compose mode"""
        # Mock container with logs
        mock_container = Mock()
        mock_logs = [b"INFO: Test log line 1\n", b"ERROR: Test error line\n"]
        mock_container.logs.return_value = iter(mock_logs)
        mcp_manager_compose.container = mock_container
        
        # Mock the log parsing
        with patch.object(mcp_manager_compose, '_parse_log_line') as mock_parse:
            mock_parse.side_effect = [("INFO", "Test log line 1"), ("ERROR", "Test error line")]
            
            with patch.object(mcp_manager_compose, '_add_log') as mock_add_log:
                # Run the log reader briefly
                task = asyncio.create_task(mcp_manager_compose._read_container_logs())
                await asyncio.sleep(0.1)  # Let it process some logs
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                # Should have called _add_log for each log line
                assert mock_add_log.call_count >= 1

    @pytest.mark.asyncio
    async def test_read_container_logs_swarm_mode(self, mcp_manager_swarm):
        """Test reading logs in Docker Swarm mode"""
        # Mock service with tasks
        mock_service = Mock()
        mock_task = {
            'Status': {
                'State': 'running',
                'ContainerStatus': {
                    'ContainerID': 'container123'
                }
            }
        }
        mock_service.tasks.return_value = [mock_task]
        mcp_manager_swarm.service = mock_service
        
        # Mock container from service task
        mock_container = Mock()
        mock_logs = [b"INFO: Swarm log line\n"]
        mock_container.logs.return_value = iter(mock_logs)
        mcp_manager_swarm.docker_client.containers.get.return_value = mock_container
        
        # Mock the log parsing
        with patch.object(mcp_manager_swarm, '_parse_log_line') as mock_parse:
            mock_parse.return_value = ("INFO", "Swarm log line")
            
            with patch.object(mcp_manager_swarm, '_add_log') as mock_add_log:
                # Run the log reader briefly
                task = asyncio.create_task(mcp_manager_swarm._read_container_logs())
                await asyncio.sleep(0.1)  # Let it process some logs
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                # Should have called _add_log for the log line
                assert mock_add_log.call_count >= 1
                # Should have tried to get container from service task
                mcp_manager_swarm.docker_client.containers.get.assert_called_with('container123')

    @pytest.mark.asyncio
    async def test_read_container_logs_swarm_no_running_tasks(self, mcp_manager_swarm):
        """Test reading logs in Docker Swarm mode with no running tasks"""
        # Mock service with no running tasks
        mock_service = Mock()
        mock_task = {
            'Status': {
                'State': 'failed',  # Not running
                'ContainerStatus': {
                    'ContainerID': 'container123'
                }
            }
        }
        mock_service.tasks.return_value = [mock_task]
        mcp_manager_swarm.service = mock_service
        
        with patch.object(mcp_manager_swarm, '_add_log') as mock_add_log:
            await mcp_manager_swarm._read_container_logs()
            
            # Should have logged a warning about no running tasks
            mock_add_log.assert_called_with("WARNING", "No running tasks found for service")
