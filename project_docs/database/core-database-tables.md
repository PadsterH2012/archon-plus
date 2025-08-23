# Core Database Tables Documentation

**File Path:** `archon_complete_database_setup.sql` and related migration files
**Last Updated:** 2025-08-22

## Purpose
Comprehensive documentation of all core database tables in the Archon Plus system. This covers the complete PostgreSQL schema including knowledge base, project management, workflow orchestration, and template injection systems.

## Database Overview

The Archon database uses **PostgreSQL with Supabase** and includes:
- **Vector embeddings** for semantic search (pgvector extension)
- **JSONB fields** for flexible metadata storage
- **Row Level Security (RLS)** for access control
- **Automatic timestamps** with triggers
- **Foreign key constraints** for data integrity

## Core Table Categories

### 1. Configuration & Settings
### 2. Knowledge Base System  
### 3. Project Management System
### 4. Workflow Orchestration System
### 5. Template Injection System

---

## 1. Configuration & Settings Tables

### `archon_settings`
**Purpose:** Stores application configuration including API keys, RAG settings, and feature flags

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| `key` | VARCHAR(255) | UNIQUE NOT NULL | Configuration key name |
| `value` | TEXT | NULL | Plain text configuration value |
| `encrypted_value` | TEXT | NULL | Encrypted sensitive data (bcrypt hashed) |
| `is_encrypted` | BOOLEAN | DEFAULT FALSE | Whether value is encrypted |
| `category` | VARCHAR(100) | NULL | Group related settings (e.g., 'rag_strategy', 'api_keys') |
| `description` | TEXT | NULL | Human-readable description |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_archon_settings_key` on `key`
- `idx_archon_settings_category` on `category`

**Triggers:**
- `update_archon_settings_updated_at` - Auto-updates `updated_at` on changes

**Sample Categories:**
- `rag_strategy` - RAG configuration (chunk size, similarity threshold)
- `api_keys` - Encrypted API keys (OpenAI, Google, OpenRouter)
- `server_config` - Server ports and CORS settings
- `features` - Feature flags (workflows, code extraction)
- `code_extraction` - Code parsing settings

---

## 2. Knowledge Base System Tables

### `archon_sources`
**Purpose:** Manages knowledge base sources (websites, documents, files)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `source_id` | TEXT | PRIMARY KEY | Unique source identifier |
| `summary` | TEXT | NULL | Source summary/description |
| `total_word_count` | INTEGER | DEFAULT 0 | Total words across all chunks |
| `title` | TEXT | NULL | Human-readable source title |
| `metadata` | JSONB | DEFAULT '{}' | Flexible metadata (knowledge_type, tags, etc.) |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_archon_sources_source_id` on `source_id`
- `idx_archon_sources_created_at` on `created_at`
- `idx_archon_sources_metadata` GIN index on `metadata`

**Metadata Structure:**
```json
{
  "knowledge_type": "technical|business",
  "tags": ["api", "documentation"],
  "source_type": "url|file",
  "status": "active|processing|error",
  "file_name": "document.pdf",
  "page_count": 25,
  "update_frequency": 7,
  "group_name": "API Documentation"
}
```

### `archon_crawled_pages`
**Purpose:** Stores document chunks with vector embeddings for semantic search

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Auto-incrementing ID |
| `url` | VARCHAR | NOT NULL | Source URL or file path |
| `chunk_number` | INTEGER | NOT NULL | Chunk sequence number |
| `content` | TEXT | NOT NULL | Text content of chunk |
| `metadata` | JSONB | DEFAULT '{}' | Chunk-specific metadata |
| `source_id` | TEXT | NOT NULL, FK to archon_sources | Parent source reference |
| `embedding` | VECTOR(1536) | NULL | OpenAI embedding vector |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |

**Constraints:**
- `UNIQUE(url, chunk_number)` - Prevents duplicate chunks
- `FOREIGN KEY (source_id) REFERENCES archon_sources(source_id)`

**Indexes:**
- `idx_archon_crawled_pages_embedding` - IVFFlat vector similarity search
- `idx_archon_crawled_pages_source_id` on `source_id`
- `idx_archon_crawled_pages_url` on `url`
- `idx_archon_crawled_pages_metadata` GIN index on `metadata`

