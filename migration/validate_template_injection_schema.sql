-- =====================================================
-- ARCHON TEMPLATE INJECTION SCHEMA VALIDATION
-- =====================================================
-- This script validates that the template injection schema
-- was created correctly and all components are working.
-- 
-- Run this after migration/add_template_injection_schema.sql
-- and migration/seed_default_templates.sql
-- 
-- Created: 2025-08-20
-- Version: 1.0.0
-- =====================================================

-- =====================================================
-- SECTION 1: VALIDATE TABLES EXIST
-- =====================================================

DO $$
DECLARE
  table_count INTEGER;
BEGIN
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'VALIDATING TEMPLATE INJECTION SCHEMA';
  RAISE NOTICE '=================================================';
  
  -- Check archon_workflow_templates table
  SELECT COUNT(*) INTO table_count 
  FROM information_schema.tables 
  WHERE table_name = 'archon_workflow_templates';
  
  IF table_count = 0 THEN
    RAISE EXCEPTION 'Table archon_workflow_templates does not exist';
  END IF;
  RAISE NOTICE '✓ archon_workflow_templates table exists';
  
  -- Check archon_template_components table
  SELECT COUNT(*) INTO table_count 
  FROM information_schema.tables 
  WHERE table_name = 'archon_template_components';
  
  IF table_count = 0 THEN
    RAISE EXCEPTION 'Table archon_template_components does not exist';
  END IF;
  RAISE NOTICE '✓ archon_template_components table exists';
  
  -- Check archon_template_assignments table
  SELECT COUNT(*) INTO table_count 
  FROM information_schema.tables 
  WHERE table_name = 'archon_template_assignments';
  
  IF table_count = 0 THEN
    RAISE EXCEPTION 'Table archon_template_assignments does not exist';
  END IF;
  RAISE NOTICE '✓ archon_template_assignments table exists';
  
  -- Check template_metadata column in archon_tasks
  SELECT COUNT(*) INTO table_count 
  FROM information_schema.columns 
  WHERE table_name = 'archon_tasks' AND column_name = 'template_metadata';
  
  IF table_count = 0 THEN
    RAISE EXCEPTION 'Column template_metadata does not exist in archon_tasks';
  END IF;
  RAISE NOTICE '✓ archon_tasks.template_metadata column exists';
  
END $$;

-- =====================================================
-- SECTION 2: VALIDATE ENUM TYPES
-- =====================================================

DO $$
DECLARE
  enum_count INTEGER;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE 'Validating enum types...';
  
  -- Check template_type enum
  SELECT COUNT(*) INTO enum_count 
  FROM pg_type 
  WHERE typname = 'template_type';
  
  IF enum_count = 0 THEN
    RAISE EXCEPTION 'Enum type template_type does not exist';
  END IF;
  RAISE NOTICE '✓ template_type enum exists';
  
  -- Check injection_level enum
  SELECT COUNT(*) INTO enum_count 
  FROM pg_type 
  WHERE typname = 'injection_level';
  
  IF enum_count = 0 THEN
    RAISE EXCEPTION 'Enum type injection_level does not exist';
  END IF;
  RAISE NOTICE '✓ injection_level enum exists';
  
  -- Check component_type enum
  SELECT COUNT(*) INTO enum_count 
  FROM pg_type 
  WHERE typname = 'component_type';
  
  IF enum_count = 0 THEN
    RAISE EXCEPTION 'Enum type component_type does not exist';
  END IF;
  RAISE NOTICE '✓ component_type enum exists';
  
  -- Check hierarchy_type enum
  SELECT COUNT(*) INTO enum_count 
  FROM pg_type 
  WHERE typname = 'hierarchy_type';
  
  IF enum_count = 0 THEN
    RAISE EXCEPTION 'Enum type hierarchy_type does not exist';
  END IF;
  RAISE NOTICE '✓ hierarchy_type enum exists';
  
END $$;

-- =====================================================
-- SECTION 3: VALIDATE INDEXES
-- =====================================================

