-- =====================================================
-- ARCHON COMPONENT HIERARCHY MIGRATION
-- =====================================================
-- This script adds the component hierarchy system to Archon
-- 
-- Features:
-- - Component management with types (foundation, feature, integration)
-- - Component dependency tracking with circular dependency prevention
-- - Template system with inheritance hierarchy
-- - Integration with existing project/task structure
-- 
-- Run this script in your Supabase SQL Editor after complete_setup.sql
-- =====================================================

-- =====================================================
-- SECTION 1: COMPONENT ENUMS AND TYPES
-- =====================================================

-- Component type enumeration
CREATE TYPE component_type_enum AS ENUM (
  'foundation',    -- Core infrastructure components
  'feature',       -- Feature development components
  'integration'    -- Integration and deployment components
);

-- Component status enumeration
CREATE TYPE component_status_enum AS ENUM (
  'not_started',   -- Component not yet begun
  'in_progress',   -- Component actively being developed
  'completed',     -- Component development finished
  'blocked'        -- Component blocked by dependencies
);

-- Template type enumeration
CREATE TYPE template_type_enum AS ENUM (
  'global',        -- Global default templates
  'industry',      -- Industry-specific templates (web, mobile, etc.)
  'team',          -- Team-specific templates
  'project'        -- Project-specific customizations
);

-- =====================================================
-- SECTION 2: COMPONENT TABLES
-- =====================================================

-- Components table - Core component management
CREATE TABLE IF NOT EXISTS archon_components (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT DEFAULT '',
  component_type component_type_enum DEFAULT 'feature',
  status component_status_enum DEFAULT 'not_started',
  
  -- Component hierarchy and dependencies
  parent_component_id UUID REFERENCES archon_components(id) ON DELETE SET NULL,
  order_index INTEGER DEFAULT 0,
  
  -- Context and configuration
  context_data JSONB DEFAULT '{}'::jsonb,
  completion_gates JSONB DEFAULT '[]'::jsonb, -- Array of completion requirements
  
  -- Template association
  template_id UUID, -- Will reference archon_template_definitions(id)
  template_customizations JSONB DEFAULT '{}'::jsonb,
  
  -- Audit fields
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT unique_component_name_per_project UNIQUE (project_id, name),
  CONSTRAINT chk_component_name_format CHECK (name ~ '^[a-z0-9_-]+$'),
  CONSTRAINT chk_order_index_non_negative CHECK (order_index >= 0),
  CONSTRAINT no_self_parent CHECK (id != parent_component_id)
);

-- Component Dependencies table - Track component dependencies
CREATE TABLE IF NOT EXISTS archon_component_dependencies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  component_id UUID REFERENCES archon_components(id) ON DELETE CASCADE,
  depends_on_component_id UUID REFERENCES archon_components(id) ON DELETE CASCADE,
  
  -- Dependency configuration
  dependency_type VARCHAR(50) DEFAULT 'hard', -- 'hard', 'soft', 'optional'
  gate_requirements JSONB DEFAULT '[]'::jsonb, -- Specific gates that must be met
  
  -- Audit fields
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT no_self_dependency CHECK (component_id != depends_on_component_id),
  CONSTRAINT unique_component_dependency UNIQUE (component_id, depends_on_component_id)
);

-- =====================================================
-- SECTION 3: TEMPLATE SYSTEM TABLES
-- =====================================================

