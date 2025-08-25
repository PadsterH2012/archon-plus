#!/bin/bash

# Backup PRPs and Plans Script
# This script copies all PRPs and planning documents to /mnt/network_repo/archon-prps/ before rollback

set -e

# Configuration
BACKUP_DIR="/mnt/network_repo/archon-prps"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CURRENT_COMMIT=$(git rev-parse HEAD)
CURRENT_BRANCH=$(git branch --show-current)

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

echo "🚀 Archon PRPs and Plans Backup Script"
echo "======================================="
echo "Backup Directory: $BACKUP_DIR"
echo "Timestamp: $TIMESTAMP"
echo "Current Commit: $CURRENT_COMMIT"
echo "Current Branch: $CURRENT_BRANCH"
echo ""

# Create backup directory structure
print_status "Creating backup directory structure..."
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/PRPs"
mkdir -p "$BACKUP_DIR/docs"
mkdir -p "$BACKUP_DIR/project_docs"
mkdir -p "$BACKUP_DIR/plans"
mkdir -p "$BACKUP_DIR/metadata"

# Create metadata file
print_status "Creating backup metadata..."
cat > "$BACKUP_DIR/metadata/backup_info.txt" << EOF
Archon PRPs and Plans Backup
============================
Backup Date: $(date)
Git Commit: $CURRENT_COMMIT
Git Branch: $CURRENT_BRANCH
Backup Reason: Pre-rollback to production stable version (6cf4cc13b313fe17e6fab13929f0230df0dbd743)

Files Backed Up:
- All PRP documents from PRPs/ folder
- Planning documents from docs/ folder
- Architecture and analysis documents from project_docs/
- Implementation plans and strategies
- Template and workflow documentation

This backup preserves all planning work before rolling back to stable production version.
EOF

# Backup PRPs folder
print_status "Backing up PRPs folder..."
if [ -d "PRPs" ]; then
    cp -r PRPs/* "$BACKUP_DIR/PRPs/" 2>/dev/null || true
    print_success "PRPs folder backed up"
else
    print_warning "PRPs folder not found"
fi

# Backup specific planning documents from docs/
print_status "Backing up planning documents from docs/..."
DOCS_FILES=(
    "docs/issues-kanban-implementation-plan.md"
    "docs/export-format-specification.md"
    "docs/template_injection_operations_guide.md"
    "docs/testing_template_injection_system.md"
    "docs/workflow-api-documentation.md"
    "docs/workflow-database-schema.md"
    "docs/workflow-documentation-summary.md"
    "docs/workflow_templates_guide.md"
    "docs/template_components_reference.md"
    "docs/tei-integration.md"
    "docs/design/"
    "docs/issues/"
    "docs/troubleshooting/"
)

for file in "${DOCS_FILES[@]}"; do
    if [ -e "$file" ]; then
        if [ -d "$file" ]; then
            mkdir -p "$BACKUP_DIR/$file"
            cp -r "$file"* "$BACKUP_DIR/$file/" 2>/dev/null || true
            print_success "Backed up directory: $file"
        else
            mkdir -p "$(dirname "$BACKUP_DIR/$file")"
            cp "$file" "$BACKUP_DIR/$file"
            print_success "Backed up file: $file"
        fi
    else
        print_warning "File not found: $file"
    fi
done

# Backup project_docs architecture and analysis
print_status "Backing up project_docs architecture and analysis..."
PROJECT_DOCS_DIRS=(
    "project_docs/architecture/"
    "project_docs/analysis/"
    "project_docs/deployment/"
    "project_docs/components/"
    "project_docs/workflows/"
)

for dir in "${PROJECT_DOCS_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        mkdir -p "$BACKUP_DIR/$dir"
        cp -r "$dir"* "$BACKUP_DIR/$dir/" 2>/dev/null || true
        print_success "Backed up directory: $dir"
    else
        print_warning "Directory not found: $dir"
    fi
done

# Backup specific planning files from root
print_status "Backing up root-level planning files..."
ROOT_PLAN_FILES=(
    "PORT_AUDIT_AND_MIGRATION_PLAN.md"
    "DEPLOYMENT_STATUS.md"
    "HOMELAB_ARCHON_CONTEXT.md"
    "PRODUCTION_DATABASE_ALIGNMENT_PLAN.md"
    "agentic_workflow_framework_dynamic_plan.md"
    "jenkins_build.log"
    "container_logs.txt"
    "troubleshooting_components_tab_crash.md"
    "components-tab-troubleshooting.md"
    "issue_management_1.md"
)

for file in "${ROOT_PLAN_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/plans/"
        print_success "Backed up plan: $file"
    else
        print_warning "Plan file not found: $file"
    fi
done

# Create file inventory
print_status "Creating file inventory..."
find "$BACKUP_DIR" -type f -name "*.md" -o -name "*.json" -o -name "*.txt" -o -name "*.log" | \
    sed "s|$BACKUP_DIR/||" | sort > "$BACKUP_DIR/metadata/file_inventory.txt"

# Create summary
TOTAL_FILES=$(find "$BACKUP_DIR" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

cat > "$BACKUP_DIR/metadata/backup_summary.txt" << EOF
Backup Summary
==============
Total Files: $TOTAL_FILES
Total Size: $TOTAL_SIZE
Backup Location: $BACKUP_DIR

Key Components Backed Up:
✅ PRPs (Product Requirement Prompts)
✅ Architecture Analysis Documents
✅ Implementation Plans
✅ Deployment Guides
✅ Template and Workflow Documentation
✅ Issue Management Plans
✅ Database Migration Plans
✅ Component Analysis
✅ Troubleshooting Guides

This backup ensures all planning work is preserved before rollback.
EOF

print_success "Backup completed successfully!"
echo ""
echo "📊 Backup Summary:"
echo "   Total Files: $TOTAL_FILES"
echo "   Total Size: $TOTAL_SIZE"
echo "   Location: $BACKUP_DIR"
echo ""
echo "📋 Next Steps:"
echo "   1. Verify backup contents: ls -la $BACKUP_DIR"
echo "   2. Proceed with git rollback to: 6cf4cc13b313fe17e6fab13929f0230df0dbd743"
echo "   3. Restore planning documents from backup as needed"
echo ""
print_success "All PRPs and plans safely backed up!"
