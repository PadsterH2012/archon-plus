import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Database, 
  Server, 
  Zap, 
  HardDrive,
  CheckCircle, 
  AlertTriangle, 
  RefreshCw,
  Play,
  Pause,
  RotateCcw,
  Settings,
  Monitor,
  Wifi,
  WifiOff
} from 'lucide-react';
import { Button } from '../ui/Button';
import { useToast } from '../../contexts/ToastContext';

interface DatabaseConfig {
  postgresql: {
    host: string;
    port: number;
    database: string;
    username: string;
    password: string;
    ssl: boolean;
  };
  chromadb: {
    host: string;
    port: number;
    collection_prefix: string;
    embedding_model: string;
  };
  redis: {
    host: string;
    port: number;
    password?: string;
    database_mapping: {
      realtime: number;
      cache: number;
      sessions: number;
      tasks: number;
    };
  };
  mongodb?: {
    host: string;
    port: number;
    database: string;
    username?: string;
    password?: string;
  };
}

interface ConnectionStatus {
  postgresql: 'connected' | 'disconnected' | 'testing' | 'error';
  chromadb: 'connected' | 'disconnected' | 'testing' | 'error';
  redis: 'connected' | 'disconnected' | 'testing' | 'error';
  mongodb: 'connected' | 'disconnected' | 'testing' | 'error' | 'disabled';
  supabase: 'connected' | 'disconnected' | 'error';
}

interface MigrationStatus {
  phase: 'idle' | 'configuring' | 'validating' | 'migrating' | 'syncing' | 'completed' | 'error';
  progress: number;
  current_step: string;
  estimated_time_remaining?: number;
  errors: string[];
  warnings: string[];
}

interface SyncStatus {
  enabled: boolean;
  last_sync: string;
  conflicts: number;
  sync_lag_ms: number;
  operations_pending: number;
}

