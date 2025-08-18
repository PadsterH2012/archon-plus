-- Migration: Add Fallback Provider Configuration
-- Description: Add support for fallback provider configuration for embedding and chat services
-- Version: 2.1
-- Date: 2025-08-17

-- Add fallback provider configuration fields
INSERT INTO archon_settings (key, value, is_encrypted, category, description) VALUES
('EMBEDDING_FALLBACK_PROVIDERS', 'openai,ollama,tei,local', false, 'rag_strategy', 'Comma-separated list of fallback embedding providers in priority order'),
('CHAT_FALLBACK_PROVIDERS', 'openai,google,ollama', false, 'rag_strategy', 'Comma-separated list of fallback chat providers in priority order'),
('ENABLE_PROVIDER_FALLBACK', 'true', false, 'rag_strategy', 'Enable automatic fallback to alternative providers when primary fails'),
('PROVIDER_HEALTH_CHECK_INTERVAL', '300', false, 'rag_strategy', 'Interval in seconds between provider health checks'),
('PROVIDER_FAILURE_THRESHOLD', '3', false, 'rag_strategy', 'Number of consecutive failures before marking provider as unhealthy'),
('PROVIDER_COOLDOWN_PERIOD', '300', false, 'rag_strategy', 'Cooldown period in seconds before retrying unhealthy provider')
ON CONFLICT (key) DO NOTHING;

-- Update migration tracking
INSERT INTO archon_migrations (migration_name, applied_at) VALUES 
('add_fallback_providers', NOW())
ON CONFLICT (migration_name) DO NOTHING;
