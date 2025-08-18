-- =====================================================
-- ARCHON WORKFLOW SYSTEM MIGRATION
-- =====================================================
-- This script adds the workflow orchestration system to Archon
-- 
-- Features:
-- - Workflow templates with versioning
-- - Workflow steps with different types (action, condition, workflow_link)
-- - Workflow executions with progress tracking
-- - Integration with existing MCP tools
-- 
-- Run this script in your Supabase SQL Editor after complete_setup.sql
-- =====================================================

-- =====================================================
-- SECTION 1: WORKFLOW ENUMS AND TYPES
-- =====================================================

-- Workflow status enumeration
DO $$ BEGIN
    CREATE TYPE workflow_status AS ENUM ('draft', 'active', 'deprecated', 'archived');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Workflow step type enumeration
DO $$ BEGIN
    CREATE TYPE workflow_step_type AS ENUM ('action', 'condition', 'workflow_link', 'parallel', 'loop');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Workflow execution status enumeration
DO $$ BEGIN
    CREATE TYPE workflow_execution_status AS ENUM ('pending', 'running', 'paused', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Step execution status enumeration
DO $$ BEGIN
    CREATE TYPE step_execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'skipped', 'retrying');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- =====================================================
-- SECTION 2: WORKFLOW TEMPLATES TABLE
-- =====================================================

-- Workflow Templates - Define reusable workflow patterns
CREATE TABLE IF NOT EXISTS archon_workflow_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  version VARCHAR(50) DEFAULT '1.0.0',
  status workflow_status DEFAULT 'draft',
  
  -- Workflow metadata
  category VARCHAR(100), -- e.g., 'infrastructure', 'deployment', 'testing'
  tags JSONB DEFAULT '[]'::jsonb, -- Array of tags for categorization
  
  -- Workflow configuration
  parameters JSONB DEFAULT '{}'::jsonb, -- Input parameters schema
  outputs JSONB DEFAULT '{}'::jsonb, -- Expected outputs schema
  
  -- Workflow definition
  steps JSONB NOT NULL DEFAULT '[]'::jsonb, -- Array of workflow steps
  
  -- Execution settings
  timeout_minutes INTEGER DEFAULT 60,
  max_retries INTEGER DEFAULT 3,
  retry_delay_seconds INTEGER DEFAULT 30,
  
  -- Permissions and access
  created_by TEXT NOT NULL DEFAULT 'system',
  is_public BOOLEAN DEFAULT false,
  allowed_assignees JSONB DEFAULT '[]'::jsonb, -- Array of allowed assignees
  
  -- Audit fields
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT chk_workflow_name_format CHECK (name ~ '^[a-z0-9_-]+$'),
  CONSTRAINT chk_workflow_version_format CHECK (version ~ '^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'),
  CONSTRAINT chk_timeout_positive CHECK (timeout_minutes > 0),
  CONSTRAINT chk_retries_non_negative CHECK (max_retries >= 0)
);

-- =====================================================
-- SECTION 3: WORKFLOW EXECUTIONS TABLE
-- =====================================================

-- Workflow Executions - Track individual workflow runs
CREATE TABLE IF NOT EXISTS archon_workflow_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_template_id UUID REFERENCES archon_workflow_templates(id) ON DELETE CASCADE,
  
  -- Execution context
  triggered_by TEXT NOT NULL, -- Agent or user who triggered the execution
  trigger_context JSONB DEFAULT '{}'::jsonb, -- Context that triggered the workflow (task, event, etc.)
  
  -- Execution parameters
  input_parameters JSONB DEFAULT '{}'::jsonb, -- Actual input values
  execution_context JSONB DEFAULT '{}'::jsonb, -- Runtime context and variables
  
  -- Status and progress
  status workflow_execution_status DEFAULT 'pending',
  current_step_index INTEGER DEFAULT 0,
  total_steps INTEGER DEFAULT 0,
  progress_percentage DECIMAL(5,2) DEFAULT 0.00,
  
  -- Timing
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  paused_at TIMESTAMPTZ,
  
  -- Results and errors
  output_data JSONB DEFAULT '{}'::jsonb,
  error_message TEXT,
  error_details JSONB DEFAULT '{}'::jsonb,
  
  -- Execution log
  execution_log JSONB DEFAULT '[]'::jsonb, -- Array of log entries
  
  -- Audit fields
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT chk_progress_range CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
  CONSTRAINT chk_step_index_non_negative CHECK (current_step_index >= 0),
  CONSTRAINT chk_total_steps_positive CHECK (total_steps >= 0),
  CONSTRAINT chk_current_step_valid CHECK (current_step_index <= total_steps)
);

