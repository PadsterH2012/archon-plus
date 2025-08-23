# Search & Embedding Services

**File Path:** `python/src/server/services/search/` and `python/src/server/services/embeddings/` directories
**Last Updated:** 2025-08-22

## Purpose
Documentation of search and embedding services that power the RAG (Retrieval Augmented Generation) system. These services handle vector search, keyword extraction, embedding generation, and intelligent content retrieval.

## Search Services

### 1. RAG Service
**File:** `search/rag_service.py`
**Purpose:** Main RAG orchestration service coordinating search strategies

**Key Features:**
- Multi-strategy search coordination
- Result aggregation and ranking
- Context compilation for AI models
- Performance monitoring and optimization
- Fallback handling for failed searches

**Usage:**
```python
from services.search.rag_service import RAGService

rag_service = RAGService()

# Perform RAG search
results = await rag_service.search(
    query="How to implement OAuth2 authentication",
    strategy="hybrid",
    max_results=10,
    source_filter="technical_docs"
)

# Get contextual results for AI
context = await rag_service.get_context_for_query(
    query="OAuth2 implementation steps",
    max_context_length=4000
)
```

**Search Strategies:**
- **Hybrid Search** - Combines vector and keyword search
- **Vector Search** - Semantic similarity using embeddings
- **Keyword Search** - Traditional text-based search
- **Agentic Search** - AI-powered search enhancement

### 2. Base Search Strategy
**File:** `search/base_search_strategy.py`
**Purpose:** Abstract base class for all search strategies

**Key Features:**
- Common search interface
- Result normalization
- Error handling patterns
- Performance metrics collection
- Extensible architecture

**Interface:**
```python
class BaseSearchStrategy:
    async def search(self, query: str, **kwargs) -> List[SearchResult]:
        """Execute search with strategy-specific implementation"""
        raise NotImplementedError
    
    async def get_similarity_threshold(self) -> float:
        """Get minimum similarity threshold for results"""
        return 0.15
    
    def normalize_results(self, results: List[Dict]) -> List[SearchResult]:
        """Normalize results to common format"""
        pass
```

### 3. Hybrid Search Strategy
**File:** `search/hybrid_search_strategy.py`
**Purpose:** Combines vector similarity and keyword search

**Key Features:**
- Vector and keyword search fusion
- Weighted result combination
- Relevance score normalization
- Performance optimization
- Configurable search weights

**Usage:**
```python
from services.search.hybrid_search_strategy import HybridSearchStrategy

hybrid_search = HybridSearchStrategy(
    vector_weight=0.7,
    keyword_weight=0.3,
    similarity_threshold=0.15
)

results = await hybrid_search.search(
    query="implement user authentication",
    match_count=10,
    source_filter="documentation"
)
```

**Algorithm:**
1. **Vector Search** - Find semantically similar content
2. **Keyword Search** - Find exact keyword matches
3. **Score Fusion** - Combine scores with weights
4. **Deduplication** - Remove duplicate results
5. **Ranking** - Sort by combined relevance score

### 4. Agentic RAG Strategy
**File:** `search/agentic_rag_strategy.py`
**Purpose:** AI-powered search enhancement and query optimization

**Key Features:**
- Query expansion and refinement
- Context-aware search planning
- Multi-step search execution
- Result validation and filtering
- Learning from search patterns

**Usage:**
```python
from services.search.agentic_rag_strategy import AgenticRAGStrategy

agentic_search = AgenticRAGStrategy()

# AI-enhanced search
results = await agentic_search.search(
    query="best practices for API security",
    context="building REST API for e-commerce",
    user_intent="implementation_guidance"
)
```

**AI Enhancement Steps:**
1. **Query Analysis** - Understand user intent and context
2. **Query Expansion** - Generate related search terms
3. **Search Planning** - Determine optimal search strategy
4. **Multi-Step Execution** - Execute planned search steps
5. **Result Validation** - Verify result relevance and quality

### 5. Reranking Strategy
**File:** `search/reranking_strategy.py`
**Purpose:** Advanced result reranking using ML models

**Key Features:**
- Cross-encoder reranking models
- Context-aware relevance scoring
- Query-document interaction modeling
- Performance optimization
- Configurable reranking thresholds

