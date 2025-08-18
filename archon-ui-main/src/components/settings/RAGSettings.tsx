import React, { useState } from 'react';
import { Settings, Check, Save, Loader, ChevronDown, ChevronUp, Zap, Database, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { Card } from '../ui/Card';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';
import { useToast } from '../../contexts/ToastContext';
import { credentialsService, ProviderTestResult } from '../../services/credentialsService';

interface RAGSettingsProps {
  ragSettings: {
    MODEL_CHOICE: string;
    USE_CONTEXTUAL_EMBEDDINGS: boolean;
    CONTEXTUAL_EMBEDDINGS_MAX_WORKERS: number;
    USE_HYBRID_SEARCH: boolean;
    USE_AGENTIC_RAG: boolean;
    USE_RERANKING: boolean;
    LLM_PROVIDER?: string;
    LLM_BASE_URL?: string;
    EMBEDDING_MODEL?: string;
    // Split Provider Configuration
    CHAT_PROVIDER?: string;
    EMBEDDING_PROVIDER?: string;
    CHAT_BASE_URL?: string;
    EMBEDDING_BASE_URL?: string;
    // Fallback Provider Configuration
    EMBEDDING_FALLBACK_PROVIDERS?: string;
    CHAT_FALLBACK_PROVIDERS?: string;
    ENABLE_PROVIDER_FALLBACK?: boolean;
    PROVIDER_HEALTH_CHECK_INTERVAL?: number;
    PROVIDER_FAILURE_THRESHOLD?: number;
    PROVIDER_COOLDOWN_PERIOD?: number;
    // Crawling Performance Settings
    CRAWL_BATCH_SIZE?: number;
    CRAWL_MAX_CONCURRENT?: number;
    CRAWL_WAIT_STRATEGY?: string;
    CRAWL_PAGE_TIMEOUT?: number;
    CRAWL_DELAY_BEFORE_HTML?: number;
    // Storage Performance Settings
    DOCUMENT_STORAGE_BATCH_SIZE?: number;
    EMBEDDING_BATCH_SIZE?: number;
    DELETE_BATCH_SIZE?: number;
    ENABLE_PARALLEL_BATCHES?: boolean;
    // Advanced Settings
    MEMORY_THRESHOLD_PERCENT?: number;
    DISPATCHER_CHECK_INTERVAL?: number;
    CODE_EXTRACTION_BATCH_SIZE?: number;
    CODE_SUMMARY_MAX_WORKERS?: number;
  };
  setRagSettings: (settings: any) => void;
}

export const RAGSettings = ({
  ragSettings,
  setRagSettings
}: RAGSettingsProps) => {
  const [saving, setSaving] = useState(false);
  const [showCrawlingSettings, setShowCrawlingSettings] = useState(false);
  const [showStorageSettings, setShowStorageSettings] = useState(false);
  const { showToast } = useToast();

  // Provider validation state
  const [chatProviderStatus, setChatProviderStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [embeddingProviderStatus, setEmbeddingProviderStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [chatProviderError, setChatProviderError] = useState<string>('');
  const [embeddingProviderError, setEmbeddingProviderError] = useState<string>('');

  // Provider validation functions
  const testChatProvider = async () => {
    const provider = getChatProvider(ragSettings);
    const baseUrl = ragSettings.CHAT_BASE_URL;
    const model = ragSettings.MODEL_CHOICE;

    setChatProviderStatus('testing');
    setChatProviderError('');

    try {
      const result = await credentialsService.testChatProvider(provider, undefined, baseUrl, model);
      if (result.success) {
        setChatProviderStatus('success');
        showToast('Chat provider connection successful!', 'success');
      } else {
        setChatProviderStatus('error');
        setChatProviderError(result.error || result.message);
        showToast(`Chat provider test failed: ${result.message}`, 'error');
      }
    } catch (error) {
      setChatProviderStatus('error');
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      setChatProviderError(errorMsg);
      showToast(`Chat provider test failed: ${errorMsg}`, 'error');
    }
  };

  const testEmbeddingProvider = async () => {
    const provider = getEmbeddingProvider(ragSettings);
    const baseUrl = ragSettings.EMBEDDING_BASE_URL;
    const model = ragSettings.EMBEDDING_MODEL;

    setEmbeddingProviderStatus('testing');
    setEmbeddingProviderError('');

    try {
      const result = await credentialsService.testEmbeddingProvider(provider, undefined, baseUrl, model);
      if (result.success) {
        setEmbeddingProviderStatus('success');
        showToast('Embedding provider connection successful!', 'success');
      } else {
        setEmbeddingProviderStatus('error');
        setEmbeddingProviderError(result.error || result.message);
        showToast(`Embedding provider test failed: ${result.message}`, 'error');
      }
    } catch (error) {
      setEmbeddingProviderStatus('error');
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      setEmbeddingProviderError(errorMsg);
      showToast(`Embedding provider test failed: ${errorMsg}`, 'error');
    }
  };

  // Validation status component
  const ValidationStatus = ({
    status,
    error,
    onTest
  }: {
    status: 'idle' | 'testing' | 'success' | 'error';
    error: string;
    onTest: () => void;
  }) => {
    const getIcon = () => {
      switch (status) {
        case 'testing':
          return <Loader className="w-4 h-4 animate-spin text-blue-500" />;
        case 'success':
          return <CheckCircle className="w-4 h-4 text-green-500" />;
        case 'error':
          return <XCircle className="w-4 h-4 text-red-500" />;
        default:
          return <AlertCircle className="w-4 h-4 text-gray-400" />;
      }
    };

    const getTooltip = () => {
      switch (status) {
        case 'testing':
          return 'Testing provider connection...';
        case 'success':
          return 'Provider connection successful';
        case 'error':
          return `Connection failed: ${error}`;
        default:
          return 'Click to test provider connection';
      }
    };

    return (
      <button
        onClick={onTest}
        disabled={status === 'testing'}
        className="ml-2 p-1 rounded hover:bg-gray-100 dark:hover:bg-zinc-700 transition-colors"
        title={getTooltip()}
      >
        {getIcon()}
      </button>
    );
  };

  return (
    <Card accentColor="green" className="overflow-hidden p-8">
        {/* Description */}
        <p className="text-sm text-gray-600 dark:text-zinc-400 mb-6">
          Configure Retrieval-Augmented Generation (RAG) strategies for optimal
          knowledge retrieval.
        </p>
        
        {/* Split Provider Selection Row */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <div className="flex items-center">
              <div className="flex-1">
                <Select
                  label="Chat Provider"
                  value={ragSettings.CHAT_PROVIDER || ragSettings.LLM_PROVIDER || 'openrouter'}
                  onChange={e => {
                    setRagSettings({
                      ...ragSettings,
                      CHAT_PROVIDER: e.target.value
                    });
                    // Reset validation status when provider changes
                    setChatProviderStatus('idle');
                    setChatProviderError('');
                  }}
                  accentColor="green"
                  options={[
                    { value: 'openai', label: 'OpenAI' },
                    { value: 'google', label: 'Google Gemini' },
                    { value: 'openrouter', label: 'OpenRouter' },
                    { value: 'ollama', label: 'Ollama' },
                  ]}
                />
              </div>
              <ValidationStatus
                status={chatProviderStatus}
                error={chatProviderError}
                onTest={testChatProvider}
              />
            </div>
          </div>
          <div>
            <div className="flex items-center">
              <div className="flex-1">
                <Select
                  label="Embedding Provider"
                  value={ragSettings.EMBEDDING_PROVIDER || ragSettings.LLM_PROVIDER || 'openai'}
                  onChange={e => {
                    setRagSettings({
                      ...ragSettings,
                      EMBEDDING_PROVIDER: e.target.value
                    });
                    // Reset validation status when provider changes
                    setEmbeddingProviderStatus('idle');
                    setEmbeddingProviderError('');
                  }}
                  accentColor="green"
                  options={[
                    { value: 'openai', label: 'OpenAI' },
                    { value: 'google', label: 'Google Gemini' },
                    { value: 'ollama', label: 'Ollama' },
                    { value: 'huggingface', label: 'Hugging Face' },
                    { value: 'tei', label: 'TEI (Text Embeddings Inference)' },
                    { value: 'local', label: 'Local Server' },
                  ]}
                />
              </div>
              <ValidationStatus
                status={embeddingProviderStatus}
                error={embeddingProviderError}
                onTest={testEmbeddingProvider}
              />
            </div>
          </div>
        </div>

        {/* Base URL Configuration Row */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            {/* Chat Provider Base URL */}
            {getChatProvider(ragSettings) && shouldShowBaseUrl(getChatProvider(ragSettings)) && (
              <Input
                label={`${getChatProvider(ragSettings)} Chat Base URL`}
                value={ragSettings.CHAT_BASE_URL || getDefaultBaseUrl(getChatProvider(ragSettings))}
                onChange={e => setRagSettings({
                  ...ragSettings,
                  CHAT_BASE_URL: e.target.value
                })}
                placeholder={getDefaultBaseUrl(getChatProvider(ragSettings))}
                accentColor="green"
              />
            )}
          </div>
          <div>
            {/* Embedding Provider Base URL */}
            {getEmbeddingProvider(ragSettings) && shouldShowBaseUrl(getEmbeddingProvider(ragSettings)) && (
              <Input
                label={`${getEmbeddingProvider(ragSettings)} Embedding Base URL`}
                value={ragSettings.EMBEDDING_BASE_URL || getDefaultBaseUrl(getEmbeddingProvider(ragSettings))}
                onChange={e => setRagSettings({
                  ...ragSettings,
                  EMBEDDING_BASE_URL: e.target.value
                })}
                placeholder={getDefaultBaseUrl(getEmbeddingProvider(ragSettings))}
                accentColor="green"
              />
            )}
          </div>
        </div>

        {/* Fallback Provider Configuration */}
        <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-5 h-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Provider Fallback Configuration
            </h3>
          </div>

          {/* Enable Fallback Toggle */}
          <div className="mb-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={ragSettings.ENABLE_PROVIDER_FALLBACK === true}
                onChange={e => setRagSettings({
                  ...ragSettings,
                  ENABLE_PROVIDER_FALLBACK: e.target.checked
                })}
                className="w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500 dark:focus:ring-green-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <span className="text-sm font-medium text-gray-900 dark:text-gray-300">
                Enable automatic provider fallback
              </span>
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Automatically switch to backup providers when primary provider fails
            </p>
          </div>

          {ragSettings.ENABLE_PROVIDER_FALLBACK === true && (
            <>
              {/* Fallback Provider Lists */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <Input
                    label="Embedding Fallback Providers"
                    value={ragSettings.EMBEDDING_FALLBACK_PROVIDERS || 'openai,ollama,local'}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      EMBEDDING_FALLBACK_PROVIDERS: e.target.value
                    })}
                    placeholder="openai,ollama,local"
                    accentColor="yellow"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Comma-separated list in priority order
                  </p>
                </div>
                <div>
                  <Input
                    label="Chat Fallback Providers"
                    value={ragSettings.CHAT_FALLBACK_PROVIDERS || 'openai,google,ollama'}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      CHAT_FALLBACK_PROVIDERS: e.target.value
                    })}
                    placeholder="openai,google,ollama"
                    accentColor="yellow"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Comma-separated list in priority order
                  </p>
                </div>
              </div>

              {/* Advanced Fallback Settings */}
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Input
                    label="Failure Threshold"
                    type="number"
                    value={ragSettings.PROVIDER_FAILURE_THRESHOLD || 3}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      PROVIDER_FAILURE_THRESHOLD: parseInt(e.target.value) || 3
                    })}
                    placeholder="3"
                    accentColor="yellow"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Failures before marking unhealthy
                  </p>
                </div>
                <div>
                  <Input
                    label="Cooldown Period (seconds)"
                    type="number"
                    value={ragSettings.PROVIDER_COOLDOWN_PERIOD || 300}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      PROVIDER_COOLDOWN_PERIOD: parseInt(e.target.value) || 300
                    })}
                    placeholder="300"
                    accentColor="yellow"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Wait time before retrying failed provider
                  </p>
                </div>
                <div>
                  <Input
                    label="Health Check Interval (seconds)"
                    type="number"
                    value={ragSettings.PROVIDER_HEALTH_CHECK_INTERVAL || 300}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      PROVIDER_HEALTH_CHECK_INTERVAL: parseInt(e.target.value) || 300
                    })}
                    placeholder="300"
                    accentColor="yellow"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Interval between health checks
                  </p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Save Button Row */}
        <div className="flex justify-end mb-4">
          <Button
            variant="outline"
            accentColor="green"
            icon={saving ? <Loader className="w-4 h-4 mr-1 animate-spin" /> : <Save className="w-4 h-4 mr-1" />}
            className="whitespace-nowrap"
            size="md"
            onClick={async () => {
              try {
                setSaving(true);
                await credentialsService.updateRagSettings(ragSettings);
                showToast('RAG settings saved successfully!', 'success');
              } catch (err) {
                console.error('Failed to save RAG settings:', err);
                showToast('Failed to save settings', 'error');
              } finally {
                setSaving(false);
              }
            }}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </div>

        {/* Model Settings Row */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <Input
              label="Chat Model"
              value={ragSettings.MODEL_CHOICE}
              onChange={e => setRagSettings({
                ...ragSettings,
                MODEL_CHOICE: e.target.value
              })}
              placeholder={getModelPlaceholder(getChatProvider(ragSettings))}
              accentColor="green"
            />
          </div>
          <div>
            <Input
              label="Embedding Model"
              value={ragSettings.EMBEDDING_MODEL || ''}
              onChange={e => setRagSettings({
                ...ragSettings,
                EMBEDDING_MODEL: e.target.value
              })}
              placeholder={getEmbeddingPlaceholder(getEmbeddingProvider(ragSettings))}
              accentColor="green"
            />
          </div>
        </div>
        
        {/* Second row: Contextual Embeddings, Max Workers, and description */}
        <div className="grid grid-cols-8 gap-4 mb-4 p-4 rounded-lg border border-green-500/20 shadow-[0_2px_8px_rgba(34,197,94,0.1)]">
          <div className="col-span-4">
            <CustomCheckbox 
              id="contextualEmbeddings" 
              checked={ragSettings.USE_CONTEXTUAL_EMBEDDINGS} 
              onChange={e => setRagSettings({
                ...ragSettings,
                USE_CONTEXTUAL_EMBEDDINGS: e.target.checked
              })} 
              label="Use Contextual Embeddings" 
              description="Enhances embeddings with contextual information for better retrieval" 
            />
          </div>
                      <div className="col-span-1">
              {ragSettings.USE_CONTEXTUAL_EMBEDDINGS && (
                <div className="flex flex-col items-center">
                  <div className="relative ml-2 mr-6">
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={ragSettings.CONTEXTUAL_EMBEDDINGS_MAX_WORKERS}
                      onChange={e => setRagSettings({
                        ...ragSettings,
                        CONTEXTUAL_EMBEDDINGS_MAX_WORKERS: parseInt(e.target.value, 10) || 3
                      })}
                      className="w-14 h-10 pl-1 pr-7 text-center font-medium rounded-md 
                        bg-gradient-to-b from-gray-100 to-gray-200 dark:from-gray-900 dark:to-black 
                        border border-green-500/30 
                        text-gray-900 dark:text-white
                        focus:border-green-500 focus:shadow-[0_0_15px_rgba(34,197,94,0.4)]
                        transition-all duration-200
                        [appearance:textfield] 
                        [&::-webkit-outer-spin-button]:appearance-none 
                        [&::-webkit-inner-spin-button]:appearance-none"
                    />
                    <div className="absolute right-1 top-1 bottom-1 flex flex-col">
                      <button
                        type="button"
                        onClick={() => setRagSettings({
                          ...ragSettings,
                          CONTEXTUAL_EMBEDDINGS_MAX_WORKERS: Math.min(ragSettings.CONTEXTUAL_EMBEDDINGS_MAX_WORKERS + 1, 10)
                        })}
                        className="flex-1 px-1 rounded-t-sm 
                          bg-gradient-to-b from-green-500/20 to-green-600/10
                          hover:from-green-500/30 hover:to-green-600/20
                          border border-green-500/30 border-b-0
                          transition-all duration-200 group"
                      >
                        <svg className="w-2.5 h-2.5 text-green-500 group-hover:filter group-hover:drop-shadow-[0_0_4px_rgba(34,197,94,0.8)]" 
                          viewBox="0 0 10 6" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M1 5L5 1L9 5" />
                        </svg>
                      </button>
                      <button
                        type="button"
                        onClick={() => setRagSettings({
                          ...ragSettings,
                          CONTEXTUAL_EMBEDDINGS_MAX_WORKERS: Math.max(ragSettings.CONTEXTUAL_EMBEDDINGS_MAX_WORKERS - 1, 1)
                        })}
                        className="flex-1 px-1 rounded-b-sm 
                          bg-gradient-to-b from-green-500/20 to-green-600/10
                          hover:from-green-500/30 hover:to-green-600/20
                          border border-green-500/30 border-t-0
                          transition-all duration-200 group"
                      >
                        <svg className="w-2.5 h-2.5 text-green-500 group-hover:filter group-hover:drop-shadow-[0_0_4px_rgba(34,197,94,0.8)]" 
                          viewBox="0 0 10 6" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M1 1L5 5L9 1" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  <label className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Max
                  </label>
                </div>
              )}
            </div>
          <div className="col-span-3">
            {ragSettings.USE_CONTEXTUAL_EMBEDDINGS && (
              <p className="text-xs text-green-900 dark:text-blue-600 mt-2">
                Controls parallel processing for embeddings (1-10)
              </p>
            )}
          </div>
        </div>
        
        {/* Third row: Hybrid Search and Agentic RAG */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <CustomCheckbox 
              id="hybridSearch" 
              checked={ragSettings.USE_HYBRID_SEARCH} 
              onChange={e => setRagSettings({
                ...ragSettings,
                USE_HYBRID_SEARCH: e.target.checked
              })} 
              label="Use Hybrid Search" 
              description="Combines vector similarity search with keyword search for better results" 
            />
          </div>
          <div>
            <CustomCheckbox 
              id="agenticRag" 
              checked={ragSettings.USE_AGENTIC_RAG} 
              onChange={e => setRagSettings({
                ...ragSettings,
                USE_AGENTIC_RAG: e.target.checked
              })} 
              label="Use Agentic RAG" 
              description="Enables code extraction and specialized search for technical content" 
            />
          </div>
        </div>
        
        {/* Fourth row: Use Reranking */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <CustomCheckbox 
              id="reranking" 
              checked={ragSettings.USE_RERANKING} 
              onChange={e => setRagSettings({
                ...ragSettings,
                USE_RERANKING: e.target.checked
              })} 
              label="Use Reranking" 
              description="Applies cross-encoder reranking to improve search result relevance" 
            />
          </div>
          <div>{/* Empty column */}</div>
        </div>

        {/* Crawling Performance Settings */}
        <div className="mt-6">
          <div
            className="flex items-center justify-between cursor-pointer p-3 rounded-lg border border-green-500/20 bg-gradient-to-r from-green-500/5 to-green-600/5 hover:from-green-500/10 hover:to-green-600/10 transition-all duration-200"
            onClick={() => setShowCrawlingSettings(!showCrawlingSettings)}
          >
            <div className="flex items-center">
              <Zap className="mr-2 text-green-500 filter drop-shadow-[0_0_8px_rgba(34,197,94,0.6)]" size={18} />
              <h3 className="font-semibold text-gray-800 dark:text-white">Crawling Performance Settings</h3>
            </div>
            {showCrawlingSettings ? (
              <ChevronUp className="text-gray-500 dark:text-gray-400" size={20} />
            ) : (
              <ChevronDown className="text-gray-500 dark:text-gray-400" size={20} />
            )}
          </div>
          
          {showCrawlingSettings && (
            <div className="mt-4 p-4 border border-green-500/10 rounded-lg bg-green-500/5">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Batch Size
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="100"
                    value={ragSettings.CRAWL_BATCH_SIZE || 50}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      CRAWL_BATCH_SIZE: parseInt(e.target.value, 10) || 50
                    })}
                    className="w-full px-3 py-2 border border-green-500/30 rounded-md bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:border-green-500 focus:ring-1 focus:ring-green-500"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">URLs to crawl in parallel (10-100)</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Max Concurrent
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={ragSettings.CRAWL_MAX_CONCURRENT || 10}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      CRAWL_MAX_CONCURRENT: parseInt(e.target.value, 10) || 10
                    })}
                    className="w-full px-3 py-2 border border-green-500/30 rounded-md bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:border-green-500 focus:ring-1 focus:ring-green-500"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Browser sessions (1-20)</p>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div>
                  <Select
                    label="Wait Strategy"
                    value={ragSettings.CRAWL_WAIT_STRATEGY || 'domcontentloaded'}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      CRAWL_WAIT_STRATEGY: e.target.value
                    })}
                    accentColor="green"
                    options={[
                      { value: 'domcontentloaded', label: 'DOM Loaded (Fast)' },
                      { value: 'networkidle', label: 'Network Idle (Thorough)' },
                      { value: 'load', label: 'Full Load (Slowest)' }
                    ]}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Page Timeout (sec)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="120"
                    value={(ragSettings.CRAWL_PAGE_TIMEOUT || 60000) / 1000}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      CRAWL_PAGE_TIMEOUT: (parseInt(e.target.value, 10) || 60) * 1000
                    })}
                    className="w-full px-3 py-2 border border-green-500/30 rounded-md bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:border-green-500 focus:ring-1 focus:ring-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Render Delay (sec)
                  </label>
                  <input
                    type="number"
                    min="0.1"
                    max="5"
                    step="0.1"
                    value={ragSettings.CRAWL_DELAY_BEFORE_HTML || 0.5}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      CRAWL_DELAY_BEFORE_HTML: parseFloat(e.target.value) || 0.5
                    })}
                    className="w-full px-3 py-2 border border-green-500/30 rounded-md bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:border-green-500 focus:ring-1 focus:ring-green-500"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Storage Performance Settings */}
        <div className="mt-4">
          <div
            className="flex items-center justify-between cursor-pointer p-3 rounded-lg border border-green-500/20 bg-gradient-to-r from-green-500/5 to-green-600/5 hover:from-green-500/10 hover:to-green-600/10 transition-all duration-200"
            onClick={() => setShowStorageSettings(!showStorageSettings)}
          >
            <div className="flex items-center">
              <Database className="mr-2 text-green-500 filter drop-shadow-[0_0_8px_rgba(34,197,94,0.6)]" size={18} />
              <h3 className="font-semibold text-gray-800 dark:text-white">Storage Performance Settings</h3>
            </div>
            {showStorageSettings ? (
              <ChevronUp className="text-gray-500 dark:text-gray-400" size={20} />
            ) : (
              <ChevronDown className="text-gray-500 dark:text-gray-400" size={20} />
            )}
          </div>
          
          {showStorageSettings && (
            <div className="mt-4 p-4 border border-green-500/10 rounded-lg bg-green-500/5">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Document Batch Size
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="100"
                    value={ragSettings.DOCUMENT_STORAGE_BATCH_SIZE || 50}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      DOCUMENT_STORAGE_BATCH_SIZE: parseInt(e.target.value, 10) || 50
                    })}
                    className="w-full px-3 py-2 border border-green-500/30 rounded-md bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:border-green-500 focus:ring-1 focus:ring-green-500"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Chunks per batch (10-100)</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Embedding Batch Size
                  </label>
                  <input
                    type="number"
                    min="20"
                    max="200"
                    value={ragSettings.EMBEDDING_BATCH_SIZE || 100}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      EMBEDDING_BATCH_SIZE: parseInt(e.target.value, 10) || 100
                    })}
                    className="w-full px-3 py-2 border border-green-500/30 rounded-md bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:border-green-500 focus:ring-1 focus:ring-green-500"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Per API call (20-200)</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Code Extraction Workers
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={ragSettings.CODE_SUMMARY_MAX_WORKERS || 3}
                    onChange={e => setRagSettings({
                      ...ragSettings,
                      CODE_SUMMARY_MAX_WORKERS: parseInt(e.target.value, 10) || 3
                    })}
                    className="w-full px-3 py-2 border border-green-500/30 rounded-md bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:border-green-500 focus:ring-1 focus:ring-green-500"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Parallel workers (1-10)</p>
                </div>
              </div>
              
              <div className="mt-4 flex items-center">
                <CustomCheckbox
                  id="parallelBatches"
                  checked={ragSettings.ENABLE_PARALLEL_BATCHES !== false}
                  onChange={e => setRagSettings({
                    ...ragSettings,
                    ENABLE_PARALLEL_BATCHES: e.target.checked
                  })}
                  label="Enable Parallel Processing"
                  description="Process multiple document batches simultaneously for faster storage"
                />
              </div>
            </div>
          )}
        </div>
    </Card>
  );
};

