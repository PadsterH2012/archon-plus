# Database Services & Repositories Documentation

**File Path:** `python/src/server/services/` directory
**Last Updated:** 2025-08-22

## Purpose
Comprehensive documentation of all database service files that handle data access, storage operations, client management, and repository patterns. These services provide the data access layer between the API endpoints and the PostgreSQL/Supabase database.

## Props/Parameters
Services use dependency injection and configuration from environment variables

## Dependencies

### Imports
```python
from supabase import Client, create_client
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime
import logging
import asyncio
```

### Exports
```python
# Client Management
from .client_manager import get_supabase_client

# Storage Services
from .storage import (
    BaseStorageService, DocumentStorageService,
    add_documents_to_supabase, add_code_examples_to_supabase
)

# Workflow Repository
from .workflow.workflow_repository import WorkflowRepository

# Knowledge Services
from .knowledge.database_metrics_service import DatabaseMetricsService

# Utility Services
from .source_management_service import SourceManagementService
from .credential_service import CredentialService
```

## Core Database Services

### 1. Client Manager (`client_manager.py`)
**Purpose:** Manages Supabase database client connections with connection pooling

#### Key Functions

**get_supabase_client()**
```python
def get_supabase_client() -> Client:
    """
    Get a Supabase client instance with connection pooling.
    
    Returns:
        Supabase client instance
        
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_SERVICE_KEY not set
    """
```

#### Configuration
- **Environment Variables:** `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- **Connection Pooling:** Handled internally by Supabase client
- **Project ID Extraction:** From URL for logging purposes
- **Error Handling:** Comprehensive logging and exception handling

#### Usage Example
```python
from .client_manager import get_supabase_client

# Get client instance
supabase = get_supabase_client()

# Use for database operations
result = supabase.table("archon_sources").select("*").execute()
```

---

### 2. Storage Services (`storage/`)
**Purpose:** Document and code storage operations with vector embeddings

#### Base Storage Service (`base_storage_service.py`)
**Abstract base class for all storage operations**

**Key Methods:**
- `smart_chunk_text()` - Intelligent text chunking with overlap
- `extract_metadata()` - Extract document metadata
- `batch_process_with_progress()` - Batch processing with progress tracking

#### Document Storage Service (`storage_services.py`)
**High-level document storage orchestration**

**DocumentStorageService Class:**
```python
class DocumentStorageService(BaseStorageService):
    def upload_document(self, file_path: str, knowledge_type: str = "technical") -> Dict[str, Any]:
        """Upload and process document with embeddings"""
        
    def store_documents(self, documents: List[Dict], source_id: str) -> bool:
        """Store multiple documents with batch processing"""
        
    def process_document(self, content: str, metadata: Dict) -> List[Dict]:
        """Process document content into chunks with embeddings"""
```

#### Document Storage Utilities (`document_storage_service.py`)
**Low-level storage utility functions**

**Key Functions:**
- `add_documents_to_supabase()` - Single document storage
- `add_documents_to_supabase_parallel()` - Parallel document processing
- Vector embedding generation and storage
- Metadata extraction and normalization

#### Code Storage Service (`code_storage_service.py`)
**Code extraction and storage with specialized embeddings**

**Key Functions:**
```python
def extract_code_blocks(content: str, url: str) -> List[Dict[str, Any]]:
    """Extract code blocks from content with language detection"""
    
def generate_code_example_summary(code_content: str, language: str) -> str:
    """Generate AI summary of code functionality"""
    
def add_code_examples_to_supabase(code_examples: List[Dict], source_id: str) -> bool:
    """Store code examples with embeddings in database"""
```

**Code Metadata Structure:**
```python
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

### 3. Workflow Repository (`workflow/workflow_repository.py`)
**Purpose:** Data access layer for workflow orchestration system

#### WorkflowRepository Class
**Complete CRUD operations for workflow templates and executions**

**Key Methods:**
```python
class WorkflowRepository:
    async def create_workflow_template(self, template_data: Dict[str, Any]) -> Tuple[bool, Dict]:
        """Create new workflow template with validation"""
        
    async def get_workflow_template(self, template_id: UUID) -> Optional[WorkflowTemplate]:
        """Retrieve workflow template by ID"""
        
    async def update_workflow_template(self, template_id: UUID, updates: Dict) -> Tuple[bool, Dict]:
        """Update existing workflow template"""
        
    async def delete_workflow_template(self, template_id: UUID) -> Tuple[bool, Dict]:
        """Soft delete workflow template"""
        
    async def list_workflow_templates(self, filters: Dict = None) -> List[WorkflowTemplate]:
        """List templates with optional filtering"""
        
    async def create_workflow_execution(self, execution_data: Dict) -> Tuple[bool, Dict]:
        """Create new workflow execution instance"""
        
    async def update_execution_status(self, execution_id: UUID, status: str) -> bool:
        """Update execution status and progress"""
```

