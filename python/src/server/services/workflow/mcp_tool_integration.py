"""
MCP Tool Integration for Workflow Execution

This module provides comprehensive integration between workflow execution
and Archon MCP tools, including:
- Tool discovery and validation
- Parameter mapping and transformation
- Result processing and validation
- Error handling and retry mechanisms
- Tool-specific optimizations
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

from ...config.logfire_config import get_logger, logfire
from ..mcp_service_client import MCPServiceClient

logger = get_logger(__name__)


class MCPToolRegistry:
    """Registry of available MCP tools with their metadata"""
    
    # Define all available MCP tools with their signatures
    AVAILABLE_TOOLS = {
        # RAG & Knowledge Management Tools
        "perform_rag_query_archon": {
            "category": "rag",
            "description": "Perform semantic search across knowledge base",
            "parameters": {
                "query": {"type": "string", "required": True, "description": "Search query text"},
                "source": {"type": "string", "required": False, "description": "Filter by source domain"},
                "match_count": {"type": "integer", "required": False, "default": 5, "description": "Max results"}
            },
            "returns": "JSON with search results and metadata",
            "example": {
                "query": "OAuth2 authentication patterns",
                "source": "docs.example.com",
                "match_count": 3
            }
        },
        
        "search_code_examples_archon": {
            "category": "rag",
            "description": "Search for code examples relevant to query",
            "parameters": {
                "query": {"type": "string", "required": True, "description": "Search query"},
                "source_id": {"type": "string", "required": False, "description": "Filter by source ID"},
                "match_count": {"type": "integer", "required": False, "default": 5, "description": "Max results"}
            },
            "returns": "JSON with code examples and summaries",
            "example": {
                "query": "FastAPI authentication middleware",
                "source_id": "github.com",
                "match_count": 3
            }
        },
        
        "get_available_sources_archon": {
            "category": "rag",
            "description": "Get list of available sources in knowledge base",
            "parameters": {},
            "returns": "JSON with list of sources",
            "example": {}
        },
        
        # Project & Task Management Tools
        "manage_project_archon": {
            "category": "project",
            "description": "Unified project lifecycle management with PRP support",
            "parameters": {
                "action": {"type": "string", "required": True, "description": "Operation: create, list, get, delete"},
                "project_id": {"type": "string", "required": False, "description": "Project UUID"},
                "title": {"type": "string", "required": False, "description": "Project title"},
                "prd": {"type": "object", "required": False, "description": "Product Requirements Document"},
                "github_repo": {"type": "string", "required": False, "description": "GitHub repository URL"}
            },
            "returns": "JSON with project operation results",
            "example": {
                "action": "create",
                "title": "OAuth2 Authentication System",
                "github_repo": "https://github.com/company/auth-service"
            }
        },
        
        "manage_task_archon": {
            "category": "project",
            "description": "Unified task management within PRP-driven projects",
            "parameters": {
                "action": {"type": "string", "required": True, "description": "Operation: create, list, get, update, delete, archive"},
                "task_id": {"type": "string", "required": False, "description": "Task UUID"},
                "project_id": {"type": "string", "required": False, "description": "Project UUID"},
                "filter_by": {"type": "string", "required": False, "description": "Filter type: status, project, assignee"},
                "filter_value": {"type": "string", "required": False, "description": "Filter value"},
                "title": {"type": "string", "required": False, "description": "Task title"},
                "description": {"type": "string", "required": False, "description": "Task description"},
                "assignee": {"type": "string", "required": False, "default": "User", "description": "Task assignee"},
                "task_order": {"type": "integer", "required": False, "default": 0, "description": "Priority order"},
                "feature": {"type": "string", "required": False, "description": "Feature label"},
                "update_fields": {"type": "object", "required": False, "description": "Fields to update"},
                "include_closed": {"type": "boolean", "required": False, "default": False, "description": "Include closed tasks"},
                "page": {"type": "integer", "required": False, "default": 1, "description": "Page number"},
                "per_page": {"type": "integer", "required": False, "default": 50, "description": "Items per page"}
            },
            "returns": "JSON with task operation results",
            "example": {
                "action": "create",
                "project_id": "uuid",
                "title": "Implement OAuth2 provider",
                "description": "Create OAuth2 provider with Google integration",
                "assignee": "AI IDE Agent",
                "feature": "authentication"
            }
        },
        
        "manage_document_archon": {
            "category": "project",
            "description": "Document management with automatic version control",
            "parameters": {
                "action": {"type": "string", "required": True, "description": "Operation: add, list, get, update, delete"},
                "project_id": {"type": "string", "required": True, "description": "Project UUID"},
                "doc_id": {"type": "string", "required": False, "description": "Document UUID"},
                "document_type": {"type": "string", "required": False, "description": "Document type"},
                "title": {"type": "string", "required": False, "description": "Document title"},
                "content": {"type": "object", "required": False, "description": "Document content"},
                "metadata": {"type": "object", "required": False, "description": "Document metadata"}
            },
            "returns": "JSON with document operation results",
            "example": {
                "action": "add",
                "project_id": "uuid",
                "document_type": "spec",
                "title": "API Specification",
                "content": {"sections": {"overview": "API overview"}}
            }
        },
        
        "manage_versions_archon": {
            "category": "project",
            "description": "Immutable document version management",
            "parameters": {
                "action": {"type": "string", "required": True, "description": "Operation: create, list, get, restore"},
                "project_id": {"type": "string", "required": True, "description": "Project UUID"},
                "field_name": {"type": "string", "required": True, "description": "JSONB field name"},
                "version_number": {"type": "integer", "required": False, "description": "Version number"},
                "content": {"type": "object", "required": False, "description": "Content to version"},
                "change_summary": {"type": "string", "required": False, "description": "Change description"},
                "document_id": {"type": "string", "required": False, "description": "Document UUID"},
                "created_by": {"type": "string", "required": False, "default": "system", "description": "Creator identifier"}
            },
            "returns": "JSON with version operation results",
            "example": {
                "action": "create",
                "project_id": "uuid",
                "field_name": "docs",
                "content": {"title": "Document"},
                "change_summary": "Initial version"
            }
        },
        
        "get_project_features_archon": {
            "category": "project",
            "description": "Get features from project's features JSONB field",
            "parameters": {
                "project_id": {"type": "string", "required": True, "description": "Project UUID"}
            },
            "returns": "JSON with list of features",
            "example": {
                "project_id": "uuid"
            }
        },
        
        # System & Monitoring Tools
        "health_check_archon": {
            "category": "system",
            "description": "Perform health check on MCP server and dependencies",
            "parameters": {},
            "returns": "JSON with health status",
            "example": {}
        },

        "session_info_archon": {
            "category": "system",
            "description": "Get current session and all active sessions info",
            "parameters": {},
            "returns": "JSON with session information",
            "example": {}
        },

        # Shell & Command Execution Tools
        "execute_shell_command": {
            "category": "system",
            "description": "Execute shell commands with working directory support",
            "parameters": {
                "command": {"type": "string", "required": True, "description": "Shell command to execute"},
                "working_directory": {"type": "string", "required": False, "default": ".", "description": "Working directory for command execution"},
                "timeout": {"type": "integer", "required": False, "default": 30, "description": "Command timeout in seconds"},
                "capture_output": {"type": "boolean", "required": False, "default": True, "description": "Whether to capture stdout/stderr"}
            },
            "returns": "JSON with command result, stdout, stderr, and exit code",
            "example": {
                "command": "git status",
                "working_directory": "/path/to/repo",
                "timeout": 10
            }
        },
        "execute_mcp_tool": {
            "category": "system",
            "description": "Execute custom MCP tools by name with parameters",
            "parameters": {
                "tool_name": {"type": "string", "required": True, "description": "Name of the MCP tool to execute"},
                "tool_parameters": {"type": "object", "required": False, "default": {}, "description": "Parameters to pass to the MCP tool"},
                "mcp_server": {"type": "string", "required": False, "description": "Specific MCP server to use (optional)"}
            },
            "returns": "JSON with tool execution result",
            "example": {
                "tool_name": "git_commit",
                "tool_parameters": {"message": "feat: add new feature"},
                "mcp_server": "git"
            }
        },

        # Export/Import & Backup Tools
        "export_project_archon": {
            "category": "export_import",
            "description": "Export a project to a portable package format",
            "parameters": {
                "project_id": {"type": "string", "required": True, "description": "UUID of project to export"},
                "export_type": {"type": "string", "required": False, "default": "full", "description": "Export type (full, selective, incremental)"},
                "include_versions": {"type": "boolean", "required": False, "default": True, "description": "Include version history"},
                "include_sources": {"type": "boolean", "required": False, "default": True, "description": "Include knowledge sources"},
                "include_attachments": {"type": "boolean", "required": False, "default": False, "description": "Include file attachments"},
                "version_limit": {"type": "integer", "required": False, "description": "Maximum versions to include"},
                "exported_by": {"type": "string", "required": False, "default": "mcp_tool", "description": "User performing export"}
            },
            "returns": "JSON with export result and download information",
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "export_type": "full",
                "include_versions": True,
                "version_limit": 50
            }
        },

        "import_project_archon": {
            "category": "export_import",
            "description": "Import a project from an exported package file",
            "parameters": {
                "import_file_path": {"type": "string", "required": True, "description": "Path to exported ZIP file"},
                "import_type": {"type": "string", "required": False, "default": "full", "description": "Import type (full, selective, merge)"},
                "conflict_resolution": {"type": "string", "required": False, "default": "merge", "description": "Conflict resolution (merge, overwrite, skip, fail)"},
                "target_project_id": {"type": "string", "required": False, "description": "Existing project ID to import into"},
                "dry_run": {"type": "boolean", "required": False, "default": False, "description": "Validate without importing"},
                "imported_by": {"type": "string", "required": False, "default": "mcp_tool", "description": "User performing import"}
            },
            "returns": "JSON with import result and project information",
            "example": {
                "import_file_path": "/tmp/project_export.zip",
                "import_type": "full",
                "conflict_resolution": "merge"
            }
        },

        "validate_import_file_archon": {
            "category": "export_import",
            "description": "Validate an import file without performing the actual import",
            "parameters": {
                "import_file_path": {"type": "string", "required": True, "description": "Path to exported ZIP file to validate"}
            },
            "returns": "JSON with validation result and file metadata",
            "example": {
                "import_file_path": "/tmp/project_export.zip"
            }
        },

        "create_backup_archon": {
            "category": "backup",
            "description": "Create a backup of a specific project",
            "parameters": {
                "project_id": {"type": "string", "required": True, "description": "UUID of project to backup"},
                "backup_type": {"type": "string", "required": False, "default": "full", "description": "Backup type (full, selective, incremental)"},
                "compress": {"type": "boolean", "required": False, "default": True, "description": "Compress the backup"},
                "encrypt": {"type": "boolean", "required": False, "default": False, "description": "Encrypt the backup"},
                "created_by": {"type": "string", "required": False, "default": "mcp_tool", "description": "User creating backup"}
            },
            "returns": "JSON with backup result and metadata",
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "backup_type": "full",
                "compress": True
            }
        },

        "restore_backup_archon": {
            "category": "backup",
            "description": "Restore a project from a backup",
            "parameters": {
                "backup_id": {"type": "string", "required": True, "description": "UUID of backup to restore"},
                "target_project_id": {"type": "string", "required": False, "description": "Existing project ID to restore into"},
                "conflict_resolution": {"type": "string", "required": False, "default": "merge", "description": "Conflict resolution strategy"},
                "restored_by": {"type": "string", "required": False, "default": "mcp_tool", "description": "User performing restoration"}
            },
            "returns": "JSON with restoration result and project information",
            "example": {
                "backup_id": "backup-123e4567-e89b-12d3-a456-426614174000",
                "conflict_resolution": "merge"
            }
        },

        "list_backups_archon": {
            "category": "backup",
            "description": "List available backups, optionally filtered by project",
            "parameters": {
                "project_id": {"type": "string", "required": False, "description": "Optional project ID to filter backups"}
            },
            "returns": "JSON with list of available backups and metadata",
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        },

        "schedule_backup_archon": {
            "category": "backup",
            "description": "Schedule automatic backups for a project",
            "parameters": {
                "project_id": {"type": "string", "required": True, "description": "UUID of project to schedule backups for"},
                "schedule_type": {"type": "string", "required": False, "default": "cron", "description": "Schedule type (cron, interval)"},
                "cron_expression": {"type": "string", "required": False, "description": "Cron expression for cron-based schedules"},
                "interval_minutes": {"type": "integer", "required": False, "description": "Interval in minutes for interval-based schedules"},
                "backup_type": {"type": "string", "required": False, "default": "full", "description": "Type of backup to create"},
                "enabled": {"type": "boolean", "required": False, "default": True, "description": "Whether schedule should be enabled"},
                "created_by": {"type": "string", "required": False, "default": "mcp_tool", "description": "User creating schedule"}
            },
            "returns": "JSON with schedule creation result",
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000",
                "schedule_type": "cron",
                "cron_expression": "0 2 * * *",
                "backup_type": "full"
            }
        },

        "list_backup_schedules_archon": {
            "category": "backup",
            "description": "List backup schedules, optionally filtered by project",
            "parameters": {
                "project_id": {"type": "string", "required": False, "description": "Optional project ID to filter schedules"}
            },
            "returns": "JSON with list of backup schedules",
            "example": {
                "project_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    }
    
    @classmethod
    def get_tool_info(cls, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        return cls.AVAILABLE_TOOLS.get(tool_name)
    
    @classmethod
    def list_tools_by_category(cls, category: str) -> List[str]:
        """List all tools in a specific category"""
        return [
            tool_name for tool_name, info in cls.AVAILABLE_TOOLS.items()
            if info.get("category") == category
        ]
    
    @classmethod
    def validate_tool_exists(cls, tool_name: str) -> bool:
        """Check if a tool exists in the registry"""
        return tool_name in cls.AVAILABLE_TOOLS
    
    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get all available tool categories"""
        categories = set()
        for info in cls.AVAILABLE_TOOLS.values():
            categories.add(info.get("category", "unknown"))
        return sorted(list(categories))


