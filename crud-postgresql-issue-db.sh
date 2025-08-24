#!/bin/bash

# Archon PostgreSQL Issue Database CRUD Operations Script
# This script provides convenient CRUD operations for the PostgreSQL container

set -e

# Configuration
CONTAINER_NAME="Archon-Issue-DB"
DB_USER="archon_user"
DB_NAME="archon_issues"

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

# Check if container is running
check_container() {
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        log_error "Container $CONTAINER_NAME is not running"
        log_info "Start it with: ./manage-postgresql-issue-db.sh start"
        exit 1
    fi
}

# Execute SQL command
execute_sql() {
    local sql="$1"
    docker exec -it "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -c "$sql"
}

# Execute SQL file
execute_sql_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        log_error "SQL file $file not found"
        exit 1
    fi
    docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" < "$file"
}

# Interactive SQL session
interactive_sql() {
    log_info "Starting interactive SQL session..."
    log_info "Type \\q to quit, \\h for help"
    docker exec -it "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME"
}

# List all tables
list_tables() {
    log_info "Listing all tables in database..."
    execute_sql "\\dt"
}

# Describe table structure
describe_table() {
    local table="$1"
    if [ -z "$table" ]; then
        log_error "Please specify table name: $0 describe <table_name>"
        exit 1
    fi
    
    log_info "Describing table: $table"
    execute_sql "\\d $table"
}

# Show table data with optional limit
show_table() {
    local table="$1"
    local limit="${2:-10}"
    
    if [ -z "$table" ]; then
        log_error "Please specify table name: $0 show <table_name> [limit]"
        exit 1
    fi
    
    log_info "Showing data from table: $table (limit: $limit)"
    execute_sql "SELECT * FROM $table LIMIT $limit;"
}

# Count rows in table
count_table() {
    local table="$1"
    if [ -z "$table" ]; then
        log_error "Please specify table name: $0 count <table_name>"
        exit 1
    fi
    
    log_info "Counting rows in table: $table"
    execute_sql "SELECT COUNT(*) as row_count FROM $table;"
}

# Search in table
search_table() {
    local table="$1"
    local column="$2"
    local value="$3"
    
    if [ -z "$table" ] || [ -z "$column" ] || [ -z "$value" ]; then
        log_error "Usage: $0 search <table_name> <column_name> <search_value>"
        exit 1
    fi
    
    log_info "Searching in table: $table, column: $column, value: $value"
    execute_sql "SELECT * FROM $table WHERE $column ILIKE '%$value%';"
}

# Insert data (interactive)
insert_data() {
    local table="$1"
    if [ -z "$table" ]; then
        log_error "Please specify table name: $0 insert <table_name>"
        exit 1
    fi
    
    log_info "Interactive insert for table: $table"
    log_info "First, let's see the table structure:"
    execute_sql "\\d $table"
    
    echo ""
    log_info "Enter your INSERT statement (or press Ctrl+C to cancel):"
    echo "Example: INSERT INTO $table (column1, column2) VALUES ('value1', 'value2');"
    read -r sql_statement
    
    if [ -n "$sql_statement" ]; then
        execute_sql "$sql_statement"
        log_success "Insert completed"
    else
        log_warning "No statement entered"
    fi
}

# Update data (interactive)
update_data() {
    local table="$1"
    if [ -z "$table" ]; then
        log_error "Please specify table name: $0 update <table_name>"
        exit 1
    fi
    
    log_info "Interactive update for table: $table"
    log_info "Current data in table (last 5 rows):"
    execute_sql "SELECT * FROM $table ORDER BY id DESC LIMIT 5;"
    
    echo ""
    log_info "Enter your UPDATE statement (or press Ctrl+C to cancel):"
    echo "Example: UPDATE $table SET column1='new_value' WHERE id=1;"
    read -r sql_statement
    
    if [ -n "$sql_statement" ]; then
        execute_sql "$sql_statement"
        log_success "Update completed"
    else
        log_warning "No statement entered"
    fi
}