**Usage:**
```python
from services.search.reranking_strategy import RerankingStrategy

reranker = RerankingStrategy(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")

# Rerank search results
reranked_results = await reranker.rerank(
    query="OAuth2 implementation",
    results=initial_results,
    top_k=5
)
```

### 6. Keyword Extractor
**File:** `search/keyword_extractor.py`
**Purpose:** Extract relevant keywords and phrases from text

**Key Features:**
- TF-IDF keyword extraction
- Named entity recognition
- Phrase extraction
- Stop word filtering
- Language-specific processing

**Usage:**
```python
from services.search.keyword_extractor import KeywordExtractor

extractor = KeywordExtractor()

# Extract keywords from text
keywords = await extractor.extract_keywords(
    text="Implement OAuth2 authentication with Google provider",
    max_keywords=10,
    include_phrases=True
)

# Extract from query for search expansion
query_keywords = await extractor.extract_query_keywords(
    query="How to secure API endpoints",
    expand_synonyms=True
)
```

## Embedding Services

### 1. Embedding Service
**File:** `embeddings/embedding_service.py`
**Purpose:** Main embedding generation service with provider abstraction

**Key Features:**
- Multi-provider support (OpenAI, TEI, local models)
- Batch embedding generation
- Caching and optimization
- Error handling and fallbacks
- Performance monitoring

**Usage:**
```python
from services.embeddings.embedding_service import EmbeddingService

embedding_service = EmbeddingService(provider="openai")

# Generate single embedding
embedding = await embedding_service.generate_embedding(
    text="OAuth2 authentication implementation guide"
)

# Generate batch embeddings
embeddings = await embedding_service.generate_embeddings_batch([
    "User authentication flow",
    "API security best practices",
    "Token management strategies"
])
```

**Supported Providers:**
- **OpenAI** - text-embedding-ada-002, text-embedding-3-small/large
- **TEI** - Text Embeddings Inference server
- **Local Models** - Sentence transformers and custom models
- **Fallback Chain** - Automatic provider switching on failure

### 2. Contextual Embedding Service
**File:** `embeddings/contextual_embedding_service.py`
**Purpose:** Context-aware embedding generation with enhanced semantics

**Key Features:**
- Context-enhanced embeddings
- Document structure awareness
- Metadata integration
- Semantic chunking
- Quality optimization

**Usage:**
```python
from services.embeddings.contextual_embedding_service import ContextualEmbeddingService

contextual_service = ContextualEmbeddingService()

# Generate context-aware embedding
embedding = await contextual_service.generate_contextual_embedding(
    text="implement user login",
    context={
        "document_type": "technical_guide",
        "section": "authentication",
        "language": "python"
    }
)
```

### 3. Embedding Fallback Service
**File:** `embeddings/embedding_fallback_service.py`
**Purpose:** Provider fallback and redundancy management

**Key Features:**
- Automatic provider switching
- Health monitoring
- Performance tracking
- Cost optimization
- Error recovery

**Usage:**
```python
from services.embeddings.embedding_fallback_service import EmbeddingFallbackService

fallback_service = EmbeddingFallbackService(
    primary_provider="openai",
    fallback_providers=["tei", "local"],
    health_check_interval=300
)

# Embedding with automatic fallback
embedding = await fallback_service.generate_embedding_with_fallback(
    text="API authentication methods",
    max_retries=3
)
```

### 4. Embedding Exceptions
**File:** `embeddings/embedding_exceptions.py`
**Purpose:** Embedding-specific error handling and exceptions

**Exception Types:**
```python
class EmbeddingException(Exception):
    """Base embedding exception"""
    pass

class ProviderUnavailableException(EmbeddingException):
    """Provider service unavailable"""
    pass

class EmbeddingGenerationException(EmbeddingException):
    """Failed to generate embedding"""
    pass

class InvalidTextException(EmbeddingException):
    """Text input validation failed"""
    pass
```

## Service Integration Patterns