### `archon_code_examples`
**Purpose:** Stores extracted code examples with embeddings for code-specific search

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | BIGSERIAL | PRIMARY KEY | Auto-incrementing ID |
| `url` | VARCHAR | NOT NULL | Source URL or file path |
| `chunk_number` | INTEGER | NOT NULL | Code example sequence number |
| `content` | TEXT | NOT NULL | Raw code content |
| `summary` | TEXT | NOT NULL | AI-generated code summary |
| `metadata` | JSONB | DEFAULT '{}' | Code-specific metadata |
| `source_id` | TEXT | NOT NULL, FK to archon_sources | Parent source reference |
| `embedding` | VECTOR(1536) | NULL | Code embedding vector |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |

**Constraints:**
- `UNIQUE(url, chunk_number)` - Prevents duplicate code examples
- `FOREIGN KEY (source_id) REFERENCES archon_sources(source_id)`

**Indexes:**
- `idx_archon_code_examples_embedding` - IVFFlat vector similarity search
- `idx_archon_code_examples_source_id` on `source_id`
- `idx_archon_code_examples_metadata` GIN index on `metadata`

**Code Metadata Structure:**
```json
{
  "language": "python",
  "function_name": "process_data",
  "class_name": "DataProcessor",
  "imports": ["pandas", "numpy"],
  "complexity": "medium",
  "line_count": 45
}
```

---

## Related Files
- **Parent components:** Supabase PostgreSQL database
- **Child components:** All Archon services and API endpoints
- **Shared utilities:** Database client manager, storage services

## Notes
- All tables use `archon_` prefix for namespace isolation
- Vector embeddings use OpenAI's 1536-dimension format
- JSONB fields provide flexibility while maintaining query performance
- RLS policies ensure proper access control (service role full access, public read for knowledge base)
- Automatic timestamp triggers maintain audit trails
- Foreign key constraints ensure referential integrity

---

## 3. Project Management System Tables

### `archon_projects`
**Purpose:** Stores project definitions with documents, features, and metadata

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique project identifier |
| `title` | TEXT | NOT NULL | Project title |
| `description` | TEXT | DEFAULT '' | Project description |
| `docs` | JSONB | DEFAULT '[]' | Array of project documents |
| `features` | JSONB | DEFAULT '[]' | Array of project features |
| `data` | JSONB | DEFAULT '[]' | Project data and configurations |
| `prd` | JSONB | DEFAULT '{}' | Product Requirements Document |
| `github_repo` | TEXT | NULL | GitHub repository URL |
| `pinned` | BOOLEAN | DEFAULT FALSE | Whether project is pinned |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes:**
- `idx_archon_projects_created_at` on `created_at`
- `idx_archon_projects_pinned` on `pinned`
- `idx_archon_projects_title` on `title`

**Triggers:**
- `update_archon_projects_updated_at` - Auto-updates `updated_at`

### `archon_tasks`
**Purpose:** Task tracking and management with hierarchical structure

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique task identifier |
| `project_id` | UUID | FK to archon_projects, CASCADE DELETE | Parent project |
| `parent_task_id` | UUID | FK to archon_tasks, CASCADE DELETE | Parent task (for subtasks) |
| `title` | TEXT | NOT NULL | Task title |
| `description` | TEXT | DEFAULT '' | Task description |
| `status` | task_status | DEFAULT 'todo' | Current status (todo, doing, review, done) |
| `assignee` | TEXT | DEFAULT 'User', NOT NULL | Assigned agent/user |
| `task_order` | INTEGER | DEFAULT 0 | Sort order within status |
| `feature` | TEXT | NULL | Feature grouping label |
| `sources` | JSONB | DEFAULT '[]' | Related knowledge sources |
| `code_examples` | JSONB | DEFAULT '[]' | Related code examples |
| `template_metadata` | JSONB | DEFAULT '{}' | Template injection metadata |
| `archived` | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| `archived_at` | TIMESTAMPTZ | NULL | Archive timestamp |
| `archived_by` | TEXT | NULL | Who archived the task |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Enums:**
- `task_status`: 'todo', 'doing', 'review', 'done'

**Indexes:**
- `idx_archon_tasks_project_id` on `project_id`
- `idx_archon_tasks_parent_task_id` on `parent_task_id`
- `idx_archon_tasks_status` on `status`
- `idx_archon_tasks_assignee` on `assignee`
- `idx_archon_tasks_archived` on `archived`
- `idx_archon_tasks_feature` on `feature`

