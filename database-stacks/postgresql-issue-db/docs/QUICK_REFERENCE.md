# Issue Management Database - Quick Reference

## 🚀 Essential Commands

### **Connection**
```bash
# Connect to database
psql -h 10.202.70.20 -p 5433 -U archon_user -d archon_issues

# Connection string
postgresql://archon_user:your_very_secure_password_here_change_this@10.202.70.20:5433/archon_issues
```

### **Set Current User (REQUIRED for audit trail)**
```sql
-- Set before making any changes
SELECT set_config('app.current_user_id', '2', false); -- paddy's user_id
```

## 📋 Projects (MANDATORY)

### **View Projects**
```sql
-- All active projects
SELECT project_id, project_name, project_key FROM projects WHERE is_active = TRUE;

-- Current projects:
-- ID 1: Archon Plus (ARCH)
-- ID 2: Database Infrastructure (DB)  
-- ID 3: AI Agent Development (AI)
-- ID 4: User Interface (UI)
-- ID 5: API Development (API)
-- ID 6: DevOps & Deployment (OPS)
```

### **Create Project**
```sql
INSERT INTO projects (project_name, description, project_key, created_by) 
VALUES ('New Project', 'Description', 'PROJ', 'paddy');
```

## 🎫 Create Issues

### **Simple Issue**
```sql
-- MANDATORY: Set user and include project_id
SELECT set_config('app.current_user_id', '2', false);

INSERT INTO issues (title, description, project_id, reporter_id, assignee_id, external_id) 
VALUES (
    'Issue title here',
    'Detailed description',
    1,           -- MANDATORY: project_id (Archon Plus)
    2,           -- reporter_id (paddy)
    2,           -- assignee_id (paddy)
    'TASK-123'   -- OPTIONAL: task_id link
);
```

### **Issue with Tags**
```sql
-- Create issue with automatic tagging
SELECT create_issue_with_tags(
    'Database performance issue',
    'Slow queries affecting user experience',
    1,                                    -- MANDATORY: project_id
    2,                                    -- reporter_id
    3,                                    -- assignee_id (archon-agent)
    'high',                               -- priority
    'major',                              -- severity
    ARRAY['bug', 'database', 'production'] -- tags
) as new_issue_id;

-- Link to task system
UPDATE issues SET external_id = 'TASK-456' WHERE issue_id = new_issue_id;
```

## 🔍 Find Issues

### **By Project (MANDATORY filter)**
```sql
-- Open issues in project
SELECT * FROM v_open_issues WHERE project_name = 'Archon Plus';

-- All issues in project
SELECT i.issue_key, i.title, i.status, p.project_name
FROM issues i
JOIN projects p ON i.project_id = p.project_id
WHERE p.project_name = 'Archon Plus'
ORDER BY i.created_date DESC;
```

### **By Task ID**
```sql
-- Find issues linked to task
SELECT i.issue_key, i.title, i.external_id as task_id, p.project_name
FROM issues i
JOIN projects p ON i.project_id = p.project_id
WHERE i.external_id = 'TASK-123'
  AND p.project_name = 'Archon Plus';
```

### **Search Issues**
```sql
-- Full-text search in project
SELECT * FROM search_issues('database', 1, NULL, 10); -- project_id required

-- My assigned issues
SELECT * FROM v_open_issues 
WHERE assignee_username = 'paddy' 
  AND project_name = 'Archon Plus';
```

## 🔄 Update Issues

### **Status Change**
```sql
SELECT set_config('app.current_user_id', '2', false);

UPDATE issues 
SET status = 'in_progress'
WHERE issue_key = 'ARCH-2' 
  AND project_id = 1; -- MANDATORY: include project verification
```

### **Assignment**
```sql
UPDATE issues 
SET assignee_id = 3  -- archon-agent
WHERE issue_key = 'ARCH-2' 
  AND project_id = 1;
```

### **Add Tags**
```sql
INSERT INTO issue_tags (issue_id, tag_id, added_by)
SELECT 
    (SELECT issue_id FROM issues WHERE issue_key = 'ARCH-2'),
    tag_id,
    2  -- user adding tag
FROM tags 
WHERE tag_name IN ('urgent', 'backend');
```

## 📊 Reports

### **Project Statistics**
```sql
-- Project overview
SELECT * FROM v_project_stats WHERE project_name = 'Archon Plus';

-- Detailed stats
SELECT * FROM get_issue_stats(1); -- project_id
```

