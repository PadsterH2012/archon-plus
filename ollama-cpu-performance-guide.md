# Ollama CPU Performance Guide for Archon Plus

## 🖥️ **CPU-Only Deployment Considerations**

### **✅ Why CPU-Only Works for Embeddings:**
- **Embedding models are smaller** than LLMs (23M-334M vs 7B+ parameters)
- **Inference is faster** - embeddings don't require iterative generation
- **Memory efficient** - can run comfortably in 2-4GB RAM
- **Batch processing** - can process multiple texts efficiently

---

## 📊 **Model Performance on CPU**

### **Recommended Models (CPU-Optimized)**

| Model | Parameters | Dimensions | CPU Performance | Memory Usage | Best For |
|-------|------------|------------|-----------------|--------------|----------|
| **all-minilm** | 23M | 384 | ⭐⭐⭐⭐⭐ Excellent | ~500MB | Fast processing |
| **nomic-embed-text** | 137M | 768 | ⭐⭐⭐⭐ Very Good | ~1GB | Best quality/speed balance |
| **mxbai-embed-large** | 334M | 1024 | ⭐⭐⭐ Good | ~2GB | High quality (slower) |

### **Performance Benchmarks (Estimated)**
*Based on typical homelab server (4-8 CPU cores, 16GB RAM)*

| Model | Single Text | Batch (10 texts) | Batch (100 texts) |
|-------|-------------|-------------------|-------------------|
| **all-minilm** | ~50ms | ~200ms | ~1.5s |
| **nomic-embed-text** | ~150ms | ~600ms | ~4s |
| **mxbai-embed-large** | ~400ms | ~1.5s | ~12s |

---

## ⚙️ **CPU Optimization Settings**

### **Container Resource Limits**
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Don't overwhelm the server
      memory: 4G       # Sufficient for embedding models
    reservations:
      cpus: '1.0'      # Guarantee minimum resources
      memory: 2G
```

### **Ollama Environment Variables**
```bash
OLLAMA_NUM_PARALLEL=2        # Reduce concurrent requests
OLLAMA_MAX_LOADED_MODELS=1   # Keep only one model in memory
OLLAMA_FLASH_ATTENTION=0     # Disable GPU-specific optimizations
OLLAMA_NUM_THREAD=4          # Match your CPU cores
```

### **System-Level Optimizations**
```bash
# Check CPU cores
nproc

# Monitor CPU usage during embedding generation
htop

# Check memory usage
free -h

# Monitor container resources
docker stats archon-ollama-embeddings
```

---

## 🎯 **Recommended Configuration for Your Homelab**

### **Primary Choice: nomic-embed-text**
```bash
# Configuration for .env files
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMENSIONS=768
EMBEDDING_BASE_URL=http://10.202.70.20:11434/v1

# Why this choice:
# ✅ 768 dimensions (good quality)
# ✅ Excellent CPU performance
# ✅ 8192 token context (handles long documents)
# ✅ Well-tested and reliable
```

### **Alternative: all-minilm (if speed is critical)**
```bash
# Fastest option
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=all-minilm
EMBEDDING_DIMENSIONS=384
EMBEDDING_BASE_URL=http://10.202.70.20:11434/v1

# Why this choice:
# ✅ Fastest CPU performance
# ✅ Smallest memory footprint
# ✅ Good enough quality for most use cases
# ⚠️ Lower dimensions (384 vs 768)
```

---

## 🚀 **Deployment Steps for Your Homelab**

### **Step 1: Deploy Container**
```bash
# Make the script executable
chmod +x ollama-standalone-deployment.sh

# Run deployment
./ollama-standalone-deployment.sh
```

### **Step 2: Verify Deployment**
```bash
# Check container status
docker ps | grep ollama

# Test API
curl http://10.202.70.20:11434/api/tags

# Test embedding generation
curl -X POST http://10.202.70.20:11434/api/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "input": "This is a test document for embedding generation"
  }'
```

### **Step 3: Update Archon Configuration**
```bash
# Update .env.production
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMENSIONS=768
EMBEDDING_BASE_URL=http://10.202.70.20:11434/v1

# Update database schema (if needed)
# ALTER TABLE archon_crawled_pages DROP COLUMN embedding;
# ALTER TABLE archon_crawled_pages ADD COLUMN embedding VECTOR(768);
```

### **Step 4: Restart Archon Services**
```bash
# Via Portainer or direct Docker commands
docker restart archon-prod-server
docker restart archon-dev-server
```

---

## 🔧 **Troubleshooting CPU Performance**

### **If Embeddings Are Too Slow:**
1. **Switch to all-minilm** (384 dimensions)
2. **Reduce OLLAMA_NUM_PARALLEL** to 1
3. **Increase container CPU limit** to 3.0 or 4.0
4. **Monitor system load** with `htop`

### **If Memory Issues Occur:**
1. **Increase container memory limit** to 6G or 8G
2. **Ensure OLLAMA_MAX_LOADED_MODELS=1**
3. **Monitor with** `docker stats`

### **If Container Fails to Start:**
1. **Check Docker logs**: `docker logs archon-ollama-embeddings`
2. **Verify port availability**: `netstat -tlnp | grep 11434`
3. **Check disk space**: `df -h`

---

## 📈 **Expected Performance**

### **For Your Homelab Setup:**
- **Document Upload**: 5-10 seconds for typical documents
- **Search Queries**: 200-500ms response time
- **Batch Processing**: 50-100 documents per minute
- **Memory Usage**: 2-4GB for embedding service
- **CPU Usage**: 20-50% during active processing

### **This Should Easily Handle:**
- ✅ Your homelab documentation uploads
- ✅ Real-time search queries
- ✅ Multiple concurrent users
- ✅ Background document processing

**Bottom Line**: CPU-only Ollama deployment will work perfectly for your Archon Plus knowledge base needs! 🎯
