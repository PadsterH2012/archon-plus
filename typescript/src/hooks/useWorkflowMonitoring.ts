/**
 * useWorkflowMonitoring Hook
 * 
 * React hook for real-time workflow execution monitoring
 * Integrates WebSocket service with React components
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { workflowWebSocketService, ExecutionUpdateData, ProgressUpdateData, LogEntryData } from '../services/workflowWebSocketService';
import { WorkflowExecution, StepExecution, ExecutionLogEntry } from '../components/workflow/types/workflow.types';

export interface MonitoringState {
  execution: WorkflowExecution | null;
  stepExecutions: StepExecution[];
  logs: ExecutionLogEntry[];
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastUpdate: Date | null;
  error: string | null;
}

export interface MonitoringOptions {
  autoReconnect?: boolean;
  maxLogs?: number;
  enableHeartbeat?: boolean;
}

export interface MonitoringActions {
  subscribe: (executionId: string) => void;
  unsubscribe: (executionId: string) => void;
  subscribeToAll: () => void;
  unsubscribeFromAll: () => void;
  reconnect: () => void;
  clearLogs: () => void;
  clearError: () => void;
}

export function useWorkflowMonitoring(
  initialExecutionId?: string,
  options: MonitoringOptions = {}
): [MonitoringState, MonitoringActions] {
  const {
    autoReconnect = true,
    maxLogs = 1000,
    enableHeartbeat = true
  } = options;

  // State
  const [state, setState] = useState<MonitoringState>({
    execution: null,
    stepExecutions: [],
    logs: [],
    isConnected: false,
    connectionStatus: 'disconnected',
    lastUpdate: null,
    error: null
  });

  // Refs for stable callbacks
  const subscriptionsRef = useRef<Set<string>>(new Set());
  const isSubscribedToAllRef = useRef(false);

  // Update connection status
  const updateConnectionStatus = useCallback(() => {
    const status = workflowWebSocketService.getConnectionStatus();
    const isConnected = workflowWebSocketService.isConnected();
    
    setState(prev => ({
      ...prev,
      connectionStatus: status,
      isConnected
    }));
  }, []);

  // Handle execution updates
  const handleExecutionUpdate = useCallback((data: ExecutionUpdateData) => {
    setState(prev => ({
      ...prev,
      execution: data.execution,
      stepExecutions: data.step_executions,
      lastUpdate: new Date(),
      error: null
    }));
  }, []);

  // Handle step updates
  const handleStepUpdate = useCallback((stepExecution: StepExecution) => {
    setState(prev => ({
      ...prev,
      stepExecutions: prev.stepExecutions.map(step =>
        step.id === stepExecution.id ? stepExecution : step
      ),
      lastUpdate: new Date()
    }));
  }, []);

  // Handle log entries
  const handleLogEntry = useCallback((data: LogEntryData) => {
    setState(prev => {
      const newLogs = [...prev.logs, data.entry];
      
      // Limit log size
      if (newLogs.length > maxLogs) {
        newLogs.splice(0, newLogs.length - maxLogs);
      }
      
      return {
        ...prev,
        logs: newLogs,
        lastUpdate: new Date()
      };
    });
  }, [maxLogs]);

  // Handle progress updates
  const handleProgressUpdate = useCallback((data: ProgressUpdateData) => {
    setState(prev => ({
      ...prev,
      execution: prev.execution ? {
        ...prev.execution,
        current_step_index: data.current_step_index,
        total_steps: data.total_steps,
        progress_percentage: data.progress_percentage,
        status: data.status as any
      } : null,
      lastUpdate: new Date()
    }));
  }, []);

  // Handle errors
  const handleError = useCallback((error: string) => {
    setState(prev => ({
      ...prev,
      error,
      lastUpdate: new Date()
    }));
  }, []);

  // Handle connection events
  const handleConnect = useCallback(() => {
    updateConnectionStatus();
    
    // Resubscribe to previous subscriptions
    subscriptionsRef.current.forEach(executionId => {
      workflowWebSocketService.subscribeToExecution(executionId);
    });
    
    if (isSubscribedToAllRef.current) {
      workflowWebSocketService.subscribeToAllExecutions();
    }
  }, [updateConnectionStatus]);

  const handleDisconnect = useCallback(() => {
    updateConnectionStatus();
  }, [updateConnectionStatus]);

  const handleReconnect = useCallback(() => {
    updateConnectionStatus();
  }, [updateConnectionStatus]);

  // Setup WebSocket handlers
  useEffect(() => {
    workflowWebSocketService.setHandlers({
      onExecutionUpdate: handleExecutionUpdate,
      onStepUpdate: handleStepUpdate,
      onLogEntry: handleLogEntry,
      onProgressUpdate: handleProgressUpdate,
      onError: handleError,
      onConnect: handleConnect,
      onDisconnect: handleDisconnect,
      onReconnect: handleReconnect
    });

    // Initial connection status
    updateConnectionStatus();

    // Subscribe to initial execution if provided
    if (initialExecutionId) {
      workflowWebSocketService.subscribeToExecution(initialExecutionId);
      subscriptionsRef.current.add(initialExecutionId);
    }

    return () => {
      // Cleanup subscriptions on unmount
      subscriptionsRef.current.forEach(executionId => {
        workflowWebSocketService.unsubscribeFromExecution(executionId);
      });
      
      if (isSubscribedToAllRef.current) {
        workflowWebSocketService.unsubscribeFromAllExecutions();
      }
    };
  }, [
    initialExecutionId,
    handleExecutionUpdate,
    handleStepUpdate,
    handleLogEntry,
    handleProgressUpdate,
    handleError,
    handleConnect,
    handleDisconnect,
    handleReconnect,
    updateConnectionStatus
  ]);

  // Periodic connection status updates
  useEffect(() => {
    const interval = setInterval(updateConnectionStatus, 5000);
    return () => clearInterval(interval);
  }, [updateConnectionStatus]);

  // Actions
  const subscribe = useCallback((executionId: string) => {
    subscriptionsRef.current.add(executionId);
    workflowWebSocketService.subscribeToExecution(executionId);
  }, []);

  const unsubscribe = useCallback((executionId: string) => {
    subscriptionsRef.current.delete(executionId);
    workflowWebSocketService.unsubscribeFromExecution(executionId);
    
    // Clear state if unsubscribing from current execution
    setState(prev => {
      if (prev.execution?.id === executionId) {
        return {
          ...prev,
          execution: null,
          stepExecutions: [],
          logs: []
        };
      }
      return prev;
    });
  }, []);

  const subscribeToAll = useCallback(() => {
    isSubscribedToAllRef.current = true;
    workflowWebSocketService.subscribeToAllExecutions();
  }, []);

  const unsubscribeFromAll = useCallback(() => {
    isSubscribedToAllRef.current = false;
    subscriptionsRef.current.clear();
    workflowWebSocketService.unsubscribeFromAllExecutions();
    
    setState(prev => ({
      ...prev,
      execution: null,
      stepExecutions: [],
      logs: []
    }));
  }, []);

  const reconnect = useCallback(() => {
    workflowWebSocketService.reconnect();
  }, []);

  const clearLogs = useCallback(() => {
    setState(prev => ({
      ...prev,
      logs: []
    }));
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({
      ...prev,
      error: null
    }));
  }, []);

  const actions: MonitoringActions = {
    subscribe,
    unsubscribe,
    subscribeToAll,
    unsubscribeFromAll,
    reconnect,
    clearLogs,
    clearError
  };

  return [state, actions];
}

// Hook for monitoring multiple executions
export function useMultipleExecutionMonitoring(
  executionIds: string[] = [],
  options: MonitoringOptions = {}
): [Record<string, MonitoringState>, MonitoringActions] {
  const [states, setStates] = useState<Record<string, MonitoringState>>({});
  const [globalState, globalActions] = useWorkflowMonitoring(undefined, options);

  // Handle execution updates for multiple executions
  useEffect(() => {
    workflowWebSocketService.setHandlers({
      ...workflowWebSocketService['handlers'],
      onExecutionUpdate: (data: ExecutionUpdateData) => {
        const executionId = data.execution.id;
        setStates(prev => ({
          ...prev,
          [executionId]: {
            execution: data.execution,
            stepExecutions: data.step_executions,
            logs: prev[executionId]?.logs || [],
            isConnected: globalState.isConnected,
            connectionStatus: globalState.connectionStatus,
            lastUpdate: new Date(),
            error: null
          }
        }));
      },
      onLogEntry: (data: LogEntryData) => {
        const executionId = data.execution_id;
        setStates(prev => {
          const currentState = prev[executionId];
          if (!currentState) return prev;
          
          const newLogs = [...currentState.logs, data.entry];
          if (newLogs.length > (options.maxLogs || 1000)) {
            newLogs.splice(0, newLogs.length - (options.maxLogs || 1000));
          }
          
          return {
            ...prev,
            [executionId]: {
              ...currentState,
              logs: newLogs,
              lastUpdate: new Date()
            }
          };
        });
      }
    });
  }, [globalState.isConnected, globalState.connectionStatus, options.maxLogs]);

  // Subscribe to execution IDs
  useEffect(() => {
    executionIds.forEach(id => {
      globalActions.subscribe(id);
      
      // Initialize state for new executions
      setStates(prev => {
        if (!prev[id]) {
          return {
            ...prev,
            [id]: {
              execution: null,
              stepExecutions: [],
              logs: [],
              isConnected: globalState.isConnected,
              connectionStatus: globalState.connectionStatus,
              lastUpdate: null,
              error: null
            }
          };
        }
        return prev;
      });
    });

    return () => {
      executionIds.forEach(id => {
        globalActions.unsubscribe(id);
      });
    };
  }, [executionIds, globalActions, globalState.isConnected, globalState.connectionStatus]);

  return [states, globalActions];
}

export default useWorkflowMonitoring;
