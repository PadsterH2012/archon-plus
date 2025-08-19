#!/bin/bash

# Archon CI/CD Pipeline Deployment Script
# Best practices for dev/staging/prod deployments

set -e

# Configuration
HARBOR_REGISTRY="hl-harbor.techpad.uk"
PROJECT_NAME="archon"
ENVIRONMENTS=("dev" "prod")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_error() { echo -e "${RED}❌ Error: $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  Warning: $1${NC}"; }
print_status() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Validate environment
validate_environment() {
    local env=$1
    if [[ ! " ${ENVIRONMENTS[@]} " =~ " ${env} " ]]; then
        print_error "Invalid environment: ${env}. Valid options: ${ENVIRONMENTS[*]}"
        exit 1
    fi
}

# Get image tag based on environment and version
get_image_tag() {
    local env=$1
    local version=${2:-latest}
    
    case $env in
        "dev")
            echo "${env}-${version}"
            ;;
        "prod")
            echo "${version}"
            ;;
    esac
}

# Get port configuration for environment
get_port_config() {
    local env=$1
    
    case $env in
        "dev")
            echo "SERVER_PORT=9181 MCP_PORT=9051 AGENTS_PORT=9052 UI_PORT=4737 EMBEDDINGS_PORT=9080"
            ;;
        "prod")
            echo "SERVER_PORT=8181 MCP_PORT=8051 AGENTS_PORT=8052 UI_PORT=3737 EMBEDDINGS_PORT=8080"
            ;;
    esac
}

# Deploy to specific environment
deploy_environment() {
    local env=$1
    local version=${2:-latest}
    local image_tag
    local port_config
    
    validate_environment "$env"
    
    image_tag=$(get_image_tag "$env" "$version")
    port_config=$(get_port_config "$env")
    
    print_status "Deploying Archon to ${env} environment..."
    print_status "Image tag: ${image_tag}"
    print_status "Port configuration: ${port_config}"
    
    # Check if environment file exists
    local env_file=".env.${env}"
    if [[ ! -f "$env_file" ]]; then
        print_error "Environment file ${env_file} not found"
        exit 1
    fi
    
    # Load environment variables
    set -a
    source "$env_file"
    set +a
    
    # Set port configuration
    eval "$port_config"
    
    # Set image tags
    export ARCHON_SERVER_IMAGE="${HARBOR_REGISTRY}/${PROJECT_NAME}/archon-server:${image_tag}"
    export ARCHON_MCP_IMAGE="${HARBOR_REGISTRY}/${PROJECT_NAME}/archon-mcp:${image_tag}"
    export ARCHON_AGENTS_IMAGE="${HARBOR_REGISTRY}/${PROJECT_NAME}/archon-agents:${image_tag}"
    export ARCHON_UI_IMAGE="${HARBOR_REGISTRY}/${PROJECT_NAME}/archon-ui:${image_tag}"
    
    # Deploy stack
    local stack_name="${PROJECT_NAME}-${env}"
    local compose_file="portainer-templates/archon-saas-supabase-${env}.yml"
    
    if [[ ! -f "$compose_file" ]]; then
        print_error "Compose file ${compose_file} not found"
        exit 1
    fi
    
    print_status "Deploying stack: ${stack_name}"
    docker stack deploy -c "$compose_file" "$stack_name"
    
    print_success "Deployment to ${env} completed!"
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    health_check "$env"
}

# Health check for deployed environment
health_check() {
    local env=$1
    local port_config
    
    port_config=$(get_port_config "$env")
    eval "$port_config"
    
    print_status "Performing health check for ${env} environment..."
    
    # Check server health
    local server_url="http://localhost:${SERVER_PORT}/health"
    if curl -f -s "$server_url" > /dev/null; then
        print_success "Server health check passed"
    else
        print_error "Server health check failed"
        return 1
    fi
    
    # Check MCP health
    local mcp_url="http://localhost:${MCP_PORT}"
    if curl -f -s "$mcp_url" > /dev/null; then
        print_success "MCP health check passed"
    else
        print_warning "MCP health check failed (may be normal)"
    fi
    
    # Check UI health
    local ui_url="http://localhost:${UI_PORT}"
    if curl -f -s "$ui_url" > /dev/null; then
        print_success "UI health check passed"
    else
        print_error "UI health check failed"
        return 1
    fi
    
    print_success "All health checks passed for ${env}!"
}

# Promote from one environment to another
promote_environment() {
    local from_env=$1
    local to_env=$2
    local version=${3:-latest}
    
    validate_environment "$from_env"
    validate_environment "$to_env"
    
    print_status "Promoting from ${from_env} to ${to_env}..."
    
    # Get current image tag from source environment
    local from_tag=$(get_image_tag "$from_env" "$version")
    local to_tag=$(get_image_tag "$to_env" "$version")
    
    # Re-tag images for target environment
    local services=("archon-server" "archon-mcp" "archon-agents" "archon-ui")
    
    for service in "${services[@]}"; do
        local from_image="${HARBOR_REGISTRY}/${PROJECT_NAME}/${service}:${from_tag}"
        local to_image="${HARBOR_REGISTRY}/${PROJECT_NAME}/${service}:${to_tag}"
        
        print_status "Promoting ${service}: ${from_tag} → ${to_tag}"
        docker pull "$from_image"
        docker tag "$from_image" "$to_image"
        docker push "$to_image"
    done
    
    # Deploy to target environment
    deploy_environment "$to_env" "$version"
    
    print_success "Promotion from ${from_env} to ${to_env} completed!"
}

# Rollback environment to previous version
rollback_environment() {
    local env=$1
    local version=$2
    
    validate_environment "$env"
    
    if [[ -z "$version" ]]; then
        print_error "Version required for rollback"
        exit 1
    fi
    
    print_status "Rolling back ${env} to version ${version}..."
    deploy_environment "$env" "$version"
    print_success "Rollback completed!"
}

# Show usage
show_usage() {
    echo "Usage: $0 {deploy|promote|rollback|health} [options]"
    echo ""
    echo "Commands:"
    echo "  deploy <env> [version]     Deploy to environment (dev|prod)"
    echo "  promote <from> <to> [ver]  Promote between environments"
    echo "  rollback <env> <version>   Rollback to specific version"
    echo "  health <env>               Run health check"
    echo ""
    echo "Examples:"
    echo "  $0 deploy dev"
    echo "  $0 deploy prod v1.2.3"
    echo "  $0 promote dev prod"
    echo "  $0 promote dev prod v1.2.3"
    echo "  $0 rollback prod v1.2.2"
    echo "  $0 health dev"
}

# Main function
main() {
    case "${1:-}" in
        "deploy")
            deploy_environment "${2:-}" "${3:-latest}"
            ;;
        "promote")
            promote_environment "${2:-}" "${3:-}" "${4:-latest}"
            ;;
        "rollback")
            rollback_environment "${2:-}" "${3:-}"
            ;;
        "health")
            health_check "${2:-}"
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
