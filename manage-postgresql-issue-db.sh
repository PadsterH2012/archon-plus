#!/bin/bash

# Archon PostgreSQL Issue Database Management Script
# This script provides convenient commands for managing the PostgreSQL container

set -e

# Configuration
COMPOSE_FILE="docker-compose.postgresql-issue-db.yml"
CONTAINER_NAME="Archon-Issue-DB"
ENV_FILE=".env"
TEMPLATE_ENV_FILE=".env.postgresql-issue-db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
}

# Check if environment file exists
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$TEMPLATE_ENV_FILE" ]; then
            log_warning "Environment file $ENV_FILE not found"
            log_info "Creating from template $TEMPLATE_ENV_FILE..."
            cp "$TEMPLATE_ENV_FILE" "$ENV_FILE"
            log_warning "Please edit $ENV_FILE and set your passwords before starting the database"
            return 1
        else
            log_error "Neither $ENV_FILE nor $TEMPLATE_ENV_FILE found"
            log_info "Please create an environment file with database configuration"
            return 1
        fi
    fi
    return 0
}

# Load environment variables from file
load_env_vars() {
    local env_file="${1:-$ENV_FILE}"

    if [ -f "$env_file" ]; then
        log_info "Loading environment variables from $env_file"
        set -a  # automatically export all variables
        source "$env_file"
        set +a
        return 0
    else
        log_warning "Environment file $env_file not found"
        return 1
    fi
}

# Function to start the database
start_db() {
    log_info "Starting Archon PostgreSQL Issue Database..."

    # Try to load environment variables
    if ! load_env_vars "$TEMPLATE_ENV_FILE" && ! load_env_vars "$ENV_FILE"; then
        if ! check_env_file; then
            log_error "Please configure $ENV_FILE first"
            exit 1
        fi
        load_env_vars "$ENV_FILE"
    fi

    docker-compose -f "$COMPOSE_FILE" up -d
    log_success "Database started successfully"

    # Wait for health check
    log_info "Waiting for database to be ready..."
    sleep 10

    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "healthy"; then
        log_success "Database is healthy and ready for connections"
    else
        log_warning "Database may still be starting up. Check logs with: $0 logs"
    fi
}

# Function to start with pgAdmin
start_with_admin() {
    log_info "Starting Archon PostgreSQL Issue Database with pgAdmin..."

    if ! check_env_file; then
        log_error "Please configure $ENV_FILE first"
        exit 1
    fi

    # Start PostgreSQL first
    docker-compose -f "$COMPOSE_FILE" up -d

    # Start pgAdmin
    docker-compose -f "docker-compose.pgadmin.yml" up -d

    log_success "Database and pgAdmin started successfully"
    log_info "pgAdmin will be available at http://localhost:5050"
    log_info "Default login: admin@archon.local / admin_password (change in .env file)"
}

# Function to stop the database
stop_db() {
    log_info "Stopping Archon PostgreSQL Issue Database..."
    docker-compose -f "$COMPOSE_FILE" down
    log_success "Database stopped successfully"
}

# Function to restart the database
restart_db() {
    log_info "Restarting Archon PostgreSQL Issue Database..."
    docker-compose -f "$COMPOSE_FILE" restart
    log_success "Database restarted successfully"
}

# Function to show status
status() {
    log_info "Checking database status..."
    docker-compose -f "$COMPOSE_FILE" ps
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        log_success "Container is running"
        
        # Check health
        if docker inspect "$CONTAINER_NAME" | grep -q '"Health"'; then
            HEALTH=$(docker inspect "$CONTAINER_NAME" | grep -A 1 '"Health"' | grep '"Status"' | cut -d'"' -f4)
            log_info "Health status: $HEALTH"
        fi
    else
        log_warning "Container is not running"
    fi
}

# Function to show logs
logs() {
    log_info "Showing database logs..."
    docker-compose -f "$COMPOSE_FILE" logs -f archon-issue-db
}

