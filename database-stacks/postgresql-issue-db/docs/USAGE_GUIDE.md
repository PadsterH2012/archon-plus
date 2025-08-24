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

### **🤖 Agent Instructions: Dynamic Project Handling**

**IMPORTANT FOR AGENTS**: Always check if the project exists before creating issues. If not found, create the project first.

#### **Step 1: Check if Project Exists**
```sql
-- Check if project exists by name
SELECT project_id, project_name, project_key
FROM projects
WHERE project_name = 'YOUR_PROJECT_NAME'
  AND is_active = TRUE;
```

#### **Step 2: Create Project if Not Found**
```sql
-- If project doesn't exist, create it
-- Generate project key from first 4 letters of name (uppercase, alphanumeric only)
INSERT INTO projects (project_name, description, project_key, created_by)
VALUES (
    'YOUR_PROJECT_NAME',
    'Auto-created project for issue tracking',
    UPPER(LEFT(REGEXP_REPLACE('YOUR_PROJECT_NAME', '[^A-Za-z0-9]', '', 'g'), 4)),
    'system'  -- or current agent user_id
) RETURNING project_id, project_name, project_key;
```

#### **Step 3: Use Project ID for Issue Creation**
```sql
-- Now use the project_id (either found or newly created)
-- Continue with issue creation using the project_id
```

### **Agent-Friendly Project Function**
```sql
-- Function to get or create project (use this in applications)
CREATE OR REPLACE FUNCTION get_or_create_project(
    p_project_name VARCHAR(100),
    p_description TEXT DEFAULT 'Auto-created project for issue tracking',
    p_created_by VARCHAR(50) DEFAULT 'system'
)
RETURNS TABLE (
    project_id INTEGER,
    project_name VARCHAR(100),
    project_key VARCHAR(10),
    was_created BOOLEAN
) AS $$
DECLARE
    existing_project RECORD;
    new_project RECORD;
    generated_key VARCHAR(10);
BEGIN
    -- Try to find existing project
    SELECT p.project_id, p.project_name, p.project_key INTO existing_project
    FROM projects p
    WHERE p.project_name = p_project_name AND p.is_active = TRUE;

    IF FOUND THEN
        -- Return existing project
        RETURN QUERY SELECT existing_project.project_id, existing_project.project_name,
                           existing_project.project_key, FALSE as was_created;
    ELSE
        -- Generate project key from name
        generated_key := UPPER(LEFT(REGEXP_REPLACE(p_project_name, '[^A-Za-z0-9]', '', 'g'), 4));

        -- Ensure key is unique
        WHILE EXISTS (SELECT 1 FROM projects WHERE project_key = generated_key) LOOP
            generated_key := generated_key || FLOOR(RANDOM() * 10)::TEXT;
            generated_key := LEFT(generated_key, 10); -- Ensure max length
        END LOOP;

        -- Create new project
        INSERT INTO projects (project_name, description, project_key, created_by)
        VALUES (p_project_name, p_description, generated_key, p_created_by)
        RETURNING projects.project_id, projects.project_name, projects.project_key INTO new_project;

        -- Return new project
        RETURN QUERY SELECT new_project.project_id, new_project.project_name,
                           new_project.project_key, TRUE as was_created;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### **Available Projects (Reference)**
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

## 🎫 Issue Creation

### **🤖 Agent Workflow: Complete Issue Creation Process**

**MANDATORY AGENT STEPS**: Always follow this sequence when creating issues.

#### **Step 1: Get or Create Project**
```sql
-- Set current user for audit trail (use appropriate agent user_id)
SELECT set_config('app.current_user_id', '3', false); -- archon-agent

-- Get or create project (returns project info)
SELECT * FROM get_or_create_project(
    'YOUR_PROJECT_NAME',                    -- Use actual project name from context
    'Project description if creating new', -- Optional description
    'archon-agent'                         -- Agent creating the project
);
```

#### **Step 2: Create Issue with Project ID**
```sql
-- Use the project_id from Step 1 (either found or created)
INSERT INTO issues (
    title,
    description,
    project_id,        -- MANDATORY: Use project_id from get_or_create_project
    reporter_id,       -- MANDATORY: Agent user_id
    assignee_id,       -- OPTIONAL: Can be same as reporter or different user
    status,
    priority,
    severity,
    external_id        -- OPTIONAL: Use for task_id linking
) VALUES (
    'Issue title (minimum 5 characters)',
    'Detailed description of the issue',
    PROJECT_ID_FROM_STEP_1,  -- MANDATORY: Project ID from get_or_create_project
    3,                       -- Reporter ID (archon-agent)
    3,                       -- Assignee ID (archon-agent or other user)
    'open',
    'medium',
    'minor',
    'TASK-123'              -- OPTIONAL: Link to task management system
);
```

### **🔄 Complete Agent Example**
```sql
-- Complete workflow for agents
DO $$
DECLARE
    project_info RECORD;
    new_issue_id INTEGER;
BEGIN
    -- Set current agent user
    PERFORM set_config('app.current_user_id', '3', false); -- archon-agent

    -- Get or create project
    SELECT * INTO project_info FROM get_or_create_project(
        'Test Project Alpha',
        'Automated testing and development project',
        'archon-agent'
    );

    -- Log project status
    IF project_info.was_created THEN
        RAISE NOTICE 'Created new project: % (ID: %, Key: %)',
            project_info.project_name, project_info.project_id, project_info.project_key;
    ELSE
        RAISE NOTICE 'Using existing project: % (ID: %, Key: %)',
            project_info.project_name, project_info.project_id, project_info.project_key;
    END IF;

    -- Create issue with the project
    INSERT INTO issues (
        title, description, project_id, reporter_id, assignee_id,
        priority, severity, external_id
    ) VALUES (
        'Automated issue creation test',
        'This issue was created automatically by an AI agent to test the project creation workflow.',
        project_info.project_id,  -- Use the project_id we got/created
        3,                        -- archon-agent as reporter
        3,                        -- archon-agent as assignee
        'medium',
        'minor',
        'AUTO-' || EXTRACT(EPOCH FROM NOW())::TEXT  -- Generate unique task ID
    ) RETURNING issue_id INTO new_issue_id;

    RAISE NOTICE 'Created issue ID: % in project: %', new_issue_id, project_info.project_name;
END $$;
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
