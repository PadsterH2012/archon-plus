-- ============================================================================
-- Issue Management Database Schema
-- ============================================================================
-- 
-- This script creates the complete database schema for the issue management
-- system including tables, enums, indexes, and constraints.
--
-- Author: AI IDE Agent
-- Created: 2025-08-24
-- Database: archon_issues
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ============================================================================
-- CUSTOM ENUM TYPES
-- ============================================================================

-- Issue workflow states
CREATE TYPE issue_status AS ENUM (
    'open',
    'in_progress', 
    'testing',
    'closed',
    'reopened'
);

-- Business priority levels
CREATE TYPE issue_priority AS ENUM (
    'critical',
    'high',
    'medium',
    'low'
);

-- Technical severity levels
CREATE TYPE issue_severity AS ENUM (
    'critical',
    'major',
    'minor',
    'trivial'
);

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Projects Table: Organizes issues by project/application
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_by VARCHAR(50) DEFAULT 'system',
    project_key VARCHAR(10) UNIQUE, -- Short key like 'ARCH', 'BUG'
    
    -- Constraints
    CONSTRAINT chk_project_name_length CHECK (LENGTH(project_name) >= 2),
    CONSTRAINT chk_project_key_format CHECK (project_key ~ '^[A-Z]{2,10}$')
);

-- Users Table: Manages all system users (assignees, reporters, etc.)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    user_type VARCHAR(20) DEFAULT 'human', -- 'human', 'ai_agent', 'system'
    is_active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Additional metadata
    avatar_url TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 2),
    CONSTRAINT chk_email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_user_type CHECK (user_type IN ('human', 'ai_agent', 'system'))
);

-- Issues Table: Core issue tracking with all essential metadata
CREATE TABLE issues (
    issue_id SERIAL PRIMARY KEY,
    issue_key VARCHAR(20) UNIQUE NOT NULL, -- Generated: PROJECT-123
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Relationships
    project_id INTEGER NOT NULL REFERENCES projects(project_id) ON DELETE RESTRICT,
    assignee_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    reporter_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    
    -- Status and Priority
    status issue_status DEFAULT 'open',
    priority issue_priority DEFAULT 'medium',
    severity issue_severity DEFAULT 'minor',
    
    -- Dates and Time Tracking
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    closed_date TIMESTAMP,
    
    -- Time Estimates
    estimated_hours DECIMAL(8,2) CHECK (estimated_hours >= 0),
    actual_hours DECIMAL(8,2) CHECK (actual_hours >= 0),
    
    -- Resolution Information
    resolution TEXT,
    version_found VARCHAR(20),
    version_fixed VARCHAR(20),
    
    -- Additional Metadata
    environment VARCHAR(50), -- 'production', 'staging', 'development'
    component VARCHAR(100),
    labels TEXT[], -- Array of labels for quick categorization
    external_id VARCHAR(100), -- For integration with external systems
    
    -- Constraints
    CONSTRAINT chk_title_length CHECK (LENGTH(title) >= 5),
    CONSTRAINT chk_due_date_future CHECK (due_date IS NULL OR due_date >= CURRENT_DATE),
    CONSTRAINT chk_closed_date_logic CHECK (
        (status = 'closed' AND closed_date IS NOT NULL) OR 
        (status != 'closed' AND closed_date IS NULL)
    )
);

