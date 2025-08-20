-- =====================================================
-- ARCHON DATABASE FACTORY RESET
-- =====================================================
-- This script completely drops all Archon tables, functions,
-- triggers, types, and policies for a clean slate
-- 
-- ⚠️  WARNING: THIS WILL PERMANENTLY DELETE ALL DATA!
-- Only use this on development databases!
-- 
-- Usage:
-- 1. Run this script to completely clean the database
-- 2. Run migration/complete_setup.sql to recreate everything
-- 3. Run migration/add_component_hierarchy.sql for components
-- =====================================================

-- =====================================================
-- SECTION 1: SAFETY WARNING
-- =====================================================

DO $$
BEGIN
  RAISE NOTICE '⚠️  WARNING: FACTORY RESET IN PROGRESS';
  RAISE NOTICE '🗑️  This will permanently delete ALL Archon data!';
  RAISE NOTICE '📊 Starting database factory reset...';
  RAISE NOTICE '';
END $$;

-- =====================================================
-- SECTION 2: DROP COMPONENT HIERARCHY (if exists)
-- =====================================================

-- Drop component tables first (this will automatically drop triggers)
DROP TABLE IF EXISTS archon_component_dependencies CASCADE;
DROP TABLE IF EXISTS archon_components CASCADE;
DROP TABLE IF EXISTS archon_template_definitions CASCADE;

-- Drop component functions
DROP FUNCTION IF EXISTS check_component_circular_dependency() CASCADE;

-- Drop component enums
DROP TYPE IF EXISTS component_type_enum CASCADE;
DROP TYPE IF EXISTS component_status_enum CASCADE;
DROP TYPE IF EXISTS template_type_enum CASCADE;

-- =====================================================
-- SECTION 3: DROP WORKFLOW SYSTEM (if exists)
-- =====================================================

-- Drop workflow tables
DROP TABLE IF EXISTS archon_workflow_template_versions CASCADE;
DROP TABLE IF EXISTS archon_workflow_step_executions CASCADE;
DROP TABLE IF EXISTS archon_workflow_executions CASCADE;
DROP TABLE IF EXISTS archon_workflow_templates CASCADE;

-- Drop workflow enums
DROP TYPE IF EXISTS workflow_status CASCADE;
DROP TYPE IF EXISTS workflow_step_type CASCADE;
DROP TYPE IF EXISTS workflow_execution_status CASCADE;
DROP TYPE IF EXISTS step_execution_status CASCADE;

-- =====================================================
-- SECTION 4: DROP MAIN ARCHON TABLES
-- =====================================================

-- Drop main project/task tables
DROP TABLE IF EXISTS archon_prompts CASCADE;
DROP TABLE IF EXISTS archon_document_versions CASCADE;
DROP TABLE IF EXISTS archon_project_sources CASCADE;
DROP TABLE IF EXISTS archon_tasks CASCADE;
DROP TABLE IF EXISTS archon_projects CASCADE;

-- Drop task enum
DROP TYPE IF EXISTS task_status CASCADE;

-- =====================================================
-- SECTION 5: DROP RAG SYSTEM TABLES
-- =====================================================

-- Drop RAG tables
DROP TABLE IF EXISTS archon_code_examples CASCADE;
DROP TABLE IF EXISTS archon_crawled_pages CASCADE;
DROP TABLE IF EXISTS archon_sources CASCADE;

-- =====================================================
-- SECTION 6: DROP SETTINGS AND CORE TABLES
-- =====================================================

-- Drop settings table
DROP TABLE IF EXISTS archon_settings CASCADE;

-- Drop core functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- =====================================================
-- SECTION 7: DROP EXTENSIONS (optional)
-- =====================================================

-- Note: We don't drop extensions as they might be used by other systems
-- If you want to drop them too, uncomment these lines:
-- DROP EXTENSION IF EXISTS vector CASCADE;
-- DROP EXTENSION IF EXISTS pgcrypto CASCADE;

-- =====================================================
-- SECTION 8: VERIFICATION
-- =====================================================

DO $$
DECLARE
  table_count INTEGER;
  type_count INTEGER;
  function_count INTEGER;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Verifying factory reset...';
  
  -- Count remaining Archon tables
  SELECT COUNT(*) INTO table_count
  FROM information_schema.tables 
  WHERE table_name LIKE 'archon_%';
  
  -- Count remaining Archon types
  SELECT COUNT(*) INTO type_count
  FROM pg_type 
  WHERE typname LIKE '%_enum' OR typname LIKE 'workflow_%' OR typname LIKE 'component_%';
  
  -- Count remaining Archon functions
  SELECT COUNT(*) INTO function_count
  FROM pg_proc 
  WHERE proname LIKE '%archon%' OR proname LIKE '%component%' OR proname LIKE '%workflow%';
  
  IF table_count = 0 THEN
    RAISE NOTICE '✅ All Archon tables removed';
  ELSE
    RAISE NOTICE '⚠️  % Archon tables still exist', table_count;
  END IF;
  
  IF type_count = 0 THEN
    RAISE NOTICE '✅ All Archon types removed';
  ELSE
    RAISE NOTICE '⚠️  % Archon types still exist', type_count;
  END IF;
  
  IF function_count <= 1 THEN -- update_updated_at_column might remain
    RAISE NOTICE '✅ All Archon functions removed';
  ELSE
    RAISE NOTICE '⚠️  % Archon functions still exist', function_count;
  END IF;
  
  RAISE NOTICE '';
  RAISE NOTICE '🎉 FACTORY RESET COMPLETE!';
  RAISE NOTICE '';
  RAISE NOTICE '📋 Next Steps:';
  RAISE NOTICE '   1. Run migration/complete_setup.sql';
  RAISE NOTICE '   2. Run migration/add_component_hierarchy.sql (optional)';
  RAISE NOTICE '   3. Run migration/add_workflow_system.sql (optional)';
  RAISE NOTICE '';
END $$;

-- =====================================================
-- FACTORY RESET COMPLETE
-- =====================================================
