# Archon Database Setup Guide

This guide provides SQL scripts to set up a complete Archon database on Supabase.

## 📁 Available Scripts

### 1. `archon_complete_database_setup.sql` (Recommended)
**Complete setup with all features including workflow system**

- ✅ All core tables (settings, knowledge base, projects, tasks)
- ✅ Workflow orchestration system
- ✅ Document version control
- ✅ Sample workflow templates
- ✅ Complete RLS policies and indexes
- ✅ Initial configuration data

**Size:** ~800 lines | **Features:** Full Archon functionality

### 2. `archon_minimal_database_setup.sql`
**Minimal setup for basic functionality**

- ✅ Core tables (settings, knowledge base, projects, tasks)
- ✅ Essential RLS policies and indexes
- ✅ Basic configuration data
- ❌ No workflow system
- ❌ No sample data

**Size:** ~300 lines | **Features:** Basic Archon functionality

## 🚀 Setup Instructions

### Step 1: Choose Your Setup
- **For production/full features:** Use `archon_complete_database_setup.sql`
- **For testing/minimal setup:** Use `archon_minimal_database_setup.sql`

### Step 2: Run the Script
1. Open your Supabase dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the chosen SQL script
4. Click **Run** to execute

### Step 3: Verify Setup
The script will output a completion message showing:
- ✅ Created tables and extensions
- ✅ Applied security policies
- ✅ Inserted initial data

### Step 4: Configure API Keys
After setup, configure your API keys in the `archon_settings` table:

```sql
-- Update OpenAI API Key
UPDATE archon_settings 
SET encrypted_value = crypt('your-openai-api-key', gen_salt('bf'))
WHERE key = 'OPENAI_API_KEY';

-- Update Google API Key (if using Google models)
UPDATE archon_settings 
SET encrypted_value = crypt('your-google-api-key', gen_salt('bf'))
WHERE key = 'GOOGLE_API_KEY';
```

### Step 5: Update Connection Strings
Update your Archon application configuration to point to the new database:

```env
SUPABASE_URL=https://your-new-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

## 📊 Database Schema Overview

### Core Tables Created

| Table | Purpose | Records |
|-------|---------|---------|
| `archon_settings` | Configuration management | ~20 settings |
| `archon_sources` | Knowledge base sources | User data |
| `archon_crawled_pages` | Document chunks with embeddings | User data |
| `archon_code_examples` | Code examples with embeddings | User data |
| `archon_projects` | Project management | User data |
| `archon_tasks` | Task tracking | User data |
| `archon_document_versions` | Version control | User data |

### Workflow Tables (Complete Setup Only)

| Table | Purpose |
|-------|---------|
| `archon_workflow_templates` | Workflow definitions |
| `archon_workflow_executions` | Workflow runs |
| `archon_workflow_step_executions` | Step tracking |
| `archon_workflow_template_versions` | Template versions |

## 🔒 Security Features

- **Row Level Security (RLS)** enabled on all tables
- **Service role** has full access for API operations
- **Public read access** for knowledge base tables
- **Authenticated user access** for project tables
- **Encrypted storage** for API keys using bcrypt

## 🎯 Default Configuration

The setup includes sensible defaults:

- **RAG Strategy:** Hybrid (semantic + keyword)
- **Chunk Size:** 1000 characters
- **LLM Provider:** OpenAI
- **Model:** GPT-4o-mini
- **Embedding Model:** text-embedding-3-small
- **Log Level:** INFO

## 🔧 Customization

After setup, you can customize settings via the `archon_settings` table:

```sql
-- Change LLM provider
UPDATE archon_settings SET value = 'google' WHERE key = 'LLM_PROVIDER';

-- Adjust chunk size
UPDATE archon_settings SET value = '1500' WHERE key = 'CHUNK_SIZE';

-- Enable debug logging
UPDATE archon_settings SET value = 'DEBUG' WHERE key = 'LOG_LEVEL';
```

## 🆘 Troubleshooting

### Common Issues

1. **Extension not found:** Ensure `vector` extension is available in your Supabase project
2. **Permission denied:** Make sure you're running as database owner or with sufficient privileges
3. **Constraint violations:** Check for existing data that might conflict with new constraints

### Reset Database (⚠️ Destructive)
If you need to start over, you can use the reset script from the original migration folder:

```sql
-- WARNING: This deletes ALL data!
-- Run migration/RESET_DB.sql first, then your chosen setup script
```

## 📞 Support

If you encounter issues:
1. Check the Supabase logs for detailed error messages
2. Verify all prerequisites are met
3. Ensure your Supabase project has the required extensions enabled

## 🎉 Success!

Once setup is complete, your Archon database will be ready for:
- Document ingestion and RAG queries
- Project and task management
- Workflow orchestration (complete setup)
- Knowledge base operations
- Multi-agent coordination

Your Archon instance can now connect to this database and begin operations!
