-- =====================================================
-- WORKFLOW SCHEMA VALIDATION SCRIPT
-- =====================================================
-- This script validates that the workflow migration was applied correctly
-- Run this after applying add_workflow_system.sql to verify everything is working
-- =====================================================

DO $$
DECLARE
    table_count INTEGER;
    enum_count INTEGER;
    index_count INTEGER;
    policy_count INTEGER;
    trigger_count INTEGER;
BEGIN
    RAISE NOTICE '🚀 Starting Workflow Schema Validation';
    RAISE NOTICE '================================================';
    
    -- =====================================================
    -- SECTION 1: VALIDATE TABLES
    -- =====================================================
    
    RAISE NOTICE '📋 Checking Tables...';
    
    -- Check archon_workflow_templates
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_name = 'archon_workflow_templates';
    
    IF table_count = 1 THEN
        RAISE NOTICE '✅ archon_workflow_templates table exists';
    ELSE
        RAISE NOTICE '❌ archon_workflow_templates table missing';
    END IF;
    
    -- Check archon_workflow_executions
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_name = 'archon_workflow_executions';
    
    IF table_count = 1 THEN
        RAISE NOTICE '✅ archon_workflow_executions table exists';
    ELSE
        RAISE NOTICE '❌ archon_workflow_executions table missing';
    END IF;
    
    -- Check archon_workflow_step_executions
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_name = 'archon_workflow_step_executions';
    
    IF table_count = 1 THEN
        RAISE NOTICE '✅ archon_workflow_step_executions table exists';
    ELSE
        RAISE NOTICE '❌ archon_workflow_step_executions table missing';
    END IF;
    
    -- Check archon_workflow_template_versions
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_name = 'archon_workflow_template_versions';
    
    IF table_count = 1 THEN
        RAISE NOTICE '✅ archon_workflow_template_versions table exists';
    ELSE
        RAISE NOTICE '❌ archon_workflow_template_versions table missing';
    END IF;
    
    -- =====================================================
    -- SECTION 2: VALIDATE ENUMS
    -- =====================================================
    
    RAISE NOTICE '🏷️  Checking Enums...';
    
    -- Check workflow_status enum
    SELECT COUNT(*) INTO enum_count 
    FROM pg_type 
    WHERE typname = 'workflow_status';
    
    IF enum_count = 1 THEN
        RAISE NOTICE '✅ workflow_status enum exists';
    ELSE
        RAISE NOTICE '❌ workflow_status enum missing';
    END IF;
    
    -- Check workflow_step_type enum
    SELECT COUNT(*) INTO enum_count 
    FROM pg_type 
    WHERE typname = 'workflow_step_type';
    
    IF enum_count = 1 THEN
        RAISE NOTICE '✅ workflow_step_type enum exists';
    ELSE
        RAISE NOTICE '❌ workflow_step_type enum missing';
    END IF;
    
    -- Check workflow_execution_status enum
    SELECT COUNT(*) INTO enum_count 
    FROM pg_type 
    WHERE typname = 'workflow_execution_status';
    
    IF enum_count = 1 THEN
        RAISE NOTICE '✅ workflow_execution_status enum exists';
    ELSE
        RAISE NOTICE '❌ workflow_execution_status enum missing';
    END IF;
    
    -- Check step_execution_status enum
    SELECT COUNT(*) INTO enum_count 
    FROM pg_type 
    WHERE typname = 'step_execution_status';
    
    IF enum_count = 1 THEN
        RAISE NOTICE '✅ step_execution_status enum exists';
    ELSE
        RAISE NOTICE '❌ step_execution_status enum missing';
    END IF;
    
    -- =====================================================
    -- SECTION 3: VALIDATE INDEXES
    -- =====================================================
    
    RAISE NOTICE '📊 Checking Indexes...';
    
    -- Count workflow-related indexes
    SELECT COUNT(*) INTO index_count 
    FROM pg_indexes 
    WHERE indexname LIKE 'idx_archon_workflow%';
    
    IF index_count >= 10 THEN
        RAISE NOTICE '✅ Workflow indexes created (% found)', index_count;
    ELSE
        RAISE NOTICE '❌ Missing workflow indexes (only % found, expected 10+)', index_count;
    END IF;
    
    -- =====================================================
    -- SECTION 4: VALIDATE RLS POLICIES
    -- =====================================================
    
    RAISE NOTICE '🔒 Checking RLS Policies...';
    
    -- Count workflow-related policies
    SELECT COUNT(*) INTO policy_count 
    FROM pg_policies 
    WHERE tablename LIKE 'archon_workflow%';
    
    IF policy_count >= 8 THEN
        RAISE NOTICE '✅ RLS policies created (% found)', policy_count;
    ELSE
        RAISE NOTICE '❌ Missing RLS policies (only % found, expected 8+)', policy_count;
    END IF;
    
    -- =====================================================
    -- SECTION 5: VALIDATE TRIGGERS
    -- =====================================================
    
    RAISE NOTICE '⚡ Checking Triggers...';
    
    -- Count workflow-related triggers
    SELECT COUNT(*) INTO trigger_count 
    FROM information_schema.triggers 
    WHERE event_object_table LIKE 'archon_workflow%';
    
    IF trigger_count >= 3 THEN
        RAISE NOTICE '✅ Triggers created (% found)', trigger_count;
    ELSE
        RAISE NOTICE '❌ Missing triggers (only % found, expected 3+)', trigger_count;
    END IF;
    
    -- =====================================================
    -- SECTION 6: TEST BASIC OPERATIONS
    -- =====================================================
    
    RAISE NOTICE '🧪 Testing Basic Operations...';
    
    BEGIN
        -- Test workflow template insertion
        INSERT INTO archon_workflow_templates (name, title, description, steps)
        VALUES ('validation_test', 'Validation Test', 'Test workflow for validation', '[{"name": "test", "type": "action"}]'::jsonb);
        
        RAISE NOTICE '✅ Workflow template insertion works';
        
        -- Clean up test data
        DELETE FROM archon_workflow_templates WHERE name = 'validation_test';
        
        RAISE NOTICE '✅ Workflow template deletion works';
        
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE '❌ Basic operations test failed: %', SQLERRM;
    END;
    
    -- =====================================================
    -- SECTION 7: VALIDATION SUMMARY
    -- =====================================================
    
    RAISE NOTICE '================================================';
    RAISE NOTICE '🎉 Workflow Schema Validation Complete!';
    RAISE NOTICE '';
    RAISE NOTICE 'Summary:';
    RAISE NOTICE '- Tables: 4 workflow tables checked';
    RAISE NOTICE '- Enums: 4 workflow enums checked';
    RAISE NOTICE '- Indexes: % workflow indexes found', index_count;
    RAISE NOTICE '- RLS Policies: % workflow policies found', policy_count;
    RAISE NOTICE '- Triggers: % workflow triggers found', trigger_count;
    RAISE NOTICE '';
    RAISE NOTICE 'If all items show ✅, the migration was successful!';
    RAISE NOTICE 'If any items show ❌, please check the migration script.';
    
END $$;
