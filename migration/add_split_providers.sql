-- =====================================================
-- Archon Split Provider Migration
-- =====================================================
-- This migration adds support for separate chat and embedding providers
-- while maintaining backward compatibility with existing LLM_PROVIDER
-- 
-- Features added:
-- - Separate CHAT_PROVIDER and EMBEDDING_PROVIDER configuration
-- - Service-specific base URLs (CHAT_BASE_URL, EMBEDDING_BASE_URL)
-- - New provider support (Hugging Face, Local servers)
-- - Backward compatibility with existing LLM_PROVIDER
-- =====================================================

-- =====================================================
-- SECTION 1: ADD NEW PROVIDER CONFIGURATION FIELDS
-- =====================================================

-- Add separate chat and embedding provider settings
-- These will default to the existing LLM_PROVIDER value for backward compatibility
INSERT INTO archon_settings (key, value, is_encrypted, category, description) VALUES
('CHAT_PROVIDER', NULL, false, 'rag_strategy', 'Chat/LLM provider: openai, google, openrouter, ollama, huggingface, local'),
('EMBEDDING_PROVIDER', NULL, false, 'rag_strategy', 'Embedding provider: openai, google, ollama, huggingface, local'),
('CHAT_BASE_URL', NULL, false, 'rag_strategy', 'Custom base URL for chat provider (overrides provider defaults)'),
('EMBEDDING_BASE_URL', NULL, false, 'rag_strategy', 'Custom base URL for embedding provider (overrides provider defaults)')
ON CONFLICT (key) DO NOTHING;

-- =====================================================
-- SECTION 2: ADD NEW API KEYS FOR ADDITIONAL PROVIDERS
-- =====================================================

-- Add API keys for new providers
INSERT INTO archon_settings (key, encrypted_value, is_encrypted, category, description) VALUES
('HUGGINGFACE_API_KEY', NULL, true, 'api_keys', 'Hugging Face API Key for embedding models. Get from: https://huggingface.co/settings/tokens'),
('LOCAL_EMBEDDING_API_KEY', NULL, true, 'api_keys', 'API Key for local embedding server (if authentication required)')
ON CONFLICT (key) DO NOTHING;

-- =====================================================
-- SECTION 3: BACKWARD COMPATIBILITY SETUP
-- =====================================================

-- Set default values for new provider fields based on existing LLM_PROVIDER
-- This ensures existing installations continue working without configuration changes
DO $$
DECLARE
    current_llm_provider TEXT;
    current_llm_base_url TEXT;
BEGIN
    -- Get current LLM_PROVIDER value
    SELECT value INTO current_llm_provider 
    FROM archon_settings 
    WHERE key = 'LLM_PROVIDER';
    
    -- Get current LLM_BASE_URL value
    SELECT value INTO current_llm_base_url 
    FROM archon_settings 
    WHERE key = 'LLM_BASE_URL';
    
    -- Set CHAT_PROVIDER to current LLM_PROVIDER if not already set
    UPDATE archon_settings 
    SET value = COALESCE(current_llm_provider, 'openai')
    WHERE key = 'CHAT_PROVIDER' AND value IS NULL;
    
    -- Set EMBEDDING_PROVIDER to current LLM_PROVIDER if not already set
    UPDATE archon_settings 
    SET value = COALESCE(current_llm_provider, 'openai')
    WHERE key = 'EMBEDDING_PROVIDER' AND value IS NULL;
    
    -- Set base URLs if they exist and new fields are empty
    IF current_llm_base_url IS NOT NULL THEN
        UPDATE archon_settings 
        SET value = current_llm_base_url
        WHERE key = 'CHAT_BASE_URL' AND value IS NULL;
        
        UPDATE archon_settings 
        SET value = current_llm_base_url
        WHERE key = 'EMBEDDING_BASE_URL' AND value IS NULL;
    END IF;
    
    RAISE NOTICE 'Split provider migration completed. Chat Provider: %, Embedding Provider: %', 
                 COALESCE(current_llm_provider, 'openai'), 
                 COALESCE(current_llm_provider, 'openai');
END $$;

-- =====================================================
-- SECTION 4: ADD MIGRATION METADATA
-- =====================================================

-- Add migration tracking (optional - for future migration management)
INSERT INTO archon_settings (key, value, is_encrypted, category, description) VALUES
('MIGRATION_SPLIT_PROVIDERS', 'completed', false, 'system', 'Tracks completion of split provider migration')
ON CONFLICT (key) DO UPDATE SET value = 'completed', updated_at = NOW();

-- Update table comment to reflect new capabilities
COMMENT ON TABLE archon_settings IS 'Stores application configuration including API keys, RAG settings, split provider configuration, and code extraction parameters';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- 
-- After running this migration:
-- 1. Existing installations will continue working with current provider settings
-- 2. New CHAT_PROVIDER and EMBEDDING_PROVIDER fields will be available
-- 3. Users can configure different providers for chat vs embedding via UI
-- 4. Backward compatibility is maintained with LLM_PROVIDER fallback
-- 
-- Next steps:
-- 1. Update credential_service.py to use new provider fields
-- 2. Update llm_provider_service.py to support new providers
-- 3. Update UI to show separate provider selection
-- =====================================================