### **Recent Activity**
```sql
-- Recent changes
SELECT created_date, issue_key, action_type, notes, user_name
FROM v_recent_activity 
WHERE project_name = 'Archon Plus'
ORDER BY created_date DESC 
LIMIT 10;
```

### **Task Integration Report**
```sql
-- Issues linked to tasks
SELECT 
    p.project_name,
    COUNT(*) as total_issues,
    COUNT(*) FILTER (WHERE i.external_id IS NOT NULL) as linked_to_tasks,
    ROUND((COUNT(*) FILTER (WHERE i.external_id IS NOT NULL) * 100.0 / COUNT(*)), 2) as link_percentage
FROM issues i
JOIN projects p ON i.project_id = p.project_id
WHERE p.project_name = 'Archon Plus'
GROUP BY p.project_name;
```

## 🏷️ Tags

### **Common Tags**
```sql
-- View available tags
SELECT tag_name, description, color FROM tags ORDER BY usage_count DESC;

-- Popular tags: bug, enhancement, production, database, api, ui-ux, backend, frontend
```

### **Tag Usage**
```sql
-- Issues with specific tags
SELECT i.issue_key, i.title, STRING_AGG(t.tag_name, ', ') as tags
FROM issues i
JOIN projects p ON i.project_id = p.project_id
JOIN issue_tags it ON i.issue_id = it.issue_id
JOIN tags t ON it.tag_id = t.tag_id
WHERE p.project_name = 'Archon Plus'
  AND t.tag_name IN ('bug', 'critical')
GROUP BY i.issue_id, i.issue_key, i.title;
```

## 📎 Attachments

### **Add Attachment Metadata**
```sql
INSERT INTO attachments (
    issue_id, filename, original_filename, file_path, 
    file_size, mime_type, uploaded_by, description
) VALUES (
    (SELECT issue_id FROM issues WHERE issue_key = 'ARCH-2'),
    'uuid-filename.png',
    'screenshot.png',
    '/attachments/2025/08/uuid-filename.png',
    245760,
    'image/png',
    2,
    'Error screenshot'
);
```

## 🔍 Audit Trail

### **Issue History**
```sql
-- Complete change history
SELECT h.created_date, h.action_type, h.field_name, h.old_value, h.new_value, u.full_name
FROM issue_history h
LEFT JOIN users u ON h.user_id = u.user_id
JOIN issues i ON h.issue_id = i.issue_id
WHERE i.issue_key = 'ARCH-2'
ORDER BY h.created_date DESC;
```

## 🤖 AI Agent Integration

### **AI Users**
```sql
-- Available AI agents
SELECT user_id, username, full_name FROM users WHERE user_type = 'ai_agent';

-- ID 3: archon-agent
-- ID 4: claude-agent  
-- ID 5: task-manager-agent
-- ID 6: qa-agent
```

### **Create as AI Agent**
```sql
-- Set AI agent as current user
SELECT set_config('app.current_user_id', '3', false); -- archon-agent

-- Create AI-generated issue
SELECT create_issue_with_tags(
    'Automated code review found issue',
    'Static analysis detected potential problem',
    1, 3, 2, 'medium', 'minor',
    ARRAY['ai-generated', 'code-review']
);
```

## 📋 Status Workflow

### **Valid Statuses**
- `open` - New issue, ready to work
- `in_progress` - Currently being worked on  
- `testing` - Implementation done, under test
- `closed` - Issue resolved and verified
- `reopened` - Previously closed, needs more work

### **Priority Levels**
- `critical` - Immediate attention required
- `high` - Important, high priority
- `medium` - Normal priority (default)
- `low` - Low priority, can wait

### **Severity Levels**
- `critical` - System down, major impact
- `major` - Significant functionality affected
- `minor` - Small issue, workaround available (default)
- `trivial` - Cosmetic or very minor

## ⚠️ Important Notes

### **MANDATORY Requirements**
1. **Always specify project_id or project_name** in queries
2. **Set current_user_id** before making changes
3. **Include project context** in all operations
4. **Use external_id** for task management linking

### **Best Practices**
- Filter by project in all queries
- Use views for common operations
- Link issues to tasks via external_id
- Add meaningful tags for categorization
- Include detailed descriptions
- Update status through proper workflow

### **Common Errors to Avoid**
- Creating issues without project_id
- Forgetting to set current_user_id
- Querying across all projects without filters
- Using invalid status transitions
- Missing audit trail context
