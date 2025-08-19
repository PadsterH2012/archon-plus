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

# Deploy SaaS Supabase - Development
deploy_saas_dev() {
    print_status "Deploying Archon Development stack with SaaS Supabase..."

    # Check required environment variables
    if [[ -z "${SUPABASE_URL:-}" ]]; then
        print_error "SUPABASE_URL environment variable is required"
        exit 1
    fi

    if [[ -z "${SUPABASE_SERVICE_KEY:-}" ]]; then
        print_error "SUPABASE_SERVICE_KEY environment variable is required"
        exit 1
    fi

    # Set default values for development
    export ARCHON_SERVER_PORT=${ARCHON_SERVER_PORT:-9181}
    export ARCHON_MCP_PORT=${ARCHON_MCP_PORT:-9051}
    export ARCHON_AGENTS_PORT=${ARCHON_AGENTS_PORT:-9052}
    export ARCHON_UI_PORT=${ARCHON_UI_PORT:-4737}
    export ARCHON_EMBEDDINGS_PORT=${ARCHON_EMBEDDINGS_PORT:-9080}
    export HOST=${HOST:-localhost}
    export LOG_LEVEL=${LOG_LEVEL:-DEBUG}

    # Deploy the stack
    docker stack deploy -c archon-saas-supabase-dev.yml archon-dev

    print_success "Archon Development stack deployed successfully!"
    print_status "Services will be available at:"
    echo "  Web UI: http://${HOST}:${ARCHON_UI_PORT}"
    echo "  API Server: http://${HOST}:${ARCHON_SERVER_PORT}"
    echo "  MCP Server: http://${HOST}:${ARCHON_MCP_PORT}"
    echo "  Agents Service: http://${HOST}:${ARCHON_AGENTS_PORT}"
    echo "  Embeddings Service: http://${HOST}:${ARCHON_EMBEDDINGS_PORT}"
}

# Deploy SaaS Supabase - Production
deploy_saas_prod() {
    print_status "Deploying Archon Production stack with SaaS Supabase..."

    # Check required environment variables
    if [[ -z "${SUPABASE_URL:-}" ]]; then
        print_error "SUPABASE_URL environment variable is required"
        exit 1
    fi

    if [[ -z "${SUPABASE_SERVICE_KEY:-}" ]]; then
        print_error "SUPABASE_SERVICE_KEY environment variable is required"
        exit 1
    fi

    # Set default values for production
    export ARCHON_SERVER_PORT=${ARCHON_SERVER_PORT:-8181}
    export ARCHON_MCP_PORT=${ARCHON_MCP_PORT:-8051}
    export ARCHON_AGENTS_PORT=${ARCHON_AGENTS_PORT:-8052}
    export ARCHON_UI_PORT=${ARCHON_UI_PORT:-3737}
    export ARCHON_EMBEDDINGS_PORT=${ARCHON_EMBEDDINGS_PORT:-8080}
    export HOST=${HOST:-localhost}
    export LOG_LEVEL=${LOG_LEVEL:-INFO}

    # Deploy the stack
    docker stack deploy -c archon-saas-supabase-prod.yml archon-prod

    print_success "Archon Production stack deployed successfully!"
    print_status "Services will be available at:"
    echo "  Web UI: http://${HOST}:${ARCHON_UI_PORT}"
    echo "  API Server: http://${HOST}:${ARCHON_SERVER_PORT}"
    echo "  MCP Server: http://${HOST}:${ARCHON_MCP_PORT}"
    echo "  Agents Service: http://${HOST}:${ARCHON_AGENTS_PORT}"
    echo "  Embeddings Service: http://${HOST}:${ARCHON_EMBEDDINGS_PORT}"
}

# Remove the stack
remove_stack() {
    local stack_name=${1:-archon}
    print_status "Removing ${stack_name} stack..."
    docker stack rm "${stack_name}"
    print_success "${stack_name} stack removed"
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
        "saas-dev")
            check_swarm
            deploy_saas_dev
            ;;
        "saas-prod")
            check_swarm
            deploy_saas_prod
            ;;
        "selfhosted")
            check_swarm
            deploy_selfhosted
            ;;
        "remove")
            remove_stack "${2:-archon}"
            ;;
        "remove-dev")
            remove_stack "archon-dev"
            ;;
        "remove-prod")
            remove_stack "archon-prod"
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        *)
            echo "Usage: $0 {saas|saas-dev|saas-prod|selfhosted|remove|remove-dev|remove-prod|status|logs}"
            echo ""
            echo "Commands:"
            echo "  saas        Deploy Archon with SaaS Supabase (legacy)"
            echo "  saas-dev    Deploy Archon DEVELOPMENT with SaaS Supabase (ports 9xxx)"
            echo "  saas-prod   Deploy Archon PRODUCTION with SaaS Supabase (ports 8xxx)"
            echo "  selfhosted  Deploy Archon with self-hosted Supabase"
            echo "  remove      Remove the default Archon stack"
            echo "  remove-dev  Remove the Archon development stack"
            echo "  remove-prod Remove the Archon production stack"
            echo "  status      Show stack status"
            echo "  logs        Show logs for a service"
            echo ""
            echo "Examples:"
            echo "  # Deploy development environment"
            echo "  SUPABASE_URL=https://xxx.supabase.co SUPABASE_SERVICE_KEY=xxx $0 saas-dev"
            echo ""
            echo "  # Deploy production environment"
            echo "  SUPABASE_URL=https://xxx.supabase.co SUPABASE_SERVICE_KEY=xxx $0 saas-prod"
            echo ""
            echo "  # Deploy self-hosted"
            echo "  POSTGRES_PASSWORD=mysecretpassword $0 selfhosted"
            echo ""
            echo "  # Show logs from development stack"
            echo "  $0 logs dev-archon-server"
            echo ""
            echo "  # Remove development stack"
            echo "  $0 remove-dev"
            echo ""
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
