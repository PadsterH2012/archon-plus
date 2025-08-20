-- =====================================================
-- ARCHON COMPONENT HIERARCHY ROLLBACK
-- =====================================================
-- This script removes the component hierarchy system from Archon
-- 
-- WARNING: This will permanently delete all component data!
-- Make sure to backup your database before running this script.
-- 
-- Run this script in your Supabase SQL Editor to rollback
-- the component hierarchy migration
-- =====================================================

-- =====================================================
-- SECTION 1: SAFETY CHECKS
-- =====================================================

DO $$
BEGIN
  -- Check if component tables exist
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_components') THEN
    RAISE NOTICE 'Component hierarchy tables not found - nothing to rollback';
    RETURN;
  END IF;
  
  -- Warn about data loss
  RAISE NOTICE '⚠️  WARNING: This will permanently delete all component hierarchy data!';
  RAISE NOTICE '📊 Component count: %', (SELECT COUNT(*) FROM archon_components);
  RAISE NOTICE '🔗 Dependency count: %', (SELECT COUNT(*) FROM archon_component_dependencies);
  RAISE NOTICE '📋 Template count: %', (SELECT COUNT(*) FROM archon_template_definitions);
END $$;

-- =====================================================
-- SECTION 2: REMOVE TRIGGERS AND FUNCTIONS
-- =====================================================

-- Drop circular dependency prevention trigger
DROP TRIGGER IF EXISTS trigger_check_component_circular_dependency ON archon_component_dependencies;

-- Drop circular dependency check function
DROP FUNCTION IF EXISTS check_component_circular_dependency();

-- =====================================================
-- SECTION 3: REMOVE FOREIGN KEY CONSTRAINTS
-- =====================================================

-- Remove component_id from tasks table
ALTER TABLE archon_tasks DROP COLUMN IF EXISTS component_id;

-- =====================================================
-- SECTION 4: DROP INDEXES
-- =====================================================

-- Component indexes
DROP INDEX IF EXISTS idx_components_project_id;
DROP INDEX IF EXISTS idx_components_status;
DROP INDEX IF EXISTS idx_components_type;
DROP INDEX IF EXISTS idx_components_parent;
DROP INDEX IF EXISTS idx_components_template;

-- Component dependency indexes
DROP INDEX IF EXISTS idx_component_deps_component_id;
DROP INDEX IF EXISTS idx_component_deps_depends_on;

-- Template indexes
DROP INDEX IF EXISTS idx_templates_type;
DROP INDEX IF EXISTS idx_templates_component_type;
DROP INDEX IF EXISTS idx_templates_parent;
DROP INDEX IF EXISTS idx_templates_category;
DROP INDEX IF EXISTS idx_templates_tags;

-- Task component index
DROP INDEX IF EXISTS idx_tasks_component_id;

-- =====================================================
-- SECTION 5: DROP TABLES
-- =====================================================

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS archon_component_dependencies CASCADE;
DROP TABLE IF EXISTS archon_components CASCADE;
DROP TABLE IF EXISTS archon_template_definitions CASCADE;

-- =====================================================
-- SECTION 6: DROP ENUMS
-- =====================================================

-- Drop enum types
DROP TYPE IF EXISTS component_type_enum CASCADE;
DROP TYPE IF EXISTS component_status_enum CASCADE;
DROP TYPE IF EXISTS template_type_enum CASCADE;

-- =====================================================
-- ROLLBACK COMPLETE
-- =====================================================

-- Verify rollback success
DO $$
BEGIN
  -- Check that all tables were removed
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_components') THEN
    RAISE EXCEPTION 'Rollback failed: archon_components table still exists';
  END IF;
  
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_component_dependencies') THEN
    RAISE EXCEPTION 'Rollback failed: archon_component_dependencies table still exists';
  END IF;
  
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_template_definitions') THEN
    RAISE EXCEPTION 'Rollback failed: archon_template_definitions table still exists';
  END IF;
  
  -- Check that enums were removed
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'component_type_enum') THEN
    RAISE EXCEPTION 'Rollback failed: component_type_enum still exists';
  END IF;
  
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'component_status_enum') THEN
    RAISE EXCEPTION 'Rollback failed: component_status_enum still exists';
  END IF;
  
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'template_type_enum') THEN
    RAISE EXCEPTION 'Rollback failed: template_type_enum still exists';
  END IF;
  
  RAISE NOTICE '✅ Component hierarchy rollback completed successfully!';
  RAISE NOTICE '🗑️  All component tables and data removed';
  RAISE NOTICE '🔄 Database restored to pre-component state';
END $$;
