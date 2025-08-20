-- =====================================================
-- ARCHON TEMPLATE INJECTION SYSTEM - DATABASE SCHEMA
-- =====================================================
-- This script creates the database schema for the Template Injection System
-- with zero breaking changes to existing Archon tables.
-- 
-- The system injects standardized operational workflows directly into
-- agent task instructions while preserving the original user intent.
-- 
-- Created: 2025-08-20
-- Version: 1.0.0
-- =====================================================

-- =====================================================
-- SECTION 1: ENUM TYPES
-- =====================================================

-- Template injection types for different scenarios
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'template_injection_type') THEN
    CREATE TYPE template_injection_type AS ENUM (
      'workflow',    -- Complete workflow templates (e.g., workflow::default)
      'sequence',    -- Ordered sequence of related actions
      'action'       -- Single atomic operation
    );
    RAISE NOTICE 'Created template_injection_type enum';
  ELSE
    RAISE NOTICE 'template_injection_type enum already exists';
  END IF;
END $$;

-- Template injection levels in the hierarchy
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'template_injection_level') THEN
    CREATE TYPE template_injection_level AS ENUM (
      'project',     -- Applied to all tasks in project
      'milestone',   -- Applied to milestone completion tasks
      'phase',       -- Applied to development phase tasks
      'task',        -- Applied to individual tasks
      'subtask'      -- Applied to granular operations
    );
    RAISE NOTICE 'Created template_injection_level enum';
  ELSE
    RAISE NOTICE 'template_injection_level enum already exists';
  END IF;
END $$;

-- Template component types for building blocks
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'template_component_type') THEN
    CREATE TYPE template_component_type AS ENUM (
      'action',      -- Single atomic instruction (e.g., action::git_commit)
      'group',       -- Related set of instructions (e.g., group::testing_strategy)
      'sequence'     -- Ordered workflow segment (e.g., sequence::deployment)
    );
    RAISE NOTICE 'Created template_component_type enum';
  ELSE
    RAISE NOTICE 'template_component_type enum already exists';
  END IF;
END $$;

-- Template hierarchy types for polymorphic references
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'template_hierarchy_type') THEN
    CREATE TYPE template_hierarchy_type AS ENUM (
      'project',
      'milestone',
      'phase',
      'task',
      'subtask'
    );
    RAISE NOTICE 'Created template_hierarchy_type enum';
  ELSE
    RAISE NOTICE 'template_hierarchy_type enum already exists';
  END IF;
END $$;

-- =====================================================
-- SECTION 2: CORE TEMPLATE TABLES
-- =====================================================

-- Template Injection Templates - Template definitions with placeholders
CREATE TABLE IF NOT EXISTS archon_template_injection_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) UNIQUE NOT NULL, -- e.g., "workflow::default", "workflow::hotfix"
  description TEXT DEFAULT '',
  template_type template_injection_type NOT NULL DEFAULT 'workflow',
  injection_level template_injection_level NOT NULL DEFAULT 'task',
  
  -- Template content with {{placeholder}} variables
  template_content TEXT NOT NULL, -- Template with {{group::name}} placeholders
  user_task_position INTEGER DEFAULT 6, -- Where {{USER_TASK}} appears in sequence
  
  -- Metadata and configuration
  estimated_duration INTEGER DEFAULT 30, -- Total estimated duration in minutes
  required_tools JSONB DEFAULT '[]'::jsonb, -- MCP tools needed for this template
  applicable_phases JSONB DEFAULT '["development", "testing", "deployment"]'::jsonb,
  
  -- Status and versioning
  is_active BOOLEAN DEFAULT true,
  version VARCHAR(50) DEFAULT '1.0.0',
  author VARCHAR(255) DEFAULT 'archon-system',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Template Components - Expandable instruction components
CREATE TABLE IF NOT EXISTS archon_template_components (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) UNIQUE NOT NULL, -- e.g., "group::understand_homelab_env"
  description TEXT DEFAULT '',
  component_type template_component_type NOT NULL DEFAULT 'group',
  
  -- Component instruction content
  instruction_text TEXT NOT NULL, -- Full expanded instruction text
  
  -- Requirements and metadata
  required_tools JSONB DEFAULT '[]'::jsonb, -- MCP tools needed (e.g., ["homelab-vault", "view"])
  estimated_duration INTEGER DEFAULT 5, -- Estimated duration in minutes
  input_requirements JSONB DEFAULT '{}'::jsonb, -- What context/data this component needs
  output_expectations JSONB DEFAULT '{}'::jsonb, -- What this component should produce
  validation_criteria JSONB DEFAULT '[]'::jsonb, -- How to verify successful completion
  
  -- Categorization and metadata
  category VARCHAR(100) DEFAULT 'general', -- e.g., "documentation", "testing", "deployment"
  priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
  tags JSONB DEFAULT '[]'::jsonb, -- Flexible tagging for search and organization
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Template Assignments - Hierarchy-level template assignments
CREATE TABLE IF NOT EXISTS archon_template_assignments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Polymorphic reference to hierarchy level
  hierarchy_type template_hierarchy_type NOT NULL,
  hierarchy_id UUID NOT NULL, -- References project, milestone, phase, task, or subtask
  
  -- Template assignment
  template_id UUID REFERENCES archon_template_injection_templates(id) ON DELETE CASCADE,
  
  -- Assignment configuration
  assignment_context JSONB DEFAULT '{}'::jsonb, -- Conditions and context for assignment
  priority INTEGER DEFAULT 0, -- Priority for conflict resolution (higher = more priority)
  conditional_logic JSONB DEFAULT '{}'::jsonb, -- Conditions for when this assignment applies
  
  -- Status and metadata
  is_active BOOLEAN DEFAULT true,
  assigned_at TIMESTAMPTZ DEFAULT NOW(),
  assigned_by VARCHAR(255) DEFAULT 'system', -- User or system that made the assignment
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Ensure unique assignments per hierarchy level (one template per level)
  UNIQUE(hierarchy_type, hierarchy_id, template_id)
);

