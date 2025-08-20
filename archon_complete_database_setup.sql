-- =====================================================
-- ARCHON COMPLETE DATABASE SETUP FOR SECOND INSTANCE
-- =====================================================
-- This script sets up a complete Archon database on Supabase
-- including all tables, indexes, triggers, RLS policies, and initial data
-- 
-- Run this script in your Supabase SQL Editor to set up
-- the complete Archon database schema and initial data
-- =====================================================

-- =====================================================
-- SECTION 1: EXTENSIONS
-- =====================================================

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =====================================================
-- SECTION 2: SETTINGS TABLE
-- =====================================================

-- Credentials and Configuration Management Table
-- This table stores both encrypted sensitive data and plain configuration settings
CREATE TABLE IF NOT EXISTS archon_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,                    -- For plain text config values
    encrypted_value TEXT,          -- For encrypted sensitive data (bcrypt hashed)
    is_encrypted BOOLEAN DEFAULT FALSE,
    category VARCHAR(100),         -- Group related settings (e.g., 'rag_strategy', 'api_keys', 'server_config')
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_archon_settings_key ON archon_settings(key);
CREATE INDEX IF NOT EXISTS idx_archon_settings_category ON archon_settings(category);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing trigger if it exists, then create it
DROP TRIGGER IF EXISTS update_archon_settings_updated_at ON archon_settings;
CREATE TRIGGER update_archon_settings_updated_at
    BEFORE UPDATE ON archon_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create RLS (Row Level Security) policies for settings
ALTER TABLE archon_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service role full access" ON archon_settings
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated users to read and update" ON archon_settings
    FOR ALL TO authenticated
    USING (true);

-- =====================================================
-- SECTION 3: INITIAL SETTINGS DATA
-- =====================================================

-- Insert default configuration values
INSERT INTO archon_settings (key, value, is_encrypted, category, description) VALUES
-- RAG Strategy Settings
('RAG_STRATEGY', 'hybrid', false, 'rag_strategy', 'RAG retrieval strategy: semantic, keyword, or hybrid'),
('CHUNK_SIZE', '1000', false, 'rag_strategy', 'Text chunk size for document processing'),
('CHUNK_OVERLAP', '200', false, 'rag_strategy', 'Overlap between text chunks'),
('MAX_CHUNKS', '10', false, 'rag_strategy', 'Maximum chunks to retrieve for RAG'),
('SIMILARITY_THRESHOLD', '0.7', false, 'rag_strategy', 'Minimum similarity score for chunk retrieval'),

-- LLM Provider Settings
('LLM_PROVIDER', 'openai', false, 'rag_strategy', 'LLM provider: openai, google, openrouter, ollama, huggingface, local'),
('LLM_MODEL', 'gpt-4o-mini', false, 'rag_strategy', 'LLM model name'),
('LLM_BASE_URL', NULL, false, 'rag_strategy', 'Custom base URL for LLM provider (overrides provider defaults)'),
('EMBEDDING_MODEL', 'text-embedding-3-small', false, 'rag_strategy', 'Embedding model name'),

-- Split Provider Settings (for separate chat and embedding providers)
('CHAT_PROVIDER', 'openai', false, 'rag_strategy', 'Chat/LLM provider: openai, google, openrouter, ollama, huggingface, local'),
('EMBEDDING_PROVIDER', 'openai', false, 'rag_strategy', 'Embedding provider: openai, google, ollama, huggingface, local'),
('CHAT_BASE_URL', NULL, false, 'rag_strategy', 'Custom base URL for chat provider (overrides provider defaults)'),
('EMBEDDING_BASE_URL', NULL, false, 'rag_strategy', 'Custom base URL for embedding provider (overrides provider defaults)'),