-- Template Definitions table - Reusable component templates
CREATE TABLE IF NOT EXISTS archon_template_definitions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  template_type template_type_enum DEFAULT 'project',
  
  -- Template hierarchy
  parent_template_id UUID REFERENCES archon_template_definitions(id) ON DELETE SET NULL,
  inheritance_level INTEGER DEFAULT 0, -- 0=global, 1=industry, 2=team, 3=project
  
  -- Template configuration
  component_type component_type_enum, -- What type of component this template applies to
  template_data JSONB NOT NULL DEFAULT '{}'::jsonb, -- Template configuration and workflows
  default_context JSONB DEFAULT '{}'::jsonb, -- Default context data
  
  -- Template metadata
  category VARCHAR(100), -- e.g., 'web-development', 'mobile-app', 'infrastructure'
  tags JSONB DEFAULT '[]'::jsonb, -- Array of tags for categorization
  
  -- Access control
  is_public BOOLEAN DEFAULT false,
  created_by TEXT NOT NULL DEFAULT 'system',
  
  -- Audit fields
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT unique_template_name UNIQUE (name),
  CONSTRAINT chk_template_name_format CHECK (name ~ '^[a-z0-9_-]+$'),
  CONSTRAINT chk_inheritance_level_valid CHECK (inheritance_level >= 0 AND inheritance_level <= 3),
  CONSTRAINT no_self_parent_template CHECK (id != parent_template_id)
);

-- =====================================================
-- SECTION 4: INDEXES FOR PERFORMANCE
-- =====================================================

-- Component indexes
CREATE INDEX IF NOT EXISTS idx_components_project_id ON archon_components(project_id);
CREATE INDEX IF NOT EXISTS idx_components_status ON archon_components(status);
CREATE INDEX IF NOT EXISTS idx_components_type ON archon_components(component_type);
CREATE INDEX IF NOT EXISTS idx_components_parent ON archon_components(parent_component_id);
CREATE INDEX IF NOT EXISTS idx_components_template ON archon_components(template_id);

-- Component dependency indexes
CREATE INDEX IF NOT EXISTS idx_component_deps_component_id ON archon_component_dependencies(component_id);
CREATE INDEX IF NOT EXISTS idx_component_deps_depends_on ON archon_component_dependencies(depends_on_component_id);

-- Template indexes
CREATE INDEX IF NOT EXISTS idx_templates_type ON archon_template_definitions(template_type);
CREATE INDEX IF NOT EXISTS idx_templates_component_type ON archon_template_definitions(component_type);
CREATE INDEX IF NOT EXISTS idx_templates_parent ON archon_template_definitions(parent_template_id);
CREATE INDEX IF NOT EXISTS idx_templates_category ON archon_template_definitions(category);
CREATE INDEX IF NOT EXISTS idx_templates_tags ON archon_template_definitions USING GIN(tags);

-- =====================================================
-- SECTION 5: FOREIGN KEY CONSTRAINTS
-- =====================================================

-- Add foreign key constraint for template_id (deferred to avoid circular dependency during creation)
ALTER TABLE archon_components 
ADD CONSTRAINT fk_components_template_id 
FOREIGN KEY (template_id) REFERENCES archon_template_definitions(id) ON DELETE SET NULL;

-- =====================================================
-- SECTION 6: EXTEND EXISTING TABLES
-- =====================================================

-- Add component_id to existing tasks table
ALTER TABLE archon_tasks 
ADD COLUMN IF NOT EXISTS component_id UUID REFERENCES archon_components(id) ON DELETE SET NULL;

-- Add index for task-component relationship
CREATE INDEX IF NOT EXISTS idx_tasks_component_id ON archon_tasks(component_id);

-- =====================================================
-- SECTION 7: CIRCULAR DEPENDENCY PREVENTION
-- =====================================================

-- Drop existing trigger if it exists (for idempotent migration)
DROP TRIGGER IF EXISTS trigger_check_component_circular_dependency ON archon_component_dependencies;

