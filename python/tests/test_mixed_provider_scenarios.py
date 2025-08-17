"""
Mixed Provider Scenario Tests

Tests real-world scenarios where different providers are used for chat and embedding.
Focuses on integration between credential service and LLM provider service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.server.services.credential_service import credential_service
from src.server.services.llm_provider_service import get_llm_client, get_embedding_model


class TestMixedProviderScenarios:
    """Test suite for mixed provider scenarios"""

    @pytest.fixture(autouse=True)
    def setup_services(self):
        """Setup clean services for each test"""
        credential_service._cache.clear()
        credential_service._cache_initialized = False
        # Clear LLM service cache
        import src.server.services.llm_provider_service as llm_module
        llm_module._settings_cache.clear()
        yield
        credential_service._cache.clear()
        credential_service._cache_initialized = False
        llm_module._settings_cache.clear()

    @pytest.mark.asyncio
    async def test_openrouter_chat_openai_embedding_integration(self):
        """Test full integration: OpenRouter for chat, OpenAI for embeddings"""
        # Setup mixed provider configuration
        credential_service._cache = {
            "CHAT_PROVIDER": "openrouter",
            "EMBEDDING_PROVIDER": "openai",
            "MODEL_CHOICE": "anthropic/claude-3.5-sonnet",
            "EMBEDDING_MODEL": "text-embedding-3-small",
            "OPENROUTER_API_KEY": {"encrypted_value": "or_key", "is_encrypted": True},
            "OPENAI_API_KEY": {"encrypted_value": "oai_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt, \
             patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:

            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"
            mock_get_creds.return_value = credential_service._cache

            # Test chat client creation
            with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client

                async with get_llm_client() as chat_client:
                    assert chat_client == mock_client
                    # Should use OpenRouter configuration
                    mock_openai.assert_called_with(
                        api_key="decrypted_or_key",
                        base_url="https://openrouter.ai/api/v1"
                    )

            # Test embedding client creation
            with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client

                async with get_llm_client(use_embedding_provider=True) as embedding_client:
                    assert embedding_client == mock_client
                    # Should use OpenAI configuration
                    mock_openai.assert_called_with(api_key="decrypted_oai_key")

    @pytest.mark.asyncio
    async def test_ollama_chat_huggingface_embedding_integration(self):
        """Test full integration: Ollama for chat, Hugging Face for embeddings"""
        credential_service._cache = {
            "CHAT_PROVIDER": "ollama",
            "EMBEDDING_PROVIDER": "huggingface",
            "CHAT_BASE_URL": "http://ollama:11434/v1",
            "MODEL_CHOICE": "llama3.2:3b",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
            "HUGGINGFACE_API_KEY": {"encrypted_value": "hf_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt, \
             patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:

            mock_decrypt.return_value = "decrypted_hf_key"
            mock_get_creds.return_value = credential_service._cache

            # Test chat client (Ollama)
            with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client

                async with get_llm_client() as chat_client:
                    assert chat_client == mock_client
                    mock_openai.assert_called_with(
                        api_key="ollama",
                        base_url="http://ollama:11434/v1"
                    )

            # Test embedding client (Hugging Face)
            with patch("src.server.services.llm_provider_service.openai.AsyncOpenAI") as mock_openai:
                mock_client = MagicMock()
                mock_openai.return_value = mock_client

                async with get_llm_client(use_embedding_provider=True) as embedding_client:
                    assert embedding_client == mock_client
                    mock_openai.assert_called_with(
                        api_key="decrypted_hf_key",
                        base_url="https://api-inference.huggingface.co/models"
                    )

    @pytest.mark.asyncio
    async def test_embedding_model_selection_mixed_providers(self):
        """Test embedding model selection with mixed providers"""
        credential_service._cache = {
            "CHAT_PROVIDER": "openrouter",
            "EMBEDDING_PROVIDER": "huggingface",
            "EMBEDDING_MODEL": "sentence-transformers/all-mpnet-base-v2",
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:
            mock_get_creds.return_value = credential_service._cache

            # Test embedding model selection
            model = await get_embedding_model()
            assert model == "sentence-transformers/all-mpnet-base-v2"

            # Test with empty embedding model (should use provider default)
            credential_service._cache["EMBEDDING_MODEL"] = ""
            model = await get_embedding_model()
            assert model == "sentence-transformers/all-MiniLM-L6-v2"  # HF default

    @pytest.mark.asyncio
    async def test_provider_fallback_chain(self):
        """Test the complete fallback chain: split -> legacy -> defaults"""
        with patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:
            # Test 1: No providers configured (should use defaults)
            credential_service._cache = {}
            credential_service._cache_initialized = True
            mock_get_creds.return_value = credential_service._cache

            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "openrouter"  # Default chat provider

            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["provider"] == "openai"  # Default embedding provider

            # Test 2: Only LLM_PROVIDER configured (legacy fallback)
            credential_service._cache = {"LLM_PROVIDER": "google"}
            mock_get_creds.return_value = credential_service._cache

            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "google"

            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["provider"] == "google"

            # Test 3: Split providers configured (should use split)
            credential_service._cache.update({
                "CHAT_PROVIDER": "openrouter",
                "EMBEDDING_PROVIDER": "huggingface"
            })
            mock_get_creds.return_value = credential_service._cache

            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "openrouter"

            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["provider"] == "huggingface"

    @pytest.mark.asyncio
    async def test_base_url_fallback_chain(self):
        """Test base URL fallback: service-specific -> LLM_BASE_URL -> provider default"""
        credential_service._cache = {
            "CHAT_PROVIDER": "ollama",
            "EMBEDDING_PROVIDER": "local",
            "LLM_BASE_URL": "http://legacy-server:8080",
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:
            mock_get_creds.return_value = credential_service._cache

            # Test 1: No service-specific URLs (should use LLM_BASE_URL)
            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["base_url"] == "http://legacy-server:8080"

            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["base_url"] == "http://legacy-server:8080"

            # Test 2: Service-specific URLs override legacy
            credential_service._cache.update({
                "CHAT_BASE_URL": "http://ollama-server:11434/v1",
                "EMBEDDING_BASE_URL": "http://embedding-server:9000"
            })
            mock_get_creds.return_value = credential_service._cache

            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["base_url"] == "http://ollama-server:11434/v1"

            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["base_url"] == "http://embedding-server:9000"

    @pytest.mark.asyncio
    async def test_api_key_mapping_mixed_providers(self):
        """Test API key mapping for different provider combinations"""
        test_cases = [
            {
                "chat_provider": "openrouter",
                "embedding_provider": "openai",
                "expected_chat_key": "OPENROUTER_API_KEY",
                "expected_embedding_key": "OPENAI_API_KEY"
            },
            {
                "chat_provider": "google",
                "embedding_provider": "huggingface",
                "expected_chat_key": "GOOGLE_API_KEY",
                "expected_embedding_key": "HUGGINGFACE_API_KEY"
            },
            {
                "chat_provider": "ollama",
                "embedding_provider": "local",
                "expected_chat_key": None,  # Ollama doesn't need API key
                "expected_embedding_key": "LOCAL_EMBEDDING_API_KEY"
            }
        ]

        for case in test_cases:
            credential_service._cache = {
                "CHAT_PROVIDER": case["chat_provider"],
                "EMBEDDING_PROVIDER": case["embedding_provider"],
                "OPENROUTER_API_KEY": {"encrypted_value": "or_key", "is_encrypted": True},
                "OPENAI_API_KEY": {"encrypted_value": "oai_key", "is_encrypted": True},
                "GOOGLE_API_KEY": {"encrypted_value": "google_key", "is_encrypted": True},
                "HUGGINGFACE_API_KEY": {"encrypted_value": "hf_key", "is_encrypted": True},
                "LOCAL_EMBEDDING_API_KEY": {"encrypted_value": "local_key", "is_encrypted": True},
            }

            with patch.object(credential_service, "_decrypt_value") as mock_decrypt, \
                 patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:

                mock_decrypt.side_effect = lambda x: f"decrypted_{x}"
                mock_get_creds.return_value = credential_service._cache

                chat_config = await credential_service.get_active_provider("llm")
                embedding_config = await credential_service.get_active_provider("embedding")

                if case["expected_chat_key"]:
                    assert "decrypted_" in chat_config["api_key"]
                else:
                    assert chat_config["api_key"] in [case["chat_provider"], None]

                if case["expected_embedding_key"]:
                    assert "decrypted_" in embedding_config["api_key"]
                else:
                    assert embedding_config["api_key"] in [case["embedding_provider"], None]

    @pytest.mark.asyncio
    async def test_error_recovery_scenarios(self):
        """Test error recovery in mixed provider scenarios"""
        # Test credential service error fallback
        with patch.object(credential_service, "get_credentials_by_category") as mock_get:
            mock_get.side_effect = Exception("Database connection failed")

            # Should fallback to environment variables
            with patch("os.getenv") as mock_env:
                mock_env.return_value = "openai"

                config = await credential_service.get_active_provider("llm")
                assert config["provider"] == "openai"
                assert "error" not in config or config.get("api_key") is not None

    @pytest.mark.asyncio
    async def test_concurrent_provider_access(self):
        """Test concurrent access to different providers"""
        import asyncio

        credential_service._cache = {
            "CHAT_PROVIDER": "openrouter",
            "EMBEDDING_PROVIDER": "openai",
            "OPENROUTER_API_KEY": {"encrypted_value": "or_key", "is_encrypted": True},
            "OPENAI_API_KEY": {"encrypted_value": "oai_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt, \
             patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:

            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"
            mock_get_creds.return_value = credential_service._cache

            # Run concurrent requests for different service types
            async def get_chat_config():
                return await credential_service.get_active_provider("llm")

            async def get_embedding_config():
                return await credential_service.get_active_provider("embedding")

            # Execute concurrently
            chat_config, embedding_config = await asyncio.gather(
                get_chat_config(),
                get_embedding_config()
            )

            # Verify both configurations are correct
            assert chat_config["provider"] == "openrouter"
            assert embedding_config["provider"] == "openai"
            assert chat_config["api_key"] == "decrypted_or_key"
            assert embedding_config["api_key"] == "decrypted_oai_key"