-- Issue History Table: Complete audit trail of all changes
CREATE TABLE issue_history (
    history_id SERIAL PRIMARY KEY,
    issue_id INTEGER NOT NULL REFERENCES issues(issue_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Change Information
    action_type VARCHAR(50) NOT NULL, -- 'created', 'updated', 'status_changed', etc.
    field_name VARCHAR(50), -- Which field was changed
    old_value TEXT,
    new_value TEXT,
    notes TEXT,
    
    -- Metadata
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    
    -- Constraints
    CONSTRAINT chk_action_type CHECK (action_type IN (
        'created', 'updated', 'status_changed', 'assigned', 'commented',
        'attachment_added', 'attachment_removed', 'tagged', 'untagged'
    ))
);

-- Attachments Table: File attachment management
CREATE TABLE attachments (
    attachment_id SERIAL PRIMARY KEY,
    issue_id INTEGER NOT NULL REFERENCES issues(issue_id) ON DELETE CASCADE,
    
    -- File Information
    filename VARCHAR(255) NOT NULL, -- System filename (UUID-based)
    original_filename VARCHAR(255) NOT NULL, -- User's original filename
    file_path TEXT NOT NULL, -- Storage location
    file_size BIGINT NOT NULL CHECK (file_size > 0),
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(64), -- SHA-256 hash for integrity
    
    -- Upload Information
    uploaded_by INTEGER NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional Metadata
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    download_count INTEGER DEFAULT 0,
    
    -- Constraints
    CONSTRAINT chk_filename_not_empty CHECK (LENGTH(filename) > 0),
    CONSTRAINT chk_original_filename_not_empty CHECK (LENGTH(original_filename) > 0),
    CONSTRAINT chk_file_size_reasonable CHECK (file_size <= 104857600) -- 100MB limit
);

-- Tags Table: Flexible categorization system
CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    tag_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6B7280', -- Hex color code
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    usage_count INTEGER DEFAULT 0,
    
    -- Constraints
    CONSTRAINT chk_tag_name_format CHECK (tag_name ~ '^[a-z0-9_-]+$'),
    CONSTRAINT chk_tag_name_length CHECK (LENGTH(tag_name) BETWEEN 2 AND 50),
    CONSTRAINT chk_color_format CHECK (color ~ '^#[0-9A-Fa-f]{6}$')
);

-- Issue_Tags Table: Many-to-many relationship between issues and tags
CREATE TABLE issue_tags (
    issue_id INTEGER NOT NULL REFERENCES issues(issue_id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    added_by INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Primary Key
    PRIMARY KEY (issue_id, tag_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Issues table indexes (most critical for performance)
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_priority ON issues(priority);
CREATE INDEX idx_issues_assignee ON issues(assignee_id) WHERE assignee_id IS NOT NULL;
CREATE INDEX idx_issues_reporter ON issues(reporter_id);
CREATE INDEX idx_issues_project ON issues(project_id);
CREATE INDEX idx_issues_created_date ON issues(created_date);
CREATE INDEX idx_issues_updated_date ON issues(updated_date);
CREATE INDEX idx_issues_due_date ON issues(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_issues_key ON issues(issue_key);

-- Composite indexes for common query patterns
CREATE INDEX idx_issues_project_status ON issues(project_id, status);
CREATE INDEX idx_issues_assignee_status ON issues(assignee_id, status) WHERE assignee_id IS NOT NULL;
CREATE INDEX idx_issues_status_priority ON issues(status, priority);

-- Full-text search index
CREATE INDEX idx_issues_search ON issues USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- History table indexes
CREATE INDEX idx_issue_history_issue_id ON issue_history(issue_id);
CREATE INDEX idx_issue_history_date ON issue_history(created_date);
CREATE INDEX idx_issue_history_user ON issue_history(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_issue_history_action ON issue_history(action_type);

-- Attachments indexes
CREATE INDEX idx_attachments_issue_id ON attachments(issue_id);
CREATE INDEX idx_attachments_uploaded_by ON attachments(uploaded_by);
CREATE INDEX idx_attachments_uploaded_date ON attachments(uploaded_date);

-- Tags indexes
CREATE INDEX idx_tags_name ON tags(tag_name);
CREATE INDEX idx_issue_tags_tag_id ON issue_tags(tag_id);

-- Users indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL;
CREATE INDEX idx_users_active ON users(is_active);

-- Projects indexes
CREATE INDEX idx_projects_name ON projects(project_name);
CREATE INDEX idx_projects_key ON projects(project_key) WHERE project_key IS NOT NULL;
CREATE INDEX idx_projects_active ON projects(is_active);

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE projects IS 'Organizes issues by project or application';
COMMENT ON TABLE users IS 'System users including humans and AI agents';
COMMENT ON TABLE issues IS 'Core issue tracking with complete metadata';
COMMENT ON TABLE issue_history IS 'Complete audit trail of all issue changes';
COMMENT ON TABLE attachments IS 'File attachment metadata and references';
COMMENT ON TABLE tags IS 'Flexible tagging system for categorization';
COMMENT ON TABLE issue_tags IS 'Many-to-many relationship between issues and tags';

COMMENT ON COLUMN issues.issue_key IS 'Human-readable unique identifier like ARCH-123';
COMMENT ON COLUMN issues.labels IS 'Quick labels array for fast filtering';
COMMENT ON COLUMN users.user_type IS 'Distinguishes between human users and AI agents';
COMMENT ON COLUMN attachments.file_hash IS 'SHA-256 hash for file integrity verification';
