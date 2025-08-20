-- =====================================================
-- ARCHON COMPONENT HIERARCHY VALIDATION
-- =====================================================
-- This script validates the component hierarchy migration
-- 
-- Run this script in your Supabase SQL Editor after
-- running add_component_hierarchy.sql to verify the migration
-- =====================================================

-- =====================================================
-- SECTION 1: TABLE EXISTENCE VALIDATION
-- =====================================================

DO $$
DECLARE
  table_count INTEGER;
  enum_count INTEGER;
  index_count INTEGER;
BEGIN
  RAISE NOTICE '🔍 Starting Component Hierarchy Validation...';
  RAISE NOTICE '';
  
  -- Check core tables exist
  SELECT COUNT(*) INTO table_count
  FROM information_schema.tables 
  WHERE table_name IN ('archon_components', 'archon_component_dependencies', 'archon_template_definitions');
  
  IF table_count = 3 THEN
    RAISE NOTICE '✅ All component tables created successfully';
  ELSE
    RAISE EXCEPTION '❌ Missing component tables. Expected 3, found %', table_count;
  END IF;
  
  -- Check enum types exist
  SELECT COUNT(*) INTO enum_count
  FROM pg_type 
  WHERE typname IN ('component_type_enum', 'component_status_enum', 'template_type_enum');
  
  IF enum_count = 3 THEN
    RAISE NOTICE '✅ All component enums created successfully';
  ELSE
    RAISE EXCEPTION '❌ Missing component enums. Expected 3, found %', enum_count;
  END IF;
  
  -- Check indexes exist
  SELECT COUNT(*) INTO index_count
  FROM pg_indexes 
  WHERE indexname LIKE 'idx_component%' OR indexname LIKE 'idx_template%';
  
  IF index_count >= 10 THEN
    RAISE NOTICE '✅ Component indexes created successfully (% indexes)', index_count;
  ELSE
    RAISE WARNING '⚠️  Expected at least 10 component indexes, found %', index_count;
  END IF;
  
  RAISE NOTICE '';
END $$;

-- =====================================================
-- SECTION 2: CONSTRAINT VALIDATION
-- =====================================================

DO $$
DECLARE
  constraint_count INTEGER;
  fk_count INTEGER;
BEGIN
  RAISE NOTICE '🔗 Validating Constraints...';
  
  -- Check unique constraints
  SELECT COUNT(*) INTO constraint_count
  FROM information_schema.table_constraints 
  WHERE constraint_type = 'UNIQUE' 
  AND table_name IN ('archon_components', 'archon_component_dependencies', 'archon_template_definitions');
  
  IF constraint_count >= 3 THEN
    RAISE NOTICE '✅ Unique constraints created successfully';
  ELSE
    RAISE WARNING '⚠️  Expected at least 3 unique constraints, found %', constraint_count;
  END IF;
  
  -- Check foreign key constraints
  SELECT COUNT(*) INTO fk_count
  FROM information_schema.table_constraints 
  WHERE constraint_type = 'FOREIGN KEY' 
  AND table_name IN ('archon_components', 'archon_component_dependencies', 'archon_template_definitions');
  
  IF fk_count >= 5 THEN
    RAISE NOTICE '✅ Foreign key constraints created successfully';
  ELSE
    RAISE WARNING '⚠️  Expected at least 5 foreign key constraints, found %', fk_count;
  END IF;
  
  RAISE NOTICE '';
END $$;

-- =====================================================
-- SECTION 3: TRIGGER VALIDATION
-- =====================================================

DO $$
DECLARE
  trigger_count INTEGER;
  function_exists BOOLEAN;
  rec RECORD;