-- Code Extraction Settings
('EXTRACT_FUNCTIONS', 'true', false, 'code_extraction', 'Extract function definitions from code'),
('EXTRACT_CLASSES', 'true', false, 'code_extraction', 'Extract class definitions from code'),
('EXTRACT_IMPORTS', 'false', false, 'code_extraction', 'Extract import statements from code'),
('EXTRACT_COMMENTS', 'true', false, 'code_extraction', 'Extract comments from code'),
('MIN_FUNCTION_LENGTH', '3', false, 'code_extraction', 'Minimum lines for function extraction'),
('MAX_FUNCTION_LENGTH', '100', false, 'code_extraction', 'Maximum lines for function extraction'),

-- Server Configuration
('SERVER_PORT', '8181', false, 'server_config', 'Main server port'),
('MCP_PORT', '8051', false, 'server_config', 'MCP server port'),
('AGENTS_PORT', '8052', false, 'server_config', 'Agents server port'),
('LOG_LEVEL', 'INFO', false, 'server_config', 'Logging level: DEBUG, INFO, WARNING, ERROR'),
('CORS_ORIGINS', '["http://localhost:3000", "http://localhost:3737"]', false, 'server_config', 'Allowed CORS origins as JSON array'),

-- Feature Flags
('ENABLE_WORKFLOWS', 'true', false, 'features', 'Enable workflow orchestration system'),
('ENABLE_CODE_EXTRACTION', 'true', false, 'features', 'Enable automatic code extraction from crawled content'),
('ENABLE_SEMANTIC_SEARCH', 'true', false, 'features', 'Enable semantic search capabilities'),
('ENABLE_KEYWORD_SEARCH', 'true', false, 'features', 'Enable keyword search capabilities')

ON CONFLICT (key) DO NOTHING;

-- Insert encrypted API keys (initially NULL - to be set via admin interface)
INSERT INTO archon_settings (key, encrypted_value, is_encrypted, category, description) VALUES
('OPENAI_API_KEY', NULL, true, 'api_keys', 'OpenAI API Key for GPT models and embeddings. Get from: https://platform.openai.com/api-keys'),
('GOOGLE_API_KEY', NULL, true, 'api_keys', 'Google AI API Key for Gemini models. Get from: https://aistudio.google.com/app/apikey'),
('OPENROUTER_API_KEY', NULL, true, 'api_keys', 'OpenRouter API Key for various LLM models. Get from: https://openrouter.ai/keys'),
('HUGGINGFACE_API_KEY', NULL, true, 'api_keys', 'Hugging Face API Key for embedding models. Get from: https://huggingface.co/settings/tokens'),
('LOCAL_EMBEDDING_API_KEY', NULL, true, 'api_keys', 'API Key for local embedding server (if authentication required)')
ON CONFLICT (key) DO NOTHING;

-- Add a comment to document when this migration was added
COMMENT ON TABLE archon_settings IS 'Stores application configuration including API keys, RAG settings, split provider configuration, and code extraction parameters';

-- =====================================================
-- SECTION 4: KNOWLEDGE BASE TABLES
-- =====================================================

-- Create the sources table
CREATE TABLE IF NOT EXISTS archon_sources (
    source_id TEXT PRIMARY KEY,
    summary TEXT,
    total_word_count INTEGER DEFAULT 0,
    title TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_archon_sources_source_id ON archon_sources(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_sources_created_at ON archon_sources(created_at);
CREATE INDEX IF NOT EXISTS idx_archon_sources_metadata ON archon_sources USING GIN(metadata);

-- Create the documentation chunks table
CREATE TABLE IF NOT EXISTS archon_crawled_pages (
    id BIGSERIAL PRIMARY KEY,
    url VARCHAR NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_id TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI embeddings are 1536 dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Add a unique constraint to prevent duplicate chunks for the same URL
    UNIQUE(url, chunk_number),
    
    -- Add foreign key constraint to sources table
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id)
);

-- Create index for faster vector similarity searches
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_embedding ON archon_crawled_pages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create the code_examples table
CREATE TABLE IF NOT EXISTS archon_code_examples (
    id BIGSERIAL PRIMARY KEY,
    url VARCHAR NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,  -- The code example content
    summary TEXT NOT NULL,  -- Summary of the code example
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_id TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI embeddings are 1536 dimensions
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- Add a unique constraint to prevent duplicate chunks for the same URL
    UNIQUE(url, chunk_number),
    
    -- Add foreign key constraint to sources table
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id)
);