// Helper functions for split provider support
function getChatProvider(ragSettings: any): string {
  return ragSettings.CHAT_PROVIDER || ragSettings.LLM_PROVIDER || 'openrouter';
}

function getEmbeddingProvider(ragSettings: any): string {
  return ragSettings.EMBEDDING_PROVIDER || ragSettings.LLM_PROVIDER || 'openai';
}

function shouldShowBaseUrl(provider: string): boolean {
  return ['ollama', 'openrouter', 'huggingface', 'tei', 'local'].includes(provider);
}

function getDefaultBaseUrl(provider: string): string {
  switch (provider) {
    case 'ollama':
      return 'http://localhost:11434/v1';
    case 'openrouter':
      return 'https://openrouter.ai/api/v1';
    case 'huggingface':
      return 'https://api-inference.huggingface.co/models';
    case 'local':
      return 'http://localhost:8080';
    case 'tei':
      return 'http://archon-embeddings:80';
    default:
      return '';
  }
}

// Helper functions for model placeholders
function getModelPlaceholder(provider: string): string {
  switch (provider) {
    case 'openai':
      return 'e.g., gpt-4o-mini';
    case 'openrouter':
      return 'e.g., anthropic/claude-3.5-sonnet, deepseek/deepseek-chat';
    case 'ollama':
      return 'e.g., llama2, mistral';
    case 'google':
      return 'e.g., gemini-1.5-flash';
    case 'huggingface':
      return 'e.g., microsoft/DialoGPT-medium';
    case 'local':
      return 'e.g., custom-model-name';
    default:
      return 'e.g., gpt-4o-mini';
  }
}

