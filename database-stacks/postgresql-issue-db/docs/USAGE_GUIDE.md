# Issue Management Database - Usage Guide

## 📋 Overview

This guide covers how to use the issue management database for tracking bugs, features, and development tasks. The system integrates with your existing task management and provides comprehensive issue tracking with audit trails.

## 🔗 System Integration

### **Required Fields**
- **Project Name** (MANDATORY): Human-readable project identifier
- **Project ID** (MANDATORY): Numeric project identifier for database relationships
- **Task ID** (OPTIONAL): Links issues to existing task management system

### **Database Connection**
```bash
# Connection Details
Host: 10.202.70.20
Port: 5433
Database: archon_issues
Username: archon_user
Password: your_very_secure_password_here_change_this

# Connection String
postgresql://archon_user:your_very_secure_password_here_change_this@10.202.70.20:5433/archon_issues
```

## 🏗️ Project Management

### **Available Projects**
```sql
-- View all active projects
SELECT project_id, project_name, project_key, description 
FROM projects 
WHERE is_active = TRUE 
ORDER BY project_name;
```

**Current Projects:**
- **ID 1**: Archon Plus (ARCH) - Main Archon project management platform
- **ID 2**: Database Infrastructure (DB) - Database setup and infrastructure
- **ID 3**: AI Agent Development (AI) - AI agents and workflows
- **ID 4**: User Interface (UI) - Frontend development and UX
- **ID 5**: API Development (API) - Backend API and integrations
- **ID 6**: DevOps & Deployment (OPS) - CI/CD and operational issues

### **Create New Project**
```sql
INSERT INTO projects (project_name, description, project_key, created_by) 
VALUES (
    'New Project Name',
    'Project description and scope',
    'PROJ', -- 2-10 character key for issue prefixes
    'paddy'
);
```

## 🎫 Issue Creation

### **Basic Issue Creation**
```sql
-- Set current user for audit trail
SELECT set_config('app.current_user_id', '2', false); -- paddy's user_id

-- Create issue with mandatory project information
INSERT INTO issues (
    title,
    description,
    project_id,        -- MANDATORY: Must reference existing project
    reporter_id,
    assignee_id,
    status,
    priority,
    severity,
    external_id        -- OPTIONAL: Use for task_id linking
) VALUES (
    'Issue title (minimum 5 characters)',
    'Detailed description of the issue',
    1,                 -- MANDATORY: Project ID (1 = Archon Plus)
    2,                 -- Reporter ID (paddy)
    2,                 -- Assignee ID (paddy)
    'open',
    'medium',
    'minor',
    'TASK-123'         -- OPTIONAL: Link to task management system
);
```

### **Advanced Issue Creation with Tags**
```sql
-- Create issue with automatic tagging and task linking
SELECT create_issue_with_tags(
    'Database connection timeout in production',
    'Users experiencing 30-second timeouts when connecting to the main database during peak hours. This affects user experience and causes transaction failures.',
    1,                 -- MANDATORY: project_id (Archon Plus)
    2,                 -- reporter_id (paddy)
    3,                 -- assignee_id (archon-agent)
    'high',            -- priority
    'major',           -- severity
    ARRAY['bug', 'production', 'database', 'performance'] -- tags
) as new_issue_id;

-- Link to task management system
UPDATE issues 
SET external_id = 'TASK-456'
WHERE issue_id = (SELECT new_issue_id FROM previous_query);
```

## 🔍 Finding Issues

### **By Project (MANDATORY Filter)**
```sql
-- All issues for a specific project
SELECT i.issue_key, i.title, i.status, i.priority, p.project_name
FROM issues i
JOIN projects p ON i.project_id = p.project_id
WHERE p.project_name = 'Archon Plus'  -- MANDATORY: Always filter by project
ORDER BY i.created_date DESC;

-- Or by project ID
SELECT * FROM v_open_issues 
WHERE project_name = 'Archon Plus';
```

### **By Task ID Integration**
```sql
-- Find issues linked to specific tasks
SELECT i.issue_key, i.title, i.external_id as task_id, p.project_name
FROM issues i
JOIN projects p ON i.project_id = p.project_id
WHERE i.external_id = 'TASK-123'
  AND p.project_name = 'Archon Plus';  -- MANDATORY: Include project filter

-- Find all issues with task links
SELECT i.issue_key, i.title, i.external_id as task_id, p.project_name
FROM issues i
JOIN projects p ON i.project_id = p.project_id
WHERE i.external_id IS NOT NULL
  AND p.project_id = 1;  -- MANDATORY: Specify project
```

### **Search with Project Context**
```sql
-- Full-text search within specific project
SELECT * FROM search_issues(
    'database timeout',  -- search term
    1,                   -- MANDATORY: project_id filter
    NULL,                -- status filter (optional)
    10                   -- limit
);
```

## 📊 Reporting and Statistics

### **Project-Specific Reports**
```sql
-- Statistics for specific project (MANDATORY)
SELECT * FROM get_issue_stats(1);  -- project_id required

-- Project comparison
SELECT 
    p.project_name,
    COUNT(i.issue_id) as total_issues,
    COUNT(i.issue_id) FILTER (WHERE i.status = 'open') as open_issues,
    COUNT(i.issue_id) FILTER (WHERE i.external_id IS NOT NULL) as linked_to_tasks
FROM projects p
LEFT JOIN issues i ON p.project_id = i.project_id
WHERE p.is_active = TRUE
GROUP BY p.project_id, p.project_name
ORDER BY total_issues DESC;
```

### **Task Integration Reports**
```sql
-- Issues linked to task management system
SELECT 
    p.project_name,
    COUNT(*) as total_linked_issues,
    COUNT(*) FILTER (WHERE i.status != 'closed') as open_linked_issues
FROM issues i
JOIN projects p ON i.project_id = p.project_id
WHERE i.external_id IS NOT NULL
GROUP BY p.project_id, p.project_name;
```