# Delete data (interactive with confirmation)
delete_data() {
    local table="$1"
    if [ -z "$table" ]; then
        log_error "Please specify table name: $0 delete <table_name>"
        exit 1
    fi
    
    log_info "Interactive delete for table: $table"
    log_info "Current data in table (last 10 rows):"
    execute_sql "SELECT * FROM $table ORDER BY id DESC LIMIT 10;"
    
    echo ""
    log_warning "⚠️  DELETE operations are permanent!"
    log_info "Enter your DELETE statement (or press Ctrl+C to cancel):"
    echo "Example: DELETE FROM $table WHERE id=1;"
    read -r sql_statement
    
    if [ -n "$sql_statement" ]; then
        log_warning "Are you sure you want to execute: $sql_statement (y/N)"
        read -r confirmation
        if [[ "$confirmation" =~ ^[Yy]$ ]]; then
            execute_sql "$sql_statement"
            log_success "Delete completed"
        else
            log_info "Delete cancelled"
        fi
    else
        log_warning "No statement entered"
    fi
}

# Execute custom SQL
custom_sql() {
    log_info "Enter your custom SQL statement (or press Ctrl+C to cancel):"
    log_info "Examples:"
    echo "  SELECT * FROM issues WHERE status = 'open';"
    echo "  CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT);"
    echo "  DROP TABLE test;"
    read -r sql_statement
    
    if [ -n "$sql_statement" ]; then
        execute_sql "$sql_statement"
        log_success "SQL executed"
    else
        log_warning "No statement entered"
    fi
}

# Database info
db_info() {
    log_info "Database Information:"
    echo ""
    echo "=== Database Size ==="
    execute_sql "SELECT pg_size_pretty(pg_database_size('$DB_NAME')) as database_size;"
    
    echo ""
    echo "=== Table Sizes ==="
    execute_sql "SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname NOT IN ('information_schema', 'pg_catalog') ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
    
    echo ""
    echo "=== Extensions ==="
    execute_sql "\\dx"
    
    echo ""
    echo "=== Connection Info ==="
    execute_sql "SELECT current_database(), current_user, inet_server_addr(), inet_server_port();"
}

# Backup table to SQL file
backup_table() {
    local table="$1"
    local output_file="${2:-${table}_backup_$(date +%Y%m%d_%H%M%S).sql}"
    
    if [ -z "$table" ]; then
        log_error "Please specify table name: $0 backup-table <table_name> [output_file]"
        exit 1
    fi
    
    log_info "Backing up table $table to $output_file"
    docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" -t "$table" > "$output_file"
    log_success "Table backup created: $output_file"
}

# Show help
show_help() {
    echo "Archon PostgreSQL Issue Database CRUD Operations"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Database Operations:"
    echo "  connect         Start interactive SQL session"
    echo "  info           Show database information and statistics"
    echo "  tables         List all tables"
    echo "  describe       Describe table structure"
    echo "  sql            Execute custom SQL statement"
    echo "  file           Execute SQL from file"
    echo ""
    echo "CRUD Operations:"
    echo "  show           Show table data with optional limit"
    echo "  count          Count rows in table"
    echo "  search         Search for data in table"
    echo "  insert         Interactive insert into table"
    echo "  update         Interactive update table data"
    echo "  delete         Interactive delete from table"
    echo ""
    echo "Backup Operations:"
    echo "  backup-table   Backup specific table to SQL file"
    echo ""
    echo "Examples:"
    echo "  $0 tables"
    echo "  $0 show issues 20"
    echo "  $0 search issues title 'login bug'"
    echo "  $0 describe issues"
    echo "  $0 count issues"
    echo "  $0 insert issues"
    echo "  $0 backup-table issues"
    echo "  $0 file my_queries.sql"
}

# Main script logic
main() {
    check_container
    
    case "${1:-help}" in
        connect)
            interactive_sql
            ;;
        info)
            db_info
            ;;
        tables)
            list_tables
            ;;
        describe)
            describe_table "$2"
            ;;
        show)
            show_table "$2" "$3"
            ;;
        count)
            count_table "$2"
            ;;
        search)
            search_table "$2" "$3" "$4"
            ;;
        insert)
            insert_data "$2"
            ;;
        update)
            update_data "$2"
            ;;
        delete)
            delete_data "$2"
            ;;
        sql)
            custom_sql
            ;;
        file)
            execute_sql_file "$2"
            ;;
        backup-table)
            backup_table "$2" "$3"
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