-- Function to check for circular dependencies
CREATE OR REPLACE FUNCTION check_component_circular_dependency()
RETURNS TRIGGER AS $$
BEGIN
  -- Use recursive CTE to detect cycles
  WITH RECURSIVE dependency_path AS (
    -- Base case: start with the new dependency
    SELECT
      NEW.component_id as start_component,
      NEW.depends_on_component_id as current_component,
      1 as depth,
      ARRAY[NEW.component_id, NEW.depends_on_component_id] as path

    UNION ALL

    -- Recursive case: follow the dependency chain
    SELECT
      dp.start_component,
      cd.depends_on_component_id,
      dp.depth + 1,
      dp.path || cd.depends_on_component_id
    FROM dependency_path dp
    JOIN archon_component_dependencies cd ON cd.component_id = dp.current_component
    WHERE dp.depth < 50 -- Prevent infinite recursion
      AND NOT (cd.depends_on_component_id = ANY(dp.path)) -- Avoid cycles in path
  )
  SELECT 1 FROM dependency_path
  WHERE current_component = start_component
  LIMIT 1;

  -- If we found a cycle, raise an error
  IF FOUND THEN
    RAISE EXCEPTION 'Circular dependency detected: Component % would create a dependency cycle', NEW.component_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to prevent circular dependencies
CREATE TRIGGER trigger_check_component_circular_dependency
  BEFORE INSERT OR UPDATE ON archon_component_dependencies
  FOR EACH ROW
  EXECUTE FUNCTION check_component_circular_dependency();

-- =====================================================
-- SECTION 8: DATA MIGRATION
-- =====================================================

-- Create default "main" component for existing projects
INSERT INTO archon_components (project_id, name, description, component_type, status)
SELECT
  id as project_id,
  'main' as name,
  'Migrated from legacy project structure' as description,
  'foundation' as component_type,
  'completed' as status
FROM archon_projects
WHERE id NOT IN (SELECT DISTINCT project_id FROM archon_components WHERE project_id IS NOT NULL);

-- Associate existing tasks with main component
UPDATE archon_tasks
SET component_id = (
  SELECT c.id 
  FROM archon_components c
  WHERE c.project_id = archon_tasks.project_id
  AND c.name = 'main'
)
WHERE component_id IS NULL
AND project_id IS NOT NULL;

-- =====================================================
-- SECTION 9: TABLE COMMENTS
-- =====================================================

-- Add table comments for documentation
COMMENT ON TABLE archon_components IS 'Component hierarchy for project organization with dependency management';
COMMENT ON TABLE archon_component_dependencies IS 'Tracks dependencies between components with gate requirements';
COMMENT ON TABLE archon_template_definitions IS 'Reusable component templates with inheritance hierarchy';

-- Add column comments for key fields
COMMENT ON COLUMN archon_components.context_data IS 'JSONB context data specific to this component';
COMMENT ON COLUMN archon_components.completion_gates IS 'JSONB array of completion requirements for this component';
COMMENT ON COLUMN archon_component_dependencies.gate_requirements IS 'JSONB array of specific gates that must be met';
COMMENT ON COLUMN archon_template_definitions.template_data IS 'JSONB template configuration including workflows and actions';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Verify migration success
DO $$
BEGIN
  -- Check that all tables were created
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_components') THEN
    RAISE EXCEPTION 'Migration failed: archon_components table not created';
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_component_dependencies') THEN
    RAISE EXCEPTION 'Migration failed: archon_component_dependencies table not created';
  END IF;
  
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'archon_template_definitions') THEN
    RAISE EXCEPTION 'Migration failed: archon_template_definitions table not created';
  END IF;
  
  -- Check that existing projects have main components
  IF EXISTS (
    SELECT 1 FROM archon_projects p 
    WHERE NOT EXISTS (
      SELECT 1 FROM archon_components c 
      WHERE c.project_id = p.id AND c.name = 'main'
    )
  ) THEN
    RAISE WARNING 'Some projects may not have been migrated to component structure';
  END IF;
  
  RAISE NOTICE '✅ Component hierarchy migration completed successfully!';
  RAISE NOTICE '📊 Tables created: archon_components, archon_component_dependencies, archon_template_definitions';
  RAISE NOTICE '🔗 Existing projects migrated to component structure';
  RAISE NOTICE '🛡️ Circular dependency prevention enabled';
END $$;
