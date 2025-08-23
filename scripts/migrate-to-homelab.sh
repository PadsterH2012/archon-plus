#!/bin/bash

# Archon Homelab Migration Script
# Migrates Archon from Supabase to homelab native infrastructure
# 
# Prerequisites:
# - PostgreSQL with pgvector extension
# - ChromaDB running and accessible
# - Redis running and accessible
# - MongoDB running (optional)
# - Supabase CLI installed
# - psql client installed

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/migration/backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="${BACKUP_DIR}/migration.log"

# Load environment variables
if [ -f "${PROJECT_ROOT}/portainer-templates/.env.homelab" ]; then
    source "${PROJECT_ROOT}/portainer-templates/.env.homelab"
else
    echo -e "${RED}Error: .env.homelab file not found${NC}"
    exit 1
fi

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Pre-flight checks
preflight_checks() {
    log "Running pre-flight checks..."
    
    # Check if required tools are installed
    command -v supabase >/dev/null 2>&1 || error "Supabase CLI not found. Install with: npm install -g supabase"
    command -v psql >/dev/null 2>&1 || error "psql not found. Install PostgreSQL client tools"
    command -v curl >/dev/null 2>&1 || error "curl not found"
    
    # Check environment variables
    [ -z "${SUPABASE_URL:-}" ] && error "SUPABASE_URL not set"
    [ -z "${SUPABASE_SERVICE_KEY:-}" ] && error "SUPABASE_SERVICE_KEY not set"
    [ -z "${POSTGRESQL_HOST:-}" ] && error "POSTGRESQL_HOST not set"
    [ -z "${POSTGRESQL_PASSWORD:-}" ] && error "POSTGRESQL_PASSWORD not set"
    [ -z "${CHROMADB_HOST:-}" ] && error "CHROMADB_HOST not set"
    [ -z "${REDIS_HOST:-}" ] && error "REDIS_HOST not set"
    
    # Test database connections
    log "Testing PostgreSQL connection..."
    PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -c "SELECT version();" >/dev/null 2>&1 || error "Cannot connect to PostgreSQL"
    
    log "Testing ChromaDB connection..."
    curl -s "http://${CHROMADB_HOST}:${CHROMADB_PORT}/api/v1/heartbeat" >/dev/null 2>&1 || error "Cannot connect to ChromaDB"
    
    log "Testing Redis connection..."
    if command -v redis-cli >/dev/null 2>&1; then
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1 || error "Cannot connect to Redis"
    else
        warning "redis-cli not found, skipping Redis connection test"
    fi
    
    success "Pre-flight checks passed"
}

# Export data from Supabase
export_supabase_data() {
    log "Exporting data from Supabase..."
    
    # Export database schema and data
    log "Exporting database schema..."
    supabase db dump --schema-only > "${BACKUP_DIR}/schema.sql" || error "Failed to export schema"
    
    log "Exporting database data..."
    supabase db dump --data-only > "${BACKUP_DIR}/data.sql" || error "Failed to export data"
    
    # Export specific tables with vector data
    log "Exporting vector embeddings..."
    PGPASSWORD="$SUPABASE_SERVICE_KEY" psql "$SUPABASE_URL" -c "COPY (SELECT id, url, chunk_number, content, metadata, embedding FROM archon_crawled_pages WHERE embedding IS NOT NULL) TO STDOUT WITH CSV HEADER" > "${BACKUP_DIR}/crawled_pages_vectors.csv" || error "Failed to export crawled pages vectors"
    
    PGPASSWORD="$SUPABASE_SERVICE_KEY" psql "$SUPABASE_URL" -c "COPY (SELECT id, url, chunk_number, content, summary, metadata, embedding FROM archon_code_examples WHERE embedding IS NOT NULL) TO STDOUT WITH CSV HEADER" > "${BACKUP_DIR}/code_examples_vectors.csv" || error "Failed to export code examples vectors"
    
    success "Supabase data exported successfully"
}

# Setup PostgreSQL schema
setup_postgresql() {
    log "Setting up PostgreSQL schema..."
    
    # Create database if it doesn't exist
    PGPASSWORD="$POSTGRESQL_PASSWORD" createdb -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" "$POSTGRESQL_DATABASE" 2>/dev/null || log "Database already exists"
    
    # Install required extensions
    log "Installing PostgreSQL extensions..."
    PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -c "CREATE EXTENSION IF NOT EXISTS vector;" || error "Failed to install pgvector extension"
    PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" || error "Failed to install uuid-ossp extension"
    
    # Apply schema (excluding vector columns for now)
    log "Applying database schema..."
    sed 's/vector(1536)/text/g' "${BACKUP_DIR}/schema.sql" > "${BACKUP_DIR}/schema_modified.sql"
    PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -f "${BACKUP_DIR}/schema_modified.sql" || error "Failed to apply schema"
    
    success "PostgreSQL schema setup completed"
}

# Import data to PostgreSQL
import_postgresql_data() {
    log "Importing data to PostgreSQL..."
    
    # Import non-vector data
    log "Importing table data..."
    sed 's/vector(1536)/text/g' "${BACKUP_DIR}/data.sql" > "${BACKUP_DIR}/data_modified.sql"
    PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -f "${BACKUP_DIR}/data_modified.sql" || error "Failed to import data"
    
    success "PostgreSQL data import completed"
}