-- Create index for faster vector similarity searches
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_embedding ON archon_code_examples USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Additional indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_source_id ON archon_crawled_pages(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_url ON archon_crawled_pages(url);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_created_at ON archon_crawled_pages(created_at);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_metadata ON archon_crawled_pages USING GIN(metadata);

CREATE INDEX IF NOT EXISTS idx_archon_code_examples_source_id ON archon_code_examples(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_url ON archon_code_examples(url);
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_created_at ON archon_code_examples(created_at);
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_metadata ON archon_code_examples USING GIN(metadata);

-- Enable RLS on the knowledge base tables
ALTER TABLE archon_crawled_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_code_examples ENABLE ROW LEVEL SECURITY;

-- Create policies that allow anyone to read
CREATE POLICY "Allow public read access to archon_crawled_pages"
  ON archon_crawled_pages
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public read access to archon_sources"
  ON archon_sources
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public read access to archon_code_examples"
  ON archon_code_examples
  FOR SELECT
  TO public
  USING (true);

-- Allow service role full access to knowledge base tables
CREATE POLICY "Allow service role full access to archon_crawled_pages" ON archon_crawled_pages
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access to archon_sources" ON archon_sources
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access to archon_code_examples" ON archon_code_examples
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- SECTION 5: PROJECT MANAGEMENT SYSTEM
-- =====================================================

-- Create task status enum
CREATE TYPE task_status AS ENUM ('todo', 'doing', 'review', 'done');

-- Projects table
CREATE TABLE IF NOT EXISTS archon_projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  docs JSONB DEFAULT '[]'::jsonb,
  features JSONB DEFAULT '[]'::jsonb,
  data JSONB DEFAULT '[]'::jsonb,
  prd JSONB DEFAULT '{}'::jsonb,
  github_repo TEXT,
  pinned BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks table
CREATE TABLE IF NOT EXISTS archon_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
  parent_task_id UUID REFERENCES archon_tasks(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  status task_status DEFAULT 'todo',
  assignee TEXT DEFAULT 'User' CHECK (assignee IS NOT NULL AND assignee != ''),
  task_order INTEGER DEFAULT 0,
  feature TEXT,
  sources JSONB DEFAULT '[]'::jsonb,
  code_examples JSONB DEFAULT '[]'::jsonb,
  archived BOOLEAN DEFAULT false,
  archived_at TIMESTAMPTZ NULL,
  archived_by TEXT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project sources table for linking external resources
CREATE TABLE IF NOT EXISTS archon_project_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
  source_type TEXT NOT NULL CHECK (source_type IN ('documentation', 'repository', 'api', 'database', 'other')),
  source_url TEXT NOT NULL,
  source_name TEXT NOT NULL,
  description TEXT DEFAULT '',
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document versions table for version control
CREATE TABLE IF NOT EXISTS archon_document_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
  task_id UUID REFERENCES archon_tasks(id) ON DELETE SET NULL,
  field_name TEXT NOT NULL,
  version_number INTEGER NOT NULL,
  content JSONB NOT NULL,
  change_summary TEXT,
  change_type TEXT DEFAULT 'manual' CHECK (change_type IN ('manual', 'automatic')),
  document_id UUID,
  created_by TEXT DEFAULT 'system',
  created_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(project_id, field_name, version_number)
);

-- Prompts table for storing reusable prompts
CREATE TABLE IF NOT EXISTS archon_prompts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_name TEXT UNIQUE NOT NULL,
  prompt_content TEXT NOT NULL,
  description TEXT DEFAULT '',
  category TEXT DEFAULT 'general',
  variables JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_archon_projects_created_at ON archon_projects(created_at);
CREATE INDEX IF NOT EXISTS idx_archon_projects_pinned ON archon_projects(pinned);
CREATE INDEX IF NOT EXISTS idx_archon_projects_title ON archon_projects(title);

CREATE INDEX IF NOT EXISTS idx_archon_tasks_project_id ON archon_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_parent_task_id ON archon_tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_status ON archon_tasks(status);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_assignee ON archon_tasks(assignee);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_archived ON archon_tasks(archived);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_feature ON archon_tasks(feature);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_created_at ON archon_tasks(created_at);

CREATE INDEX IF NOT EXISTS idx_archon_project_sources_project_id ON archon_project_sources(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_project_sources_source_type ON archon_project_sources(source_type);

CREATE INDEX IF NOT EXISTS idx_archon_document_versions_project_id ON archon_document_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_task_id ON archon_document_versions(task_id);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_field_name ON archon_document_versions(field_name);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_version_number ON archon_document_versions(version_number);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_created_at ON archon_document_versions(created_at);

CREATE INDEX IF NOT EXISTS idx_archon_prompts_name ON archon_prompts(prompt_name);

-- Apply triggers to tables (drop existing first)
DROP TRIGGER IF EXISTS update_archon_projects_updated_at ON archon_projects;
CREATE TRIGGER update_archon_projects_updated_at
    BEFORE UPDATE ON archon_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_archon_tasks_updated_at ON archon_tasks;
CREATE TRIGGER update_archon_tasks_updated_at
    BEFORE UPDATE ON archon_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_archon_prompts_updated_at ON archon_prompts;
CREATE TRIGGER update_archon_prompts_updated_at
    BEFORE UPDATE ON archon_prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Soft delete function for tasks
CREATE OR REPLACE FUNCTION archive_task(
    task_id_param UUID,
    archived_by_param TEXT DEFAULT 'system'
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE archon_tasks
    SET
        archived = true,
        archived_at = NOW(),
        archived_by = archived_by_param,
        updated_at = NOW()
    WHERE id = task_id_param;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security (RLS) for all tables
ALTER TABLE archon_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_project_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_document_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_prompts ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for service role (full access)
CREATE POLICY "Allow service role full access to archon_projects" ON archon_projects
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access to archon_tasks" ON archon_tasks
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access to archon_project_sources" ON archon_project_sources
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access to archon_document_versions" ON archon_document_versions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access to archon_prompts" ON archon_prompts
    FOR ALL USING (auth.role() = 'service_role');

-- Create RLS policies for authenticated users (read access)
CREATE POLICY "Allow authenticated users to read archon_projects" ON archon_projects
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to read archon_tasks" ON archon_tasks
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to read archon_project_sources" ON archon_project_sources
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to read archon_document_versions" ON archon_document_versions
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to read archon_prompts" ON archon_prompts
    FOR SELECT TO authenticated USING (true);

-- =====================================================
-- SECTION 6: WORKFLOW ORCHESTRATION SYSTEM
-- =====================================================

-- Create workflow enums
CREATE TYPE workflow_status AS ENUM ('draft', 'active', 'deprecated', 'archived');
CREATE TYPE workflow_step_type AS ENUM ('action', 'condition', 'workflow_link');
CREATE TYPE workflow_execution_status AS ENUM ('pending', 'running', 'paused', 'completed', 'failed', 'cancelled');
CREATE TYPE step_execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'skipped', 'cancelled');

-- Workflow Templates - Define reusable workflow patterns
CREATE TABLE IF NOT EXISTS archon_workflow_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  version VARCHAR(50) DEFAULT '1.0.0',
  status workflow_status DEFAULT 'draft',

  -- Workflow metadata
  category VARCHAR(100), -- e.g., 'infrastructure', 'deployment', 'testing'
  tags JSONB DEFAULT '[]'::jsonb, -- Array of tags for categorization

  -- Workflow configuration
  parameters JSONB DEFAULT '{}'::jsonb, -- Input parameters schema
  outputs JSONB DEFAULT '{}'::jsonb, -- Expected outputs schema

  -- Workflow definition
  steps JSONB NOT NULL DEFAULT '[]'::jsonb, -- Array of workflow steps

  -- Execution settings
  timeout_minutes INTEGER DEFAULT 60,
  max_retries INTEGER DEFAULT 3,
  retry_delay_seconds INTEGER DEFAULT 30,

  -- Permissions and access
  created_by TEXT NOT NULL DEFAULT 'system',
  is_public BOOLEAN DEFAULT false,
  allowed_assignees JSONB DEFAULT '[]'::jsonb, -- Array of allowed assignees

  -- Audit fields
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT chk_workflow_name_format CHECK (name ~ '^[a-z0-9_-]+$'),
  CONSTRAINT chk_workflow_version_format CHECK (version ~ '^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'),
  CONSTRAINT chk_timeout_positive CHECK (timeout_minutes > 0),
  CONSTRAINT chk_retries_non_negative CHECK (max_retries >= 0)
);

-- Workflow Executions - Track individual workflow runs
CREATE TABLE IF NOT EXISTS archon_workflow_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_template_id UUID REFERENCES archon_workflow_templates(id) ON DELETE CASCADE,

  -- Execution context
  triggered_by TEXT NOT NULL DEFAULT 'system',
  trigger_context JSONB DEFAULT '{}'::jsonb, -- Task ID, event data, etc.
  input_parameters JSONB DEFAULT '{}'::jsonb,
  execution_context JSONB DEFAULT '{}'::jsonb, -- Runtime variables, state

  -- Execution status
  status workflow_execution_status DEFAULT 'pending',
  current_step_index INTEGER DEFAULT 0,
  total_steps INTEGER DEFAULT 0,
  progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),

  -- Timing
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  paused_at TIMESTAMPTZ,

  -- Results and errors
  output_data JSONB DEFAULT '{}'::jsonb,
  error_message TEXT,
  error_details JSONB DEFAULT '{}'::jsonb,

  -- Audit
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workflow Step Executions - Track individual step runs within workflows
CREATE TABLE IF NOT EXISTS archon_workflow_step_executions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_execution_id UUID REFERENCES archon_workflow_executions(id) ON DELETE CASCADE,

  -- Step identification
  step_index INTEGER NOT NULL,
  step_name TEXT NOT NULL,
  step_type workflow_step_type NOT NULL,

  -- Step configuration
  step_config JSONB DEFAULT '{}'::jsonb,
  input_data JSONB DEFAULT '{}'::jsonb,

  -- Execution details
  status step_execution_status DEFAULT 'pending',
  tool_name TEXT, -- MCP tool being executed
  tool_arguments JSONB DEFAULT '{}'::jsonb,

  -- Results
  output_data JSONB DEFAULT '{}'::jsonb,
  error_message TEXT,
  error_details JSONB DEFAULT '{}'::jsonb,

  -- Timing
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER,

  -- Retry tracking
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,

  -- Audit
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  CONSTRAINT chk_step_index_non_negative CHECK (step_index >= 0),
  CONSTRAINT chk_retry_count_non_negative CHECK (retry_count >= 0),
  CONSTRAINT chk_max_retries_non_negative CHECK (max_retries >= 0),
  CONSTRAINT chk_duration_non_negative CHECK (duration_ms IS NULL OR duration_ms >= 0)
);

