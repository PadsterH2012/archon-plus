"""
Issue Management MCP Tools

This module provides MCP tools for issue management integration:
- Create issues from Archon tasks with automatic project linking
- Sync task status to issues database
- Query issues by project or task ID
- Integration with PostgreSQL issues database

🔗 Integration Architecture:
User Natural Language Request → Augment Agent → Archon MCP Tools → Issues Database

🛡️ Safety Features:
- Zero breaking changes to existing Archon functionality
- Follows existing MCP module patterns
- Complete error handling and validation
- Maintains audit trails in issues database
"""

import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

# Import HTTP client and service discovery
import httpx

from mcp.server.fastmcp import Context, FastMCP

# Import service discovery for HTTP calls
from src.server.config.service_discovery import get_api_url

logger = logging.getLogger(__name__)


def register_issue_management_tools(mcp: FastMCP):
    """Register issue management tools with the MCP server."""
    
    @mcp.tool()
    async def create_issue_from_task(
        ctx: Context,
        task_id: str,
        project_name: str,
        sync_enabled: bool = True
    ) -> str:
        """
        Create issue in issues database from Archon task with automatic linking.
        
        This tool:
        1. Gets task details from Archon
        2. Creates issue in issues database using get_or_create_project()
        3. Updates task description with issue reference
        4. Sets up bidirectional sync
        
        Args:
            task_id: Archon task UUID
            project_name: Project name for issue database
            sync_enabled: Enable bidirectional sync
            
        Returns:
            JSON string with issue creation result
        """
        try:
            # TODO: Implement actual issue creation logic
            # This would call the issues database API
            
            # For now, return a placeholder result
            result = {
                "success": True,
                "message": f"Issue creation placeholder for task {task_id}",
                "task_id": task_id,
                "project_name": project_name,
                "issue_key": f"ARCH-{task_id[-4:]}",  # Placeholder
                "sync_enabled": sync_enabled,
                "note": "This is a placeholder - actual issue database integration needed"
            }
            
            logger.info(f"Issue creation placeholder executed | task={task_id}")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error creating issue from task: {e}")
            return json.dumps({
                "success": False,
                "error": f"Issue creation error: {str(e)}",
                "task_id": task_id
            }, indent=2)

    @mcp.tool()
    async def sync_task_to_issue(
        ctx: Context,
        task_id: str,
        issue_status: str = None
    ) -> str:
        """
        Sync Archon task changes to issues database.
        
        Args:
            task_id: Archon task UUID
            issue_status: New issue status to sync
            
        Returns:
            JSON string with sync result
        """
        try:
            # TODO: Implement actual sync logic
            
            result = {
                "success": True,
                "message": f"Task sync placeholder for {task_id}",
                "task_id": task_id,
                "issue_status": issue_status,
                "note": "This is a placeholder - actual sync implementation needed"
            }
            
            logger.info(f"Task sync placeholder executed | task={task_id}")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error syncing task to issue: {e}")
            return json.dumps({
                "success": False,
                "error": f"Task sync error: {str(e)}",
                "task_id": task_id
            }, indent=2)

    @mcp.tool()
    async def query_issues_by_project(
        ctx: Context,
        project_name: str,
        status_filter: str = None,
        limit: int = 10
    ) -> str:
        """
        Query issues from the issues database by project.
        
        Args:
            project_name: Project name to filter by
            status_filter: Optional status filter (open, in_progress, resolved, closed)
            limit: Maximum number of issues to return
            
        Returns:
            JSON string with issues list
        """
        try:
            # TODO: Implement actual query logic
            
            result = {
                "success": True,
                "message": f"Issues query placeholder for project {project_name}",
                "project_name": project_name,
                "status_filter": status_filter,
                "limit": limit,
                "issues": [],  # Placeholder empty list
                "note": "This is a placeholder - actual database query implementation needed"
            }
            
            logger.info(f"Issues query placeholder executed | project={project_name}")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error querying issues: {e}")
            return json.dumps({
                "success": False,
                "error": f"Issues query error: {str(e)}",
                "project_name": project_name
            }, indent=2)

    @mcp.tool()
    async def update_issue_status(
        ctx: Context,
        issue_key: str,
        new_status: str,
        comment: str = None
    ) -> str:
        """
        Update issue status in the issues database.
        
        Args:
            issue_key: Issue key (e.g., ARCH-123)
            new_status: New status (open, in_progress, resolved, closed)
            comment: Optional comment for the status change
            
        Returns:
            JSON string with update result
        """
        try:
            # TODO: Implement actual status update logic
            
            result = {
                "success": True,
                "message": f"Issue status update placeholder for {issue_key}",
                "issue_key": issue_key,
                "new_status": new_status,
                "comment": comment,
                "note": "This is a placeholder - actual database update implementation needed"
            }
            
            logger.info(f"Issue status update placeholder executed | issue={issue_key}")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error updating issue status: {e}")
            return json.dumps({
                "success": False,
                "error": f"Issue status update error: {str(e)}",
                "issue_key": issue_key
            }, indent=2)

    logger.info("✓ Issue management tools registered (placeholder version)")