### 1. RAG Pipeline Orchestration
```python
class RAGPipeline:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.search_service = RAGService()
        self.reranker = RerankingStrategy()
    
    async def execute_rag_query(self, query: str, context: str = None):
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Perform hybrid search
        initial_results = await self.search_service.search(
            query=query,
            strategy="hybrid",
            max_results=20
        )
        
        # Rerank results
        final_results = await self.reranker.rerank(
            query=query,
            results=initial_results,
            top_k=5
        )
        
        return final_results
```

### 2. Embedding Pipeline with Fallback
```python
class EmbeddingPipeline:
    def __init__(self):
        self.primary_service = EmbeddingService(provider="openai")
        self.fallback_service = EmbeddingFallbackService()
        self.cache = EmbeddingCache()
    
    async def generate_embedding_with_cache(self, text: str):
        # Check cache first
        cached_embedding = await self.cache.get(text)
        if cached_embedding:
            return cached_embedding
        
        try:
            # Try primary service
            embedding = await self.primary_service.generate_embedding(text)
        except Exception:
            # Fallback to secondary service
            embedding = await self.fallback_service.generate_embedding_with_fallback(text)
        
        # Cache result
        await self.cache.set(text, embedding)
        return embedding
```

### 3. Search Strategy Selection
```python
class SearchStrategySelector:
    def __init__(self):
        self.strategies = {
            'vector': VectorSearchStrategy(),
            'keyword': KeywordSearchStrategy(),
            'hybrid': HybridSearchStrategy(),
            'agentic': AgenticRAGStrategy()
        }
    
    def select_strategy(self, query: str, context: Dict) -> str:
        # Simple heuristics for strategy selection
        if len(query.split()) > 10:
            return 'agentic'  # Complex queries benefit from AI enhancement
        elif any(keyword in query.lower() for keyword in ['exact', 'specific', 'definition']):
            return 'keyword'  # Exact matches for definitions
        else:
            return 'hybrid'  # Default to hybrid search
```

## Performance Optimization

### 1. Embedding Caching
```python
class EmbeddingCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 86400  # 24 hours
    
    async def get(self, text: str) -> Optional[List[float]]:
        key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None
    
    async def set(self, text: str, embedding: List[float]):
        key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
        await self.redis.setex(key, self.ttl, json.dumps(embedding))
```

### 2. Batch Processing Optimization
```python
class BatchEmbeddingProcessor:
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.embedding_service = EmbeddingService()
    
    async def process_documents(self, documents: List[str]):
        results = []
        
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            batch_embeddings = await self.embedding_service.generate_embeddings_batch(batch)
            results.extend(batch_embeddings)
        
        return results
```

## Monitoring and Analytics

### 1. Search Analytics
```python
class SearchAnalytics:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record_search(self, query: str, strategy: str, result_count: int, duration: float):
        self.metrics['searches'].append({
            'query': query,
            'strategy': strategy,
            'result_count': result_count,
            'duration': duration,
            'timestamp': time.time()
        })
    
    def get_popular_queries(self, limit: int = 10) -> List[str]:
        query_counts = Counter(search['query'] for search in self.metrics['searches'])
        return [query for query, count in query_counts.most_common(limit)]
```

### 2. Embedding Performance Monitoring
```python
class EmbeddingMetrics:
    def __init__(self):
        self.provider_stats = defaultdict(lambda: {'requests': 0, 'failures': 0, 'avg_duration': 0})
    
    def record_embedding_request(self, provider: str, duration: float, success: bool):
        stats = self.provider_stats[provider]
        stats['requests'] += 1
        if not success:
            stats['failures'] += 1
        
        # Update average duration
        stats['avg_duration'] = (stats['avg_duration'] * (stats['requests'] - 1) + duration) / stats['requests']
```

## Related Files
- **Parent components:** API endpoints, RAG workflows, document processing
- **Child components:** Database repositories, external API clients, ML models
- **Shared utilities:** Text processing, caching, configuration management

## Notes
- All services implement async patterns for I/O operations
- Comprehensive error handling and fallback strategies
- Performance optimization with caching and batch processing
- Provider abstraction for flexibility and redundancy
- Monitoring and analytics for optimization
- Extensible architecture for new search strategies
- Integration with external ML models and services

---
*Auto-generated documentation - verify accuracy before use*
