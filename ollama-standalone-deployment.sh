#!/bin/bash
# Standalone Ollama Container Deployment Script
# For homelab deployment at 10.202.70.20

set -e

echo "🐳 Deploying Ollama Container for Archon Plus"
echo "=============================================="

# Configuration
OLLAMA_PORT=11434
OLLAMA_CONTAINER_NAME="archon-ollama"
OLLAMA_VOLUME="archon_ollama_models"
OLLAMA_NETWORK="archon_network"

# Create network if it doesn't exist
echo "📡 Creating Docker network..."
docker network create $OLLAMA_NETWORK 2>/dev/null || echo "Network already exists"

# Create volume for model persistence
echo "💾 Creating volume for model storage..."
docker volume create $OLLAMA_VOLUME 2>/dev/null || echo "Volume already exists"

# Stop and remove existing container if it exists
echo "🛑 Stopping existing Ollama container..."
docker stop $OLLAMA_CONTAINER_NAME 2>/dev/null || true
docker rm $OLLAMA_CONTAINER_NAME 2>/dev/null || true

# Deploy Ollama container (CPU-optimized)
echo "🚀 Deploying CPU-optimized Ollama container..."
docker run -d \
  --name $OLLAMA_CONTAINER_NAME \
  --restart unless-stopped \
  --network $OLLAMA_NETWORK \
  -p $OLLAMA_PORT:11434 \
  -v $OLLAMA_VOLUME:/root/.ollama \
  --cpus="2.0" \
  --memory="4g" \
  -e OLLAMA_HOST=0.0.0.0 \
  -e OLLAMA_ORIGINS=* \
  -e OLLAMA_NUM_PARALLEL=2 \
  -e OLLAMA_MAX_LOADED_MODELS=1 \
  -e OLLAMA_FLASH_ATTENTION=0 \
  -e OLLAMA_NUM_THREAD=4 \
  ollama/ollama:latest

# Wait for container to be ready
echo "⏳ Waiting for Ollama to start..."
sleep 10

# Health check
echo "🏥 Checking Ollama health..."
for i in {1..30}; do
  if curl -s http://localhost:$OLLAMA_PORT/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is healthy!"
    break
  fi
  echo "Waiting for Ollama... ($i/30)"
  sleep 2
done

# Pull CPU-optimized embedding models
echo "📥 Pulling CPU-optimized embedding models..."
echo "⚡ Pulling nomic-embed-text (768 dims, best CPU performance)..."
docker exec $OLLAMA_CONTAINER_NAME ollama pull nomic-embed-text
echo "⚡ Pulling all-minilm (384 dims, fastest CPU performance)..."
docker exec $OLLAMA_CONTAINER_NAME ollama pull all-minilm
echo "ℹ️  Skipping mxbai-embed-large (too heavy for CPU-only deployment)"

# List available models
echo "📋 Available models:"
docker exec $OLLAMA_CONTAINER_NAME ollama list

echo ""
echo "🎉 Ollama deployment complete!"
echo "=============================================="
echo "📍 Ollama API URL: http://10.202.70.20:$OLLAMA_PORT"
echo "🔧 Container Name: $OLLAMA_CONTAINER_NAME"
echo "💾 Volume: $OLLAMA_VOLUME"
echo "🌐 Network: $OLLAMA_NETWORK"
echo ""
echo "📝 Update your Archon configuration:"
echo "EMBEDDING_PROVIDER=ollama"
echo "EMBEDDING_MODEL=nomic-embed-text"
echo "EMBEDDING_DIMENSIONS=768"
echo "EMBEDDING_BASE_URL=http://10.202.70.20:$OLLAMA_PORT/v1"
echo ""
echo "🧪 Test the API:"
echo "curl http://10.202.70.20:$OLLAMA_PORT/api/tags"
