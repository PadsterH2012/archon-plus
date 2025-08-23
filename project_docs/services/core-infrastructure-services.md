# Core Infrastructure Services

**File Path:** `python/src/server/services/` directory
**Last Updated:** 2025-08-22

## Purpose
Documentation of core infrastructure services that provide foundational functionality for the entire application. These services handle connection management, task orchestration, session management, and security.

## Core Infrastructure Services

### 1. Client Manager Service
**File:** `client_manager.py`
**Purpose:** Database client connection management and configuration

**Key Features:**
- Supabase client singleton management
- Connection pooling and lifecycle management
- Environment-based configuration
- Error handling and reconnection logic

**Usage:**
```python
from services.client_manager import get_supabase_client

# Get configured Supabase client
supabase = get_supabase_client()

# Execute database operations
result = supabase.table('projects').select('*').execute()
```

**Configuration:**
```python
def get_supabase_client() -> Client:
    """Get configured Supabase client with proper error handling"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not url or not key:
        raise ValueError("Supabase configuration missing")
    
    return create_client(url, key)
```

### 2. Background Task Manager
**File:** `background_task_manager.py`
**Purpose:** Async task orchestration and lifecycle management

**Key Features:**
- Task queue management
- Priority-based task scheduling
- Progress tracking and monitoring
- Error handling and retry logic
- Resource management and cleanup

**Usage:**
```python
from services.background_task_manager import BackgroundTaskManager

task_manager = BackgroundTaskManager()

# Submit background task
task_id = await task_manager.submit_task(
    func=crawl_website,
    args=['https://example.com'],
    priority='high',
    timeout=3600
)

# Monitor task progress
status = await task_manager.get_task_status(task_id)
```

**Task Types:**
- **Crawling Tasks** - Web crawling operations
- **Processing Tasks** - Document processing and embedding generation
- **Export Tasks** - Data export operations
- **Cleanup Tasks** - Maintenance and cleanup operations

### 3. Threading Service
**File:** `threading_service.py`
**Purpose:** Thread pool management for CPU-intensive operations

**Key Features:**
- Configurable thread pool sizes
- Task distribution and load balancing
- Resource monitoring and management
- Graceful shutdown handling

**Usage:**
```python
from services.threading_service import ThreadingService

threading_service = ThreadingService(max_workers=8)

# Execute CPU-intensive task
result = await threading_service.execute(
    func=process_large_document,
    args=[document_content],
    timeout=300
)
```

### 4. Crawler Manager
**File:** `crawler_manager.py`
**Purpose:** Web crawler instance management and coordination

**Key Features:**
- Crawler instance lifecycle management
- Rate limiting and throttling
- Session management and cookies
- User agent rotation
- Proxy support and rotation

**Usage:**
```python
from services.crawler_manager import CrawlerManager

crawler_manager = CrawlerManager()

# Get configured crawler instance
crawler = await crawler_manager.get_crawler(
    rate_limit=1.0,
    user_agent='custom-agent',
    use_proxy=True
)

# Crawl with managed instance
content = await crawler.fetch_page('https://example.com')
```

**Configuration:**
```python
class CrawlerConfig:
    rate_limit: float = 1.0
    max_concurrent: int = 5
    timeout: int = 30
    user_agents: List[str] = [...]
    proxy_list: List[str] = [...]
```

### 5. MCP Session Manager
**File:** `mcp_session_manager.py`
**Purpose:** MCP (Model Context Protocol) session lifecycle management

**Key Features:**
- Session creation and termination
- Connection pooling for MCP clients
- Session state management
- Error recovery and reconnection
- Resource cleanup and monitoring

**Usage:**
```python
from services.mcp_session_manager import MCPSessionManager

session_manager = MCPSessionManager()

# Create MCP session
session_id = await session_manager.create_session(
    server_url='http://localhost:8080',
    capabilities=['tools', 'resources']
)

# Use session for MCP operations
result = await session_manager.call_tool(
    session_id=session_id,
    tool_name='manage_project',
    parameters={'action': 'list'}
)

# Cleanup session
await session_manager.close_session(session_id)
```

### 6. MCP Service Client
**File:** `mcp_service_client.py`
**Purpose:** MCP protocol client implementation

**Key Features:**
- MCP protocol implementation
- Tool calling and resource access
- Message serialization/deserialization
- Error handling and validation
- Async communication patterns

**Usage:**
```python
from services.mcp_service_client import MCPServiceClient

client = MCPServiceClient('http://localhost:8080')

# Initialize connection
await client.connect()

# Call MCP tool
response = await client.call_tool(
    name='manage_task',
    arguments={
        'action': 'create',
        'title': 'New Task',
        'description': 'Task description'
    }
)

# Access MCP resource
resource = await client.get_resource('project://123/tasks')
```

### 7. Credential Service
**File:** `credential_service.py`
**Purpose:** Secure credential storage and retrieval

