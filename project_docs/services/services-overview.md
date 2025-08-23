# Services Architecture Overview

**File Path:** `python/src/server/services/` and `archon-ui-main/src/services/` directories
**Last Updated:** 2025-08-22

## Purpose
Comprehensive documentation of the service layer architecture that handles business logic, external integrations, and core functionality. Services provide the application logic layer between API endpoints and data storage.

## Service Architecture

### Backend Services (Python)
Located in `python/src/server/services/` - 50+ service files organized by domain

### Frontend Services (TypeScript)
Located in `archon-ui-main/src/services/` - Client-side service layer for API integration

## Backend Service Categories

### 1. Core Infrastructure Services (8 files)
- **client_manager.py** - Database client connection management
- **background_task_manager.py** - Async task orchestration
- **threading_service.py** - Thread pool management
- **crawler_manager.py** - Web crawler instance management
- **mcp_session_manager.py** - MCP session lifecycle management
- **mcp_service_client.py** - MCP protocol client implementation
- **credential_service.py** - Secure credential storage and retrieval
- **prompt_service.py** - Prompt template management

### 2. Storage Services (4 files)
- **base_storage_service.py** - Abstract storage operations base class
- **storage_services.py** - DocumentStorageService orchestration
- **document_storage_service.py** - Document storage utilities
- **code_storage_service.py** - Code extraction and storage

### 3. Search & RAG Services (6 files)
- **rag_service.py** - Main RAG orchestration service
- **base_search_strategy.py** - Abstract search strategy base
- **hybrid_search_strategy.py** - Hybrid vector/keyword search
- **agentic_rag_strategy.py** - AI-powered search enhancement
- **reranking_strategy.py** - Result reranking algorithms
- **keyword_extractor.py** - Keyword extraction utilities

### 4. Embedding Services (4 files)
- **embedding_service.py** - Main embedding generation service
- **contextual_embedding_service.py** - Context-aware embeddings
- **embedding_fallback_service.py** - Provider fallback handling
- **embedding_exceptions.py** - Embedding-specific error handling

### 5. Crawling Services (4 files + helpers)
- **crawling_service.py** - Web crawling orchestration
- **code_extraction_service.py** - Code block extraction from web pages
- **document_storage_operations.py** - Crawled content storage
- **progress_mapper.py** - Crawling progress tracking

### 6. Project Management Services (9 files)
- **project_service.py** - Core project operations
- **project_creation_service.py** - Project initialization workflows
- **task_service.py** - Task management operations
- **document_service.py** - Project document management
- **versioning_service.py** - Document version control
- **progress_service.py** - Project progress tracking
- **export_service.py** - Project data export
- **import_service.py** - Project data import
- **source_linking_service.py** - Knowledge source linking

### 7. Knowledge Management Services (2 files)
- **knowledge_item_service.py** - Knowledge item operations
- **database_metrics_service.py** - Knowledge base analytics

### 8. Template Services (6 files)
- **template_service.py** - Template management operations
- **template_injection_service.py** - Dynamic template injection
- **template_assignment_service.py** - Template-to-entity assignments
- **template_context_selector.py** - Context-aware template selection
- **template_resolver.py** - Template resolution and expansion
- **component_service.py** - Component hierarchy management

### 9. Workflow Services (5 files)
- **workflow_repository.py** - Workflow data access layer
- **workflow_execution_service.py** - Workflow execution engine
- **workflow_executor.py** - Individual workflow execution
- **workflow_detection_service.py** - Workflow pattern detection
- **mcp_tool_integration.py** - MCP tool integration for workflows

### 10. Backup Services (2 files)
- **backup_manager.py** - Backup operations management
- **backup_scheduler.py** - Automated backup scheduling

### 11. Integration Services (3 files)
- **llm_provider_service.py** - LLM provider abstraction
- **context_compilation_service.py** - Context aggregation for AI
- **source_management_service.py** - External source management

## Frontend Service Categories

### 1. API Integration Services (4 files)
- **componentService.ts** - Component management API wrapper
- **credentialsService.ts** - Credentials management API wrapper
- **bugReportService.ts** - Bug reporting and GitHub integration
- **Additional services** - Project, task, and workflow API wrappers

## Service Design Patterns

### 1. Repository Pattern
```python
class ProjectService:
    def __init__(self):
        self.repository = ProjectRepository()
    
    async def create_project(self, data: Dict) -> Project:
        # Business logic
        validated_data = self.validate_project_data(data)
        # Repository call
        return await self.repository.create(validated_data)
```

### 2. Strategy Pattern
```python
class SearchService:
    def __init__(self):
        self.strategies = {
            'hybrid': HybridSearchStrategy(),
            'vector': VectorSearchStrategy(),
            'keyword': KeywordSearchStrategy()
        }
    
    async def search(self, query: str, strategy: str = 'hybrid'):
        return await self.strategies[strategy].execute(query)
```

