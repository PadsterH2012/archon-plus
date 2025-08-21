#!/bin/bash

# =====================================================
# Template Injection System Enablement Script
# =====================================================
# This script enables template injection for specified projects
# with comprehensive validation and monitoring
# =====================================================

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="/tmp/template_injection_enable_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Configuration
ENVIRONMENT="${ENVIRONMENT:-dev}"
SUPABASE_URL="${SUPABASE_URL:-https://gifepwbtqkhiblgjgabq.supabase.co}"
API_BASE_URL="${API_BASE_URL:-http://localhost:9181}"
MCP_BASE_URL="${MCP_BASE_URL:-http://localhost:9051}"

# Default settings
DEFAULT_TEMPLATE="${DEFAULT_TEMPLATE:-workflow_default}"
CACHE_TTL="${CACHE_TTL:-1800}"
MAX_EXPANSION_TIME="${MAX_EXPANSION_TIME:-100}"

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS] [PROJECT_IDS...]

Enable template injection for specified projects with controlled rollout.

OPTIONS:
    -e, --environment ENV     Target environment (dev|prod) [default: dev]
    -g, --global             Enable globally for all projects
    -t, --template NAME      Default template name [default: workflow_default]
    -c, --cache-ttl SECONDS  Cache TTL in seconds [default: 1800]
    -m, --max-time MS        Max expansion time in ms [default: 100]
    -d, --dry-run           Show what would be done without making changes
    -v, --validate          Validate configuration and test expansion
    -h, --help              Show this help message

EXAMPLES:
    # Enable for specific projects
    $0 project-1 project-2 project-3

    # Enable globally
    $0 --global

    # Enable with custom template
    $0 --template workflow_hotfix project-urgent

    # Dry run to see what would happen
    $0 --dry-run --global

    # Validate configuration
    $0 --validate

ENVIRONMENT VARIABLES:
    ENVIRONMENT              Target environment (dev|prod)
    SUPABASE_URL            Supabase project URL
    API_BASE_URL            Archon API base URL
    MCP_BASE_URL            Archon MCP base URL
    DEFAULT_TEMPLATE        Default template name
    CACHE_TTL               Cache TTL in seconds
    MAX_EXPANSION_TIME      Max expansion time in ms

EOF
}

# Function to validate prerequisites
validate_prerequisites() {
    log "Validating prerequisites..."

    # Check required tools
    for tool in curl jq docker; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool '$tool' is not installed"
            exit 1
        fi
    done

    # Check Docker Swarm
    if ! docker info --format '{{.Swarm.LocalNodeState}}' | grep -q "active"; then
        log_error "Docker Swarm is not active"
        exit 1
    fi

    # Check services are running
    local services=("archon-${ENVIRONMENT}_dev-archon-server" "archon-${ENVIRONMENT}_dev-archon-mcp")
    for service in "${services[@]}"; do
        if ! docker service ls --format "{{.Name}}" | grep -q "$service"; then
            log_error "Service '$service' is not running"
            exit 1
        fi
    done

    log_success "Prerequisites validated"
}

# Function to check service health
check_service_health() {
    log "Checking service health..."

    # Check API health
    if ! curl -sf "$API_BASE_URL/api/health" > /dev/null; then
        log_error "API service is not healthy at $API_BASE_URL"
        exit 1
    fi

    # Check MCP health
    if ! curl -sf "$MCP_BASE_URL/health" > /dev/null; then
        log_error "MCP service is not healthy at $MCP_BASE_URL"
        exit 1
    fi

    # Check template injection service
    local response
    response=$(curl -sf "$API_BASE_URL/api/template-injection/health" 2>/dev/null || echo '{"status":"unavailable"}')
    local status
    status=$(echo "$response" | jq -r '.status // "unknown"')
    
    if [[ "$status" != "healthy" ]]; then
        log_warning "Template injection service status: $status"
    else
        log_success "All services are healthy"
    fi
}