-- =====================================================
-- SECTION 3: EXTEND EXISTING TABLES
-- =====================================================

-- Add template metadata to existing archon_tasks table (zero breaking changes)
DO $$
BEGIN
  -- Check if template_metadata column exists, add if not
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'archon_tasks' 
    AND column_name = 'template_metadata'
  ) THEN
    ALTER TABLE archon_tasks 
    ADD COLUMN template_metadata JSONB DEFAULT '{}'::jsonb;
    
    RAISE NOTICE 'Added template_metadata column to archon_tasks table';
  ELSE
    RAISE NOTICE 'template_metadata column already exists in archon_tasks table';
  END IF;
END $$;

-- =====================================================
-- SECTION 4: INDEXES FOR PERFORMANCE
-- =====================================================

-- Workflow Templates indexes
CREATE INDEX IF NOT EXISTS idx_workflow_templates_name ON archon_workflow_templates(name);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_type ON archon_workflow_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_injection_level ON archon_workflow_templates(injection_level);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_active ON archon_workflow_templates(is_active);
CREATE INDEX IF NOT EXISTS idx_workflow_templates_phases ON archon_workflow_templates USING GIN(applicable_phases);

-- Template Components indexes
CREATE INDEX IF NOT EXISTS idx_template_components_name ON archon_template_components(name);
CREATE INDEX IF NOT EXISTS idx_template_components_type ON archon_template_components(component_type);
CREATE INDEX IF NOT EXISTS idx_template_components_category ON archon_template_components(category);
CREATE INDEX IF NOT EXISTS idx_template_components_active ON archon_template_components(is_active);
CREATE INDEX IF NOT EXISTS idx_template_components_tags ON archon_template_components USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_template_components_tools ON archon_template_components USING GIN(required_tools);

-- Template Assignments indexes
CREATE INDEX IF NOT EXISTS idx_template_assignments_hierarchy ON archon_template_assignments(hierarchy_type, hierarchy_id);
CREATE INDEX IF NOT EXISTS idx_template_assignments_template ON archon_template_assignments(template_id);
CREATE INDEX IF NOT EXISTS idx_template_assignments_active ON archon_template_assignments(is_active);
CREATE INDEX IF NOT EXISTS idx_template_assignments_priority ON archon_template_assignments(priority DESC);

-- Tasks template metadata index
CREATE INDEX IF NOT EXISTS idx_tasks_template_metadata ON archon_tasks USING GIN(template_metadata);

-- =====================================================
-- SECTION 5: TRIGGERS FOR UPDATED_AT
-- =====================================================

-- Create or replace the update timestamp function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
CREATE TRIGGER update_workflow_templates_updated_at
  BEFORE UPDATE ON archon_workflow_templates
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_template_components_updated_at
  BEFORE UPDATE ON archon_template_components
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_template_assignments_updated_at
  BEFORE UPDATE ON archon_template_assignments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SECTION 6: VALIDATION FUNCTIONS
-- =====================================================

-- Function to validate template content has required placeholders
CREATE OR REPLACE FUNCTION validate_template_content(template_content TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  -- Check if template contains {{USER_TASK}} placeholder
  IF template_content !~ '\{\{USER_TASK\}\}' THEN
    RAISE EXCEPTION 'Template content must contain {{USER_TASK}} placeholder';
  END IF;

  -- Check for valid placeholder format
  IF template_content ~ '\{\{[^}]*[^a-zA-Z0-9_:][^}]*\}\}' THEN
    RAISE EXCEPTION 'Template placeholders must only contain alphanumeric characters, underscores, and colons';
  END IF;

  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function to validate component name format
CREATE OR REPLACE FUNCTION validate_component_name(component_name VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
  -- Check component name format: type::name
  IF component_name !~ '^(action|group|sequence)::[a-zA-Z0-9_]+$' THEN
    RAISE EXCEPTION 'Component name must follow format: type::name (e.g., group::understand_homelab_env)';
  END IF;

  RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Add validation constraints
ALTER TABLE archon_workflow_templates
ADD CONSTRAINT check_template_content
CHECK (validate_template_content(template_content));

ALTER TABLE archon_template_components
ADD CONSTRAINT check_component_name
CHECK (validate_component_name(name));

-- =====================================================
-- SECTION 7: COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'ARCHON TEMPLATE INJECTION SCHEMA CREATED SUCCESSFULLY';
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'Tables created:';
  RAISE NOTICE '  - archon_workflow_templates (template definitions)';
  RAISE NOTICE '  - archon_template_components (expandable components)';
  RAISE NOTICE '  - archon_template_assignments (hierarchy assignments)';
  RAISE NOTICE '';
  RAISE NOTICE 'Existing table extended:';
  RAISE NOTICE '  - archon_tasks.template_metadata (JSONB column added)';
  RAISE NOTICE '';
  RAISE NOTICE 'Performance optimizations:';
  RAISE NOTICE '  - Strategic indexes created for fast queries';
  RAISE NOTICE '  - GIN indexes for JSONB fields';
  RAISE NOTICE '  - Validation functions and constraints';
  RAISE NOTICE '';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '  1. Run migration/seed_default_templates.sql';
  RAISE NOTICE '  2. Test template injection system';
  RAISE NOTICE '  3. Enable feature flags for gradual rollout';
  RAISE NOTICE '=================================================';
END $$;
