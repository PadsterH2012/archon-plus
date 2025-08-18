# Text Embeddings Inference (TEI) Integration

Archon now includes integrated support for [Hugging Face's Text Embeddings Inference (TEI)](https://github.com/huggingface/text-embeddings-inference), providing a high-performance, containerized embedding solution for complete data privacy and cost optimization.

## 🎯 Overview

TEI is a toolkit for deploying and serving text embeddings models. It provides:

- **High Performance**: Optimized inference with batching and pooling
- **Multiple Model Support**: Compatible with popular embedding models
- **OpenAI-Compatible API**: Drop-in replacement for OpenAI embeddings
- **Resource Efficient**: Optimized memory usage and CPU/GPU utilization
- **Production Ready**: Built for scale with health checks and monitoring

## 🚀 Quick Start

### 1. Enable TEI in Docker Compose

TEI is included by default in Archon's docker-compose setup:

```yaml
# docker-compose.yml includes:
archon-embeddings:
  image: ghcr.io/huggingface/text-embeddings-inference:cpu-1.8
  ports:
    - "8080:80"
  environment:
    - MODEL_ID=sentence-transformers/all-MiniLM-L6-v2
```

### 2. Configure Provider in UI

1. Navigate to **Settings** → **RAG Settings**
2. Set **Embedding Provider** to **TEI (Text Embeddings Inference)**
3. Configure **Base URL** (default: `http://archon-embeddings:80`)
4. Set **Model** (default: `sentence-transformers/all-MiniLM-L6-v2`)
5. Save settings

### 3. Test Integration

```bash
# Check TEI health
curl http://localhost:8080/health

# Test embedding creation
curl -X POST http://localhost:8080/embed \
  -H "Content-Type: application/json" \
  -d '{"inputs": ["Hello world"]}'
```

## ⚙️ Configuration

### Environment Variables

Configure TEI behavior through environment variables:

```env
# Model Configuration
EMBEDDING_MODEL_ID=sentence-transformers/all-MiniLM-L6-v2
ARCHON_EMBEDDINGS_PORT=8080

# Performance Tuning
TEI_MAX_CONCURRENT=512
TEI_MAX_BATCH_TOKENS=16384
TEI_MAX_BATCH_REQUESTS=32

# Resource Limits
TEI_MEMORY_LIMIT=2G
TEI_CPU_LIMIT=2
TEI_MEMORY_RESERVATION=1G
TEI_CPU_RESERVATION=1
```

### Supported Models

TEI supports various embedding models from Hugging Face:

#### Recommended Models

| Model | Dimensions | Use Case | Performance |
|-------|------------|----------|-------------|
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | General purpose, fast | ⭐⭐⭐⭐⭐ |
| `sentence-transformers/all-mpnet-base-v2` | 768 | High quality, balanced | ⭐⭐⭐⭐ |
| `sentence-transformers/paraphrase-MiniLM-L6-v2` | 384 | Paraphrase detection | ⭐⭐⭐⭐⭐ |
| `BAAI/bge-small-en-v1.5` | 384 | Multilingual, efficient | ⭐⭐⭐⭐ |
| `BAAI/bge-base-en-v1.5` | 768 | High quality English | ⭐⭐⭐ |

#### Model Selection Guidelines

- **Fast & Efficient**: `all-MiniLM-L6-v2` (384 dims)
- **Best Quality**: `all-mpnet-base-v2` (768 dims)
- **Multilingual**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Code Embeddings**: `microsoft/codebert-base`

### Provider Configuration

#### Primary Provider Setup

```yaml
# Use TEI as primary embedding provider
EMBEDDING_PROVIDER: "tei"
EMBEDDING_BASE_URL: "http://archon-embeddings:80"
EMBEDDING_MODEL: "sentence-transformers/all-MiniLM-L6-v2"
```

#### Fallback Configuration

```yaml
# Include TEI in fallback chain
EMBEDDING_FALLBACK_PROVIDERS: "openai,ollama,tei,local"
ENABLE_PROVIDER_FALLBACK: true
```

## 🔧 Advanced Configuration

### Custom Model Deployment

Deploy custom or fine-tuned models:

```yaml
archon-embeddings:
  image: ghcr.io/huggingface/text-embeddings-inference:cpu-1.8
  environment:
    - MODEL_ID=your-org/custom-embedding-model
    - HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}  # If model is private
  volumes:
    - ./models:/models  # Mount local model directory
```

### GPU Acceleration

For better performance with larger models:

```yaml
archon-embeddings:
  image: ghcr.io/huggingface/text-embeddings-inference:1.8
  environment:
    - MODEL_ID=sentence-transformers/all-mpnet-base-v2
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### Performance Optimization

#### Memory Optimization

```env
# Reduce memory usage for smaller deployments
TEI_MAX_CONCURRENT=128
TEI_MAX_BATCH_TOKENS=8192
TEI_MAX_BATCH_REQUESTS=16
TEI_MEMORY_LIMIT=1G
```

#### High Throughput Setup

```env
# Optimize for high throughput
TEI_MAX_CONCURRENT=1024
TEI_MAX_BATCH_TOKENS=32768
TEI_MAX_BATCH_REQUESTS=64
TEI_MEMORY_LIMIT=4G
TEI_CPU_LIMIT=4
```

## 🔍 Monitoring & Health Checks

### Health Endpoints

TEI provides several health and monitoring endpoints:

```bash
# Basic health check
curl http://localhost:8080/health

# Model information
curl http://localhost:8080/info

# Metrics (Prometheus format)
curl http://localhost:8080/metrics
```

### Archon Integration

Monitor TEI through Archon's provider health system:

```bash
# Check provider health via Archon API
curl http://localhost:8181/api/provider-health

# Reset provider health status
curl -X POST http://localhost:8181/api/provider-health/reset
```

### Logging

Configure logging levels for debugging:

```yaml
archon-embeddings:
  environment:
    - RUST_LOG=text_embeddings_inference=debug
```

## 🚀 Deployment Scenarios

### Development Setup

Minimal configuration for development:

```yaml
archon-embeddings:
  image: ghcr.io/huggingface/text-embeddings-inference:cpu-1.8
  ports:
    - "8080:80"
  environment:
    - MODEL_ID=sentence-transformers/all-MiniLM-L6-v2
```

### Production Setup

Optimized for production with resource limits:

```yaml
archon-embeddings:
  image: ghcr.io/huggingface/text-embeddings-inference:cpu-1.8
  ports:
    - "8080:80"
  environment:
    - MODEL_ID=sentence-transformers/all-mpnet-base-v2
    - MAX_CONCURRENT_REQUESTS=512
    - MAX_BATCH_TOKENS=16384
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '2'
      reservations:
        memory: 1G
        cpus: '1'
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:80/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### High Availability Setup

Multiple TEI instances with load balancing:

```yaml
archon-embeddings-1:
  image: ghcr.io/huggingface/text-embeddings-inference:cpu-1.8
  # ... configuration

archon-embeddings-2:
  image: ghcr.io/huggingface/text-embeddings-inference:cpu-1.8
  # ... configuration

nginx:
  image: nginx:alpine
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  ports:
    - "8080:80"
```

## 🔒 Security Considerations

### Network Security

- TEI runs on internal Docker network by default
- Only expose port 8080 if external access needed
- Use reverse proxy (Nginx/Traefik) for SSL termination

### Model Security

- Verify model checksums when downloading
- Use private registries for custom models
- Implement access controls for sensitive models

### Resource Limits

- Set appropriate memory and CPU limits
- Monitor resource usage in production
- Implement rate limiting if needed

## 🐛 Troubleshooting

### Common Issues

#### Model Download Failures

```bash
# Check model availability
curl -s https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2

# Verify network connectivity
docker exec archon-embeddings curl -s https://huggingface.co
```

#### Memory Issues

```bash
# Check container memory usage
docker stats archon-embeddings

# Reduce batch size
TEI_MAX_BATCH_TOKENS=8192
TEI_MAX_BATCH_REQUESTS=16
```

#### Performance Issues

```bash
# Monitor request latency
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8080/embed

# Check concurrent requests
docker logs archon-embeddings | grep "concurrent"
```

### Debug Commands

```bash
# View TEI logs
docker logs archon-embeddings -f

# Check model loading
docker exec archon-embeddings ls -la /tmp/

# Test embedding endpoint directly
curl -X POST http://localhost:8080/embed \
  -H "Content-Type: application/json" \
  -d '{"inputs": ["test"]}'
```

## 📚 Additional Resources

- [TEI GitHub Repository](https://github.com/huggingface/text-embeddings-inference)
- [Hugging Face Model Hub](https://huggingface.co/models?pipeline_tag=sentence-similarity)
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## 🤝 Contributing

To contribute to TEI integration:

1. Test with different models and configurations
2. Report performance benchmarks
3. Submit optimization suggestions
4. Improve documentation and examples

For issues specific to TEI integration, please include:
- Model ID and configuration
- Resource limits and usage
- Error logs and symptoms
- Performance metrics if applicable
