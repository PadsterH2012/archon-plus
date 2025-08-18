/**
 * WorkflowAnalytics Component
 * 
 * Comprehensive analytics dashboard for workflow performance and insights
 */

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Activity,
  Users,
  Calendar,
  Zap
} from 'lucide-react';
import { Card } from '../ui/Card';

interface WorkflowAnalyticsProps {
  className?: string;
}

interface AnalyticsData {
  totalExecutions: number;
  successfulExecutions: number;
  failedExecutions: number;
  averageExecutionTime: number;
  totalWorkflows: number;
  activeWorkflows: number;
  topWorkflows: Array<{
    id: string;
    title: string;
    executions: number;
    successRate: number;
  }>;
  executionTrends: Array<{
    date: string;
    executions: number;
    success: number;
    failed: number;
  }>;
}

export const WorkflowAnalytics: React.FC<WorkflowAnalyticsProps> = ({ className = '' }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  useEffect(() => {
    // Simulate analytics data - in real implementation, this would fetch from API
    const mockAnalytics: AnalyticsData = {
      totalExecutions: 1247,
      successfulExecutions: 1156,
      failedExecutions: 91,
      averageExecutionTime: 45.2,
      totalWorkflows: 23,
      activeWorkflows: 18,
      topWorkflows: [
        { id: '1', title: 'System Health Check', executions: 342, successRate: 98.5 },
        { id: '2', title: 'Project Analysis', executions: 189, successRate: 94.2 },
        { id: '3', title: 'Data Backup', executions: 156, successRate: 99.1 },
        { id: '4', title: 'Security Scan', executions: 134, successRate: 87.3 },
        { id: '5', title: 'Performance Test', executions: 98, successRate: 91.8 }
      ],
      executionTrends: [
        { date: '2025-08-11', executions: 45, success: 42, failed: 3 },
        { date: '2025-08-12', executions: 52, success: 48, failed: 4 },
        { date: '2025-08-13', executions: 38, success: 36, failed: 2 },
        { date: '2025-08-14', executions: 61, success: 57, failed: 4 },
        { date: '2025-08-15', executions: 49, success: 45, failed: 4 },
        { date: '2025-08-16', executions: 55, success: 52, failed: 3 },
        { date: '2025-08-17', executions: 43, success: 41, failed: 2 },
        { date: '2025-08-18', executions: 67, success: 63, failed: 4 }
      ]
    };

    setTimeout(() => {
      setAnalytics(mockAnalytics);
      setLoading(false);
    }, 1000);
  }, [timeRange]);

  if (loading) {
    return (
      <div className={`p-6 ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className={`p-6 ${className}`}>
        <div className="text-center py-12">
          <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Unable to load analytics data</p>
        </div>
      </div>
    );
  }

  const successRate = (analytics.successfulExecutions / analytics.totalExecutions) * 100;

  return (
    <div className={`p-6 space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BarChart3 className="h-8 w-8 text-blue-500" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Workflow Analytics
          </h1>
        </div>
        <div className="flex gap-2">
          {(['7d', '30d', '90d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 text-sm rounded ${
                timeRange === range
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              } transition-colors`}
            >
              {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Executions</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.totalExecutions.toLocaleString()}</p>
            </div>
            <Activity className="h-8 w-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Success Rate</p>
              <p className="text-2xl font-bold text-green-600">{successRate.toFixed(1)}%</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg. Execution Time</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.averageExecutionTime}s</p>
            </div>
            <Clock className="h-8 w-8 text-orange-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Workflows</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{analytics.activeWorkflows}/{analytics.totalWorkflows}</p>
            </div>
            <Zap className="h-8 w-8 text-purple-500" />
          </div>
        </Card>
      </div>

      {/* Top Workflows */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Top Performing Workflows
        </h2>
        <div className="space-y-4">
          {analytics.topWorkflows.map((workflow, index) => (
            <div key={workflow.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-500 text-white text-sm font-bold rounded">
                  {index + 1}
                </span>
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">{workflow.title}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {workflow.executions} executions
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-green-600">{workflow.successRate}%</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">success rate</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Execution Trends */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Execution Trends
        </h2>
        <div className="space-y-2">
          {analytics.executionTrends.map((trend) => (
            <div key={trend.date} className="flex items-center justify-between p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {new Date(trend.date).toLocaleDateString()}
              </span>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-900 dark:text-white">
                  {trend.executions} total
                </span>
                <span className="text-sm text-green-600">
                  {trend.success} success
                </span>
                <span className="text-sm text-red-600">
                  {trend.failed} failed
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