### `archon_project_sources`
**Purpose:** Links external resources to projects

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| `project_id` | UUID | FK to archon_projects, CASCADE DELETE | Parent project |
| `source_type` | TEXT | CHECK IN ('documentation', 'repository', 'api', 'database', 'other') | Resource type |
| `source_url` | TEXT | NOT NULL | Resource URL |
| `source_name` | TEXT | NOT NULL | Human-readable name |
| `description` | TEXT | DEFAULT '' | Resource description |
| `metadata` | JSONB | DEFAULT '{}' | Additional metadata |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

### `archon_document_versions`
**Purpose:** Version control for project documents and data

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique version identifier |
| `project_id` | UUID | FK to archon_projects, CASCADE DELETE | Parent project |
| `task_id` | UUID | FK to archon_tasks, SET NULL | Related task (optional) |
| `field_name` | TEXT | NOT NULL | Field being versioned (docs, features, data, prd) |
| `version_number` | INTEGER | NOT NULL | Incremental version number |
| `content` | JSONB | NOT NULL | Complete content snapshot |
| `change_summary` | TEXT | NULL | Description of changes |
| `change_type` | TEXT | DEFAULT 'manual', CHECK IN ('manual', 'automatic') | Change type |
| `document_id` | UUID | NULL | Specific document ID within array |
| `created_by` | TEXT | DEFAULT 'system' | Who made the change |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Version creation timestamp |

**Constraints:**
- `UNIQUE(project_id, field_name, version_number)` - Prevents duplicate versions

### `archon_prompts`
**Purpose:** Stores reusable prompts for AI interactions

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| `prompt_name` | TEXT | UNIQUE NOT NULL | Prompt identifier |
| `prompt_content` | TEXT | NOT NULL | Prompt template content |
| `description` | TEXT | DEFAULT '' | Prompt description |
| `category` | TEXT | DEFAULT 'general' | Prompt category |
| `variables` | JSONB | DEFAULT '[]' | Template variables |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Functions:**
- `archive_task(task_id_param UUID, archived_by_param TEXT)` - Soft delete function

---

## 4. Workflow Orchestration System Tables

### `archon_workflow_templates`
**Purpose:** Defines reusable workflow patterns for automation

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique template identifier |
| `name` | VARCHAR(255) | NOT NULL, CHECK format ^[a-z0-9_-]+$ | System name (snake_case) |
| `title` | TEXT | NOT NULL | Human-readable display name |
| `description` | TEXT | DEFAULT '' | Workflow description |
| `version` | VARCHAR(50) | DEFAULT '1.0.0', CHECK semver format | Semantic version |
| `status` | workflow_status | DEFAULT 'draft' | Lifecycle status |
| `category` | VARCHAR(100) | NULL | Grouping category |
| `tags` | JSONB | DEFAULT '[]' | Array of tags |
| `parameters` | JSONB | DEFAULT '{}' | Input parameters schema |
| `outputs` | JSONB | DEFAULT '{}' | Expected outputs schema |
| `steps` | JSONB | DEFAULT '[]' | Array of workflow steps |
| `timeout_minutes` | INTEGER | DEFAULT 60, CHECK > 0 | Maximum execution time |
| `max_retries` | INTEGER | DEFAULT 3, CHECK >= 0 | Retry attempts |
| `retry_delay_seconds` | INTEGER | DEFAULT 30 | Delay between retries |
| `created_by` | TEXT | DEFAULT 'system' | Creator identifier |
| `is_public` | BOOLEAN | DEFAULT FALSE | Public availability |
| `allowed_assignees` | JSONB | DEFAULT '[]' | Array of allowed assignees |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Enums:**
- `workflow_status`: 'draft', 'active', 'deprecated', 'archived'
- `workflow_step_type`: 'action', 'condition', 'workflow_link'

**Indexes:**
- `idx_archon_workflow_templates_name` UNIQUE on `name`
- `idx_archon_workflow_templates_status` on `status`
- `idx_archon_workflow_templates_category` on `category`
- `idx_archon_workflow_templates_tags` GIN on `tags`

**Step Definition Structure:**
```json
{
  "name": "create_vm",
  "type": "action",
  "tool_name": "manage_infrastructure",
  "parameters": {
    "action": "create_vm",
    "template": "{{workflow.parameters.vm_template}}"
  },
  "timeout_seconds": 300,
  "on_success": "next",
  "on_failure": "retry",
  "retry_count": 3
}
```

