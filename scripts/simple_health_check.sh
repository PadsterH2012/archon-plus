#!/bin/bash

# Simple Archon Health Check (no external dependencies)
echo "🔍 ARCHON SIMPLE HEALTH CHECK"
echo "============================="
echo "Timestamp: $(date)"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK") echo -e "${GREEN}✅ $message${NC}" ;;
        "WARN") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️  $message${NC}" ;;
    esac
}

echo "🐳 DOCKER STATUS"
echo "---------------"
if docker --version >/dev/null 2>&1; then
    print_status "OK" "Docker is installed: $(docker --version)"
else
    print_status "ERROR" "Docker is not installed or not accessible"
    exit 1
fi

if docker info >/dev/null 2>&1; then
    print_status "OK" "Docker daemon is running"
else
    print_status "ERROR" "Docker daemon is not running"
    exit 1
fi

if docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then
    print_status "OK" "Docker Swarm is active"
else
    print_status "ERROR" "Docker Swarm is not active - run: docker swarm init"
fi
echo ""

echo "📋 DOCKER SERVICES"
echo "------------------"
if docker service ls >/dev/null 2>&1; then
    services=$(docker service ls --format "{{.Name}}" | grep archon || true)
    if [ -n "$services" ]; then
        print_status "OK" "Archon services found:"
        docker service ls | head -1
        docker service ls | grep archon
        echo ""
        
        # Check each service
        for service in $services; do
            replicas=$(docker service ls --filter name=$service --format "{{.Replicas}}")
            if [[ $replicas == "1/1" ]]; then
                print_status "OK" "$service: $replicas"
            else
                print_status "ERROR" "$service: $replicas (not ready)"
            fi
        done
    else
        print_status "ERROR" "No Archon services found"
        echo "Deploy with: docker stack deploy -c archon-saas-supabase.yml archon"
    fi
else
    print_status "ERROR" "Cannot access Docker services"
fi
echo ""

echo "🌐 NETWORKS"
echo "-----------"
networks=$(docker network ls | grep archon || true)
if [ -n "$networks" ]; then
    print_status "OK" "Archon networks found:"
    echo "$networks"
else
    print_status "WARN" "No Archon networks found"
fi
echo ""

echo "📊 RUNNING CONTAINERS"
echo "--------------------"
containers=$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep archon || true)
if [ -n "$containers" ]; then
    print_status "OK" "Running Archon containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -1
    echo "$containers"
else
    print_status "ERROR" "No running Archon containers found"
fi
echo ""

echo "🏥 BASIC CONNECTIVITY"
echo "---------------------"
# Test basic HTTP connectivity
if command -v curl >/dev/null 2>&1; then
    # Test archon-server
    if curl -s -f http://localhost:8181/health >/dev/null 2>&1; then
        print_status "OK" "archon-server (8181) is responding"
    else
        print_status "ERROR" "archon-server (8181) is not responding"
    fi
    
    # Test archon-ui
    if curl -s -f http://localhost:3737 >/dev/null 2>&1; then
        print_status "OK" "archon-ui (3737) is responding"
    else
        print_status "ERROR" "archon-ui (3737) is not responding"
    fi
    
    # Test archon-agents
    if curl -s -f http://localhost:8052/health >/dev/null 2>&1; then
        print_status "OK" "archon-agents (8052) is responding"
    else
        print_status "ERROR" "archon-agents (8052) is not responding"
    fi
else
    print_status "WARN" "curl not available - cannot test HTTP endpoints"
fi
echo ""

echo "📝 RECENT SERVICE LOGS"
echo "---------------------"
services=$(docker service ls --format "{{.Name}}" | grep archon || true)
for service in $services; do
    echo "--- $service (last 5 lines) ---"
    docker service logs --tail 5 $service 2>/dev/null || print_status "ERROR" "Cannot get logs for $service"
    echo ""
done

echo "🔧 TROUBLESHOOTING TIPS"
echo "----------------------"
echo "If services are not accessible:"
echo "1. Check service status: docker service ls"
echo "2. Check service logs: docker service logs <service-name>"
echo "3. Check if ports are bound: docker ps"
echo "4. Restart services: docker service update --force <service-name>"
echo "5. Redeploy stack: docker stack rm archon && docker stack deploy -c archon-saas-supabase.yml archon"
echo ""

echo "🎯 QUICK COMMANDS"
echo "----------------"
echo "View all services: docker service ls"
echo "View service logs: docker service logs archon_archon-server"
echo "Scale service: docker service scale archon_archon-server=1"
echo "Update service: docker service update --force archon_archon-server"
echo "Remove stack: docker stack rm archon"
echo "Deploy stack: docker stack deploy -c archon-saas-supabase.yml archon"
