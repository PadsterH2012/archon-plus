-- ============================================================================
-- Issue Management Database - Triggers and Functions
-- ============================================================================
-- 
-- This script creates automated triggers and utility functions for the
-- issue management system including audit trails and business logic.
--
-- Author: AI IDE Agent
-- Created: 2025-08-24
-- Database: archon_issues
-- ============================================================================

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to update the updated_date column automatically
CREATE OR REPLACE FUNCTION update_updated_date_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_date = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to generate issue keys (PROJECT-123 format)
CREATE OR REPLACE FUNCTION generate_issue_key()
RETURNS TRIGGER AS $$
DECLARE
    project_key_val VARCHAR(10);
    next_number INTEGER;
    new_issue_key VARCHAR(20);
BEGIN
    -- Get the project key
    SELECT project_key INTO project_key_val 
    FROM projects 
    WHERE project_id = NEW.project_id;
    
    -- If no project key, use project name first 4 chars
    IF project_key_val IS NULL THEN
        SELECT UPPER(LEFT(REGEXP_REPLACE(project_name, '[^A-Za-z0-9]', '', 'g'), 4))
        INTO project_key_val
        FROM projects 
        WHERE project_id = NEW.project_id;
    END IF;
    
    -- Get next number for this project
    SELECT COALESCE(MAX(CAST(SPLIT_PART(issue_key, '-', 2) AS INTEGER)), 0) + 1
    INTO next_number
    FROM issues 
    WHERE issue_key LIKE project_key_val || '-%';
    
    -- Generate the new issue key
    new_issue_key := project_key_val || '-' || next_number;
    NEW.issue_key := new_issue_key;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to log issue changes to history
CREATE OR REPLACE FUNCTION log_issue_change()
RETURNS TRIGGER AS $$
DECLARE
    change_user_id INTEGER;
    change_action VARCHAR(50);
BEGIN
    -- Determine the user making the change (from session or default to system)
    change_user_id := COALESCE(
        NULLIF(current_setting('app.current_user_id', true), '')::INTEGER,
        1 -- Default to system user
    );
    
    -- Determine action type
    IF TG_OP = 'INSERT' THEN
        change_action := 'created';
        
        -- Log the creation
        INSERT INTO issue_history (
            issue_id, user_id, action_type, field_name, 
            old_value, new_value, notes
        ) VALUES (
            NEW.issue_id, change_user_id, change_action, 'issue',
            NULL, 'Issue created', 
            'Initial issue creation with title: ' || NEW.title
        );
        
    ELSIF TG_OP = 'UPDATE' THEN
        change_action := 'updated';
        
        -- Log specific field changes
        IF OLD.status != NEW.status THEN
            INSERT INTO issue_history (
                issue_id, user_id, action_type, field_name, 
                old_value, new_value, notes
            ) VALUES (
                NEW.issue_id, change_user_id, 'status_changed', 'status',
                OLD.status::TEXT, NEW.status::TEXT,
                'Status changed from ' || OLD.status || ' to ' || NEW.status
            );
        END IF;
        
        IF OLD.assignee_id IS DISTINCT FROM NEW.assignee_id THEN
            INSERT INTO issue_history (
                issue_id, user_id, action_type, field_name, 
                old_value, new_value, notes
            ) VALUES (
                NEW.issue_id, change_user_id, 'assigned', 'assignee_id',
                COALESCE(OLD.assignee_id::TEXT, 'NULL'), 
                COALESCE(NEW.assignee_id::TEXT, 'NULL'),
                'Assignee changed'
            );
        END IF;
        
        IF OLD.priority != NEW.priority THEN
            INSERT INTO issue_history (
                issue_id, user_id, action_type, field_name, 
                old_value, new_value, notes
            ) VALUES (
                NEW.issue_id, change_user_id, 'updated', 'priority',
                OLD.priority::TEXT, NEW.priority::TEXT,
                'Priority changed from ' || OLD.priority || ' to ' || NEW.priority
            );
        END IF;
        
        IF OLD.title != NEW.title THEN
            INSERT INTO issue_history (
                issue_id, user_id, action_type, field_name, 
                old_value, new_value, notes
            ) VALUES (
                NEW.issue_id, change_user_id, 'updated', 'title',
                OLD.title, NEW.title,
                'Title updated'
            );
        END IF;
        
        IF OLD.description IS DISTINCT FROM NEW.description THEN
            INSERT INTO issue_history (
                issue_id, user_id, action_type, field_name, 
                old_value, new_value, notes
            ) VALUES (
                NEW.issue_id, change_user_id, 'updated', 'description',
                COALESCE(OLD.description, 'NULL'), 
                COALESCE(NEW.description, 'NULL'),
                'Description updated'
            );
        END IF;
        
        -- Set closed_date when status changes to closed
        IF OLD.status != 'closed' AND NEW.status = 'closed' THEN
            NEW.closed_date := CURRENT_TIMESTAMP;
        ELSIF OLD.status = 'closed' AND NEW.status != 'closed' THEN
            NEW.closed_date := NULL;
        END IF;
        
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Function to update tag usage count
CREATE OR REPLACE FUNCTION update_tag_usage_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE tags SET usage_count = usage_count + 1 WHERE tag_id = NEW.tag_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE tags SET usage_count = usage_count - 1 WHERE tag_id = OLD.tag_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Function to log attachment changes
CREATE OR REPLACE FUNCTION log_attachment_change()
RETURNS TRIGGER AS $$
DECLARE
    change_user_id INTEGER;