### `archon_workflow_executions`
**Purpose:** Tracks individual workflow execution instances

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique execution identifier |
| `workflow_template_id` | UUID | FK to archon_workflow_templates, CASCADE DELETE | Template being executed |
| `triggered_by` | TEXT | DEFAULT 'system' | Agent/user who started execution |
| `trigger_context` | JSONB | DEFAULT '{}' | Context data (task ID, event data) |
| `input_parameters` | JSONB | DEFAULT '{}' | Actual input values |
| `execution_context` | JSONB | DEFAULT '{}' | Runtime variables and state |
| `status` | workflow_execution_status | DEFAULT 'pending' | Current execution status |
| `current_step_index` | INTEGER | DEFAULT 0 | Index of currently executing step |
| `total_steps` | INTEGER | DEFAULT 0 | Total number of steps |
| `progress_percentage` | INTEGER | DEFAULT 0, CHECK 0-100 | Calculated progress |
| `started_at` | TIMESTAMPTZ | NULL | Execution start time |
| `completed_at` | TIMESTAMPTZ | NULL | Execution completion time |
| `paused_at` | TIMESTAMPTZ | NULL | Pause timestamp |
| `output_data` | JSONB | DEFAULT '{}' | Final results |
| `error_message` | TEXT | NULL | Error description |
| `error_details` | JSONB | DEFAULT '{}' | Detailed error information |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Enums:**
- `workflow_execution_status`: 'pending', 'running', 'paused', 'completed', 'failed', 'cancelled'

### `archon_workflow_step_executions`
**Purpose:** Records detailed execution information for each workflow step

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique step execution identifier |
| `workflow_execution_id` | UUID | FK to archon_workflow_executions, CASCADE DELETE | Parent execution |
| `step_index` | INTEGER | NOT NULL, CHECK >= 0 | Position in workflow |
| `step_name` | TEXT | NOT NULL | Name of the step |
| `step_type` | workflow_step_type | NOT NULL | Type of step |
| `step_config` | JSONB | DEFAULT '{}' | Step configuration snapshot |
| `input_data` | JSONB | DEFAULT '{}' | Step input data |
| `status` | step_execution_status | DEFAULT 'pending' | Step execution status |
| `tool_name` | TEXT | NULL | MCP tool being executed |
| `tool_arguments` | JSONB | DEFAULT '{}' | Tool execution arguments |
| `output_data` | JSONB | DEFAULT '{}' | Step output data |
| `error_message` | TEXT | NULL | Error description |
| `error_details` | JSONB | DEFAULT '{}' | Detailed error information |
| `started_at` | TIMESTAMPTZ | NULL | Step start time |
| `completed_at` | TIMESTAMPTZ | NULL | Step completion time |
| `duration_ms` | INTEGER | CHECK >= 0 | Execution duration |
| `retry_count` | INTEGER | DEFAULT 0, CHECK >= 0 | Current retry attempt |
| `max_retries` | INTEGER | DEFAULT 3, CHECK >= 0 | Maximum retry attempts |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Enums:**
- `step_execution_status`: 'pending', 'running', 'completed', 'failed', 'skipped', 'cancelled'

### `archon_workflow_template_versions`
**Purpose:** Maintains complete version history for workflow templates

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique version identifier |
| `template_id` | UUID | FK to archon_workflow_templates, CASCADE DELETE | Template being versioned |
| `version_number` | INTEGER | NOT NULL, CHECK > 0 | Incremental version number |
| `template_snapshot` | JSONB | NOT NULL | Complete template data snapshot |
| `change_summary` | TEXT | NULL | Description of changes |
| `change_type` | TEXT | DEFAULT 'manual', CHECK IN ('manual', 'automatic') | Type of change |
| `created_by` | TEXT | DEFAULT 'system' | Who made the changes |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Version creation timestamp |

**Constraints:**
- `UNIQUE(template_id, version_number)` - Prevents duplicate versions

---

## 5. Template Injection System Tables

### `archon_template_injection_templates`
**Purpose:** Template definitions with placeholders for workflow injection

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique template identifier |
| `name` | VARCHAR(255) | UNIQUE NOT NULL | Template name (e.g., "workflow::default") |
| `description` | TEXT | DEFAULT '' | Template description |
| `template_type` | template_injection_type | DEFAULT 'workflow' | Type of template |
| `injection_level` | template_injection_level | DEFAULT 'task' | Injection level |
| `template_content` | TEXT | NOT NULL | Template with {{placeholder}} variables |
| `user_task_position` | INTEGER | DEFAULT 6 | Where {{USER_TASK}} appears in sequence |
| `estimated_duration` | INTEGER | DEFAULT 30 | Total estimated duration in minutes |
| `required_tools` | JSONB | DEFAULT '[]' | MCP tools needed for template |
| `applicable_phases` | JSONB | DEFAULT phases array | Development phases where applicable |
| `is_active` | BOOLEAN | DEFAULT TRUE | Whether template is active |
| `version` | VARCHAR(50) | DEFAULT '1.0.0' | Template version |
| `author` | VARCHAR(255) | DEFAULT 'archon-system' | Template author |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Enums:**
- `template_injection_type`: 'workflow', 'component', 'validation'
- `template_injection_level`: 'project', 'milestone', 'phase', 'task', 'subtask'

