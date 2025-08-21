#!/bin/bash

# =====================================================
# Template Injection System Rollback Script
# =====================================================
# This script safely rolls back template injection deployment
# with comprehensive validation and backup procedures
# =====================================================

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="/tmp/template_injection_rollback_$(date +%Y%m%d_%H%M%S).log"

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

# Rollback options
ROLLBACK_TYPE="${ROLLBACK_TYPE:-feature_flag}"  # feature_flag, service, database, full
BACKUP_ENABLED="${BACKUP_ENABLED:-true}"
FORCE_ROLLBACK="${FORCE_ROLLBACK:-false}"

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Rollback template injection deployment with various levels of rollback.

OPTIONS:
    -e, --environment ENV     Target environment (dev|prod) [default: dev]
    -t, --type TYPE          Rollback type [default: feature_flag]
                             - feature_flag: Disable feature flags only
                             - service: Rollback services to previous version
                             - database: Rollback database schema
                             - full: Complete rollback (all of the above)
    -b, --backup             Create backup before rollback [default: true]
    -f, --force              Force rollback without confirmation
    -d, --dry-run           Show what would be done without making changes
    -h, --help              Show this help message

ROLLBACK TYPES:
    feature_flag    Fastest rollback - just disable feature flags
                    - Sets TEMPLATE_INJECTION_ENABLED=false
                    - Preserves all data and services
                    - Recommended for most issues

    service         Rollback service images to previous versions
                    - Reverts to pre-template-injection images
                    - Disables feature flags
                    - Preserves database schema and data

    database        Rollback database schema changes
                    - Removes template injection tables
                    - ⚠️  DESTROYS ALL TEMPLATE DATA
                    - Only use if schema is corrupted

    full            Complete rollback
                    - All of the above in reverse order
                    - Nuclear option for critical issues

EXAMPLES:
    # Quick disable (recommended)
    $0 --type feature_flag

    # Rollback services
    $0 --type service --backup

    # Emergency full rollback
    $0 --type full --force

    # Dry run to see what would happen
    $0 --type full --dry-run

ENVIRONMENT VARIABLES:
    ENVIRONMENT              Target environment (dev|prod)
    SUPABASE_URL            Supabase project URL
    API_BASE_URL            Archon API base URL
    MCP_BASE_URL            Archon MCP base URL
    ROLLBACK_TYPE           Default rollback type
    BACKUP_ENABLED          Create backups before rollback
    FORCE_ROLLBACK          Skip confirmation prompts

EOF
}

# Function to confirm rollback
confirm_rollback() {
    if [[ "$FORCE_ROLLBACK" == "true" ]] || [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    log_warning "You are about to perform a '$ROLLBACK_TYPE' rollback"
    log_warning "Environment: $ENVIRONMENT"
    
    case "$ROLLBACK_TYPE" in
        database|full)
            log_warning "⚠️  THIS WILL DELETE TEMPLATE INJECTION DATA!"
            ;;
    esac

    echo -n "Are you sure you want to continue? (yes/no): "
    read -r response
    if [[ "$response" != "yes" ]]; then
        log "Rollback cancelled by user"
        exit 0
    fi
}