-- Workflow Template Versions - Track template changes over time
CREATE TABLE IF NOT EXISTS archon_workflow_template_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id UUID REFERENCES archon_workflow_templates(id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,

  -- Snapshot of template at this version
  template_snapshot JSONB NOT NULL,

  -- Version metadata
  change_summary TEXT,
  change_type TEXT DEFAULT 'manual' CHECK (change_type IN ('manual', 'automatic')),
  created_by TEXT NOT NULL DEFAULT 'system',
  created_at TIMESTAMPTZ DEFAULT NOW(),

  -- Constraints
  UNIQUE(template_id, version_number),
  CONSTRAINT chk_version_number_positive CHECK (version_number > 0)
);

-- Create indexes for workflow system
CREATE UNIQUE INDEX IF NOT EXISTS idx_archon_workflow_templates_name ON archon_workflow_templates(name);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_templates_status ON archon_workflow_templates(status);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_templates_category ON archon_workflow_templates(category);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_templates_tags ON archon_workflow_templates USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_templates_created_by ON archon_workflow_templates(created_by);

CREATE INDEX IF NOT EXISTS idx_archon_workflow_executions_template_id ON archon_workflow_executions(workflow_template_id);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_executions_status ON archon_workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_executions_triggered_by ON archon_workflow_executions(triggered_by);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_executions_started_at ON archon_workflow_executions(started_at);

