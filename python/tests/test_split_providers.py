"""
Comprehensive Tests for Split Provider Functionality

Tests the new split provider system that allows separate chat and embedding providers.
Covers provider selection, configuration, fallback mechanisms, and backward compatibility.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.server.services.credential_service import credential_service


class TestSplitProviderConfiguration:
    """Test suite for split provider configuration and selection"""

    @pytest.fixture(autouse=True)
    def setup_credential_service(self):
        """Setup clean credential service for each test"""
        credential_service._cache.clear()
        credential_service._cache_initialized = False
        yield
        credential_service._cache.clear()
        credential_service._cache_initialized = False

    @pytest.mark.asyncio
    async def test_openrouter_chat_openai_embedding(self):
        """Test OpenRouter for chat, OpenAI for embeddings"""
        # Setup split provider configuration
        credential_service._cache = {
            "CHAT_PROVIDER": "openrouter",
            "EMBEDDING_PROVIDER": "openai",
            "CHAT_BASE_URL": "https://openrouter.ai/api/v1",
            "EMBEDDING_BASE_URL": None,
            "MODEL_CHOICE": "anthropic/claude-3.5-sonnet",
            "EMBEDDING_MODEL": "text-embedding-3-small",
            "OPENROUTER_API_KEY": {"encrypted_value": "encrypted_openrouter_key", "is_encrypted": True},
            "OPENAI_API_KEY": {"encrypted_value": "encrypted_openai_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt, \
             patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:

            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"
            mock_get_creds.return_value = credential_service._cache

            # Test chat provider configuration
            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "openrouter"
            assert chat_config["model"] == "anthropic/claude-3.5-sonnet"
            assert chat_config["base_url"] == "https://openrouter.ai/api/v1"
            assert chat_config["api_key"] == "decrypted_encrypted_openrouter_key"

            # Test embedding provider configuration
            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["provider"] == "openai"
            assert embedding_config["model"] == "text-embedding-3-small"
            assert embedding_config["base_url"] is None  # Uses OpenAI default
            assert embedding_config["api_key"] == "decrypted_encrypted_openai_key"

    @pytest.mark.asyncio
    async def test_ollama_chat_local_embedding(self):
        """Test Ollama for chat, local server for embeddings"""
        credential_service._cache = {
            "CHAT_PROVIDER": "ollama",
            "EMBEDDING_PROVIDER": "local",
            "CHAT_BASE_URL": "http://ollama:11434/v1",
            "EMBEDDING_BASE_URL": "http://tei-container:8080",
            "MODEL_CHOICE": "llama3.2:3b",
            "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
            "LOCAL_EMBEDDING_API_KEY": {"encrypted_value": "local_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt, \
             patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:

            mock_decrypt.return_value = "decrypted_local_key"
            mock_get_creds.return_value = credential_service._cache

            # Test chat provider (Ollama - no API key needed)
            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "ollama"
            assert chat_config["model"] == "llama3.2:3b"
            assert chat_config["base_url"] == "http://ollama:11434/v1"
            assert chat_config["api_key"] == "ollama"

            # Test embedding provider (Local server)
            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["provider"] == "local"
            assert embedding_config["model"] == "all-MiniLM-L6-v2"
            assert embedding_config["base_url"] == "http://tei-container:8080"
            assert embedding_config["api_key"] == "decrypted_local_key"

    @pytest.mark.asyncio
    async def test_google_chat_huggingface_embedding(self):
        """Test Google for chat, Hugging Face for embeddings"""
        credential_service._cache = {
            "CHAT_PROVIDER": "google",
            "EMBEDDING_PROVIDER": "huggingface",
            "MODEL_CHOICE": "gemini-1.5-flash",
            "EMBEDDING_MODEL": "sentence-transformers/all-mpnet-base-v2",
            "GOOGLE_API_KEY": {"encrypted_value": "google_key", "is_encrypted": True},
            "HUGGINGFACE_API_KEY": {"encrypted_value": "hf_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt, \
             patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:

            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"
            mock_get_creds.return_value = credential_service._cache

            # Test chat provider (Google)
            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "google"
            assert chat_config["model"] == "gemini-1.5-flash"
            assert chat_config["base_url"] == "https://generativelanguage.googleapis.com/v1beta/openai/"
            assert chat_config["api_key"] == "decrypted_google_key"

            # Test embedding provider (Hugging Face)
            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["provider"] == "huggingface"
            assert embedding_config["model"] == "sentence-transformers/all-mpnet-base-v2"
            assert embedding_config["base_url"] == "https://api-inference.huggingface.co/models"
            assert embedding_config["api_key"] == "decrypted_hf_key"

    @pytest.mark.asyncio
    async def test_backward_compatibility_llm_provider(self):
        """Test backward compatibility with existing LLM_PROVIDER configuration"""
        # Setup legacy configuration (no split providers)
        credential_service._cache = {
            "LLM_PROVIDER": "openai",
            "LLM_BASE_URL": None,
            "MODEL_CHOICE": "gpt-4o-mini",
            "EMBEDDING_MODEL": "text-embedding-3-small",
            "OPENAI_API_KEY": {"encrypted_value": "openai_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt, \
             patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:

            mock_decrypt.return_value = "decrypted_openai_key"
            mock_get_creds.return_value = credential_service._cache

            # Both chat and embedding should fallback to LLM_PROVIDER
            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "openai"
            assert chat_config["model"] == "gpt-4o-mini"
            assert chat_config["api_key"] == "decrypted_openai_key"

            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["provider"] == "openai"
            assert embedding_config["model"] == "text-embedding-3-small"
            assert embedding_config["api_key"] == "decrypted_openai_key"

    @pytest.mark.asyncio
    async def test_partial_migration_scenario(self):
        """Test scenario where only one split provider is configured"""
        # Setup partial migration (only CHAT_PROVIDER set)
        credential_service._cache = {
            "LLM_PROVIDER": "openai",
            "CHAT_PROVIDER": "openrouter",  # Only chat provider migrated
            "MODEL_CHOICE": "anthropic/claude-3.5-sonnet",
            "EMBEDDING_MODEL": "text-embedding-3-small",
            "OPENAI_API_KEY": {"encrypted_value": "openai_key", "is_encrypted": True},
            "OPENROUTER_API_KEY": {"encrypted_value": "openrouter_key", "is_encrypted": True},
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "_decrypt_value") as mock_decrypt, \
             patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:

            mock_decrypt.side_effect = lambda x: f"decrypted_{x}"
            mock_get_creds.return_value = credential_service._cache

            # Chat should use CHAT_PROVIDER
            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "openrouter"
            assert chat_config["api_key"] == "decrypted_openrouter_key"

            # Embedding should fallback to LLM_PROVIDER
            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["provider"] == "openai"
            assert embedding_config["api_key"] == "decrypted_openai_key"

    @pytest.mark.asyncio
    async def test_provider_setting_operations(self):
        """Test setting active providers for different service types"""
        with patch.object(credential_service, "set_credential") as mock_set:
            mock_set.return_value = True

            # Test setting chat provider
            result = await credential_service.set_active_provider("openrouter", "llm")
            assert result is True
            mock_set.assert_called_with(
                "CHAT_PROVIDER",
                "openrouter",
                category="rag_strategy",
                description="Active chat/LLM provider: openrouter"
            )

            # Test setting embedding provider
            result = await credential_service.set_active_provider("huggingface", "embedding")
            assert result is True
            mock_set.assert_called_with(
                "EMBEDDING_PROVIDER",
                "huggingface",
                category="rag_strategy",
                description="Active embedding provider: huggingface"
            )

    @pytest.mark.asyncio
    async def test_error_handling_missing_api_keys(self):
        """Test error handling when required API keys are missing"""
        credential_service._cache = {
            "CHAT_PROVIDER": "openrouter",
            "EMBEDDING_PROVIDER": "huggingface",
            # Missing API keys
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:
            mock_get_creds.return_value = credential_service._cache

            # Should handle missing API keys gracefully
            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["provider"] == "openrouter"
            assert chat_config["api_key"] is None

            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["provider"] == "huggingface"
            assert embedding_config["api_key"] is None

    @pytest.mark.asyncio
    async def test_custom_base_urls_override_defaults(self):
        """Test that custom base URLs override provider defaults"""
        credential_service._cache = {
            "CHAT_PROVIDER": "ollama",
            "EMBEDDING_PROVIDER": "local",
            "CHAT_BASE_URL": "http://custom-ollama:11434/v1",
            "EMBEDDING_BASE_URL": "http://custom-embedding:9000",
        }
        credential_service._cache_initialized = True

        with patch.object(credential_service, "get_credentials_by_category") as mock_get_creds:
            mock_get_creds.return_value = credential_service._cache

            chat_config = await credential_service.get_active_provider("llm")
            assert chat_config["base_url"] == "http://custom-ollama:11434/v1"

            embedding_config = await credential_service.get_active_provider("embedding")
            assert embedding_config["base_url"] == "http://custom-embedding:9000"
