"""
Shell Command Execution Module for MCP

Provides secure shell command execution capabilities for workflows.
Includes working directory support, timeout handling, and output capture.
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import mcp
from mcp import Context

logger = logging.getLogger(__name__)


class ShellCommandModule:
    """Module for executing shell commands safely within workflows"""
    
    def __init__(self):
        self.logger = logger
        
        # Security: Define allowed commands/patterns
        self.allowed_commands = {
            "git", "npm", "yarn", "pip", "python", "node", "docker", 
            "ls", "pwd", "cat", "echo", "mkdir", "cp", "mv", "rm",
            "curl", "wget", "grep", "find", "sed", "awk"
        }
        
        # Dangerous commands to block
        self.blocked_commands = {
            "sudo", "su", "chmod", "chown", "rm -rf", "format", "fdisk",
            "dd", "mkfs", "mount", "umount", "systemctl", "service"
        }

    def _validate_command(self, command: str) -> bool:
        """
        Validate that the command is safe to execute.
        
        Args:
            command: Shell command to validate
            
        Returns:
            True if command is safe, False otherwise
        """
        command_lower = command.lower().strip()
        
        # Check for blocked commands
        for blocked in self.blocked_commands:
            if blocked in command_lower:
                self.logger.warning(f"Blocked dangerous command: {command}")
                return False
        
        # Extract first word (command name)
        first_word = command.split()[0] if command.split() else ""
        
        # Allow if first word is in allowed commands
        if first_word in self.allowed_commands:
            return True
            
        # Allow relative paths and common patterns
        if first_word.startswith("./") or first_word.startswith("../"):
            return True
            
        self.logger.warning(f"Command not in allowed list: {first_word}")
        return False

    def _validate_working_directory(self, working_dir: str) -> bool:
        """
        Validate that the working directory is safe.
        
        Args:
            working_dir: Directory path to validate
            
        Returns:
            True if directory is safe, False otherwise
        """
        try:
            # Resolve to absolute path
            abs_path = Path(working_dir).resolve()
            
            # Check if directory exists
            if not abs_path.exists():
                self.logger.warning(f"Working directory does not exist: {abs_path}")
                return False
                
            # Check if it's actually a directory
            if not abs_path.is_dir():
                self.logger.warning(f"Working directory is not a directory: {abs_path}")
                return False
                
            # Basic security: don't allow system directories
            system_dirs = {"/bin", "/sbin", "/usr/bin", "/usr/sbin", "/etc", "/sys", "/proc"}
            if str(abs_path) in system_dirs:
                self.logger.warning(f"Access to system directory blocked: {abs_path}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating working directory: {e}")
            return False

    @mcp.tool()
    async def execute_shell_command(
        self,
        ctx: Context,
        command: str,
        working_directory: str = ".",
        timeout: int = 30,
        capture_output: bool = True
    ) -> str:
        """
        Execute shell commands with working directory support.
        
        Provides secure shell command execution for workflows with proper
        validation, timeout handling, and output capture.
        
        Args:
            ctx: MCP context
            command: Shell command to execute
            working_directory: Working directory for command execution
            timeout: Command timeout in seconds (max 300)
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            JSON string with execution results
        """
        try:
            self.logger.info(f"Executing shell command: {command}")
            
            # Validate command safety
            if not self._validate_command(command):
                return json.dumps({
                    "success": False,
                    "error": "Command not allowed for security reasons",
                    "command": command
                })
            
            # Validate and resolve working directory
            if not self._validate_working_directory(working_directory):
                return json.dumps({
                    "success": False,
                    "error": "Invalid or unsafe working directory",
                    "working_directory": working_directory
                })
            
            # Limit timeout for security
            timeout = min(timeout, 300)  # Max 5 minutes
            
            # Resolve working directory
            work_dir = Path(working_directory).resolve()
            
            # Execute command
            if capture_output:
                process = await asyncio.create_subprocess_shell(
                    command,
                    cwd=work_dir,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), 
                        timeout=timeout
                    )
                    
                    result = {
                        "success": process.returncode == 0,
                        "exit_code": process.returncode,
                        "stdout": stdout.decode('utf-8', errors='replace'),
                        "stderr": stderr.decode('utf-8', errors='replace'),
                        "command": command,
                        "working_directory": str(work_dir)
                    }
                    
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    result = {
                        "success": False,
                        "error": f"Command timed out after {timeout} seconds",
                        "command": command,
                        "working_directory": str(work_dir)
                    }
                    
            else:
                # Execute without capturing output
                process = await asyncio.create_subprocess_shell(
                    command,
                    cwd=work_dir
                )
                
                try:
                    await asyncio.wait_for(process.wait(), timeout=timeout)
                    result = {
                        "success": process.returncode == 0,
                        "exit_code": process.returncode,
                        "command": command,
                        "working_directory": str(work_dir)
                    }
                    
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    result = {
                        "success": False,
                        "error": f"Command timed out after {timeout} seconds",
                        "command": command,
                        "working_directory": str(work_dir)
                    }
            
            self.logger.info(f"Command executed | success={result['success']} | exit_code={result.get('exit_code')}")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"Error executing shell command: {e}")
            return json.dumps({
                "success": False,
                "error": f"Execution error: {str(e)}",
                "command": command
            })

    @mcp.tool()
    async def execute_mcp_tool(
        self,
        ctx: Context,
        tool_name: str,
        tool_parameters: Dict[str, Any] = None,
        mcp_server: Optional[str] = None
    ) -> str:
        """
        Execute custom MCP tools by name with parameters.
        
        Allows workflows to call any available MCP tool dynamically,
        providing flexibility for custom integrations.
        
        Args:
            ctx: MCP context
            tool_name: Name of the MCP tool to execute
            tool_parameters: Parameters to pass to the MCP tool
            mcp_server: Specific MCP server to use (optional)
            
        Returns:
            JSON string with tool execution result
        """
        try:
            if tool_parameters is None:
                tool_parameters = {}
                
            self.logger.info(f"Executing MCP tool: {tool_name}")
            
            # TODO: Implement actual MCP tool execution
            # This would integrate with the MCP client to call external tools
            
            # For now, return a placeholder result
            result = {
                "success": True,
                "message": f"MCP tool execution placeholder for {tool_name}",
                "tool_name": tool_name,
                "parameters": tool_parameters,
                "mcp_server": mcp_server,
                "note": "This is a placeholder - actual MCP tool integration needed"
            }
            
            self.logger.info(f"MCP tool executed | tool={tool_name}")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"Error executing MCP tool: {e}")
            return json.dumps({
                "success": False,
                "error": f"MCP tool execution error: {str(e)}",
                "tool_name": tool_name
            })


# Create module instance
shell_module = ShellCommandModule()


def register_shell_tools(mcp_instance):
    """Register shell command tools with the MCP server."""
    logger.info("Registering shell command tools...")

    # Register the shell command execution tool
    mcp_instance.tool()(shell_module.execute_shell_command)

    # Register the MCP tool execution tool
    mcp_instance.tool()(shell_module.execute_mcp_tool)

    logger.info("Shell command tools registered successfully")
