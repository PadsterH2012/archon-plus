# 🔧 Archon Port Configuration Audit & Migration Plan

## Executive Summary

This document provides a comprehensive audit of all port configurations throughout the Archon codebase and implements a systematic migration to the new **Internal/External Port Variable Architecture**. This migration will provide complete flexibility for port management across development and production environments.

## 🎯 Migration Objectives

- **Separate Internal/External Ports**: Clear distinction between container-internal and host-external ports
- **Environment Flexibility**: Easy port changes without affecting internal service communication
- **Backward Compatibility**: Maintain existing deployments during migration
- **Systematic Implementation**: File-by-file checklist with completion tracking

---

## 📊 Complete Port Inventory

### Current Port Usage Matrix

| Service | Dev External | Dev Internal | Prod External | Prod Internal | Status |
|---------|-------------|-------------|---------------|---------------|---------|
| Server | 9181 | 8181 | 8181 | 8181 | ⚠️ Mixed |
| MCP | 9051 | 8051/9051 | 8051 | 8051 | ❌ Inconsistent |
| Agents | 9052 | 8052 | 8052 | 8052 | ⚠️ Mixed |
| UI | 4737 | 5173 | 3737 | 5173 | ⚠️ Mixed |
| Embeddings | 9080 | 80/8080 | 8080 | 80/8080 | ⚠️ Mixed |
| PostgreSQL | 5433 | 5432 | 5432 | 5432 | ✅ Consistent |

### Port References by Category

#### 🔴 Critical Issues Found
- **MCP Service**: Inconsistent internal port usage (8051 vs 9051)
- **Health Checks**: Hardcoded port references in multiple files
- **Frontend Fallbacks**: Hardcoded port logic in API configuration
- **Documentation**: Outdated port references in README files

---

## 🏗️ New Variable Architecture

### Environment Variable Structure

```bash
# External Ports (for host access and port mapping)
ARCHON_SERVER_EXTERNAL_PORT=9181    # Dev: 9181, Prod: 8181
ARCHON_MCP_EXTERNAL_PORT=9051       # Dev: 9051, Prod: 8051
ARCHON_AGENTS_EXTERNAL_PORT=9052    # Dev: 9052, Prod: 8052
ARCHON_UI_EXTERNAL_PORT=4737        # Dev: 4737, Prod: 3737
ARCHON_EMBEDDINGS_EXTERNAL_PORT=9080 # Dev: 9080, Prod: 8080

# Internal Ports (for container-to-container communication)
ARCHON_SERVER_INTERNAL_PORT=8181    # Standard across all environments
ARCHON_MCP_INTERNAL_PORT=8051       # Standard across all environments  
ARCHON_AGENTS_INTERNAL_PORT=8052    # Standard across all environments
ARCHON_UI_INTERNAL_PORT=5173        # Standard across all environments
ARCHON_EMBEDDINGS_INTERNAL_PORT=80  # Standard across all environments
```

### Template Usage Pattern

```yaml
ports:
  - target: ${ARCHON_MCP_INTERNAL_PORT:-8051}
    published: ${ARCHON_MCP_EXTERNAL_PORT:-9051}
environment:
  - ARCHON_MCP_PORT=${ARCHON_MCP_INTERNAL_PORT:-8051}
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:${ARCHON_MCP_INTERNAL_PORT:-8051}/health"]
```

---

## 📋 Migration Checklist

### Phase 1: Environment Files ⏳

#### 1.1 Core Environment Files
- [ ] **`.env.example`** - Add new internal/external port variables
- [ ] **`portainer-templates/.env.dev`** - Update with new variable structure  
- [ ] **`portainer-templates/.env.prod`** - Update with new variable structure
- [ ] **`portainer-templates/.env.homelab`** - Update with new variable structure

#### 1.2 Validation
- [ ] Verify all new variables have appropriate defaults
- [ ] Ensure backward compatibility with existing variables
- [ ] Test environment variable inheritance

### Phase 2: Portainer Templates 🔄

#### 2.1 Development Templates
- [ ] **`portainer-templates/archon-saas-supabase-dev.yml`**
  - [ ] Line 32: `ARCHON_MCP_PORT=${ARCHON_MCP_INTERNAL_PORT:-8051}`
  - [ ] Line 107: `ARCHON_MCP_PORT=${ARCHON_MCP_INTERNAL_PORT:-8051}`
  - [ ] Line 119: `target: ${ARCHON_MCP_INTERNAL_PORT:-8051}`
  - [ ] Line 120: `published: ${ARCHON_MCP_EXTERNAL_PORT:-9051}`
  - [ ] Line 126: Health check port variable
  - [ ] Add server internal/external port separation
  - [ ] Add agents internal/external port separation
  - [ ] Add UI internal/external port separation

