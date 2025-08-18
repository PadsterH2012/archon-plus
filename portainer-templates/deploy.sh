#!/bin/bash

# Archon Docker Swarm Deployment Script
# This script helps deploy Archon using Docker Swarm with or without Portainer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker Swarm is initialized
check_swarm() {
    if ! docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then
        print_warning "Docker Swarm is not initialized. Initializing now..."
        docker swarm init
        print_success "Docker Swarm initialized"
    else
        print_status "Docker Swarm is already active"
    fi
}

# Deploy SaaS Supabase version
deploy_saas() {
    print_status "Deploying Archon with SaaS Supabase..."
    
    # Check required environment variables
    if [[ -z "$SUPABASE_URL" || -z "$SUPABASE_SERVICE_KEY" ]]; then
        print_error "Required environment variables missing:"
        echo "  SUPABASE_URL=https://your-project.supabase.co"
        echo "  SUPABASE_SERVICE_KEY=your-service-role-key"
        echo ""
        echo "Get these from your Supabase project settings at https://supabase.com"
        exit 1
    fi
    
    # Set default values
    export ARCHON_SERVER_PORT=${ARCHON_SERVER_PORT:-8181}
    export ARCHON_MCP_PORT=${ARCHON_MCP_PORT:-8051}
    export ARCHON_AGENTS_PORT=${ARCHON_AGENTS_PORT:-8052}
    export ARCHON_UI_PORT=${ARCHON_UI_PORT:-3737}
    export HOST=${HOST:-localhost}
    export LOG_LEVEL=${LOG_LEVEL:-INFO}
    
    # Deploy the stack
    docker stack deploy -c archon-saas-supabase.yml archon
    
    print_success "Archon stack deployed successfully!"
    print_status "Services will be available at:"
    echo "  Web UI: http://${HOST}:${ARCHON_UI_PORT}"
    echo "  API Server: http://${HOST}:${ARCHON_SERVER_PORT}"
    echo "  MCP Server: http://${HOST}:${ARCHON_MCP_PORT}"
    echo "  Agents Service: http://${HOST}:${ARCHON_AGENTS_PORT}"
}

# Deploy self-hosted version
deploy_selfhosted() {
    print_status "Deploying Archon with Self-Hosted Supabase..."
    
    # Check required environment variables
    if [[ -z "$POSTGRES_PASSWORD" ]]; then
        print_error "Required environment variable missing:"
        echo "  POSTGRES_PASSWORD=your-secure-password"
        exit 1
    fi
    
    # Set default values
    export POSTGRES_DB=${POSTGRES_DB:-archon}
    export POSTGRES_USER=${POSTGRES_USER:-postgres}
    export POSTGRES_PORT=${POSTGRES_PORT:-5432}
    export JWT_SECRET=${JWT_SECRET:-your-super-secret-jwt-token-with-at-least-32-characters-long}
    export SERVICE_ROLE_KEY=${SERVICE_ROLE_KEY:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU}
    export ARCHON_SERVER_PORT=${ARCHON_SERVER_PORT:-8181}
    export ARCHON_MCP_PORT=${ARCHON_MCP_PORT:-8051}
    export ARCHON_AGENTS_PORT=${ARCHON_AGENTS_PORT:-8052}
    export ARCHON_UI_PORT=${ARCHON_UI_PORT:-3737}
    export HOST=${HOST:-localhost}
    export API_EXTERNAL_URL=${API_EXTERNAL_URL:-http://${HOST}:8000}
    export SITE_URL=${SITE_URL:-http://${HOST}:${ARCHON_UI_PORT}}
    export LOG_LEVEL=${LOG_LEVEL:-INFO}
    
    # Warn about JWT secret
    if [[ "$JWT_SECRET" == "your-super-secret-jwt-token-with-at-least-32-characters-long" ]]; then
        print_warning "Using default JWT_SECRET. Please change this for production!"
    fi
    
    # Deploy the stack
    docker stack deploy -c archon-self-hosted.yml archon
    
    print_success "Archon stack deployed successfully!"
    print_status "Services will be available at:"
    echo "  Web UI: http://${HOST}:${ARCHON_UI_PORT}"
    echo "  API Server: http://${HOST}:${ARCHON_SERVER_PORT}"
    echo "  MCP Server: http://${HOST}:${ARCHON_MCP_PORT}"
    echo "  Agents Service: http://${HOST}:${ARCHON_AGENTS_PORT}"
    echo "  Supabase REST API: http://${HOST}:8000"
    echo "  Supabase Realtime: http://${HOST}:4000"
    echo "  PostgreSQL: ${HOST}:${POSTGRES_PORT}"
}

# Remove the stack
remove_stack() {
    print_status "Removing Archon stack..."
    docker stack rm archon
    print_success "Archon stack removed"
}

# Show stack status
show_status() {
    print_status "Archon stack status:"
    docker stack services archon 2>/dev/null || print_warning "Archon stack not found"
}

# Show logs for a service
show_logs() {
    local service=$1
    if [[ -z "$service" ]]; then
        print_error "Please specify a service name"
        echo "Available services: archon-server, archon-mcp, archon-agents, archon-ui"
        if docker stack services archon 2>/dev/null | grep -q postgres; then
            echo "Self-hosted services: postgres, supabase-auth, supabase-rest, supabase-realtime"
        fi
        exit 1
    fi
    
    print_status "Showing logs for archon_${service}..."
    docker service logs -f archon_${service}
}

# Main script
main() {
    echo "🚀 Archon Docker Swarm Deployment Script"
    echo "========================================"
    echo ""
    
    case "${1:-}" in
        "saas")
            check_swarm
            deploy_saas
            ;;
        "selfhosted")
            check_swarm
            deploy_selfhosted
            ;;
        "remove")
            remove_stack
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        *)
            echo "Usage: $0 {saas|selfhosted|remove|status|logs}"
            echo ""
            echo "Commands:"
            echo "  saas        Deploy Archon with SaaS Supabase"
            echo "  selfhosted  Deploy Archon with self-hosted Supabase"
            echo "  remove      Remove the Archon stack"
            echo "  status      Show stack status"
            echo "  logs        Show logs for a service"
            echo ""
            echo "Examples:"
            echo "  # Deploy with SaaS Supabase"
            echo "  SUPABASE_URL=https://xxx.supabase.co SUPABASE_SERVICE_KEY=xxx $0 saas"
            echo ""
            echo "  # Deploy self-hosted"
            echo "  POSTGRES_PASSWORD=mysecretpassword $0 selfhosted"
            echo ""
            echo "  # Show logs"
            echo "  $0 logs archon-server"
            echo ""
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
