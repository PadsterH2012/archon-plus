"""
Embedding Services

Handles all embedding-related operations.
"""

from .contextual_embedding_service import (
    generate_contextual_embedding,
    generate_contextual_embeddings_batch,
    process_chunk_with_context,
)
from .embedding_service import (
    create_embedding,
    create_embeddings_batch,
    create_embedding_with_fallback,
    create_embeddings_batch_with_fallback,
    get_embedding_provider_health,
    get_openai_client
)

__all__ = [
    # Embedding functions
    "create_embedding",
    "create_embeddings_batch",
    "create_embedding_with_fallback",
    "create_embeddings_batch_with_fallback",
    "get_embedding_provider_health",
    "get_openai_client",
    # Contextual embedding functions
    "generate_contextual_embedding",
    "generate_contextual_embeddings_batch",
    "process_chunk_with_context",
]
