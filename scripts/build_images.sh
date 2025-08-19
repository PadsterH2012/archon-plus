#!/bin/bash

# Build Archon Docker Images Locally
echo "🔨 BUILDING ARCHON DOCKER IMAGES"
echo "================================"

# Build archon-server
echo "📦 Building archon-server..."
docker build -f python/Dockerfile.server -t hl-harbor.techpad.uk/archon/archon-server:latest python/

# Build archon-mcp
echo "📦 Building archon-mcp..."
docker build -f python/Dockerfile.mcp -t hl-harbor.techpad.uk/archon/archon-mcp:latest python/

# Build archon-agents
echo "📦 Building archon-agents..."
docker build -f python/Dockerfile.agents -t hl-harbor.techpad.uk/archon/archon-agents:latest python/

# Build archon-ui
echo "📦 Building archon-ui..."
docker build -f archon-ui-main/Dockerfile -t hl-harbor.techpad.uk/archon/archon-ui:latest archon-ui-main/

echo "✅ All images built successfully!"
echo ""
echo "📋 Built images:"
docker images | grep "hl-harbor.techpad.uk/archon"