CREATE INDEX IF NOT EXISTS idx_archon_workflow_step_executions_execution_id ON archon_workflow_step_executions(workflow_execution_id);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_step_executions_step_index ON archon_workflow_step_executions(step_index);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_step_executions_status ON archon_workflow_step_executions(status);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_step_executions_tool_name ON archon_workflow_step_executions(tool_name);

CREATE INDEX IF NOT EXISTS idx_archon_workflow_template_versions_template_id ON archon_workflow_template_versions(template_id);
CREATE INDEX IF NOT EXISTS idx_archon_workflow_template_versions_version_number ON archon_workflow_template_versions(version_number);

-- Apply triggers to workflow tables (drop existing first)
DROP TRIGGER IF EXISTS update_archon_workflow_templates_updated_at ON archon_workflow_templates;
CREATE TRIGGER update_archon_workflow_templates_updated_at
    BEFORE UPDATE ON archon_workflow_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_archon_workflow_executions_updated_at ON archon_workflow_executions;
CREATE TRIGGER update_archon_workflow_executions_updated_at
    BEFORE UPDATE ON archon_workflow_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_archon_workflow_step_executions_updated_at ON archon_workflow_step_executions;
CREATE TRIGGER update_archon_workflow_step_executions_updated_at
    BEFORE UPDATE ON archon_workflow_step_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS on workflow tables
