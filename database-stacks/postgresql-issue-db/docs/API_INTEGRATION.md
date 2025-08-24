# Issue Management Database - API Integration Guide

## 🔗 Integration Overview

This guide shows how to integrate the issue management database with applications, focusing on mandatory project requirements and task management system linking.

## 📋 Required Parameters

### **Mandatory Fields**
- **project_id** (INTEGER) - Database project identifier
- **project_name** (VARCHAR) - Human-readable project name
- **reporter_id** (INTEGER) - User creating the issue

### **Optional Integration Fields**
- **task_id** (VARCHAR) - External task management system ID (stored in `external_id`)
- **assignee_id** (INTEGER) - User assigned to the issue
- **tags** (ARRAY) - Categorization tags

## 🐍 Python Integration Examples

### **Database Connection Setup**
```python
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import List, Optional, Dict, Any

class IssueManager:
    def __init__(self):
        self.connection_params = {
            'host': '10.202.70.20',
            'port': 5433,
            'database': 'archon_issues',
            'user': 'archon_user',
            'password': 'your_very_secure_password_here_change_this'
        }
    
    def get_connection(self):
        return psycopg2.connect(**self.connection_params)
    
    def set_current_user(self, cursor, user_id: int):
        """Set current user for audit trail"""
        cursor.execute("SELECT set_config('app.current_user_id', %s, false)", (str(user_id),))
```

### **Project Management**
```python
def get_projects(self) -> List[Dict[str, Any]]:
    """Get all active projects (MANDATORY for issue creation)"""
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT project_id, project_name, project_key, description
                FROM projects
                WHERE is_active = TRUE
                ORDER BY project_name
            """)
            return [dict(row) for row in cursor.fetchall()]

def get_or_create_project(self, project_name: str,
                         description: str = "Auto-created project for issue tracking",
                         created_by: str = "system") -> Dict[str, Any]:
    """
    Get existing project or create new one (AGENT-FRIENDLY METHOD)

    This is the primary method agents should use to ensure project exists
    before creating issues.

    Args:
        project_name: Name of the project to find or create
        description: Description for new project (if created)
        created_by: Who is creating the project (agent name)

    Returns:
        Dict with project_id, project_name, project_key, was_created
    """
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM get_or_create_project(%s, %s, %s)
            """, (project_name, description, created_by))
            result = dict(cursor.fetchone())

            if result['was_created']:
                print(f"✅ Created new project: {result['project_name']} (ID: {result['project_id']}, Key: {result['project_key']})")
            else:
                print(f"📁 Using existing project: {result['project_name']} (ID: {result['project_id']}, Key: {result['project_key']})")

            return result

def validate_project(self, project_id: int) -> bool:
    """Validate project exists and is active (MANDATORY check)"""
    with self.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM projects
                WHERE project_id = %s AND is_active = TRUE
            """, (project_id,))
            return cursor.fetchone() is not None

def get_project_by_name(self, project_name: str) -> Optional[Dict[str, Any]]:
    """Get project by name (for name-to-ID conversion)"""
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT project_id, project_name, project_key, description
                FROM projects
                WHERE project_name = %s AND is_active = TRUE
            """, (project_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
```

