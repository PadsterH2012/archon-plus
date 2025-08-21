# Template Injection System Deployment Guide

This guide provides step-by-step instructions for deploying the Template Injection System to the Archon development environment with feature flags for controlled rollout.

## Overview

The Template Injection System deployment follows a phased approach:
1. **Database Migration** - Deploy schema and seed data
2. **Feature Flag Configuration** - Set up controlled rollout
3. **Service Deployment** - Deploy updated services
4. **Pilot Testing** - Enable for selected projects
5. **Monitoring & Validation** - Track performance and errors

## Prerequisites

- Access to Supabase project: `homelab-archon-plus-b` (gifepwbtqkhiblgjgabq)
- Docker Swarm environment configured
- Harbor registry access for image deployment
- Monitoring and alerting systems configured

## Phase 1: Database Migration

### 1.1 Deploy Template Injection Schema

**Target Environment**: Development (`homelab-archon-plus-b`)

```bash
# Connect to Supabase SQL Editor
# URL: https://supabase.com/dashboard/project/gifepwbtqkhiblgjgabq/sql

# Run the following migrations in order:
```

**Migration Scripts to Execute**:

1. **Template Injection Schema**:
   ```sql
   -- Run: migration/add_template_injection_schema.sql
   -- Creates: archon_template_definitions, archon_template_components, archon_template_assignments
   ```

2. **Seed Default Templates**:
   ```sql
   -- Run: migration/seed_template_injection_data.sql
   -- Creates: Default workflow template and components
   ```

### 1.2 Verify Migration Success

```sql
-- Verify tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'archon_template_%';

-- Verify default template exists
SELECT name, title, is_active FROM archon_template_definitions 
WHERE name = 'workflow_default';

-- Verify components exist
SELECT COUNT(*) as component_count FROM archon_template_components 
WHERE is_active = true;
```

**Expected Results**:
- 3 new tables: `archon_template_definitions`, `archon_template_components`, `archon_template_assignments`
- 1 default template: `workflow_default`
- 8+ active components

### 1.3 Create Rollback Plan

```sql
-- Rollback script (if needed)
DROP TABLE IF EXISTS archon_template_assignments CASCADE;
DROP TABLE IF EXISTS archon_template_components CASCADE;
DROP TABLE IF EXISTS archon_template_definitions CASCADE;
DROP TYPE IF EXISTS template_definition_type CASCADE;
DROP TYPE IF EXISTS template_component_type CASCADE;
DROP TYPE IF EXISTS template_injection_level CASCADE;
DROP TYPE IF EXISTS hierarchy_type CASCADE;
```

## Phase 2: Feature Flag Configuration

### 2.1 Environment Variables Setup

**Development Environment Configuration**:

```bash
# Template Injection Feature Flags
TEMPLATE_INJECTION_ENABLED=false                    # Start disabled
TEMPLATE_INJECTION_PROJECTS=""                      # No project restrictions initially
TEMPLATE_INJECTION_DEFAULT_TEMPLATE=workflow_default
TEMPLATE_INJECTION_CACHE_TTL=1800                   # 30 minutes
TEMPLATE_INJECTION_MAX_EXPANSION_TIME=100           # 100ms timeout
```

### 2.2 Update Docker Compose Configuration

**File**: `portainer-templates/archon-saas-supabase-dev.yml`

Add to all service environment sections:
```yaml
environment:
  # Existing environment variables...
  
  # Template Injection Configuration
  - TEMPLATE_INJECTION_ENABLED=${TEMPLATE_INJECTION_ENABLED:-false}
  - TEMPLATE_INJECTION_PROJECTS=${TEMPLATE_INJECTION_PROJECTS:-}
  - TEMPLATE_INJECTION_DEFAULT_TEMPLATE=${TEMPLATE_INJECTION_DEFAULT_TEMPLATE:-workflow_default}
  - TEMPLATE_INJECTION_CACHE_TTL=${TEMPLATE_INJECTION_CACHE_TTL:-1800}
  - TEMPLATE_INJECTION_MAX_EXPANSION_TIME=${TEMPLATE_INJECTION_MAX_EXPANSION_TIME:-100}
```

