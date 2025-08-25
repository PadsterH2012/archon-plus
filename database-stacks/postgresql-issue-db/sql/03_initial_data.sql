-- ============================================================================
-- Issue Management Database - Initial Data Population
-- ============================================================================
-- 
-- This script populates the database with initial data including default
-- users, projects, and common tags to get started with issue tracking.
--
-- Author: AI IDE Agent
-- Created: 2025-08-24
-- Database: archon_issues
-- ============================================================================

-- ============================================================================
-- INITIAL USERS
-- ============================================================================

-- System user (for automated actions)
INSERT INTO users (user_id, username, full_name, email, user_type, is_active) VALUES 
(1, 'system', 'System User', 'system@archon.local', 'system', TRUE);

-- Human user (you)
INSERT INTO users (username, full_name, email, user_type, is_active, timezone, preferences) VALUES 
('paddy', 'Paddy H', 'paddy@bastiondata.com', 'human', TRUE, 'Europe/London', 
 '{"notifications": true, "theme": "dark", "language": "en"}');

-- AI Agent users
INSERT INTO users (username, full_name, email, user_type, is_active, preferences) VALUES 
('archon-agent', 'Archon AI Agent', 'archon@archon.local', 'ai_agent', TRUE,
 '{"auto_assign": true, "priority_threshold": "medium"}'),
 
('claude-agent', 'Claude AI Assistant', 'claude@archon.local', 'ai_agent', TRUE,
 '{"specialization": "code_analysis", "auto_tag": true}'),
 
('task-manager-agent', 'Task Manager Agent', 'taskmanager@archon.local', 'ai_agent', TRUE,
 '{"role": "task_coordination", "auto_prioritize": true}'),
 
('qa-agent', 'QA Testing Agent', 'qa@archon.local', 'ai_agent', TRUE,
 '{"role": "quality_assurance", "auto_test": true}');

-- ============================================================================
-- INITIAL PROJECTS
-- ============================================================================

-- Main Archon project
INSERT INTO projects (project_name, description, project_key, created_by) VALUES 
('Archon Plus', 'Main Archon project management and development platform', 'ARCH', 'paddy'),

('Database Infrastructure', 'Database setup, migrations, and infrastructure issues', 'DB', 'system'),

('AI Agent Development', 'Development and improvement of AI agents and workflows', 'AI', 'system'),

('User Interface', 'Frontend development, UI/UX improvements, and user experience', 'UI', 'system'),

('API Development', 'Backend API development, endpoints, and integrations', 'API', 'system'),

('DevOps & Deployment', 'CI/CD, deployment, infrastructure, and operational issues', 'OPS', 'system');

-- ============================================================================
-- COMMON TAGS
-- ============================================================================

-- Priority/Severity Tags
INSERT INTO tags (tag_name, description, color) VALUES 
('bug', 'Software defect or error', '#EF4444'),
('enhancement', 'New feature or improvement', '#10B981'),
('critical', 'Critical issue requiring immediate attention', '#DC2626'),
('urgent', 'High priority issue', '#F59E0B'),
('documentation', 'Documentation related', '#6366F1'),
('testing', 'Testing and QA related', '#8B5CF6'),
('performance', 'Performance optimization', '#F97316'),
('security', 'Security related issue', '#EF4444'),
('ui-ux', 'User interface and experience', '#EC4899'),
('backend', 'Backend/server-side issue', '#059669'),
('frontend', 'Frontend/client-side issue', '#3B82F6'),
('database', 'Database related', '#7C3AED'),
('api', 'API related issue', '#06B6D4'),
('deployment', 'Deployment and infrastructure', '#84CC16'),
('configuration', 'Configuration and setup', '#6B7280'),
('integration', 'Third-party integration', '#F59E0B'),
('ai-agent', 'AI agent related', '#8B5CF6'),
('automation', 'Automation and workflows', '#10B981'),
('monitoring', 'Monitoring and alerting', '#F97316'),
('backup', 'Backup and recovery', '#6366F1');

-- Environment Tags
INSERT INTO tags (tag_name, description, color) VALUES 
('production', 'Production environment', '#DC2626'),
('staging', 'Staging environment', '#F59E0B'),
('development', 'Development environment', '#10B981'),
('local', 'Local development', '#6B7280');

-- Component Tags
INSERT INTO tags (tag_name, description, color) VALUES 
('archon-core', 'Core Archon functionality', '#7C3AED'),
('portainer', 'Portainer related', '#3B82F6'),
('postgresql', 'PostgreSQL database', '#059669'),
('docker', 'Docker containers', '#06B6D4'),
('swarm', 'Docker Swarm', '#0EA5E9'),
('webhook', 'Webhook functionality', '#F59E0B'),
('template', 'Template system', '#8B5CF6'),
('task-management', 'Task management features', '#EC4899'),
('project-management', 'Project management', '#10B981'),
('user-management', 'User management', '#6366F1');

-- ============================================================================
-- SAMPLE ISSUE FOR TESTING
-- ============================================================================

-- Set the current user for audit trail
SELECT set_config('app.current_user_id', '2', false); -- paddy's user_id