DO $$
DECLARE
  index_count INTEGER;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE 'Validating indexes...';
  
  -- Count template injection indexes
  SELECT COUNT(*) INTO index_count 
  FROM pg_indexes 
  WHERE indexname LIKE 'idx_workflow_templates_%' 
     OR indexname LIKE 'idx_template_components_%'
     OR indexname LIKE 'idx_template_assignments_%'
     OR indexname = 'idx_tasks_template_metadata';
  
  IF index_count < 10 THEN
    RAISE WARNING 'Expected at least 10 template injection indexes, found %', index_count;
  ELSE
    RAISE NOTICE '✓ % template injection indexes created', index_count;
  END IF;
  
END $$;

-- =====================================================
-- SECTION 4: VALIDATE FUNCTIONS
-- =====================================================

DO $$
DECLARE
  function_count INTEGER;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE 'Validating functions...';
  
  -- Check validation functions
  SELECT COUNT(*) INTO function_count 
  FROM pg_proc 
  WHERE proname IN ('validate_template_content', 'validate_component_name');
  
  IF function_count < 2 THEN
    RAISE WARNING 'Expected 2 validation functions, found %', function_count;
  ELSE
    RAISE NOTICE '✓ % validation functions created', function_count;
  END IF;
  
END $$;

-- =====================================================
-- SECTION 5: VALIDATE SEED DATA (if present)
-- =====================================================

DO $$
DECLARE
  component_count INTEGER;
  template_count INTEGER;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE 'Checking seed data...';
  
  -- Check template components
  SELECT COUNT(*) INTO component_count FROM archon_template_components;
  RAISE NOTICE '✓ % template components found', component_count;
  
  -- Check workflow templates
  SELECT COUNT(*) INTO template_count FROM archon_workflow_templates;
  RAISE NOTICE '✓ % workflow templates found', template_count;
  
  -- Check for default workflow template
  IF EXISTS (SELECT 1 FROM archon_workflow_templates WHERE name = 'workflow::default') THEN
    RAISE NOTICE '✓ Default workflow template (workflow::default) exists';
  ELSE
    RAISE NOTICE '⚠ Default workflow template not found (run seed_default_templates.sql)';
  END IF;
  
END $$;

-- =====================================================
-- SECTION 6: TEST BASIC OPERATIONS
-- =====================================================

DO $$
DECLARE
  test_template_id UUID;
  test_component_id UUID;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE 'Testing basic operations...';
  
  -- Test inserting a template component
  INSERT INTO archon_template_components (
    name, 
    description, 
    component_type, 
    instruction_text,
    category
  ) VALUES (
    'group::test_component',
    'Test component for validation',
    'group',
    'This is a test component for schema validation.',
    'testing'
  ) RETURNING id INTO test_component_id;
  
  RAISE NOTICE '✓ Successfully inserted test component';
  
  -- Test inserting a workflow template
  INSERT INTO archon_workflow_templates (
    name,
    description,
    template_type,
    template_content
  ) VALUES (
    'workflow::test',
    'Test workflow template',
    'workflow',
    '{{group::test_component}}

{{USER_TASK}}

{{group::test_component}}'
  ) RETURNING id INTO test_template_id;
  
  RAISE NOTICE '✓ Successfully inserted test template';
  
  -- Clean up test data
  DELETE FROM archon_workflow_templates WHERE id = test_template_id;
  DELETE FROM archon_template_components WHERE id = test_component_id;
  
  RAISE NOTICE '✓ Successfully cleaned up test data';
  
END $$;

-- =====================================================
-- SECTION 7: COMPLETION SUMMARY
-- =====================================================

DO $$
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'TEMPLATE INJECTION SCHEMA VALIDATION COMPLETE';
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'Schema validation successful!';
  RAISE NOTICE '';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '1. If seed data not present, run: migration/seed_default_templates.sql';
  RAISE NOTICE '2. Implement TemplateInjectionService';
  RAISE NOTICE '3. Integrate with TaskService';
  RAISE NOTICE '4. Create MCP tools';
  RAISE NOTICE '5. Enable feature flags for testing';
  RAISE NOTICE '=================================================';
END $$;
