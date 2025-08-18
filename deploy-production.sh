#!/bin/bash

# Archon Production Deployment Script
# This script deploys the Archon system using Harbor images and SaaS Supabase

set -e  # Exit on any error

echo "🚀 Archon Production Deployment Script"
echo "======================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy .env.production to .env and configure your settings:"
    echo "   cp .env.production .env"
    echo "   nano .env  # Edit with your Supabase credentials"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Harbor registry is accessible
echo "🔍 Checking Harbor registry access..."
echo "P0w3rPla72012@@" | docker login hl-harbor.techpad.uk --username jenkins --password-stdin
if [ $? -eq 0 ]; then
    echo "✅ Harbor registry access confirmed"
else
    echo "❌ Cannot login to Harbor registry. Trying to pull images anyway..."
fi

# Pull latest images
echo "📥 Pulling latest images from Harbor..."
docker-compose -f docker-compose.production.yml pull

# Stop existing containers if running
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down

# Start services
echo "🚀 Starting Archon services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

services=("archon-server:8181/api/health" "archon-mcp:8051/health" "archon-agents:8052/health" "archon-ui:3737" "archon-embeddings:8080/health")
all_healthy=true

for service in "${services[@]}"; do
    IFS=':' read -r name endpoint <<< "$service"
    echo -n "  Checking $name... "
    
    if curl -f -s "http://localhost:$endpoint" > /dev/null; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy"
        all_healthy=false
    fi
done

echo ""
echo "📊 Deployment Status:"
docker-compose -f docker-compose.production.yml ps

if [ "$all_healthy" = true ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo "🌐 Access your Archon system:"
    echo "   • Archon UI: http://localhost:3737"
    echo "   • Archon API: http://localhost:8181"
    echo "   • API Documentation: http://localhost:8181/docs"
    echo "   • Workflow System: http://localhost:3737/workflows"
    echo ""
    echo "📝 To view logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "🛑 To stop: docker-compose -f docker-compose.production.yml down"
else
    echo ""
    echo "⚠️  Some services are not healthy. Check logs:"
    echo "   docker-compose -f docker-compose.production.yml logs"
fi