ALTER TABLE archon_workflow_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_workflow_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_workflow_step_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_workflow_template_versions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for public read access (following Archon patterns)
CREATE POLICY "Allow public read access to archon_workflow_templates"
  ON archon_workflow_templates
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public read access to archon_workflow_executions"
  ON archon_workflow_executions
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public read access to archon_workflow_step_executions"
  ON archon_workflow_step_executions
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public read access to archon_workflow_template_versions"
  ON archon_workflow_template_versions
  FOR SELECT
  TO public
  USING (true);

-- Create RLS policies for service role (full access)
CREATE POLICY "Allow service role full access to archon_workflow_templates" ON archon_workflow_templates
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access to archon_workflow_executions" ON archon_workflow_executions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access to archon_workflow_step_executions" ON archon_workflow_step_executions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access to archon_workflow_template_versions" ON archon_workflow_template_versions
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- SECTION 7: SAMPLE WORKFLOW TEMPLATES
-- =====================================================

-- Insert sample workflow templates for demonstration
INSERT INTO archon_workflow_templates
(name, title, description, category, tags, parameters, outputs, steps, timeout_minutes, max_retries, created_by, is_public)
VALUES
(
    'health_check_workflow',
    'System Health Check',
    'Performs a comprehensive system health check using MCP tools',
    'monitoring',
    '["health", "monitoring", "mcp"]'::jsonb,
    '{}'::jsonb,
    '{
        "health_status": {"type": "object", "description": "System health status"},
        "session_info": {"type": "object", "description": "Current session information"}
    }'::jsonb,
    '[
        {
            "name": "health_check",
            "type": "action",
            "description": "Check system health",
            "tool": "health_check_archon-dev",
            "arguments": {},
            "timeout_seconds": 30
        },
        {
            "name": "session_info",
            "type": "action",
            "description": "Get session information",
            "tool": "session_info_archon-dev",
            "arguments": {},
            "timeout_seconds": 15
        }
    ]'::jsonb,
    15,
    2,
    'system',
    true
),
(
    'project_setup_workflow',
    'Project Setup and Initialization',
    'Creates a new project with initial structure and documentation',
    'project_management',
    '["project", "setup", "initialization"]'::jsonb,
    '{
        "project_title": {"type": "string", "required": true, "description": "Project title"},
        "project_description": {"type": "string", "required": false, "description": "Project description"},
        "github_repo": {"type": "string", "required": false, "description": "GitHub repository URL"}
    }'::jsonb,
    '{
        "project_id": {"type": "string", "description": "Created project UUID"},
        "setup_status": {"type": "string", "description": "Setup completion status"}
    }'::jsonb,
    '[
        {
            "name": "create_project",
            "type": "action",
            "description": "Create new project",
            "tool": "manage_project_archon-dev",
            "arguments": {
                "action": "create",
                "title": "{{project_title}}",
                "github_repo": "{{github_repo}}"
            },
            "timeout_seconds": 60
        },
        {
            "name": "setup_initial_tasks",
            "type": "action",
            "description": "Create initial project tasks",
            "tool": "manage_task_archon-dev",
            "arguments": {
                "action": "create",
                "project_id": "{{create_project.project.id}}",
                "title": "Project Setup Complete",
                "description": "Initial project structure has been created",
                "assignee": "User"
            },
            "timeout_seconds": 30
        }
    ]'::jsonb,
    30,
    3,
    'system',
    true
)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- SECTION 8: COMPLETION MESSAGE
-- =====================================================