BEGIN
    change_user_id := COALESCE(
        NULLIF(current_setting('app.current_user_id', true), '')::INTEGER,
        NEW.uploaded_by
    );
    
    IF TG_OP = 'INSERT' THEN
        INSERT INTO issue_history (
            issue_id, user_id, action_type, field_name, 
            old_value, new_value, notes
        ) VALUES (
            NEW.issue_id, change_user_id, 'attachment_added', 'attachment',
            NULL, NEW.original_filename,
            'Attachment added: ' || NEW.original_filename || ' (' || 
            pg_size_pretty(NEW.file_size) || ')'
        );
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO issue_history (
            issue_id, user_id, action_type, field_name, 
            old_value, new_value, notes
        ) VALUES (
            OLD.issue_id, change_user_id, 'attachment_removed', 'attachment',
            OLD.original_filename, NULL,
            'Attachment removed: ' || OLD.original_filename
        );
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Function to log tag changes
CREATE OR REPLACE FUNCTION log_tag_change()
RETURNS TRIGGER AS $$
DECLARE
    change_user_id INTEGER;
    tag_name_val VARCHAR(50);
BEGIN
    change_user_id := COALESCE(
        NULLIF(current_setting('app.current_user_id', true), '')::INTEGER,
        COALESCE(NEW.added_by, OLD.added_by, 1)
    );
    
    IF TG_OP = 'INSERT' THEN
        SELECT tag_name INTO tag_name_val FROM tags WHERE tag_id = NEW.tag_id;
        INSERT INTO issue_history (
            issue_id, user_id, action_type, field_name, 
            old_value, new_value, notes
        ) VALUES (
            NEW.issue_id, change_user_id, 'tagged', 'tags',
            NULL, tag_name_val,
            'Tag added: ' || tag_name_val
        );
    ELSIF TG_OP = 'DELETE' THEN
        SELECT tag_name INTO tag_name_val FROM tags WHERE tag_id = OLD.tag_id;
        INSERT INTO issue_history (
            issue_id, user_id, action_type, field_name, 
            old_value, new_value, notes
        ) VALUES (
            OLD.issue_id, change_user_id, 'untagged', 'tags',
            tag_name_val, NULL,
            'Tag removed: ' || tag_name_val
        );
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Automatic updated_date triggers
CREATE TRIGGER trigger_projects_updated_date
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_date_column();

