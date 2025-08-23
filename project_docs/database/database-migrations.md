# Database Migrations Documentation

**File Path:** `migration/` directory
**Last Updated:** 2025-08-22

## Purpose
Comprehensive documentation of all database migration files including setup procedures, rollback strategies, validation steps, and migration history. These migrations handle schema evolution, feature additions, and system upgrades for the Archon Plus database.

## Props/Parameters
Migrations use SQL scripts with PostgreSQL/Supabase compatibility

## Dependencies

### Prerequisites
- PostgreSQL database with Supabase
- Admin/service role access
- pgvector extension enabled
- Complete database backup before migrations

### Migration Tools
- Supabase SQL Editor (recommended)
- psql command line tool
- Python validation scripts (optional)

## Migration Categories

### 1. Core Setup Migrations
### 2. Feature Addition Migrations
### 3. Schema Enhancement Migrations
### 4. Data Seeding Migrations
### 5. Rollback & Cleanup Migrations
### 6. Validation & Testing Migrations

---

## 1. Core Setup Migrations

### `complete_setup.sql` (797 lines)
**Purpose:** Complete database schema initialization with all core tables

**What it Creates:**
- **Configuration Tables:** `archon_settings` with encrypted credential storage
- **Knowledge Base Tables:** `archon_sources`, `archon_crawled_pages`, `archon_code_examples`
- **Project Management Tables:** `archon_projects`, `archon_tasks`, `archon_document_versions`, `archon_prompts`
- **Core Functions:** `update_updated_at_column()`, `archive_task()`
- **RLS Policies:** Row Level Security for all tables
- **Indexes:** Performance optimization indexes
- **Triggers:** Automatic timestamp updates

**Usage:**
```sql
-- Run in Supabase SQL Editor
-- This is the foundation migration - run first
\i complete_setup.sql
```

### `RESET_DB.sql`
**Purpose:** Complete database reset for development/testing

**What it Does:**
- Drops all Archon tables and functions
- Removes all custom types and enums
- Cleans up RLS policies and triggers
- Resets database to clean state

**⚠️ WARNING:** Permanently deletes all data!

### `factory_reset.sql`
**Purpose:** Factory reset with data preservation options

**Features:**
- Selective table cleanup
- Data export options before reset
- Staged reset process
- Recovery checkpoints

---

## 2. Feature Addition Migrations

### `add_workflow_system.sql` (369 lines)
**Purpose:** Complete workflow orchestration system

**Tables Created:**
- `archon_workflow_templates` - Reusable workflow definitions
- `archon_workflow_executions` - Individual workflow runs  
- `archon_workflow_step_executions` - Step-level execution tracking
- `archon_workflow_template_versions` - Version control for templates

**Enums Created:**
- `workflow_status` - draft, active, deprecated, archived
- `workflow_step_type` - action, condition, workflow_link, parallel, loop
- `workflow_execution_status` - pending, running, paused, completed, failed, cancelled
- `step_execution_status` - pending, running, completed, failed, skipped, retrying

**Indexes Created (13):**
- Performance indexes on commonly queried fields
- GIN indexes for JSONB fields (tags, context)
- Composite indexes for complex queries

**Security (8 RLS Policies):**
- Public read access for all workflow data
- Service role full access for system operations

**Migration Process:**
```bash
# 1. Backup database
# 2. Run migration
psql -f migration/add_workflow_system.sql

# 3. Validate
psql -f migration/validate_workflow_schema.sql

# 4. Test (optional)
python migration/test_workflow_migration.py
```

### `add_template_injection_schema.sql` (320 lines)
**Purpose:** Dynamic template injection system for workflow enhancement

**Tables Created:**
- `archon_template_injection_templates` - Template definitions with placeholders
- `archon_template_components` - Reusable instruction components
- `archon_template_assignments` - Hierarchy-level template assignments

**Enums Created:**
- `template_injection_type` - workflow, sequence, action
- `template_injection_level` - project, milestone, phase, task, subtask
- `template_component_type` - action, group, sequence, validation
- `template_hierarchy_type` - project, milestone, phase, task, subtask

**Key Features:**
- Zero breaking changes to existing tables
- Hierarchical template assignment system
- Component-based template building
- Dynamic placeholder expansion

### `add_component_hierarchy.sql`
**Purpose:** Component dependency management system

**Tables Created:**
- `archon_component_hierarchy` - Component relationships
- `archon_component_dependencies` - Dependency tracking
- `archon_component_metadata` - Component metadata storage

**Features:**
- Hierarchical component organization
- Dependency validation
- Circular dependency prevention
- Component lifecycle tracking

### `add_split_providers.sql`
**Purpose:** Multi-provider configuration system

**Enhancements:**
- Provider-specific configurations
- Load balancing support
- Failover mechanisms
- Provider health monitoring

### `add_fallback_providers.sql`
**Purpose:** Provider fallback and redundancy

**Features:**
- Automatic provider switching
- Health check integration
- Performance monitoring
- Error recovery mechanisms

---

## 3. Schema Enhancement Migrations

### `enhance_template_assignments.sql`
**Purpose:** Enhanced template assignment capabilities

**Improvements:**
- Conditional assignment logic
- Priority-based conflict resolution
- Context-aware template selection
- Assignment audit trails

### `add_additional_workflow_templates.sql`
**Purpose:** Extended workflow template features

**Enhancements:**
- Advanced step types (parallel, loop)
- Conditional branching logic
- Sub-workflow execution
- Error handling patterns

---

## 4. Data Seeding Migrations

### `seed_default_templates.sql`
**Purpose:** Default workflow templates for common operations

