"""
Tests for Text Embeddings Inference (TEI) integration.

Tests the containerized embedding tool integration with Archon,
including provider configuration, fallback scenarios, and health monitoring.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.server.services.llm_provider_service import get_llm_client, get_embedding_model_default
from src.server.services.credential_service import credential_service


class TestTEIProviderIntegration:
    """Test TEI provider integration with Archon."""

    @pytest.mark.asyncio
    async def test_tei_client_creation(self):
        """Test TEI client creation with default configuration."""
        with patch('src.server.services.llm_provider_service.openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            async with get_llm_client(provider="tei", use_embedding_provider=True) as client:
                assert client is not None
                
                # Verify OpenAI client was created with TEI configuration
                mock_openai.assert_called_once_with(
                    api_key="tei",
                    base_url="http://archon-embeddings:80"
                )

    @pytest.mark.asyncio
    async def test_tei_client_custom_base_url(self):
        """Test TEI client creation with custom base URL."""
        custom_url = "http://custom-tei:8080"
        
        with patch('src.server.services.llm_provider_service.openai.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            async with get_llm_client(
                provider="tei", 
                base_url=custom_url,
                use_embedding_provider=True
            ) as client:
                assert client is not None
                
                # Verify custom base URL was used
                mock_openai.assert_called_once_with(
                    api_key="tei",
                    base_url=custom_url
                )

    def test_tei_embedding_model_default(self):
        """Test TEI embedding model default."""
        default_model = get_embedding_model_default("tei")
        assert default_model == "sentence-transformers/all-MiniLM-L6-v2"

    @pytest.mark.asyncio
    async def test_tei_in_fallback_chain(self):
        """Test TEI provider in fallback configuration."""
        with patch.object(credential_service, 'get_rag_settings') as mock_settings:
            # Mock settings with TEI in fallback chain
            mock_settings.return_value = {
                "EMBEDDING_FALLBACK_PROVIDERS": "openai,ollama,tei,local",
                "ENABLE_PROVIDER_FALLBACK": True
            }
            
            fallback_providers = await credential_service._get_fallback_providers(
                "embedding", mock_settings.return_value
            )
            
            # Verify TEI is included in fallback chain
            provider_names = [p["provider"] for p in fallback_providers]
            assert "tei" in provider_names
            
            # Find TEI provider config
            tei_config = next(p for p in fallback_providers if p["provider"] == "tei")
            assert tei_config["api_key"] == "tei"
            assert tei_config["base_url"] == "http://archon-embeddings:80"
            assert tei_config["model"] == "sentence-transformers/all-MiniLM-L6-v2"

    @pytest.mark.asyncio
    async def test_tei_provider_health_check(self):
        """Test TEI provider health check functionality."""
        from src.server.services.embeddings.embedding_fallback_service import embedding_fallback_service
        
        # Mock successful TEI response
        mock_embedding = [0.1, 0.2, 0.3, 0.4]
        
        with patch('src.server.services.embeddings.embedding_fallback_service.get_llm_client') as mock_client:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=mock_embedding)]
            
            mock_client_instance = AsyncMock()
            mock_client_instance.embeddings.create.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Test health check
            provider_config = {
                "provider": "tei",
                "api_key": "tei",
                "base_url": "http://archon-embeddings:80",
                "model": "sentence-transformers/all-MiniLM-L6-v2"
            }
            
            is_healthy = await embedding_fallback_service._test_provider_health(provider_config)
            assert is_healthy is True
            
            # Verify embedding call was made
            mock_client_instance.embeddings.create.assert_called_once_with(
                model="sentence-transformers/all-MiniLM-L6-v2",
                input=["health check"]
            )

    @pytest.mark.asyncio
    async def test_tei_embedding_creation(self):
        """Test embedding creation using TEI provider."""
        from src.server.services.embeddings import create_embedding_with_fallback
        
        mock_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        test_text = "This is a test text for embedding"
        
        with patch('src.server.services.embeddings.embedding_fallback_service.get_llm_client') as mock_client:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=mock_embedding)]
            
            mock_client_instance = AsyncMock()
            mock_client_instance.embeddings.create.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Test embedding creation with TEI provider
            embedding, provider_used = await create_embedding_with_fallback(
                test_text, provider="tei"
            )
            
            assert embedding == mock_embedding
            assert provider_used == "tei"
            
            # Verify correct model was used
            mock_client_instance.embeddings.create.assert_called_once_with(
                model="sentence-transformers/all-MiniLM-L6-v2",
                input=[test_text]
            )

    @pytest.mark.asyncio
    async def test_tei_batch_embedding_creation(self):
        """Test batch embedding creation using TEI provider."""
        from src.server.services.embeddings import create_embeddings_batch_with_fallback
        
        test_texts = ["Text 1", "Text 2", "Text 3"]
        mock_embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        
        with patch('src.server.services.embeddings.embedding_fallback_service.embedding_fallback_service.create_embedding_with_fallback') as mock_create:
            # Mock successful embeddings for all texts
            mock_create.side_effect = [
                (mock_embeddings[0], "tei"),
                (mock_embeddings[1], "tei"),
                (mock_embeddings[2], "tei"),
            ]
            
            result = await create_embeddings_batch_with_fallback(
                test_texts, provider="tei"
            )
            
            assert result.success_count == 3
            assert result.failure_count == 0
            assert len(result.embeddings) == 3
            assert result.embeddings == mock_embeddings

    @pytest.mark.asyncio
    async def test_tei_fallback_from_openai(self):
        """Test fallback from OpenAI to TEI when OpenAI fails."""
        from src.server.services.embeddings.embedding_fallback_service import embedding_fallback_service
        
        test_text = "Test text for fallback scenario"
        mock_embedding = [0.7, 0.8, 0.9]
        
        # Mock provider configuration with TEI as fallback
        provider_config = {
            "provider": "openai",
            "api_key": "test-key",
            "base_url": None,
            "model": "text-embedding-3-small",
            "fallback_providers": [
                {
                    "provider": "tei",
                    "api_key": "tei",
                    "base_url": "http://archon-embeddings:80",
                    "model": "sentence-transformers/all-MiniLM-L6-v2"
                }
            ]
        }
        
        with patch('src.server.services.embeddings.embedding_fallback_service.get_llm_client') as mock_client:
            call_count = 0
            
            def mock_client_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                
                mock_client_instance = AsyncMock()
                
                if call_count == 1:
                    # First call (OpenAI) fails
                    mock_client_instance.embeddings.create.side_effect = Exception("OpenAI API Error")
                else:
                    # Second call (TEI) succeeds
                    mock_response = MagicMock()
                    mock_response.data = [MagicMock(embedding=mock_embedding)]
                    mock_client_instance.embeddings.create.return_value = mock_response
                
                return AsyncMock(__aenter__=AsyncMock(return_value=mock_client_instance))
            
            mock_client.side_effect = mock_client_side_effect
            
            # Test fallback scenario
            embedding, provider_used = await embedding_fallback_service.create_embedding_with_fallback(
                test_text, provider_config
            )
            
            assert embedding == mock_embedding
            assert provider_used == "tei"
            assert call_count == 2  # OpenAI failed, TEI succeeded

    @pytest.mark.asyncio
    async def test_tei_api_key_not_required(self):
        """Test that TEI provider doesn't require API key."""
        api_key = await credential_service._get_provider_api_key("tei")
        assert api_key == "tei"  # Returns provider name for providers without API keys

    def test_tei_base_url_default(self):
        """Test TEI provider base URL default."""
        base_url = credential_service._get_provider_base_url("tei", {}, "EMBEDDING_BASE_URL")
        assert base_url == "http://archon-embeddings:80"

    @pytest.mark.asyncio
    async def test_tei_provider_configuration_validation(self):
        """Test TEI provider configuration validation."""
        # Test that TEI is recognized as a valid provider
        valid_providers = ["openai", "google", "ollama", "huggingface", "tei", "local"]
        
        # This should not raise an exception
        try:
            async with get_llm_client(provider="tei", use_embedding_provider=True):
                pass
        except ValueError as e:
            if "Unsupported LLM provider" in str(e):
                pytest.fail("TEI provider should be supported")

    @pytest.mark.asyncio
    async def test_tei_model_configuration(self):
        """Test TEI model configuration with custom model."""
        custom_model = "sentence-transformers/paraphrase-MiniLM-L6-v2"
        
        with patch('src.server.services.embeddings.embedding_fallback_service.get_llm_client') as mock_client:
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
            
            mock_client_instance = AsyncMock()
            mock_client_instance.embeddings.create.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            # Test with custom model
            provider_config = {
                "provider": "tei",
                "api_key": "tei",
                "base_url": "http://archon-embeddings:80",
                "model": custom_model
            }
            
            from src.server.services.embeddings.embedding_fallback_service import embedding_fallback_service
            
            embedding, provider_used = await embedding_fallback_service.create_embedding_with_fallback(
                "test text", provider_config
            )
            
            # Verify custom model was used
            mock_client_instance.embeddings.create.assert_called_once_with(
                model=custom_model,
                input=["test text"]
            )
            
            assert provider_used == "tei"
