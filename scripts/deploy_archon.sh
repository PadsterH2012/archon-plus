#!/bin/bash

# Archon Deployment Script
echo "🚀 DEPLOYING ARCHON STACK"
echo "========================="

# Set environment variables
export SUPABASE_URL=https://aaoewgjxxeiyfpnlkkao.supabase.co
export SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhb2V3Z2p4eGVpeWZwbmxra2FvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTUxOTA4NywiZXhwIjoyMDcxMDk1MDg3fQ.VjTlpr6V6eT7tpMxadGc90-yoZtL3LOK-MBpiqKyEwI
export LOG_LEVEL=INFO

echo "✅ Environment variables set"

# Check if Docker Swarm is initialized
if ! docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then
    echo "🔧 Initializing Docker Swarm..."
    docker swarm init
fi

echo "✅ Docker Swarm is active"

# Deploy the stack
echo "🚀 Deploying Archon stack..."
docker stack deploy -c portainer-templates/archon-saas-supabase.yml archon

echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📋 Service Status:"
docker service ls

echo ""
echo "🎯 DEPLOYMENT COMPLETE"
echo "====================="
echo "Access URLs:"
echo "- Archon UI: http://localhost:3737"
echo "- Archon API: http://localhost:8181"
echo "- API Docs: http://localhost:8181/docs"
echo "- MCP Server: http://localhost:8051"
echo "- Agents Service: http://localhost:8052"
echo ""
echo "To check service logs:"
echo "  docker service logs archon_archon-server"
echo "  docker service logs archon_archon-ui"
echo ""
echo "To check service status:"
echo "  docker service ls"
echo "  docker service ps archon_archon-server"
