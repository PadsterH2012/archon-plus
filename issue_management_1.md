# Issue Management Integration Implementation Guide

## 🎯 **Objective**
Integrate the PostgreSQL Issue Management Database with Archon's natural language workflow system to enable:
- Creating issues from Archon tasks via natural language
- Automatic project creation using Archon project IDs
- Bidirectional sync between Archon tasks and issues database
- Zero breaking changes to existing Archon functionality

## 📋 **Current State Analysis**

### **Issue Management Database (Ready)**
- ✅ **Location**: `database-stacks/postgresql-issue-db/`
- ✅ **Database**: PostgreSQL at `10.202.70.20:5433/archon_issues`
- ✅ **Features**: Complete schema with projects, issues, audit trails, tagging
- ✅ **Agent Support**: `get_or_create_project()` function for autonomous operation
- ✅ **Documentation**: Complete usage guides and API examples

### **Archon Architecture (Analyzed)**
- ✅ **MCP Tools**: Uses FastMCP framework for tool registration
- ✅ **Module Pattern**: Safe registration in `python/src/mcp/mcp_server.py`
- ✅ **Natural Language**: Augment Agent orchestrates, Archon agents execute
- ✅ **Execution Flow**: Augment Agent → Archon MCP Tools → Database Operations

## 🚀 **Implementation Strategy: Minimal Risk Approach**

### **Phase 1: Safe MCP Module Addition (30 minutes)**

#### **Step 1: Create Issue Management MCP Module**
**File**: `python/src/mcp/modules/issue_management_module.py`

```python
"""
Issue Management MCP Tools

This module provides MCP tools for issue management integration:
- Create issues from Archon tasks with automatic project linking
- Sync task status to issues database
- Query issues by project or task ID
- Integration with PostgreSQL issues database
"""

import json
from typing import Any, Dict, Optional

import httpx
from fastmcp import FastMCP
from urllib.parse import urljoin

from ...config.logfire_config import get_logger
from ...config.api import get_api_url

logger = get_logger(__name__)


def register_issue_management_tools(mcp: FastMCP):
    """Register issue management tools with the MCP server."""
    
    @mcp.tool()
    async def create_issue_from_task(
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

    logger.info("✓ Issue management tools registered (placeholder version)")
```

#### **Step 2: Register Module Safely**
**File**: `python/src/mcp/mcp_server.py` (add to existing `register_modules()` function)

**Find this section around line 300:**
```python
def register_modules():
    """Register all MCP tool modules."""
    logger.info("🔧 Registering MCP tool modules...")

    modules_registered = 0

    # ... existing module registrations ...
```

**Add this AFTER the existing modules (around line 395):**
```python
    # Import and register Issue Management module (NEW - SAFE ADDITION)
    try:
        from src.mcp.modules.issue_management_module import register_issue_management_tools

        register_issue_management_tools(mcp)
        modules_registered += 1
        logger.info("✓ Issue management module registered (placeholder)")
    except ImportError as e:
        logger.warning(f"⚠ Issue management module not available: {e}")
    except Exception as e:
        logger.error(f"✗ Error registering issue management module: {e}")
        logger.error(traceback.format_exc())
```

#### **Step 3: Test Integration**
Test with Augment Agent:
```python
# Test the new MCP tools
result = await archon_mcp.create_issue_from_task(
    task_id="test-task-123",
    project_name="Test Project",
    sync_enabled=True
)

print(result)  # Should return placeholder response
```

### **Phase 2: Real Implementation (2-3 hours)**

#### **Replace Placeholder with Real Database Integration**

