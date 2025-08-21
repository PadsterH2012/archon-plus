# Template Injection System Operations Guide

This guide provides comprehensive operational procedures for managing the Template Injection System in production environments.

## Overview

The Template Injection System enhances agent task instructions by automatically expanding user tasks with standardized operational workflows while preserving the original user intent.

### Key Components
- **TemplateInjectionService**: Core expansion engine
- **Template Definitions**: Workflow templates (e.g., workflow_default)
- **Template Components**: Reusable instruction blocks
- **Feature Flags**: Controlled rollout mechanism
- **Caching Layer**: Performance optimization

## System Architecture

```
User Task → TaskService → TemplateInjectionService → Expanded Instructions
                ↓              ↓
         Feature Flags    Template Cache
                ↓              ↓
         Project Filter   Component Resolution
```

## Feature Flag Management

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `TEMPLATE_INJECTION_ENABLED` | Global enable/disable | `false` | `true` |
| `TEMPLATE_INJECTION_PROJECTS` | Comma-separated project IDs | `""` | `proj-1,proj-2` |
| `TEMPLATE_INJECTION_DEFAULT_TEMPLATE` | Default template name | `workflow_default` | `workflow_hotfix` |
| `TEMPLATE_INJECTION_CACHE_TTL` | Cache TTL in seconds | `1800` | `3600` |
| `TEMPLATE_INJECTION_MAX_EXPANSION_TIME` | Timeout in milliseconds | `100` | `200` |

### Feature Flag Hierarchy

1. **Explicit Override**: Task-level `enable_template_injection` parameter
2. **Project Filter**: `TEMPLATE_INJECTION_PROJECTS` environment variable
3. **Global Flag**: `TEMPLATE_INJECTION_ENABLED` environment variable

### Enabling Template Injection

```bash
# Enable globally
./scripts/enable_template_injection.sh --global

# Enable for specific projects
./scripts/enable_template_injection.sh project-1 project-2

# Enable with custom template
./scripts/enable_template_injection.sh --template workflow_hotfix project-urgent

# Dry run to preview changes
./scripts/enable_template_injection.sh --dry-run --global
```

### Disabling Template Injection

```bash
# Quick disable (recommended)
./scripts/rollback_template_injection.sh --type feature_flag

# Emergency disable
docker service update --env-add TEMPLATE_INJECTION_ENABLED=false archon-dev_dev-archon-server
```

## Monitoring and Alerting

### Key Metrics

| Metric | Target | Alert Threshold | Description |
|--------|--------|-----------------|-------------|
| Template Expansion Time | <100ms | >200ms | Time to expand template |
| Task Creation Overhead | <50ms | >100ms | Additional time for template injection |
| Cache Hit Ratio | >80% | <60% | Template cache efficiency |
| Error Rate | <1% | >5% | Template expansion failures |
| Memory Usage | <512MB | >1GB | Service memory consumption |

### Health Check Endpoints

```bash
# Service health
curl http://localhost:9181/api/health

# Template injection health
curl http://localhost:9181/api/template-injection/health

# Performance metrics
curl http://localhost:9181/api/metrics | grep template_
```

### Log Monitoring

**Important Log Patterns**:
```bash
# Template expansion errors
grep "template.*error" /var/log/archon/server.log

# Performance issues
grep "expansion.*timeout" /var/log/archon/server.log

# Cache performance
grep "template.*cache" /var/log/archon/server.log
```

**Sample Log Entries**:
```
INFO: Template expansion completed: template=workflow_default, time=45ms, success=true
WARN: Template expansion timeout: template=workflow_default, time=150ms
ERROR: Template not found: template=workflow_nonexistent, project=proj-123
```

## Performance Optimization

### Cache Management

**Cache Types**:
- **Template Cache**: 30-minute TTL for template definitions
- **Component Cache**: 15-minute TTL for template components
- **Expansion Cache**: 5-minute TTL for frequent expansions

**Cache Operations**:
```bash
# Clear template cache
curl -X POST http://localhost:9181/api/template-injection/cache/clear

# Cache statistics
curl http://localhost:9181/api/template-injection/cache/stats
```

### Performance Tuning

**Environment Variable Adjustments**:
```bash
# Increase cache TTL for stable environments
TEMPLATE_INJECTION_CACHE_TTL=3600

# Reduce timeout for faster failure detection
TEMPLATE_INJECTION_MAX_EXPANSION_TIME=50

# Disable caching for debugging
TEMPLATE_INJECTION_CACHE_ENABLED=false
```

## Troubleshooting

### Common Issues

#### 1. Template Expansion Timeouts

**Symptoms**: Tasks created with original descriptions, timeout errors in logs
**Causes**: Database performance, complex templates, network issues
**Solutions**:
```bash
# Increase timeout
docker service update --env-add TEMPLATE_INJECTION_MAX_EXPANSION_TIME=200 archon-dev_dev-archon-server

# Check database performance
# Run in Supabase SQL Editor:
SELECT COUNT(*) FROM archon_template_components WHERE is_active = true;

# Clear cache
curl -X POST http://localhost:9181/api/template-injection/cache/clear
```

#### 2. High Memory Usage

**Symptoms**: Service restarts, memory alerts, slow performance
**Causes**: Large templates, cache bloat, memory leaks
**Solutions**:
```bash
# Reduce cache TTL
docker service update --env-add TEMPLATE_INJECTION_CACHE_TTL=900 archon-dev_dev-archon-server

# Restart service
docker service update --force archon-dev_dev-archon-server

# Monitor memory usage
docker stats archon-dev_dev-archon-server
```

#### 3. Template Not Found Errors

