"""
Embedding Fallback Service

Provides intelligent fallback mechanism for embedding providers when primary provider fails.
Implements automatic failover with health checking and graceful degradation.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

from ...config.logfire_config import safe_span, search_logger
from ..credential_service import credential_service
from ..llm_provider_service import get_llm_client
from .embedding_exceptions import (
    EmbeddingAPIError,
    EmbeddingError,
    EmbeddingQuotaExhaustedError,
    EmbeddingRateLimitError,
)
# Import moved to avoid circular import - will import locally when needed


@dataclass
class ProviderHealth:
    """Tracks health status of embedding providers."""
    
    provider: str
    is_healthy: bool = True
    last_failure: float | None = None
    failure_count: int = 0
    last_success: float | None = None
    consecutive_failures: int = 0
    
    def record_success(self):
        """Record successful operation."""
        self.is_healthy = True
        self.last_success = time.time()
        self.consecutive_failures = 0
    
    def record_failure(self):
        """Record failed operation."""
        self.last_failure = time.time()
        self.failure_count += 1
        self.consecutive_failures += 1
        
        # Mark as unhealthy after 3 consecutive failures
        if self.consecutive_failures >= 3:
            self.is_healthy = False
    
    def should_retry(self, cooldown_seconds: int = 300) -> bool:
        """Check if provider should be retried after cooldown period."""
        if self.is_healthy:
            return True
        
        if self.last_failure is None:
            return True
            
        # Allow retry after cooldown period
        return (time.time() - self.last_failure) > cooldown_seconds


class EmbeddingFallbackService:
    """Service that provides embedding fallback capabilities."""
    
    def __init__(self):
        self.provider_health: dict[str, ProviderHealth] = {}
        self._health_check_interval = 60  # seconds
        self._last_health_check = 0
    
    def _get_provider_health(self, provider: str) -> ProviderHealth:
        """Get or create provider health tracker."""
        if provider not in self.provider_health:
            self.provider_health[provider] = ProviderHealth(provider=provider)
        return self.provider_health[provider]
    
    async def _test_provider_health(self, provider_config: dict[str, Any]) -> bool:
        """Test if a provider is healthy by attempting a simple embedding."""
        try:
            # Use a simple test text
            test_text = "health check"
            
            async with get_llm_client(
                provider=provider_config["provider"],
                use_embedding_provider=True
            ) as client:
                response = await client.embeddings.create(
                    model=provider_config["model"] or "text-embedding-3-small",
                    input=[test_text],
                )
                
                # If we get a response with embeddings, provider is healthy
                return len(response.data) > 0 and len(response.data[0].embedding) > 0
                
        except Exception as e:
            search_logger.warning(f"Health check failed for provider {provider_config['provider']}: {e}")
            return False
    
    async def create_embedding_with_fallback(
        self, 
        text: str, 
        primary_provider: dict[str, Any] | None = None
    ) -> tuple[list[float], str]:
        """
        Create embedding with automatic fallback to alternative providers.
        
        Args:
            text: Text to create embedding for
            primary_provider: Primary provider configuration (if None, gets from credential service)
            
        Returns:
            Tuple of (embedding, provider_used)
            
        Raises:
            EmbeddingError: When all providers fail
        """
        # Get provider configuration
        if primary_provider is None:
            primary_provider = await credential_service.get_active_provider("embedding")
        
        fallback_providers = primary_provider.get("fallback_providers", [])
        all_providers = [primary_provider] + fallback_providers
        
        last_error = None
        
        with safe_span("create_embedding_with_fallback", text_length=len(text)) as span:
            for i, provider_config in enumerate(all_providers):
                provider_name = provider_config["provider"]
                health = self._get_provider_health(provider_name)
                
                # Skip unhealthy providers unless it's the last option
                if not health.should_retry() and i < len(all_providers) - 1:
                    search_logger.info(f"Skipping unhealthy provider {provider_name}")
                    continue
                
                try:
                    search_logger.info(f"Attempting embedding with provider: {provider_name}")
                    
                    async with get_llm_client(
                        provider=provider_name,
                        use_embedding_provider=True
                    ) as client:
                        response = await client.embeddings.create(
                            model=provider_config["model"] or "text-embedding-3-small",
                            input=[text],
                        )
                        
                        if response.data and len(response.data) > 0:
                            embedding = response.data[0].embedding
                            
                            # Record success
                            health.record_success()
                            
                            # Log fallback usage
                            if i > 0:
                                search_logger.warning(
                                    f"Successfully used fallback provider {provider_name} "
                                    f"after {i} failed attempts"
                                )
                                span.set_attribute("fallback_used", True)
                                span.set_attribute("fallback_provider", provider_name)
                                span.set_attribute("fallback_attempt", i + 1)
                            
                            span.set_attribute("provider_used", provider_name)
                            span.set_attribute("success", True)
                            
                            return embedding, provider_name
                
                except Exception as e:
                    # Record failure
                    health.record_failure()
                    last_error = e
                    
                    search_logger.error(
                        f"Provider {provider_name} failed: {e}",
                        exc_info=True
                    )
                    
                    # Convert to appropriate exception type for better error handling
                    if "insufficient_quota" in str(e).lower():
                        last_error = EmbeddingQuotaExhaustedError(
                            f"Quota exhausted for {provider_name}: {e}",
                            text_preview=text
                        )
                    elif "rate_limit" in str(e).lower():
                        last_error = EmbeddingRateLimitError(
                            f"Rate limit for {provider_name}: {e}",
                            text_preview=text
                        )
                    else:
                        last_error = EmbeddingAPIError(
                            f"API error for {provider_name}: {e}",
                            text_preview=text,
                            original_error=e
                        )
                    
                    # Continue to next provider
                    continue
            
            # All providers failed
            span.set_attribute("all_providers_failed", True)
            span.set_attribute("providers_attempted", len(all_providers))
            
            if last_error:
                raise last_error
            else:
                raise EmbeddingAPIError(
                    "All embedding providers failed",
                    text_preview=text
                )
    
    async def create_embeddings_batch_with_fallback(
        self,
        texts: list[str],
        websocket: Any | None = None,
        progress_callback: Any | None = None,
        primary_provider: dict[str, Any] | None = None,
    ):
        """
        Create embeddings for multiple texts with fallback support.

        Args:
            texts: List of texts to create embeddings for
            websocket: Optional WebSocket for progress updates
            progress_callback: Optional callback for progress reporting
            primary_provider: Primary provider configuration

        Returns:
            EmbeddingBatchResult with successful embeddings and failure details
        """
        # Import locally to avoid circular import
        from .embedding_service import EmbeddingBatchResult

        if not texts:
            return EmbeddingBatchResult()
        
        result = EmbeddingBatchResult()
        
        with safe_span("create_embeddings_batch_with_fallback", text_count=len(texts)) as span:
            # Process texts individually to allow per-text fallback
            for i, text in enumerate(texts):
                try:
                    embedding, provider_used = await self.create_embedding_with_fallback(
                        text, primary_provider
                    )
                    result.add_success(embedding, text)
                    
                    # Log provider usage for monitoring
                    if provider_used != (primary_provider or {}).get("provider", "unknown"):
                        search_logger.info(f"Used fallback provider {provider_used} for text {i}")
                
                except Exception as e:
                    result.add_failure(text, e, i)
                    search_logger.error(f"Failed to create embedding for text {i}: {e}")
                
                # Progress reporting
                if progress_callback:
                    processed = i + 1
                    progress = (processed / len(texts)) * 100
                    message = f"Processed {processed}/{len(texts)} texts"
                    if result.has_failures:
                        message += f" ({result.failure_count} failed)"
                    await progress_callback(message, progress)
                
                # WebSocket update
                if websocket:
                    processed = i + 1
                    ws_progress = (processed / len(texts)) * 100
                    await websocket.send_json({
                        "type": "embedding_progress",
                        "processed": processed,
                        "successful": result.success_count,
                        "failed": result.failure_count,
                        "total": len(texts),
                        "percentage": ws_progress,
                    })
                
                # Yield control
                await asyncio.sleep(0.01)
            
            span.set_attribute("embeddings_created", result.success_count)
            span.set_attribute("embeddings_failed", result.failure_count)
            span.set_attribute("success", not result.has_failures)
            
            return result
    
    async def get_provider_health_status(self) -> dict[str, dict[str, Any]]:
        """Get health status of all tracked providers."""
        status = {}
        
        for provider, health in self.provider_health.items():
            status[provider] = {
                "is_healthy": health.is_healthy,
                "failure_count": health.failure_count,
                "consecutive_failures": health.consecutive_failures,
                "last_failure": health.last_failure,
                "last_success": health.last_success,
                "should_retry": health.should_retry(),
            }
        
        return status


# Global instance
embedding_fallback_service = EmbeddingFallbackService()