## 🏷️ Tagging System

### **Available Tags by Category**

**Priority/Type Tags:**
- `bug`, `enhancement`, `critical`, `urgent`

**Environment Tags:**
- `production`, `staging`, `development`, `local`

**Component Tags:**
- `archon-core`, `database`, `api`, `ui-ux`, `backend`, `frontend`

**Technology Tags:**
- `postgresql`, `docker`, `portainer`, `webhook`, `template`

### **Tag Management**
```sql
-- Add tags to existing issue
INSERT INTO issue_tags (issue_id, tag_id, added_by)
SELECT 
    (SELECT issue_id FROM issues WHERE issue_key = 'ARCH-2'),
    tag_id,
    2  -- user_id adding the tag
FROM tags 
WHERE tag_name IN ('bug', 'production', 'urgent');

-- View issues with specific tags in project
SELECT i.issue_key, i.title, STRING_AGG(t.tag_name, ', ') as tags
FROM issues i
JOIN projects p ON i.project_id = p.project_id
JOIN issue_tags it ON i.issue_id = it.issue_id
JOIN tags t ON it.tag_id = t.tag_id
WHERE p.project_name = 'Archon Plus'  -- MANDATORY: Project filter
  AND t.tag_name IN ('bug', 'critical')
GROUP BY i.issue_id, i.issue_key, i.title;
```

## 🔄 Issue Lifecycle Management

### **Status Updates**
```sql
-- Update issue status with audit trail
SELECT set_config('app.current_user_id', '2', false);

UPDATE issues 
SET status = 'in_progress',
    assignee_id = 2
WHERE issue_key = 'ARCH-2'
  AND project_id = 1;  -- MANDATORY: Include project verification
```

### **Workflow States**
- `open` - New issue, ready to be worked on
- `in_progress` - Currently being worked on
- `testing` - Implementation complete, under testing
- `closed` - Issue resolved and verified
- `reopened` - Previously closed issue that needs more work

## 📎 File Attachments

### **Add Attachment Metadata**
```sql
-- Add attachment metadata (files stored separately)
INSERT INTO attachments (
    issue_id,
    filename,           -- System filename (UUID-based)
    original_filename,  -- User's original filename
    file_path,         -- Storage location
    file_size,         -- Size in bytes
    mime_type,         -- File type
    uploaded_by,
    description
) VALUES (
    (SELECT issue_id FROM issues WHERE issue_key = 'ARCH-2'),
    'uuid-generated-filename.png',
    'screenshot-error.png',
    '/attachments/2025/08/uuid-generated-filename.png',
    245760,  -- 240KB
    'image/png',
    2,       -- paddy
    'Screenshot showing the database connection error'
);
```

## 🔍 Audit Trail and History

### **View Issue History**
```sql
-- Complete change history for an issue
SELECT 
    h.created_date,
    h.action_type,
    h.field_name,
    h.old_value,
    h.new_value,
    h.notes,
    u.full_name as changed_by
FROM issue_history h
LEFT JOIN users u ON h.user_id = u.user_id
JOIN issues i ON h.issue_id = i.issue_id
JOIN projects p ON i.project_id = p.project_id
WHERE i.issue_key = 'ARCH-2'
  AND p.project_name = 'Archon Plus'  -- MANDATORY: Project context
ORDER BY h.created_date DESC;
```

## 🤖 AI Agent Integration

### **AI Agent Users**
- **archon-agent** (ID: 3) - General AI development tasks
- **claude-agent** (ID: 4) - Code analysis and assistance
- **task-manager-agent** (ID: 5) - Task coordination
- **qa-agent** (ID: 6) - Quality assurance and testing

### **Create Issue as AI Agent**
```sql
-- Set AI agent as current user
SELECT set_config('app.current_user_id', '3', false); -- archon-agent

-- Create issue with task linking
SELECT create_issue_with_tags(
    'Automated code review found potential memory leak',
    'Static analysis detected potential memory leak in user authentication module. Requires manual review and testing.',
    1,                 -- MANDATORY: project_id
    3,                 -- archon-agent as reporter
    2,                 -- assign to paddy
    'medium',
    'minor',
    ARRAY['ai-generated', 'code-review', 'memory-leak', 'backend']
) as new_issue_id;

-- Link to originating task
UPDATE issues 
SET external_id = 'TASK-789'
WHERE issue_id = (SELECT new_issue_id FROM previous_query);
```

## 📋 Best Practices

### **MANDATORY Requirements**
1. **Always specify project_id or project_name** in queries
2. **Include project context** in all issue operations
3. **Use external_id** for task management system integration
4. **Set current_user_id** before making changes for audit trail

### **Recommended Workflow**
1. **Create Issue**: Use `create_issue_with_tags()` function
2. **Link to Task**: Set `external_id` if applicable
3. **Add Tags**: Use appropriate categorization
4. **Track Progress**: Update status through workflow
5. **Attach Files**: Add metadata for screenshots/logs
6. **Close Issue**: Update status and add resolution notes

### **Query Templates**
```sql
-- Template: Find my issues in specific project
SELECT * FROM v_open_issues 
WHERE assignee_username = 'paddy' 
  AND project_name = 'PROJECT_NAME_HERE';

-- Template: Project dashboard
SELECT * FROM v_project_stats 
WHERE project_name = 'PROJECT_NAME_HERE';

-- Template: Task integration lookup
SELECT i.issue_key, i.title, i.status, i.external_id
FROM issues i
JOIN projects p ON i.project_id = p.project_id
WHERE p.project_name = 'PROJECT_NAME_HERE'
  AND i.external_id = 'TASK_ID_HERE';
```
