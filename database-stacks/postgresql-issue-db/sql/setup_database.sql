-- ============================================================================
-- Issue Management Database - Master Setup Script
-- ============================================================================
-- 
-- This master script executes all the database setup scripts in the correct
-- order to create a complete issue management system.
--
-- Author: AI IDE Agent
-- Created: 2025-08-24
-- Database: archon_issues
-- 
-- Usage:
--   psql -h 10.202.70.20 -p 5433 -U archon_user -d archon_issues -f setup_database.sql
-- 
-- Or execute each script individually:
--   \i 01_create_schema.sql
--   \i 02_triggers_functions.sql
--   \i 03_initial_data.sql
--   \i 04_utility_queries.sql
-- ============================================================================

\echo '============================================================================'
\echo 'Starting Issue Management Database Setup'
\echo '============================================================================'

-- Check if we're connected to the right database
SELECT 
    current_database() as database_name,
    current_user as connected_user,
    version() as postgresql_version;

\echo ''
\echo 'Step 1: Creating database schema (tables, indexes, constraints)...'
\echo '============================================================================'

\i 01_create_schema.sql

\echo ''
\echo 'Step 2: Creating triggers and functions...'
\echo '============================================================================'

\i 02_triggers_functions.sql

\echo ''
\echo 'Step 3: Populating initial data...'
\echo '============================================================================'

\i 03_initial_data.sql

\echo ''
\echo 'Step 4: Loading utility queries and functions...'
\echo '============================================================================'

\i 04_utility_queries.sql

\echo ''
\echo '============================================================================'
\echo 'Database Setup Complete!'
\echo '============================================================================'

-- Final verification queries
\echo ''
\echo 'Verification: Checking created objects...'

-- Count tables
SELECT 
    'Tables created' as object_type,
    COUNT(*) as count
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE';

-- Count views
SELECT 
    'Views created' as object_type,
    COUNT(*) as count
FROM information_schema.views 
WHERE table_schema = 'public';

-- Count functions
SELECT 
    'Functions created' as object_type,
    COUNT(*) as count
FROM information_schema.routines 
WHERE routine_schema = 'public' 
  AND routine_type = 'FUNCTION';

-- Count triggers
SELECT 
    'Triggers created' as object_type,
    COUNT(*) as count
FROM information_schema.triggers 
WHERE trigger_schema = 'public';

-- Count initial data
SELECT 'Users' as data_type, COUNT(*) as count FROM users
UNION ALL
SELECT 'Projects' as data_type, COUNT(*) as count FROM projects
UNION ALL
SELECT 'Tags' as data_type, COUNT(*) as count FROM tags
UNION ALL
SELECT 'Issues' as data_type, COUNT(*) as count FROM issues
ORDER BY data_type;

\echo ''
\echo 'Sample queries to get started:'
\echo ''
\echo '-- View all open issues:'
\echo 'SELECT * FROM v_open_issues;'
\echo ''
\echo '-- View recent activity:'
\echo 'SELECT * FROM v_recent_activity LIMIT 10;'
\echo ''
\echo '-- Get project statistics:'
\echo 'SELECT * FROM v_project_stats;'
\echo ''
\echo '-- Search for issues:'
\echo 'SELECT * FROM search_issues(''database'');'
\echo ''
\echo '-- Create a new issue:'
\echo 'SELECT create_issue_with_tags('
\echo '    ''My new issue'','
\echo '    ''Description of the issue'','
\echo '    1, -- project_id'
\echo '    2, -- reporter_id'
\echo '    2, -- assignee_id'
\echo '    ''medium'','
\echo '    ''minor'','
\echo '    ARRAY[''bug'', ''development'']'
\echo ');'
\echo ''
\echo '============================================================================'
\echo 'Ready to start tracking issues!'
\echo '============================================================================'