function getEmbeddingPlaceholder(provider: string): string {
  switch (provider) {
    case 'openai':
      return 'Default: text-embedding-3-small';
    case 'openrouter':
      return 'e.g., text-embedding-3-small (via OpenAI)';
    case 'ollama':
      return 'e.g., nomic-embed-text';
    case 'google':
      return 'e.g., text-embedding-004';
    case 'huggingface':
      return 'Default: sentence-transformers/all-MiniLM-L6-v2';
    case 'local':
      return 'Default: all-MiniLM-L6-v2';
    case 'tei':
      return 'Default: sentence-transformers/all-MiniLM-L6-v2';
    default:
      return 'Default: text-embedding-3-small';
  }
}

interface CustomCheckboxProps {
  id: string;
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  label: string;
  description: string;
}

const CustomCheckbox = ({
  id,
  checked,
  onChange,
  label,
  description
}: CustomCheckboxProps) => {
  return (
    <div className="flex items-start group">
      <div className="relative flex items-center h-5 mt-1">
        <input 
          type="checkbox" 
          id={id} 
          checked={checked} 
          onChange={onChange} 
          className="sr-only peer" 
        />
        <label 
          htmlFor={id}
          className="relative w-5 h-5 rounded-md transition-all duration-200 cursor-pointer
            bg-gradient-to-b from-white/80 to-white/60 dark:from-white/5 dark:to-black/40
            border border-gray-300 dark:border-gray-700
            peer-checked:border-green-500 dark:peer-checked:border-green-500/50
            peer-checked:bg-gradient-to-b peer-checked:from-green-500/20 peer-checked:to-green-600/20
            group-hover:border-green-500/50 dark:group-hover:border-green-500/30
            peer-checked:shadow-[0_0_10px_rgba(34,197,94,0.2)] dark:peer-checked:shadow-[0_0_15px_rgba(34,197,94,0.3)]"
        >
          <Check className={`
              w-3.5 h-3.5 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
              transition-all duration-200 text-green-500 pointer-events-none
              ${checked ? 'opacity-100 scale-100' : 'opacity-0 scale-50'}
            `} />
        </label>
      </div>
      <div className="ml-3 flex-1">
        <label htmlFor={id} className="text-gray-700 dark:text-zinc-300 font-medium cursor-pointer block text-sm">
          {label}
        </label>
        <p className="text-xs text-gray-600 dark:text-zinc-400 mt-0.5 leading-tight">
          {description}
        </p>
      </div>
    </div>
  );
};