**Templates Included:**
- `workflow::default` - Standard operational workflow
- `workflow::hotfix` - Emergency fix procedures
- `workflow::research` - Research and analysis workflow
- `workflow::deployment` - Deployment procedures

### `seed_template_injection_data.sql`
**Purpose:** Default template components and assignments

**Components Included:**
- `group::understand_homelab_env` - Environment review
- `group::send_task_to_review` - Review submission
- `action::git_commit` - Git operations
- `sequence::testing_strategy` - Testing procedures

---

## 5. Rollback & Cleanup Migrations

### `rollback_workflow_system.sql`
**Purpose:** Complete workflow system removal

**What it Removes:**
- All workflow tables and data
- Workflow-related enums and types
- Associated indexes and triggers
- RLS policies for workflow tables

**⚠️ WARNING:** Permanently deletes all workflow data!

**Usage:**
```sql
-- Backup workflow data first
SELECT * FROM archon_workflow_templates;
SELECT * FROM archon_workflow_executions;

-- Run rollback
\i rollback_workflow_system.sql

-- Verify cleanup
SELECT table_name FROM information_schema.tables 
WHERE table_name LIKE 'archon_workflow%';
-- Should return no rows
```

### `rollback_template_injection_schema.sql`
**Purpose:** Template injection system removal

**Cleanup Process:**
- Removes template injection tables
- Cleans up template-related enums
- Removes template assignments
- Preserves original task data

### `rollback_component_hierarchy.sql`
**Purpose:** Component system removal

**Features:**
- Safe component data export
- Dependency cleanup
- Metadata preservation options
- Staged rollback process

### `cleanup_component_duplicates.sql`
**Purpose:** Data cleanup and deduplication

**Operations:**
- Identifies duplicate components
- Merges duplicate entries
- Updates references
- Validates data integrity

---

## 6. Validation & Testing Migrations

### `validate_workflow_schema.sql`
**Purpose:** Comprehensive workflow system validation

**Validation Checks:**
- Table existence verification
- Enum type validation
- Index presence confirmation
- RLS policy verification
- Trigger functionality testing
- Basic CRUD operation testing

**Expected Output:**
```
🚀 Starting Workflow Schema Validation
================================================
📋 Checking Tables...
✅ archon_workflow_templates table exists
✅ archon_workflow_executions table exists
✅ archon_workflow_step_executions table exists
✅ archon_workflow_template_versions table exists
🏷️  Checking Enums...
✅ workflow_status enum exists
✅ workflow_step_type enum exists
✅ workflow_execution_status enum exists
✅ step_execution_status enum exists
📊 Checking Indexes...
✅ Workflow indexes created (13 found)
🔒 Checking RLS Policies...
✅ RLS policies created (8 found)
⚡ Checking Triggers...
✅ Triggers created (3 found)
🧪 Testing Basic Operations...
✅ Workflow template insertion works
✅ Workflow template deletion works
================================================
🎉 Workflow Schema Validation Complete!
```

### `validate_template_injection_schema.sql`
**Purpose:** Template injection system validation

**Validation Areas:**
- Template component validation
- Assignment logic verification
- Placeholder expansion testing
- Hierarchy integrity checks

### `validate_component_hierarchy.sql`
**Purpose:** Component system validation

**Checks:**
- Component relationship integrity
- Dependency cycle detection
- Metadata consistency
- Performance optimization verification

### `test_component_migration.sql`
**Purpose:** Component migration testing

**Test Cases:**
- Component creation and deletion
- Dependency management
- Hierarchy navigation
- Performance benchmarks

### `test_workflow_migration.py`
**Purpose:** Python-based workflow testing

**Features:**
- Async database operations testing
- Pydantic model validation
- API endpoint testing
- Performance benchmarking

**Usage:**
```bash
# Install dependencies
pip install asyncpg python-dotenv

# Set environment variables
export SUPABASE_URL="your-url"
export SUPABASE_SERVICE_KEY="your-key"

# Run tests
python migration/test_workflow_migration.py
```

---

## Migration Best Practices

### Pre-Migration Checklist
- [ ] **Database Backup:** Always backup before migrations
- [ ] **Review Changes:** Read migration scripts thoroughly
- [ ] **Check Dependencies:** Verify prerequisite migrations
- [ ] **Test Environment:** Run on staging first
- [ ] **Verify Permissions:** Ensure admin access

### Migration Execution
1. **Backup Database:** Create complete backup
2. **Run Migration:** Execute in Supabase SQL Editor
3. **Validate Results:** Run validation scripts
4. **Test Functionality:** Verify system operations
5. **Monitor Performance:** Check for performance impacts

### Rollback Strategy
1. **Identify Issues:** Determine rollback necessity
2. **Export Data:** Save any new data created
3. **Run Rollback:** Execute rollback migration
4. **Verify Cleanup:** Confirm complete removal
5. **Restore Backup:** If needed, restore from backup

### Error Handling
- **Permission Errors:** Check service role access
- **Duplicate Objects:** Use IF NOT EXISTS patterns
- **Missing Dependencies:** Verify prerequisite migrations
- **Data Conflicts:** Resolve before migration

---

## Related Files
- **Parent components:** Database schema, Supabase configuration
- **Child components:** Application models, API endpoints
- **Shared utilities:** Validation scripts, test suites

## Notes
- All migrations use idempotent patterns (safe to re-run)
- Comprehensive validation ensures migration success
- Rollback scripts provide safe removal paths
- Python test scripts offer additional validation
- Migration history tracked in README.md

---
*Auto-generated documentation - verify accuracy before use*
