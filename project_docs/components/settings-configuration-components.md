# Settings & Configuration Components Documentation

**File Path:** `archon-ui-main/src/components/settings/` directory
**Last Updated:** 2025-08-23

## Purpose
Comprehensive documentation of the settings and configuration system components that manage application configuration, API keys, feature toggles, testing infrastructure, and development tools. These components provide the administrative interface for system configuration and maintenance.

## Core Settings Components

### 1. APIKeysSection
**File:** `APIKeysSection.tsx`
**Purpose:** Secure management of API keys and credentials with encryption support

**Key Features:**
- **Credential Management:** Add, edit, delete API keys and credentials
- **Encryption Support:** Automatic encryption for sensitive values
- **Visibility Toggle:** Show/hide credential values for security
- **Change Tracking:** Track unsaved changes with visual indicators
- **Validation:** Key format validation and duplicate prevention
- **Bulk Operations:** Save all changes at once

**Props Interface:**
```typescript
interface CustomCredential {
  key: string;
  value: string;
  description: string;
  originalValue?: string;
  originalKey?: string;
  hasChanges?: boolean;
  is_encrypted?: boolean;
  showValue?: boolean;
  isNew?: boolean;
}
```

**State Management:**
- `customCredentials` - Array of credential objects
- `loading` - Loading state for credential fetching
- `saving` - Saving state for batch operations
- `hasUnsavedChanges` - Tracks if there are pending changes

**Security Features:**
- **Automatic Encryption:** New credentials encrypted by default
- **Masked Display:** Values hidden by default with toggle option
- **Change Detection:** Visual indicators for modified credentials
- **Validation:** Prevents duplicate keys and invalid formats

### 2. RAGSettings
**File:** `RAGSettings.tsx`
**Purpose:** Configuration for Retrieval Augmented Generation system settings

**Key Features:**
- **Model Configuration:** LLM and embedding model selection
- **Provider Management:** Split provider configuration for chat and embeddings
- **Fallback Configuration:** Provider fallback and health monitoring
- **Performance Tuning:** Batch sizes and concurrency settings
- **Advanced Options:** Memory thresholds and optimization settings

**Settings Categories:**
```typescript
interface RAGSettingsProps {
  ragSettings: {
    // Core Settings
    MODEL_CHOICE: string;
    USE_CONTEXTUAL_EMBEDDINGS: boolean;
    CONTEXTUAL_EMBEDDINGS_MAX_WORKERS: number;
    USE_HYBRID_SEARCH: boolean;
    USE_AGENTIC_RAG: boolean;
    USE_RERANKING: boolean;
    
    // Provider Configuration
    LLM_PROVIDER?: string;
    LLM_BASE_URL?: string;
    EMBEDDING_MODEL?: string;
    CHAT_PROVIDER?: string;
    EMBEDDING_PROVIDER?: string;
    CHAT_BASE_URL?: string;
    EMBEDDING_BASE_URL?: string;
    
    // Fallback Configuration
    EMBEDDING_FALLBACK_PROVIDERS?: string;
    CHAT_FALLBACK_PROVIDERS?: string;
    ENABLE_PROVIDER_FALLBACK?: boolean;
    PROVIDER_HEALTH_CHECK_INTERVAL?: number;
    PROVIDER_FAILURE_THRESHOLD?: number;
    PROVIDER_COOLDOWN_PERIOD?: number;
    
    // Performance Settings
    CRAWL_BATCH_SIZE?: number;
    CRAWL_MAX_CONCURRENT?: number;
    CRAWL_WAIT_STRATEGY?: string;
    CRAWL_PAGE_TIMEOUT?: number;
    CRAWL_DELAY_BEFORE_HTML?: number;
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
```

### 3. CodeExtractionSettings
**File:** `CodeExtractionSettings.tsx`
**Purpose:** Configuration for code extraction and analysis parameters

**Key Features:**
- **Block Length Control:** Min/max code block length settings
- **Detection Algorithms:** Enable/disable various detection methods
- **Filtering Options:** Prose filtering and diagram detection
- **Performance Tuning:** Worker count and batch size configuration
- **Context Management:** Context window and summary settings

