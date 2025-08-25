-- ============================================================================
-- Issue Management Database - Utility Queries and Examples
-- ============================================================================
-- 
-- This script contains useful queries and examples for working with the
-- issue management database. Use these as templates for common operations.
--
-- Author: AI IDE Agent
-- Created: 2025-08-24
-- Database: archon_issues
-- ============================================================================

-- ============================================================================
-- BASIC ISSUE OPERATIONS
-- ============================================================================

-- Create a new issue (example)
/*
-- Set current user for audit trail
SELECT set_config('app.current_user_id', '2', false); -- Replace with actual user_id

INSERT INTO issues (
    title, 
    description, 
    project_id, 
    reporter_id, 
    assignee_id,
    status, 
    priority, 
    severity,
    environment,
    component,
    estimated_hours,
    due_date
) VALUES (
    'Fix database connection timeout',
    'Database connections are timing out after 30 seconds in production environment. This affects user experience and causes failed transactions.',
    1, -- project_id (Archon Plus)
    2, -- reporter_id (paddy)
    3, -- assignee_id (archon-agent)
    'open',
    'high',
    'major',
    'production',
    'database',
    4.0,
    CURRENT_DATE + INTERVAL '3 days'
);
*/

-- Update issue status
/*
UPDATE issues 
SET status = 'in_progress', 
    assignee_id = 2 
WHERE issue_key = 'ARCH-1';
*/

-- Add tags to an issue
/*
INSERT INTO issue_tags (issue_id, tag_id, added_by)
SELECT 
    (SELECT issue_id FROM issues WHERE issue_key = 'ARCH-1'),
    tag_id,
    2 -- user_id adding the tag
FROM tags 
WHERE tag_name IN ('bug', 'production', 'database');
*/

-- ============================================================================
-- COMMON QUERIES
-- ============================================================================

-- 1. Get all open issues assigned to a user
SELECT 
    i.issue_key,
    i.title,
    i.priority,
    i.status,
    p.project_name,
    i.created_date,
    i.due_date
FROM issues i
JOIN projects p ON i.project_id = p.project_id
JOIN users u ON i.assignee_id = u.user_id
WHERE u.username = 'paddy' 
  AND i.status != 'closed'
ORDER BY 
    CASE i.priority 
        WHEN 'critical' THEN 1 
        WHEN 'high' THEN 2 
        WHEN 'medium' THEN 3 
        WHEN 'low' THEN 4 
    END,
    i.due_date NULLS LAST;

-- 2. Get recent activity for all issues
SELECT 
    h.created_date,
    i.issue_key,
    i.title,
    h.action_type,
    h.notes,
    u.full_name as changed_by
FROM issue_history h
JOIN issues i ON h.issue_id = i.issue_id
LEFT JOIN users u ON h.user_id = u.user_id
WHERE h.created_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY h.created_date DESC
LIMIT 20;

-- 3. Get issues by project with statistics
SELECT 
    p.project_name,
    COUNT(*) as total_issues,
    COUNT(*) FILTER (WHERE i.status = 'open') as open_issues,
    COUNT(*) FILTER (WHERE i.status = 'in_progress') as in_progress,
    COUNT(*) FILTER (WHERE i.status = 'closed') as closed_issues,
    COUNT(*) FILTER (WHERE i.priority = 'critical') as critical_issues
FROM projects p
LEFT JOIN issues i ON p.project_id = i.project_id
GROUP BY p.project_id, p.project_name
ORDER BY total_issues DESC;

-- 4. Search issues by text
SELECT * FROM search_issues('database timeout', NULL, NULL, 10);

-- 5. Get overdue issues
SELECT 
    i.issue_key,
    i.title,
    i.priority,
    i.due_date,
    u.full_name as assignee,
    CURRENT_DATE - i.due_date as days_overdue
FROM issues i
LEFT JOIN users u ON i.assignee_id = u.user_id
WHERE i.due_date < CURRENT_DATE 
  AND i.status NOT IN ('closed')
ORDER BY days_overdue DESC;

-- 6. Get issues with specific tags
SELECT 
    i.issue_key,
    i.title,
    i.status,
    i.priority,
    STRING_AGG(t.tag_name, ', ') as tags
FROM issues i
JOIN issue_tags it ON i.issue_id = it.issue_id
JOIN tags t ON it.tag_id = t.tag_id
WHERE t.tag_name IN ('bug', 'critical')
GROUP BY i.issue_id, i.issue_key, i.title, i.status, i.priority
ORDER BY i.created_date DESC;

-- 7. Get issue history for a specific issue
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
WHERE h.issue_id = (SELECT issue_id FROM issues WHERE issue_key = 'ARCH-1')
ORDER BY h.created_date DESC;

-- ============================================================================
-- REPORTING QUERIES
-- ============================================================================

-- 1. Issues created per day (last 30 days)
SELECT 
    DATE(created_date) as date,
    COUNT(*) as issues_created
FROM issues
WHERE created_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_date)
ORDER BY date;

