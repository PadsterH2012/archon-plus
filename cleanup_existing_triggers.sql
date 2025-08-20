-- =====================================================
-- ARCHON TRIGGER CLEANUP SCRIPT
-- =====================================================
-- Run this script BEFORE running the main setup scripts
-- if you encounter trigger conflicts
-- =====================================================

-- Drop all existing Archon triggers
DO $$
BEGIN
    RAISE NOTICE 'Cleaning up existing Archon triggers...';
    
    -- Settings table triggers
    DROP TRIGGER IF EXISTS update_archon_settings_updated_at ON archon_settings;
    DROP TRIGGER IF EXISTS update_settings_updated_at ON settings;
    
    -- Projects table triggers
    DROP TRIGGER IF EXISTS update_archon_projects_updated_at ON archon_projects;
    DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
    
    -- Tasks table triggers
    DROP TRIGGER IF EXISTS update_archon_tasks_updated_at ON archon_tasks;
    DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
    
    -- Prompts table triggers
    DROP TRIGGER IF EXISTS update_archon_prompts_updated_at ON archon_prompts;
    DROP TRIGGER IF EXISTS update_prompts_updated_at ON prompts;
    
    -- Workflow table triggers
    DROP TRIGGER IF EXISTS update_archon_workflow_templates_updated_at ON archon_workflow_templates;
    DROP TRIGGER IF EXISTS update_archon_workflow_executions_updated_at ON archon_workflow_executions;
    DROP TRIGGER IF EXISTS update_archon_workflow_step_executions_updated_at ON archon_workflow_step_executions;
    
    RAISE NOTICE 'Trigger cleanup completed successfully!';
    
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error during trigger cleanup: %', SQLERRM;
    RAISE NOTICE 'This is normal if some triggers did not exist.';
END $$;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ TRIGGER CLEANUP COMPLETED';
    RAISE NOTICE 'You can now run your main setup script without trigger conflicts.';
END $$;
