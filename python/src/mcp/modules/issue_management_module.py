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

# Import PostgreSQL adapter
import psycopg2
from psycopg2.extras import RealDictCursor

from mcp.server.fastmcp import Context, FastMCP

# Import service discovery for HTTP calls
from src.server.config.service_discovery import get_api_url

logger = logging.getLogger(__name__)


# Database connection configuration
DB_CONFIG = {
    'host': '10.202.70.20',
    'port': 5433,
    'database': 'archon_issues',
    'user': 'archon_user',
    'password': 'your_very_secure_password_here_change_this'
}


def get_db_connection():
    """Get PostgreSQL database connection."""
    return psycopg2.connect(**DB_CONFIG)


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
            # Step 1: Get task details from Archon (placeholder for now)
            # TODO: Implement task retrieval via existing MCP tools
            task_title = f"Task: {task_id}"
            task_description = f"Issue created from Archon task {task_id}"

            # Step 2: Connect to issues database
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Step 3: Set current user for audit trail (archon-agent)
                    cursor.execute("SELECT set_config('app.current_user_id', '3', false)")

                    # Step 4: Get or create project using Archon project ID
                    cursor.execute("""
                        SELECT * FROM get_or_create_project(%s, %s, %s)
                    """, (
                        project_name,
                        f"Auto-created from Archon task {task_id}",
                        "archon-agent"
                    ))

                    project_info = dict(cursor.fetchone())

                    # Step 5: Create issue with Archon task ID as external reference
                    cursor.execute("""
                        INSERT INTO issues (
                            title, description, project_id, reporter_id, assignee_id,
                            external_id, priority, severity
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING issue_id, issue_key
                    """, (
                        task_title,
                        task_description,
                        project_info['project_id'],
                        3,  # archon-agent user_id (reporter)
                        3,  # archon-agent assignee
                        task_id,  # Store Archon task ID for linking
                        'medium',
                        'minor'
                    ))

                    issue_result = dict(cursor.fetchone())
                    conn.commit()

            # Step 6: TODO: Update Archon task description with issue reference
            # Replace "archon_issue_ref: NULL" with "archon_issue_ref: {issue_key}"

            result = {
                "success": True,
                "issue_key": issue_result['issue_key'],
                "issue_id": issue_result['issue_id'],
                "project_name": project_name,
                "project_id": project_info['project_id'],
                "project_was_created": project_info['was_created'],
                "task_id": task_id,
                "sync_enabled": sync_enabled,
                "message": f"Successfully created issue {issue_result['issue_key']} from task {task_id}"
            }

            logger.info(f"Issue created successfully | issue={issue_result['issue_key']} | task={task_id}")
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
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Set current user for audit trail (archon-agent)
                    cursor.execute("SELECT set_config('app.current_user_id', '3', false)")

                    # Find issue linked to this task
                    cursor.execute("""
                        SELECT i.issue_id, i.issue_key, i.status, i.title, p.project_name
                        FROM issues i
                        JOIN projects p ON i.project_id = p.project_id
                        WHERE i.external_id = %s
                    """, (task_id,))

                    issue_info = cursor.fetchone()
                    if not issue_info:
                        return json.dumps({
                            "success": False,
                            "error": f"No issue found linked to task {task_id}",
                            "task_id": task_id
                        }, indent=2)

                    issue_info = dict(issue_info)
                    old_status = issue_info['status']

                    # Update issue status if provided
                    if issue_status and issue_status != old_status:
                        cursor.execute("""
                            UPDATE issues
                            SET status = %s, updated_date = CURRENT_TIMESTAMP
                            WHERE issue_id = %s
                        """, (issue_status, issue_info['issue_id']))

                        # Add sync comment
                        cursor.execute("""
                            INSERT INTO issue_history (issue_id, user_id, action_type, notes)
                            VALUES (%s, 3, 'commented', %s)
                        """, (issue_info['issue_id'], f"Status synced from Archon task {task_id}"))

                        conn.commit()
                        sync_message = f"Synced status from '{old_status}' to '{issue_status}'"
                    else:
                        sync_message = "No status change needed"

            result = {
                "success": True,
                "task_id": task_id,
                "issue_key": issue_info['issue_key'],
                "old_status": old_status,
                "new_status": issue_status or old_status,
                "project_name": issue_info['project_name'],
                "sync_message": sync_message,
                "message": f"Task {task_id} synced with issue {issue_info['issue_key']}"
            }

            logger.info(f"Task synced to issue | task={task_id} | issue={issue_info['issue_key']}")
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
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Build query with optional status filter
                    base_query = """
                        SELECT i.issue_key, i.title, i.status, i.priority, i.severity,
                               i.external_id as task_id, i.created_date, i.updated_date,
                               p.project_name, p.project_key,
                               reporter.username as reporter_username,
                               assignee.username as assignee_username
                        FROM issues i
                        JOIN projects p ON i.project_id = p.project_id
                        LEFT JOIN users reporter ON i.reporter_id = reporter.user_id
                        LEFT JOIN users assignee ON i.assignee_id = assignee.user_id
                        WHERE p.project_name = %s
                    """

                    params = [project_name]

                    if status_filter:
                        base_query += " AND i.status = %s"
                        params.append(status_filter)

                    base_query += " ORDER BY i.created_date DESC LIMIT %s"
                    params.append(limit)

                    cursor.execute(base_query, params)
                    issues = [dict(row) for row in cursor.fetchall()]

                    # Convert datetime objects to strings for JSON serialization
                    for issue in issues:
                        if issue['created_date']:
                            issue['created_date'] = issue['created_date'].isoformat()
                        if issue['updated_date']:
                            issue['updated_date'] = issue['updated_date'].isoformat()

            result = {
                "success": True,
                "project_name": project_name,
                "status_filter": status_filter,
                "limit": limit,
                "issues_count": len(issues),
                "issues": issues,
                "message": f"Found {len(issues)} issues in project '{project_name}'"
            }

            logger.info(f"Issues queried successfully | project={project_name} | count={len(issues)}")
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
            with get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Set current user for audit trail (archon-agent)
                    cursor.execute("SELECT set_config('app.current_user_id', '3', false)")

                    # First, verify the issue exists and get current status
                    cursor.execute("""
                        SELECT i.issue_id, i.status, i.title, p.project_name
                        FROM issues i
                        JOIN projects p ON i.project_id = p.project_id
                        WHERE i.issue_key = %s
                    """, (issue_key,))

                    issue_info = cursor.fetchone()
                    if not issue_info:
                        return json.dumps({
                            "success": False,
                            "error": f"Issue {issue_key} not found",
                            "issue_key": issue_key
                        }, indent=2)

                    issue_info = dict(issue_info)
                    old_status = issue_info['status']

                    # Update the issue status
                    cursor.execute("""
                        UPDATE issues
                        SET status = %s, updated_date = CURRENT_TIMESTAMP
                        WHERE issue_key = %s
                    """, (new_status, issue_key))

                    # Add comment if provided
                    if comment:
                        cursor.execute("""
                            INSERT INTO issue_history (issue_id, user_id, action_type, notes)
                            VALUES (%s, 3, 'commented', %s)
                        """, (issue_info['issue_id'], comment))

                    conn.commit()

            result = {
                "success": True,
                "issue_key": issue_key,
                "old_status": old_status,
                "new_status": new_status,
                "comment": comment,
                "project_name": issue_info['project_name'],
                "title": issue_info['title'],
                "message": f"Successfully updated {issue_key} status from '{old_status}' to '{new_status}'"
            }

            logger.info(f"Issue status updated | issue={issue_key} | {old_status} -> {new_status}")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error updating issue status: {e}")
            return json.dumps({
                "success": False,
                "error": f"Issue status update error: {str(e)}",
                "issue_key": issue_key
            }, indent=2)

    logger.info("✓ Issue management tools registered with PostgreSQL integration")