### 2.3 Create Environment File

**File**: `.env.template-injection-dev`

```bash
# Template Injection Development Configuration
# Copy to .env and customize for your environment

# Supabase Configuration (Development)
SUPABASE_URL=https://gifepwbtqkhiblgjgabq.supabase.co
SUPABASE_SERVICE_KEY=your_dev_service_key_here

# Template Injection Feature Flags
TEMPLATE_INJECTION_ENABLED=false
TEMPLATE_INJECTION_PROJECTS=
TEMPLATE_INJECTION_DEFAULT_TEMPLATE=workflow_default
TEMPLATE_INJECTION_CACHE_TTL=1800
TEMPLATE_INJECTION_MAX_EXPANSION_TIME=100

# Development Port Configuration
ARCHON_SERVER_PORT=9181
ARCHON_MCP_PORT=9051
ARCHON_AGENTS_PORT=9052
ARCHON_UI_PORT=4737
ARCHON_EMBEDDINGS_PORT=9080

# Logging
LOG_LEVEL=DEBUG
HOST=localhost
```

## Phase 3: Service Deployment

### 3.1 Build and Push Updated Images

```bash
# Build updated images with template injection support
cd /path/to/archon-plus

# Build server image
docker build -t hl-harbor.techpad.uk/archon/archon-server:template-injection-v1 \
  -f python/Dockerfile.server python/

# Build MCP image  
docker build -t hl-harbor.techpad.uk/archon/archon-mcp:template-injection-v1 \
  -f python/Dockerfile.mcp python/

# Push to registry
docker push hl-harbor.techpad.uk/archon/archon-server:template-injection-v1
docker push hl-harbor.techpad.uk/archon/archon-mcp:template-injection-v1
```

### 3.2 Deploy to Development Environment

```bash
# Load environment variables
source .env.template-injection-dev

# Deploy development stack
./portainer-templates/deploy.sh saas-dev

# Verify deployment
docker service ls | grep archon-dev
```

### 3.3 Health Check Verification

```bash
# Check service health
curl -f http://localhost:9181/api/health
curl -f http://localhost:9051/health

# Check template injection service availability
curl -X POST http://localhost:9181/api/template-injection/health \
  -H "Content-Type: application/json"
```

**Expected Response**:
```json
{
  "status": "healthy",
  "template_injection_enabled": false,
  "template_service_available": true,
  "default_template": "workflow_default",
  "cache_status": "active"
}
```

## Phase 4: Pilot Project Setup

### 4.1 Select Pilot Projects

**Recommended Pilot Projects**:
1. **Internal Development Project** - Low risk, high visibility
2. **Template Testing Project** - Dedicated testing environment

### 4.2 Enable Template Injection for Pilot

```bash
# Update environment variables
export TEMPLATE_INJECTION_ENABLED=true
export TEMPLATE_INJECTION_PROJECTS="pilot-project-1,pilot-project-2"

# Restart services to pick up new configuration
docker service update --env-add TEMPLATE_INJECTION_ENABLED=true archon-dev_dev-archon-server
docker service update --env-add TEMPLATE_INJECTION_PROJECTS="pilot-project-1,pilot-project-2" archon-dev_dev-archon-server
```

### 4.3 Test Template Injection

```bash
# Test template expansion via MCP tool
curl -X POST http://localhost:9051/tools/manage_task \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create",
    "project_id": "pilot-project-1",
    "title": "Test Template Injection",
    "description": "Create a simple API endpoint",
    "template_name": "workflow_default",
    "enable_template_injection": true
  }'
```

**Expected Behavior**:
- Task created with expanded description
- Original description preserved in template_metadata
- Expansion time < 100ms
- No errors in service logs

## Phase 5: Monitoring and Validation

### 5.1 Performance Monitoring