-- Create a sample issue to test the system
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
    labels,
    estimated_hours
) VALUES (
    'Setup issue management database schema',
    'Create comprehensive PostgreSQL schema for tracking software issues including:
    
    - Core tables for issues, users, projects
    - Audit trail with complete change history
    - File attachment support
    - Flexible tagging system
    - Performance optimized indexes
    - Automated triggers for data integrity
    
    This will serve as the foundation for tracking all development issues and bugs.',
    1, -- Archon Plus project
    2, -- paddy as reporter
    2, -- paddy as assignee
    'in_progress',
    'high',
    'major',
    'development',
    'database',
    ARRAY['database', 'schema', 'setup'],
    8.0
);

-- Get the issue ID for tagging
DO $$
DECLARE
    sample_issue_id INTEGER;
BEGIN
    SELECT issue_id INTO sample_issue_id FROM issues WHERE title = 'Setup issue management database schema';
    
    -- Add tags to the sample issue
    INSERT INTO issue_tags (issue_id, tag_id, added_by) 
    SELECT sample_issue_id, tag_id, 2 
    FROM tags 
    WHERE tag_name IN ('database', 'enhancement', 'development', 'archon-core', 'postgresql');
END $$;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for open issues with assignee information
CREATE VIEW v_open_issues AS
SELECT 
    i.issue_id,
    i.issue_key,
    i.title,
    i.status,
    i.priority,
    i.severity,
    p.project_name,
    u_assignee.full_name as assignee_name,
    u_assignee.username as assignee_username,
    u_reporter.full_name as reporter_name,
    i.created_date,
    i.updated_date,
    i.due_date,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - i.created_date))/86400 as age_days
FROM issues i
JOIN projects p ON i.project_id = p.project_id
LEFT JOIN users u_assignee ON i.assignee_id = u_assignee.user_id
JOIN users u_reporter ON i.reporter_id = u_reporter.user_id
WHERE i.status != 'closed'
ORDER BY 
    CASE i.priority 
        WHEN 'critical' THEN 1 
        WHEN 'high' THEN 2 
        WHEN 'medium' THEN 3 
        WHEN 'low' THEN 4 
    END,
    i.created_date;

-- View for recent activity
CREATE VIEW v_recent_activity AS
SELECT 
    h.history_id,
    h.issue_id,
    i.issue_key,
    i.title as issue_title,
    h.action_type,
    h.field_name,
    h.old_value,
    h.new_value,
    h.notes,
    u.full_name as user_name,
    u.username,
    h.created_date,
    p.project_name
FROM issue_history h
JOIN issues i ON h.issue_id = i.issue_id
JOIN projects p ON i.project_id = p.project_id
LEFT JOIN users u ON h.user_id = u.user_id
ORDER BY h.created_date DESC;

-- View for issue statistics by project
CREATE VIEW v_project_stats AS
SELECT 
    p.project_id,
    p.project_name,
    p.project_key,
    COUNT(i.issue_id) as total_issues,
    COUNT(i.issue_id) FILTER (WHERE i.status = 'open') as open_issues,
    COUNT(i.issue_id) FILTER (WHERE i.status = 'in_progress') as in_progress_issues,
    COUNT(i.issue_id) FILTER (WHERE i.status = 'testing') as testing_issues,
    COUNT(i.issue_id) FILTER (WHERE i.status = 'closed') as closed_issues,
    COUNT(i.issue_id) FILTER (WHERE i.priority = 'critical') as critical_issues,
    COUNT(i.issue_id) FILTER (WHERE i.priority = 'high') as high_priority_issues,
    AVG(EXTRACT(EPOCH FROM (COALESCE(i.closed_date, CURRENT_TIMESTAMP) - i.created_date))/86400) as avg_age_days
FROM projects p
LEFT JOIN issues i ON p.project_id = i.project_id
WHERE p.is_active = TRUE
GROUP BY p.project_id, p.project_name, p.project_key
ORDER BY p.project_name;

-- View for tag usage statistics
CREATE VIEW v_tag_stats AS
SELECT 
    t.tag_id,
    t.tag_name,
    t.description,
    t.color,
    t.usage_count,
    COUNT(it.issue_id) as current_usage,
    t.created_date
FROM tags t
LEFT JOIN issue_tags it ON t.tag_id = it.tag_id
GROUP BY t.tag_id, t.tag_name, t.description, t.color, t.usage_count, t.created_date
ORDER BY current_usage DESC, t.tag_name;

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant permissions to the archon_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO archon_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO archon_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO archon_user;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

-- Insert a completion record
INSERT INTO issue_history (issue_id, user_id, action_type, field_name, old_value, new_value, notes)
SELECT 
    i.issue_id, 
    1, -- system user
    'updated', 
    'database_setup', 
    NULL, 
    'completed',
    'Issue management database schema created successfully with all tables, triggers, functions, and initial data populated.'
FROM issues i 
WHERE i.title = 'Setup issue management database schema';

-- Display success message
DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Issue Management Database Setup Complete!';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Tables created: %, %, %, %, %, %, %', 'projects', 'users', 'issues', 'issue_history', 'attachments', 'tags', 'issue_tags';
    RAISE NOTICE 'Initial data: % users, % projects, % tags, % sample issue', 
        (SELECT COUNT(*) FROM users),
        (SELECT COUNT(*) FROM projects), 
        (SELECT COUNT(*) FROM tags),
        (SELECT COUNT(*) FROM issues);
    RAISE NOTICE 'Views created: v_open_issues, v_recent_activity, v_project_stats, v_tag_stats';
    RAISE NOTICE 'Ready for issue tracking!';
    RAISE NOTICE '============================================================================';
END $$;
