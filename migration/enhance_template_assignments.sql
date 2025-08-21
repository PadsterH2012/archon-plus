-- =====================================================
-- Template Assignment System Enhancement
-- =====================================================
-- This migration enhances the template assignment system to support
-- multi-level template assignment with inheritance hierarchy:
-- Global → Project → Milestone → Phase → Task
-- =====================================================

-- Add new enum for assignment scope
DO $$ BEGIN
    CREATE TYPE assignment_scope_enum AS ENUM (
        'all',              -- Apply to all entities at this level
        'specific_types',   -- Apply to specific entity types
        'conditional'       -- Apply based on conditional logic
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Add new enum for hierarchy levels
DO $$ BEGIN
    CREATE TYPE hierarchy_level_enum AS ENUM (
        'global',
        'project', 
        'milestone',
        'phase',
        'task'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Enhance the existing template_assignments table
ALTER TABLE archon_template_assignments 
ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS assignment_scope assignment_scope_enum DEFAULT 'all',
ADD COLUMN IF NOT EXISTS conditional_logic JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS inheritance_enabled BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS hierarchy_level hierarchy_level_enum DEFAULT 'task',
ADD COLUMN IF NOT EXISTS entity_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS effective_from TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS effective_until TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS created_by VARCHAR(255) DEFAULT 'system',
ADD COLUMN IF NOT EXISTS updated_by VARCHAR(255) DEFAULT 'system';

-- Add comments for new columns
COMMENT ON COLUMN archon_template_assignments.priority IS 'Priority for conflict resolution (higher = more priority)';
COMMENT ON COLUMN archon_template_assignments.assignment_scope IS 'Scope of assignment: all, specific_types, or conditional';
COMMENT ON COLUMN archon_template_assignments.conditional_logic IS 'JSONB containing conditional assignment rules';
COMMENT ON COLUMN archon_template_assignments.inheritance_enabled IS 'Whether this assignment participates in inheritance';
COMMENT ON COLUMN archon_template_assignments.hierarchy_level IS 'Level in hierarchy: global, project, milestone, phase, task';
COMMENT ON COLUMN archon_template_assignments.entity_type IS 'Type of entity (e.g., feature, bugfix, research)';
COMMENT ON COLUMN archon_template_assignments.metadata IS 'Additional metadata for assignment';
COMMENT ON COLUMN archon_template_assignments.effective_from IS 'When assignment becomes effective';
COMMENT ON COLUMN archon_template_assignments.effective_until IS 'When assignment expires (null = never)';

-- Create template assignment resolution cache table
CREATE TABLE IF NOT EXISTS archon_template_assignment_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Cache key components
    entity_id UUID NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    hierarchy_level hierarchy_level_enum NOT NULL,
    context_hash VARCHAR(64), -- Hash of context data for cache invalidation
    
    -- Resolved template information
    resolved_template_name VARCHAR(255) NOT NULL,
    resolution_path JSONB NOT NULL, -- Array of assignments that led to this resolution
    assignment_metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Cache metadata
    cache_hit_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(entity_id, entity_type, hierarchy_level, context_hash)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_template_assignments_hierarchy 
ON archon_template_assignments(hierarchy_level, entity_type, priority DESC);

CREATE INDEX IF NOT EXISTS idx_template_assignments_entity 
ON archon_template_assignments(entity_id, hierarchy_level);

CREATE INDEX IF NOT EXISTS idx_template_assignments_effective 
ON archon_template_assignments(effective_from, effective_until) 
WHERE effective_until IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_template_assignment_cache_entity 
ON archon_template_assignment_cache(entity_id, entity_type, hierarchy_level);

CREATE INDEX IF NOT EXISTS idx_template_assignment_cache_expires 
ON archon_template_assignment_cache(expires_at);

-- Create function to resolve template inheritance
CREATE OR REPLACE FUNCTION resolve_template_inheritance(
    p_entity_id UUID,
    p_entity_type VARCHAR(50),
    p_project_id UUID DEFAULT NULL,
    p_context_data JSONB DEFAULT '{}'::jsonb
) RETURNS TABLE (
    template_name VARCHAR(255),
    hierarchy_level hierarchy_level_enum,
    assignment_id UUID,
    priority INTEGER,
    resolution_path JSONB
) AS $$
DECLARE
    v_resolution_path JSONB := '[]'::jsonb;
    v_current_level hierarchy_level_enum;
    v_assignment_record RECORD;
    v_found_assignment BOOLEAN := FALSE;
BEGIN
    -- Walk up the hierarchy: task → phase → milestone → project → global
    FOR v_current_level IN SELECT unnest(ARRAY['task'::hierarchy_level_enum, 'phase'::hierarchy_level_enum, 'milestone'::hierarchy_level_enum, 'project'::hierarchy_level_enum, 'global'::hierarchy_level_enum]) LOOP
        
        -- Look for assignments at current level
        FOR v_assignment_record IN
            SELECT 
                ta.id,
                ta.template_name,
                ta.hierarchy_level,
                ta.priority,
                ta.assignment_scope,
                ta.conditional_logic,
                ta.inheritance_enabled,
                ta.entity_type,
                ta.metadata
            FROM archon_template_assignments ta
            WHERE ta.hierarchy_level = v_current_level
              AND ta.is_active = true
              AND ta.inheritance_enabled = true
              AND (ta.effective_from <= NOW())
              AND (ta.effective_until IS NULL OR ta.effective_until > NOW())
              AND (
                  -- Global assignments apply to all
                  v_current_level = 'global'
                  -- Project assignments
                  OR (v_current_level = 'project' AND ta.entity_id = p_project_id)
                  -- Task-specific assignments
                  OR (v_current_level = 'task' AND ta.entity_id = p_entity_id)
                  -- Entity type matching
                  OR (ta.assignment_scope = 'specific_types' AND ta.entity_type = p_entity_type)
                  -- Conditional assignments (simplified - would need more complex logic)
                  OR (ta.assignment_scope = 'conditional')
              )
            ORDER BY ta.priority DESC, ta.created_at ASC
            LIMIT 1
        LOOP
            -- Add to resolution path
            v_resolution_path := v_resolution_path || jsonb_build_object(
                'level', v_current_level,
                'assignment_id', v_assignment_record.id,
                'template_name', v_assignment_record.template_name,
                'priority', v_assignment_record.priority
            );
            
            -- Return the first matching assignment
            template_name := v_assignment_record.template_name;
            hierarchy_level := v_assignment_record.hierarchy_level;
            assignment_id := v_assignment_record.id;
            priority := v_assignment_record.priority;
            resolution_path := v_resolution_path;
            
            v_found_assignment := TRUE;
            RETURN NEXT;
            EXIT; -- Exit the hierarchy loop
        END LOOP;
        
        -- If we found an assignment, stop walking up the hierarchy
        EXIT WHEN v_found_assignment;
    END LOOP;
    
    -- If no assignment found, return default
    IF NOT v_found_assignment THEN
        template_name := 'workflow_default';
        hierarchy_level := 'global';
        assignment_id := NULL;
        priority := 0;
        resolution_path := jsonb_build_array(jsonb_build_object(
            'level', 'global',
            'assignment_id', NULL,
            'template_name', 'workflow_default',
            'priority', 0,
            'source', 'default_fallback'
        ));
        RETURN NEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create function to cache template resolution
CREATE OR REPLACE FUNCTION cache_template_resolution(
    p_entity_id UUID,
    p_entity_type VARCHAR(50),
    p_hierarchy_level hierarchy_level_enum,
    p_context_hash VARCHAR(64),
    p_template_name VARCHAR(255),
    p_resolution_path JSONB,
    p_assignment_metadata JSONB DEFAULT '{}'::jsonb,
    p_cache_ttl_minutes INTEGER DEFAULT 30
) RETURNS UUID AS $$
DECLARE
    v_cache_id UUID;
    v_expires_at TIMESTAMPTZ;
BEGIN
    v_expires_at := NOW() + (p_cache_ttl_minutes || ' minutes')::INTERVAL;
    
    -- Insert or update cache entry
    INSERT INTO archon_template_assignment_cache (
        entity_id,
        entity_type,
        hierarchy_level,
        context_hash,
        resolved_template_name,
        resolution_path,
        assignment_metadata,
        expires_at
    ) VALUES (
        p_entity_id,
        p_entity_type,
        p_hierarchy_level,
        p_context_hash,
        p_template_name,
        p_resolution_path,
        p_assignment_metadata,
        v_expires_at
    )
    ON CONFLICT (entity_id, entity_type, hierarchy_level, context_hash)
    DO UPDATE SET
        resolved_template_name = EXCLUDED.resolved_template_name,
        resolution_path = EXCLUDED.resolution_path,
        assignment_metadata = EXCLUDED.assignment_metadata,
        expires_at = EXCLUDED.expires_at,
        cache_hit_count = archon_template_assignment_cache.cache_hit_count + 1,
        last_accessed_at = NOW(),
        updated_at = NOW()
    RETURNING id INTO v_cache_id;
    
    RETURN v_cache_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to invalidate cache
CREATE OR REPLACE FUNCTION invalidate_template_assignment_cache(
    p_entity_id UUID DEFAULT NULL,
    p_hierarchy_level hierarchy_level_enum DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM archon_template_assignment_cache
    WHERE (p_entity_id IS NULL OR entity_id = p_entity_id)
      AND (p_hierarchy_level IS NULL OR hierarchy_level = p_hierarchy_level);
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to invalidate cache when assignments change
CREATE OR REPLACE FUNCTION trigger_invalidate_assignment_cache()
RETURNS TRIGGER AS $$
BEGIN
    -- Invalidate cache for affected entities
    IF TG_OP = 'DELETE' THEN
        PERFORM invalidate_template_assignment_cache(OLD.entity_id, OLD.hierarchy_level);
        RETURN OLD;
    ELSE
        PERFORM invalidate_template_assignment_cache(NEW.entity_id, NEW.hierarchy_level);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_template_assignment_cache_invalidation ON archon_template_assignments;
CREATE TRIGGER trigger_template_assignment_cache_invalidation
    AFTER INSERT OR UPDATE OR DELETE ON archon_template_assignments
    FOR EACH ROW EXECUTE FUNCTION trigger_invalidate_assignment_cache();

-- Create cleanup function for expired cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_template_cache()
RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM archon_template_assignment_cache
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Insert some default template assignments
INSERT INTO archon_template_assignments (
    id, entity_id, template_name, hierarchy_level, assignment_scope, 
    priority, inheritance_enabled, is_active, created_by
) VALUES 
-- Global default assignment
(
    gen_random_uuid(),
    NULL, -- Global assignment
    'workflow_default',
    'global',
    'all',
    0,
    true,
    true,
    'system'
)
ON CONFLICT DO NOTHING;

-- Add helpful comments
COMMENT ON TABLE archon_template_assignment_cache IS 'Cache for resolved template assignments to improve performance';
COMMENT ON FUNCTION resolve_template_inheritance IS 'Resolves template inheritance hierarchy for an entity';
COMMENT ON FUNCTION cache_template_resolution IS 'Caches template resolution results for performance';
COMMENT ON FUNCTION invalidate_template_assignment_cache IS 'Invalidates cached template resolutions';
COMMENT ON FUNCTION cleanup_expired_template_cache IS 'Removes expired cache entries';

-- Verify the migration
SELECT 
    'Template assignment enhancement completed' as status,
    COUNT(*) as assignment_count
FROM archon_template_assignments;
