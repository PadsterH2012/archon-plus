/**
 * WorkflowExecutionDashboard Component
 * 
 * Dashboard for monitoring all workflow executions
 * Shows execution list, status overview, and quick actions
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Activity, 
  RefreshCw, 
  Filter, 
  Search, 
  Play, 
  Pause, 
  Square, 
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  User,
  Calendar,
  TrendingUp,
  BarChart3
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { LoadingSpinner } from '../animations/Animations';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import { 
  ExecutionDashboardProps,
  WorkflowExecution,
  WorkflowExecutionStatus,
  ExecutionFilters
} from './types/workflow.types';

export const WorkflowExecutionDashboard: React.FC<ExecutionDashboardProps> = ({
  executions: initialExecutions = [],
  isLoading: externalLoading = false,
  onExecutionSelect,
  onExecutionCancel,
  onExecutionPause,
  onExecutionResume,
  onRefresh,
  autoRefresh = true,
  refreshInterval = 10000
}) => {
  // State management
  const [executions, setExecutions] = useState<WorkflowExecution[]>(initialExecutions);
  const [isLoading, setIsLoading] = useState(externalLoading);
  const [filters, setFilters] = useState<ExecutionFilters>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  const [stats, setStats] = useState({
    total: 0,
    running: 0,
    completed: 0,
    failed: 0,
    pending: 0
  });

  const { showToast } = useToast();

  // Load executions from API
  const loadExecutions = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await workflowService.listExecutions(filters, 1, 50);
      setExecutions(response.executions);
      
      // Calculate stats
      const newStats = response.executions.reduce((acc, execution) => {
        acc.total++;
        switch (execution.status) {
          case WorkflowExecutionStatus.RUNNING:
            acc.running++;
            break;
          case WorkflowExecutionStatus.COMPLETED:
            acc.completed++;
            break;
          case WorkflowExecutionStatus.FAILED:
            acc.failed++;
            break;
          case WorkflowExecutionStatus.PENDING:
            acc.pending++;
            break;
        }
        return acc;
      }, { total: 0, running: 0, completed: 0, failed: 0, pending: 0 });
      
      setStats(newStats);
      onRefresh?.();
      
    } catch (error) {
      console.error('Failed to load executions:', error);
      showToast('Failed to load executions', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [filters, onRefresh, showToast]);

  // Auto-refresh effect
  useEffect(() => {
    loadExecutions();
  }, [loadExecutions]);

  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(loadExecutions, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, loadExecutions]);

  // Handle execution actions
  const handleExecutionAction = useCallback(async (
    executionId: string, 
    action: 'cancel' | 'pause' | 'resume',
    callback?: (executionId: string) => void
  ) => {
    try {
      switch (action) {
        case 'cancel':
          await workflowService.cancelExecution(executionId);
          onExecutionCancel?.(executionId);
          break;
        case 'pause':
          await workflowService.pauseExecution(executionId);
          onExecutionPause?.(executionId);
          break;
        case 'resume':
          await workflowService.resumeExecution(executionId);
          onExecutionResume?.(executionId);
          break;
      }
      
      await loadExecutions();
      showToast(`Execution ${action}${action.endsWith('e') ? 'd' : action === 'cancel' ? 'led' : 'ed'}`, 'success');
      callback?.(executionId);
      
    } catch (error) {
      console.error(`Failed to ${action} execution:`, error);
      showToast(`Failed to ${action} execution`, 'error');
    }
  }, [onExecutionCancel, onExecutionPause, onExecutionResume, loadExecutions, showToast]);

  // Filter executions based on search
  const filteredExecutions = executions.filter(execution => {
    if (!searchQuery) return true;
    
    const searchLower = searchQuery.toLowerCase();
    return (
      execution.id.toLowerCase().includes(searchLower) ||
      execution.triggered_by.toLowerCase().includes(searchLower) ||
      execution.status.toLowerCase().includes(searchLower)
    );
  });

  // Get status info
  const getStatusInfo = (status: WorkflowExecutionStatus) => {
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className="w-8 h-8 text-blue-500" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Execution Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Monitor and manage workflow executions
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            icon={<Filter className="w-4 h-4" />}
          >
            Filters
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={loadExecutions}
            disabled={isLoading}
            icon={isLoading ? <LoadingSpinner size="sm" /> : <RefreshCw className="w-4 h-4" />}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card accentColor="purple" className="p-4">
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-8 h-8 text-purple-500" />
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
            </div>
          </div>
        </Card>
        
        <Card accentColor="blue" className="p-4">
          <div className="flex items-center space-x-3">
            <Activity className="w-8 h-8 text-blue-500" />
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.running}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Running</p>
            </div>
          </div>
        </Card>
        
        <Card accentColor="green" className="p-4">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.completed}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
            </div>
          </div>
        </Card>
        
        <Card accentColor="red" className="p-4">
          <div className="flex items-center space-x-3">
            <XCircle className="w-8 h-8 text-red-500" />
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.failed}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
            </div>
          </div>
        </Card>
        
        <Card accentColor="orange" className="p-4">
          <div className="flex items-center space-x-3">
            <Clock className="w-8 h-8 text-orange-500" />
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.pending}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Pending</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card accentColor="blue" className="p-4">
        <div className="space-y-4">
          <Input
            placeholder="Search executions by ID, user, or status..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon={<Search className="w-4 h-4" />}
            accentColor="blue"
          />
          
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={filters.status || ''}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value as WorkflowExecutionStatus || undefined }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value="">All Statuses</option>
                  <option value={WorkflowExecutionStatus.PENDING}>Pending</option>
                  <option value={WorkflowExecutionStatus.RUNNING}>Running</option>
                  <option value={WorkflowExecutionStatus.PAUSED}>Paused</option>
                  <option value={WorkflowExecutionStatus.COMPLETED}>Completed</option>
                  <option value={WorkflowExecutionStatus.FAILED}>Failed</option>
                  <option value={WorkflowExecutionStatus.CANCELLED}>Cancelled</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Triggered By
                </label>
                <Input
                  placeholder="Filter by user..."
                  value={filters.triggered_by || ''}
                  onChange={(e) => setFilters(prev => ({ ...prev, triggered_by: e.target.value || undefined }))}
                  accentColor="blue"
                />
              </div>
              
              <div className="flex items-end">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setFilters({});
                    setSearchQuery('');
                  }}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Executions List */}
      {isLoading && executions.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredExecutions.length === 0 ? (
        <Card accentColor="gray" className="p-12 text-center">
          <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No executions found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {searchQuery || Object.keys(filters).length > 0
              ? 'Try adjusting your search criteria or filters'
              : 'No workflow executions have been started yet'
            }
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredExecutions.map((execution) => {
            const statusInfo = getStatusInfo(execution.status);
            const duration = workflowService.formatExecutionDuration(execution.started_at, execution.completed_at);
            
            return (
              <Card 
                key={execution.id} 
                accentColor={statusInfo.color}
                className="p-6 hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => {
                  setSelectedExecution(execution);
                  onExecutionSelect?.(execution);
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <Badge 
                        color={statusInfo.color}
                        icon={statusInfo.icon}
                      >
                        {statusInfo.label}
                      </Badge>
                      
                      <code className="text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                        {execution.id.slice(0, 8)}...
                      </code>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Triggered by:</span>
                        <div className="flex items-center space-x-1 mt-1">
                          <User className="w-3 h-3" />
                          <span className="font-medium">{execution.triggered_by}</span>
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Progress:</span>
                        <div className="mt-1">
                          <Progress 
                            value={execution.progress_percentage} 
                            color={statusInfo.color}
                            className="h-2"
                          />
                          <span className="text-xs text-gray-500 mt-1">
                            {execution.current_step_index} / {execution.total_steps} steps ({Math.round(execution.progress_percentage)}%)
                          </span>
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
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onExecutionSelect?.(execution);
                      }}
                      icon={<Eye className="w-4 h-4" />}
                    >
                      View
                    </Button>

                    {execution.status === WorkflowExecutionStatus.RUNNING && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleExecutionAction(execution.id, 'pause');
                        }}
                        icon={<Pause className="w-4 h-4" />}
                      >
                        Pause
                      </Button>
                    )}

                    {execution.status === WorkflowExecutionStatus.PAUSED && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleExecutionAction(execution.id, 'resume');
                        }}
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
                        onClick={(e) => {
                          e.stopPropagation();
                          if (confirm('Are you sure you want to cancel this execution?')) {
                            handleExecutionAction(execution.id, 'cancel');
                          }
                        }}
                        icon={<Square className="w-4 h-4" />}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </div>

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
            );
          })}
        </div>
      )}
    </div>
  );
};
