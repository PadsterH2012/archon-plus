#!/bin/bash

# Archon Health Check Script
# This script checks the health of all Archon services in Docker Swarm

set -e

echo "🔍 ARCHON HEALTH CHECK DIAGNOSTIC"
echo "=================================="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker Swarm is active
check_swarm_status() {
    echo "🐳 DOCKER SWARM STATUS"
    echo "----------------------"
    
    if docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then
        print_status "OK" "Docker Swarm is active"
        docker node ls
    else
        print_status "ERROR" "Docker Swarm is not active"
        echo "Run: docker swarm init"
        return 1
    fi
    echo ""
}

# Check Docker Swarm services
check_swarm_services() {
    echo "📋 DOCKER SWARM SERVICES"
    echo "------------------------"
    
    if docker service ls | grep -q "archon"; then
        print_status "INFO" "Archon services found:"
        docker service ls | grep archon
        echo ""
        
        # Check each service status
        for service in $(docker service ls --format "{{.Name}}" | grep archon); do
            replicas=$(docker service ls --filter name=$service --format "{{.Replicas}}")
            if [[ $replicas == "1/1" ]]; then
                print_status "OK" "$service: $replicas"
            else
                print_status "ERROR" "$service: $replicas"
            fi
        done
    else
        print_status "ERROR" "No Archon services found"
        echo "Deploy the stack first with: docker stack deploy -c archon-saas-supabase.yml archon"
    fi
    echo ""
}

# Check service logs for errors
check_service_logs() {
    echo "📝 SERVICE LOGS (Last 20 lines)"
    echo "-------------------------------"
    
    for service in $(docker service ls --format "{{.Name}}" | grep archon); do
        echo "--- $service ---"
        if docker service logs --tail 20 $service 2>/dev/null; then
            print_status "OK" "$service logs retrieved"
        else
            print_status "ERROR" "Failed to get $service logs"
        fi
        echo ""
    done
}

# Check network connectivity
check_network() {
    echo "🌐 NETWORK CONNECTIVITY"
    echo "-----------------------"
    
    # Check if archon network exists
    if docker network ls | grep -q "archon"; then
        print_status "OK" "Archon network exists"
        docker network ls | grep archon
    else
        print_status "ERROR" "Archon network not found"
    fi
    echo ""
}

# Check port accessibility
check_ports() {
    echo "🔌 PORT ACCESSIBILITY"
    echo "---------------------"
    
    # Default ports
    declare -A ports=(
        ["archon-server"]="8181"
        ["archon-mcp"]="8051"
        ["archon-agents"]="8052"
        ["archon-ui"]="3737"
        ["archon-embeddings"]="8080"
    )
    
    for service in "${!ports[@]}"; do
        port=${ports[$service]}
        if nc -z localhost $port 2>/dev/null; then
            print_status "OK" "$service port $port is accessible"
        else
            print_status "ERROR" "$service port $port is not accessible"
        fi
    done
    echo ""
}

# Check health endpoints
check_health_endpoints() {
    echo "🏥 HEALTH ENDPOINTS"
    echo "------------------"
    
    # Check archon-server health
    if curl -s -f http://localhost:8181/health >/dev/null 2>&1; then
        print_status "OK" "archon-server health endpoint responding"
        echo "Response: $(curl -s http://localhost:8181/health)"
    else
        print_status "ERROR" "archon-server health endpoint not responding"
    fi
    
    # Check archon-agents health
    if curl -s -f http://localhost:8052/health >/dev/null 2>&1; then
        print_status "OK" "archon-agents health endpoint responding"
        echo "Response: $(curl -s http://localhost:8052/health)"
    else
        print_status "ERROR" "archon-agents health endpoint not responding"
    fi
    
    # Check archon-embeddings health
    if curl -s -f http://localhost:8080/health >/dev/null 2>&1; then
        print_status "OK" "archon-embeddings health endpoint responding"
    else
        print_status "ERROR" "archon-embeddings health endpoint not responding"
    fi
    
    # Check archon-ui
    if curl -s -f http://localhost:3737 >/dev/null 2>&1; then
        print_status "OK" "archon-ui is accessible"
    else
        print_status "ERROR" "archon-ui is not accessible"
    fi
    echo ""
}

# Check environment variables
check_environment() {
    echo "🔧 ENVIRONMENT CONFIGURATION"
    echo "----------------------------"
    
    # Check if required environment variables are set
    required_vars=("SUPABASE_URL" "SUPABASE_SERVICE_KEY")
    
    for var in "${required_vars[@]}"; do
        if [ -n "${!var}" ]; then
            print_status "OK" "$var is set"
        else
            print_status "ERROR" "$var is not set"
        fi
    done
    echo ""
}

# Check container resource usage
check_resources() {
    echo "💾 RESOURCE USAGE"
    echo "----------------"
    
    # Get container stats
    if docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep archon; then
        print_status "OK" "Resource usage retrieved"
    else
        print_status "WARN" "No running containers found"
    fi
    echo ""
}

# Check Docker Swarm tasks
check_swarm_tasks() {
    echo "📊 SWARM TASK STATUS"
    echo "-------------------"
    
    for service in $(docker service ls --format "{{.Name}}" | grep archon); do
        echo "--- $service tasks ---"
        docker service ps $service --format "table {{.Name}}\t{{.CurrentState}}\t{{.Error}}"
        echo ""
    done
}

# Main execution
main() {
    echo "Starting comprehensive health check..."
    echo ""
    
    # Run all checks
    check_swarm_status || exit 1
    check_swarm_services
    check_network
    check_ports
    check_health_endpoints
    check_environment
    check_resources
    check_swarm_tasks
    check_service_logs
    
    echo "🎯 SUMMARY"
    echo "----------"
    print_status "INFO" "Health check completed"
    echo "If services are not accessible:"
    echo "1. Check if all services are running (1/1 replicas)"
    echo "2. Verify environment variables are set"
    echo "3. Check service logs for errors"
    echo "4. Ensure ports are not blocked by firewall"
    echo "5. Verify Supabase connection"
    echo ""
    echo "For detailed troubleshooting, run:"
    echo "  docker service logs <service-name>"
    echo "  docker service inspect <service-name>"
}

# Check if required tools are installed
check_prerequisites() {
    local missing_tools=()
    
    for tool in docker curl nc; do
        if ! command -v $tool &> /dev/null; then
            missing_tools+=($tool)
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_status "ERROR" "Missing required tools: ${missing_tools[*]}"
        echo "Please install the missing tools and try again."
        exit 1
    fi
}

# Run prerequisite check first
check_prerequisites

# Run main function
main
