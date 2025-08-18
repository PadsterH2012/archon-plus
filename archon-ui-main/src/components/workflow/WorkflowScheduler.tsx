/**
 * WorkflowScheduler Component
 * 
 * Advanced workflow scheduling interface with cron expressions and triggers
 */

import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Calendar, 
  Play, 
  Pause, 
  Trash2, 
  Plus, 
  Edit, 
  AlertCircle,
  CheckCircle,
  Zap,
  GitBranch
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

interface ScheduledWorkflow {
  id: string;
  workflow_id: string;
  workflow_title: string;
  schedule_type: 'cron' | 'interval' | 'webhook' | 'event';
  cron_expression?: string;
  interval_minutes?: number;
  webhook_url?: string;
  event_type?: string;
  enabled: boolean;
  next_execution?: string;
  last_execution?: string;
  execution_count: number;
  created_at: string;
  created_by: string;
}

interface WorkflowSchedulerProps {
  className?: string;
}

export const WorkflowScheduler: React.FC<WorkflowSchedulerProps> = ({ className = '' }) => {
  const [schedules, setSchedules] = useState<ScheduledWorkflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    // Simulate scheduled workflows data
    const mockSchedules: ScheduledWorkflow[] = [
      {
        id: 'sched-1',
        workflow_id: 'wf-1',
        workflow_title: 'System Health Check',
        schedule_type: 'cron',
        cron_expression: '0 */6 * * *',
        enabled: true,
        next_execution: '2025-08-18T20:00:00Z',
        last_execution: '2025-08-18T14:00:00Z',
        execution_count: 342,
        created_at: '2025-08-01T10:00:00Z',
        created_by: 'admin'
      },
      {
        id: 'sched-2',
        workflow_id: 'wf-2',
        workflow_title: 'Data Backup',
        schedule_type: 'cron',
        cron_expression: '0 2 * * *',
        enabled: true,
        next_execution: '2025-08-19T02:00:00Z',
        last_execution: '2025-08-18T02:00:00Z',
        execution_count: 18,
        created_at: '2025-08-01T15:30:00Z',
        created_by: 'admin'
      },
      {
        id: 'sched-3',
        workflow_id: 'wf-3',
        workflow_title: 'Performance Monitoring',
        schedule_type: 'interval',
        interval_minutes: 15,
        enabled: false,
        next_execution: undefined,
        last_execution: '2025-08-18T13:45:00Z',
        execution_count: 1247,
        created_at: '2025-07-15T09:00:00Z',
        created_by: 'devops'
      },
      {
        id: 'sched-4',
        workflow_id: 'wf-4',
        workflow_title: 'Security Scan',
        schedule_type: 'webhook',
        webhook_url: 'https://api.example.com/webhook/security-scan',
        enabled: true,
        execution_count: 89,
        created_at: '2025-08-10T14:20:00Z',
        created_by: 'security'
      }
    ];

    setTimeout(() => {
      setSchedules(mockSchedules);
      setLoading(false);
    }, 800);
  }, []);

  const toggleSchedule = (scheduleId: string) => {
    setSchedules(prev => prev.map(schedule => 
      schedule.id === scheduleId 
        ? { ...schedule, enabled: !schedule.enabled }
        : schedule
    ));
  };

  const deleteSchedule = (scheduleId: string) => {
    if (confirm('Are you sure you want to delete this schedule?')) {
      setSchedules(prev => prev.filter(schedule => schedule.id !== scheduleId));
    }
  };

  const getScheduleDescription = (schedule: ScheduledWorkflow) => {
    switch (schedule.schedule_type) {
      case 'cron':
        return `Cron: ${schedule.cron_expression}`;
      case 'interval':
        return `Every ${schedule.interval_minutes} minutes`;
      case 'webhook':
        return 'Webhook trigger';
      case 'event':
        return `Event: ${schedule.event_type}`;
      default:
        return 'Unknown schedule type';
    }
  };

  const getScheduleTypeColor = (type: string) => {
    switch (type) {
      case 'cron': return 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400';
      case 'interval': return 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400';
      case 'webhook': return 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400';
      case 'event': return 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400';
      default: return 'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className={`p-6 ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading schedules...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`p-6 space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Clock className="h-8 w-8 text-orange-500" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Workflow Scheduler
          </h1>
        </div>
        <Button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Create Schedule
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Schedules</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{schedules.length}</p>
            </div>
            <Calendar className="h-6 w-6 text-blue-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
              <p className="text-2xl font-bold text-green-600">{schedules.filter(s => s.enabled).length}</p>
            </div>
            <CheckCircle className="h-6 w-6 text-green-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Paused</p>
              <p className="text-2xl font-bold text-orange-600">{schedules.filter(s => !s.enabled).length}</p>
            </div>
            <Pause className="h-6 w-6 text-orange-500" />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Executions</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {schedules.reduce((sum, s) => sum + s.execution_count, 0).toLocaleString()}
              </p>
            </div>
            <Zap className="h-6 w-6 text-purple-500" />
          </div>
        </Card>
      </div>

      {/* Schedules List */}
      <div className="space-y-4">
        {schedules.map((schedule) => (
          <Card key={schedule.id} className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {schedule.workflow_title}
                  </h3>
                  <Badge className={getScheduleTypeColor(schedule.schedule_type)}>
                    {schedule.schedule_type}
                  </Badge>
                  <Badge className={schedule.enabled ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400'}>
                    {schedule.enabled ? 'Active' : 'Paused'}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {getScheduleDescription(schedule)}
                </p>
                <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-500">
                  <span>Executions: {schedule.execution_count}</span>
                  {schedule.next_execution && (
                    <span>Next: {new Date(schedule.next_execution).toLocaleString()}</span>
                  )}
                  {schedule.last_execution && (
                    <span>Last: {new Date(schedule.last_execution).toLocaleString()}</span>
                  )}
                  <span>Created by: {schedule.created_by}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => toggleSchedule(schedule.id)}
                  className="flex items-center gap-1"
                >
                  {schedule.enabled ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                  {schedule.enabled ? 'Pause' : 'Resume'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => alert(`Edit schedule for ${schedule.workflow_title}\n\nComing soon: Edit schedule configuration, cron expressions, and trigger settings.`)}
                  className="flex items-center gap-1"
                >
                  <Edit className="h-3 w-3" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => deleteSchedule(schedule.id)}
                  className="flex items-center gap-1 text-red-600 hover:text-red-700"
                >
                  <Trash2 className="h-3 w-3" />
                  Delete
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Create Schedule Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 max-w-full mx-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Create Schedule
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Advanced workflow scheduling is coming soon! Features will include:
              <br />• Cron expression scheduling
              <br />• Interval-based execution
              <br />• Webhook triggers
              <br />• Event-driven workflows
              <br />• Conditional execution logic
            </p>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setShowCreateForm(false)}
                className="flex-1"
              >
                Close
              </Button>
              <Button
                onClick={() => {
                  alert('Schedule creation will be available in the next update!');
                  setShowCreateForm(false);
                }}
                className="flex-1"
              >
                Coming Soon
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