### `archon_template_components`
**Purpose:** Expandable instruction components for building templates

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique component identifier |
| `name` | VARCHAR(255) | UNIQUE NOT NULL | Component name (e.g., "group::understand_homelab_env") |
| `description` | TEXT | DEFAULT '' | Component description |
| `component_type` | template_component_type | DEFAULT 'group' | Type of component |
| `instruction_text` | TEXT | NOT NULL | Full expanded instruction text |
| `required_tools` | JSONB | DEFAULT '[]' | MCP tools needed |
| `estimated_duration` | INTEGER | DEFAULT 5 | Estimated duration in minutes |
| `input_requirements` | JSONB | DEFAULT '{}' | Required context/data |
| `output_expectations` | JSONB | DEFAULT '{}' | Expected outputs |
| `validation_criteria` | JSONB | DEFAULT '[]' | Success verification criteria |
| `category` | VARCHAR(100) | DEFAULT 'general' | Component category |
| `priority` | VARCHAR(20) | DEFAULT 'medium' | Priority level (low, medium, high, critical) |
| `tags` | JSONB | DEFAULT '[]' | Flexible tagging for search |
| `is_active` | BOOLEAN | DEFAULT TRUE | Whether component is active |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Enums:**
- `template_component_type`: 'action', 'group', 'sequence', 'validation'

### `archon_template_assignments`
**Purpose:** Hierarchy-level template assignments for automatic injection

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique assignment identifier |
| `hierarchy_type` | template_hierarchy_type | NOT NULL | Type of hierarchy level |
| `hierarchy_id` | UUID | NOT NULL | Reference to project/task/etc. |
| `template_id` | UUID | FK to archon_template_injection_templates, CASCADE DELETE | Assigned template |
| `assignment_context` | JSONB | DEFAULT '{}' | Conditions and context |
| `priority` | INTEGER | DEFAULT 0 | Priority for conflict resolution |
| `conditional_logic` | JSONB | DEFAULT '{}' | Conditions for assignment |
| `is_active` | BOOLEAN | DEFAULT TRUE | Whether assignment is active |
| `assigned_at` | TIMESTAMPTZ | DEFAULT NOW() | Assignment timestamp |
| `assigned_by` | VARCHAR(255) | DEFAULT 'system' | Who made the assignment |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Constraints:**
- `UNIQUE(hierarchy_type, hierarchy_id, template_id)` - One template per hierarchy level

**Enums:**
- `template_hierarchy_type`: 'project', 'milestone', 'phase', 'task', 'subtask'

---

## Security & Access Control

### Row Level Security (RLS)
All tables have RLS enabled with the following policies:

**Service Role Access:**
- Full CRUD access to all tables for `service_role`

**Public Access:**
- Read-only access to knowledge base tables (`archon_sources`, `archon_crawled_pages`, `archon_code_examples`)
- Read-only access to workflow templates and executions

**Authenticated Users:**
- Read access to project management tables
- Read access to configuration settings (non-encrypted values)

### Data Integrity

**Foreign Key Constraints:**
- Cascade deletes maintain referential integrity
- SET NULL for optional relationships
- Prevents orphaned records

**Check Constraints:**
- Enum validation for status fields
- Positive number validation for durations and counts
- Format validation for names and versions

**Unique Constraints:**
- Prevent duplicate configurations, templates, and versions
- Ensure data consistency across related tables

---

## Performance Optimizations

### Vector Search
- IVFFlat indexes on embedding columns for fast similarity search
- Optimized for 1536-dimension OpenAI embeddings
- Configurable list size (100) for index performance

### JSONB Indexing
- GIN indexes on all JSONB metadata fields
- Enables fast queries on nested JSON properties
- Supports complex filtering and aggregation

### Query Optimization
- Strategic indexes on frequently queried columns
- Composite indexes for common query patterns
- Automatic statistics collection for query planning

---
*Auto-generated documentation - verify accuracy before use*