#### 2.2 Production Templates  
- [ ] **`portainer-templates/archon-saas-supabase-prod.yml`**
  - [ ] Update all port mappings to use internal/external variables
  - [ ] Ensure prod external ports (8xxx series)
  - [ ] Update health checks to use internal ports

#### 2.3 Legacy Templates
- [ ] **`portainer-templates/archon-homelab-native.yml`**
- [ ] **`deployment/swarm/archon-stack.yml`**
- [ ] **`deployment/swarm/archon-dev-stack.yml`**

### Phase 3: Docker Configuration 🐳

#### 3.1 Dockerfiles
- [ ] **`python/Dockerfile.server`**
  - [ ] Line 69: `ARG ARCHON_SERVER_INTERNAL_PORT=8181`
  - [ ] Line 71: `EXPOSE ${ARCHON_SERVER_INTERNAL_PORT}`
  - [ ] Line 75: Health check port variable

- [ ] **`python/Dockerfile.mcp`**
  - [ ] Line 37: `ARG ARCHON_MCP_INTERNAL_PORT=8051`
  - [ ] Line 39: `EXPOSE ${ARCHON_MCP_INTERNAL_PORT}`

- [ ] **`python/Dockerfile.agents`** (if exists)
- [ ] **`archon-ui-main/Dockerfile`** (if exists)

#### 3.2 Docker Compose Files
- [ ] **`docker-compose.yml`**
  - [ ] Line 9: Build args with internal port
  - [ ] Line 12: Port mapping with internal/external variables
  - [ ] Line 20-22: Environment variables using internal ports

- [ ] **`docker-compose.portainer.yml`**
- [ ] **`docker-compose.swarm.yml`**
- [ ] **`docker-compose.portainer-postgresql.yml`**

### Phase 4: Python Source Code 🐍

#### 4.1 Configuration Files
- [ ] **`python/src/server/config/config.py`**
  - [ ] Line 88: Update port resolution logic
  - [ ] Add internal port preference over external port

- [ ] **`python/src/server/config/service_discovery.py`**
  - [ ] Line 32-53: Update to use internal port variables
  - [ ] Ensure service-to-service communication uses internal ports

#### 4.2 Test Files
- [ ] **`python/tests/test_port_configuration.py`**
  - [ ] Line 61-71: Update test cases for new variable structure
  - [ ] Add tests for internal/external port separation

### Phase 5: Frontend Code 🎨

#### 5.1 Configuration Files
- [ ] **`archon-ui-main/src/config/api.ts`**
  - [ ] Line 19: Update to use external port variables
  - [ ] Line 29-37: Update fallback logic for new port structure

- [ ] **`archon-ui-main/vite.config.ts`**
  - [ ] Line 22: Use external port for proxy configuration
  - [ ] Line 285: Update proxy target to use external port
  - [ ] Line 314: Update environment variable definitions

#### 5.2 Component Files
- [ ] **`archon-ui-main/src/pages/MCPPage.tsx`**
  - [ ] Line 139: Update default port to use external port variable

#### 5.3 Test Files
- [ ] **`archon-ui-main/test/config/api.test.ts`**
  - [ ] Line 184-186: Update test cases for new variables

### Phase 6: Infrastructure & Scripts 🔧

#### 6.1 Health Check Scripts
- [ ] **`scripts/check_archon_health.sh`**
  - [ ] Line 111-117: Update port array to use external ports
  - [ ] Add environment variable reading for dynamic ports

#### 6.2 Deployment Scripts
- [ ] **`portainer-templates/deploy.sh`**
  - [ ] Line 266-267: Update port documentation
  - [ ] Line 61-65: Update port configuration function

- [ ] **`portainer-templates/pipeline-deploy.sh`**
  - [ ] Line 61-65: Update get_port_config function

#### 6.3 Nginx Configuration
- [ ] **`archon-ui-main/nginx.conf`**
  - [ ] Line 55: Update listen port to use variable
  - [ ] Line 87: Update proxy_pass to use internal port variable

### Phase 7: Documentation 📚

#### 7.1 README Files
- [ ] **`README.md`**
  - [ ] Line 249-267: Update port documentation
  - [ ] Add internal/external port explanation
  - [ ] Update environment variable examples

#### 7.2 Context Documentation
- [ ] **`HOMELAB_ARCHON_CONTEXT.md`**
  - [ ] Line 23-36: Update port mapping documentation

- [ ] **`QUICK_REFERENCE_CARD.md`**
  - [ ] Line 10-11: Update URL references