-- 2. Average resolution time by priority
SELECT 
    priority,
    COUNT(*) as total_closed,
    AVG(EXTRACT(EPOCH FROM (closed_date - created_date))/86400) as avg_days_to_close,
    MIN(EXTRACT(EPOCH FROM (closed_date - created_date))/86400) as min_days,
    MAX(EXTRACT(EPOCH FROM (closed_date - created_date))/86400) as max_days
FROM issues
WHERE status = 'closed' AND closed_date IS NOT NULL
GROUP BY priority
ORDER BY 
    CASE priority 
        WHEN 'critical' THEN 1 
        WHEN 'high' THEN 2 
        WHEN 'medium' THEN 3 
        WHEN 'low' THEN 4 
    END;

-- 3. Most active users (by issues created/modified)
SELECT 
    u.full_name,
    u.username,
    COUNT(DISTINCT i.issue_id) as issues_reported,
    COUNT(DISTINCT h.issue_id) as issues_modified,
    MAX(h.created_date) as last_activity
FROM users u
LEFT JOIN issues i ON u.user_id = i.reporter_id
LEFT JOIN issue_history h ON u.user_id = h.user_id
WHERE u.user_type = 'human'
GROUP BY u.user_id, u.full_name, u.username
ORDER BY (COUNT(DISTINCT i.issue_id) + COUNT(DISTINCT h.issue_id)) DESC;

-- 4. Tag usage statistics
SELECT 
    t.tag_name,
    COUNT(it.issue_id) as usage_count,
    COUNT(it.issue_id) FILTER (WHERE i.status != 'closed') as active_usage
FROM tags t
LEFT JOIN issue_tags it ON t.tag_id = it.tag_id
LEFT JOIN issues i ON it.issue_id = i.issue_id
GROUP BY t.tag_id, t.tag_name
ORDER BY usage_count DESC;

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- 1. Find issues without tags
SELECT 
    i.issue_key,
    i.title,
    i.status,
    i.created_date
FROM issues i
LEFT JOIN issue_tags it ON i.issue_id = it.issue_id
WHERE it.issue_id IS NULL
ORDER BY i.created_date DESC;

-- 2. Find orphaned attachments (issues that don't exist)
SELECT 
    a.attachment_id,
    a.original_filename,
    a.file_size,
    a.uploaded_date
FROM attachments a
LEFT JOIN issues i ON a.issue_id = i.issue_id
WHERE i.issue_id IS NULL;

-- 3. Database size information
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 4. Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- ============================================================================
-- BULK OPERATIONS
-- ============================================================================

-- 1. Close all issues older than 90 days with no activity
/*
UPDATE issues 
SET status = 'closed', 
    resolution = 'Auto-closed due to inactivity'
WHERE status != 'closed' 
  AND updated_date < CURRENT_DATE - INTERVAL '90 days'
  AND priority = 'low';
*/

-- 2. Bulk tag assignment
/*
INSERT INTO issue_tags (issue_id, tag_id, added_by)
SELECT 
    i.issue_id,
    (SELECT tag_id FROM tags WHERE tag_name = 'legacy'),
    1 -- system user
FROM issues i
WHERE i.created_date < '2024-01-01'
  AND NOT EXISTS (
      SELECT 1 FROM issue_tags it 
      WHERE it.issue_id = i.issue_id 
        AND it.tag_id = (SELECT tag_id FROM tags WHERE tag_name = 'legacy')
  );
*/

-- ============================================================================
-- USEFUL FUNCTIONS FOR APPLICATIONS
-- ============================================================================

-- Function to create an issue with automatic tagging
CREATE OR REPLACE FUNCTION create_issue_with_tags(
    p_title VARCHAR(255),
    p_description TEXT,
    p_project_id INTEGER,
    p_reporter_id INTEGER,
    p_assignee_id INTEGER DEFAULT NULL,
    p_priority issue_priority DEFAULT 'medium',
    p_severity issue_severity DEFAULT 'minor',
    p_tag_names TEXT[] DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    new_issue_id INTEGER;
    tag_name TEXT;
BEGIN
    -- Set current user for audit trail
    PERFORM set_config('app.current_user_id', p_reporter_id::TEXT, false);
    
    -- Insert the issue
    INSERT INTO issues (
        title, description, project_id, reporter_id, 
        assignee_id, priority, severity
    ) VALUES (
        p_title, p_description, p_project_id, p_reporter_id,
        p_assignee_id, p_priority, p_severity
    ) RETURNING issue_id INTO new_issue_id;
    
    -- Add tags if provided
    IF p_tag_names IS NOT NULL THEN
        FOREACH tag_name IN ARRAY p_tag_names
        LOOP
            INSERT INTO issue_tags (issue_id, tag_id, added_by)
            SELECT new_issue_id, tag_id, p_reporter_id
            FROM tags 
            WHERE tag_name = tag_name
            ON CONFLICT DO NOTHING;
        END LOOP;
    END IF;
    
    RETURN new_issue_id;
END;
$$ LANGUAGE plpgsql;

-- Example usage:
/*
SELECT create_issue_with_tags(
    'Database performance issue',
    'Queries are running slowly on the production database',
    1, -- project_id
    2, -- reporter_id (paddy)
    3, -- assignee_id (archon-agent)
    'high',
    'major',
    ARRAY['bug', 'performance', 'production', 'database']
);
*/