# Setup ChromaDB collections
setup_chromadb() {
    log "Setting up ChromaDB collections..."
    
    # Create collections for different data types
    curl -X POST "http://${CHROMADB_HOST}:${CHROMADB_PORT}/api/v1/collections" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"${CHROMADB_COLLECTION_PREFIX}_documents\", \"metadata\": {\"description\": \"Document embeddings\"}}" || log "Documents collection may already exist"
    
    curl -X POST "http://${CHROMADB_HOST}:${CHROMADB_PORT}/api/v1/collections" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"${CHROMADB_COLLECTION_PREFIX}_code_examples\", \"metadata\": {\"description\": \"Code example embeddings\"}}" || log "Code examples collection may already exist"
    
    success "ChromaDB collections setup completed"
}

# Migrate vectors to ChromaDB
migrate_vectors_to_chromadb() {
    log "Migrating vectors to ChromaDB..."
    
    # This would typically be done with a Python script
    # For now, we'll create a placeholder script
    cat > "${BACKUP_DIR}/migrate_vectors.py" << 'EOF'
#!/usr/bin/env python3
import csv
import json
import requests
import os
from typing import List, Dict

def migrate_vectors(csv_file: str, collection_name: str, chromadb_host: str, chromadb_port: str):
    """Migrate vectors from CSV to ChromaDB"""
    base_url = f"http://{chromadb_host}:{chromadb_port}/api/v1"
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        batch_size = 100
        batch = []
        
        for row in reader:
            # Parse embedding vector
            embedding = json.loads(row['embedding']) if row['embedding'] else None
            if not embedding:
                continue
                
            batch.append({
                'id': row['id'],
                'embedding': embedding,
                'metadata': {
                    'url': row['url'],
                    'chunk_number': int(row['chunk_number']),
                    'content': row['content'][:1000],  # Truncate for metadata
                    'original_metadata': json.loads(row['metadata']) if row['metadata'] else {}
                },
                'document': row['content']
            })
            
            if len(batch) >= batch_size:
                # Send batch to ChromaDB
                response = requests.post(
                    f"{base_url}/collections/{collection_name}/add",
                    json={
                        'ids': [item['id'] for item in batch],
                        'embeddings': [item['embedding'] for item in batch],
                        'metadatas': [item['metadata'] for item in batch],
                        'documents': [item['document'] for item in batch]
                    }
                )
                if response.status_code != 200:
                    print(f"Error adding batch: {response.text}")
                else:
                    print(f"Added batch of {len(batch)} items to {collection_name}")
                batch = []
        
        # Send remaining items
        if batch:
            response = requests.post(
                f"{base_url}/collections/{collection_name}/add",
                json={
                    'ids': [item['id'] for item in batch],
                    'embeddings': [item['embedding'] for item in batch],
                    'metadatas': [item['metadata'] for item in batch],
                    'documents': [item['document'] for item in batch]
                }
            )
            if response.status_code != 200:
                print(f"Error adding final batch: {response.text}")
            else:
                print(f"Added final batch of {len(batch)} items to {collection_name}")

if __name__ == "__main__":
    chromadb_host = os.environ.get('CHROMADB_HOST', 'localhost')
    chromadb_port = os.environ.get('CHROMADB_PORT', '8000')
    collection_prefix = os.environ.get('CHROMADB_COLLECTION_PREFIX', 'archon')
    
    # Migrate crawled pages
    migrate_vectors(
        'crawled_pages_vectors.csv',
        f'{collection_prefix}_documents',
        chromadb_host,
        chromadb_port
    )
    
    # Migrate code examples
    migrate_vectors(
        'code_examples_vectors.csv',
        f'{collection_prefix}_code_examples',
        chromadb_host,
        chromadb_port
    )
EOF
    
    # Run the migration script
    cd "$BACKUP_DIR"
    python3 migrate_vectors.py || error "Failed to migrate vectors to ChromaDB"
    
    success "Vector migration to ChromaDB completed"
}

# Validate migration
validate_migration() {
    log "Validating migration..."
    
    # Check PostgreSQL data
    local pg_count
    pg_count=$(PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -t -c "SELECT COUNT(*) FROM archon_projects;" | tr -d ' ')
    log "PostgreSQL projects count: $pg_count"
    
    # Check ChromaDB collections
    local chroma_docs
    chroma_docs=$(curl -s "http://${CHROMADB_HOST}:${CHROMADB_PORT}/api/v1/collections/${CHROMADB_COLLECTION_PREFIX}_documents/count" | jq -r '.count // 0')
    log "ChromaDB documents count: $chroma_docs"
    
    local chroma_code
    chroma_code=$(curl -s "http://${CHROMADB_HOST}:${CHROMADB_PORT}/api/v1/collections/${CHROMADB_COLLECTION_PREFIX}_code_examples/count" | jq -r '.count // 0')
    log "ChromaDB code examples count: $chroma_code"
    
    success "Migration validation completed"
}

# Main migration process
main() {
    log "Starting Archon homelab migration..."
    log "Backup directory: $BACKUP_DIR"
    
    preflight_checks
    export_supabase_data
    setup_postgresql
    import_postgresql_data
    setup_chromadb
    migrate_vectors_to_chromadb
    validate_migration
    
    success "Migration completed successfully!"
    log "Next steps:"
    log "1. Update your Archon deployment to use homelab configuration"
    log "2. Deploy using: portainer-templates/archon-homelab-native.yml"
    log "3. Test all functionality thoroughly"
    log "4. Keep Supabase running until you're confident in the migration"
    log ""
    log "Backup location: $BACKUP_DIR"
}

# Run main function
main "$@"