#### 7.3 Technical Documentation
- [ ] **`CLAUDE.md`**
  - [ ] Line 109-112: Update architecture port references

- [ ] **`add_tech_knowl_source_project.txt`**
  - [ ] Line 15-22: Update service port documentation

---

## 🧪 Validation & Testing Plan

### Testing Procedures

#### 1. Environment Variable Testing
```bash
# Test variable inheritance
docker-compose config | grep -E "ARCHON.*PORT"

# Verify port separation
echo "External: ${ARCHON_MCP_EXTERNAL_PORT}"
echo "Internal: ${ARCHON_MCP_INTERNAL_PORT}"
```

#### 2. Service Communication Testing
```bash
# Test internal service communication
curl http://dev-archon-mcp:${ARCHON_MCP_INTERNAL_PORT}/health

# Test external access
curl http://localhost:${ARCHON_MCP_EXTERNAL_PORT}/health
```

#### 3. Deployment Testing
- [ ] Deploy dev environment with new variables
- [ ] Verify all services start correctly
- [ ] Test service-to-service communication
- [ ] Validate external access on correct ports

### Rollback Procedures

#### Emergency Rollback
1. Revert environment files to previous versions
2. Restart affected services
3. Verify service communication restored

#### Gradual Rollback
1. Update individual services back to old configuration
2. Test each service independently
3. Document any issues encountered

---

## 📈 Success Criteria

### Completion Indicators
- [ ] All hardcoded ports replaced with variables
- [ ] Internal/external port separation implemented
- [ ] All services communicate correctly
- [ ] Documentation updated and accurate
- [ ] Tests pass with new configuration

### Performance Validation
- [ ] No increase in service startup time
- [ ] Service discovery works correctly
- [ ] Health checks pass consistently
- [ ] External access works on correct ports

---

## 🚀 Implementation Timeline

| Phase | Duration | Dependencies | Validation |
|-------|----------|--------------|------------|
| Phase 1: Environment Files | 1 day | None | Variable inheritance test |
| Phase 2: Portainer Templates | 2 days | Phase 1 | Template validation |
| Phase 3: Docker Configuration | 1 day | Phase 1 | Build test |
| Phase 4: Python Source | 2 days | Phase 1-3 | Unit tests |
| Phase 5: Frontend Code | 1 day | Phase 1-3 | Integration tests |
| Phase 6: Infrastructure | 1 day | Phase 1-5 | End-to-end tests |
| Phase 7: Documentation | 1 day | Phase 1-6 | Documentation review |

**Total Estimated Duration: 9 days**

---

## 📞 Support & Escalation

### Issue Resolution
- **Configuration Issues**: Check environment variable inheritance
- **Service Communication**: Verify internal port usage
- **External Access**: Verify external port mapping
- **Documentation**: Update affected documentation immediately

### Emergency Contacts
- **Primary**: Development team lead
- **Secondary**: Infrastructure team
- **Escalation**: Project manager

---

## 📁 Detailed File Analysis

### Critical Files Requiring Immediate Attention

#### 🔴 High Priority (Service Breaking)

**`portainer-templates/archon-saas-supabase-dev.yml`**
- **Issues**: Lines 32, 107 have hardcoded `ARCHON_MCP_PORT=9051`
- **Impact**: Prevents proper environment variable inheritance
- **Fix**: Change to `ARCHON_MCP_PORT=${ARCHON_MCP_INTERNAL_PORT:-8051}`
- **Status**: ❌ Blocking ARCH-3 resolution

**`python/src/server/config/service_discovery.py`**
- **Issues**: Lines 32-53 require all port environment variables
- **Impact**: Service startup failure if variables missing
- **Fix**: Add fallback logic for internal/external port variables
- **Status**: ⚠️ Needs update for new architecture

**`archon-ui-main/src/config/api.ts`**
- **Issues**: Lines 29-37 hardcoded fallback ports
- **Impact**: Frontend connects to wrong backend in some scenarios
- **Fix**: Use external port variables for API connections
- **Status**: ⚠️ Needs external port logic

#### 🟡 Medium Priority (Configuration Issues)

**`scripts/check_archon_health.sh`**
- **Issues**: Lines 111-117 hardcoded port array
- **Impact**: Health checks fail when ports change
- **Fix**: Read ports from environment variables
- **Status**: ⚠️ Static configuration

**`archon-ui-main/nginx.conf`**
- **Issues**: Lines 87, 100 hardcoded `archon-server:8181`
- **Impact**: Proxy fails if server port changes
- **Fix**: Use environment variable substitution
- **Status**: ⚠️ Hardcoded proxy configuration

