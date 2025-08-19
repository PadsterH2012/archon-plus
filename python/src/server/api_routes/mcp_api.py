"""
MCP API endpoints for Archon

Handles:
- MCP server lifecycle (start/stop/status)
- MCP server configuration management
- WebSocket log streaming
- Tool discovery and testing
"""

import asyncio
import os
import time
from collections import deque
from datetime import datetime
from typing import Any

import docker
from docker.errors import APIError, NotFound
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Import unified logging
from ..config.logfire_config import api_logger, mcp_logger, safe_set_attribute, safe_span
from ..utils import get_supabase_client

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


class ServerConfig(BaseModel):
    transport: str = "sse"
    host: str = "localhost"
    port: int = 8051


class ServerResponse(BaseModel):
    success: bool
    message: str
    status: str | None = None
    pid: int | None = None


class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str


class MCPServerManager:
    """Manages the MCP Docker container lifecycle."""

    def __init__(self):
        # Determine container/service name based on environment
        self.deployment_mode = os.getenv("SERVICE_DISCOVERY_MODE", "docker_compose")

        if self.deployment_mode == "docker_swarm":
            # In Docker Swarm, we need to check if we're in dev or prod environment
            # Use environment variable override or detect from service names
            mcp_host = os.getenv("ARCHON_MCP_HOST")
            if mcp_host and mcp_host.startswith("dev-"):
                # Development environment
                self.container_name = "archon-dev_dev-archon-mcp"
            else:
                # Production environment
                self.container_name = "archon-prod_archon-mcp"
            self.is_swarm_mode = True
        else:
            # Docker Compose mode - use original container name
            self.container_name = os.getenv("MCP_CONTAINER_NAME", "Archon-MCP")
            self.is_swarm_mode = False

        self.docker_client = None
        self.container = None
        self.service = None  # For Docker Swarm mode
        self.status: str = "stopped"
        self.start_time: float | None = None
        self.logs: deque = deque(maxlen=1000)  # Keep last 1000 log entries
        self.log_websockets: list[WebSocket] = []
        self.log_reader_task: asyncio.Task | None = None
        self._operation_lock = asyncio.Lock()  # Prevent concurrent start/stop operations
        self._last_operation_time = 0
        self._min_operation_interval = 2.0  # Minimum 2 seconds between operations
        # Internal debug/control flags
        self._service_log_processor_logged = False  # ensure we log v3 bridge info once
        self._has_emitted_service_logs = False  # seed once when switching to service logs
        self._last_service_log_since: int | None = None  # epoch seconds for 'since' param
        self._initialize_docker_client()

    def _initialize_docker_client(self):
        """Initialize Docker client and get container/service reference."""
        try:
            self.docker_client = docker.from_env()

            if self.is_swarm_mode:
                # In Docker Swarm mode, we work with services, not containers
                try:
                    # Get the service by name
                    self.service = self.docker_client.services.get(self.container_name)
                    mcp_logger.info(f"Found Docker Swarm service: {self.container_name}")
                    self.container = None  # We don't use container reference in swarm mode
                except NotFound:
                    mcp_logger.warning(f"Docker Swarm service {self.container_name} not found")
                    self.service = None
            else:
                # Docker Compose mode - use containers
                try:
                    self.container = self.docker_client.containers.get(self.container_name)
                    mcp_logger.info(f"Found Docker container: {self.container_name}")
                    self.service = None  # We don't use service reference in compose mode
                except NotFound:
                    mcp_logger.warning(f"Docker container {self.container_name} not found")
                    self.container = None
        except Exception as e:
            mcp_logger.error(f"Failed to initialize Docker client: {str(e)}")
            self.docker_client = None

    def _get_container_status(self) -> str:
        """Get the current status of the MCP container/service."""
        if not self.docker_client:
            return "docker_unavailable"

        try:
            if self.is_swarm_mode:
                # Docker Swarm mode - check service status
                if self.service:
                    self.service.reload()  # Refresh service info
                else:
                    self.service = self.docker_client.services.get(self.container_name)

                # In swarm mode, check if service has running tasks
                tasks = self.service.tasks()
                if not tasks:
                    return "not_found"

                # Check if any task is running
                running_tasks = [task for task in tasks if task.get('Status', {}).get('State') == 'running']
                if running_tasks:
                    return "running"
                else:
                    # Check for other states
                    latest_task = max(tasks, key=lambda t: t.get('CreatedAt', ''))
                    task_state = latest_task.get('Status', {}).get('State', 'unknown')
                    return task_state
            else:
                # Docker Compose mode - check container status
                if self.container:
                    self.container.reload()  # Refresh container info
                else:
                    self.container = self.docker_client.containers.get(self.container_name)

                return self.container.status
        except NotFound:
            return "not_found"
        except Exception as e:
            mcp_logger.error(f"Error getting container/service status: {str(e)}")
            return "error"

    def _is_log_reader_active(self) -> bool:
        """Check if the log reader task is active."""
        return self.log_reader_task is not None and not self.log_reader_task.done()

    async def _ensure_log_reader_running(self):
        """Ensure the log reader task is running if container is active."""
        # Check if we have a container (Compose mode) or service (Swarm mode)
        if not self.container and not self.service:
            self._add_log("DEBUG", "No container or service available for log reading")
            return

        # Cancel existing task if any
        if self.log_reader_task:
            self.log_reader_task.cancel()
            try:
                await self.log_reader_task
            except asyncio.CancelledError:
                pass

        # Start new log reader task
        self.log_reader_task = asyncio.create_task(self._read_container_logs())
        self._add_log("INFO", "Connected to MCP container logs")

        if self.is_swarm_mode:
            self._add_log("DEBUG", f"Started log reader for Swarm service: {self.container_name}")
            mcp_logger.info(f"Started log reader for Swarm service: {self.container_name}")
        else:
            self._add_log("DEBUG", f"Started log reader for Compose container: {self.container_name}")
            mcp_logger.info(f"Started log reader for Compose container: {self.container_name}")

    async def start_server(self) -> dict[str, Any]:
        """Start the MCP Docker container."""
        async with self._operation_lock:
            # Check throttling
            current_time = time.time()
            if current_time - self._last_operation_time < self._min_operation_interval:
                wait_time = self._min_operation_interval - (
                    current_time - self._last_operation_time
                )
                mcp_logger.warning(f"Start operation throttled, please wait {wait_time:.1f}s")
                return {
                    "success": False,
                    "status": self.status,
                    "message": f"Please wait {wait_time:.1f}s before starting server again",
                }

        with safe_span("mcp_server_start") as span:
            safe_set_attribute(span, "action", "start_server")

            if not self.docker_client:
                mcp_logger.error("Docker client not available")
                return {
                    "success": False,
                    "status": "docker_unavailable",
                    "message": "Docker is not available. Is Docker socket mounted?",
                }

            # Check current container status
            container_status = self._get_container_status()

            if container_status == "not_found":
                if self.is_swarm_mode:
                    mcp_logger.error(f"Service {self.container_name} not found")
                    return {
                        "success": False,
                        "status": "not_found",
                        "message": f"MCP service {self.container_name} not found. Check Docker Swarm deployment.",
                    }
                else:
                    mcp_logger.error(f"Container {self.container_name} not found")
                    return {
                        "success": False,
                        "status": "not_found",
                        "message": f"MCP container {self.container_name} not found. Run docker-compose up -d archon-mcp",
                    }

            if container_status == "running":
                if self.is_swarm_mode:
                    # In Swarm mode, service is managed by orchestrator, but we can start log reading
                    self.status = "running"
                    self.start_time = time.time()

                    # Start log reader if not already active
                    if not self._is_log_reader_active():
                        await self._ensure_log_reader_running()

                    mcp_logger.info("MCP service is already running in Docker Swarm")
                    return {
                        "success": True,
                        "status": "running",
                        "message": "MCP service is running in Docker Swarm (managed by orchestrator)",
                    }
                else:
                    mcp_logger.warning("MCP server start attempted while already running")
                    return {
                        "success": False,
                        "status": "running",
                        "message": "MCP server is already running",
                    }

            try:
                # Start the container
                self.container.start()
                self.status = "starting"
                self.start_time = time.time()
                self._last_operation_time = time.time()
                self._add_log("INFO", "MCP container starting...")
                mcp_logger.info(f"Starting MCP container: {self.container_name}")
                safe_set_attribute(span, "container_id", self.container.id)

                # Start reading logs from the container
                if self.log_reader_task:
                    self.log_reader_task.cancel()
                self.log_reader_task = asyncio.create_task(self._read_container_logs())

                # Give it a moment to start
                await asyncio.sleep(2)

                # Check if container is running
                self.container.reload()
                if self.container.status == "running":
                    self.status = "running"
                    self._add_log("INFO", "MCP container started successfully")
                    mcp_logger.info(
                        f"MCP container started successfully - container_id={self.container.id}"
                    )
                    safe_set_attribute(span, "success", True)
                    safe_set_attribute(span, "status", "running")
                    return {
                        "success": True,
                        "status": self.status,
                        "message": "MCP server started successfully",
                        "container_id": self.container.id[:12],
                    }
                else:
                    self.status = "failed"
                    self._add_log(
                        "ERROR", f"MCP container failed to start. Status: {self.container.status}"
                    )
                    mcp_logger.error(
                        f"MCP container failed to start - status: {self.container.status}"
                    )
                    safe_set_attribute(span, "success", False)
                    safe_set_attribute(span, "status", self.container.status)
                    return {
                        "success": False,
                        "status": self.status,
                        "message": f"MCP container failed to start. Status: {self.container.status}",
                    }

            except APIError as e:
                self.status = "failed"
                self._add_log("ERROR", f"Docker API error: {str(e)}")
                mcp_logger.error(f"Docker API error during MCP startup - error={str(e)}")
                safe_set_attribute(span, "success", False)
                safe_set_attribute(span, "error", str(e))
                return {
                    "success": False,
                    "status": self.status,
                    "message": f"Docker API error: {str(e)}",
                }
            except Exception as e:
                self.status = "failed"
                self._add_log("ERROR", f"Failed to start MCP server: {str(e)}")
                mcp_logger.error(
                    f"Exception during MCP server startup - error={str(e)}, error_type={type(e).__name__}"
                )
                safe_set_attribute(span, "success", False)
                safe_set_attribute(span, "error", str(e))
                return {
                    "success": False,
                    "status": self.status,
                    "message": f"Failed to start MCP server: {str(e)}",
                }

    async def stop_server(self) -> dict[str, Any]:
        """Stop the MCP Docker container."""
        async with self._operation_lock:
            # Check throttling
            current_time = time.time()
            if current_time - self._last_operation_time < self._min_operation_interval:
                wait_time = self._min_operation_interval - (
                    current_time - self._last_operation_time
                )
                mcp_logger.warning(f"Stop operation throttled, please wait {wait_time:.1f}s")
                return {
                    "success": False,
                    "status": self.status,
                    "message": f"Please wait {wait_time:.1f}s before stopping server again",
                }

        with safe_span("mcp_server_stop") as span:
            safe_set_attribute(span, "action", "stop_server")

            if not self.docker_client:
                mcp_logger.error("Docker client not available")
                return {
                    "success": False,
                    "status": "docker_unavailable",
                    "message": "Docker is not available",
                }

            # Check current container status
            container_status = self._get_container_status()

            if container_status not in ["running", "restarting"]:
                mcp_logger.warning(
                    f"MCP server stop attempted when not running. Status: {container_status}"
                )
                return {
                    "success": False,
                    "status": container_status,
                    "message": f"MCP server is not running (status: {container_status})",
                }

            try:
                self.status = "stopping"
                self._add_log("INFO", "Stopping MCP container...")
                mcp_logger.info(f"Stopping MCP container: {self.container_name}")
                safe_set_attribute(span, "container_id", self.container.id)

                # Cancel log reading task
                if self.log_reader_task:
                    self.log_reader_task.cancel()
                    try:
                        await self.log_reader_task
                    except asyncio.CancelledError:
                        pass

                # Stop the container with timeout
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.container.stop(timeout=10),  # 10 second timeout
                )

                self.status = "stopped"
                self.start_time = None
                self._last_operation_time = time.time()
                self._add_log("INFO", "MCP container stopped")
                mcp_logger.info("MCP container stopped successfully")
                safe_set_attribute(span, "success", True)
                safe_set_attribute(span, "status", "stopped")

                return {
                    "success": True,
                    "status": self.status,
                    "message": "MCP server stopped successfully",
                }

            except APIError as e:
                self._add_log("ERROR", f"Docker API error: {str(e)}")
                mcp_logger.error(f"Docker API error during MCP stop - error={str(e)}")
                safe_set_attribute(span, "success", False)
                safe_set_attribute(span, "error", str(e))
                return {
                    "success": False,
                    "status": self.status,
                    "message": f"Docker API error: {str(e)}",
                }
            except Exception as e:
                self._add_log("ERROR", f"Error stopping MCP server: {str(e)}")
                mcp_logger.error(
                    f"Exception during MCP server stop - error={str(e)}, error_type={type(e).__name__}"
                )
                safe_set_attribute(span, "success", False)
                safe_set_attribute(span, "error", str(e))
                return {
                    "success": False,
                    "status": self.status,
                    "message": f"Error stopping MCP server: {str(e)}",
                }

    def get_status(self) -> dict[str, Any]:
        """Get the current server status."""
        # Update status based on actual container state
        container_status = self._get_container_status()

        # Map Docker statuses to our statuses
        status_map = {
            "running": "running",
            "restarting": "restarting",
            "paused": "paused",
            "exited": "stopped",
            "dead": "stopped",
            "created": "stopped",
            "removing": "stopping",
            "not_found": "not_found",
            "docker_unavailable": "docker_unavailable",
            "error": "error",
        }

        self.status = status_map.get(container_status, "unknown")

        # If container is running but log reader isn't active, start it
        if self.status == "running" and not self._is_log_reader_active():
            self._add_log("DEBUG", f"Status is running but log reader not active. Starting log reader. Container: {self.container is not None}, Service: {self.service is not None}")
            asyncio.create_task(self._ensure_log_reader_running())

        uptime = None
        if self.status == "running" and self.start_time:
            uptime = int(time.time() - self.start_time)
        elif self.status == "running" and self.container:
            # Try to get uptime from container info
            try:
                self.container.reload()
                started_at = self.container.attrs["State"]["StartedAt"]
                # Parse ISO format datetime
                from datetime import datetime

                started_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                uptime = int((datetime.now(started_time.tzinfo) - started_time).total_seconds())
            except Exception:
                pass

        # Convert log entries to strings for backward compatibility
        recent_logs = []
        for log in list(self.logs)[-10:]:
            if isinstance(log, dict):
                recent_logs.append(f"[{log['level']}] {log['message']}")
            else:
                recent_logs.append(str(log))

        return {
            "status": self.status,
            "uptime": uptime,
            "logs": recent_logs,
            "container_status": container_status,  # Include raw Docker status
        }

    def _add_log(self, level: str, message: str):
        """Add a log entry and broadcast to connected WebSockets."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "message": message,
        }
        self.logs.append(log_entry)

        # Broadcast to all connected WebSockets
        asyncio.create_task(self._broadcast_log(log_entry))

    async def _broadcast_log(self, log_entry: dict[str, Any]):
        """Broadcast log entry to all connected WebSockets."""
        disconnected = []
        for ws in self.log_websockets:
            try:
                await ws.send_json(log_entry)
            except Exception:
                disconnected.append(ws)

        # Remove disconnected WebSockets
        for ws in disconnected:
            self.log_websockets.remove(ws)

    async def _read_container_logs(self):
        """Read logs from Docker container or service."""
        container_to_read = None

        try:
            if self.is_swarm_mode and self.service:
                # In Docker Swarm mode, get the actual container from service tasks
                tasks = self.service.tasks()
                running_tasks = [task for task in tasks if task.get('Status', {}).get('State') == 'running']

                if not running_tasks:
                    self._add_log("WARNING", "No running tasks found for service")
                    return

                # Debug: log task information
                self._add_log("DEBUG", f"Found {len(running_tasks)} running tasks for service")

                # Get the container ID from the first running task
                task = running_tasks[0]
                container_id = task.get('Status', {}).get('ContainerStatus', {}).get('ContainerID')

                if not container_id:
                    self._add_log("WARNING", "Could not find container ID from service task")
                    return

                # Debug: log the container ID we found and task details
                self._add_log("DEBUG", f"Found container ID from task: {container_id[:12]}...{container_id[-12:] if len(container_id) > 24 else ''}")

                # Debug: log task node information
                node_id = task.get('NodeID', 'unknown')
                task_slot = task.get('Slot', 'unknown')
                self._add_log("DEBUG", f"Task running on node: {node_id}, slot: {task_slot}")

                # Try different approaches to get the container
                try:
                    # First try with full container ID
                    container_to_read = self.docker_client.containers.get(container_id)
                    self._add_log("INFO", f"Reading logs from Swarm service container: {container_id[:12]}")
                except Exception as e:
                    # If full ID fails, try with short ID (first 12 characters)
                    short_id = container_id[:12]
                    try:
                        container_to_read = self.docker_client.containers.get(short_id)
                        self._add_log("INFO", f"Reading logs from Swarm service container (short ID): {short_id}")
                    except Exception as e2:
                        # If both fail, try to find container by listing all containers
                        try:
                            all_containers = self.docker_client.containers.list(all=True)
                            self._add_log("DEBUG", f"Found {len(all_containers)} total containers on this node")

                            matching_container = None
                            for container in all_containers:
                                if container.id.startswith(container_id[:12]) or container_id.startswith(container.id[:12]):
                                    matching_container = container
                                    break

                            if matching_container:
                                container_to_read = matching_container
                                self._add_log("INFO", f"Found matching container: {matching_container.id[:12]}")
                            else:
                                # In Swarm mode, container might be on different node - try service logs instead
                                self._add_log("WARNING", f"Container not found on this node. Task container ID: {container_id[:12]}, tried full ID and short ID")
                                self._add_log("INFO", "Attempting to read logs directly from service instead of container")

                                # Try to read logs from the service directly using polling
                                try:
                                    self._add_log("INFO", "Starting service log polling (service logs don't support streaming)")
                                    self._add_log("DEBUG", f"Service ID: {self.service.id}, Service name: {self.service.name}")

                                    # Use polling approach for service logs since streaming isn't supported
                                    # Force an initial seed of recent logs regardless of internal debug buffer content
                                    first_poll = True
                                    self._has_emitted_service_logs = False
                                    self._add_log("INFO", "Service logs mode engaged; initial seed will be attempted")
                                    poll_interval = 2  # Poll every 2 seconds
                                    processed_log_hashes = set()  # Track processed logs by hash to avoid duplicates

                                    while True:
                                        try:
                                            # Get recent logs from service
                                            self._add_log("DEBUG", "Attempting to fetch service logs...")
                                            # Build parameters for service logs fetch
                                            def _fetch_service_logs():
                                                # Always fetch a recent tail and dedup in-process; 'since' support is unreliable
                                                return self.service.logs(timestamps=True, stdout=True, stderr=True, tail=50)
                                            logs_generator = await asyncio.get_event_loop().run_in_executor(
                                                None, _fetch_service_logs
                                            )

                                            self._add_log("DEBUG", f"Service logs generator type: {type(logs_generator)}")

                                            if logs_generator:
                                                # Process logs from generator
                                                log_lines = []
                                                log_count = 0
                                                try:
                                                    # Convert generator to list of log lines
                                                    for log_entry in logs_generator:
                                                        log_count += 1
                                                        if isinstance(log_entry, bytes):
                                                            log_entry = log_entry.decode("utf-8")
                                                        if log_entry.strip():
                                                            log_lines.append(log_entry.strip())

                                                    self._add_log("DEBUG", f"Processed {log_count} log entries, {len(log_lines)} non-empty lines")

                                                    # Process the log lines
                                                    try:
                                                        if not self._service_log_processor_logged:
                                                            self._add_log("INFO", "Using v3 service log processor (bridge to main async context)")
                                                            self._service_log_processor_logged = True

                                                        parsed_logs, new_hashes, _ = self._process_service_log_lines_v3(log_lines, first_poll, processed_log_hashes)
                                                        processed_log_hashes.update(new_hashes)
                                                        first_poll = False  # After first poll, only show new logs

                                                        # Add the parsed logs to the main async context
                                                        self._add_log("INFO", f"MCP log bridge: about to append {len(parsed_logs)} parsed logs to buffer")
                                                        for level, message in parsed_logs:
                                                            self._add_log(level, message)
                                                        self._add_log("INFO", f"MCP log bridge: buffer size now {len(self.logs)}")

                                                        if parsed_logs:
                                                            self._add_log("DEBUG", f"Added {len(parsed_logs)} logs to dashboard from service logs")

                                                    except Exception as process_error:
                                                        self._add_log("ERROR", f"Error processing log lines: {str(process_error)}")
                                                        # Show first few lines for debugging even if processing fails
                                                        for i, line in enumerate(log_lines[:3]):
                                                            self._add_log("DEBUG", f"Failed processing line {i}: {line[:100]}...")

                                                except Exception as gen_error:
                                                    self._add_log("ERROR", f"Error processing log generator: {str(gen_error)}")
                                                    continue
                                            else:
                                                self._add_log("DEBUG", "No logs generator returned from service")



                                            # Wait before next poll
                                            await asyncio.sleep(poll_interval)

                                        except Exception as e:
                                            self._add_log("ERROR", f"Service log polling error: {str(e)}")
                                            await asyncio.sleep(poll_interval)

                                    return  # Exit the function as we're reading from service logs

                                except Exception as service_log_error:
                                    self._add_log("ERROR", f"Failed to read service logs: {str(service_log_error)}")
                                    return
                        except Exception as e3:
                            self._add_log("ERROR", f"Failed to find container: {str(e3)}")
                            return

            elif not self.is_swarm_mode and self.container:
                # Docker Compose mode - use the container directly
                container_to_read = self.container
                self._add_log("INFO", f"Reading logs from Compose container: {self.container.id[:12]}")
            else:
                self._add_log("WARNING", "No container or service available for log reading")
                return

            # Stream logs from container
            log_generator = container_to_read.logs(stream=True, follow=True, tail=100)

            while True:
                try:
                    log_line = await asyncio.get_event_loop().run_in_executor(
                        None, next, log_generator, None
                    )

                    if log_line is None:
                        break

                    # Decode bytes to string
                    if isinstance(log_line, bytes):
                        log_line = log_line.decode("utf-8").strip()

                    if log_line:
                        level, message = self._parse_log_line(log_line)
                        self._add_log(level, message)

                except StopIteration:
                    break
                except Exception as e:
                    self._add_log("ERROR", f"Log reading error: {str(e)}")
                    break

        except asyncio.CancelledError:
            pass
        except APIError as e:
            if "container not found" not in str(e).lower():
                self._add_log("ERROR", f"Docker API error reading logs: {str(e)}")
        except Exception as e:
            self._add_log("ERROR", f"Error reading container logs: {str(e)}")
        finally:
            # Check if container stopped
            try:
                self.container.reload()
                if self.container.status not in ["running", "restarting"]:
                    self._add_log(
                        "INFO", f"MCP container stopped with status: {self.container.status}"
                    )
            except Exception:
                pass

    def _process_service_log_lines(self, log_lines, last_timestamp):
        """Process log lines from Docker service logs."""
        new_logs_added = 0

        self._add_log("DEBUG", f"Starting to process {len(log_lines)} log lines")

        for i, log_line in enumerate(log_lines):
            if log_line.strip():
                # Debug first few log lines to understand format
                if i < 3:
                    self._add_log("DEBUG", f"Sample log line {i}: {log_line[:100]}...")

                # Parse timestamp if present
                if log_line.startswith('20') and 'T' in log_line[:20]:
                    # Extract timestamp and message
                    parts = log_line.split(' ', 1)
                    if len(parts) >= 2:
                        timestamp = parts[0]
                        message = parts[1]

                        # Skip if we've seen this timestamp before
                        if last_timestamp and timestamp <= last_timestamp:
                            if i < 3:
                                self._add_log("DEBUG", f"Skipping log with timestamp {timestamp} (last: {last_timestamp})")
                            continue

                        last_timestamp = timestamp
                        level, parsed_message = self._parse_log_line(message)
                        self._add_log(level, parsed_message)
                        new_logs_added += 1
                else:
                    # No timestamp, just process the line - but only if it's the first poll
                    if last_timestamp is None:
                        level, parsed_message = self._parse_log_line(log_line)
                        self._add_log(level, parsed_message)
                        new_logs_added += 1
                    elif i < 3:
                        self._add_log("DEBUG", f"Skipping non-timestamped log: {log_line[:50]}...")

        self._add_log("DEBUG", f"Added {new_logs_added} new log entries this poll (last_timestamp: {last_timestamp})")
        return last_timestamp

    def _process_service_log_lines_v2(self, log_lines, first_poll, processed_log_hashes):
        """Process log lines from Docker service logs using hash-based deduplication."""
        import hashlib

        new_logs_added = 0
        new_hashes = set()

        # If we have no logs in our buffer yet, treat this as first poll to show recent logs
        current_log_count = len(self.logs)
        treat_as_first_poll = first_poll or current_log_count == 0

        self._add_log("DEBUG", f"Processing {len(log_lines)} log lines (first_poll: {first_poll}, current_logs: {current_log_count}, treat_as_first: {treat_as_first_poll})")

        for i, log_line in enumerate(log_lines):
            if log_line.strip():
                # Create hash of log line for deduplication
                log_hash = hashlib.md5(log_line.encode()).hexdigest()

                # Debug first few log lines to understand format
                if i < 3:
                    self._add_log("DEBUG", f"Sample log line {i}: {log_line[:100]}...")

                # On first poll or when no logs exist, show recent logs. On subsequent polls, only show new logs
                if treat_as_first_poll:
                    # Show all logs on first poll, but track them
                    processed_log_hashes.add(log_hash)
                    new_hashes.add(log_hash)

                    # Extract message from timestamped log
                    if log_line.startswith('20') and 'T' in log_line[:20]:
                        parts = log_line.split(' ', 1)
                        if len(parts) >= 2:
                            message = parts[1]
                            level, parsed_message = self._parse_log_line(message)
                            self._add_log(level, parsed_message)
                            new_logs_added += 1
                    else:
                        level, parsed_message = self._parse_log_line(log_line)
                        self._add_log(level, parsed_message)
                        new_logs_added += 1
                else:
                    # Only show logs we haven't seen before
                    if log_hash not in processed_log_hashes:
                        new_hashes.add(log_hash)

                        # Extract message from timestamped log
                        if log_line.startswith('20') and 'T' in log_line[:20]:
                            parts = log_line.split(' ', 1)
                            if len(parts) >= 2:
                                message = parts[1]
                                level, parsed_message = self._parse_log_line(message)
                                self._add_log(level, parsed_message)
                                new_logs_added += 1
                        else:
                            level, parsed_message = self._parse_log_line(log_line)
                            self._add_log(level, parsed_message)
                            new_logs_added += 1

        self._add_log("DEBUG", f"Added {new_logs_added} new log entries this poll")
        return new_hashes

    def _process_service_log_lines_v3(self, log_lines, first_poll, processed_log_hashes):
        """Process log lines, return parsed logs and update last-seen timestamp.
        NOTE: Do not call _add_log from here (executor thread)."""
        import hashlib
        import datetime

        parsed_logs = []
        new_hashes = set()
        latest_ts = None  # track latest Docker timestamp seen

        # Seed on first run of service logs, regardless of buffer containing internal debug
        treat_as_first_poll = first_poll or (not self._has_emitted_service_logs)

        for i, log_line in enumerate(log_lines):
            line = log_line.strip()
            if not line:
                continue

            # Docker service adds RFC3339 timestamp before app log; split once
            ts_str = None
            msg_part = line
            if line.startswith('20') and 'T' in line[:20]:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    ts_str, msg_part = parts[0], parts[1]
                    # Track latest timestamp
                    try:
                        # RFC3339 with nanoseconds; trim to microseconds for Python
                        ts_norm = ts_str.rstrip('Z')
                        # allow variable fractional seconds
                        if '.' in ts_norm:
                            date_part, frac = ts_norm.split('.')
                            # keep microseconds precision
                            ts_parse = datetime.datetime.fromisoformat(f"{date_part}.{frac[:6]}")
                        else:
                            ts_parse = datetime.datetime.fromisoformat(ts_norm)
                        if latest_ts is None or ts_parse > latest_ts:
                            latest_ts = ts_parse
                    except Exception:
                        pass

            # Dedup on inner message (not Docker timestamp)
            log_hash = hashlib.md5(msg_part.encode()).hexdigest()

            if treat_as_first_poll:
                processed_log_hashes.add(log_hash)
                new_hashes.add(log_hash)
                level, parsed_message = self._parse_log_line(msg_part)
                parsed_logs.append((level, parsed_message))
            else:
                if log_hash not in processed_log_hashes:
                    new_hashes.add(log_hash)
                    level, parsed_message = self._parse_log_line(msg_part)
                    parsed_logs.append((level, parsed_message))

        # Update state: after first emission, flip the flag
        if treat_as_first_poll:
            self._has_emitted_service_logs = True

        # Convert latest_ts to epoch seconds for 'since'
        latest_since = None
        if latest_ts is not None:
            try:
                latest_since = int(latest_ts.timestamp())
            except Exception:
                latest_since = None

        return parsed_logs, new_hashes, latest_since

    def _parse_log_line(self, line: str) -> tuple[str, str]:
        """Parse a log line to extract level and message."""
        line = line.strip()
        if not line:
            return "INFO", ""

        # Try to extract log level from common formats
        if line.startswith("[") and "]" in line:
            end_bracket = line.find("]")
            potential_level = line[1:end_bracket].upper()
            if potential_level in ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]:
                return potential_level, line[end_bracket + 1 :].strip()

        # Check for common log level indicators
        line_lower = line.lower()
        if any(word in line_lower for word in ["error", "exception", "failed", "critical"]):
            return "ERROR", line
        elif any(word in line_lower for word in ["warning", "warn"]):
            return "WARNING", line
        elif any(word in line_lower for word in ["debug"]):
            return "DEBUG", line
        else:
            return "INFO", line

    def get_logs(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get historical logs."""
        logs = list(self.logs)
        if limit > 0:
            logs = logs[-limit:]
        return logs

    def clear_logs(self):
        """Clear the log buffer."""
        self.logs.clear()
        self._add_log("INFO", "Logs cleared")

    async def add_websocket(self, websocket: WebSocket):
        """Add a WebSocket connection for log streaming."""
        await websocket.accept()
        self.log_websockets.append(websocket)

        # Send connection info but NOT historical logs
        # The frontend already fetches historical logs via the /logs endpoint
        await websocket.send_json({
            "type": "connection",
            "message": "WebSocket connected for log streaming",
        })

    def remove_websocket(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.log_websockets:
            self.log_websockets.remove(websocket)


# Global MCP manager instance
mcp_manager = MCPServerManager()


@router.post("/start", response_model=ServerResponse)
async def start_server():
    """Start the MCP server."""
    with safe_span("api_mcp_start") as span:
        safe_set_attribute(span, "endpoint", "/mcp/start")
        safe_set_attribute(span, "method", "POST")

        try:
            result = await mcp_manager.start_server()
            api_logger.info(
                "MCP server start API called - success=%s", result.get("success", False)
            )
            safe_set_attribute(span, "success", result.get("success", False))
            return result
        except Exception as e:
            api_logger.error("MCP server start API failed - error=%s", str(e))
            safe_set_attribute(span, "success", False)
            safe_set_attribute(span, "error", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=ServerResponse)
async def stop_server():
    """Stop the MCP server."""
    with safe_span("api_mcp_stop") as span:
        safe_set_attribute(span, "endpoint", "/mcp/stop")
        safe_set_attribute(span, "method", "POST")

        try:
            result = await mcp_manager.stop_server()
            api_logger.info(f"MCP server stop API called - success={result.get('success', False)}")
            safe_set_attribute(span, "success", result.get("success", False))
            return result
        except Exception as e:
            api_logger.error(f"MCP server stop API failed - error={str(e)}")
            safe_set_attribute(span, "success", False)
            safe_set_attribute(span, "error", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get MCP server status."""
    with safe_span("api_mcp_status") as span:
        safe_set_attribute(span, "endpoint", "/mcp/status")
        safe_set_attribute(span, "method", "GET")

        try:
            status = mcp_manager.get_status()
            api_logger.debug(f"MCP server status checked - status={status.get('status')}")
            safe_set_attribute(span, "status", status.get("status"))
            safe_set_attribute(span, "uptime", status.get("uptime"))
            return status
        except Exception as e:
            api_logger.error(f"MCP server status API failed - error={str(e)}")
            safe_set_attribute(span, "error", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_logs(limit: int = 100):
    """Get MCP server logs."""
    with safe_span("api_mcp_logs") as span:
        safe_set_attribute(span, "endpoint", "/mcp/logs")
        safe_set_attribute(span, "method", "GET")
        safe_set_attribute(span, "limit", limit)

        try:
            logs = mcp_manager.get_logs(limit)
            api_logger.debug("MCP server logs retrieved", count=len(logs))
            safe_set_attribute(span, "log_count", len(logs))
            return {"logs": logs}
        except Exception as e:
            api_logger.error("MCP server logs API failed", error=str(e))
            safe_set_attribute(span, "error", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@router.delete("/logs")
async def clear_logs():
    """Clear MCP server logs."""
    with safe_span("api_mcp_clear_logs") as span:
        safe_set_attribute(span, "endpoint", "/mcp/logs")
        safe_set_attribute(span, "method", "DELETE")

        try:
            mcp_manager.clear_logs()
            api_logger.info("MCP server logs cleared")
            safe_set_attribute(span, "success", True)
            return {"success": True, "message": "Logs cleared successfully"}
        except Exception as e:
            api_logger.error("MCP server clear logs API failed", error=str(e))
            safe_set_attribute(span, "success", False)
            safe_set_attribute(span, "error", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_mcp_config():
    """Get MCP server configuration."""
    with safe_span("api_get_mcp_config") as span:
        safe_set_attribute(span, "endpoint", "/api/mcp/config")
        safe_set_attribute(span, "method", "GET")

        try:
            api_logger.info("Getting MCP server configuration")

            # Get actual MCP port and host from environment or use defaults
            import os

            # Use external MCP port for client connections, fall back to internal port
            mcp_port = int(os.getenv("MCP_EXTERNAL_PORT", os.getenv("ARCHON_MCP_PORT", "8051")))
            # Use MCP_HOST environment variable or fall back to localhost
            mcp_host = os.getenv("MCP_HOST", "localhost")

            # Configuration for SSE-only mode with actual host and port
            config = {
                "host": mcp_host,
                "port": mcp_port,
                "transport": "sse",
            }

            # Get only model choice from database
            try:
                from ..services.credential_service import credential_service

                model_choice = await credential_service.get_credential(
                    "MODEL_CHOICE", "gpt-4o-mini"
                )
                config["model_choice"] = model_choice
                config["use_contextual_embeddings"] = (
                    await credential_service.get_credential("USE_CONTEXTUAL_EMBEDDINGS", "false")
                ).lower() == "true"
                config["use_hybrid_search"] = (
                    await credential_service.get_credential("USE_HYBRID_SEARCH", "false")
                ).lower() == "true"
                config["use_agentic_rag"] = (
                    await credential_service.get_credential("USE_AGENTIC_RAG", "false")
                ).lower() == "true"
                config["use_reranking"] = (
                    await credential_service.get_credential("USE_RERANKING", "false")
                ).lower() == "true"
            except Exception:
                # Fallback to default model
                config["model_choice"] = "gpt-4o-mini"
                config["use_contextual_embeddings"] = False
                config["use_hybrid_search"] = False
                config["use_agentic_rag"] = False
                config["use_reranking"] = False

            api_logger.info("MCP configuration (SSE-only mode)")
            safe_set_attribute(span, "host", config["host"])
            safe_set_attribute(span, "port", config["port"])
            safe_set_attribute(span, "transport", "sse")
            safe_set_attribute(span, "model_choice", config.get("model_choice", "gpt-4o-mini"))

            return config
        except Exception as e:
            api_logger.error("Failed to get MCP configuration", error=str(e))
            safe_set_attribute(span, "error", str(e))
            raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/config")
async def save_configuration(config: ServerConfig):
    """Save MCP server configuration."""
    with safe_span("api_save_mcp_config") as span:
        safe_set_attribute(span, "endpoint", "/api/mcp/config")
        safe_set_attribute(span, "method", "POST")
        safe_set_attribute(span, "transport", config.transport)
        safe_set_attribute(span, "host", config.host)
        safe_set_attribute(span, "port", config.port)

        try:
            api_logger.info(
                f"Saving MCP server configuration | transport={config.transport} | host={config.host} | port={config.port}"
            )
            supabase_client = get_supabase_client()

            config_json = config.model_dump_json()

            # Save MCP config using credential service
            from ..services.credential_service import credential_service

            success = await credential_service.set_credential(
                "mcp_config",
                config_json,
                category="mcp",
                description="MCP server configuration settings",
            )

            if success:
                api_logger.info("MCP configuration saved successfully")
                safe_set_attribute(span, "operation", "save")
            else:
                raise Exception("Failed to save MCP configuration")

            safe_set_attribute(span, "success", True)
            return {"success": True, "message": "Configuration saved"}

        except Exception as e:
            api_logger.error(f"Failed to save MCP configuration | error={str(e)}")
            safe_set_attribute(span, "error", str(e))
            raise HTTPException(status_code=500, detail={"error": str(e)})


@router.websocket("/logs/stream")
async def websocket_log_stream(websocket: WebSocket):
    """WebSocket endpoint for streaming MCP server logs."""
    await mcp_manager.add_websocket(websocket)
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
            # Check if WebSocket is still connected
            await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        mcp_manager.remove_websocket(websocket)
    except Exception:
        mcp_manager.remove_websocket(websocket)
        try:
            await websocket.close()
        except:
            pass


@router.get("/tools")
async def get_mcp_tools():
    """Get available MCP tools by querying the running MCP server's registered tools."""
    with safe_span("api_get_mcp_tools") as span:
        safe_set_attribute(span, "endpoint", "/api/mcp/tools")
        safe_set_attribute(span, "method", "GET")

        try:
            api_logger.info("Getting MCP tools from registered server instance")

            # Check if server is running
            server_status = mcp_manager.get_status()
            is_running = server_status.get("status") == "running"
            safe_set_attribute(span, "server_running", is_running)

            if not is_running:
                api_logger.warning("MCP server not running when requesting tools")
                return {
                    "tools": [],
                    "count": 0,
                    "server_running": False,
                    "source": "server_not_running",
                    "message": "MCP server is not running. Start the server to see available tools.",
                }

            # SIMPLE DEBUG: Just check if we can see any tools at all
            try:
                # Try to inspect the process to see what tools exist
                api_logger.info("Debugging: Attempting to check MCP server tools")

                # For now, just return the known modules info since server is registering them
                # This will at least show the UI that tools exist while we debug the real issue
                if is_running:
                    return {
                        "tools": [
                            {
                                "name": "debug_placeholder",
                                "description": "MCP server is running and modules are registered, but tool introspection is not working yet",
                                "module": "debug",
                                "parameters": [],
                            }
                        ],
                        "count": 1,
                        "server_running": True,
                        "source": "debug_placeholder",
                        "message": "MCP server is running with 3 modules registered. Tool introspection needs to be fixed.",
                    }
                else:
                    return {
                        "tools": [],
                        "count": 0,
                        "server_running": False,
                        "source": "server_not_running",
                        "message": "MCP server is not running. Start the server to see available tools.",
                    }

            except Exception as e:
                api_logger.error("Failed to debug MCP server tools", error=str(e))

                return {
                    "tools": [],
                    "count": 0,
                    "server_running": is_running,
                    "source": "debug_error",
                    "message": f"Debug failed: {str(e)}",
                }

        except Exception as e:
            api_logger.error("Failed to get MCP tools", error=str(e))
            safe_set_attribute(span, "error", str(e))
            safe_set_attribute(span, "source", "general_error")

            return {
                "tools": [],
                "count": 0,
                "server_running": False,
                "source": "general_error",
                "message": f"Error retrieving MCP tools: {str(e)}",
            }


@router.get("/health")
async def mcp_health():
    """Health check for MCP API."""
    with safe_span("api_mcp_health") as span:
        safe_set_attribute(span, "endpoint", "/api/mcp/health")
        safe_set_attribute(span, "method", "GET")

        # Removed health check logging to reduce console noise
        result = {"status": "healthy", "service": "mcp"}
        safe_set_attribute(span, "status", "healthy")

        return result