**Configuration Options:**
```typescript
interface CodeExtractionSettings {
  MIN_CODE_BLOCK_LENGTH: number;
  MAX_CODE_BLOCK_LENGTH: number;
  ENABLE_COMPLETE_BLOCK_DETECTION: boolean;
  ENABLE_LANGUAGE_SPECIFIC_PATTERNS: boolean;
  ENABLE_PROSE_FILTERING: boolean;
  MAX_PROSE_RATIO: number;
  MIN_CODE_INDICATORS: number;
  ENABLE_DIAGRAM_FILTERING: boolean;
  ENABLE_CONTEXTUAL_LENGTH: boolean;
  CODE_EXTRACTION_MAX_WORKERS: number;
  CONTEXT_WINDOW_SIZE: number;
  ENABLE_CODE_SUMMARIES: boolean;
}
```

**Validation Rules:**
- **Length Constraints:** Min: 50-1000, Max: 1000-10000
- **Ratio Limits:** Prose ratio: 0.0-1.0
- **Worker Limits:** 1-10 workers maximum
- **Context Window:** 100-5000 characters

### 4. FeaturesSection
**File:** `FeaturesSection.tsx`
**Purpose:** Feature flag management and system capability toggles

**Key Features:**
- **Feature Toggles:** Enable/disable major system features
- **Health Monitoring:** Check feature dependencies and status
- **Schema Validation:** Verify database schema for features
- **Permission Control:** Role-based feature access
- **Dependency Management:** Handle feature interdependencies

**Feature Categories:**
- **Logfire Integration:** Logging and monitoring features
- **Projects System:** Project management capabilities
- **Disconnect Screen:** Connection monitoring overlay
- **Advanced Features:** Experimental and beta features

**State Management:**
```typescript
const [logfireEnabled, setLogfireEnabled] = useState(false);
const [projectsEnabled, setProjectsEnabled] = useState(false);
const [projectsHealthy, setProjectsHealthy] = useState(false);
const [disconnectScreenEnabled, setDisconnectScreenEnabled] = useState(true);
const [loading, setLoading] = useState(true);
```

## Development & Testing Components

### 5. TestStatus
**File:** `TestStatus.tsx`
**Purpose:** Comprehensive testing interface with real-time execution monitoring

**Key Features:**
- **Multi-Test Support:** Python (MCP) and JavaScript (UI) test suites
- **Real-time Streaming:** Live test output via WebSocket
- **Result Visualization:** Pretty mode with test result summaries
- **Dashboard Integration:** Comprehensive test analytics dashboard
- **Error Tracking:** Detailed error logs and stack traces
- **Performance Metrics:** Test duration and performance tracking

**Test Execution State:**
```typescript
interface TestExecutionState {
  execution?: TestExecution;
  logs: string[];
  isRunning: boolean;
  duration?: number;
  exitCode?: number;
  results: TestResult[];
  summary?: {
    total: number;
    passed: number;
    failed: number;
    skipped: number;
  };
}
```

**Display Modes:**
- **Pretty Mode:** Formatted test results with visual indicators
- **Dashboard Mode:** Comprehensive analytics and metrics
- **Raw Logs:** Terminal-style output for debugging

### 6. ButtonPlayground
**File:** `ButtonPlayground.tsx`
**Purpose:** Interactive design tool for creating and testing UI button styles

**Key Features:**
- **Visual Editor:** Real-time button style customization
- **Layer System:** Multi-layer glassmorphism effects
- **Color Picker:** Advanced color selection with gradients
- **Border Controls:** Radius, width, and style customization
- **Glow Effects:** Configurable glow intensity and colors
- **CSS Export:** Generate CSS code for custom styles
- **Copy Functionality:** One-click CSS copying

**Customization Options:**
```typescript
interface ButtonCustomization {
  showLayer2: boolean;
  layer2Inset: number;
  layer1Color: ColorOption;
  layer2Color: ColorOption;
  layer1Border: number;
  layer2Border: number;
  layer1Radius: CornerRadius;
  layer2Radius: CornerRadius;
  layer1Glow: GlowIntensity;
  layer2Glow: GlowIntensity;
  borderGlow: GlowIntensity;
  coloredText: boolean;
}
```

