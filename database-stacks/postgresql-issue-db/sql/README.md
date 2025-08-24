# Issue Management Database SQL Scripts

This directory contains all the SQL scripts needed to set up a comprehensive issue management database system.

## 📁 Files Overview

### **Core Setup Scripts**
- `setup_database.sql` - **Master script** that runs all others in correct order
- `01_create_schema.sql` - Creates tables, indexes, constraints, and enums
- `02_triggers_functions.sql` - Automated triggers and utility functions
- `03_initial_data.sql` - Populates initial users, projects, tags, and sample data
- `04_utility_queries.sql` - Common queries and helper functions

## 🚀 Quick Setup

### **Option 1: Run Master Script (Recommended)**

```bash
# Connect to database and run everything
psql -h 10.202.70.20 -p 5433 -U archon_user -d archon_issues -f setup_database.sql
```

### **Option 2: Run Scripts Individually**

```bash
# Run each script in order
psql -h 10.202.70.20 -p 5433 -U archon_user -d archon_issues -f 01_create_schema.sql
psql -h 10.202.70.20 -p 5433 -U archon_user -d archon_issues -f 02_triggers_functions.sql
psql -h 10.202.70.20 -p 5433 -U archon_user -d archon_issues -f 03_initial_data.sql
psql -h 10.202.70.20 -p 5433 -U archon_user -d archon_issues -f 04_utility_queries.sql
```

### **Option 3: Interactive psql Session**

```bash
# Connect to database
psql -h 10.202.70.20 -p 5433 -U archon_user -d archon_issues

# Run scripts interactively
\i setup_database.sql
```

## 📊 What Gets Created

### **Tables (7 core tables)**
- `projects` - Project organization
- `users` - Human users and AI agents
- `issues` - Core issue tracking
- `issue_history` - Complete audit trail
- `attachments` - File attachment metadata
- `tags` - Flexible categorization
- `issue_tags` - Many-to-many issue/tag relationships

### **Views (4 useful views)**
- `v_open_issues` - All open issues with assignee info
- `v_recent_activity` - Recent changes and activity
- `v_project_stats` - Statistics by project
- `v_tag_stats` - Tag usage statistics

### **Functions (6 utility functions)**
- `search_issues()` - Full-text search across issues
- `get_issue_stats()` - Project statistics
- `create_issue_with_tags()` - Create issue with automatic tagging
- `update_updated_date_column()` - Auto-update timestamps
- `generate_issue_key()` - Auto-generate issue keys (PROJ-123)
- `log_issue_change()` - Automatic audit trail

### **Triggers (8 automated triggers)**
- Automatic timestamp updates
- Issue key generation
- Complete audit trail logging
- Tag usage counting
- Attachment change logging

### **Initial Data**
- **5 Users**: System, Paddy, and 3 AI agents
- **6 Projects**: Archon Plus, Database, AI, UI, API, DevOps
- **30+ Tags**: Common categorization tags
- **1 Sample Issue**: For testing the system

## 🔧 Database Schema Features

### **Automatic Features**
- ✅ **Issue Keys**: Auto-generated (ARCH-1, DB-2, etc.)
- ✅ **Audit Trail**: Complete change history
- ✅ **Timestamps**: Auto-updated on changes
- ✅ **Tag Counting**: Usage statistics maintained
- ✅ **Data Integrity**: Foreign key constraints

### **Performance Optimizations**
- ✅ **Strategic Indexes**: For common query patterns
- ✅ **Full-text Search**: Optimized text searching
- ✅ **Composite Indexes**: Multi-column queries
- ✅ **Partial Indexes**: Conditional indexing

### **Flexible Design**
- ✅ **Tag System**: Unlimited categorization
- ✅ **User Types**: Humans and AI agents
- ✅ **File Attachments**: Metadata tracking
- ✅ **Custom Fields**: JSON preferences and labels

## 📋 Common Operations

### **Create a New Issue**
```sql
SELECT create_issue_with_tags(
    'Database connection timeout',
    'Connections timing out in production',
    1, -- project_id (Archon Plus)
    2, -- reporter_id (paddy)
    3, -- assignee_id (archon-agent)
    'high',
    'major',
    ARRAY['bug', 'production', 'database']
);
```

### **Search Issues**
```sql
-- Search by text
SELECT * FROM search_issues('database timeout');

-- View open issues
SELECT * FROM v_open_issues WHERE assignee_username = 'paddy';

-- Recent activity
SELECT * FROM v_recent_activity LIMIT 10;
```

### **Update Issue Status**
```sql
-- Set current user for audit trail
SELECT set_config('app.current_user_id', '2', false);

-- Update the issue
UPDATE issues 
SET status = 'in_progress', 
    assignee_id = 2 
WHERE issue_key = 'ARCH-1';
```

### **Add Tags to Issue**
```sql
INSERT INTO issue_tags (issue_id, tag_id, added_by)
SELECT 
    (SELECT issue_id FROM issues WHERE issue_key = 'ARCH-1'),
    tag_id,
    2 -- user_id adding the tag
FROM tags 
WHERE tag_name IN ('urgent', 'backend');
```

## 🔍 Useful Queries

### **Dashboard Queries**
```sql
-- My open issues
SELECT * FROM v_open_issues WHERE assignee_username = 'paddy';

-- Critical issues
SELECT * FROM v_open_issues WHERE priority = 'critical';

-- Overdue issues
SELECT issue_key, title, due_date, 
       CURRENT_DATE - due_date as days_overdue
FROM v_open_issues 
WHERE due_date < CURRENT_DATE;
```

### **Reporting Queries**
```sql
-- Project statistics
SELECT * FROM v_project_stats;

-- Issues created per day (last 30 days)
SELECT DATE(created_date) as date, COUNT(*) as issues_created
FROM issues
WHERE created_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_date)
ORDER BY date;

-- Tag usage
SELECT * FROM v_tag_stats ORDER BY current_usage DESC;
```

## 🛠️ Maintenance

### **Regular Maintenance**
```sql
-- Update table statistics
ANALYZE;

-- Check database size
SELECT pg_size_pretty(pg_database_size('archon_issues'));

-- Check table sizes
SELECT tablename, 
       pg_size_pretty(pg_total_relation_size(tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename) DESC;
```

### **Backup Recommendations**
- **Daily**: Full database backup
- **Hourly**: Transaction log backup
- **File System**: Separate backup of attachment files

## 🔐 Security Notes

- All operations are logged in `issue_history`
- User context tracked via `app.current_user_id` setting
- File attachments store metadata only (files stored separately)
- Soft deletes preserve referential integrity

## 📞 Support

For issues with the database setup:
1. Check PostgreSQL logs for errors
2. Verify all scripts ran successfully
3. Check the verification queries in `setup_database.sql`
4. Review the `issue_history` table for audit trail

## 🎯 Next Steps

After setup:
1. **Test the system** with sample issues
2. **Configure file storage** for attachments
3. **Set up backup procedures**
4. **Create application integration**
5. **Add monitoring and alerting**
