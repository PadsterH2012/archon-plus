# Homelab Archon Plus Context Document

**Purpose**: This document contains all critical context information for Archon Plus development and troubleshooting to avoid repeating setup details in every chat session.

---

## 🏠 **Homelab Infrastructure**

### **Server Details**
- **Primary Server IP**: `10.202.70.20`
- **Portainer Management**: `http://10.202.70.20:9000`
- **Admin Credentials**: `paddy / P0w3rPla72012@@`

### **Archon Service Architecture**
```
ARCHON-PROD (Production Instance)
├── Server Port: 8181
├── Purpose: Main knowledge base for building ARCHON-DEV
├── URL: http://10.202.70.20:8181
└── Status: Primary working instance

ARCHON-DEV (Development Instance)  
├── Server Port: 9181
├── Purpose: Testing new features and template injection
├── URL: http://10.202.70.20:9181
└── Status: Development/testing environment
```

### **Complete Port Mapping**
- **Archon-Prod Server**: `8181`
- **Archon-Dev Server**: `9181`
- **Archon MCP**: `9051`
- **Archon Agents**: `9052`
- **Archon UI**: `4737`
- **Archon Embeddings**: `9080`
- **Archon Docs**: `4838`

---

## 🔧 **Development Workflow & Rules**

### **Critical Workflow Principles**
1. **ARCHON-PROD is for building ARCHON-DEV** - Upload documentation to PROD to help develop DEV
2. **Never update archon-prod directly** - Use for reference and knowledge base only
3. **Use archon-dev for testing** - All new features and template injection changes
4. **Deploy via Jenkins webhook** - After successful build and testing
5. **Restart services in Portainer** - Don't redeploy, just restart containers

### **Container Management**
```bash
# SSH Access to homelab server
sshpass -p 'P0w3rPla72012@@' ssh paddy@10.202.70.20

# Container restart via Portainer (preferred method)
# Navigate to: http://10.202.70.20:9000
# Credentials: paddy / P0w3rPla72012@@
```

---

## 🗃️ **Database Management**

### **Development Database Reset**
- **Factory Reset Script**: `migration/factory_reset.sql`
- **Purpose**: Clean slate for development database issues
- **Usage**: Apply when dev database gets corrupted or needs reset
- **Architecture**: Standalone SQL scripts + modular base/migration scripts

### **Migration Strategy**
- **Base Scripts**: Core schema and initial data
- **Migration Scripts**: Incremental changes for deployment
- **Factory Reset**: Complete rebuild capability for development

---

## 🐛 **Known Issues & Solutions**

### **Knowledge Base Upload/Indexing Bug**
**Status**: **CONFIRMED UPSTREAM BUG** in original Archon repository

**Symptoms**:
- Upload API returns success but documents don't appear in search
- `crawled_pages` and `code_examples` tables remain empty
- RAG queries return no results despite successful uploads
- Only some uploads get indexed (inconsistent behavior)

**GitHub Issues in Original Repo**:
- **Issue #388**: "Should my crawled_pages and code_examples tables be empty?"
- **Issue #313**: "RAG query returns no results"  
- **Issue #302**: "No code examples being generated for RAG search"

**Root Cause**: Broken indexing pipeline between upload API and content processing

**Workarounds**:
1. Use UI upload method (slightly more reliable than script uploads)
2. Monitor original Archon repo for fixes
3. Focus on other features while this is being resolved upstream

### **Components Tab Crashes**
**Solution**: Implemented React Error Boundary
**Status**: Fixed with defensive programming patterns

### **Template Injection Deployment**
**Rule**: Always deploy template injection changes to ARCHON-DEV first
**Reason**: Avoid breaking production knowledge base functionality

---

## 🔍 **API Endpoints Reference**

### **Knowledge Base APIs**
```
Upload Document:    POST /api/documents/upload
Search Content:     POST /api/knowledge-items/search  
List Sources:       GET  /api/knowledge-items
Health Check:       GET  /api/health
```

### **Health Check URLs**
- **Prod Health**: `http://10.202.70.20:8181/api/health`
- **Dev Health**: `http://10.202.70.20:9181/api/health`

---

## 📁 **Project Structure & Codebase**

### **Archon Plus Origin**
- **Based on**: Fork/clone of original Archon project from `https://github.com/coleam00/Archon`
- **Customizations**: Significant modifications from original codebase
- **Architecture**: PRP (Product Requirement Prompt) driven development
- **Task Management**: Integrated task tracking with status workflows

### **Development Patterns**
- **Error Boundaries**: Implemented for React components
- **Defensive Programming**: Null checks, default values, graceful degradation
- **Version Control**: Automatic versioning for all project content
- **Task Lifecycle**: todo → doing → review → done

---

## 🎯 **Common Troubleshooting Commands**

### **Quick Verification Script**
```bash
# Run the homelab helper script
python3 homelab_helper.py

# Test knowledge base search
python3 test_knowledge_search.py

# Verify upload functionality  
python3 verify_archon_upload.py
```

### **Service Status Checks**
```bash
# Check if services are responding
curl http://10.202.70.20:8181/api/health  # Prod
curl http://10.202.70.20:9181/api/health  # Dev
```

---

## 🔐 **Security & Access**

### **Credentials Summary**
- **Homelab Server**: `paddy / P0w3rPla72012@@`
- **Portainer**: `paddy / P0w3rPla72012@@`
- **SSH Access**: `sshpass -p 'P0w3rPla72012@@' ssh paddy@10.202.70.20`

### **Network Access**
- **Internal Network**: `10.202.70.x` range
- **Primary Server**: `10.202.70.20`
- **All services accessible** via server IP with different ports

---

## 📝 **User Preferences & Patterns**

### **Terminology Preferences**
- **Task Groups**: "Workflows, Sequences, Actions"
- **Database Resets**: Prefer simple 'drop all' or factory reset scripts
- **Deployment**: Template injection to Dev instance, not production

### **Workflow Preferences**
- **Component Management**: Reusable workflow task groups
- **Task Injection**: Into agent task list rather than external processes
- **Service Management**: Restart via Portainer, not redeployment

---

## 🚀 **Quick Start for New Chat Sessions**

When starting a new chat session, reference this document and mention:

1. **"Check HOMELAB_ARCHON_CONTEXT.md for full setup details"**
2. **Current issue context**: What you're working on
3. **Specific section**: Point to relevant section of this document
4. **Known limitations**: Mention knowledge base upload bug if relevant

This eliminates the need to re-explain the entire homelab setup, service architecture, known issues, and development workflow every time.

---

**Last Updated**: 2025-08-21  
**Document Version**: 1.0  
**Maintained By**: Homelab Admin (Paddy)
