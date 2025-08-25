-- ============================================================================
-- Issue Management Database - Task Integration Enhancements
-- ============================================================================
-- 
-- This script adds enhancements for better integration with task management
-- systems, including improved indexing and utility functions for task linking.
--
-- Author: AI IDE Agent
-- Created: 2025-08-24
-- Database: archon_issues
-- ============================================================================

-- ============================================================================
-- ENHANCED INDEXES FOR TASK INTEGRATION
-- ============================================================================

-- Index for external_id (task_id) lookups
CREATE INDEX IF NOT EXISTS idx_issues_external_id ON issues(external_id) 
WHERE external_id IS NOT NULL;

-- Composite index for project + external_id queries
CREATE INDEX IF NOT EXISTS idx_issues_project_external_id ON issues(project_id, external_id) 
WHERE external_id IS NOT NULL;

-- Index for finding unlinked issues
CREATE INDEX IF NOT EXISTS idx_issues_no_external_id ON issues(project_id, status) 
WHERE external_id IS NULL;

-- ============================================================================
-- TASK INTEGRATION UTILITY FUNCTIONS
-- ============================================================================

-- Function to get or create project (AGENT-FRIENDLY)
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
        WHILE EXISTS (SELECT 1 FROM projects pr WHERE pr.project_key = generated_key) LOOP
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

-- Function to link existing issue to task
CREATE OR REPLACE FUNCTION link_issue_to_task(
    p_issue_key VARCHAR(20),
    p_task_id VARCHAR(100),
    p_project_name VARCHAR(100),
    p_user_id INTEGER DEFAULT 1
)
RETURNS BOOLEAN AS $$
DECLARE
    rows_updated INTEGER;
BEGIN
    -- Set current user for audit trail
    PERFORM set_config('app.current_user_id', p_user_id::TEXT, false);
    
    -- Update the issue with task link and project verification
    UPDATE issues 
    SET external_id = p_task_id
    FROM projects p
    WHERE issues.project_id = p.project_id
      AND issues.issue_key = p_issue_key
      AND p.project_name = p_project_name;
    
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    
    -- Log the linking action
    IF rows_updated > 0 THEN
        INSERT INTO issue_history (
            issue_id, user_id, action_type, field_name, 
            old_value, new_value, notes
        ) 
        SELECT 
            i.issue_id, p_user_id, 'updated', 'external_id',
            NULL, p_task_id,
            'Linked to task: ' || p_task_id
        FROM issues i
        JOIN projects p ON i.project_id = p.project_id
        WHERE i.issue_key = p_issue_key 
          AND p.project_name = p_project_name;
    END IF;
    
    RETURN rows_updated > 0;
END;
$$ LANGUAGE plpgsql;