# Function to validate template exists
validate_template() {
    local template_name="$1"
    log "Validating template: $template_name"

    local response
    response=$(curl -sf "$API_BASE_URL/api/template-injection/templates/$template_name" 2>/dev/null || echo '{"success":false}')
    local success
    success=$(echo "$response" | jq -r '.success // false')

    if [[ "$success" != "true" ]]; then
        log_error "Template '$template_name' not found or not available"
        exit 1
    fi

    log_success "Template '$template_name' validated"
}

# Function to test template expansion
test_template_expansion() {
    local template_name="$1"
    log "Testing template expansion with: $template_name"

    local test_payload
    test_payload=$(cat << EOF
{
    "original_description": "Test template expansion functionality",
    "template_name": "$template_name",
    "context_data": {"test": true}
}
EOF
)

    local response
    response=$(curl -sf -X POST "$API_BASE_URL/api/template-injection/expand" \
        -H "Content-Type: application/json" \
        -d "$test_payload" 2>/dev/null || echo '{"success":false}')

    local success
    success=$(echo "$response" | jq -r '.success // false')
    local expansion_time
    expansion_time=$(echo "$response" | jq -r '.result.expansion_time_ms // 0')

    if [[ "$success" != "true" ]]; then
        log_error "Template expansion test failed"
        echo "$response" | jq '.' | tee -a "$LOG_FILE"
        exit 1
    fi

    if (( $(echo "$expansion_time > $MAX_EXPANSION_TIME" | bc -l) )); then
        log_warning "Template expansion took ${expansion_time}ms (target: <${MAX_EXPANSION_TIME}ms)"
    else
        log_success "Template expansion test passed (${expansion_time}ms)"
    fi
}

# Function to update service environment variables
update_service_environment() {
    local service_name="$1"
    local env_vars=("${@:2}")

    log "Updating environment for service: $service_name"

    for env_var in "${env_vars[@]}"; do
        log "Setting: $env_var"
        if [[ "$DRY_RUN" != "true" ]]; then
            docker service update --env-add "$env_var" "$service_name" > /dev/null
        fi
    done

    if [[ "$DRY_RUN" != "true" ]]; then
        log "Waiting for service to update..."
        sleep 10
    fi
}