```python
@mcp.tool()
async def create_issue_from_task(
    task_id: str,
    project_name: str,
    sync_enabled: bool = True
) -> str:
    """Real implementation with PostgreSQL integration"""
    try:
        # 1. Get task details from Archon
        # TODO: Implement task retrieval via existing MCP tools
        
        # 2. Connect to issues database
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host="10.202.70.20",
            port=5433,
            database="archon_issues",
            user="archon_user",
            password="your_very_secure_password_here_change_this"
        )
        
        # 3. Set current user for audit trail
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT set_config('app.current_user_id', '3', false)")  # archon-agent
            
            # 4. Get or create project using Archon project ID
            cursor.execute("""
                SELECT * FROM get_or_create_project(%s, %s, %s)
            """, (
                project_name, 
                f"Auto-created from Archon task {task_id}", 
                "archon-agent"
            ))
            
            project_info = dict(cursor.fetchone())
            
            # 5. Extract issue description from task
            # Parse task description to extract issue content after "archon_issue_ref: NULL"
            issue_description = "Issue created from Archon task"  # TODO: Extract from task
            
            # 6. Create issue with Archon task ID as external reference
            cursor.execute("""
                INSERT INTO issues (
                    title, description, project_id, reporter_id, assignee_id,
                    external_id, priority, severity
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING issue_id, issue_key
            """, (
                f"Task: {task_id}",  # TODO: Use real task title
                issue_description,
                project_info['project_id'],
                3,  # archon-agent user_id
                3,  # archon-agent assignee
                task_id,  # Store Archon task ID for linking
                'medium',
                'minor'
            ))
            
            issue_result = dict(cursor.fetchone())
            conn.commit()
        
        # 7. TODO: Update Archon task description with issue reference
        # Replace "archon_issue_ref: NULL" with "archon_issue_ref: {issue_key}"
        
        return json.dumps({
            "success": True,
            "issue_key": issue_result['issue_key'],
            "issue_id": issue_result['issue_id'],
            "project_name": project_name,
            "project_was_created": project_info['was_created'],
            "task_id": task_id,
            "sync_enabled": sync_enabled
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating issue: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "task_id": task_id
        }, indent=2)
```

## 🔄 **Natural Language Workflow**

### **User Interaction Examples**

#### **Creating Issues from Tasks**
**User**: *"I found a database connection issue, can you create a task and track it as a bug?"*

**Augment Agent Response**:
1. Creates Archon task with `archon_issue_ref: NULL` in description
2. Calls `create_issue_from_task()` MCP tool
3. Updates task description with issue reference
4. Confirms to user: "Created task TASK-123 and linked to issue ARCH-456"

#### **Status Updates**
**User**: *"Update the database issue to in progress"*

**Augment Agent Response**:
1. Identifies issue from context
2. Calls `sync_task_to_issue()` MCP tool
3. Updates both Archon task and issues database
4. Confirms sync completion

## 📊 **Integration Architecture**

```
User Natural Language Request
         ↓
Augment Agent (Claude) - Orchestrates workflow
         ↓
Archon MCP Tools - create_issue_from_task()
         ↓
Issues Database (PostgreSQL) - get_or_create_project()
         ↓
Archon Task Update - Replace "archon_issue_ref: NULL"
         ↓
Bidirectional Sync Established
```

## ✅ **Implementation Checklist**

### **Phase 1: Foundation (30 minutes)**
- [ ] Create `issue_management_module.py` with placeholder functions
- [ ] Add module registration to `mcp_server.py`
- [ ] Test MCP tool discovery with Augment Agent
- [ ] Verify placeholder responses work

### **Phase 2: Database Integration (2-3 hours)**
- [ ] Replace placeholders with PostgreSQL connections
- [ ] Implement `get_or_create_project()` integration
- [ ] Add task description parsing for issue content
- [ ] Test issue creation end-to-end

### **Phase 3: Task Integration (1-2 hours)**
- [ ] Implement Archon task description updates
- [ ] Add bidirectional sync functionality
- [ ] Test complete workflow with natural language
- [ ] Add error handling and validation

## 🎯 **Success Criteria**

### **Functional Requirements**
- ✅ User can say "create a bug report" and get both Archon task + issue
- ✅ Issues are automatically linked to Archon projects
- ✅ Task descriptions show issue references
- ✅ Status updates sync between systems

### **Technical Requirements**
- ✅ Zero breaking changes to existing Archon functionality
- ✅ Follows existing MCP module patterns
- ✅ Uses existing issues database schema
- ✅ Maintains complete audit trails

## 📚 **Reference Documentation**

- **Issues Database**: `database-stacks/postgresql-issue-db/docs/USAGE_GUIDE.md`
- **API Integration**: `database-stacks/postgresql-issue-db/docs/API_INTEGRATION.md`
- **Quick Reference**: `database-stacks/postgresql-issue-db/docs/QUICK_REFERENCE.md`
- **Archon Docs**: `docs/docs/issue-management.mdx`

## 🚀 **Ready to Implement**

This guide provides everything needed to implement issue management integration with Archon safely and efficiently. Start with Phase 1 to establish the foundation, then incrementally add real functionality.

**Estimated Total Time**: 4-6 hours for complete implementation
**Risk Level**: Minimal (follows existing patterns, optional module)
**Breaking Changes**: None (purely additive functionality)
