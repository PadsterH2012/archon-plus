"""
Integration Tests for Provider Combinations

End-to-end tests that verify the complete split provider functionality
works correctly across the entire system stack.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.server.services.credential_service import credential_service
from src.server.services.llm_provider_service import get_llm_client, get_embedding_model


class TestProviderCombinationIntegration:
    """Integration tests for provider combinations"""

    @pytest.fixture(autouse=True)
    def setup_integration_environment(self):
        """Setup clean environment for integration tests"""
        # Clear all caches
        credential_service._cache.clear()
        credential_service._cache_initialized = False
        
        import src.server.services.llm_provider_service as llm_module
        llm_module._settings_cache.clear()
        
        yield
        
        # Cleanup
        credential_service._cache.clear()
        credential_service._cache_initialized = False
        llm_module._settings_cache.clear()

    @pytest.mark.asyncio
    async def test_end_to_end_openrouter_openai_combination(self):
        """End-to-end test: OpenRouter for chat, OpenAI for embeddings"""
        # Setup complete configuration
        credential_service._cache = {
            "CHAT_PROVIDER": "openrouter",
            "EMBEDDING_PROVIDER": "openai",
            "CHAT_BASE_URL": "https://openrouter.ai/api/v1",
            "MODEL_CHOICE": "anthropic/claude-3.5-sonnet",
            "EMBEDDING_MODEL": "text-embedding-3-small",
            "OPENROUTER_API_KEY": {"encrypted_value": "or_key_123", "is_encrypted": True},
            "OPENAI_API_KEY": {"encrypted_value": "oai_key_456", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt:
            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"

            # Test 1: Chat client creation and configuration
            with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                mock_chat_client = MagicMock()
                mock_openai.return_value = mock_chat_client

                async with get_llm_client() as chat_client:
                    # Verify correct client configuration
                    assert chat_client == mock_chat_client
                    mock_openai.assert_called_with(
                        api_key="decrypted_or_key_123",
                        base_url="https://openrouter.ai/api/v1"
                    )

            # Test 2: Embedding client creation and configuration
            with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                mock_embedding_client = MagicMock()
                mock_openai.return_value = mock_embedding_client

                async with get_llm_client(use_embedding_provider=True) as embedding_client:
                    # Verify correct client configuration
                    assert embedding_client == mock_embedding_client
                    mock_openai.assert_called_with(api_key="decrypted_oai_key_456")

            # Test 3: Embedding model selection
            embedding_model = await get_embedding_model()
            assert embedding_model == "text-embedding-3-small"

    @pytest.mark.asyncio
    async def test_end_to_end_ollama_local_combination(self):
        """End-to-end test: Ollama for chat, Local server for embeddings"""
        credential_service._cache = {
            "CHAT_PROVIDER": "ollama",
            "EMBEDDING_PROVIDER": "local",
            "CHAT_BASE_URL": "http://ollama-server:11434/v1",
            "EMBEDDING_BASE_URL": "http://tei-server:8080",
            "MODEL_CHOICE": "llama3.2:3b",
            "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
            "LOCAL_EMBEDDING_API_KEY": {"encrypted_value": "local_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt:
            mock_decrypt.return_value = "decrypted_local_key"

            # Test chat client (Ollama)
            with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                mock_chat_client = MagicMock()
                mock_openai.return_value = mock_chat_client

                async with get_llm_client() as chat_client:
                    assert chat_client == mock_chat_client
                    mock_openai.assert_called_with(
                        api_key="ollama",
                        base_url="http://ollama-server:11434/v1"
                    )

            # Test embedding client (Local)
            with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                mock_embedding_client = MagicMock()
                mock_openai.return_value = mock_embedding_client

                async with get_llm_client(use_embedding_provider=True) as embedding_client:
                    assert embedding_client == mock_embedding_client
                    mock_openai.assert_called_with(
                        api_key="decrypted_local_key",
                        base_url="http://tei-server:8080"
                    )

            # Test embedding model
            embedding_model = await get_embedding_model()
            assert embedding_model == "all-MiniLM-L6-v2"

    @pytest.mark.asyncio
    async def test_migration_scenario_integration(self):
        """Test migration from legacy to split provider configuration"""
        # Phase 1: Legacy configuration
        credential_service._cache = {
            "LLM_PROVIDER": "openai",
            "MODEL_CHOICE": "gpt-4o-mini",
            "EMBEDDING_MODEL": "text-embedding-3-small",
            "OPENAI_API_KEY": {"encrypted_value": "legacy_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt:
            mock_decrypt.return_value = "decrypted_legacy_key"

            # Verify legacy behavior works
            chat_config = await credential_service.get_active_provider("llm")
            embedding_config = await credential_service.get_active_provider("embedding")
            
            assert chat_config["provider"] == "openai"
            assert embedding_config["provider"] == "openai"
            assert chat_config["api_key"] == "decrypted_legacy_key"
            assert embedding_config["api_key"] == "decrypted_legacy_key"

        # Phase 2: Partial migration (add chat provider)
        credential_service._cache.update({
            "CHAT_PROVIDER": "openrouter",
            "OPENROUTER_API_KEY": {"encrypted_value": "or_key", "is_encrypted": True},
        })

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt:
            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"

            chat_config = await credential_service.get_active_provider("llm")
            embedding_config = await credential_service.get_active_provider("embedding")
            
            # Chat should use new provider
            assert chat_config["provider"] == "openrouter"
            assert chat_config["api_key"] == "decrypted_or_key"
            
            # Embedding should still use legacy
            assert embedding_config["provider"] == "openai"
            assert embedding_config["api_key"] == "decrypted_legacy_key"

        # Phase 3: Complete migration
        credential_service._cache.update({
            "EMBEDDING_PROVIDER": "huggingface",
            "HUGGINGFACE_API_KEY": {"encrypted_value": "hf_key", "is_encrypted": True},
        })

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt:
            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"

            chat_config = await credential_service.get_active_provider("llm")
            embedding_config = await credential_service.get_active_provider("embedding")
            
            # Both should use split providers
            assert chat_config["provider"] == "openrouter"
            assert embedding_config["provider"] == "huggingface"
            assert chat_config["api_key"] == "decrypted_or_key"
            assert embedding_config["api_key"] == "decrypted_hf_key"

    @pytest.mark.asyncio
    async def test_concurrent_mixed_provider_operations(self):
        """Test concurrent operations with mixed providers"""
        credential_service._cache = {
            "CHAT_PROVIDER": "google",
            "EMBEDDING_PROVIDER": "huggingface",
            "MODEL_CHOICE": "gemini-1.5-flash",
            "EMBEDDING_MODEL": "sentence-transformers/all-mpnet-base-v2",
            "GOOGLE_API_KEY": {"encrypted_value": "google_key", "is_encrypted": True},
            "HUGGINGFACE_API_KEY": {"encrypted_value": "hf_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt:
            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"

            # Define concurrent operations
            async def create_chat_client():
                with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                    mock_client = MagicMock()
                    mock_openai.return_value = mock_client
                    async with get_llm_client() as client:
                        return client, mock_openai.call_args

            async def create_embedding_client():
                with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                    mock_client = MagicMock()
                    mock_openai.return_value = mock_client
                    async with get_llm_client(use_embedding_provider=True) as client:
                        return client, mock_openai.call_args

            async def get_embedding_model_async():
                return await get_embedding_model()

            # Execute operations concurrently
            results = await asyncio.gather(
                create_chat_client(),
                create_embedding_client(),
                get_embedding_model_async(),
                return_exceptions=True
            )

            # Verify all operations completed successfully
            assert len(results) == 3
            assert all(not isinstance(result, Exception) for result in results)

            # Verify embedding model result
            embedding_model = results[2]
            assert embedding_model == "sentence-transformers/all-mpnet-base-v2"

    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling across the integration stack"""
        # Test 1: Missing API key scenario
        credential_service._cache = {
            "CHAT_PROVIDER": "openrouter",
            "EMBEDDING_PROVIDER": "huggingface",
            # Missing API keys
        }
        credential_service._cache_initialized = True

        # Should handle gracefully without crashing
        chat_config = await credential_service.get_active_provider("llm")
        embedding_config = await credential_service.get_active_provider("embedding")
        
        assert chat_config["provider"] == "openrouter"
        assert embedding_config["provider"] == "huggingface"
        assert chat_config["api_key"] is None
        assert embedding_config["api_key"] is None

        # Test 2: Database connection failure
        with patch.object(credential_service, "get_credentials_by_category") as mock_get:
            mock_get.side_effect = Exception("Database connection failed")

            # Should fallback to environment variables
            with patch("os.getenv") as mock_env:
                mock_env.side_effect = lambda key, default=None: {
                    "LLM_PROVIDER": "openai",
                    "OPENAI_API_KEY": "env_key"
                }.get(key, default)

                config = await credential_service.get_active_provider("llm")
                assert config["provider"] == "openai"

    @pytest.mark.asyncio
    async def test_provider_switching_integration(self):
        """Test dynamic provider switching"""
        # Start with one configuration
        credential_service._cache = {
            "CHAT_PROVIDER": "openai",
            "EMBEDDING_PROVIDER": "openai",
            "OPENAI_API_KEY": {"encrypted_value": "oai_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt:
            mock_decrypt.return_value = "decrypted_oai_key"

            # Verify initial configuration
            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "openai"

            # Switch providers
            with patch.object(credential_service, "set_credential") as mock_set:
                mock_set.return_value = True

                # Switch chat provider
                result = await credential_service.set_active_provider("openrouter", "llm")
                assert result is True

                # Switch embedding provider
                result = await credential_service.set_active_provider("huggingface", "embedding")
                assert result is True

                # Verify correct calls were made
                assert mock_set.call_count == 2
                calls = mock_set.call_args_list
                
                assert calls[0][0] == ("CHAT_PROVIDER", "openrouter")
                assert calls[1][0] == ("EMBEDDING_PROVIDER", "huggingface")

    @pytest.mark.asyncio
    async def test_performance_mixed_providers(self):
        """Test performance characteristics with mixed providers"""
        import time

        credential_service._cache = {
            "CHAT_PROVIDER": "openrouter",
            "EMBEDDING_PROVIDER": "openai",
            "OPENROUTER_API_KEY": {"encrypted_value": "or_key", "is_encrypted": True},
            "OPENAI_API_KEY": {"encrypted_value": "oai_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt:
            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"

            # Measure configuration retrieval performance
            start_time = time.time()
            
            # Perform multiple operations
            for _ in range(10):
                chat_config = await credential_service.get_active_provider("llm")
                embedding_config = await credential_service.get_active_provider("embedding")
                
                assert chat_config["provider"] == "openrouter"
                assert embedding_config["provider"] == "openai"
            
            end_time = time.time()
            
            # Should complete quickly (under 1 second for 10 operations)
            assert (end_time - start_time) < 1.0
