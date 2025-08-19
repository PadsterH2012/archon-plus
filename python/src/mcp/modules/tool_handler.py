"""
MCP Tool Handler for Export/Import Operations

This module provides the handler that connects MCP tool definitions
to their actual implementations for export/import and backup operations.
"""

import json
from typing import Any, Dict, Optional, Tuple

from ...server.config.logfire_config import get_logger
from .export_import_tools import (
    create_backup_archon,
    export_project_archon,
    import_project_archon,
    list_backup_schedules_archon,
    list_backups_archon,
    restore_backup_archon,
    schedule_backup_archon,
    validate_import_file_archon,
)

logger = get_logger(__name__)


class ExportImportToolHandler:
    """Handler for export/import MCP tools"""
    
    def __init__(self):
        self.tool_mapping = {
            "export_project_archon": export_project_archon,
            "import_project_archon": import_project_archon,
            "validate_import_file_archon": validate_import_file_archon,
            "create_backup_archon": create_backup_archon,
            "restore_backup_archon": restore_backup_archon,
            "list_backups_archon": list_backups_archon,
            "schedule_backup_archon": schedule_backup_archon,
            "list_backup_schedules_archon": list_backup_schedules_archon,
        }
    
    async def handle_tool_call(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle MCP tool call for export/import operations.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Tuple of (success, result_dict)
        """
        try:
            if tool_name not in self.tool_mapping:
                return False, {
                    "error": f"Unknown export/import tool: {tool_name}",
                    "available_tools": list(self.tool_mapping.keys())
                }
            
            logger.info(f"Executing export/import tool | tool={tool_name} | params={parameters}")
            
            # Get the tool function
            tool_function = self.tool_mapping[tool_name]
            
            # Execute the tool
            result_json = await tool_function(**parameters)
            
            # Parse the result
            try:
                result = json.loads(result_json)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool result | tool={tool_name} | error={str(e)}")
                return False, {
                    "error": f"Tool returned invalid JSON: {str(e)}",
                    "raw_result": result_json
                }
            
            # Check if the tool execution was successful
            success = result.get("success", False)
            
            if success:
                logger.info(f"Export/import tool executed successfully | tool={tool_name}")
                return True, {
                    "success": True,
                    "tool_name": tool_name,
                    "result": result
                }
            else:
                logger.warning(f"Export/import tool execution failed | tool={tool_name} | error={result.get('error')}")
                return False, {
                    "success": False,
                    "tool_name": tool_name,
                    "error": result.get("error", "Tool execution failed"),
                    "result": result
                }
                
        except Exception as e:
            logger.error(f"Error handling export/import tool call | tool={tool_name} | error={str(e)}")
            return False, {
                "success": False,
                "tool_name": tool_name,
                "error": f"Tool handler error: {str(e)}"
            }
    
    def get_available_tools(self) -> List[str]:
        """Get list of available export/import tools"""
        return list(self.tool_mapping.keys())
    
    def is_export_import_tool(self, tool_name: str) -> bool:
        """Check if a tool is an export/import tool"""
        return tool_name in self.tool_mapping


# Global handler instance
_export_import_handler: Optional[ExportImportToolHandler] = None


def get_export_import_handler() -> ExportImportToolHandler:
    """Get the global export/import tool handler instance"""
    global _export_import_handler
    if _export_import_handler is None:
        _export_import_handler = ExportImportToolHandler()
    return _export_import_handler


# Tool execution wrapper functions for integration with existing MCP infrastructure
async def execute_export_import_tool(tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Execute an export/import MCP tool.
    
    This function serves as the main entry point for export/import tool execution
    and can be integrated with the existing MCP tool execution infrastructure.
    
    Args:
        tool_name: Name of the export/import tool to execute
        parameters: Parameters for the tool
        
    Returns:
        Tuple of (success, result_dict)
    """
    handler = get_export_import_handler()
    return await handler.handle_tool_call(tool_name, parameters)


def validate_export_import_parameters(tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate parameters for export/import tools.
    
    Args:
        tool_name: Name of the tool
        parameters: Parameters to validate
        
    Returns:
        Tuple of (is_valid, validation_result)
    """
    try:
        handler = get_export_import_handler()
        
        if not handler.is_export_import_tool(tool_name):
            return False, {"error": f"Unknown export/import tool: {tool_name}"}
        
        # Basic parameter validation
        errors = []
        
        # Tool-specific validation
        if tool_name == "export_project_archon":
            if "project_id" not in parameters:
                errors.append("Missing required parameter: project_id")
            if "export_type" in parameters and parameters["export_type"] not in ["full", "selective", "incremental"]:
                errors.append("export_type must be one of: full, selective, incremental")
                
        elif tool_name == "import_project_archon":
            if "import_file_path" not in parameters:
                errors.append("Missing required parameter: import_file_path")
            if "import_type" in parameters and parameters["import_type"] not in ["full", "selective", "merge"]:
                errors.append("import_type must be one of: full, selective, merge")
            if "conflict_resolution" in parameters and parameters["conflict_resolution"] not in ["merge", "overwrite", "skip", "fail"]:
                errors.append("conflict_resolution must be one of: merge, overwrite, skip, fail")
                
        elif tool_name == "validate_import_file_archon":
            if "import_file_path" not in parameters:
                errors.append("Missing required parameter: import_file_path")
                
        elif tool_name == "create_backup_archon":
            if "project_id" not in parameters:
                errors.append("Missing required parameter: project_id")
            if "backup_type" in parameters and parameters["backup_type"] not in ["full", "selective", "incremental"]:
                errors.append("backup_type must be one of: full, selective, incremental")
                
        elif tool_name == "restore_backup_archon":
            if "backup_id" not in parameters:
                errors.append("Missing required parameter: backup_id")
            if "conflict_resolution" in parameters and parameters["conflict_resolution"] not in ["merge", "overwrite", "skip", "fail"]:
                errors.append("conflict_resolution must be one of: merge, overwrite, skip, fail")
                
        elif tool_name == "schedule_backup_archon":
            if "project_id" not in parameters:
                errors.append("Missing required parameter: project_id")
            if "schedule_type" in parameters and parameters["schedule_type"] not in ["cron", "interval"]:
                errors.append("schedule_type must be one of: cron, interval")
            if parameters.get("schedule_type") == "cron" and "cron_expression" not in parameters:
                errors.append("cron_expression required for cron schedule type")
            if parameters.get("schedule_type") == "interval" and "interval_minutes" not in parameters:
                errors.append("interval_minutes required for interval schedule type")
        
        if errors:
            return False, {
                "error": "Parameter validation failed",
                "validation_errors": errors
            }
        
        return True, {"message": "Parameters validated successfully"}
        
    except Exception as e:
        return False, {"error": f"Parameter validation error: {str(e)}"}


def get_export_import_tool_info(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about an export/import tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool information dictionary or None if not found
    """
    # This would typically be imported from the MCP tool registry
    # For now, return basic info
    handler = get_export_import_handler()
    
    if not handler.is_export_import_tool(tool_name):
        return None
    
    # Basic tool info - in a real implementation, this would come from the registry
    return {
        "name": tool_name,
        "category": "export_import" if "backup" not in tool_name else "backup",
        "description": f"MCP tool for {tool_name.replace('_archon', '').replace('_', ' ')}",
        "available": True
    }


def list_export_import_tools() -> List[Dict[str, Any]]:
    """
    List all available export/import tools with their information.
    
    Returns:
        List of tool information dictionaries
    """
    handler = get_export_import_handler()
    tools = []
    
    for tool_name in handler.get_available_tools():
        tool_info = get_export_import_tool_info(tool_name)
        if tool_info:
            tools.append(tool_info)
    
    return tools