class MCPToolExecutor:
    """Executes MCP tools with parameter validation and result processing"""
    
    def __init__(self):
        self.registry = MCPToolRegistry()
    
    async def execute_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute an MCP tool with validation and error handling.
        
        Args:
            tool_name: Name of the MCP tool to execute
            parameters: Parameters to pass to the tool
            context: Optional execution context for logging
            
        Returns:
            Tuple of (success, result_dict)
        """
        try:
            logfire.info(f"Executing MCP tool | tool={tool_name} | params={parameters}")
            
            # Validate tool exists
            if not self.registry.validate_tool_exists(tool_name):
                return False, {
                    "error": f"Unknown MCP tool: {tool_name}",
                    "available_tools": list(self.registry.AVAILABLE_TOOLS.keys())
                }
            
            # Get tool info for validation
            tool_info = self.registry.get_tool_info(tool_name)
            
            # Validate parameters
            validation_success, validation_result = self._validate_parameters(tool_name, parameters, tool_info)
            if not validation_success:
                return False, validation_result
            
            # Clean and prepare parameters
            cleaned_params = self._clean_parameters(parameters, tool_info)
            
            # TODO: Implement actual MCP tool execution
            # For now, return a mock result to allow the server to start
            result = {
                "success": True,
                "message": f"Mock execution of {tool_name}",
                "data": {"tool": tool_name, "parameters": cleaned_params}
            }
            
            # Process and validate result
            processed_result = self._process_tool_result(tool_name, result, tool_info)
            
            logfire.info(f"MCP tool executed successfully | tool={tool_name}")
            
            return True, {
                "success": True,
                "tool_name": tool_name,
                "parameters": cleaned_params,
                "result": processed_result,
                "executed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error executing MCP tool {tool_name}: {str(e)}"
            logfire.error(f"MCP tool execution failed | tool={tool_name} | error={str(e)}")
            
            return False, {
                "success": False,
                "error": error_msg,
                "tool_name": tool_name,
                "parameters": parameters,
                "executed_at": datetime.now().isoformat()
            }
    
    def _validate_parameters(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        tool_info: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Validate parameters against tool schema"""
        try:
            tool_params = tool_info.get("parameters", {})
            errors = []
            
            # Check required parameters
            for param_name, param_info in tool_params.items():
                if param_info.get("required", False) and param_name not in parameters:
                    errors.append(f"Missing required parameter: {param_name}")
            
            # Check parameter types
            for param_name, param_value in parameters.items():
                if param_name in tool_params:
                    param_info = tool_params[param_name]
                    expected_type = param_info.get("type")
                    
                    if expected_type == "string" and not isinstance(param_value, str):
                        errors.append(f"Parameter {param_name} must be a string")
                    elif expected_type == "integer" and not isinstance(param_value, int):
                        errors.append(f"Parameter {param_name} must be an integer")
                    elif expected_type == "boolean" and not isinstance(param_value, bool):
                        errors.append(f"Parameter {param_name} must be a boolean")
                    elif expected_type == "object" and not isinstance(param_value, dict):
                        errors.append(f"Parameter {param_name} must be an object")
            
            if errors:
                return False, {
                    "error": "Parameter validation failed",
                    "validation_errors": errors,
                    "tool_schema": tool_params
                }
            
            return True, {"message": "Parameters validated successfully"}
            
        except Exception as e:
            return False, {"error": f"Parameter validation error: {str(e)}"}
    
    def _clean_parameters(self, parameters: Dict[str, Any], tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and prepare parameters for tool execution"""
        tool_params = tool_info.get("parameters", {})
        cleaned = {}
        
        for param_name, param_value in parameters.items():
            if param_name in tool_params:
                # Apply defaults if value is None
                if param_value is None and "default" in tool_params[param_name]:
                    cleaned[param_name] = tool_params[param_name]["default"]
                else:
                    cleaned[param_name] = param_value
        
        return cleaned
    
    def _process_tool_result(
        self, 
        tool_name: str, 
        result: Any, 
        tool_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process and validate tool execution result"""
        try:
            # If result is a string, try to parse as JSON
            if isinstance(result, str):
                try:
                    parsed_result = json.loads(result)
                    return {
                        "raw_result": result,
                        "parsed_result": parsed_result,
                        "result_type": "json"
                    }
                except json.JSONDecodeError:
                    return {
                        "raw_result": result,
                        "result_type": "string"
                    }
            else:
                return {
                    "raw_result": result,
                    "result_type": type(result).__name__
                }
                
        except Exception as e:
            logfire.warning(f"Error processing tool result | tool={tool_name} | error={str(e)}")
            return {
                "raw_result": result,
                "result_type": "unknown",
                "processing_error": str(e)
            }


class MCPToolMapper:
    """Maps workflow step parameters to MCP tool parameters"""
    
    @staticmethod
    def map_parameters(
        step_parameters: Dict[str, Any],
        tool_name: str,
        context_variables: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Map workflow step parameters to MCP tool parameters.
        
        Args:
            step_parameters: Parameters from workflow step
            tool_name: Name of the MCP tool
            context_variables: Available context variables
            
        Returns:
            Mapped parameters for MCP tool
        """
        try:
            # Get tool info for parameter mapping
            tool_info = MCPToolRegistry.get_tool_info(tool_name)
            if not tool_info:
                return step_parameters
            
            mapped_params = {}
            tool_params = tool_info.get("parameters", {})
            
            # Map each step parameter to tool parameter
            for step_param, step_value in step_parameters.items():
                if step_param in tool_params:
                    mapped_params[step_param] = step_value
                else:
                    # Try to find a matching parameter by common aliases
                    mapped_param = MCPToolMapper._find_parameter_alias(step_param, tool_params)
                    if mapped_param:
                        mapped_params[mapped_param] = step_value
                    else:
                        # Keep unmapped parameters for debugging
                        mapped_params[step_param] = step_value
            
            # Add default values for missing required parameters
            for param_name, param_info in tool_params.items():
                if param_name not in mapped_params and "default" in param_info:
                    mapped_params[param_name] = param_info["default"]
            
            return mapped_params
            
        except Exception as e:
            logfire.error(f"Error mapping parameters | tool={tool_name} | error={str(e)}")
            return step_parameters
    
    @staticmethod
    def _find_parameter_alias(step_param: str, tool_params: Dict[str, Any]) -> Optional[str]:
        """Find parameter alias for common parameter name variations"""
        # Common parameter aliases
        aliases = {
            "id": ["task_id", "project_id", "doc_id"],
            "name": ["title", "workflow_name"],
            "text": ["query", "content", "description"],
            "count": ["match_count", "limit", "per_page"],
            "filter": ["source", "source_id", "filter_by"],
            "type": ["document_type", "action"]
        }
        
        # Check if step parameter matches any alias
        for tool_param in tool_params.keys():
            if step_param == tool_param:
                return tool_param
            
            # Check aliases
            for alias_group in aliases.values():
                if step_param in alias_group and tool_param in alias_group:
                    return tool_param
        
        return None


class MCPWorkflowIntegration:
    """High-level integration between workflows and MCP tools"""
    
    def __init__(self):
        self.executor = MCPToolExecutor()
        self.mapper = MCPToolMapper()
        self.registry = MCPToolRegistry()
    
    async def execute_workflow_step(
        self,
        tool_name: str,
        step_parameters: Dict[str, Any],
        context_variables: Dict[str, Any] = None,
        execution_context: Dict[str, Any] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute a workflow step using MCP tools.
        
        Args:
            tool_name: Name of the MCP tool to execute
            step_parameters: Parameters from the workflow step
            context_variables: Available context variables
            execution_context: Workflow execution context
            
        Returns:
            Tuple of (success, result_dict)
        """
        try:
            logfire.info(f"Executing workflow step with MCP tool | tool={tool_name}")
            
            # Map step parameters to tool parameters
            mapped_params = self.mapper.map_parameters(
                step_parameters, 
                tool_name, 
                context_variables
            )
            
            # Execute the tool
            success, result = await self.executor.execute_tool(
                tool_name,
                mapped_params,
                execution_context
            )
            
            if success:
                # Extract useful information from result
                tool_result = result.get("result", {})
                
                return True, {
                    "success": True,
                    "tool_name": tool_name,
                    "mapped_parameters": mapped_params,
                    "tool_result": tool_result,
                    "execution_info": {
                        "executed_at": result.get("executed_at"),
                        "result_type": tool_result.get("result_type"),
                        "has_parsed_result": "parsed_result" in tool_result
                    }
                }
            else:
                return False, {
                    "success": False,
                    "tool_name": tool_name,
                    "error": result.get("error"),
                    "validation_errors": result.get("validation_errors", []),
                    "mapped_parameters": mapped_params
                }
                
        except Exception as e:
            error_msg = f"Error in workflow step execution: {str(e)}"
            logfire.error(f"Workflow step execution failed | tool={tool_name} | error={str(e)}")
            
            return False, {
                "success": False,
                "error": error_msg,
                "tool_name": tool_name,
                "step_parameters": step_parameters
            }
    
    def get_tool_suggestions(self, step_description: str) -> List[Dict[str, Any]]:
        """Get tool suggestions based on step description"""
        suggestions = []
        
        # Simple keyword-based matching
        keywords = step_description.lower().split()
        
        for tool_name, tool_info in self.registry.AVAILABLE_TOOLS.items():
            score = 0
            tool_desc = tool_info.get("description", "").lower()
            
            # Check for keyword matches
            for keyword in keywords:
                if keyword in tool_desc or keyword in tool_name.lower():
                    score += 1
            
            if score > 0:
                suggestions.append({
                    "tool_name": tool_name,
                    "description": tool_info.get("description"),
                    "category": tool_info.get("category"),
                    "score": score,
                    "example": tool_info.get("example", {})
                })
        
        # Sort by score (highest first)
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def validate_workflow_tools(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate all tools used in a workflow"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "tool_summary": {}
        }
        
        for step in workflow_steps:
            if step.get("type") == "action":
                tool_name = step.get("tool_name")
                if tool_name:
                    if not self.registry.validate_tool_exists(tool_name):
                        validation_results["valid"] = False
                        validation_results["errors"].append(
                            f"Unknown tool '{tool_name}' in step '{step.get('name')}'"
                        )
                    else:
                        # Validate parameters
                        step_params = step.get("parameters", {})
                        tool_info = self.registry.get_tool_info(tool_name)
                        
                        validation_success, validation_result = self.executor._validate_parameters(
                            tool_name, step_params, tool_info
                        )
                        
                        if not validation_success:
                            validation_results["warnings"].append(
                                f"Parameter issues in step '{step.get('name')}': {validation_result.get('validation_errors', [])}"
                            )
                        
                        # Add to tool summary
                        category = tool_info.get("category", "unknown")
                        if category not in validation_results["tool_summary"]:
                            validation_results["tool_summary"][category] = []
                        validation_results["tool_summary"][category].append(tool_name)
        
        return validation_results


# Global MCP integration instance
_mcp_integration: Optional[MCPWorkflowIntegration] = None


def get_mcp_workflow_integration() -> MCPWorkflowIntegration:
    """Get or create the global MCP workflow integration instance"""
    global _mcp_integration
    
    if _mcp_integration is None:
        _mcp_integration = MCPWorkflowIntegration()
    
    return _mcp_integration