### 7. IDEGlobalRules
**File:** `IDEGlobalRules.tsx`
**Purpose:** IDE integration rules and workflow guidelines for development

**Key Features:**
- **Rule Templates:** Pre-defined rule sets for different IDEs
- **Archon Integration:** Specific rules for Archon MCP server workflow
- **Copy Functionality:** Easy copying of rules to IDE settings
- **Rule Types:** Claude-specific and universal rule sets
- **Workflow Guidelines:** Step-by-step development workflows

**Rule Categories:**
- **Archon-First Rules:** Prioritize Archon MCP server usage
- **Task Management:** Task-driven development workflows
- **Project Initialization:** New project setup procedures
- **Code Quality:** Development best practices and standards

## System Management Components

### 8. BackupRestoreSection
**File:** `BackupRestoreSection.tsx`
**Purpose:** System backup and restore functionality with progress tracking

**Key Features:**
- **System Backup:** Complete system data backup creation
- **Project Import:** Individual project import functionality
- **Progress Tracking:** Real-time backup/restore progress
- **Validation:** Pre-operation validation and checks
- **Error Handling:** Comprehensive error reporting and recovery
- **Scheduling:** Future support for scheduled backups

**Backup Operations:**
```typescript
const handleCreateSystemBackup = async () => {
  setIsCreatingBackup(true);
  try {
    // Create comprehensive system backup
    const backup = await createSystemBackup();
    setLastBackupTime(new Date().toISOString());
    addToast('System backup created successfully', 'success');
  } catch (error) {
    addToast('Failed to create backup', 'error');
  } finally {
    setIsCreatingBackup(false);
  }
};
```

**Backup Contents:**
- **Projects:** All project data and metadata
- **Documents:** Document content and version history
- **Tasks:** Task data and relationships
- **Settings:** System configuration and credentials
- **Knowledge Base:** Crawled content and embeddings

## Configuration Patterns

### Settings Persistence
```typescript
// Credential-based settings
const saveSettings = async (settings: SettingsObject) => {
  await credentialsService.updateCredential(settingKey, settingValue);
  showToast('Settings saved successfully', 'success');
};

// Batch settings update
const saveBatchSettings = async (settingsMap: Record<string, any>) => {
  await Promise.all(
    Object.entries(settingsMap).map(([key, value]) =>
      credentialsService.updateCredential(key, value)
    )
  );
};
```

### Validation Patterns
```typescript
// Input validation with constraints
const validateNumericSetting = (
  value: number,
  min: number,
  max: number,
  fieldName: string
): boolean => {
  if (value < min || value > max) {
    showToast(`${fieldName} must be between ${min} and ${max}`, 'error');
    return false;
  }
  return true;
};

// Feature dependency validation
const validateFeatureDependencies = async (
  feature: string,
  enabled: boolean
): Promise<boolean> => {
  if (enabled) {
    const dependencies = await checkFeatureDependencies(feature);
    return dependencies.every(dep => dep.satisfied);
  }
  return true;
};
```

### State Synchronization
```typescript
// Real-time settings sync
useEffect(() => {
  const syncSettings = async () => {
    const currentSettings = await credentialsService.getAllCredentials();
    updateLocalState(currentSettings);
  };
  
  const interval = setInterval(syncSettings, 30000); // Sync every 30s
  return () => clearInterval(interval);
}, []);
```

## Integration Notes

### Service Dependencies
- **credentialsService:** Settings persistence and encryption
- **testService:** Test execution and monitoring
- **exportImportService:** Backup and restore operations
- **serverHealthService:** Feature health monitoring

### Security Considerations
- **Credential Encryption:** Automatic encryption for sensitive data
- **Access Control:** Role-based settings access
- **Audit Logging:** Track configuration changes
- **Validation:** Input sanitization and validation

### Performance Optimizations
- **Debounced Inputs:** Prevent excessive API calls
- **Batch Operations:** Group related settings updates
- **Lazy Loading:** Load settings on demand
- **Caching:** Cache frequently accessed settings
