-- =====================================================
-- ARCHON TEMPLATE INJECTION SYSTEM - MINIMAL MIGRATION
-- =====================================================
-- This script adds only the missing pieces for Template Injection System
-- by leveraging existing tables that already match our requirements.
-- 
-- EXISTING TABLES WE'LL USE:
-- - archon_template_components (perfect match!)
-- - archon_template_assignments (for hierarchy assignments)
-- - archon_template_definitions (for workflow templates)
-- 
-- WHAT THIS SCRIPT ADDS:
-- - template_injection_level enum (for hierarchy levels)
-- - template_metadata column to archon_tasks
-- - Validation functions for template injection
-- - Indexes for performance
-- 
-- Created: 2025-08-20
-- Version: 1.0.0 (Minimal)
-- =====================================================

-- =====================================================
-- SECTION 1: ADD MISSING ENUM TYPES
-- =====================================================

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

-- =====================================================
-- SECTION 2: EXTEND EXISTING TABLES
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

-- Add injection_level column to archon_template_assignments if needed
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'archon_template_assignments' 
    AND column_name = 'injection_level'
  ) THEN
    ALTER TABLE archon_template_assignments 
    ADD COLUMN injection_level template_injection_level DEFAULT 'task';
    
    RAISE NOTICE 'Added injection_level column to archon_template_assignments table';
  ELSE
    RAISE NOTICE 'injection_level column already exists in archon_template_assignments table';
  END IF;
END $$;

-- =====================================================
-- SECTION 3: VALIDATION FUNCTIONS
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

-- =====================================================
-- SECTION 4: ADD VALIDATION CONSTRAINTS
-- =====================================================

-- Add validation constraint to archon_template_components for name format
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE table_name = 'archon_template_components' 
    AND constraint_name = 'check_component_name_format'
  ) THEN
    ALTER TABLE archon_template_components 
    ADD CONSTRAINT check_component_name_format 
    CHECK (validate_component_name(name));
    
    RAISE NOTICE 'Added component name validation constraint';
  ELSE
    RAISE NOTICE 'Component name validation constraint already exists';
  END IF;
END $$;

-- =====================================================
-- SECTION 5: PERFORMANCE INDEXES
-- =====================================================

-- Template Components indexes (add missing ones)
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
CREATE INDEX IF NOT EXISTS idx_template_assignments_injection_level ON archon_template_assignments(injection_level);

-- Tasks template metadata index
CREATE INDEX IF NOT EXISTS idx_tasks_template_metadata ON archon_tasks USING GIN(template_metadata);

-- Template Definitions indexes (for workflow templates)
CREATE INDEX IF NOT EXISTS idx_template_definitions_name ON archon_template_definitions(name);
CREATE INDEX IF NOT EXISTS idx_template_definitions_type ON archon_template_definitions(template_type);
CREATE INDEX IF NOT EXISTS idx_template_definitions_category ON archon_template_definitions(category);

-- =====================================================
-- SECTION 6: COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'TEMPLATE INJECTION MINIMAL MIGRATION COMPLETED';
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'Leveraged existing tables:';
  RAISE NOTICE '  - archon_template_components (template building blocks)';
  RAISE NOTICE '  - archon_template_assignments (hierarchy assignments)';
  RAISE NOTICE '  - archon_template_definitions (workflow templates)';
  RAISE NOTICE '';
  RAISE NOTICE 'Added:';
  RAISE NOTICE '  - template_injection_level enum';
  RAISE NOTICE '  - archon_tasks.template_metadata column';
  RAISE NOTICE '  - injection_level column to assignments';
  RAISE NOTICE '  - Validation functions and constraints';
  RAISE NOTICE '  - Performance indexes';
  RAISE NOTICE '';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '  1. Run migration/seed_template_injection_data.sql';
  RAISE NOTICE '  2. Update Pydantic models to match existing schema';
  RAISE NOTICE '  3. Implement TemplateInjectionService';
  RAISE NOTICE '  4. Test template injection system';
  RAISE NOTICE '=================================================';
END $$;