-- Log successful setup
DO $$
BEGIN
    RAISE NOTICE '🎉 ARCHON DATABASE SETUP COMPLETED SUCCESSFULLY!';
    RAISE NOTICE '================================================';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Created Extensions:';
    RAISE NOTICE '   - vector (for embeddings)';
    RAISE NOTICE '   - pgcrypto (for encryption)';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Created Tables:';
    RAISE NOTICE '   - archon_settings (configuration management)';
    RAISE NOTICE '   - archon_sources (knowledge base sources)';
    RAISE NOTICE '   - archon_crawled_pages (documentation chunks)';
    RAISE NOTICE '   - archon_code_examples (code examples)';
    RAISE NOTICE '   - archon_projects (project management)';
    RAISE NOTICE '   - archon_tasks (task tracking)';
    RAISE NOTICE '   - archon_project_sources (project resources)';
    RAISE NOTICE '   - archon_document_versions (version control)';
    RAISE NOTICE '   - archon_prompts (reusable prompts)';
    RAISE NOTICE '   - archon_workflow_templates (workflow definitions)';
    RAISE NOTICE '   - archon_workflow_executions (workflow runs)';
    RAISE NOTICE '   - archon_workflow_step_executions (step tracking)';
    RAISE NOTICE '   - archon_workflow_template_versions (template versions)';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Created Enums:';
    RAISE NOTICE '   - task_status (todo, doing, review, done)';
    RAISE NOTICE '   - workflow_status (draft, active, deprecated, archived)';
    RAISE NOTICE '   - workflow_step_type (action, condition, workflow_link)';
    RAISE NOTICE '   - workflow_execution_status (pending, running, paused, completed, failed, cancelled)';
    RAISE NOTICE '   - step_execution_status (pending, running, completed, failed, skipped, cancelled)';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Applied Security:';
    RAISE NOTICE '   - Row Level Security (RLS) policies';
    RAISE NOTICE '   - Service role full access';
    RAISE NOTICE '   - Public read access for knowledge base';
    RAISE NOTICE '   - Authenticated user read access for projects';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Added Performance Features:';
    RAISE NOTICE '   - Vector similarity search indexes';
    RAISE NOTICE '   - JSONB GIN indexes for metadata';
    RAISE NOTICE '   - Optimized query indexes';
    RAISE NOTICE '   - Automatic timestamp triggers';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Inserted Sample Data:';
    RAISE NOTICE '   - Default configuration settings';
    RAISE NOTICE '   - Sample workflow templates';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 NEXT STEPS:';
    RAISE NOTICE '1. Configure API keys in archon_settings table';
    RAISE NOTICE '2. Update Archon application connection strings';
    RAISE NOTICE '3. Test the setup with health check endpoints';
    RAISE NOTICE '4. Start uploading documents to build knowledge base';
    RAISE NOTICE '';
    RAISE NOTICE '📚 Your Archon database is ready for production use!';
    RAISE NOTICE '================================================';
END $$;