### **Issue Creation with Mandatory Project**
```python
def create_issue(self,
                title: str,
                description: str,
                project_name: str,      # MANDATORY: Project name
                reporter_id: int,       # MANDATORY: Who's creating the issue
                assignee_id: Optional[int] = None,
                priority: str = 'medium',
                severity: str = 'minor',
                task_id: Optional[str] = None,  # OPTIONAL: Link to task system
                tags: Optional[List[str]] = None,
                environment: Optional[str] = None,
                auto_create_project: bool = True) -> Dict[str, Any]:
    """
    Create new issue with automatic project creation if needed (AGENT-FRIENDLY)

    Args:
        title: Issue title (minimum 5 characters)
        description: Detailed description
        project_name: MANDATORY - Project name (will be created if doesn't exist)
        reporter_id: MANDATORY - User ID creating the issue
        assignee_id: Optional user ID to assign issue to
        priority: critical, high, medium, low
        severity: critical, major, minor, trivial
        task_id: Optional external task management ID
        tags: Optional list of tag names
        environment: production, staging, development, local
        auto_create_project: If True, creates project if it doesn't exist

    Returns:
        Dict with issue_id, issue_key, project info, and success status
    """

    # AGENT-FRIENDLY: Get or create project automatically
    if auto_create_project:
        project = self.get_or_create_project(
            project_name=project_name,
            description=f"Auto-created project for {project_name} issues",
            created_by=f"user_{reporter_id}"
        )
        project_id = project['project_id']
        project_was_created = project['was_created']
    else:
        # Original behavior: validate project exists
        project = self.get_project_by_name(project_name)
        if not project:
            raise ValueError(f"Project '{project_name}' not found or inactive")
        project_id = project['project_id']
        project_was_created = False
    
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Set current user for audit trail
            self.set_current_user(cursor, reporter_id)
            
            # Create issue with tags if provided
            if tags:
                cursor.execute("""
                    SELECT create_issue_with_tags(%s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, description, project_id, reporter_id, 
                     assignee_id, priority, severity, tags))
                issue_id = cursor.fetchone()[0]
            else:
                # Create basic issue
                cursor.execute("""
                    INSERT INTO issues (
                        title, description, project_id, reporter_id, 
                        assignee_id, priority, severity, environment, external_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING issue_id
                """, (title, description, project_id, reporter_id,
                     assignee_id, priority, severity, environment, task_id))
                issue_id = cursor.fetchone()[0]
            
            # Link to task management system if provided
            if task_id and not tags:  # Only if not already set above
                cursor.execute("""
                    UPDATE issues SET external_id = %s WHERE issue_id = %s
                """, (task_id, issue_id))
            
            # Get the created issue details
            cursor.execute("""
                SELECT i.issue_id, i.issue_key, i.title, p.project_name, p.project_key
                FROM issues i
                JOIN projects p ON i.project_id = p.project_id
                WHERE i.issue_id = %s
            """, (issue_id,))

            result = dict(cursor.fetchone())
            result['success'] = True
            result['task_id'] = task_id
            result['project_was_created'] = project_was_created
            result['project_id'] = project_id

            return result

# Example usage for agents
issue_manager = IssueManager()

# AGENT-FRIENDLY: Create issue with automatic project creation
new_issue = issue_manager.create_issue(
    title="Database connection pool exhaustion",
    description="Connection pool reaching maximum capacity during peak hours",
    project_name="Test Project Alpha",  # Will be created if doesn't exist
    reporter_id=3,                      # archon-agent
    assignee_id=3,                      # archon-agent
    priority="high",
    severity="major",
    task_id="TASK-456",                 # OPTIONAL: Link to task system
    tags=["bug", "production", "database", "performance"],
    environment="production",
    auto_create_project=True            # AGENT-FRIENDLY: Auto-create project
)

print(f"Created issue {new_issue['issue_key']} in project {new_issue['project_name']}")
print(f"Project was {'created' if new_issue['project_was_created'] else 'existing'}")
print(f"Linked to task: {new_issue['task_id']}")

# Example for existing project (original behavior)
existing_project_issue = issue_manager.create_issue(
    title="UI responsiveness issue",
    description="Interface becomes unresponsive on mobile devices",
    project_name="Archon Plus",        # Must exist or will raise error
    reporter_id=2,                     # paddy
    assignee_id=2,                     # paddy
    auto_create_project=False          # Strict mode: project must exist
)
```

### **Issue Querying with Project Context**
```python
def get_issues_by_project(self, project_name: str, 
                         status: Optional[str] = None,
                         assignee_username: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get issues for specific project (MANDATORY project filter)"""
    
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT i.issue_key, i.title, i.status, i.priority, i.external_id as task_id,
                       p.project_name, u_assignee.username as assignee_username,
                       u_reporter.username as reporter_username, i.created_date
                FROM issues i
                JOIN projects p ON i.project_id = p.project_id
                LEFT JOIN users u_assignee ON i.assignee_id = u_assignee.user_id
                JOIN users u_reporter ON i.reporter_id = u_reporter.user_id
                WHERE p.project_name = %s
            """
            params = [project_name]
            
            if status:
                query += " AND i.status = %s"
                params.append(status)
            
            if assignee_username:
                query += " AND u_assignee.username = %s"
                params.append(assignee_username)
            
            query += " ORDER BY i.created_date DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

def get_issues_by_task_id(self, task_id: str, 
                         project_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Find issues linked to specific task ID"""
    
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT i.issue_key, i.title, i.status, i.priority, i.external_id as task_id,
                       p.project_name, u_assignee.username as assignee_username
                FROM issues i
                JOIN projects p ON i.project_id = p.project_id
                LEFT JOIN users u_assignee ON i.assignee_id = u_assignee.user_id
                WHERE i.external_id = %s
            """
            params = [task_id]
            
            if project_name:
                query += " AND p.project_name = %s"
                params.append(project_name)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

def search_issues(self, search_term: str, project_name: str, 
                 limit: int = 50) -> List[Dict[str, Any]]:
    """Search issues within specific project (MANDATORY project filter)"""
    
    # Get project ID first
    project = self.get_project_by_name(project_name)
    if not project:
        raise ValueError(f"Project '{project_name}' not found")
    
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM search_issues(%s, %s, NULL, %s)
            """, (search_term, project['project_id'], limit))
            return [dict(row) for row in cursor.fetchall()]
```