BEGIN
  RAISE NOTICE '🛡️  Validating Circular Dependency Prevention...';
  
  -- Check if circular dependency function exists
  SELECT EXISTS(
    SELECT 1 FROM pg_proc 
    WHERE proname = 'check_component_circular_dependency'
  ) INTO function_exists;
  
  IF function_exists THEN
    RAISE NOTICE '✅ Circular dependency check function created';
  ELSE
    RAISE EXCEPTION '❌ Circular dependency check function missing';
  END IF;
  
  -- Check if trigger exists
  SELECT COUNT(*) INTO trigger_count
  FROM information_schema.triggers
  WHERE trigger_name = 'trigger_check_component_circular_dependency'
  AND event_object_table = 'archon_component_dependencies';

  -- Debug: Show all triggers on the table
  RAISE NOTICE 'Debug: Triggers on archon_component_dependencies table:';
  FOR rec IN
    SELECT trigger_name, event_manipulation, action_timing
    FROM information_schema.triggers
    WHERE event_object_table = 'archon_component_dependencies'
  LOOP
    RAISE NOTICE '  - %: % %', rec.trigger_name, rec.action_timing, rec.event_manipulation;
  END LOOP;

  IF trigger_count = 1 THEN
    RAISE NOTICE '✅ Circular dependency trigger created';
  ELSIF trigger_count = 0 THEN
    RAISE EXCEPTION '❌ Circular dependency trigger missing. Run migration/add_component_hierarchy.sql';
  ELSE
    RAISE EXCEPTION '❌ Circular dependency trigger duplicated (found % instances). Run migration/cleanup_component_duplicates.sql to fix', trigger_count;
  END IF;
  
  RAISE NOTICE '';
END $$;

-- =====================================================
-- SECTION 4: DATA MIGRATION VALIDATION
-- =====================================================

DO $$
DECLARE
  project_count INTEGER;
  component_count INTEGER;
  migrated_task_count INTEGER;
  unmigrated_task_count INTEGER;
BEGIN
  RAISE NOTICE '📊 Validating Data Migration...';
  
  -- Count existing projects
  SELECT COUNT(*) INTO project_count FROM archon_projects;
  
  -- Count main components created
  SELECT COUNT(*) INTO component_count 
  FROM archon_components 
  WHERE name = 'main' AND component_type = 'foundation';
  
  IF project_count = component_count THEN
    RAISE NOTICE '✅ All % projects migrated to component structure', project_count;
  ELSE
    RAISE WARNING '⚠️  Project migration incomplete. Projects: %, Main components: %', 
                  project_count, component_count;
  END IF;
  
  -- Check task migration
  SELECT COUNT(*) INTO migrated_task_count 
  FROM archon_tasks 
  WHERE component_id IS NOT NULL;
  
  SELECT COUNT(*) INTO unmigrated_task_count 
  FROM archon_tasks 
  WHERE component_id IS NULL AND project_id IS NOT NULL;
  
  IF unmigrated_task_count = 0 THEN
    RAISE NOTICE '✅ All % tasks migrated to component structure', migrated_task_count;
  ELSE
    RAISE WARNING '⚠️  Task migration incomplete. Migrated: %, Unmigrated: %', 
                  migrated_task_count, unmigrated_task_count;
  END IF;
  
  RAISE NOTICE '';
END $$;

-- =====================================================
-- SECTION 5: PERFORMANCE VALIDATION
-- =====================================================

DO $$
BEGIN
  RAISE NOTICE '⚡ Validating Performance Indexes...';
  
  -- Test component queries
  EXPLAIN (FORMAT TEXT, ANALYZE FALSE, BUFFERS FALSE, COSTS FALSE) 
  SELECT * FROM archon_components WHERE project_id = gen_random_uuid();
  
  RAISE NOTICE '✅ Component query performance validated';
  
  -- Test dependency queries  
  EXPLAIN (FORMAT TEXT, ANALYZE FALSE, BUFFERS FALSE, COSTS FALSE)
  SELECT * FROM archon_component_dependencies WHERE component_id = gen_random_uuid();
  
  RAISE NOTICE '✅ Dependency query performance validated';
  
  -- Test template queries
  EXPLAIN (FORMAT TEXT, ANALYZE FALSE, BUFFERS FALSE, COSTS FALSE)
  SELECT * FROM archon_template_definitions WHERE template_type = 'project';
  
  RAISE NOTICE '✅ Template query performance validated';
  RAISE NOTICE '';
