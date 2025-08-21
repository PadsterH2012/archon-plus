# Archon DEV Integration Testing Guide

## 🧪 **Phase 2: Test Ollama with Archon DEV**

After running the dev machine Ollama container, test integration with your Archon DEV instance.

---

## 🔧 **Step 1: Update DEV Configuration**

### **Backup Current Config**
```bash
# Backup current .env.dev
cp .env.dev .env.dev.backup.$(date +%Y%m%d_%H%M%S)
```

### **Update .env.dev for Testing**
```bash
# Replace DEV_MACHINE_IP with your actual dev machine IP
# Example: 192.168.1.100, 10.0.0.50, etc.

# Current (broken) config:
# EMBEDDING_PROVIDER=tei
# EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
# EMBEDDING_DIMENSIONS=384

# New test config:
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMENSIONS=768
EMBEDDING_BASE_URL=http://DEV_MACHINE_IP:11434/v1
```

---

## 🗃️ **Step 2: Database Schema Testing**

### **Option A: Test with New Database (Recommended)**
```sql
-- Create test database with correct dimensions
CREATE TABLE IF NOT EXISTS test_archon_crawled_pages (
    id BIGSERIAL PRIMARY KEY,
    url VARCHAR NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_id TEXT NOT NULL,
    embedding VECTOR(768),  -- 768 for nomic-embed-text
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(url, chunk_number)
);
```

### **Option B: Temporary Schema Change (Risky)**
```sql
-- ONLY if you want to test with existing DEV database
-- ⚠️ WARNING: This will lose existing embeddings!
ALTER TABLE archon_crawled_pages DROP COLUMN embedding;
ALTER TABLE archon_crawled_pages ADD COLUMN embedding VECTOR(768);
```

---

## 🚀 **Step 3: Restart and Test**

### **Restart Archon DEV Services**
```bash
# Via Portainer (recommended)
# Navigate to: http://10.202.70.20:9000
# Restart: archon-dev containers

# Or via Docker commands:
docker restart archon-dev-server
docker restart archon-dev-mcp
```

### **Test Upload and Indexing**
```bash
# 1. Upload a test document via UI
# Navigate to: http://10.202.70.20:9181
# Upload: One of your test documents

# 2. Monitor Ollama container logs
docker logs test-ollama-embeddings -f

# 3. Check if embeddings are generated
# You should see API calls to /api/embed in the logs

# 4. Test search after upload
# Try searching for content from your uploaded document
```

---

## 📊 **Step 4: Validation Tests**

### **Test 1: Embedding Generation**
```bash
# Direct API test
curl -X POST http://DEV_MACHINE_IP:11434/api/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "input": "Test document content for Archon knowledge base"
  }' | jq '.embeddings[0] | length'

# Should return: 768
```

### **Test 2: Database Verification**
```sql
-- Check if embeddings are being stored
SELECT 
    COUNT(*) as total_pages,
    COUNT(embedding) as pages_with_embeddings,
    AVG(array_length(embedding::float[], 1)) as avg_dimensions
FROM archon_crawled_pages;

-- Should show:
-- total_pages > 0
-- pages_with_embeddings > 0  
-- avg_dimensions = 768
```

### **Test 3: Search Functionality**
```bash
# Test RAG query via MCP tools
# Use: perform_rag_query_archon-dev
# Query: Content from your uploaded test document
# Should return: Relevant results with similarity scores
```

---

## 📈 **Step 5: Performance Monitoring**

### **Monitor Dev Machine Resources**
```bash
# CPU and memory usage
htop

# Docker container stats
docker stats test-ollama-embeddings

# Network traffic
netstat -i
```

### **Monitor Archon DEV Performance**
```bash
# Check Archon DEV logs for embedding generation times
docker logs archon-dev-server | grep -i embed

# Monitor response times
curl -w "@curl-format.txt" -s -o /dev/null http://10.202.70.20:9181/api/health
```

---

## ✅ **Success Criteria**

### **✅ Test Passes If:**
1. **Ollama container runs stable** on dev machine
2. **Embeddings generate successfully** (768 dimensions)
3. **Documents upload and get indexed** (non-zero embeddings in DB)
4. **Search returns relevant results** for uploaded content
5. **Performance is acceptable** (< 5 seconds for document processing)
6. **No memory/CPU issues** on dev machine

### **❌ Test Fails If:**
1. **Container crashes** or becomes unresponsive
2. **Dimension mismatch errors** in logs
3. **Documents upload but don't get indexed** (same old problem)
4. **Search returns empty results** for known content
5. **Performance is too slow** (> 30 seconds for simple documents)
6. **Dev machine becomes unstable** under load

---

## 🎯 **Decision Matrix**

### **If Tests PASS ✅:**
1. **Deploy to homelab server** using the production deployment script
2. **Update production database schema** to 768 dimensions
3. **Switch production config** to use homelab Ollama
4. **Migrate existing knowledge base** (re-upload and re-index)

### **If Tests FAIL ❌:**
1. **Try alternative model** (all-minilm with 384 dimensions)
2. **Adjust resource limits** (more CPU/memory)
3. **Debug specific issues** (check logs, network connectivity)
4. **Consider hybrid approach** (keep TEI for some models)

---

## 🔄 **Rollback Plan**

### **Quick Rollback (if needed):**
```bash
# 1. Restore original config
cp .env.dev.backup.YYYYMMDD_HHMMSS .env.dev

# 2. Restart Archon DEV
docker restart archon-dev-server

# 3. Stop test container
docker stop test-ollama-embeddings

# 4. Verify DEV is working
curl http://10.202.70.20:9181/api/health
```

---

## 📝 **Testing Checklist**

- [ ] Dev machine Ollama container deployed
- [ ] Models pulled successfully (nomic-embed-text, all-minilm)
- [ ] Performance tests completed
- [ ] .env.dev updated with Ollama config
- [ ] Database schema updated (if needed)
- [ ] Archon DEV services restarted
- [ ] Test document uploaded via UI
- [ ] Embedding generation confirmed in logs
- [ ] Database contains embeddings with correct dimensions
- [ ] Search functionality returns relevant results
- [ ] Performance is acceptable
- [ ] Resource usage is stable
- [ ] Ready for production deployment OR rollback completed

**This testing approach will give you confidence before making any changes to your production setup!** 🎯
