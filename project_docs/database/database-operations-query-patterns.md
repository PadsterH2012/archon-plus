# Database Operations & Query Patterns Documentation

**File Path:** Various database operation files across the codebase
**Last Updated:** 2025-08-22

## Purpose
Comprehensive documentation of database operations, query patterns, vector similarity searches, complex joins, aggregation queries, bulk operations, and performance optimization patterns used throughout the Archon Plus system.

## Props/Parameters
Operations use Supabase client with PostgreSQL-compatible SQL and vector extensions

## Dependencies

### Imports
```python
from supabase import Client
from typing import Any, Dict, List, Optional, Tuple
import asyncio
import logging
```

### Database Extensions
- **pgvector** - Vector similarity search
- **GIN indexes** - JSONB query optimization
- **IVFFlat indexes** - Vector search performance
- **RLS policies** - Row Level Security

## Core Query Pattern Categories

### 1. Vector Similarity Search Patterns
### 2. Complex Join Operations
### 3. Aggregation & Analytics Queries
### 4. Bulk Operations & Batch Processing
### 5. Performance Optimization Patterns
### 6. Real-time Query Patterns

---

## 1. Vector Similarity Search Patterns

### Basic Vector Search Function
**Purpose:** Core semantic search using vector embeddings

```sql
-- PostgreSQL function for vector similarity search
CREATE OR REPLACE FUNCTION match_archon_crawled_pages(
  query_embedding vector(1536),
  match_count int DEFAULT 10,
  filter jsonb DEFAULT '{}'::jsonb,
  source_filter text DEFAULT NULL
) RETURNS TABLE (
  id bigint,
  url varchar,
  chunk_number integer,
  content text,
  metadata jsonb,
  source_id text,
  similarity float
)
LANGUAGE plpgsql
AS $$
#variable_conflict use_column
BEGIN
  RETURN QUERY
  SELECT
    archon_crawled_pages.id,
    archon_crawled_pages.url,
    archon_crawled_pages.chunk_number,
    archon_crawled_pages.content,
    archon_crawled_pages.metadata,
    archon_crawled_pages.source_id,
    1 - (archon_crawled_pages.embedding <=> query_embedding) as similarity
  FROM archon_crawled_pages
  WHERE 
    (source_filter IS NULL OR archon_crawled_pages.source_id = source_filter)
    AND (filter = '{}'::jsonb OR archon_crawled_pages.metadata @> filter)
  ORDER BY archon_crawled_pages.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

### Code Example Vector Search
**Purpose:** Specialized search for code examples with enhanced metadata

```sql
CREATE OR REPLACE FUNCTION match_archon_code_examples(
  query_embedding vector(1536),
  match_count int DEFAULT 10,
  filter jsonb DEFAULT '{}'::jsonb,
  source_filter text DEFAULT NULL
) RETURNS TABLE (
  id bigint,
  url varchar,
  chunk_number integer,
  content text,
  summary text,
  metadata jsonb,
  source_id text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    archon_code_examples.id,
    archon_code_examples.url,
    archon_code_examples.chunk_number,
    archon_code_examples.content,
    archon_code_examples.summary,
    archon_code_examples.metadata,
    archon_code_examples.source_id,
    1 - (archon_code_examples.embedding <=> query_embedding) as similarity
  FROM archon_code_examples
  WHERE 
    (source_filter IS NULL OR archon_code_examples.source_id = source_filter)
    AND (filter = '{}'::jsonb OR archon_code_examples.metadata @> filter)
  ORDER BY archon_code_examples.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

### Python Vector Search Implementation
**Purpose:** Application-layer vector search with filtering and thresholds

```python
class BaseSearchStrategy:
    async def vector_search(
        self,
        query_embedding: List[float],
        match_count: int,
        filter_metadata: Dict = None,
        table_rpc: str = "match_archon_crawled_pages"
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search with filtering.
        
        Args:
            query_embedding: 1536-dimension vector
            match_count: Number of results to return
            filter_metadata: Optional metadata filters
            table_rpc: RPC function name
            
        Returns:
            List of results with similarity scores
        """
        # Build RPC parameters
        rpc_params = {
            "query_embedding": query_embedding,
            "match_count": match_count
        }
        
        # Add metadata filters
        if filter_metadata:
            if "source" in filter_metadata:
                rpc_params["source_filter"] = filter_metadata["source"]
                rpc_params["filter"] = {}
            else:
                rpc_params["filter"] = filter_metadata
        else:
            rpc_params["filter"] = {}
        
        # Execute search
        response = self.supabase_client.rpc(table_rpc, rpc_params).execute()
        
        # Apply similarity threshold filtering
        SIMILARITY_THRESHOLD = 0.15
        filtered_results = []
        if response.data:
            for result in response.data:
                similarity = float(result.get("similarity", 0.0))
                if similarity >= SIMILARITY_THRESHOLD:
                    filtered_results.append(result)
        
        return filtered_results
```

### Vector Index Optimization
**Purpose:** Performance optimization for vector searches

```sql
-- IVFFlat index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_embedding 
ON archon_crawled_pages 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Code examples vector index
CREATE INDEX IF NOT EXISTS idx_archon_code_examples_embedding 
ON archon_code_examples 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Metadata GIN indexes for fast JSONB queries
CREATE INDEX IF NOT EXISTS idx_archon_crawled_pages_metadata 
ON archon_crawled_pages 
USING gin (metadata);

CREATE INDEX IF NOT EXISTS idx_archon_code_examples_metadata 
ON archon_code_examples 
USING gin (metadata);
```

---

## 2. Complex Join Operations

### Project-Task Hierarchical Queries
**Purpose:** Retrieve complete project hierarchies with task relationships

```sql
-- Recursive CTE for task hierarchies
WITH RECURSIVE task_hierarchy AS (
  -- Base case: root tasks (no parent)
  SELECT 
    id, project_id, parent_task_id, title, description, status,
    assignee, task_order, feature, 0 as level,
    ARRAY[id] as path
  FROM archon_tasks 
  WHERE parent_task_id IS NULL 
    AND project_id = $1
    AND (archived IS NULL OR archived = false)
  
  UNION ALL
  
  -- Recursive case: child tasks
  SELECT 
    t.id, t.project_id, t.parent_task_id, t.title, t.description, t.status,
    t.assignee, t.task_order, t.feature, th.level + 1,
    th.path || t.id
  FROM archon_tasks t
  INNER JOIN task_hierarchy th ON t.parent_task_id = th.id
  WHERE (t.archived IS NULL OR t.archived = false)
)
SELECT * FROM task_hierarchy 
ORDER BY level, task_order, created_at;
```

### Project Sources with Knowledge Base Join
**Purpose:** Link projects to external knowledge sources

```sql
-- Join projects with their linked knowledge sources
SELECT 
  p.id as project_id,
  p.title as project_title,
  ps.source_type,
  ps.source_url,
  ps.source_name,
  s.title as source_title,
  s.total_word_count,
  s.metadata->>'knowledge_type' as knowledge_type,
  COUNT(cp.id) as chunk_count
FROM archon_projects p
LEFT JOIN archon_project_sources ps ON p.id = ps.project_id
LEFT JOIN archon_sources s ON ps.source_url = s.source_id
LEFT JOIN archon_crawled_pages cp ON s.source_id = cp.source_id
WHERE p.id = $1
GROUP BY p.id, p.title, ps.source_type, ps.source_url, ps.source_name, 
         s.title, s.total_word_count, s.metadata
ORDER BY ps.created_at DESC;
```

### Workflow Execution with Step Details
**Purpose:** Complete workflow execution status with step breakdown

```sql
-- Complex join for workflow execution details
SELECT 
  we.id as execution_id,
  we.status as execution_status,
  we.progress_percentage,
  we.started_at,
  we.completed_at,
  wt.name as template_name,
  wt.title as template_title,
  COUNT(wse.id) as total_steps,
  COUNT(CASE WHEN wse.status = 'completed' THEN 1 END) as completed_steps,
  COUNT(CASE WHEN wse.status = 'failed' THEN 1 END) as failed_steps,
  AVG(wse.duration_ms) as avg_step_duration,
  ARRAY_AGG(
    JSON_BUILD_OBJECT(
      'step_name', wse.step_name,
      'status', wse.status,
      'started_at', wse.started_at,
      'completed_at', wse.completed_at,
      'error_message', wse.error_message
    ) ORDER BY wse.step_index
  ) as step_details
FROM archon_workflow_executions we
JOIN archon_workflow_templates wt ON we.workflow_template_id = wt.id
LEFT JOIN archon_workflow_step_executions wse ON we.id = wse.workflow_execution_id
WHERE we.id = $1
GROUP BY we.id, we.status, we.progress_percentage, we.started_at, 
         we.completed_at, wt.name, wt.title;
```

---

## 3. Aggregation & Analytics Queries

### Knowledge Base Analytics
**Purpose:** Comprehensive knowledge base statistics and metrics

```sql
-- Knowledge base analytics dashboard
SELECT 
  -- Source statistics
  COUNT(DISTINCT s.source_id) as total_sources,
  COUNT(DISTINCT cp.id) as total_chunks,
  COUNT(DISTINCT ce.id) as total_code_examples,
  
  -- Content statistics
  SUM(s.total_word_count) as total_words,
  AVG(s.total_word_count) as avg_words_per_source,
  
  -- Knowledge type distribution
  COUNT(CASE WHEN s.metadata->>'knowledge_type' = 'technical' THEN 1 END) as technical_sources,
  COUNT(CASE WHEN s.metadata->>'knowledge_type' = 'business' THEN 1 END) as business_sources,
  
  -- Recent activity (last 7 days)
  COUNT(CASE WHEN s.created_at > NOW() - INTERVAL '7 days' THEN 1 END) as sources_last_week,
  COUNT(CASE WHEN cp.created_at > NOW() - INTERVAL '7 days' THEN 1 END) as chunks_last_week,
  
  -- Top sources by content
  (
    SELECT JSON_AGG(
      JSON_BUILD_OBJECT(
        'source_id', source_id,
        'title', title,
        'word_count', total_word_count,
        'chunk_count', chunk_count
      ) ORDER BY total_word_count DESC
    )
    FROM (
      SELECT 
        s2.source_id, s2.title, s2.total_word_count,
        COUNT(cp2.id) as chunk_count
      FROM archon_sources s2
      LEFT JOIN archon_crawled_pages cp2 ON s2.source_id = cp2.source_id
      GROUP BY s2.source_id, s2.title, s2.total_word_count
      ORDER BY s2.total_word_count DESC
      LIMIT 10
    ) top_sources
  ) as top_sources_by_content

FROM archon_sources s
LEFT JOIN archon_crawled_pages cp ON s.source_id = cp.source_id
LEFT JOIN archon_code_examples ce ON s.source_id = ce.source_id;
```

### Project Progress Analytics
**Purpose:** Project completion metrics and progress tracking

```sql
-- Project progress analytics with task breakdown
SELECT 
  p.id as project_id,
  p.title,
  p.created_at,
  
  -- Task statistics
  COUNT(t.id) as total_tasks,
  COUNT(CASE WHEN t.status = 'todo' THEN 1 END) as todo_tasks,
  COUNT(CASE WHEN t.status = 'doing' THEN 1 END) as doing_tasks,
  COUNT(CASE WHEN t.status = 'review' THEN 1 END) as review_tasks,
  COUNT(CASE WHEN t.status = 'done' THEN 1 END) as done_tasks,
  
  -- Progress calculations
  ROUND(
    (COUNT(CASE WHEN t.status = 'done' THEN 1 END)::float / 
     NULLIF(COUNT(t.id), 0)) * 100, 2
  ) as completion_percentage,
  
  -- Feature breakdown
  COUNT(DISTINCT t.feature) as unique_features,
  JSON_AGG(
    DISTINCT JSON_BUILD_OBJECT(
      'feature', t.feature,
      'task_count', (
        SELECT COUNT(*) FROM archon_tasks t2 
        WHERE t2.project_id = p.id AND t2.feature = t.feature
      )
    )
  ) FILTER (WHERE t.feature IS NOT NULL) as feature_breakdown,
  
  -- Assignee workload
  JSON_AGG(
    DISTINCT JSON_BUILD_OBJECT(
      'assignee', t.assignee,
      'task_count', (
        SELECT COUNT(*) FROM archon_tasks t3 
        WHERE t3.project_id = p.id AND t3.assignee = t.assignee
      ),
      'completed_count', (
        SELECT COUNT(*) FROM archon_tasks t4 
        WHERE t4.project_id = p.id AND t4.assignee = t.assignee AND t4.status = 'done'
      )
    )
  ) as assignee_workload

FROM archon_projects p
LEFT JOIN archon_tasks t ON p.id = t.project_id 
  AND (t.archived IS NULL OR t.archived = false)
WHERE p.id = $1
GROUP BY p.id, p.title, p.created_at;
```

### Workflow Performance Metrics
**Purpose:** Workflow execution performance and success rates

```sql
-- Workflow performance analytics
SELECT 
  wt.name as template_name,
  wt.title,
  
  -- Execution statistics
  COUNT(we.id) as total_executions,
  COUNT(CASE WHEN we.status = 'completed' THEN 1 END) as successful_executions,
  COUNT(CASE WHEN we.status = 'failed' THEN 1 END) as failed_executions,
  
  -- Success rate
  ROUND(
    (COUNT(CASE WHEN we.status = 'completed' THEN 1 END)::float / 
     NULLIF(COUNT(we.id), 0)) * 100, 2
  ) as success_rate,
  
  -- Performance metrics
  AVG(
    EXTRACT(EPOCH FROM (we.completed_at - we.started_at))
  ) FILTER (WHERE we.completed_at IS NOT NULL) as avg_duration_seconds,
  
  MIN(
    EXTRACT(EPOCH FROM (we.completed_at - we.started_at))
  ) FILTER (WHERE we.completed_at IS NOT NULL) as min_duration_seconds,
  
  MAX(
    EXTRACT(EPOCH FROM (we.completed_at - we.started_at))
  ) FILTER (WHERE we.completed_at IS NOT NULL) as max_duration_seconds,
  
  -- Recent activity
  COUNT(CASE WHEN we.created_at > NOW() - INTERVAL '7 days' THEN 1 END) as executions_last_week,
  
  -- Step failure analysis
  (
    SELECT JSON_AGG(
      JSON_BUILD_OBJECT(
        'step_name', step_name,
        'failure_count', failure_count,
        'total_attempts', total_attempts,
        'failure_rate', ROUND((failure_count::float / total_attempts) * 100, 2)
      ) ORDER BY failure_count DESC
    )
    FROM (
      SELECT 
        wse.step_name,
        COUNT(CASE WHEN wse.status = 'failed' THEN 1 END) as failure_count,
        COUNT(*) as total_attempts
      FROM archon_workflow_step_executions wse
      JOIN archon_workflow_executions we2 ON wse.workflow_execution_id = we2.id
      WHERE we2.workflow_template_id = wt.id
      GROUP BY wse.step_name
      HAVING COUNT(CASE WHEN wse.status = 'failed' THEN 1 END) > 0
      ORDER BY failure_count DESC
      LIMIT 5
    ) step_failures
  ) as top_failing_steps

FROM archon_workflow_templates wt
LEFT JOIN archon_workflow_executions we ON wt.id = we.workflow_template_id
WHERE wt.status = 'active'
GROUP BY wt.id, wt.name, wt.title
ORDER BY total_executions DESC;
```

---

## 4. Bulk Operations & Batch Processing

### Batch Document Storage
**Purpose:** Efficient bulk insertion of document chunks with embeddings

```python
async def add_documents_to_supabase_batch(
    documents: List[Dict[str, Any]], 
    source_id: str,
    batch_size: int = 100
) -> bool:
    """
    Batch insert documents with progress tracking.
    
    Args:
        documents: List of document chunks with embeddings
        source_id: Source identifier
        batch_size: Number of documents per batch
        
    Returns:
        Success status
    """
    supabase = get_supabase_client()
    
    # Process in batches to avoid memory issues
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        # Prepare batch data
        batch_data = []
        for doc in batch:
            batch_data.append({
                "url": doc["url"],
                "chunk_number": doc["chunk_number"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "source_id": source_id,
                "embedding": doc["embedding"]
            })
        
        try:
            # Batch insert with conflict resolution
            response = supabase.table("archon_crawled_pages").upsert(
                batch_data,
                on_conflict="url,chunk_number"
            ).execute()
            
            if not response.data:
                logger.error(f"Batch insert failed for batch {i//batch_size + 1}")
                return False
                
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            return False
    
    return True
```

### Bulk Task Updates
**Purpose:** Efficient batch updates for task status changes

```python
async def bulk_update_task_status(
    task_updates: List[Dict[str, Any]]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Bulk update task statuses with validation.
    
    Args:
        task_updates: List of {task_id, status, assignee} updates
        
    Returns:
        Success status and results
    """
    supabase = get_supabase_client()
    
    # Validate all task IDs exist first
    task_ids = [update["task_id"] for update in task_updates]
    existing_tasks = supabase.table("archon_tasks").select("id").in_("id", task_ids).execute()
    
    if len(existing_tasks.data) != len(task_ids):
        return False, {"error": "Some task IDs do not exist"}
    
    # Perform bulk update using PostgreSQL CASE statements
    update_cases = []
    status_values = []
    assignee_values = []
    
    for update in task_updates:
        task_id = update["task_id"]
        status = update.get("status")
        assignee = update.get("assignee")
        
        if status:
            update_cases.append(f"WHEN id = '{task_id}' THEN '{status}'")
        if assignee:
            assignee_values.append(f"WHEN id = '{task_id}' THEN '{assignee}'")
    
    # Build dynamic SQL for bulk update
    sql_parts = ["UPDATE archon_tasks SET"]
    
    if update_cases:
        sql_parts.append(f"status = CASE {' '.join(update_cases)} ELSE status END")
    
    if assignee_values:
        if update_cases:
            sql_parts.append(",")
        sql_parts.append(f"assignee = CASE {' '.join(assignee_values)} ELSE assignee END")
    
    sql_parts.append(f"WHERE id IN ({','.join([f\"'{tid}'\" for tid in task_ids])})")
    
    try:
        response = supabase.rpc("execute_sql", {"sql": " ".join(sql_parts)}).execute()
        return True, {"updated_count": len(task_updates)}
    except Exception as e:
        return False, {"error": str(e)}
```

---

## Related Files
- **Parent components:** Database tables, indexes, RLS policies
- **Child components:** API endpoints, service layers, UI components
- **Shared utilities:** Supabase client, embedding services, logging

## Notes
- All vector searches use cosine similarity with IVFFlat indexes
- JSONB queries leverage GIN indexes for performance
- Bulk operations use batch processing to avoid memory issues
- Complex joins utilize CTEs for hierarchical data
- Analytics queries use window functions and aggregations
- Performance monitoring through query execution time tracking

---
*Auto-generated documentation - verify accuracy before use*