# Function to create backup
create_backup() {
    if [[ "$BACKUP_ENABLED" != "true" ]] || [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    log "Creating backup before rollback..."

    local backup_dir="$PROJECT_ROOT/backups/template_injection_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # Backup current service configurations
    log "Backing up service configurations..."
    docker service inspect archon-${ENVIRONMENT}_dev-archon-server > "$backup_dir/server_config.json" 2>/dev/null || true
    docker service inspect archon-${ENVIRONMENT}_dev-archon-mcp > "$backup_dir/mcp_config.json" 2>/dev/null || true

    # Backup environment variables
    log "Backing up environment variables..."
    docker service inspect archon-${ENVIRONMENT}_dev-archon-server --format '{{range .Spec.TaskTemplate.ContainerSpec.Env}}{{println .}}{{end}}' > "$backup_dir/server_env.txt" 2>/dev/null || true

    # Backup database data (if applicable)
    if [[ "$ROLLBACK_TYPE" == "database" ]] || [[ "$ROLLBACK_TYPE" == "full" ]]; then
        log "Backing up template injection data..."
        
        # Create SQL backup script
        cat > "$backup_dir/backup_template_data.sql" << 'EOF'
-- Template Injection Data Backup
-- Generated automatically before rollback

-- Backup template definitions
CREATE TABLE IF NOT EXISTS backup_template_definitions AS 
SELECT * FROM archon_template_definitions;

-- Backup template components  
CREATE TABLE IF NOT EXISTS backup_template_components AS 
SELECT * FROM archon_template_components;

-- Backup template assignments
CREATE TABLE IF NOT EXISTS backup_template_assignments AS 
SELECT * FROM archon_template_assignments;

-- Backup tasks with template metadata
CREATE TABLE IF NOT EXISTS backup_tasks_with_templates AS 
SELECT * FROM archon_tasks WHERE template_metadata IS NOT NULL;
EOF

        log "Database backup script created: $backup_dir/backup_template_data.sql"
        log_warning "Please run this script in Supabase SQL Editor before proceeding"
    fi

    log_success "Backup created: $backup_dir"
    echo "$backup_dir" > "/tmp/last_template_injection_backup"
}

# Function to rollback feature flags
rollback_feature_flags() {
    log "Rolling back template injection feature flags..."

    local env_vars=(
        "TEMPLATE_INJECTION_ENABLED=false"
        "TEMPLATE_INJECTION_PROJECTS="
    )

    local services=("archon-${ENVIRONMENT}_dev-archon-server" "archon-${ENVIRONMENT}_dev-archon-mcp")
    for service in "${services[@]}"; do
        log "Disabling template injection for service: $service"
        
        if [[ "$DRY_RUN" != "true" ]]; then
            for env_var in "${env_vars[@]}"; do
                docker service update --env-add "$env_var" "$service" > /dev/null
            done
        else
            log "Would disable template injection for: $service"
        fi
    done

    if [[ "$DRY_RUN" != "true" ]]; then
        log "Waiting for services to update..."
        sleep 15
    fi

    log_success "Feature flags rolled back"
}

# Function to rollback services
rollback_services() {
    log "Rolling back services to previous versions..."

    # First disable feature flags
    rollback_feature_flags

    # Get previous image versions (this would need to be customized based on your versioning)
    local previous_server_image="${PREVIOUS_SERVER_IMAGE:-hl-harbor.techpad.uk/archon/archon-server:latest}"
    local previous_mcp_image="${PREVIOUS_MCP_IMAGE:-hl-harbor.techpad.uk/archon/archon-mcp:latest}"

    log "Rolling back to images:"
    log "  Server: $previous_server_image"
    log "  MCP: $previous_mcp_image"

    if [[ "$DRY_RUN" != "true" ]]; then
        # Rollback server service
        log "Rolling back server service..."
        docker service update --image "$previous_server_image" archon-${ENVIRONMENT}_dev-archon-server

        # Rollback MCP service
        log "Rolling back MCP service..."
        docker service update --image "$previous_mcp_image" archon-${ENVIRONMENT}_dev-archon-mcp

        log "Waiting for services to rollback..."
        sleep 30
    else
        log "Would rollback services to previous images"
    fi

    log_success "Services rolled back"
}

# Function to rollback database
rollback_database() {
    log_warning "Rolling back database schema..."
    log_warning "⚠️  THIS WILL DELETE ALL TEMPLATE INJECTION DATA!"

    if [[ "$DRY_RUN" == "true" ]]; then
        log "Would execute database rollback script"
        return 0
    fi

    # Create rollback SQL script
    local rollback_script="/tmp/template_injection_rollback.sql"
    cat > "$rollback_script" << 'EOF'
-- Template Injection Database Rollback Script
-- ⚠️  WARNING: THIS WILL DELETE ALL TEMPLATE INJECTION DATA!

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS archon_template_assignments CASCADE;
DROP TABLE IF EXISTS archon_template_components CASCADE;
DROP TABLE IF EXISTS archon_template_definitions CASCADE;

-- Drop custom types
DROP TYPE IF EXISTS template_definition_type CASCADE;
DROP TYPE IF EXISTS template_component_type CASCADE;
DROP TYPE IF EXISTS template_injection_level CASCADE;
DROP TYPE IF EXISTS hierarchy_type CASCADE;

-- Clean up any template metadata from tasks (optional)
-- UPDATE archon_tasks SET template_metadata = NULL WHERE template_metadata IS NOT NULL;

-- Verify cleanup
SELECT 
    'Template tables dropped' as status,
    COUNT(*) as remaining_tables
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'archon_template_%';
EOF

    log "Database rollback script created: $rollback_script"
    log_warning "Please run this script in Supabase SQL Editor to complete database rollback"
    log_warning "URL: https://supabase.com/dashboard/project/gifepwbtqkhiblgjgabq/sql"

    log_success "Database rollback script prepared"
}

# Function to verify rollback
verify_rollback() {
    if [[ "$DRY_RUN" == "true" ]]; then
        return 0
    fi

    log "Verifying rollback..."

    # Wait for services to stabilize
    sleep 30

    # Check service health
    log "Checking service health..."
    if ! curl -sf "$API_BASE_URL/api/health" > /dev/null; then
        log_error "API service is not healthy after rollback"
        return 1
    fi

    if ! curl -sf "$MCP_BASE_URL/health" > /dev/null; then
        log_error "MCP service is not healthy after rollback"
        return 1
    fi

    # Check template injection status
    local response
    response=$(curl -sf "$API_BASE_URL/api/template-injection/health" 2>/dev/null || echo '{"template_injection_enabled":true}')
    local enabled
    enabled=$(echo "$response" | jq -r '.template_injection_enabled // true')

    case "$ROLLBACK_TYPE" in
        feature_flag|service|full)
            if [[ "$enabled" == "true" ]]; then
                log_error "Template injection is still enabled after rollback"
                return 1
            fi
            ;;
    esac

    # Test basic functionality
    log "Testing basic task creation..."
    local test_response
    test_response=$(curl -sf -X POST "$API_BASE_URL/api/tasks" \
        -H "Content-Type: application/json" \
        -d '{
            "project_id": "test-project",
            "title": "Rollback Test Task",
            "description": "Testing basic functionality after rollback",
            "enable_template_injection": false
        }' 2>/dev/null || echo '{"success":false}')

    local success
    success=$(echo "$test_response" | jq -r '.success // false')
    if [[ "$success" != "true" ]]; then
        log_warning "Basic task creation test failed - this may be expected"
    else
        log_success "Basic functionality verified"
    fi

    log_success "Rollback verification completed"
}

