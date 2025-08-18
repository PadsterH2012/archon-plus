# Archon Database Migrations

This directory contains database migration scripts for the Archon system.

## Workflow System Migration

### Files Overview

| File | Purpose | Status |
|------|---------|--------|
| `add_workflow_system.sql` | Main migration script to add workflow tables | ✅ Ready |
| `rollback_workflow_system.sql` | Rollback script to remove workflow system | ✅ Ready |
| `validate_workflow_schema.sql` | Validation script to verify migration | ✅ Ready |
| `test_workflow_migration.py` | Python test script (requires asyncpg) | ✅ Ready |

### Migration Process

#### 1. Pre-Migration Checklist

- [ ] **Backup Database**: Always backup your database before running migrations
- [ ] **Review Changes**: Read through `add_workflow_system.sql` to understand what will be created
- [ ] **Check Dependencies**: Ensure `complete_setup.sql` has been run first
- [ ] **Verify Permissions**: Ensure you have admin access to the database

#### 2. Apply Migration

**Option A: Supabase Dashboard (Recommended)**
1. Open your Supabase project dashboard
2. Go to SQL Editor
3. Copy and paste the contents of `add_workflow_system.sql`
4. Click "Run" to execute the migration
5. Check for any error messages

**Option B: Command Line (Advanced)**
```bash
# Using psql (replace with your connection details)
psql -h db.your-project.supabase.co -U postgres -d postgres -f migration/add_workflow_system.sql
```

#### 3. Validate Migration

Run the validation script to ensure everything was created correctly:

**In Supabase SQL Editor:**
1. Copy and paste the contents of `validate_workflow_schema.sql`
2. Click "Run" to execute the validation
3. Check the output messages for any ❌ indicators

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

#### 4. Test with Python Script (Optional)

If you have Python and asyncpg installed:

```bash
# Install dependencies
pip install asyncpg python-dotenv

# Run test script
python migration/test_workflow_migration.py
```

### What Gets Created

#### Tables (4)
1. **`archon_workflow_templates`** - Reusable workflow definitions
2. **`archon_workflow_executions`** - Individual workflow runs
3. **`archon_workflow_step_executions`** - Step-level execution tracking
4. **`archon_workflow_template_versions`** - Version control for templates

#### Enums (4)
1. **`workflow_status`** - Template lifecycle status
2. **`workflow_step_type`** - Types of workflow steps
3. **`workflow_execution_status`** - Execution status tracking
4. **`step_execution_status`** - Individual step status

#### Indexes (13)
- Performance indexes on commonly queried fields
- GIN indexes for JSONB fields (tags, context)
- Composite indexes for complex queries

#### Security (8 RLS Policies)
- Public read access for all workflow data
- Service role full access for system operations
- Row Level Security enabled on all tables

#### Triggers (3)
- Automatic `updated_at` timestamp updates
- Maintains data consistency

### Rollback Process

If you need to remove the workflow system:

⚠️ **WARNING: This will permanently delete all workflow data!**

1. **Backup Data**: Export any workflow data you want to keep
2. **Run Rollback**: Execute `rollback_workflow_system.sql` in SQL Editor
3. **Verify Cleanup**: Check that all workflow tables are removed

```sql
-- Check that tables are gone
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE 'archon_workflow%';
-- Should return no rows
```

### Troubleshooting

#### Common Issues

**Error: "relation already exists"**
- The migration has already been applied
- Check if tables exist: `\dt archon_workflow*`
- If partial migration, run rollback first

**Error: "permission denied"**
- Ensure you're using the service role key
- Check that RLS policies allow your access level

**Error: "function update_updated_at_column() does not exist"**
- Run `complete_setup.sql` first
- This function should be created by the main setup

**Validation shows missing items**
- Re-run the migration script
- Check for error messages in the migration output
- Ensure you have sufficient database permissions

#### Getting Help

1. **Check Logs**: Look at the SQL execution output for specific error messages
2. **Verify Prerequisites**: Ensure `complete_setup.sql` was run successfully
3. **Database State**: Check current database state with validation script
4. **Rollback and Retry**: If needed, rollback and try migration again

### Next Steps

After successful migration:

1. **Update Application Code**: Implement Pydantic models for the new tables
2. **Create Repository Layer**: Build data access layer for workflow operations
3. **Add API Endpoints**: Create REST endpoints for workflow management
4. **Build UI Components**: Add workflow management to the frontend
5. **Write Tests**: Create comprehensive test suite for workflow functionality

### Migration History

| Version | Date | Description | Files |
|---------|------|-------------|-------|
| 1.0.0 | 2025-08-18 | Initial workflow system | `add_workflow_system.sql` |

### Schema Documentation

For detailed information about the database schema, see:
- `docs/workflow-database-schema.md` - Complete schema documentation
- `migration/add_workflow_system.sql` - Commented migration script
- Table comments in the database after migration
