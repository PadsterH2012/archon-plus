/**
 * WorkflowExecutionMonitor Component
 * 
 * Real-time monitoring component for workflow execution
 * Shows progress, step details, and execution logs
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Play, 
  Pause, 
  Square, 
  RefreshCw, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  ChevronDown,
  ChevronRight,
  Activity,
  Zap,
  GitBranch,
  RotateCcw,
  Link,
  List,
  User,
  Calendar
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { LoadingSpinner } from '../animations/Animations';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import { 
  WorkflowExecutionProps,
  WorkflowExecution,
  StepExecution,
  WorkflowExecutionStatus,
  StepExecutionStatus,
  WorkflowStepType,
  ExecutionLogEntry
} from './types/workflow.types';

export const WorkflowExecutionMonitor: React.FC<WorkflowExecutionProps> = ({
  execution: initialExecution,
  stepExecutions: initialStepExecutions = [],
  onCancel,
  onPause,
  onResume,
  onRefresh,
  autoRefresh = true,
  refreshInterval = 5000
}) => {
  // State management
  const [execution, setExecution] = useState<WorkflowExecution>(initialExecution);
  const [stepExecutions, setStepExecutions] = useState<StepExecution[]>(initialStepExecutions);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [showLogs, setShowLogs] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const { showToast } = useToast();

  // Auto-refresh execution status
  const refreshExecution = useCallback(async () => {
    try {
      setIsRefreshing(true);
      const response = await workflowService.getExecutionStatus(execution.id);
      setExecution(response.execution);
      setStepExecutions(response.step_executions);
      onRefresh?.(execution.id);
    } catch (error) {
      console.error('Failed to refresh execution:', error);
      showToast('Failed to refresh execution status', 'error');
    } finally {
      setIsRefreshing(false);
    }
  }, [execution.id, onRefresh, showToast]);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;
    
    const isRunning = execution.status === WorkflowExecutionStatus.RUNNING || 
                     execution.status === WorkflowExecutionStatus.PENDING;
    
    if (!isRunning) return;

    const interval = setInterval(refreshExecution, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, execution.status, refreshExecution]);

  // Handle execution actions
  const handleCancel = useCallback(async () => {
    if (!confirm('Are you sure you want to cancel this execution?')) return;
    
    try {
      setIsLoading(true);
      await workflowService.cancelExecution(execution.id);
      await refreshExecution();
      showToast('Execution cancelled', 'success');
      onCancel?.(execution.id);
    } catch (error) {
      console.error('Failed to cancel execution:', error);
      showToast('Failed to cancel execution', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [execution.id, onCancel, refreshExecution, showToast]);

  const handlePause = useCallback(async () => {
    try {
      setIsLoading(true);
      await workflowService.pauseExecution(execution.id);
      await refreshExecution();
      showToast('Execution paused', 'success');
      onPause?.(execution.id);
    } catch (error) {
      console.error('Failed to pause execution:', error);
      showToast('Failed to pause execution', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [execution.id, onPause, refreshExecution, showToast]);

  const handleResume = useCallback(async () => {
    try {
      setIsLoading(true);
      await workflowService.resumeExecution(execution.id);
      await refreshExecution();
      showToast('Execution resumed', 'success');
      onResume?.(execution.id);
    } catch (error) {
      console.error('Failed to resume execution:', error);
      showToast('Failed to resume execution', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [execution.id, onResume, refreshExecution, showToast]);

  // Toggle step expansion
  const toggleStepExpansion = useCallback((stepId: string) => {
    setExpandedSteps(prev => {
      const newSet = new Set(prev);
      if (newSet.has(stepId)) {
        newSet.delete(stepId);
      } else {
        newSet.add(stepId);
      }
      return newSet;
    });
  }, []);

  // Get status info
  const getExecutionStatusInfo = (status: WorkflowExecutionStatus) => {
    switch (status) {
      case WorkflowExecutionStatus.PENDING:
        return { color: 'orange', icon: <Clock className="w-4 h-4" />, label: 'Pending' };
      case WorkflowExecutionStatus.RUNNING:
        return { color: 'blue', icon: <Activity className="w-4 h-4" />, label: 'Running' };
      case WorkflowExecutionStatus.PAUSED:
        return { color: 'yellow', icon: <Pause className="w-4 h-4" />, label: 'Paused' };
      case WorkflowExecutionStatus.COMPLETED:
        return { color: 'green', icon: <CheckCircle className="w-4 h-4" />, label: 'Completed' };
      case WorkflowExecutionStatus.FAILED:
        return { color: 'red', icon: <XCircle className="w-4 h-4" />, label: 'Failed' };
      case WorkflowExecutionStatus.CANCELLED:
        return { color: 'gray', icon: <Square className="w-4 h-4" />, label: 'Cancelled' };
      default:
        return { color: 'gray', icon: <AlertCircle className="w-4 h-4" />, label: 'Unknown' };
    }
  };

  const getStepStatusInfo = (status: StepExecutionStatus) => {
    switch (status) {
      case StepExecutionStatus.PENDING:
        return { color: 'orange', icon: <Clock className="w-3 h-3" />, label: 'Pending' };
      case StepExecutionStatus.RUNNING:
        return { color: 'blue', icon: <Activity className="w-3 h-3" />, label: 'Running' };
      case StepExecutionStatus.COMPLETED:
        return { color: 'green', icon: <CheckCircle className="w-3 h-3" />, label: 'Completed' };
      case StepExecutionStatus.FAILED:
        return { color: 'red', icon: <XCircle className="w-3 h-3" />, label: 'Failed' };
      case StepExecutionStatus.SKIPPED:
        return { color: 'gray', icon: <AlertCircle className="w-3 h-3" />, label: 'Skipped' };
      default:
        return { color: 'gray', icon: <AlertCircle className="w-3 h-3" />, label: 'Unknown' };
    }
  };

  const getStepTypeIcon = (stepType: WorkflowStepType) => {
    switch (stepType) {
      case WorkflowStepType.ACTION:
        return <Zap className="w-4 h-4" />;
      case WorkflowStepType.CONDITION:
        return <GitBranch className="w-4 h-4" />;
      case WorkflowStepType.PARALLEL:
        return <List className="w-4 h-4" />;
      case WorkflowStepType.LOOP:
        return <RotateCcw className="w-4 h-4" />;
      case WorkflowStepType.WORKFLOW_LINK:
        return <Link className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const executionStatusInfo = getExecutionStatusInfo(execution.status);
  const duration = workflowService.formatExecutionDuration(execution.started_at, execution.completed_at);

  return (
    <div className="space-y-6">
      {/* Execution Header */}
      <Card accentColor="blue" className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              {executionStatusInfo.icon}
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Workflow Execution
              </h2>
            </div>
            
            <Badge 
              color={executionStatusInfo.color}
              icon={executionStatusInfo.icon}
            >
              {executionStatusInfo.label}
            </Badge>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={refreshExecution}
              disabled={isRefreshing}
              icon={isRefreshing ? <LoadingSpinner size="sm" /> : <RefreshCw className="w-4 h-4" />}
            >
              Refresh
            </Button>

            {execution.status === WorkflowExecutionStatus.RUNNING && (
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

            {execution.status === WorkflowExecutionStatus.PAUSED && (
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

            {(execution.status === WorkflowExecutionStatus.RUNNING || 
              execution.status === WorkflowExecutionStatus.PAUSED) && (
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

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Progress: {execution.current_step_index} / {execution.total_steps} steps
            </span>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {Math.round(execution.progress_percentage)}%
            </span>
          </div>
          <Progress 
            value={execution.progress_percentage} 
            color={executionStatusInfo.color}
            className="h-2"
          />
        </div>

        {/* Execution Metadata */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-600 dark:text-gray-400">Triggered by:</span>
            <div className="flex items-center space-x-1 mt-1">
              <User className="w-3 h-3" />
              <span className="font-medium">{execution.triggered_by}</span>
            </div>
          </div>
          
          <div>
            <span className="text-gray-600 dark:text-gray-400">Duration:</span>
            <div className="flex items-center space-x-1 mt-1">
              <Clock className="w-3 h-3" />
              <span className="font-medium">{duration}</span>
            </div>
          </div>
          
          <div>
            <span className="text-gray-600 dark:text-gray-400">Started:</span>
            <div className="flex items-center space-x-1 mt-1">
              <Calendar className="w-3 h-3" />
              <span className="font-medium">
                {execution.started_at ? new Date(execution.started_at).toLocaleString() : 'Not started'}
              </span>
            </div>
          </div>
          
          <div>
            <span className="text-gray-600 dark:text-gray-400">Execution ID:</span>
            <div className="mt-1">
              <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                {execution.id.slice(0, 8)}...
              </code>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {execution.error_message && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <div className="flex items-center space-x-2">
              <XCircle className="w-4 h-4 text-red-500" />
              <span className="text-sm font-medium text-red-800 dark:text-red-200">Error:</span>
            </div>
            <p className="text-sm text-red-700 dark:text-red-300 mt-1">
              {execution.error_message}
            </p>
          </div>
        )}
      </Card>

      {/* Step Executions */}
      <Card accentColor="purple" className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Step Executions
          </h3>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowLogs(!showLogs)}
            icon={showLogs ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          >
            {showLogs ? 'Hide' : 'Show'} Logs
          </Button>
        </div>

        <div className="space-y-3">
          {stepExecutions.map((stepExecution) => {
            const stepStatusInfo = getStepStatusInfo(stepExecution.status);
            const isExpanded = expandedSteps.has(stepExecution.id);
            
            return (
              <div key={stepExecution.id} className="border border-gray-200 dark:border-gray-700 rounded-lg">
                <div 
                  className="p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800"
                  onClick={() => toggleStepExpansion(stepExecution.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getStepTypeIcon(stepExecution.step_type)}
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-gray-900 dark:text-white">
                            {stepExecution.step_name}
                          </span>
                          <Badge 
                            color={stepStatusInfo.color}
                            size="sm"
                            icon={stepStatusInfo.icon}
                          >
                            {stepStatusInfo.label}
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                          Step {stepExecution.step_index + 1} • {stepExecution.step_type}
                          {stepExecution.tool_name && ` • ${stepExecution.tool_name}`}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {stepExecution.started_at && (
                        <span className="text-xs text-gray-500">
                          {workflowService.formatExecutionDuration(stepExecution.started_at, stepExecution.completed_at)}
                        </span>
                      )}
                      {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 text-sm">
                      {stepExecution.tool_parameters && Object.keys(stepExecution.tool_parameters).length > 0 && (
                        <div>
                          <span className="font-medium text-gray-700 dark:text-gray-300">Parameters:</span>
                          <pre className="mt-1 text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-x-auto">
                            {JSON.stringify(stepExecution.tool_parameters, null, 2)}
                          </pre>
                        </div>
                      )}
                      
                      {stepExecution.output_data && Object.keys(stepExecution.output_data).length > 0 && (
                        <div>
                          <span className="font-medium text-gray-700 dark:text-gray-300">Output:</span>
                          <pre className="mt-1 text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded overflow-x-auto">
                            {JSON.stringify(stepExecution.output_data, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                    
                    {stepExecution.error_message && (
                      <div className="mt-3 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
                        <span className="text-sm font-medium text-red-800 dark:text-red-200">Error:</span>
                        <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                          {stepExecution.error_message}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Execution Logs */}
      {showLogs && execution.execution_log && execution.execution_log.length > 0 && (
        <Card accentColor="gray" className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Execution Logs
          </h3>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {execution.execution_log.map((logEntry, index) => (
              <div key={index} className="flex items-start space-x-3 text-sm">
                <span className="text-xs text-gray-500 w-20 flex-shrink-0">
                  {new Date(logEntry.timestamp).toLocaleTimeString()}
                </span>
                
                <Badge 
                  color={logEntry.level === 'error' ? 'red' : logEntry.level === 'warning' ? 'orange' : 'blue'}
                  size="sm"
                  className="flex-shrink-0"
                >
                  {logEntry.level}
                </Badge>
                
                <span className="text-gray-700 dark:text-gray-300 flex-1">
                  {logEntry.step_name && `[${logEntry.step_name}] `}
                  {logEntry.message}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};