# Function to connect to database
connect() {
    log_info "Connecting to database..."
    docker exec -it "$CONTAINER_NAME" psql -U archon_user -d archon_issues
}

# Function to create backup
backup() {
    BACKUP_FILE="archon_issues_backup_$(date +%Y%m%d_%H%M%S).sql"
    log_info "Creating backup: $BACKUP_FILE"
    
    docker exec "$CONTAINER_NAME" pg_dump -U archon_user archon_issues > "$BACKUP_FILE"
    log_success "Backup created: $BACKUP_FILE"
}

# Function to restore backup
restore() {
    if [ -z "$1" ]; then
        log_error "Please specify backup file: $0 restore <backup_file.sql>"
        exit 1
    fi
    
    if [ ! -f "$1" ]; then
        log_error "Backup file $1 not found"
        exit 1
    fi
    
    log_warning "This will overwrite the current database. Are you sure? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled"
        exit 0
    fi
    
    log_info "Restoring backup: $1"
    docker exec -i "$CONTAINER_NAME" psql -U archon_user -d archon_issues < "$1"
    log_success "Backup restored successfully"
}

# Function to reset database (dangerous!)
reset() {
    log_error "⚠️  WARNING: This will DELETE ALL DATA in the database!"
    log_warning "Are you absolutely sure? Type 'DELETE ALL DATA' to confirm:"
    read -r confirmation
    
    if [ "$confirmation" != "DELETE ALL DATA" ]; then
        log_info "Reset cancelled"
        exit 0
    fi
    
    log_info "Stopping database..."
    docker-compose -f "$COMPOSE_FILE" down
    
    log_info "Removing data directory..."
    sudo rm -rf /mnt/network_repo/stack_dbs/postgresql/issue_db/*
    
    log_info "Starting fresh database..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_success "Database reset completed"
}

# Function to start with template (no .env file needed)
start_with_template() {
    log_info "Starting with template environment file..."

    if [ ! -f "$TEMPLATE_ENV_FILE" ]; then
        log_error "Template file $TEMPLATE_ENV_FILE not found"
        exit 1
    fi

    log_info "Using environment variables from $TEMPLATE_ENV_FILE"
    docker-compose --env-file "$TEMPLATE_ENV_FILE" -f "$COMPOSE_FILE" up -d
    log_success "Database started successfully with template configuration"
    log_warning "⚠️  Using default passwords from template - change them for production!"
}

# Function to show help
show_help() {
    echo "Archon PostgreSQL Issue Database Management Script"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  start          Start the database container"
    echo "  start-template Start with template env file (no .env needed)"
    echo "  start-admin    Start the database with pgAdmin"
    echo "  stop           Stop the database container"
    echo "  restart        Restart the database container"
    echo "  status         Show container status and health"
    echo "  logs           Show and follow database logs"
    echo "  connect        Connect to the database with psql"
    echo "  backup         Create a database backup"
    echo "  restore        Restore from a backup file"
    echo "  reset          Reset database (⚠️  DELETES ALL DATA!)"
    echo "  help           Show this help message"
    echo ""
    echo "Environment Options:"
    echo "  - Copy template: cp $TEMPLATE_ENV_FILE .env"
    echo "  - Use template directly: $0 start-template"
    echo "  - Use custom env file: --env-file custom.env"
    echo ""
    echo "Examples:"
    echo "  $0 start-template    # Quick start with defaults"
    echo "  $0 start             # Start with .env file"
    echo "  $0 backup"
    echo "  $0 restore backup_file.sql"
    echo "  $0 logs"
}

# Main script logic
main() {
    check_docker_compose
    
    case "${1:-help}" in
        start)
            start_db
            ;;
        start-template)
            start_with_template
            ;;
        start-admin)
            start_with_admin
            ;;
        stop)
            stop_db
            ;;
        restart)
            restart_db
            ;;
        status)
            status
            ;;
        logs)
            logs
            ;;
        connect)
            connect
            ;;
        backup)
            backup
            ;;
        restore)
            restore "$2"
            ;;
        reset)
            reset
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