#### Database Operations
- **Template Validation:** Using Pydantic models before database operations
- **Version Management:** Automatic version creation on template changes
- **Transaction Handling:** Proper error handling and rollback
- **Step Serialization:** Converting step objects to/from JSON
- **Progress Tracking:** Real-time execution progress updates

#### Error Handling
```python
try:
    # Database operation
    response = self.supabase_client.table("archon_workflow_templates").insert(data).execute()
    if not response.data:
        return False, {"error": "Database returned no data"}
except Exception as e:
    logger.error(f"Database operation failed: {e}")
    return False, {"error": str(e)}
```

---

### 4. Knowledge Services (`knowledge/`)
**Purpose:** Knowledge base management and metrics

#### Database Metrics Service (`database_metrics_service.py`)
**Database statistics and health monitoring**

**DatabaseMetricsService Class:**
```python
class DatabaseMetricsService:
    def get_database_metrics(self) -> Dict[str, Any]:
        """Get comprehensive database metrics"""
        
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage distribution and activity stats"""
```

**Metrics Collected:**
- **Source Counts:** Total knowledge sources
- **Page Counts:** Total crawled pages/chunks
- **Code Examples:** Total code examples stored
- **Knowledge Type Distribution:** Technical vs business content
- **Recent Activity:** Latest source additions
- **Average Ratios:** Pages per source calculations

**Sample Metrics Output:**
```python
{
    "sources_count": 45,
    "pages_count": 1250,
    "code_examples_count": 89,
    "average_pages_per_source": 27.78,
    "timestamp": "2025-08-22T10:30:00Z",
    "knowledge_type_distribution": {
        "technical": 32,
        "business": 13
    },
    "recent_sources": [
        {"source_id": "example.com", "created_at": "2025-08-22T09:15:00Z"}
    ]
}
```

---

### 5. Utility Services
**Purpose:** Supporting services for credentials, sources, and operations

#### Source Management Service (`source_management_service.py`)
**Knowledge source metadata management**

**Key Functions:**
- `extract_source_summary()` - Generate source summaries
- `generate_source_title_and_metadata()` - Auto-generate titles and metadata
- `update_source_info()` - Update source information

#### Credential Service (`credential_service.py`)
**Secure credential storage and retrieval**

**Key Functions:**
- `get_credential()` - Retrieve encrypted credentials
- `set_credential()` - Store encrypted credentials
- Encryption/decryption handling
- Environment variable fallbacks

---

## API Patterns

### Service Layer Architecture
```python
# Controller Layer (FastAPI endpoints)
@app.post("/api/workflows")
async def create_workflow(template_data: Dict):
    # Input validation
    # Call service layer
    result = await workflow_service.create_template(template_data)
    # Return response

# Service Layer (Business logic)
class WorkflowService:
    def __init__(self):
        self.repository = WorkflowRepository()
    
    async def create_template(self, data: Dict):
        # Business logic
        # Call repository layer
        return await self.repository.create_workflow_template(data)

# Repository Layer (Data access)
class WorkflowRepository:
    async def create_workflow_template(self, data: Dict):
        # Database operations
        # Error handling
        # Return results
```

### Error Handling Patterns
```python
# Consistent error response format
def handle_database_error(operation: str, error: Exception) -> Tuple[bool, Dict]:
    logger.error(f"{operation} failed: {error}")
    return False, {
        "error": f"{operation} failed",
        "details": str(error),
        "timestamp": datetime.now().isoformat()
    }

# Service-level error handling
try:
    result = await database_operation()
    return True, {"data": result}
except ValidationError as e:
    return False, {"error": "Validation failed", "details": e.errors()}
except Exception as e:
    return handle_database_error("Operation", e)
```

### Integration Points
- **Supabase Client:** All services use centralized client manager
- **Pydantic Models:** Data validation before database operations
- **Logging:** Structured logging with operation context
- **Environment Config:** Centralized configuration management
- **Error Propagation:** Consistent error handling across layers

---

## Related Files
- **Parent components:** Database tables, Pydantic models
- **Child components:** API endpoints, business logic services
- **Shared utilities:** Client manager, logging configuration

## Notes
- All services follow repository pattern for data access
- Comprehensive error handling with structured logging
- Automatic connection pooling through Supabase client
- Vector embedding integration for semantic search
- Transaction support for complex operations
- Consistent API patterns across all services

---
*Auto-generated documentation - verify accuracy before use*
