-- =====================================================
-- ARCHON WORKFLOW SYSTEM ROLLBACK SCRIPT
-- =====================================================
-- This script safely removes the workflow orchestration system from Archon
-- 
-- ⚠️  WARNING: THIS WILL DELETE ALL WORKFLOW DATA! ⚠️
-- 
-- Usage:
--   1. Connect to your Supabase/PostgreSQL database
--   2. Run this script in the SQL editor to remove workflow system
--   3. This is the reverse of add_workflow_system.sql
-- 
-- Created: 2025-08-18
-- =====================================================

DO $$ 
BEGIN
    RAISE NOTICE 'Starting Archon Workflow System rollback...';
END $$;

-- =====================================================
-- SECTION 1: DROP RLS POLICIES
-- =====================================================

DO $$ 
BEGIN
    RAISE NOTICE 'Dropping Row Level Security policies...';
    
    -- Workflow templates policies
    DROP POLICY IF EXISTS "Allow public read access to archon_workflow_templates" ON archon_workflow_templates;
    DROP POLICY IF EXISTS "Allow service role full access to workflow_templates" ON archon_workflow_templates;
    
    -- Workflow executions policies
    DROP POLICY IF EXISTS "Allow public read access to archon_workflow_executions" ON archon_workflow_executions;
    DROP POLICY IF EXISTS "Allow service role full access to workflow_executions" ON archon_workflow_executions;
    
    -- Workflow step executions policies
    DROP POLICY IF EXISTS "Allow public read access to archon_workflow_step_executions" ON archon_workflow_step_executions;
    DROP POLICY IF EXISTS "Allow service role full access to workflow_step_executions" ON archon_workflow_step_executions;
    
    -- Workflow template versions policies
    DROP POLICY IF EXISTS "Allow public read access to archon_workflow_template_versions" ON archon_workflow_template_versions;
    DROP POLICY IF EXISTS "Allow service role full access to workflow_template_versions" ON archon_workflow_template_versions;
    
    RAISE NOTICE 'RLS policies dropped successfully.';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error dropping RLS policies: %', SQLERRM;
END $$;

-- =====================================================
-- SECTION 2: DROP TRIGGERS
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Dropping triggers...';
    
    -- Drop update triggers
    DROP TRIGGER IF EXISTS update_archon_workflow_templates_updated_at ON archon_workflow_templates;
    DROP TRIGGER IF EXISTS update_archon_workflow_executions_updated_at ON archon_workflow_executions;
    DROP TRIGGER IF EXISTS update_archon_workflow_step_executions_updated_at ON archon_workflow_step_executions;
    
    RAISE NOTICE 'Triggers dropped successfully.';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error dropping triggers: %', SQLERRM;
END $$;

-- =====================================================
-- SECTION 3: DROP INDEXES
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Dropping indexes...';
    
    -- Workflow Templates indexes
    DROP INDEX IF EXISTS idx_archon_workflow_templates_name;
    DROP INDEX IF EXISTS idx_archon_workflow_templates_status;
    DROP INDEX IF EXISTS idx_archon_workflow_templates_category;
    DROP INDEX IF EXISTS idx_archon_workflow_templates_created_by;
    DROP INDEX IF EXISTS idx_archon_workflow_templates_tags;
    
    -- Workflow Executions indexes
    DROP INDEX IF EXISTS idx_archon_workflow_executions_template_id;
    DROP INDEX IF EXISTS idx_archon_workflow_executions_status;
    DROP INDEX IF EXISTS idx_archon_workflow_executions_triggered_by;
    DROP INDEX IF EXISTS idx_archon_workflow_executions_started_at;
    DROP INDEX IF EXISTS idx_archon_workflow_executions_context;
    
    -- Workflow Step Executions indexes
    DROP INDEX IF EXISTS idx_archon_workflow_step_executions_execution_id;
    DROP INDEX IF EXISTS idx_archon_workflow_step_executions_step_index;
    DROP INDEX IF EXISTS idx_archon_workflow_step_executions_status;
    DROP INDEX IF EXISTS idx_archon_workflow_step_executions_tool_name;
    
    -- Workflow Template Versions indexes
    DROP INDEX IF EXISTS idx_archon_workflow_template_versions_template_id;
    DROP INDEX IF EXISTS idx_archon_workflow_template_versions_version_number;
    
    RAISE NOTICE 'Indexes dropped successfully.';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error dropping indexes: %', SQLERRM;
END $$;

-- =====================================================
-- SECTION 4: DROP TABLES
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Dropping workflow tables with CASCADE...';
    
    -- Drop in reverse dependency order to minimize cascade issues
    DROP TABLE IF EXISTS archon_workflow_template_versions CASCADE;
    DROP TABLE IF EXISTS archon_workflow_step_executions CASCADE;
    DROP TABLE IF EXISTS archon_workflow_executions CASCADE;
    DROP TABLE IF EXISTS archon_workflow_templates CASCADE;
    
    RAISE NOTICE 'Workflow tables dropped successfully.';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error dropping tables: %', SQLERRM;
END $$;

-- =====================================================
-- SECTION 5: DROP ENUMS AND TYPES
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE 'Dropping workflow enums and types...';
    
    -- Drop workflow-specific enums
    DROP TYPE IF EXISTS step_execution_status CASCADE;
    DROP TYPE IF EXISTS workflow_execution_status CASCADE;
    DROP TYPE IF EXISTS workflow_step_type CASCADE;
    DROP TYPE IF EXISTS workflow_status CASCADE;
    
    RAISE NOTICE 'Workflow enums dropped successfully.';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error dropping enums: %', SQLERRM;
END $$;

-- =====================================================
-- SECTION 6: CLEANUP FUNCTIONS (OPTIONAL)
-- =====================================================

-- Note: We don't drop update_updated_at_column() function as it's used by other tables
-- If you need to drop it, uncomment the following:
-- DO $$
-- BEGIN
--     RAISE NOTICE 'Dropping workflow-specific functions...';
--     
--     -- Only drop if no other tables are using this function
--     -- DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
--     
--     RAISE NOTICE 'Functions dropped successfully.';
--     
-- EXCEPTION WHEN OTHERS THEN
--     RAISE NOTICE 'Error dropping functions: %', SQLERRM;
-- END $$;

-- =====================================================
-- ROLLBACK COMPLETE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Archon Workflow System rollback completed successfully!';
    RAISE NOTICE 'Removed tables: archon_workflow_templates, archon_workflow_executions, archon_workflow_step_executions, archon_workflow_template_versions';
    RAISE NOTICE 'Removed enums: workflow_status, workflow_step_type, workflow_execution_status, step_execution_status';
    RAISE NOTICE 'Removed indexes, triggers, and RLS policies';
    RAISE NOTICE 'All workflow data has been permanently deleted.';
END $$;