**Key Features:**
- Encrypted credential storage
- Environment variable integration
- Credential categorization and organization
- Access control and audit logging
- Secure credential rotation

**Usage:**
```python
from services.credential_service import CredentialService

cred_service = CredentialService()

# Store encrypted credential
await cred_service.store_credential(
    key='openai_api_key',
    value='sk-...',
    category='api_keys',
    encrypted=True
)

# Retrieve credential
api_key = await cred_service.get_credential('openai_api_key')

# Get credentials by category
rag_settings = await cred_service.get_credentials_by_category('rag_strategy')
```

**Security Features:**
- AES-256 encryption for sensitive values
- Key derivation from environment secrets
- Audit logging for credential access
- Automatic credential expiration
- Secure credential sharing between services

### 8. Prompt Service
**File:** `prompt_service.py`
**Purpose:** Prompt template management and rendering

**Key Features:**
- Template storage and versioning
- Dynamic prompt rendering with variables
- Prompt optimization and A/B testing
- Context-aware prompt selection
- Performance monitoring and analytics

**Usage:**
```python
from services.prompt_service import PromptService

prompt_service = PromptService()

# Store prompt template
await prompt_service.store_template(
    name='code_review_prompt',
    template='Review this code for {language}: {code}',
    variables=['language', 'code'],
    category='code_analysis'
)

# Render prompt with variables
prompt = await prompt_service.render_prompt(
    name='code_review_prompt',
    variables={
        'language': 'Python',
        'code': 'def hello(): print("Hello")'
    }
)
```

## Service Integration Patterns

### 1. Service Dependency Injection
```python
class ServiceContainer:
    def __init__(self):
        self.client_manager = ClientManager()
        self.task_manager = BackgroundTaskManager()
        self.credential_service = CredentialService()
        self.prompt_service = PromptService()
    
    def get_configured_service(self, service_type: str):
        services = {
            'client': self.client_manager,
            'tasks': self.task_manager,
            'credentials': self.credential_service,
            'prompts': self.prompt_service
        }
        return services.get(service_type)
```

### 2. Service Health Monitoring
```python
class HealthMonitor:
    def __init__(self, services: List[Service]):
        self.services = services
    
    async def check_health(self) -> Dict[str, bool]:
        health_status = {}
        
        for service in self.services:
            try:
                await service.health_check()
                health_status[service.name] = True
            except Exception as e:
                health_status[service.name] = False
                logger.error(f"Health check failed for {service.name}: {e}")
        
        return health_status
```

### 3. Service Configuration Management
```python
class ServiceConfig:
    def __init__(self):
        self.load_from_environment()
    
    def load_from_environment(self):
        self.database_config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_SERVICE_KEY')
        }
        
        self.task_config = {
            'max_workers': int(os.getenv('MAX_WORKERS', '5')),
            'queue_size': int(os.getenv('QUEUE_SIZE', '100'))
        }
        
        self.crawler_config = {
            'rate_limit': float(os.getenv('CRAWLER_RATE_LIMIT', '1.0')),
            'timeout': int(os.getenv('CRAWLER_TIMEOUT', '30'))
        }
```

## Error Handling and Resilience

### 1. Circuit Breaker Implementation
```python
class ServiceCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
    
    async def call_service(self, service_func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise ServiceUnavailableException()
        
        try:
            result = await service_func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
```

### 2. Retry Logic with Exponential Backoff
```python
async def retry_with_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
            logger.warning(f"Retry attempt {attempt + 1} after {delay}s delay")
```

## Performance Monitoring

### 1. Service Metrics Collection
```python
class ServiceMetrics:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record_execution_time(self, service_name: str, duration: float):
        self.metrics[f"{service_name}_execution_time"].append(duration)
    
    def record_error(self, service_name: str, error_type: str):
        self.metrics[f"{service_name}_errors"].append(error_type)
    
    def get_average_execution_time(self, service_name: str) -> float:
        times = self.metrics[f"{service_name}_execution_time"]
        return sum(times) / len(times) if times else 0
```

### 2. Resource Usage Monitoring
```python
class ResourceMonitor:
    async def monitor_service_resources(self, service_name: str):
        process = psutil.Process()
        
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'open_files': len(process.open_files()),
            'connections': len(process.connections()),
            'threads': process.num_threads()
        }
```

## Related Files
- **Parent components:** API endpoints, application initialization, configuration
- **Child components:** Database repositories, external API clients, utilities
- **Shared utilities:** Configuration management, logging, error handling

## Notes
- All services implement proper async patterns
- Comprehensive error handling and logging
- Resource management and cleanup
- Health monitoring and metrics collection
- Security best practices for credential handling
- Performance optimization with connection pooling
- Graceful shutdown and resource cleanup
- Extensive configuration options

---
*Auto-generated documentation - verify accuracy before use*