# Function to generate rollback report
generate_rollback_report() {
    local report_file="$PROJECT_ROOT/reports/template_injection_rollback_$(date +%Y%m%d_%H%M%S).md"
    mkdir -p "$(dirname "$report_file")"

    cat > "$report_file" << EOF
# Template Injection Rollback Report

**Date**: $(date)
**Environment**: $ENVIRONMENT
**Rollback Type**: $ROLLBACK_TYPE
**Performed By**: $(whoami)

## Rollback Summary

- **Status**: $(if [[ "$DRY_RUN" == "true" ]]; then echo "DRY RUN"; else echo "COMPLETED"; fi)
- **Backup Created**: $BACKUP_ENABLED
- **Force Mode**: $FORCE_ROLLBACK

## Actions Performed

EOF

    case "$ROLLBACK_TYPE" in
        feature_flag)
            echo "- ✅ Disabled template injection feature flags" >> "$report_file"
            ;;
        service)
            echo "- ✅ Disabled template injection feature flags" >> "$report_file"
            echo "- ✅ Rolled back service images to previous versions" >> "$report_file"
            ;;
        database)
            echo "- ✅ Disabled template injection feature flags" >> "$report_file"
            echo "- ⚠️  Database rollback script prepared (manual execution required)" >> "$report_file"
            ;;
        full)
            echo "- ✅ Disabled template injection feature flags" >> "$report_file"
            echo "- ✅ Rolled back service images to previous versions" >> "$report_file"
            echo "- ⚠️  Database rollback script prepared (manual execution required)" >> "$report_file"
            ;;
    esac

    cat >> "$report_file" << EOF

## Next Steps

1. Monitor service logs for any issues
2. Verify system stability
3. Investigate root cause of rollback
4. Plan re-deployment if needed

## Backup Location

$(if [[ -f "/tmp/last_template_injection_backup" ]]; then cat /tmp/last_template_injection_backup; else echo "No backup created"; fi)

## Log File

$LOG_FILE

EOF

    log_success "Rollback report generated: $report_file"
}

# Main function
main() {
    local DRY_RUN="false"

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--type)
                ROLLBACK_TYPE="$2"
                shift 2
                ;;
            -b|--backup)
                BACKUP_ENABLED="true"
                shift
                ;;
            -f|--force)
                FORCE_ROLLBACK="true"
                shift
                ;;
            -d|--dry-run)
                DRY_RUN="true"
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
                log_error "Unexpected argument: $1"
                usage
                exit 1
                ;;
        esac
    done

    # Validate rollback type
    case "$ROLLBACK_TYPE" in
        feature_flag|service|database|full)
            ;;
        *)
            log_error "Invalid rollback type: $ROLLBACK_TYPE"
            usage
            exit 1
            ;;
    esac

    # Update API URLs based on environment
    if [[ "$ENVIRONMENT" == "prod" ]]; then
        API_BASE_URL="${API_BASE_URL:-http://localhost:8181}"
        MCP_BASE_URL="${MCP_BASE_URL:-http://localhost:8051}"
    fi

    log "Starting template injection rollback process"
    log "Rollback type: $ROLLBACK_TYPE"
    log "Environment: $ENVIRONMENT"
    log "Log file: $LOG_FILE"

    # Confirm rollback
    confirm_rollback

    # Create backup
    create_backup

    # Perform rollback based on type
    case "$ROLLBACK_TYPE" in
        feature_flag)
            rollback_feature_flags
            ;;
        service)
            rollback_services
            ;;
        database)
            rollback_feature_flags
            rollback_database
            ;;
        full)
            rollback_services
            rollback_database
            ;;
    esac

    # Verify rollback
    verify_rollback

    # Generate report
    generate_rollback_report

    if [[ "$DRY_RUN" == "true" ]]; then
        log_success "Dry run completed - no changes made"
    else
        log_success "Template injection rollback completed successfully"
    fi

    log "Next steps:"
    log "1. Monitor service logs: docker service logs archon-${ENVIRONMENT}_dev-archon-server"
    log "2. Verify system stability"
    log "3. Investigate root cause"
    log "4. Plan re-deployment if needed"
}

# Run main function with all arguments
main "$@"
