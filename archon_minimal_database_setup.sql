-- =====================================================
-- ARCHON MINIMAL DATABASE SETUP FOR SECOND INSTANCE
-- =====================================================
-- This script sets up the essential Archon database tables
-- without workflow system for a lighter installation
-- 
-- Run this script in your Supabase SQL Editor for basic functionality
-- =====================================================

-- =====================================================
-- SECTION 1: EXTENSIONS
-- =====================================================

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- =====================================================
-- SECTION 2: CORE FUNCTIONS
-- =====================================================

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================================
-- SECTION 3: SETTINGS TABLE
-- =====================================================

-- Configuration Management Table
CREATE TABLE IF NOT EXISTS archon_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    encrypted_value TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    category VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes and triggers
CREATE INDEX IF NOT EXISTS idx_archon_settings_key ON archon_settings(key);
CREATE INDEX IF NOT EXISTS idx_archon_settings_category ON archon_settings(category);

-- Drop existing trigger if it exists, then create it
DROP TRIGGER IF EXISTS update_archon_settings_updated_at ON archon_settings;
CREATE TRIGGER update_archon_settings_updated_at
    BEFORE UPDATE ON archon_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE archon_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service role full access" ON archon_settings
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated users to read and update" ON archon_settings
    FOR ALL TO authenticated USING (true);

-- =====================================================
-- SECTION 4: KNOWLEDGE BASE TABLES
-- =====================================================

-- Sources table
CREATE TABLE IF NOT EXISTS archon_sources (
    source_id TEXT PRIMARY KEY,
    summary TEXT,
    total_word_count INTEGER DEFAULT 0,
    title TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Documentation chunks table
CREATE TABLE IF NOT EXISTS archon_crawled_pages (
    id BIGSERIAL PRIMARY KEY,
    url VARCHAR NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_id TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    UNIQUE(url, chunk_number),
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id)
);

-- Code examples table
CREATE TABLE IF NOT EXISTS archon_code_examples (
    id BIGSERIAL PRIMARY KEY,
    url VARCHAR NOT NULL,
    chunk_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_id TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    UNIQUE(url, chunk_number),
    FOREIGN KEY (source_id) REFERENCES archon_sources(source_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_archon_sources_source_id ON archon_sources(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_embedding ON archon_crawled_pages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_source_id ON archon_crawled_pages(source_id);
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_embedding ON archon_code_examples USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_source_id ON archon_code_examples(source_id);

-- Enable RLS
ALTER TABLE archon_crawled_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_code_examples ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow public read access to archon_crawled_pages" ON archon_crawled_pages FOR SELECT TO public USING (true);
CREATE POLICY "Allow public read access to archon_sources" ON archon_sources FOR SELECT TO public USING (true);
CREATE POLICY "Allow public read access to archon_code_examples" ON archon_code_examples FOR SELECT TO public USING (true);

CREATE POLICY "Allow service role full access to archon_crawled_pages" ON archon_crawled_pages FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow service role full access to archon_sources" ON archon_sources FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow service role full access to archon_code_examples" ON archon_code_examples FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- SECTION 5: PROJECT MANAGEMENT TABLES
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

-- Document versions table
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_archon_projects_created_at ON archon_projects(created_at);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_project_id ON archon_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_status ON archon_tasks(status);
CREATE INDEX IF NOT EXISTS idx_archon_document_versions_project_id ON archon_document_versions(project_id);

-- Apply triggers (drop existing first)
DROP TRIGGER IF EXISTS update_archon_projects_updated_at ON archon_projects;
CREATE TRIGGER update_archon_projects_updated_at
    BEFORE UPDATE ON archon_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_archon_tasks_updated_at ON archon_tasks;
CREATE TRIGGER update_archon_tasks_updated_at
    BEFORE UPDATE ON archon_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE archon_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon_document_versions ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow service role full access to archon_projects" ON archon_projects FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow service role full access to archon_tasks" ON archon_tasks FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow service role full access to archon_document_versions" ON archon_document_versions FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow authenticated users to read archon_projects" ON archon_projects FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated users to read archon_tasks" ON archon_tasks FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated users to read archon_document_versions" ON archon_document_versions FOR SELECT TO authenticated USING (true);

-- =====================================================
-- SECTION 6: ESSENTIAL SETTINGS
-- =====================================================

-- Insert essential configuration values
INSERT INTO archon_settings (key, value, is_encrypted, category, description) VALUES
('RAG_STRATEGY', 'hybrid', false, 'rag_strategy', 'RAG retrieval strategy: semantic, keyword, or hybrid'),
('CHUNK_SIZE', '1000', false, 'rag_strategy', 'Text chunk size for document processing'),
('LLM_PROVIDER', 'openai', false, 'rag_strategy', 'LLM provider: openai, google, openrouter, ollama'),
('LLM_MODEL', 'gpt-4o-mini', false, 'rag_strategy', 'LLM model name'),
('EMBEDDING_MODEL', 'text-embedding-3-small', false, 'rag_strategy', 'Embedding model name'),
('LOG_LEVEL', 'INFO', false, 'server_config', 'Logging level: DEBUG, INFO, WARNING, ERROR')
ON CONFLICT (key) DO NOTHING;

-- Insert API key placeholders
INSERT INTO archon_settings (key, encrypted_value, is_encrypted, category, description) VALUES
('OPENAI_API_KEY', NULL, true, 'api_keys', 'OpenAI API Key for GPT models and embeddings'),
('GOOGLE_API_KEY', NULL, true, 'api_keys', 'Google AI API Key for Gemini models')
ON CONFLICT (key) DO NOTHING;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '🎉 ARCHON MINIMAL DATABASE SETUP COMPLETED!';
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'Created: Settings, Knowledge Base, Projects, Tasks';
    RAISE NOTICE 'Next: Configure API keys and connection strings';
    RAISE NOTICE '==========================================';
END $$;
