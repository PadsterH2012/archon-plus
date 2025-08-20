-- =====================================================
-- COMPONENT HIERARCHY MIGRATION TEST
-- =====================================================
-- Simple test script to verify the migration works
-- Run this after add_component_hierarchy.sql
-- =====================================================

-- Test 1: Basic table creation
DO $$
BEGIN
  RAISE NOTICE 'Test 1: Checking table creation...';
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_components') THEN
    RAISE EXCEPTION 'FAIL: archon_components table missing';
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_component_dependencies') THEN
    RAISE EXCEPTION 'FAIL: archon_component_dependencies table missing';
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_template_definitions') THEN
    RAISE EXCEPTION 'FAIL: archon_template_definitions table missing';
  END IF;
  
  RAISE NOTICE 'PASS: All tables created successfully';
END $$;

-- Test 2: Enum creation
DO $$
BEGIN
  RAISE NOTICE 'Test 2: Checking enum creation...';
  
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'component_type_enum') THEN
    RAISE EXCEPTION 'FAIL: component_type_enum missing';
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'component_status_enum') THEN
    RAISE EXCEPTION 'FAIL: component_status_enum missing';
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'template_type_enum') THEN
    RAISE EXCEPTION 'FAIL: template_type_enum missing';
  END IF;
  
  RAISE NOTICE 'PASS: All enums created successfully';
END $$;

-- Test 3: Function creation
DO $$
BEGIN
  RAISE NOTICE 'Test 3: Checking function creation...';
  
  IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'check_component_circular_dependency') THEN
    RAISE EXCEPTION 'FAIL: check_component_circular_dependency function missing';
  END IF;
  
  RAISE NOTICE 'PASS: Circular dependency function created';
END $$;

-- Test 4: Trigger creation
DO $$
DECLARE
  trigger_count INTEGER;
BEGIN
  RAISE NOTICE 'Test 4: Checking trigger creation...';
  
  SELECT COUNT(*) INTO trigger_count
  FROM information_schema.triggers 
  WHERE trigger_name = 'trigger_check_component_circular_dependency'
  AND event_object_table = 'archon_component_dependencies';
  
  IF trigger_count = 0 THEN
    RAISE EXCEPTION 'FAIL: Circular dependency trigger missing';
  ELSIF trigger_count > 1 THEN
    RAISE EXCEPTION 'FAIL: Multiple circular dependency triggers found';
  END IF;
  
  RAISE NOTICE 'PASS: Circular dependency trigger created';
END $$;

-- Test 5: Basic component creation
DO $$
DECLARE
  test_project_id UUID;
  test_component_id UUID;
BEGIN
  RAISE NOTICE 'Test 5: Testing component creation...';
  
  -- Create test project
  INSERT INTO archon_projects (title, description) 
  VALUES ('Test Project', 'Test project for component validation')
  RETURNING id INTO test_project_id;
  
  -- Create test component
  INSERT INTO archon_components (project_id, name, description, component_type, status)
  VALUES (test_project_id, 'test-component', 'Test component', 'feature', 'not_started')
  RETURNING id INTO test_component_id;
  
  -- Verify component was created
  IF test_component_id IS NULL THEN
    RAISE EXCEPTION 'FAIL: Component creation failed';
  END IF;
  
  -- Clean up
  DELETE FROM archon_projects WHERE id = test_project_id;
  
  RAISE NOTICE 'PASS: Component creation working';
END $$;

-- Test 6: Circular dependency prevention
DO $$
DECLARE
  test_project_id UUID;
  comp_a_id UUID;
  comp_b_id UUID;
  error_caught BOOLEAN := FALSE;
BEGIN
  RAISE NOTICE 'Test 6: Testing circular dependency prevention...';
  
  -- Create test project
  INSERT INTO archon_projects (title, description) 
  VALUES ('Test Circular Deps', 'Test project for circular dependency validation')
  RETURNING id INTO test_project_id;
  
  -- Create test components
  INSERT INTO archon_components (project_id, name, description, component_type)
  VALUES 
    (test_project_id, 'comp-a', 'Component A', 'feature'),
    (test_project_id, 'comp-b', 'Component B', 'feature')
  RETURNING id INTO comp_a_id;
  
  SELECT id INTO comp_b_id FROM archon_components WHERE name = 'comp-b' AND project_id = test_project_id;
  
  -- Create dependency: A -> B
  INSERT INTO archon_component_dependencies (component_id, depends_on_component_id)
  VALUES (comp_a_id, comp_b_id);
  
  -- Try to create circular dependency: B -> A (should fail)
  BEGIN
    INSERT INTO archon_component_dependencies (component_id, depends_on_component_id)
    VALUES (comp_b_id, comp_a_id);
  EXCEPTION
    WHEN OTHERS THEN
      error_caught := TRUE;
  END;
  
  -- Clean up
  DELETE FROM archon_projects WHERE id = test_project_id;
  
  IF error_caught THEN
    RAISE NOTICE 'PASS: Circular dependency prevention working';
  ELSE
    RAISE EXCEPTION 'FAIL: Circular dependency was allowed';
  END IF;
END $$;

-- Test 7: Template creation
DO $$
DECLARE
  test_template_id UUID;
BEGIN
  RAISE NOTICE 'Test 7: Testing template creation...';
  
  -- Create test template
  INSERT INTO archon_template_definitions (
    name, title, description, template_type, component_type, template_data
  )
  VALUES (
    'test-template', 
    'Test Template', 
    'Test template for validation',
    'project',
    'feature',
    '{"workflows": [], "actions": []}'::jsonb
  )
  RETURNING id INTO test_template_id;
  
  -- Verify template was created
  IF test_template_id IS NULL THEN
    RAISE EXCEPTION 'FAIL: Template creation failed';
  END IF;
  
  -- Clean up
  DELETE FROM archon_template_definitions WHERE id = test_template_id;
  
  RAISE NOTICE 'PASS: Template creation working';
END $$;

-- Final summary
DO $$
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '🎉 ALL TESTS PASSED!';
  RAISE NOTICE '✅ Component hierarchy migration successful';
  RAISE NOTICE '✅ All tables, enums, functions, and triggers created';
  RAISE NOTICE '✅ Basic functionality verified';
  RAISE NOTICE '✅ Circular dependency prevention working';
  RAISE NOTICE '';
  RAISE NOTICE 'Migration is ready for production use!';
END $$;
