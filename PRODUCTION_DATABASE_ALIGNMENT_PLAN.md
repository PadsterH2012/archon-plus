# Production Database Alignment Plan
**Date**: 2025-08-22  
**Objective**: Align Production Supabase database with Development database while preserving project-specific tasks and data

## 🚨 CRITICAL ISSUES IDENTIFIED

### **Current Status Summary**
- **DEV Database**: ✅ Working (4/4 pages have embeddings, search functional)
- **PROD Database**: ❌ Broken (93/93 pages missing embeddings, search non-functional)
- **Schema Differences**: Multiple table structure inconsistencies
- **Missing Configuration**: No `archon_credentials` table in either database

### **Key Findings**
| Component | DEV Status | PROD Status | Issue |
|-----------|------------|-------------|-------|
| Embeddings | ✅ Working | ❌ All NULL | Embedding generation broken |
| Search | ✅ Functional | ❌ Non-functional | No embeddings to search |
| Templates | ✅ Modern schema | ❌ Legacy schema | Schema mismatch |
| Projects/Tasks | ✅ Current | ✅ Current | **PRESERVE THESE** |

## 📋 EXECUTION PLAN

### **PHASE 1: Pre-Migration Assessment (30 minutes)**

#### **1.1 Backup Critical Production Data**
```bash
# Export project-specific data that MUST be preserved
- archon_projects (all project definitions)
- archon_tasks (all task assignments and status)
- archon_document_versions (project documentation)
- archon_project_sources (project-specific knowledge)
```

#### **1.2 Document Current Production State**
```sql
-- Run these queries on PROD to document current state
SELECT COUNT(*) FROM archon_projects;
SELECT COUNT(*) FROM archon_tasks;
SELECT COUNT(*) FROM archon_sources;
SELECT COUNT(*) FROM archon_crawled_pages;
```

#### **1.3 Identify Schema Differences**
- Compare table structures between DEV and PROD
- Document missing tables in PROD
- Identify data that needs migration vs recreation

### **PHASE 2: Schema Alignment (45 minutes)**

#### **2.1 Create Missing Tables in Production**
```sql
-- Tables missing in PROD that exist in DEV:
- archon_components
- archon_component_dependencies  
- archon_template_definitions
- archon_credentials (missing in both - create new)
```

#### **2.2 Update Existing Table Structures**
```sql
-- Align table schemas where differences exist
- Update archon_template_* tables to match DEV structure
- Add any missing columns to existing tables
- Ensure vector extensions are properly configured
```

#### **2.3 Create archon_credentials Table**
```sql
-- New table needed for configuration storage
CREATE TABLE archon_credentials (
  id SERIAL PRIMARY KEY,
  category VARCHAR(100) NOT NULL,
  key VARCHAR(200) NOT NULL,
  value TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(category, key)
);
```

### **PHASE 3: Data Migration (60 minutes)**

#### **3.1 Preserve Critical Production Data**
- ✅ **KEEP**: All project data (`archon_projects`)
- ✅ **KEEP**: All task data (`archon_tasks`) 
- ✅ **KEEP**: All document versions (`archon_document_versions`)
- ✅ **KEEP**: Project-specific sources (`archon_project_sources`)

#### **3.2 Clean and Rebuild Broken Data**
- ❌ **REBUILD**: `archon_crawled_pages` (93 records with NULL embeddings)
- ❌ **REBUILD**: `archon_sources` (8 sources, may need re-processing)
- ✅ **MIGRATE**: Template components from DEV to PROD
- ✅ **CREATE**: Embedding provider configurations

#### **3.3 Configuration Migration**
```sql
-- Migrate key configurations to archon_credentials
INSERT INTO archon_credentials (category, key, value) VALUES
('embedding', 'EMBEDDING_PROVIDER', 'ollama'),
('embedding', 'EMBEDDING_MODEL', 'nomic-embed-text'),
('embedding', 'EMBEDDING_DIMENSIONS', '768'),
('embedding', 'EMBEDDING_BASE_URL', 'http://10.202.28.47:11434/v1');
```

### **PHASE 4: Embedding Regeneration (90 minutes)**

#### **4.1 Verify Embedding Service Connectivity**
```bash
# Test embedding service from production environment
curl -X POST http://10.202.28.47:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "test", "model": "nomic-embed-text"}'
```

#### **4.2 Clear Broken Embedding Data**
```sql
-- Remove all crawled pages with NULL embeddings
DELETE FROM archon_crawled_pages WHERE embedding IS NULL;
```

#### **4.3 Re-upload and Process Documents**
- Use Archon's document upload API to re-process sources
- Monitor embedding generation in real-time
- Verify embeddings are being created properly

#### **4.4 Validate Search Functionality**
```sql
-- Test vector search functions
SELECT * FROM match_archon_crawled_pages(
  query_embedding := (SELECT embedding FROM archon_crawled_pages LIMIT 1),
  match_count := 5
);
```

### **PHASE 5: Template System Alignment (45 minutes)**

#### **5.1 Migrate Template Components**
- Export template components from DEV
- Import to PROD with proper dependencies
- Verify template injection system works

#### **5.2 Update Template Configurations**
- Align template management settings
- Test template expansion functionality
- Verify MCP template tools work

### **PHASE 6: Validation and Testing (30 minutes)**

#### **6.1 Functional Testing**
- ✅ Search functionality works
- ✅ Document upload and embedding generation
- ✅ Template management system
- ✅ Project and task management preserved
- ✅ MCP tools functional

#### **6.2 Data Integrity Verification**
```sql
-- Verify critical data preserved
SELECT COUNT(*) as projects FROM archon_projects;
SELECT COUNT(*) as tasks FROM archon_tasks;
SELECT COUNT(*) as pages_with_embeddings FROM archon_crawled_pages WHERE embedding IS NOT NULL;
SELECT COUNT(*) as template_components FROM archon_template_components;
```

## 🎯 EXECUTION CHECKLIST

### **Pre-Execution Requirements**
- [ ] Access to both DEV and PROD Supabase databases
- [ ] Backup of critical production data
- [ ] Embedding service (Ollama) accessible from production
- [ ] Archon production services running

### **Critical Success Criteria**
- [ ] All project data preserved (archon_projects, archon_tasks)
- [ ] Search functionality restored in production
- [ ] Template management system working
- [ ] Embedding generation functional for new uploads
- [ ] Schema consistency between DEV and PROD

### **Rollback Plan**
- Restore from pre-migration backup if critical issues occur
- Preserve project/task data at all costs
- Document any data loss for recovery

## 🚨 WARNINGS AND PRECAUTIONS

1. **NEVER DELETE PROJECT DATA**: Projects and tasks contain critical work
2. **Test embedding service first**: Ensure connectivity before data migration
3. **Monitor disk space**: Embedding regeneration may require significant storage
4. **Backup before each phase**: Create restore points throughout process
5. **Validate incrementally**: Test each component before proceeding

## 📞 SUPPORT CONTACTS

- **Database Issues**: Supabase dashboard and SQL editor
- **Embedding Service**: Ollama at 10.202.28.47:11434
- **Archon Services**: Portainer at 10.202.70.20:9000

---
**Next Session Instructions**: Follow this plan step-by-step, validating each phase before proceeding. Focus on preserving project data while restoring search functionality.