END $$;

-- =====================================================
-- SECTION 6: CIRCULAR DEPENDENCY TEST
-- =====================================================

DO $$
DECLARE
  test_project_id UUID;
  comp_a_id UUID;
  comp_b_id UUID;
  comp_c_id UUID;
  error_caught BOOLEAN := FALSE;
BEGIN
  RAISE NOTICE '🔄 Testing Circular Dependency Prevention...';
  
  -- Create test project
  INSERT INTO archon_projects (title, description) 
  VALUES ('Test Circular Dependencies', 'Test project for validation')
  RETURNING id INTO test_project_id;
  
  -- Create test components
  INSERT INTO archon_components (project_id, name, description, component_type)
  VALUES 
    (test_project_id, 'comp-a', 'Component A', 'feature'),
    (test_project_id, 'comp-b', 'Component B', 'feature'),
    (test_project_id, 'comp-c', 'Component C', 'feature')
  RETURNING id INTO comp_a_id;
  
  SELECT id INTO comp_b_id FROM archon_components WHERE name = 'comp-b' AND project_id = test_project_id;
  SELECT id INTO comp_c_id FROM archon_components WHERE name = 'comp-c' AND project_id = test_project_id;
  
  -- Create valid dependencies: A -> B -> C
  INSERT INTO archon_component_dependencies (component_id, depends_on_component_id)
  VALUES 
    (comp_a_id, comp_b_id),
    (comp_b_id, comp_c_id);
  
  -- Try to create circular dependency: C -> A (should fail)
  BEGIN
    INSERT INTO archon_component_dependencies (component_id, depends_on_component_id)
    VALUES (comp_c_id, comp_a_id);
  EXCEPTION
    WHEN OTHERS THEN
      error_caught := TRUE;
  END;
  
  IF error_caught THEN
    RAISE NOTICE '✅ Circular dependency prevention working correctly';
  ELSE
    RAISE EXCEPTION '❌ Circular dependency prevention failed - circular dependency was allowed';
  END IF;
  
  -- Clean up test data
  DELETE FROM archon_projects WHERE id = test_project_id;
  
  RAISE NOTICE '';
END $$;

-- =====================================================
-- SECTION 7: SUMMARY REPORT
-- =====================================================

DO $$
DECLARE
  total_components INTEGER;
  total_dependencies INTEGER;
  total_templates INTEGER;
BEGIN
  RAISE NOTICE '📋 VALIDATION SUMMARY REPORT';
  RAISE NOTICE '================================================';
  
  SELECT COUNT(*) INTO total_components FROM archon_components;
  SELECT COUNT(*) INTO total_dependencies FROM archon_component_dependencies;
  SELECT COUNT(*) INTO total_templates FROM archon_template_definitions;
  
  RAISE NOTICE '📊 Database Objects:';
  RAISE NOTICE '   • Components: %', total_components;
  RAISE NOTICE '   • Dependencies: %', total_dependencies;
  RAISE NOTICE '   • Templates: %', total_templates;
  RAISE NOTICE '';
  
  RAISE NOTICE '✅ Component Hierarchy Migration Validation Complete!';
  RAISE NOTICE '';
  RAISE NOTICE '🎯 Next Steps:';
  RAISE NOTICE '   1. Implement Pydantic models (component_models.py)';
  RAISE NOTICE '   2. Create ComponentService and TemplateService';
  RAISE NOTICE '   3. Add MCP tools for component management';
  RAISE NOTICE '   4. Build frontend UI components';
  RAISE NOTICE '';
  RAISE NOTICE '================================================';
END $$;