**`python/Dockerfile.mcp`**
- **Issues**: Line 37 `ARG ARCHON_MCP_PORT` without default
- **Impact**: Build fails if argument not provided
- **Fix**: Add appropriate default or use internal port variable
- **Status**: ✅ Recently fixed, needs validation

#### 🟢 Low Priority (Documentation/Legacy)

**`README.md`**
- **Issues**: Lines 249-267 outdated port documentation
- **Impact**: User confusion about port configuration
- **Fix**: Update with new internal/external port architecture
- **Status**: 📝 Documentation update needed

**`deployment/swarm/archon-stack.yml`**
- **Issues**: Legacy deployment file with hardcoded ports
- **Impact**: Legacy deployments use old configuration
- **Fix**: Update to use new variable structure or mark as deprecated
- **Status**: 📝 Legacy file needs update

### Files with Correct Implementation

#### ✅ Already Following Best Practices

**`docker-compose.yml`**
- **Status**: ✅ Uses `${ARCHON_SERVER_PORT:-8181}` pattern correctly
- **Note**: Good example of proper variable usage

**`python/Dockerfile.server`**
- **Status**: ✅ Uses `ARG ARCHON_SERVER_PORT=8181` with default
- **Note**: Proper Dockerfile argument handling

**`docker-compose.portainer-postgresql.yml`**
- **Status**: ✅ Uses `${POSTGRES_PORT:-5433}:5432` pattern
- **Note**: Good example of external:internal port mapping

### Environment Variable Dependencies

#### Current Variable Usage
```bash
# Currently Used (Legacy)
ARCHON_SERVER_PORT=8181/9181
ARCHON_MCP_PORT=8051/9051
ARCHON_AGENTS_PORT=8052/9052
ARCHON_UI_PORT=3737/4737
ARCHON_EMBEDDINGS_PORT=8080/9080

# Frontend Specific
VITE_MCP_HOST=dev-archon-mcp
VITE_MCP_PORT=9051
VITE_MCP_NAME=archon-dev
```

#### New Variable Structure
```bash
# External Ports (Host Access)
ARCHON_SERVER_EXTERNAL_PORT=9181    # Dev
ARCHON_MCP_EXTERNAL_PORT=9051       # Dev
ARCHON_AGENTS_EXTERNAL_PORT=9052    # Dev
ARCHON_UI_EXTERNAL_PORT=4737        # Dev
ARCHON_EMBEDDINGS_EXTERNAL_PORT=9080 # Dev

# Internal Ports (Container Communication)
ARCHON_SERVER_INTERNAL_PORT=8181    # Standard
ARCHON_MCP_INTERNAL_PORT=8051       # Standard
ARCHON_AGENTS_INTERNAL_PORT=8052    # Standard
ARCHON_UI_INTERNAL_PORT=5173        # Standard
ARCHON_EMBEDDINGS_INTERNAL_PORT=80  # Standard

# Backward Compatibility (Deprecated)
ARCHON_SERVER_PORT=${ARCHON_SERVER_INTERNAL_PORT}
ARCHON_MCP_PORT=${ARCHON_MCP_INTERNAL_PORT}
ARCHON_AGENTS_PORT=${ARCHON_AGENTS_INTERNAL_PORT}
```

### Migration Risk Assessment

#### 🔴 High Risk Changes
- **Service Discovery**: Changes to `service_discovery.py` affect all services
- **Portainer Templates**: Incorrect template changes break deployments
- **Docker Port Mapping**: Wrong port mapping breaks external access

#### 🟡 Medium Risk Changes
- **Frontend Configuration**: API connection issues affect user experience
- **Health Checks**: Failed health checks trigger unnecessary restarts
- **Documentation**: Outdated docs cause user confusion

#### 🟢 Low Risk Changes
- **Test Files**: Test failures don't affect production
- **Legacy Files**: Deprecated files have minimal impact
- **Comments**: Documentation changes are safe

### Validation Commands

#### Pre-Migration Validation
```bash
# Check current port usage
grep -r "8051\|8181\|8052\|9051\|9181\|9052" --include="*.yml" --include="*.py" --include="*.ts"

# Verify environment variables
env | grep ARCHON.*PORT

# Test current service communication
curl http://dev-archon-mcp:8051/health
```

#### Post-Migration Validation
```bash
# Verify new variable structure
env | grep -E "ARCHON.*_(INTERNAL|EXTERNAL)_PORT"

# Test service communication with new ports
curl http://dev-archon-mcp:${ARCHON_MCP_INTERNAL_PORT}/health

# Test external access
curl http://localhost:${ARCHON_MCP_EXTERNAL_PORT}/health
```

---

*This migration plan ensures systematic, trackable progress through the entire Archon codebase while maintaining service availability and backward compatibility.*