### **Issue Updates with Audit Trail**
```python
def update_issue_status(self, issue_key: str, new_status: str, 
                       user_id: int, project_name: str) -> bool:
    """Update issue status with mandatory project verification"""
    
    with self.get_connection() as conn:
        with conn.cursor() as cursor:
            # Set current user for audit trail
            self.set_current_user(cursor, user_id)
            
            # Update with project verification
            cursor.execute("""
                UPDATE issues 
                SET status = %s
                FROM projects p
                WHERE issues.project_id = p.project_id
                  AND issues.issue_key = %s
                  AND p.project_name = %s
            """, (new_status, issue_key, project_name))
            
            return cursor.rowcount > 0

def assign_issue(self, issue_key: str, assignee_username: str, 
                user_id: int, project_name: str) -> bool:
    """Assign issue to user with project verification"""
    
    with self.get_connection() as conn:
        with conn.cursor() as cursor:
            # Set current user for audit trail
            self.set_current_user(cursor, user_id)
            
            # Get assignee user ID
            cursor.execute("SELECT user_id FROM users WHERE username = %s", 
                          (assignee_username,))
            assignee_row = cursor.fetchone()
            if not assignee_row:
                raise ValueError(f"User '{assignee_username}' not found")
            
            assignee_id = assignee_row[0]
            
            # Update assignment with project verification
            cursor.execute("""
                UPDATE issues 
                SET assignee_id = %s
                FROM projects p
                WHERE issues.project_id = p.project_id
                  AND issues.issue_key = %s
                  AND p.project_name = %s
            """, (assignee_id, issue_key, project_name))
            
            return cursor.rowcount > 0
```

## 🔄 Task Management Integration

### **Bidirectional Linking**
```python
def link_issue_to_task(self, issue_key: str, task_id: str, 
                      project_name: str) -> bool:
    """Link existing issue to task management system"""
    
    with self.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE issues 
                SET external_id = %s
                FROM projects p
                WHERE issues.project_id = p.project_id
                  AND issues.issue_key = %s
                  AND p.project_name = %s
            """, (task_id, issue_key, project_name))
            
            return cursor.rowcount > 0

def get_task_integration_report(self, project_name: str) -> Dict[str, Any]:
    """Get report on task management integration for project"""
    
    with self.get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_issues,
                    COUNT(*) FILTER (WHERE external_id IS NOT NULL) as linked_issues,
                    COUNT(*) FILTER (WHERE external_id IS NOT NULL AND status != 'closed') as active_linked,
                    ROUND(
                        (COUNT(*) FILTER (WHERE external_id IS NOT NULL) * 100.0 / COUNT(*)), 2
                    ) as link_percentage
                FROM issues i
                JOIN projects p ON i.project_id = p.project_id
                WHERE p.project_name = %s
            """, (project_name,))
            
            return dict(cursor.fetchone())
```

## 🚀 FastAPI Integration Example

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Issue Management API")

class IssueCreate(BaseModel):
    title: str
    description: str
    project_name: str          # MANDATORY
    assignee_username: Optional[str] = None
    priority: str = 'medium'
    severity: str = 'minor'
    task_id: Optional[str] = None  # OPTIONAL: Task system integration
    tags: Optional[List[str]] = None
    environment: Optional[str] = None

class IssueResponse(BaseModel):
    issue_id: int
    issue_key: str
    title: str
    project_name: str
    task_id: Optional[str]
    success: bool

@app.post("/issues", response_model=IssueResponse)
async def create_issue(issue: IssueCreate, current_user_id: int = 2):
    """Create new issue with mandatory project validation"""
    
    issue_manager = IssueManager()
    
    try:
        # Get assignee ID if provided
        assignee_id = None
        if issue.assignee_username:
            with issue_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT user_id FROM users WHERE username = %s", 
                                  (issue.assignee_username,))
                    row = cursor.fetchone()
                    if row:
                        assignee_id = row[0]
        
        # Create issue
        result = issue_manager.create_issue(
            title=issue.title,
            description=issue.description,
            project_name=issue.project_name,  # MANDATORY
            reporter_id=current_user_id,      # MANDATORY
            assignee_id=assignee_id,
            priority=issue.priority,
            severity=issue.severity,
            task_id=issue.task_id,            # OPTIONAL
            tags=issue.tags,
            environment=issue.environment
        )
        
        return IssueResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/projects/{project_name}/issues")
async def get_project_issues(project_name: str, 
                           status: Optional[str] = None,
                           assignee: Optional[str] = None):
    """Get issues for specific project (MANDATORY project filter)"""
    
    issue_manager = IssueManager()
    
    try:
        issues = issue_manager.get_issues_by_project(
            project_name=project_name,  # MANDATORY
            status=status,
            assignee_username=assignee
        )
        return {"project_name": project_name, "issues": issues}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}/issues")
async def get_task_issues(task_id: str, project_name: Optional[str] = None):
    """Get issues linked to specific task ID"""
    
    issue_manager = IssueManager()
    
    try:
        issues = issue_manager.get_issues_by_task_id(
            task_id=task_id,
            project_name=project_name  # OPTIONAL but recommended
        )
        return {"task_id": task_id, "issues": issues}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 📋 Integration Checklist

### **Before Creating Issues**
- [ ] Validate project exists and is active
- [ ] Confirm user has permission for the project
- [ ] Set current user ID for audit trail
- [ ] Validate task ID format if linking

### **Required Error Handling**
- [ ] Invalid project name/ID
- [ ] Non-existent users
- [ ] Invalid status transitions
- [ ] Duplicate task ID links
- [ ] Database connection failures

### **Best Practices**
- [ ] Always filter by project in queries
- [ ] Use external_id for task management linking
- [ ] Include audit trail user context
- [ ] Validate input parameters
- [ ] Handle database transactions properly
- [ ] Log integration activities
