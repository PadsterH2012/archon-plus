-- =====================================================
-- ARCHON TEMPLATE INJECTION SYSTEM - ROLLBACK SCRIPT
-- =====================================================
-- This script safely removes the Template Injection System database schema
-- while preserving all existing data and functionality.
-- 
-- This rollback script can be used to completely remove the template
-- injection system if needed, with zero impact on existing tasks.
-- 
-- Created: 2025-08-20
-- Version: 1.0.0
-- =====================================================

-- =====================================================
-- SECTION 1: SAFETY WARNING
-- =====================================================

DO $$
BEGIN
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'ARCHON TEMPLATE INJECTION ROLLBACK STARTING';
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'This will remove all template injection tables and data.';
  RAISE NOTICE 'Existing tasks will continue working unchanged.';
  RAISE NOTICE 'Template metadata in tasks will be preserved.';
  RAISE NOTICE '=================================================';
END $$;

-- =====================================================
-- SECTION 2: DROP VALIDATION CONSTRAINTS
-- =====================================================

-- Remove validation constraints first
DO $$
BEGIN
  -- Drop template content validation constraint
  IF EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE table_name = 'archon_workflow_templates' 
    AND constraint_name = 'check_template_content'
  ) THEN
    ALTER TABLE archon_workflow_templates DROP CONSTRAINT check_template_content;
    RAISE NOTICE 'Dropped template content validation constraint';
  END IF;
  
  -- Drop component name validation constraint
  IF EXISTS (
    SELECT 1 FROM information_schema.table_constraints 
    WHERE table_name = 'archon_template_components' 
    AND constraint_name = 'check_component_name'
  ) THEN
    ALTER TABLE archon_template_components DROP CONSTRAINT check_component_name;
    RAISE NOTICE 'Dropped component name validation constraint';
  END IF;
END $$;

-- =====================================================
-- SECTION 3: DROP TRIGGERS
-- =====================================================

-- Drop update triggers
DROP TRIGGER IF EXISTS update_workflow_templates_updated_at ON archon_workflow_templates;
DROP TRIGGER IF EXISTS update_template_components_updated_at ON archon_template_components;
DROP TRIGGER IF EXISTS update_template_assignments_updated_at ON archon_template_assignments;

RAISE NOTICE 'Dropped update triggers';

-- =====================================================
-- SECTION 4: DROP VALIDATION FUNCTIONS
-- =====================================================

-- Drop validation functions
DROP FUNCTION IF EXISTS validate_template_content(TEXT);
DROP FUNCTION IF EXISTS validate_component_name(VARCHAR);

RAISE NOTICE 'Dropped validation functions';

-- =====================================================
-- SECTION 5: DROP INDEXES
-- =====================================================

-- Drop all template injection indexes
DROP INDEX IF EXISTS idx_workflow_templates_name;
DROP INDEX IF EXISTS idx_workflow_templates_type;
DROP INDEX IF EXISTS idx_workflow_templates_injection_level;
DROP INDEX IF EXISTS idx_workflow_templates_active;
DROP INDEX IF EXISTS idx_workflow_templates_phases;

DROP INDEX IF EXISTS idx_template_components_name;
DROP INDEX IF EXISTS idx_template_components_type;
DROP INDEX IF EXISTS idx_template_components_category;
DROP INDEX IF EXISTS idx_template_components_active;
DROP INDEX IF EXISTS idx_template_components_tags;
DROP INDEX IF EXISTS idx_template_components_tools;

DROP INDEX IF EXISTS idx_template_assignments_hierarchy;
DROP INDEX IF EXISTS idx_template_assignments_template;
DROP INDEX IF EXISTS idx_template_assignments_active;
DROP INDEX IF EXISTS idx_template_assignments_priority;

DROP INDEX IF EXISTS idx_tasks_template_metadata;

RAISE NOTICE 'Dropped all template injection indexes';

-- =====================================================
-- SECTION 6: DROP TABLES
-- =====================================================

-- Drop tables in correct order (respecting foreign key constraints)
DROP TABLE IF EXISTS archon_template_assignments CASCADE;
DROP TABLE IF EXISTS archon_template_components CASCADE;
DROP TABLE IF EXISTS archon_workflow_templates CASCADE;

RAISE NOTICE 'Dropped all template injection tables';

-- =====================================================
-- SECTION 7: REMOVE COLUMN FROM EXISTING TABLE
-- =====================================================

-- Optionally remove template_metadata column from archon_tasks
-- (Commented out by default to preserve any existing template metadata)
/*
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'archon_tasks' 
    AND column_name = 'template_metadata'
  ) THEN
    ALTER TABLE archon_tasks DROP COLUMN template_metadata;
    RAISE NOTICE 'Removed template_metadata column from archon_tasks';
  END IF;
END $$;
*/

RAISE NOTICE 'Preserved template_metadata column in archon_tasks (contains existing data)';

-- =====================================================
-- SECTION 8: DROP ENUM TYPES
-- =====================================================

-- Drop enum types (in reverse dependency order)
DROP TYPE IF EXISTS template_hierarchy_type CASCADE;
DROP TYPE IF EXISTS template_component_type CASCADE;
DROP TYPE IF EXISTS template_injection_level CASCADE;
DROP TYPE IF EXISTS template_injection_type CASCADE;

RAISE NOTICE 'Dropped all template injection enum types';

-- =====================================================
-- SECTION 9: COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'ARCHON TEMPLATE INJECTION ROLLBACK COMPLETED';
  RAISE NOTICE '=================================================';
  RAISE NOTICE 'Successfully removed:';
  RAISE NOTICE '  - All template injection tables';
  RAISE NOTICE '  - All template injection indexes';
  RAISE NOTICE '  - All template injection functions';
  RAISE NOTICE '  - All template injection triggers';
  RAISE NOTICE '  - All template injection enum types';
  RAISE NOTICE '';
  RAISE NOTICE 'Preserved:';
  RAISE NOTICE '  - All existing task data';
  RAISE NOTICE '  - Template metadata in tasks (if any)';
  RAISE NOTICE '  - All other Archon functionality';
  RAISE NOTICE '';
  RAISE NOTICE 'System status: Template injection completely removed';
  RAISE NOTICE 'All existing functionality continues unchanged';
  RAISE NOTICE '=================================================';
END $$;
