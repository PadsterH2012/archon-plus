# Archon Rollback Instructions

**Date:** 2025-08-25  
**Current Commit:** 3a85ee572945fa5670728bdf9ab97c098fb6b296  
**Target Production Commit:** 6cf4cc13b313fe17e6fab13929f0230df0dbd743  
**Backup Location:** `/mnt/network_repo/archon-prps/`

## ✅ Backup Completed Successfully

### 📋 What Was Backed Up (99 files, 1.1M total)

#### **PRPs (Product Requirement Prompts)**
- `agentic_workflow_framework_implementation.md`
- `database-abstraction-system.json`
- `database-migration-settings-system.json`
- `guvnor_prp.md`
- `homelab-database-migration.json`
- `issue_bug_management_system_prp.md`
- `multi_agent_work_assignments_prp.md`
- `project-import-analysis-system.json`
- `vscode_chat_bridge_prp.md`
- Plus PRP templates folder

#### **Critical Planning Documents**
- `PORT_AUDIT_AND_MIGRATION_PLAN.md`
- `DEPLOYMENT_STATUS.md`
- `HOMELAB_ARCHON_CONTEXT.md`
- `PRODUCTION_DATABASE_ALIGNMENT_PLAN.md`
- `agentic_workflow_framework_dynamic_plan.md`
- `jenkins_build.log`
- `container_logs.txt`
- All troubleshooting guides

#### **Architecture & Analysis**
- Complete `project_docs/architecture/` folder
- Complete `project_docs/analysis/` folder
- Complete `project_docs/components/` folder
- Complete `project_docs/workflows/` folder
- Template management architectural analysis
- Component analysis documents

#### **Documentation & Guides**
- Issues Kanban implementation plan
- Template injection operations guide
- Workflow API documentation
- Database schema documentation
- All troubleshooting guides

## 🔄 Rollback Process

### Step 1: Verify Current State
```bash
# Check current commit
git log --oneline -1
# Should show: 3a85ee5 (current unstable state)

# Check current branch
git branch --show-current
# Should show: main
```

### Step 2: Checkout Production Commit
```bash
# Checkout the stable production commit
git checkout 6cf4cc13b313fe17e6fab13929f0230df0dbd743

# Verify you're on the right commit
git log --oneline -1
# Should show: 6cf4cc1 feat: Jenkins CI/CD pipeline integration and production deployment setup
```

### Step 3: Create Rollback Branch
```bash
# Create a new branch from the stable commit
git checkout -b dev-rollback-to-production-stable

# Push the branch to remote
git push origin dev-rollback-to-production-stable
```

### Step 4: Verify Stable Configuration
```bash
# Check the stable port configuration
cat .env.production
# Should show stable production ports:
# ARCHON_SERVER_PORT=8181
# ARCHON_MCP_PORT=8051
# etc.

# Check docker-compose files exist and are stable
ls -la docker-compose*.yml
ls -la portainer-templates/
```

### Step 5: Deploy Stable Version to Dev
```bash
# Stop current dev services (if running)
docker service rm archon-dev_dev-archon-server archon-dev_dev-archon-mcp archon-dev_dev-archon-agents archon-dev_dev-archon-ui 2>/dev/null || true

# Deploy the stable version to dev environment
docker stack deploy -c portainer-templates/archon-saas-supabase-dev.yml archon-dev

# Wait for services to start
sleep 30

# Check service health
docker service ls | grep archon-dev
```

### Step 6: Verify Dev Environment Health
```bash
# Test basic connectivity
curl -s http://10.202.70.20:9181/health || echo "❌ Server not responding"
curl -s http://10.202.70.20:9051/health || echo "❌ MCP not responding"
curl -s http://10.202.70.20:4737 || echo "❌ UI not responding"

# Test working API endpoint
curl -s http://10.202.70.20:9181/api/projects | head -5 || echo "❌ API not working"
```

## 📊 Expected Stable State

### **Working Features (Production Proven)**
- ✅ Projects management
- ✅ Tasks management  
- ✅ Knowledge base and RAG
- ✅ MCP server and tools
- ✅ Document management
- ✅ Basic workflow system
- ✅ All 5 services healthy

### **Port Configuration (Stable)**
```bash
# Production ports (working):
ARCHON_SERVER_PORT=8181
ARCHON_MCP_PORT=8051
ARCHON_AGENTS_PORT=8052
ARCHON_UI_PORT=3737
ARCHON_EMBEDDINGS_PORT=8080

# Dev ports (should work after rollback):
ARCHON_SERVER_PORT=9181
ARCHON_MCP_PORT=9051
ARCHON_AGENTS_PORT=9052
ARCHON_UI_PORT=4737
ARCHON_EMBEDDINGS_PORT=9080
```

## 🔄 Restoring Planning Work

### After Rollback is Complete and Stable
```bash
# Copy back specific PRPs as needed
cp /mnt/network_repo/archon-prps/PRPs/[specific-prp].md ./PRPs/

# Copy back specific plans as needed
cp /mnt/network_repo/archon-prps/plans/[specific-plan].md ./

# Copy back architecture analysis as needed
cp -r /mnt/network_repo/archon-prps/project_docs/architecture/ ./project_docs/
```

## 🎯 Next Steps After Rollback

1. **Verify stable dev environment** (all services healthy)
2. **Test basic functionality** (projects, tasks, knowledge base)
3. **Choose ONE feature to fix** (recommend: Template Management)
4. **Follow working patterns** (REST API like projects/tasks)
5. **Avoid circular dependencies** (fix foundation first)

## 📞 Emergency Recovery

If rollback fails or causes issues:

```bash
# Return to current unstable state
git checkout main
git reset --hard 3a85ee572945fa5670728bdf9ab97c098fb6b296

# All planning work is safely backed up in:
# /mnt/network_repo/archon-prps/
```

## ✅ Backup Verification

To verify backup integrity:
```bash
# Check backup exists
ls -la /mnt/network_repo/archon-prps/

# Check file count
find /mnt/network_repo/archon-prps -type f | wc -l
# Should show: 99 files

# Check backup size
du -sh /mnt/network_repo/archon-prps
# Should show: 1.1M
```

---

**All PRPs and planning work is safely preserved. You can now proceed with the rollback to the stable production version.**