-- Function to find issues by task ID with project context
CREATE OR REPLACE FUNCTION get_issues_by_task_id(
    p_task_id VARCHAR(100),
    p_project_name VARCHAR(100) DEFAULT NULL
)
RETURNS TABLE (
    issue_id INTEGER,
    issue_key VARCHAR(20),
    title VARCHAR(255),
    status issue_status,
    priority issue_priority,
    project_name VARCHAR(100),
    assignee_name VARCHAR(100),
    reporter_name VARCHAR(100),
    created_date TIMESTAMP,
    task_id VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.issue_id,
        i.issue_key,
        i.title,
        i.status,
        i.priority,
        p.project_name,
        u_assignee.full_name as assignee_name,
        u_reporter.full_name as reporter_name,
        i.created_date,
        i.external_id as task_id
    FROM issues i
    JOIN projects p ON i.project_id = p.project_id
    LEFT JOIN users u_assignee ON i.assignee_id = u_assignee.user_id
    JOIN users u_reporter ON i.reporter_id = u_reporter.user_id
    WHERE i.external_id = p_task_id
      AND (p_project_name IS NULL OR p.project_name = p_project_name)
    ORDER BY i.created_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get task integration statistics
CREATE OR REPLACE FUNCTION get_task_integration_stats(p_project_name VARCHAR(100))
RETURNS TABLE (
    project_name VARCHAR(100),
    total_issues BIGINT,
    linked_issues BIGINT,
    unlinked_issues BIGINT,
    link_percentage NUMERIC,
    active_linked_issues BIGINT,
    closed_linked_issues BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.project_name,
        COUNT(i.issue_id) as total_issues,
        COUNT(i.issue_id) FILTER (WHERE i.external_id IS NOT NULL) as linked_issues,
        COUNT(i.issue_id) FILTER (WHERE i.external_id IS NULL) as unlinked_issues,
        ROUND(
            (COUNT(i.issue_id) FILTER (WHERE i.external_id IS NOT NULL) * 100.0 / 
             NULLIF(COUNT(i.issue_id), 0)), 2
        ) as link_percentage,
        COUNT(i.issue_id) FILTER (WHERE i.external_id IS NOT NULL AND i.status != 'closed') as active_linked_issues,
        COUNT(i.issue_id) FILTER (WHERE i.external_id IS NOT NULL AND i.status = 'closed') as closed_linked_issues
    FROM projects p
    LEFT JOIN issues i ON p.project_id = i.project_id
    WHERE p.project_name = p_project_name
      AND p.is_active = TRUE
    GROUP BY p.project_id, p.project_name;
END;
$$ LANGUAGE plpgsql;

-- Function to bulk link issues to tasks
CREATE OR REPLACE FUNCTION bulk_link_issues_to_tasks(
    p_links JSONB, -- Array of {issue_key, task_id, project_name}
    p_user_id INTEGER DEFAULT 1
)
RETURNS TABLE (
    issue_key VARCHAR(20),
    task_id VARCHAR(100),
    success BOOLEAN,
    message TEXT
) AS $$
DECLARE
    link_record JSONB;
    current_issue_key VARCHAR(20);
    current_task_id VARCHAR(100);
    current_project_name VARCHAR(100);
    link_success BOOLEAN;
BEGIN
    -- Set current user for audit trail
    PERFORM set_config('app.current_user_id', p_user_id::TEXT, false);
    
    -- Process each link
    FOR link_record IN SELECT * FROM jsonb_array_elements(p_links)
    LOOP
        current_issue_key := link_record->>'issue_key';
        current_task_id := link_record->>'task_id';
        current_project_name := link_record->>'project_name';
        
        -- Attempt to link
        SELECT link_issue_to_task(
            current_issue_key, 
            current_task_id, 
            current_project_name, 
            p_user_id
        ) INTO link_success;
        
        -- Return result
        RETURN QUERY SELECT 
            current_issue_key,
            current_task_id,
            link_success,
            CASE 
                WHEN link_success THEN 'Successfully linked'
                ELSE 'Failed to link - issue or project not found'
            END as message;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ENHANCED VIEWS FOR TASK INTEGRATION
-- ============================================================================

-- View for issues with task integration status
CREATE OR REPLACE VIEW v_issues_with_task_status AS
SELECT 
    i.issue_id,
    i.issue_key,
    i.title,
    i.status,
    i.priority,
    i.severity,
    p.project_name,
    p.project_key,
    u_assignee.full_name as assignee_name,
    u_assignee.username as assignee_username,
    u_reporter.full_name as reporter_name,
    i.created_date,
    i.updated_date,
    i.due_date,
    i.external_id as task_id,
    CASE 
        WHEN i.external_id IS NOT NULL THEN 'linked'
        ELSE 'unlinked'
    END as task_link_status,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - i.created_date))/86400 as age_days
FROM issues i
JOIN projects p ON i.project_id = p.project_id
LEFT JOIN users u_assignee ON i.assignee_id = u_assignee.user_id
JOIN users u_reporter ON i.reporter_id = u_reporter.user_id
ORDER BY i.created_date DESC;

