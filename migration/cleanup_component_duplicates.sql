-- =====================================================
-- COMPONENT HIERARCHY CLEANUP SCRIPT
-- =====================================================
-- This script cleans up any duplicate triggers or other
-- issues that may have occurred from running the migration
-- multiple times
-- =====================================================

-- =====================================================
-- SECTION 1: CLEANUP DUPLICATE TRIGGERS
-- =====================================================

DO $$
DECLARE
  trigger_count INTEGER;
BEGIN
  RAISE NOTICE '🧹 Starting Component Hierarchy Cleanup...';
  
  -- Check current trigger count
  SELECT COUNT(*) INTO trigger_count
  FROM information_schema.triggers 
  WHERE trigger_name = 'trigger_check_component_circular_dependency'
  AND event_object_table = 'archon_component_dependencies';
  
  RAISE NOTICE 'Found % circular dependency triggers', trigger_count;
  
  -- Drop all instances of the trigger
  IF trigger_count > 0 THEN
    DROP TRIGGER IF EXISTS trigger_check_component_circular_dependency ON archon_component_dependencies;
    RAISE NOTICE '✅ Removed all circular dependency triggers';
  END IF;
  
  -- Recreate the trigger (only once)
  CREATE TRIGGER trigger_check_component_circular_dependency
    BEFORE INSERT OR UPDATE ON archon_component_dependencies
    FOR EACH ROW
    EXECUTE FUNCTION check_component_circular_dependency();
    
  RAISE NOTICE '✅ Recreated single circular dependency trigger';
END $$;

-- =====================================================
-- SECTION 2: VERIFY CLEANUP SUCCESS
-- =====================================================

DO $$
DECLARE
  trigger_count INTEGER;
  function_exists BOOLEAN;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '🔍 Verifying cleanup results...';
  
  -- Check function exists
  SELECT EXISTS(
    SELECT 1 FROM pg_proc 
    WHERE proname = 'check_component_circular_dependency'
  ) INTO function_exists;
  
  IF function_exists THEN
    RAISE NOTICE '✅ Circular dependency function exists';
  ELSE
    RAISE EXCEPTION '❌ Circular dependency function missing';
  END IF;
  
  -- Check trigger count
  SELECT COUNT(*) INTO trigger_count
  FROM information_schema.triggers 
  WHERE trigger_name = 'trigger_check_component_circular_dependency'
  AND event_object_table = 'archon_component_dependencies';
  
  IF trigger_count = 1 THEN
    RAISE NOTICE '✅ Exactly one circular dependency trigger exists';
  ELSIF trigger_count = 0 THEN
    RAISE EXCEPTION '❌ No circular dependency trigger found';
  ELSE
    RAISE EXCEPTION '❌ Multiple circular dependency triggers found: %', trigger_count;
  END IF;
END $$;

-- =====================================================
-- SECTION 3: TEST CIRCULAR DEPENDENCY PREVENTION
-- =====================================================

DO $$
DECLARE
  test_project_id UUID;
  comp_a_id UUID;
  comp_b_id UUID;
  error_caught BOOLEAN := FALSE;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '🧪 Testing circular dependency prevention...';
  
  -- Create test project
  INSERT INTO archon_projects (title, description) 
  VALUES ('Cleanup Test Project', 'Test project for cleanup validation')
  RETURNING id INTO test_project_id;
  
  -- Create test components
  INSERT INTO archon_components (project_id, name, description, component_type)
  VALUES 
    (test_project_id, 'cleanup-comp-a', 'Component A', 'feature'),
    (test_project_id, 'cleanup-comp-b', 'Component B', 'feature')
  RETURNING id INTO comp_a_id;
  
  SELECT id INTO comp_b_id FROM archon_components WHERE name = 'cleanup-comp-b' AND project_id = test_project_id;
  
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
  
  -- Clean up test data
  DELETE FROM archon_projects WHERE id = test_project_id;
  
  IF error_caught THEN
    RAISE NOTICE '✅ Circular dependency prevention working correctly';
  ELSE
    RAISE EXCEPTION '❌ Circular dependency prevention failed - circular dependency was allowed';
  END IF;
END $$;

-- =====================================================
-- CLEANUP COMPLETE
-- =====================================================

DO $$
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '🎉 Component Hierarchy Cleanup Complete!';
  RAISE NOTICE '✅ Duplicate triggers removed';
  RAISE NOTICE '✅ Single trigger recreated';
  RAISE NOTICE '✅ Circular dependency prevention verified';
  RAISE NOTICE '';
  RAISE NOTICE 'Component hierarchy is now ready for use!';
END $$;
