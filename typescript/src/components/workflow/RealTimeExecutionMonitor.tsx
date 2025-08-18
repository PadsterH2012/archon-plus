/**
 * RealTimeExecutionMonitor Component
 * 
 * Enhanced real-time monitoring component with WebSocket integration
 * Provides live updates, streaming logs, and performance metrics
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  Wifi,
  WifiOff,
  RefreshCw,
  Pause,
  Play,
  Square,
  AlertTriangle,
  TrendingUp,
  Clock,
  Zap,
  Eye,
  EyeOff,
  Download,
  Filter,
  Search
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { LoadingSpinner } from '../animations/Animations';
import { useToast } from '../../contexts/ToastContext';
import { useWorkflowMonitoring } from '../../hooks/useWorkflowMonitoring';
import { workflowService } from '../../services/workflowService';
import {
  WorkflowExecution,
  StepExecution,
  ExecutionLogEntry,
  WorkflowExecutionStatus,
  StepExecutionStatus
} from './types/workflow.types';

interface RealTimeExecutionMonitorProps {
  executionId: string;
  onCancel?: (executionId: string) => void;
  onPause?: (executionId: string) => void;
  onResume?: (executionId: string) => void;
  autoScroll?: boolean;
  showMetrics?: boolean;
  showLogs?: boolean;
}

export const RealTimeExecutionMonitor: React.FC<RealTimeExecutionMonitorProps> = ({
  executionId,
  onCancel,
  onPause,
  onResume,
  autoScroll = true,
  showMetrics = true,
  showLogs = true
}) => {
  // Real-time monitoring state
  const [monitoringState, monitoringActions] = useWorkflowMonitoring(executionId, {
    autoReconnect: true,
    maxLogs: 1000
  });

  // Local state
  const [isLoading, setIsLoading] = useState(false);
  const [showAllLogs, setShowAllLogs] = useState(false);
  const [logFilter, setLogFilter] = useState<'all' | 'error' | 'warning' | 'info'>('all');
  const [logSearch, setLogSearch] = useState('');
  const [metrics, setMetrics] = useState({
    avgStepDuration: 0,
    totalDuration: 0,
    stepsPerMinute: 0,
    errorRate: 0
  });

  const { showToast } = useToast();

  // Calculate metrics
  useEffect(() => {
    if (!monitoringState.execution || !monitoringState.stepExecutions.length) return;

    const completedSteps = monitoringState.stepExecutions.filter(
      step => step.status === StepExecutionStatus.COMPLETED && step.started_at && step.completed_at
    );

    const failedSteps = monitoringState.stepExecutions.filter(
      step => step.status === StepExecutionStatus.FAILED
    );

    if (completedSteps.length > 0) {
      const durations = completedSteps.map(step => {
        const start = new Date(step.started_at!).getTime();
        const end = new Date(step.completed_at!).getTime();
        return end - start;
      });

      const avgDuration = durations.reduce((sum, d) => sum + d, 0) / durations.length;
      
      const totalDuration = monitoringState.execution.started_at
        ? Date.now() - new Date(monitoringState.execution.started_at).getTime()
        : 0;

      const stepsPerMinute = totalDuration > 0 
        ? (completedSteps.length / (totalDuration / 60000))
        : 0;

      const errorRate = monitoringState.stepExecutions.length > 0
        ? (failedSteps.length / monitoringState.stepExecutions.length) * 100
        : 0;

      setMetrics({
        avgStepDuration: avgDuration,
        totalDuration,
        stepsPerMinute,
        errorRate
      });
    }
  }, [monitoringState.execution, monitoringState.stepExecutions]);

  // Handle execution actions
  const handleCancel = useCallback(async () => {
    if (!confirm('Are you sure you want to cancel this execution?')) return;
    
    try {
      setIsLoading(true);
      await workflowService.cancelExecution(executionId);
      showToast('Execution cancelled', 'success');
      onCancel?.(executionId);
    } catch (error) {
      console.error('Failed to cancel execution:', error);
      showToast('Failed to cancel execution', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [executionId, onCancel, showToast]);

  const handlePause = useCallback(async () => {
    try {
      setIsLoading(true);
      await workflowService.pauseExecution(executionId);
      showToast('Execution paused', 'success');
      onPause?.(executionId);
    } catch (error) {
      console.error('Failed to pause execution:', error);
      showToast('Failed to pause execution', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [executionId, onPause, showToast]);

  const handleResume = useCallback(async () => {
    try {
      setIsLoading(true);
      await workflowService.resumeExecution(executionId);
      showToast('Execution resumed', 'success');
      onResume?.(executionId);
    } catch (error) {
      console.error('Failed to resume execution:', error);
      showToast('Failed to resume execution', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [executionId, onResume, showToast]);

  // Filter logs
  const filteredLogs = monitoringState.logs.filter(log => {
    if (logFilter !== 'all' && log.level !== logFilter) return false;
    if (logSearch && !log.message.toLowerCase().includes(logSearch.toLowerCase())) return false;
    return true;
  });

  // Get status info
  const getStatusInfo = (status: WorkflowExecutionStatus) => {
    switch (status) {
      case WorkflowExecutionStatus.PENDING:
        return { color: 'orange', icon: Clock, label: 'Pending' };
      case WorkflowExecutionStatus.RUNNING:
        return { color: 'blue', icon: Activity, label: 'Running' };
      case WorkflowExecutionStatus.PAUSED:
        return { color: 'yellow', icon: Pause, label: 'Paused' };
      case WorkflowExecutionStatus.COMPLETED:
        return { color: 'green', icon: Activity, label: 'Completed' };
      case WorkflowExecutionStatus.FAILED:
        return { color: 'red', icon: AlertTriangle, label: 'Failed' };
      case WorkflowExecutionStatus.CANCELLED:
        return { color: 'gray', icon: Square, label: 'Cancelled' };
      default:
        return { color: 'gray', icon: Activity, label: 'Unknown' };
    }
  };

  const statusInfo = monitoringState.execution ? getStatusInfo(monitoringState.execution.status) : null;

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Card accentColor={monitoringState.isConnected ? 'green' : 'red'} className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {monitoringState.isConnected ? (
              <Wifi className="w-5 h-5 text-green-500" />
            ) : (
              <WifiOff className="w-5 h-5 text-red-500" />
            )}
            <div>
              <span className="font-medium text-gray-900 dark:text-white">
                Real-time Monitoring
              </span>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Status: {monitoringState.connectionStatus}
                {monitoringState.lastUpdate && (
                  <span className="ml-2">
                    • Last update: {monitoringState.lastUpdate.toLocaleTimeString()}
                  </span>
                )}
              </p>
            </div>
          </div>
          
          {!monitoringState.isConnected && (
            <Button
              variant="ghost"
              size="sm"
              onClick={monitoringActions.reconnect}
              icon={<RefreshCw className="w-4 h-4" />}
            >
              Reconnect
            </Button>
          )}
        </div>
        
        {monitoringState.error && (
          <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
            <div className="flex items-center justify-between">
              <span className="text-red-800 dark:text-red-200 text-sm">{monitoringState.error}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={monitoringActions.clearError}
                className="text-red-600 hover:text-red-800"
              >
                Dismiss
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Execution Overview */}
      {monitoringState.execution && (
        <Card accentColor={statusInfo?.color || 'blue'} className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              {statusInfo && <statusInfo.icon className="w-6 h-6" />}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Execution Monitor
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  ID: {executionId.slice(0, 8)}...
                </p>
              </div>
              {statusInfo && (
                <Badge color={statusInfo.color} icon={<statusInfo.icon className="w-3 h-3" />}>
                  {statusInfo.label}
                </Badge>
              )}
            </div>

            <div className="flex items-center space-x-2">
              {monitoringState.execution.status === WorkflowExecutionStatus.RUNNING && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handlePause}
                  disabled={isLoading}
                  icon={<Pause className="w-4 h-4" />}
                >
                  Pause
                </Button>
              )}

              {monitoringState.execution.status === WorkflowExecutionStatus.PAUSED && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleResume}
                  disabled={isLoading}
                  icon={<Play className="w-4 h-4" />}
                >
                  Resume
                </Button>
              )}

              {(monitoringState.execution.status === WorkflowExecutionStatus.RUNNING || 
                monitoringState.execution.status === WorkflowExecutionStatus.PAUSED) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCancel}
                  disabled={isLoading}
                  icon={<Square className="w-4 h-4" />}
                >
                  Cancel
                </Button>
              )}
            </div>
          </div>

          {/* Progress */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Progress: {monitoringState.execution.current_step_index} / {monitoringState.execution.total_steps} steps
              </span>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {Math.round(monitoringState.execution.progress_percentage)}%
              </span>
            </div>
            <Progress 
              value={monitoringState.execution.progress_percentage} 
              color={statusInfo?.color || 'blue'}
              className="h-3"
            />
          </div>

          {/* Metrics */}
          {showMetrics && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round(metrics.avgStepDuration / 1000)}s
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Avg Step Duration</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round(metrics.totalDuration / 1000)}s
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Duration</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metrics.stepsPerMinute.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Steps/Min</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metrics.errorRate.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Error Rate</div>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Step Executions */}
      {monitoringState.stepExecutions.length > 0 && (
        <Card accentColor="purple" className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Step Executions ({monitoringState.stepExecutions.length})
          </h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {monitoringState.stepExecutions.map((step) => (
              <div key={step.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    step.status === StepExecutionStatus.COMPLETED ? 'bg-green-500' :
                    step.status === StepExecutionStatus.RUNNING ? 'bg-blue-500 animate-pulse' :
                    step.status === StepExecutionStatus.FAILED ? 'bg-red-500' :
                    step.status === StepExecutionStatus.PENDING ? 'bg-orange-500' :
                    'bg-gray-500'
                  }`} />
                  
                  <div>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {step.step_name}
                    </span>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {step.step_type} • Step {step.step_index + 1}
                      {step.tool_name && ` • ${step.tool_name}`}
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <Badge 
                    color={
                      step.status === StepExecutionStatus.COMPLETED ? 'green' :
                      step.status === StepExecutionStatus.RUNNING ? 'blue' :
                      step.status === StepExecutionStatus.FAILED ? 'red' :
                      step.status === StepExecutionStatus.PENDING ? 'orange' :
                      'gray'
                    }
                    size="sm"
                  >
                    {step.status}
                  </Badge>
                  
                  {step.started_at && (
                    <div className="text-xs text-gray-500 mt-1">
                      {workflowService.formatExecutionDuration(step.started_at, step.completed_at)}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Real-time Logs */}
      {showLogs && (
        <Card accentColor="gray" className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Live Logs ({filteredLogs.length})
            </h3>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAllLogs(!showAllLogs)}
                icon={showAllLogs ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              >
                {showAllLogs ? 'Collapse' : 'Expand'}
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={monitoringActions.clearLogs}
                icon={<RefreshCw className="w-4 h-4" />}
              >
                Clear
              </Button>
            </div>
          </div>
          
          {/* Log Filters */}
          <div className="flex items-center space-x-4 mb-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={logFilter}
                onChange={(e) => setLogFilter(e.target.value as any)}
                className="px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
              >
                <option value="all">All Levels</option>
                <option value="error">Errors</option>
                <option value="warning">Warnings</option>
                <option value="info">Info</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2 flex-1">
              <Search className="w-4 h-4 text-gray-500" />
              <input
                type="text"
                value={logSearch}
                onChange={(e) => setLogSearch(e.target.value)}
                placeholder="Search logs..."
                className="flex-1 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
              />
            </div>
          </div>
          
          {/* Log Entries */}
          <div className={`space-y-1 font-mono text-sm ${showAllLogs ? 'max-h-96' : 'max-h-48'} overflow-y-auto bg-gray-900 dark:bg-gray-800 text-green-400 p-4 rounded`}>
            {filteredLogs.length === 0 ? (
              <div className="text-gray-500 text-center py-4">
                {monitoringState.logs.length === 0 ? 'No logs yet...' : 'No logs match current filters'}
              </div>
            ) : (
              filteredLogs.map((log, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <span className="text-gray-500 w-20 flex-shrink-0">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  
                  <span className={`w-16 flex-shrink-0 ${
                    log.level === 'error' ? 'text-red-400' :
                    log.level === 'warning' ? 'text-yellow-400' :
                    'text-blue-400'
                  }`}>
                    [{log.level.toUpperCase()}]
                  </span>
                  
                  <span className="flex-1 text-gray-300">
                    {log.step_name && <span className="text-purple-400">[{log.step_name}] </span>}
                    {log.message}
                  </span>
                </div>
              ))
            )}
          </div>
        </Card>
      )}
    </div>
  );
};
