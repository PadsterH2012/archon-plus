"""
Tests for embedding provider fallback functionality.

Tests the intelligent fallback system that automatically switches to alternative
providers when the primary provider fails or becomes unavailable.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.server.services.embeddings.embedding_fallback_service import (
    EmbeddingFallbackService,
    ProviderHealth,
)
from src.server.services.embeddings.embedding_exceptions import (
    EmbeddingAPIError,
    EmbeddingQuotaExhaustedError,
    EmbeddingRateLimitError,
)


class TestProviderHealth:
    """Test provider health tracking."""

    def test_provider_health_initialization(self):
        """Test provider health is initialized correctly."""
        health = ProviderHealth(provider="openai")
        
        assert health.provider == "openai"
        assert health.is_healthy is True
        assert health.failure_count == 0
        assert health.consecutive_failures == 0
        assert health.last_failure is None
        assert health.last_success is None

    def test_record_success(self):
        """Test recording successful operations."""
        health = ProviderHealth(provider="openai")
        health.consecutive_failures = 2
        health.is_healthy = False
        
        health.record_success()
        
        assert health.is_healthy is True
        assert health.consecutive_failures == 0
        assert health.last_success is not None

    def test_record_failure(self):
        """Test recording failed operations."""
        health = ProviderHealth(provider="openai")
        
        # First failure
        health.record_failure()
        assert health.failure_count == 1
        assert health.consecutive_failures == 1
        assert health.is_healthy is True  # Still healthy after 1 failure
        
        # Second failure
        health.record_failure()
        assert health.failure_count == 2
        assert health.consecutive_failures == 2
        assert health.is_healthy is True  # Still healthy after 2 failures
        
        # Third failure - should mark as unhealthy
        health.record_failure()
        assert health.failure_count == 3
        assert health.consecutive_failures == 3
        assert health.is_healthy is False  # Now unhealthy

    def test_should_retry_healthy_provider(self):
        """Test that healthy providers should always be retried."""
        health = ProviderHealth(provider="openai")
        assert health.should_retry() is True

    def test_should_retry_after_cooldown(self):
        """Test that unhealthy providers can be retried after cooldown."""
        health = ProviderHealth(provider="openai")
        health.is_healthy = False
        health.last_failure = 0  # Very old failure
        
        # Should retry after cooldown
        assert health.should_retry(cooldown_seconds=1) is True

    def test_should_not_retry_during_cooldown(self):
        """Test that unhealthy providers are not retried during cooldown."""
        import time
        
        health = ProviderHealth(provider="openai")
        health.is_healthy = False
        health.last_failure = time.time()  # Recent failure
        
        # Should not retry during cooldown
        assert health.should_retry(cooldown_seconds=300) is False


class TestEmbeddingFallbackService:
    """Test embedding fallback service functionality."""

    @pytest.fixture
    def fallback_service(self):
        """Create a fresh fallback service for each test."""
        return EmbeddingFallbackService()

    @pytest.fixture
    def mock_provider_config(self):
        """Mock provider configuration."""
        return {
            "provider": "openai",
            "api_key": "test-key",
            "base_url": None,
            "model": "text-embedding-3-small",
            "fallback_providers": [
                {
                    "provider": "ollama",
                    "api_key": None,
                    "base_url": "http://ollama:11434",
                    "model": "nomic-embed-text"
                },
                {
                    "provider": "local",
                    "api_key": "local",
                    "base_url": "http://localhost:8080",
                    "model": "all-MiniLM-L6-v2"
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_successful_primary_provider(self, fallback_service, mock_provider_config):
        """Test successful embedding with primary provider."""
        mock_embedding = [0.1, 0.2, 0.3]
        
        with patch('src.server.services.embeddings.embedding_fallback_service.get_llm_client') as mock_client:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=mock_embedding)]
            
            mock_client_instance = AsyncMock()
            mock_client_instance.embeddings.create.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Test embedding creation
            embedding, provider_used = await fallback_service.create_embedding_with_fallback(
                "test text", mock_provider_config
            )
            
            assert embedding == mock_embedding
            assert provider_used == "openai"
            
            # Verify primary provider health is good
            health = fallback_service._get_provider_health("openai")
            assert health.is_healthy is True
            assert health.consecutive_failures == 0

    @pytest.mark.asyncio
    async def test_fallback_to_secondary_provider(self, fallback_service, mock_provider_config):
        """Test fallback when primary provider fails."""
        mock_embedding = [0.4, 0.5, 0.6]
        
        with patch('src.server.services.embeddings.embedding_fallback_service.get_llm_client') as mock_client:
            call_count = 0
            
            def mock_client_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                
                mock_client_instance = AsyncMock()
                
                if call_count == 1:
                    # First call (primary provider) fails
                    mock_client_instance.embeddings.create.side_effect = Exception("API Error")
                else:
                    # Second call (fallback provider) succeeds
                    mock_response = MagicMock()
                    mock_response.data = [MagicMock(embedding=mock_embedding)]
                    mock_client_instance.embeddings.create.return_value = mock_response
                
                return AsyncMock(__aenter__=AsyncMock(return_value=mock_client_instance))
            
            mock_client.side_effect = mock_client_side_effect
            
            # Test embedding creation with fallback
            embedding, provider_used = await fallback_service.create_embedding_with_fallback(
                "test text", mock_provider_config
            )
            
            assert embedding == mock_embedding
            assert provider_used == "ollama"  # Should use first fallback
            
            # Verify primary provider health is degraded
            primary_health = fallback_service._get_provider_health("openai")
            assert primary_health.failure_count == 1
            
            # Verify fallback provider health is good
            fallback_health = fallback_service._get_provider_health("ollama")
            assert fallback_health.is_healthy is True

    @pytest.mark.asyncio
    async def test_all_providers_fail(self, fallback_service, mock_provider_config):
        """Test when all providers fail."""
        with patch('src.server.services.embeddings.embedding_fallback_service.get_llm_client') as mock_client:
            # All providers fail
            mock_client_instance = AsyncMock()
            mock_client_instance.embeddings.create.side_effect = Exception("All providers down")
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Test that appropriate exception is raised
            with pytest.raises(EmbeddingAPIError) as exc_info:
                await fallback_service.create_embedding_with_fallback(
                    "test text", mock_provider_config
                )
            
            assert "All providers down" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_quota_exhausted_fallback(self, fallback_service, mock_provider_config):
        """Test fallback when primary provider quota is exhausted."""
        mock_embedding = [0.7, 0.8, 0.9]
        
        with patch('src.server.services.embeddings.embedding_fallback_service.get_llm_client') as mock_client:
            call_count = 0
            
            def mock_client_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                
                mock_client_instance = AsyncMock()
                
                if call_count == 1:
                    # Primary provider quota exhausted
                    mock_client_instance.embeddings.create.side_effect = Exception("insufficient_quota")
                else:
                    # Fallback provider succeeds
                    mock_response = MagicMock()
                    mock_response.data = [MagicMock(embedding=mock_embedding)]
                    mock_client_instance.embeddings.create.return_value = mock_response
                
                return AsyncMock(__aenter__=AsyncMock(return_value=mock_client_instance))
            
            mock_client.side_effect = mock_client_side_effect
            
            # Test embedding creation
            embedding, provider_used = await fallback_service.create_embedding_with_fallback(
                "test text", mock_provider_config
            )
            
            assert embedding == mock_embedding
            assert provider_used == "ollama"

    @pytest.mark.asyncio
    async def test_batch_embedding_with_fallback(self, fallback_service, mock_provider_config):
        """Test batch embedding with fallback support."""
        texts = ["text1", "text2", "text3"]
        mock_embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        
        with patch.object(fallback_service, 'create_embedding_with_fallback') as mock_create:
            # Mock successful embeddings with different providers
            mock_create.side_effect = [
                (mock_embeddings[0], "openai"),
                (mock_embeddings[1], "ollama"),  # Fallback used
                (mock_embeddings[2], "openai"),
            ]
            
            result = await fallback_service.create_embeddings_batch_with_fallback(
                texts, primary_provider=mock_provider_config
            )
            
            assert result.success_count == 3
            assert result.failure_count == 0
            assert len(result.embeddings) == 3
            assert result.embeddings == mock_embeddings

    @pytest.mark.asyncio
    async def test_provider_health_status(self, fallback_service):
        """Test getting provider health status."""
        # Add some provider health data
        fallback_service.provider_health["openai"] = ProviderHealth("openai")
        fallback_service.provider_health["openai"].record_failure()
        
        fallback_service.provider_health["ollama"] = ProviderHealth("ollama")
        fallback_service.provider_health["ollama"].record_success()
        
        status = await fallback_service.get_provider_health_status()
        
        assert "openai" in status
        assert "ollama" in status
        assert status["openai"]["failure_count"] == 1
        assert status["ollama"]["is_healthy"] is True

    @pytest.mark.asyncio
    async def test_unhealthy_provider_skipping(self, fallback_service, mock_provider_config):
        """Test that unhealthy providers are skipped during fallback."""
        # Mark primary provider as unhealthy
        primary_health = fallback_service._get_provider_health("openai")
        primary_health.is_healthy = False
        primary_health.last_failure = 999999999  # Recent failure
        
        mock_embedding = [0.1, 0.2, 0.3]
        
        with patch('src.server.services.embeddings.embedding_fallback_service.get_llm_client') as mock_client:
            # Only fallback provider should be called
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=mock_embedding)]
            
            mock_client_instance = AsyncMock()
            mock_client_instance.embeddings.create.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            embedding, provider_used = await fallback_service.create_embedding_with_fallback(
                "test text", mock_provider_config
            )
            
            assert embedding == mock_embedding
            assert provider_used == "ollama"  # Should skip unhealthy primary
            
            # Verify only one call was made (to fallback provider)
            assert mock_client.call_count == 1