### 3. Factory Pattern
```python
class EmbeddingServiceFactory:
    @staticmethod
    def create_service(provider: str) -> EmbeddingService:
        if provider == 'openai':
            return OpenAIEmbeddingService()
        elif provider == 'tei':
            return TEIEmbeddingService()
        else:
            raise ValueError(f"Unknown provider: {provider}")
```

### 4. Observer Pattern
```python
class WorkflowExecutionService:
    def __init__(self):
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    async def execute_step(self, step):
        result = await step.execute()
        for observer in self.observers:
            await observer.on_step_completed(step, result)
```

## Service Integration Patterns

### 1. Service Composition
```python
class ProjectCreationService:
    def __init__(self):
        self.project_service = ProjectService()
        self.document_service = DocumentService()
        self.task_service = TaskService()
    
    async def create_project_with_prp(self, project_data, prp_content):
        # Orchestrate multiple services
        project = await self.project_service.create(project_data)
        document = await self.document_service.create_prp(project.id, prp_content)
        tasks = await self.task_service.generate_from_prp(project.id, prp_content)
        return project, document, tasks
```

### 2. Event-Driven Architecture
```python
class CrawlingService:
    async def crawl_source(self, source_url):
        # Emit events for progress tracking
        await self.emit_event('crawl_started', {'url': source_url})
        
        documents = await self.extract_documents(source_url)
        await self.emit_event('documents_extracted', {'count': len(documents)})
        
        await self.storage_service.store_documents(documents)
        await self.emit_event('crawl_completed', {'url': source_url})
```

### 3. Dependency Injection
```python
class ServiceContainer:
    def __init__(self):
        self._services = {}
    
    def register(self, interface, implementation):
        self._services[interface] = implementation
    
    def get(self, interface):
        return self._services[interface]

# Usage
container = ServiceContainer()
container.register(IEmbeddingService, OpenAIEmbeddingService())
container.register(IStorageService, SupabaseStorageService())
```

## Error Handling Patterns

### 1. Service-Level Exception Handling
```python
class ServiceException(Exception):
    def __init__(self, message: str, code: str = None, details: Dict = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}

class ProjectServiceException(ServiceException):
    pass

class ProjectService:
    async def create_project(self, data: Dict) -> Project:
        try:
            return await self._create_project_impl(data)
        except ValidationError as e:
            raise ProjectServiceException(
                "Project validation failed",
                code="VALIDATION_ERROR",
                details={"errors": e.errors()}
            )
        except Exception as e:
            raise ProjectServiceException(
                "Project creation failed",
                code="CREATION_ERROR",
                details={"original_error": str(e)}
            )
```

### 2. Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenException()
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
```

## Performance Optimization

### 1. Caching Strategies
```python
from functools import lru_cache
import asyncio

class CachedService:
    def __init__(self):
        self._cache = {}
        self._cache_ttl = {}
    
    @lru_cache(maxsize=128)
    def get_static_data(self, key: str):
        return self._fetch_static_data(key)
    
    async def get_dynamic_data(self, key: str, ttl: int = 300):
        if key in self._cache:
            if time.time() - self._cache_ttl[key] < ttl:
                return self._cache[key]
        
        data = await self._fetch_dynamic_data(key)
        self._cache[key] = data
        self._cache_ttl[key] = time.time()
        return data
```

### 2. Async Batch Processing
```python
class BatchProcessor:
    def __init__(self, batch_size: int = 100, max_workers: int = 5):
        self.batch_size = batch_size
        self.max_workers = max_workers
    
    async def process_items(self, items: List[Any], processor_func):
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_batch(batch):
            async with semaphore:
                return await processor_func(batch)
        
        batches = [items[i:i + self.batch_size] 
                  for i in range(0, len(items), self.batch_size)]
        
        tasks = [process_batch(batch) for batch in batches]
        return await asyncio.gather(*tasks)
```

## Service Configuration

### 1. Environment-Based Configuration
```python
class ServiceConfig:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.redis_url = os.getenv('REDIS_URL')
        self.embedding_provider = os.getenv('EMBEDDING_PROVIDER', 'openai')
        self.max_workers = int(os.getenv('MAX_WORKERS', '5'))
        self.cache_ttl = int(os.getenv('CACHE_TTL', '300'))
```

### 2. Service Registry
```python
class ServiceRegistry:
    _instance = None
    _services = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_service(self, name: str, service_instance):
        self._services[name] = service_instance
    
    def get_service(self, name: str):
        return self._services.get(name)
```

## Related Files
- **Parent components:** API endpoints, background tasks, CLI commands
- **Child components:** Database repositories, external API clients, utilities
- **Shared utilities:** Configuration, logging, error handling, type definitions

## Notes
- Services follow single responsibility principle
- Comprehensive error handling and logging
- Async/await patterns for I/O operations
- Dependency injection for testability
- Circuit breaker patterns for external services
- Caching strategies for performance
- Event-driven architecture for loose coupling
- Comprehensive type hints for maintainability

---
*Auto-generated documentation - verify accuracy before use*