export const DatabaseMigrationSettings: React.FC = () => {
  const { addToast } = useToast();
  
  // State management
  const [activeTab, setActiveTab] = useState<'config' | 'migration' | 'sync'>('config');
  const [databaseConfig, setDatabaseConfig] = useState<DatabaseConfig>({
    postgresql: {
      host: '10.202.70.30',
      port: 5432,
      database: 'archon',
      username: 'archon_user',
      password: '',
      ssl: false
    },
    chromadb: {
      host: '10.202.70.31',
      port: 8000,
      collection_prefix: 'archon',
      embedding_model: 'sentence-transformers/all-MiniLM-L6-v2'
    },
    redis: {
      host: '10.202.70.32',
      port: 6379,
      password: '',
      database_mapping: {
        realtime: 0,
        cache: 1,
        sessions: 2,
        tasks: 3
      }
    },
    mongodb: {
      host: '10.202.70.33',
      port: 27017,
      database: 'archon_documents',
      username: 'archon_user',
      password: ''
    }
  });
  
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    postgresql: 'disconnected',
    chromadb: 'disconnected',
    redis: 'disconnected',
    mongodb: 'disabled',
    supabase: 'connected'
  });
  
  const [migrationStatus, setMigrationStatus] = useState<MigrationStatus>({
    phase: 'idle',
    progress: 0,
    current_step: 'Ready to configure homelab connections',
    errors: [],
    warnings: []
  });
  
  const [syncStatus, setSyncStatus] = useState<SyncStatus>({
    enabled: false,
    last_sync: '',
    conflicts: 0,
    sync_lag_ms: 0,
    operations_pending: 0
  });

  // Connection testing
  const testConnection = async (provider: keyof DatabaseConfig) => {
    setConnectionStatus(prev => ({ ...prev, [provider]: 'testing' }));
    
    try {
      const response = await fetch('/api/migration/test-connection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, config: databaseConfig[provider] })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setConnectionStatus(prev => ({ ...prev, [provider]: 'connected' }));
        addToast({
          type: 'success',
          title: 'Connection Successful',
          message: `Successfully connected to ${provider.toUpperCase()}`
        });
      } else {
        setConnectionStatus(prev => ({ ...prev, [provider]: 'error' }));
        addToast({
          type: 'error',
          title: 'Connection Failed',
          message: result.error || `Failed to connect to ${provider.toUpperCase()}`
        });
      }
    } catch (error) {
      setConnectionStatus(prev => ({ ...prev, [provider]: 'error' }));
      addToast({
        type: 'error',
        title: 'Connection Error',
        message: `Error testing ${provider.toUpperCase()} connection`
      });
    }
  };

  // Test all connections
  const testAllConnections = async () => {
    const providers: (keyof DatabaseConfig)[] = ['postgresql', 'chromadb', 'redis'];
    if (databaseConfig.mongodb) {
      providers.push('mongodb');
    }
    
    for (const provider of providers) {
      await testConnection(provider);
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  };

  // Start migration
  const startMigration = async () => {
    try {
      const response = await fetch('/api/migration/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config: databaseConfig })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setMigrationStatus(prev => ({ 
          ...prev, 
          phase: 'migrating',
          current_step: 'Starting migration process...'
        }));
        addToast({
          type: 'success',
          title: 'Migration Started',
          message: 'Database migration has begun'
        });
      } else {
        addToast({
          type: 'error',
          title: 'Migration Failed',
          message: result.error || 'Failed to start migration'
        });
      }
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Migration Error',
        message: 'Error starting migration process'
      });
    }
  };

  // Enable/disable sync
  const toggleSync = async () => {
    try {
      const response = await fetch('/api/migration/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !syncStatus.enabled })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setSyncStatus(prev => ({ ...prev, enabled: !prev.enabled }));
        addToast({
          type: 'success',
          title: syncStatus.enabled ? 'Sync Disabled' : 'Sync Enabled',
          message: `Database sync has been ${syncStatus.enabled ? 'disabled' : 'enabled'}`
        });
      }
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Sync Error',
        message: 'Error toggling sync status'
      });
    }
  };

  // Rollback to Supabase
  const rollbackToSupabase = async () => {
    if (!confirm('Are you sure you want to rollback to Supabase? This will switch the primary database back to Supabase.')) {
      return;
    }
    
    try {
      const response = await fetch('/api/migration/rollback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setMigrationStatus(prev => ({ 
          ...prev, 
          phase: 'idle',
          current_step: 'Rolled back to Supabase'
        }));
        addToast({
          type: 'success',
          title: 'Rollback Complete',
          message: 'Successfully rolled back to Supabase'
        });
      }
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Rollback Error',
        message: 'Error during rollback process'
      });
    }
  };

  // Connection status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'testing': return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'error': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'disabled': return <WifiOff className="w-5 h-5 text-gray-400" />;
      default: return <WifiOff className="w-5 h-5 text-gray-400" />;
    }
  };

  // Check if all required connections are ready
  const allConnectionsReady = connectionStatus.postgresql === 'connected' && 
                              connectionStatus.chromadb === 'connected' && 
                              connectionStatus.redis === 'connected';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Database Migration
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Migrate from Supabase to your homelab infrastructure
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600 dark:text-gray-400">Supabase Active</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'config', label: 'Configuration', icon: Settings },
            { id: 'migration', label: 'Migration', icon: Database },
            { id: 'sync', label: 'Sync Status', icon: Monitor }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'config' && (
            <div className="space-y-6">
              {/* Current Status */}
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Current Database Status
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(connectionStatus).map(([provider, status]) => (
                    <div key={provider} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="flex items-center space-x-3">
                        {provider === 'postgresql' && <Database className="w-5 h-5 text-blue-500" />}
                        {provider === 'chromadb' && <Zap className="w-5 h-5 text-purple-500" />}
                        {provider === 'redis' && <Server className="w-5 h-5 text-red-500" />}
                        {provider === 'mongodb' && <HardDrive className="w-5 h-5 text-green-500" />}
                        {provider === 'supabase' && <Database className="w-5 h-5 text-emerald-500" />}
                        <span className="font-medium text-gray-900 dark:text-white capitalize">
                          {provider}
                        </span>
                      </div>
                      {getStatusIcon(status)}
                    </div>
                  ))}
                </div>
              </div>

              {/* Connection Testing */}
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Test Homelab Connections
                  </h3>
                  <Button
                    onClick={testAllConnections}
                    disabled={Object.values(connectionStatus).some(status => status === 'testing')}
                    className="flex items-center space-x-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Test All</span>
                  </Button>
                </div>
                
                <div className="space-y-4">
                  {(['postgresql', 'chromadb', 'redis', 'mongodb'] as const).map((provider) => (
                    <div key={provider} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <span className="font-medium text-gray-900 dark:text-white capitalize">
                          {provider}
                        </span>
                        <span className="text-sm text-gray-500">
                          {databaseConfig[provider]?.host}:{databaseConfig[provider]?.port}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(connectionStatus[provider])}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => testConnection(provider)}
                          disabled={connectionStatus[provider] === 'testing'}
                        >
                          Test
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Migration Actions */}
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Migration Actions
                </h3>
                
                <div className="flex flex-wrap gap-3">
                  <Button
                    onClick={startMigration}
                    disabled={!allConnectionsReady || migrationStatus.phase === 'migrating'}
                    className="flex items-center space-x-2"
                  >
                    <Play className="w-4 h-4" />
                    <span>Start Migration</span>
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={toggleSync}
                    disabled={!allConnectionsReady}
                    className="flex items-center space-x-2"
                  >
                    {syncStatus.enabled ? <Pause className="w-4 h-4" /> : <Wifi className="w-4 h-4" />}
                    <span>{syncStatus.enabled ? 'Disable Sync' : 'Enable Sync'}</span>
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={rollbackToSupabase}
                    className="flex items-center space-x-2 text-orange-600 border-orange-600 hover:bg-orange-50"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>Rollback to Supabase</span>
                  </Button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'migration' && (
            <div className="space-y-6">
              {/* Migration Progress */}
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Migration Progress
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {migrationStatus.current_step}
                    </span>
                    <span className="text-sm text-gray-500">
                      {migrationStatus.progress}%
                    </span>
                  </div>
                  
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${migrationStatus.progress}%` }}
                    />
                  </div>
                  
                  {migrationStatus.estimated_time_remaining && (
                    <p className="text-sm text-gray-500">
                      Estimated time remaining: {Math.ceil(migrationStatus.estimated_time_remaining / 60)} minutes
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'sync' && (
            <div className="space-y-6">
              {/* Sync Status */}
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Sync Status
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {syncStatus.enabled ? 'Active' : 'Inactive'}
                    </div>
                    <div className="text-sm text-gray-500">Sync Status</div>
                  </div>
                  
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {syncStatus.conflicts}
                    </div>
                    <div className="text-sm text-gray-500">Conflicts</div>
                  </div>
                  
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {syncStatus.sync_lag_ms}ms
                    </div>
                    <div className="text-sm text-gray-500">Sync Lag</div>
                  </div>
                  
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {syncStatus.operations_pending}
                    </div>
                    <div className="text-sm text-gray-500">Pending Ops</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};
