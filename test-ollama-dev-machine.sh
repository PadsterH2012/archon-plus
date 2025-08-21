#!/bin/bash
# Test Ollama Container on Dev Machine
# Run this on your development machine first

set -e

echo "🧪 TESTING OLLAMA ON DEV MACHINE"
echo "================================="

# Get dev machine IP
DEV_IP=$(hostname -I | awk '{print $1}')
echo "📍 Dev machine IP: $DEV_IP"

# Configuration
OLLAMA_PORT=11434
CONTAINER_NAME="test-ollama-embeddings"
VOLUME_NAME="test_ollama_models"

# Cleanup any existing test container
echo "🧹 Cleaning up existing test containers..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true
docker volume rm $VOLUME_NAME 2>/dev/null || true

# Create test volume
echo "💾 Creating test volume..."
docker volume create $VOLUME_NAME

# Deploy test container
echo "🚀 Deploying test Ollama container..."
docker run -d \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  -p $OLLAMA_PORT:11434 \
  -v $VOLUME_NAME:/root/.ollama \
  --cpus="2.0" \
  --memory="4g" \
  -e OLLAMA_HOST=0.0.0.0 \
  -e OLLAMA_ORIGINS=* \
  -e OLLAMA_NUM_PARALLEL=2 \
  -e OLLAMA_MAX_LOADED_MODELS=1 \
  -e OLLAMA_FLASH_ATTENTION=0 \
  -e OLLAMA_NUM_THREAD=4 \
  ollama/ollama:latest

# Wait for startup
echo "⏳ Waiting for Ollama to start..."
sleep 15

# Health check
echo "🏥 Testing Ollama health..."
for i in {1..30}; do
  if curl -s http://localhost:$OLLAMA_PORT/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is healthy!"
    break
  fi
  echo "Waiting... ($i/30)"
  sleep 2
done

# Pull test models
echo "📥 Pulling test embedding models..."
echo "⚡ Pulling nomic-embed-text (768 dims)..."
docker exec $CONTAINER_NAME ollama pull nomic-embed-text

echo "⚡ Pulling all-minilm (384 dims)..."
docker exec $CONTAINER_NAME ollama pull all-minilm

# List models
echo "📋 Available models:"
docker exec $CONTAINER_NAME ollama list

# Performance test
echo ""
echo "🏃 PERFORMANCE TESTING"
echo "======================"

# Test nomic-embed-text
echo "Testing nomic-embed-text (768 dims)..."
time curl -s -X POST http://localhost:$OLLAMA_PORT/api/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "input": "This is a test document for embedding generation performance testing on CPU."
  }' | jq '.embeddings[0] | length'

# Test all-minilm
echo "Testing all-minilm (384 dims)..."
time curl -s -X POST http://localhost:$OLLAMA_PORT/api/embed \
  -H "Content-Type: application/json" \
  -d '{
    "model": "all-minilm",
    "input": "This is a test document for embedding generation performance testing on CPU."
  }' | jq '.embeddings[0] | length'

# Resource usage
echo ""
echo "📊 RESOURCE USAGE"
echo "=================="
docker stats $CONTAINER_NAME --no-stream

echo ""
echo "🎉 TEST DEPLOYMENT COMPLETE!"
echo "============================="
echo "📍 Test Ollama URL: http://$DEV_IP:$OLLAMA_PORT"
echo "🔧 Container: $CONTAINER_NAME"
echo "💾 Volume: $VOLUME_NAME"
echo ""
echo "🧪 NEXT: Test with Archon DEV instance"
echo "Update your .env.dev with:"
echo "EMBEDDING_PROVIDER=ollama"
echo "EMBEDDING_MODEL=nomic-embed-text"
echo "EMBEDDING_DIMENSIONS=768"
echo "EMBEDDING_BASE_URL=http://$DEV_IP:$OLLAMA_PORT/v1"
echo ""
echo "🧹 To cleanup test:"
echo "docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME && docker volume rm $VOLUME_NAME"