-- =====================================================
-- SECTION 4: WORKFLOW STEP EXECUTIONS TABLE
-- =====================================================

-- Workflow Step Executions - Track individual step runs within executions
CREATE TABLE IF NOT EXISTS archon_workflow_step_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_execution_id UUID REFERENCES archon_workflow_executions(id) ON DELETE CASCADE,
  
  -- Step identification
  step_index INTEGER NOT NULL,
  step_name VARCHAR(255) NOT NULL,
  step_type workflow_step_type NOT NULL,
  
  -- Step configuration (snapshot from template)
  step_config JSONB NOT NULL DEFAULT '{}'::jsonb,
  
  -- Execution details
  status step_execution_status DEFAULT 'pending',
  attempt_number INTEGER DEFAULT 1,
  max_attempts INTEGER DEFAULT 1,
  
  -- Timing
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  
  -- Input/Output
  input_data JSONB DEFAULT '{}'::jsonb,
  output_data JSONB DEFAULT '{}'::jsonb,
  
  -- Error handling
  error_message TEXT,
  error_details JSONB DEFAULT '{}'::jsonb,
  
  -- Tool execution details (for action steps)
  tool_name VARCHAR(255),
  tool_parameters JSONB DEFAULT '{}'::jsonb,
  tool_result JSONB DEFAULT '{}'::jsonb,
  
  -- Sub-workflow details (for workflow_link steps)
  sub_workflow_execution_id UUID REFERENCES archon_workflow_executions(id),
  
  -- Audit fields
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT chk_step_index_non_negative CHECK (step_index >= 0),
  CONSTRAINT chk_attempt_positive CHECK (attempt_number > 0),
  CONSTRAINT chk_max_attempts_positive CHECK (max_attempts > 0),
  CONSTRAINT chk_attempt_within_max CHECK (attempt_number <= max_attempts)
);

-- =====================================================
-- SECTION 5: WORKFLOW TEMPLATE VERSIONS TABLE
-- =====================================================

-- Workflow Template Versions - Version control for workflow templates
CREATE TABLE IF NOT EXISTS archon_workflow_template_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_template_id UUID REFERENCES archon_workflow_templates(id) ON DELETE CASCADE,
  
  -- Version information
  version_number INTEGER NOT NULL,
  version_tag VARCHAR(50) NOT NULL, -- e.g., '1.0.0', '1.1.0-beta'
  
  -- Snapshot of template at this version
  template_snapshot JSONB NOT NULL, -- Complete template data
  
  -- Change information
  change_summary TEXT,
  change_type VARCHAR(50) DEFAULT 'update', -- 'create', 'update', 'major', 'minor', 'patch'
  breaking_changes BOOLEAN DEFAULT false,
  
  -- Audit fields
  created_by TEXT NOT NULL DEFAULT 'system',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT chk_version_number_positive CHECK (version_number > 0),
  UNIQUE(workflow_template_id, version_number),
  UNIQUE(workflow_template_id, version_tag)
);

-- =====================================================
-- SECTION 6: INDEXES FOR PERFORMANCE
-- =====================================================

-- Workflow Templates indexes
CREATE INDEX IF NOT EXISTS idx_archon_workflow_templates_name ON archon_workflow_templates(name);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_templates_status ON archon_workflow_templates(status);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_templates_category ON archon_workflow_templates(category);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_templates_created_by ON archon_workflow_templates(created_by);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_templates_tags ON archon_workflow_templates USING GIN(tags);