**Key Metrics to Track**:
- Template expansion time (target: <100ms)
- Task creation overhead (target: <50ms)
- Template cache hit ratio (target: >80%)
- Error rates (target: <1%)

**Monitoring Commands**:
```bash
# Check service logs
docker service logs archon-dev_dev-archon-server --tail 100

# Monitor performance metrics
curl http://localhost:9181/api/metrics | grep template_

# Check database performance
# Run in Supabase SQL Editor:
SELECT 
  COUNT(*) as total_tasks,
  COUNT(CASE WHEN template_metadata IS NOT NULL THEN 1 END) as template_tasks,
  AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_processing_time
FROM archon_tasks 
WHERE created_at > NOW() - INTERVAL '1 hour';
```

### 5.2 Error Monitoring

**Log Patterns to Watch**:
```bash
# Template expansion errors
docker service logs archon-dev_dev-archon-server 2>&1 | grep "template.*error"

# Performance issues
docker service logs archon-dev_dev-archon-server 2>&1 | grep "expansion.*timeout"

# Database errors
docker service logs archon-dev_dev-archon-server 2>&1 | grep "template.*database"
```

### 5.3 Usage Analytics

```sql
-- Template usage statistics
SELECT 
  template_metadata->>'template_name' as template_name,
  COUNT(*) as usage_count,
  AVG((template_metadata->>'expansion_time_ms')::float) as avg_expansion_time
FROM archon_tasks 
WHERE template_metadata IS NOT NULL
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY template_metadata->>'template_name';

-- Agent task completion rates
SELECT 
  assignee,
  COUNT(*) as total_tasks,
  COUNT(CASE WHEN status = 'done' THEN 1 END) as completed_tasks,
  COUNT(CASE WHEN template_metadata IS NOT NULL THEN 1 END) as template_tasks
FROM archon_tasks 
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY assignee;
```

## Rollback Procedures

### Emergency Rollback

```bash
# Disable template injection immediately
docker service update --env-add TEMPLATE_INJECTION_ENABLED=false archon-dev_dev-archon-server

# Verify rollback
curl http://localhost:9181/api/template-injection/health
```

### Full Rollback

```bash
# 1. Disable feature flags
export TEMPLATE_INJECTION_ENABLED=false
export TEMPLATE_INJECTION_PROJECTS=""

# 2. Restart services
docker service update archon-dev_dev-archon-server
docker service update archon-dev_dev-archon-mcp

# 3. Rollback database (if necessary)
# Run rollback SQL script in Supabase SQL Editor

# 4. Deploy previous image versions
docker service update --image hl-harbor.techpad.uk/archon/archon-server:previous-version archon-dev_dev-archon-server
```

## Success Criteria

### Deployment Success
- ✅ All services start without errors
- ✅ Health checks pass
- ✅ Template injection service responds correctly
- ✅ Database migrations complete successfully

### Performance Success
- ✅ Template expansion < 100ms average
- ✅ Task creation overhead < 50ms
- ✅ Cache hit ratio > 80%
- ✅ Error rate < 1%

### Functional Success
- ✅ Template injection works for pilot projects
- ✅ Original task descriptions preserved
- ✅ Expanded instructions are coherent
- ✅ Feature flags control access correctly

## Next Steps

After successful pilot deployment:
1. **Gradual Rollout** - Enable for additional projects
2. **Performance Optimization** - Based on monitoring data
3. **Template Enhancement** - Add additional workflow templates
4. **Production Deployment** - Deploy to main production environment

## Support and Troubleshooting

### Common Issues

**Issue**: Template expansion timeouts
**Solution**: Check database performance, increase `TEMPLATE_INJECTION_MAX_EXPANSION_TIME`

**Issue**: High memory usage
**Solution**: Reduce cache TTL, monitor component complexity

**Issue**: Template not found errors
**Solution**: Verify seed data migration, check template names

### Contact Information

- **Development Team**: Archon Development Team
- **Database Issues**: Supabase Support
- **Infrastructure**: DevOps Team
- **Monitoring**: Operations Team