**Symptoms**: Tasks created with original descriptions, template errors in logs
**Causes**: Missing templates, incorrect template names, database issues
**Solutions**:
```bash
# Verify template exists
curl http://localhost:9181/api/template-injection/templates/workflow_default

# Check database
# Run in Supabase SQL Editor:
SELECT name, is_active FROM archon_template_definitions WHERE name = 'workflow_default';

# Reseed templates
# Run: migration/seed_template_injection_data.sql
```

#### 4. Feature Flag Not Working

**Symptoms**: Template injection not enabling/disabling as expected
**Causes**: Environment variable issues, service restart needed, caching
**Solutions**:
```bash
# Check current environment
docker service inspect archon-dev_dev-archon-server --format '{{range .Spec.TaskTemplate.ContainerSpec.Env}}{{println .}}{{end}}' | grep TEMPLATE

# Update environment
docker service update --env-add TEMPLATE_INJECTION_ENABLED=true archon-dev_dev-archon-server

# Verify health
curl http://localhost:9181/api/template-injection/health
```

### Diagnostic Commands

```bash
# Service status
docker service ls | grep archon

# Service logs
docker service logs archon-dev_dev-archon-server --tail 100

# Resource usage
docker stats --no-stream

# Network connectivity
curl -I http://localhost:9181/api/health

# Database connectivity
# Test in Supabase SQL Editor:
SELECT 1 as connection_test;
```

## Backup and Recovery

### Data Backup

**Template Data Backup**:
```sql
-- Run in Supabase SQL Editor
CREATE TABLE backup_template_definitions AS 
SELECT * FROM archon_template_definitions;

CREATE TABLE backup_template_components AS 
SELECT * FROM archon_template_components;

CREATE TABLE backup_template_assignments AS 
SELECT * FROM archon_template_assignments;
```

**Configuration Backup**:
```bash
# Service configuration
docker service inspect archon-dev_dev-archon-server > server_config_backup.json

# Environment variables
docker service inspect archon-dev_dev-archon-server --format '{{range .Spec.TaskTemplate.ContainerSpec.Env}}{{println .}}{{end}}' > env_backup.txt
```

### Recovery Procedures

**Service Recovery**:
```bash
# Restart services
docker service update --force archon-dev_dev-archon-server
docker service update --force archon-dev_dev-archon-mcp

# Rollback to previous version
./scripts/rollback_template_injection.sh --type service
```

**Data Recovery**:
```sql
-- Restore from backup (run in Supabase SQL Editor)
INSERT INTO archon_template_definitions 
SELECT * FROM backup_template_definitions 
WHERE name NOT IN (SELECT name FROM archon_template_definitions);
```

## Maintenance Procedures

### Regular Maintenance

**Weekly Tasks**:
- Review performance metrics
- Check error rates and logs
- Verify cache performance
- Update monitoring dashboards

**Monthly Tasks**:
- Analyze template usage patterns
- Review and optimize templates
- Update documentation
- Performance testing

### Template Management

**Adding New Templates**:
1. Create template definition in database
2. Add required components
3. Test template expansion
4. Update documentation
5. Deploy to production

**Updating Existing Templates**:
1. Create backup of current template
2. Update template definition
3. Test with sample tasks
4. Monitor performance impact
5. Rollback if issues occur

### Capacity Planning

**Scaling Indicators**:
- Template expansion time >100ms consistently
- Cache hit ratio <60%
- Memory usage >80% of allocated
- Error rate >2%

**Scaling Actions**:
- Increase service memory allocation
- Add service replicas
- Optimize template complexity
- Implement database read replicas

## Security Considerations

### Access Control
- Template definitions stored in secure database
- Service-to-service authentication required
- Environment variables contain sensitive data
- Audit logging for template changes

### Data Protection
- Template metadata includes original descriptions
- Cache contains expanded instructions
- Logs may contain sensitive task information
- Backup data requires secure storage

### Compliance
- Template expansion preserves user intent
- Original descriptions always maintained
- Audit trail for all template usage
- Data retention policies apply

## Emergency Procedures

### Critical Issues

**Service Down**:
1. Check service health endpoints
2. Review service logs
3. Restart affected services
4. Escalate if not resolved in 15 minutes

**Performance Degradation**:
1. Disable template injection immediately
2. Investigate root cause
3. Implement temporary fixes
4. Plan permanent solution

**Data Corruption**:
1. Stop template injection services
2. Assess data integrity
3. Restore from backup if needed
4. Investigate corruption cause

### Escalation Contacts

- **Development Team**: Primary support for template logic issues
- **DevOps Team**: Infrastructure and deployment issues
- **Database Team**: Supabase and data issues
- **On-Call Engineer**: Critical production issues

## Change Management

### Deployment Process
1. Test in development environment
2. Create deployment plan
3. Schedule maintenance window
4. Execute deployment
5. Verify functionality
6. Monitor for issues

### Rollback Criteria
- Error rate >5%
- Performance degradation >50%
- Service unavailability >5 minutes
- Data integrity issues
- Security vulnerabilities

### Documentation Updates
- Update this operations guide
- Revise monitoring procedures
- Update troubleshooting steps
- Maintain change log

## Appendix

### Useful SQL Queries

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

-- Performance analysis
SELECT
  DATE_TRUNC('hour', created_at) as hour,
  COUNT(*) as total_tasks,
  COUNT(CASE WHEN template_metadata IS NOT NULL THEN 1 END) as template_tasks,
  AVG(CASE WHEN template_metadata IS NOT NULL
      THEN (template_metadata->>'expansion_time_ms')::float
      END) as avg_expansion_time
FROM archon_tasks
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;

-- Error analysis
SELECT
  template_metadata->>'template_name' as template_name,
  template_metadata->>'expansion_error' as error_message,
  COUNT(*) as error_count
FROM archon_tasks
WHERE template_metadata->>'expansion_failed' = 'true'
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY template_name, error_message;
```