-- Workflow Executions indexes
CREATE INDEX IF NOT EXISTS idx_archon_workflow_executions_template_id ON archon_workflow_executions(workflow_template_id);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_executions_status ON archon_workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_executions_triggered_by ON archon_workflow_executions(triggered_by);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_executions_started_at ON archon_workflow_executions(started_at);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_executions_context ON archon_workflow_executions USING GIN(trigger_context);

-- Workflow Step Executions indexes
CREATE INDEX IF NOT EXISTS idx_archon_workflow_step_executions_execution_id ON archon_workflow_step_executions(workflow_execution_id);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_step_executions_step_index ON archon_workflow_step_executions(step_index);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_step_executions_status ON archon_workflow_step_executions(status);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_step_executions_tool_name ON archon_workflow_step_executions(tool_name);

-- Workflow Template Versions indexes
CREATE INDEX IF NOT EXISTS idx_archon_workflow_template_versions_template_id ON archon_workflow_template_versions(workflow_template_id);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_template_versions_version_number ON archon_workflow_template_versions(version_number);

-- =====================================================
-- SECTION 7: TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Update timestamp trigger function (reuse existing if available)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
CREATE TRIGGER update_archon_workflow_templates_updated_at 
    BEFORE UPDATE ON archon_workflow_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_workflow_executions_updated_at 
    BEFORE UPDATE ON archon_workflow_executions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_workflow_step_executions_updated_at 
    BEFORE UPDATE ON archon_workflow_step_executions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SECTION 8: ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on workflow tables
ALTER TABLE archon_workflow_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_workflow_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_workflow_step_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_workflow_template_versions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for public read access (following Archon patterns)
CREATE POLICY "Allow public read access to archon_workflow_templates"
  ON archon_workflow_templates
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public read access to archon_workflow_executions"
  ON archon_workflow_executions
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public read access to archon_workflow_step_executions"
  ON archon_workflow_step_executions
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public read access to archon_workflow_template_versions"
  ON archon_workflow_template_versions
  FOR SELECT
  TO public
  USING (true);

-- Allow service role full access
CREATE POLICY "Allow service role full access to workflow_templates"
  ON archon_workflow_templates
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow service role full access to workflow_executions"
  ON archon_workflow_executions
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow service role full access to workflow_step_executions"
  ON archon_workflow_step_executions
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow service role full access to workflow_template_versions"
  ON archon_workflow_template_versions
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- =====================================================
-- SECTION 9: COMMENTS AND DOCUMENTATION
-- =====================================================

-- Add table comments for documentation
COMMENT ON TABLE archon_workflow_templates IS 'Stores reusable workflow templates with steps, parameters, and configuration';
COMMENT ON TABLE archon_workflow_executions IS 'Tracks individual workflow execution instances with status and progress';
COMMENT ON TABLE archon_workflow_step_executions IS 'Records execution details for each step within a workflow run';
COMMENT ON TABLE archon_workflow_template_versions IS 'Maintains version history for workflow templates';

-- Add column comments for key fields
COMMENT ON COLUMN archon_workflow_templates.steps IS 'JSONB array of workflow step definitions with type, config, and parameters';
COMMENT ON COLUMN archon_workflow_templates.parameters IS 'JSONB schema defining required and optional input parameters';
COMMENT ON COLUMN archon_workflow_executions.trigger_context IS 'JSONB context that triggered the workflow (task ID, event data, etc.)';
COMMENT ON COLUMN archon_workflow_step_executions.step_config IS 'JSONB snapshot of step configuration from template at execution time';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Log successful migration
DO $$
BEGIN
    RAISE NOTICE 'Archon Workflow System migration completed successfully!';
    RAISE NOTICE 'Created tables: archon_workflow_templates, archon_workflow_executions, archon_workflow_step_executions, archon_workflow_template_versions';
    RAISE NOTICE 'Created enums: workflow_status, workflow_step_type, workflow_execution_status, step_execution_status';
    RAISE NOTICE 'Added indexes, triggers, and RLS policies';
END $$;