CREATE TRIGGER trigger_users_updated_date
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_date_column();

CREATE TRIGGER trigger_issues_updated_date
    BEFORE UPDATE ON issues
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_date_column();

-- Issue key generation trigger
CREATE TRIGGER trigger_generate_issue_key
    BEFORE INSERT ON issues
    FOR EACH ROW
    EXECUTE FUNCTION generate_issue_key();

-- Issue change logging triggers
CREATE TRIGGER trigger_log_issue_changes
    AFTER INSERT OR UPDATE ON issues
    FOR EACH ROW
    EXECUTE FUNCTION log_issue_change();

-- Tag usage count triggers
CREATE TRIGGER trigger_tag_usage_insert
    AFTER INSERT ON issue_tags
    FOR EACH ROW
    EXECUTE FUNCTION update_tag_usage_count();

CREATE TRIGGER trigger_tag_usage_delete
    AFTER DELETE ON issue_tags
    FOR EACH ROW
    EXECUTE FUNCTION update_tag_usage_count();

-- Attachment logging triggers
CREATE TRIGGER trigger_log_attachment_changes
    AFTER INSERT OR DELETE ON attachments
    FOR EACH ROW
    EXECUTE FUNCTION log_attachment_change();

-- Tag change logging triggers
CREATE TRIGGER trigger_log_tag_changes
    AFTER INSERT OR DELETE ON issue_tags
    FOR EACH ROW
    EXECUTE FUNCTION log_tag_change();

-- ============================================================================
-- UTILITY FUNCTIONS FOR APPLICATION USE
-- ============================================================================

-- Function to search issues with full-text search
CREATE OR REPLACE FUNCTION search_issues(
    search_term TEXT,
    project_filter INTEGER DEFAULT NULL,
    status_filter issue_status DEFAULT NULL,
    limit_count INTEGER DEFAULT 50
)
RETURNS TABLE (
    issue_id INTEGER,
    issue_key VARCHAR(20),
    title VARCHAR(255),
    status issue_status,
    priority issue_priority,
    assignee_name VARCHAR(100),
    created_date TIMESTAMP,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.issue_id,
        i.issue_key,
        i.title,
        i.status,
        i.priority,
        u.full_name as assignee_name,
        i.created_date,
        ts_rank(to_tsvector('english', i.title || ' ' || COALESCE(i.description, '')), 
                plainto_tsquery('english', search_term)) as rank
    FROM issues i
    LEFT JOIN users u ON i.assignee_id = u.user_id
    WHERE 
        to_tsvector('english', i.title || ' ' || COALESCE(i.description, '')) @@ 
        plainto_tsquery('english', search_term)
        AND (project_filter IS NULL OR i.project_id = project_filter)
        AND (status_filter IS NULL OR i.status = status_filter)
    ORDER BY rank DESC, i.created_date DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get issue statistics
CREATE OR REPLACE FUNCTION get_issue_stats(project_filter INTEGER DEFAULT NULL)
RETURNS TABLE (
    total_issues BIGINT,
    open_issues BIGINT,
    in_progress_issues BIGINT,
    closed_issues BIGINT,
    critical_priority BIGINT,
    high_priority BIGINT,
    avg_resolution_days NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_issues,
        COUNT(*) FILTER (WHERE status = 'open') as open_issues,
        COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_issues,
        COUNT(*) FILTER (WHERE status = 'closed') as closed_issues,
        COUNT(*) FILTER (WHERE priority = 'critical') as critical_priority,
        COUNT(*) FILTER (WHERE priority = 'high') as high_priority,
        AVG(EXTRACT(EPOCH FROM (closed_date - created_date))/86400) 
        FILTER (WHERE closed_date IS NOT NULL) as avg_resolution_days
    FROM issues
    WHERE project_filter IS NULL OR project_id = project_filter;
END;
$$ LANGUAGE plpgsql;