-- View for task integration summary by project
CREATE OR REPLACE VIEW v_task_integration_summary AS
SELECT 
    p.project_id,
    p.project_name,
    p.project_key,
    COUNT(i.issue_id) as total_issues,
    COUNT(i.issue_id) FILTER (WHERE i.external_id IS NOT NULL) as linked_issues,
    COUNT(i.issue_id) FILTER (WHERE i.external_id IS NULL) as unlinked_issues,
    ROUND(
        (COUNT(i.issue_id) FILTER (WHERE i.external_id IS NOT NULL) * 100.0 / 
         NULLIF(COUNT(i.issue_id), 0)), 2
    ) as link_percentage,
    COUNT(i.issue_id) FILTER (WHERE i.external_id IS NOT NULL AND i.status != 'closed') as active_linked,
    COUNT(i.issue_id) FILTER (WHERE i.external_id IS NOT NULL AND i.status = 'closed') as closed_linked
FROM projects p
LEFT JOIN issues i ON p.project_id = i.project_id
WHERE p.is_active = TRUE
GROUP BY p.project_id, p.project_name, p.project_key
ORDER BY total_issues DESC;

-- ============================================================================
-- TASK ID VALIDATION AND CONSTRAINTS
-- ============================================================================

-- Add constraint to ensure task IDs follow a pattern (optional)
-- Uncomment if you want to enforce task ID format
/*
ALTER TABLE issues 
ADD CONSTRAINT chk_external_id_format 
CHECK (external_id IS NULL OR external_id ~ '^[A-Z]+-[0-9]+$');
*/

-- Add unique constraint for task IDs within projects (optional)
-- Uncomment if you want to prevent duplicate task links within a project
/*
CREATE UNIQUE INDEX idx_issues_project_external_id_unique 
ON issues(project_id, external_id) 
WHERE external_id IS NOT NULL;
*/

-- ============================================================================
-- UTILITY QUERIES FOR TASK MANAGEMENT
-- ============================================================================

-- Find issues that should be linked to tasks but aren't
CREATE OR REPLACE FUNCTION find_unlinkable_issues(p_project_name VARCHAR(100))
RETURNS TABLE (
    issue_key VARCHAR(20),
    title VARCHAR(255),
    status issue_status,
    created_date TIMESTAMP,
    age_days NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.issue_key,
        i.title,
        i.status,
        i.created_date,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - i.created_date))/86400 as age_days
    FROM issues i
    JOIN projects p ON i.project_id = p.project_id
    WHERE p.project_name = p_project_name
      AND i.external_id IS NULL
      AND i.status != 'closed'
    ORDER BY i.created_date DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS AND DOCUMENTATION
-- ============================================================================

COMMENT ON FUNCTION link_issue_to_task IS 'Links an existing issue to a task management system via external_id';
COMMENT ON FUNCTION get_issues_by_task_id IS 'Retrieves all issues linked to a specific task ID';
COMMENT ON FUNCTION get_task_integration_stats IS 'Provides statistics on task integration for a project';
COMMENT ON FUNCTION bulk_link_issues_to_tasks IS 'Bulk operation to link multiple issues to tasks';
COMMENT ON FUNCTION find_unlinkable_issues IS 'Finds issues that could be linked to tasks but are not';

COMMENT ON VIEW v_issues_with_task_status IS 'Enhanced issue view showing task integration status';
COMMENT ON VIEW v_task_integration_summary IS 'Project-level summary of task integration statistics';

COMMENT ON COLUMN issues.external_id IS 'Links to external task management systems (task_id)';

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Task Integration Enhancements Complete!';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Added: Enhanced indexes for task_id lookups';
    RAISE NOTICE 'Added: Utility functions for task linking and statistics';
    RAISE NOTICE 'Added: Enhanced views with task integration status';
    RAISE NOTICE 'Added: Bulk operations for task management integration';
    RAISE NOTICE 'Ready for advanced task management system integration!';
    RAISE NOTICE '============================================================================';
END $$;