# Function to enable template injection
enable_template_injection() {
    local projects=("$@")
    
    log "Enabling template injection..."
    log "Environment: $ENVIRONMENT"
    log "Default template: $DEFAULT_TEMPLATE"
    log "Cache TTL: ${CACHE_TTL}s"
    log "Max expansion time: ${MAX_EXPANSION_TIME}ms"

    if [[ ${#projects[@]} -eq 0 ]] || [[ "$GLOBAL_ENABLE" == "true" ]]; then
        log "Enabling globally for all projects"
        local project_list=""
    else
        log "Enabling for projects: ${projects[*]}"
        local project_list
        project_list=$(IFS=','; echo "${projects[*]}")
    fi

    # Prepare environment variables
    local env_vars=(
        "TEMPLATE_INJECTION_ENABLED=true"
        "TEMPLATE_INJECTION_PROJECTS=$project_list"
        "TEMPLATE_INJECTION_DEFAULT_TEMPLATE=$DEFAULT_TEMPLATE"
        "TEMPLATE_INJECTION_CACHE_TTL=$CACHE_TTL"
        "TEMPLATE_INJECTION_MAX_EXPANSION_TIME=$MAX_EXPANSION_TIME"
    )

    # Update services
    local services=("archon-${ENVIRONMENT}_dev-archon-server" "archon-${ENVIRONMENT}_dev-archon-mcp")
    for service in "${services[@]}"; do
        update_service_environment "$service" "${env_vars[@]}"
    done

    if [[ "$DRY_RUN" != "true" ]]; then
        log_success "Template injection enabled successfully"
    else
        log_success "Dry run completed - no changes made"
    fi
}

# Function to verify enablement
verify_enablement() {
    if [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    log "Verifying template injection enablement..."

    # Wait for services to restart
    sleep 30

    # Check service health again
    check_service_health

    # Test template injection
    local response
    response=$(curl -sf "$API_BASE_URL/api/template-injection/health" 2>/dev/null || echo '{"template_injection_enabled":false}')
    local enabled
    enabled=$(echo "$response" | jq -r '.template_injection_enabled // false')

    if [[ "$enabled" != "true" ]]; then
        log_error "Template injection is not enabled after update"
        exit 1
    fi

    # Test actual template expansion
    test_template_expansion "$DEFAULT_TEMPLATE"

    log_success "Template injection enablement verified"
}

# Function to create monitoring dashboard
create_monitoring_dashboard() {
    log "Creating monitoring dashboard configuration..."

    local dashboard_config
    dashboard_config=$(cat << EOF
{
    "dashboard": {
        "title": "Template Injection System",
        "panels": [
            {
                "title": "Template Expansion Performance",
                "type": "graph",
                "targets": [
                    {
                        "expr": "template_expansion_duration_ms",
                        "legendFormat": "Expansion Time (ms)"
                    }
                ]
            },
            {
                "title": "Template Usage",
                "type": "stat",
                "targets": [
                    {
                        "expr": "template_usage_total",
                        "legendFormat": "Total Expansions"
                    }
                ]
            },
            {
                "title": "Error Rate",
                "type": "stat",
                "targets": [
                    {
                        "expr": "template_errors_total",
                        "legendFormat": "Errors"
                    }
                ]
            }
        ]
    }
}
EOF
)

    if [[ "$DRY_RUN" != "true" ]]; then
        echo "$dashboard_config" > "$PROJECT_ROOT/monitoring/template_injection_dashboard.json"
        log_success "Monitoring dashboard configuration created"
    else
        log "Would create monitoring dashboard configuration"
    fi
}

# Main function
main() {
    local projects=()
    local GLOBAL_ENABLE="false"
    local DRY_RUN="false"
    local VALIDATE_ONLY="false"

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -g|--global)
                GLOBAL_ENABLE="true"
                shift
                ;;
            -t|--template)
                DEFAULT_TEMPLATE="$2"
                shift 2
                ;;
            -c|--cache-ttl)
                CACHE_TTL="$2"
                shift 2
                ;;
            -m|--max-time)
                MAX_EXPANSION_TIME="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -v|--validate)
                VALIDATE_ONLY="true"
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                projects+=("$1")
                shift
                ;;
        esac
    done

    # Update API URLs based on environment
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        API_BASE_URL="${API_BASE_URL:-http://localhost:8181}"
        MCP_BASE_URL="${MCP_BASE_URL:-http://localhost:8051}"
    fi

    log "Starting template injection enablement process"
    log "Log file: $LOG_FILE"

    # Validate prerequisites
    validate_prerequisites

    # Check service health
    check_service_health

    # Validate template
    validate_template "$DEFAULT_TEMPLATE"

    # Test template expansion
    test_template_expansion "$DEFAULT_TEMPLATE"

    if [[ "$VALIDATE_ONLY" == "true" ]]; then
        log_success "Validation completed successfully"
        exit 0
    fi

    # Enable template injection
    enable_template_injection "${projects[@]}"

    # Verify enablement
    verify_enablement

    # Create monitoring dashboard
    create_monitoring_dashboard

    log_success "Template injection enablement completed successfully"
    log "Next steps:"
    log "1. Monitor service logs: docker service logs archon-${ENVIRONMENT}_dev-archon-server"
    log "2. Check performance metrics: curl $API_BASE_URL/api/metrics"
    log "3. Test with real tasks in enabled projects"
    log "4. Review monitoring dashboard for performance trends"
}

# Run main function with all arguments
main "$@"
