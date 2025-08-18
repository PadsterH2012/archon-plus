/**
 * WorkflowManagementPage Component
 * 
 * Main page component for workflow management
 * Integrates workflow list, execution dashboard, and detail views
 */

import React, { useState, useCallback } from 'react';
import { 
  Workflow, 
  Activity, 
  Plus, 
  ArrowLeft,
  Settings,
  BookOpen,
  Zap
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Tabs } from '../ui/Tabs';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import { WorkflowList } from './WorkflowList';
import { WorkflowExecutionDashboard } from './WorkflowExecutionDashboard';
import { WorkflowExecutionMonitor } from './WorkflowExecutionMonitor';
import { WorkflowBuilder } from './WorkflowBuilder';
import { 
  WorkflowTemplate, 
  WorkflowExecution,
  StepExecution
} from './types/workflow.types';

type ViewMode = 'list' | 'executions' | 'execution-detail' | 'workflow-detail' | 'workflow-builder';

export const WorkflowManagementPage: React.FC = () => {
  // State management
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowTemplate | null>(null);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecution | null>(null);
  const [selectedStepExecutions, setSelectedStepExecutions] = useState<StepExecution[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const { showToast } = useToast();

  // Handle workflow selection
  const handleWorkflowSelect = useCallback((workflow: WorkflowTemplate) => {
    setSelectedWorkflow(workflow);
    setViewMode('workflow-detail');
  }, []);

  // Handle workflow edit
  const handleWorkflowEdit = useCallback((workflow?: WorkflowTemplate) => {
    setSelectedWorkflow(workflow || null);
    setViewMode('workflow-builder');
  }, []);

  // Handle workflow execution
  const handleWorkflowExecute = useCallback(async (workflowId: string) => {
    try {
      setIsLoading(true);
      
      // For now, execute with empty parameters
      // In a real implementation, you'd show a parameter input dialog
      const response = await workflowService.executeWorkflow(workflowId, {});
      
      showToast('Workflow execution started', 'success');
      
      // Switch to executions view to see the new execution
      setViewMode('executions');
      
    } catch (error) {
      console.error('Failed to execute workflow:', error);
      showToast('Failed to execute workflow', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [showToast]);

  // Handle execution selection
  const handleExecutionSelect = useCallback(async (execution: WorkflowExecution) => {
    try {
      setIsLoading(true);
      
      // Get detailed execution information
      const response = await workflowService.getExecutionStatus(execution.id);
      setSelectedExecution(response.execution);
      setSelectedStepExecutions(response.step_executions);
      setViewMode('execution-detail');
      
    } catch (error) {
      console.error('Failed to get execution details:', error);
      showToast('Failed to load execution details', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [showToast]);

  // Handle back navigation
  const handleBack = useCallback(() => {
    switch (viewMode) {
      case 'workflow-detail':
      case 'workflow-builder':
        setViewMode('list');
        setSelectedWorkflow(null);
        break;
      case 'execution-detail':
        setViewMode('executions');
        setSelectedExecution(null);
        setSelectedStepExecutions([]);
        break;
      default:
        setViewMode('list');
    }
  }, [viewMode]);

  // Handle workflow save
  const handleWorkflowSave = useCallback(async (workflowData: Partial<WorkflowTemplate>) => {
    try {
      setIsLoading(true);
      
      if (selectedWorkflow) {
        // Update existing workflow
        await workflowService.updateWorkflow(selectedWorkflow.id, workflowData);
        showToast('Workflow updated successfully', 'success');
      } else {
        // Create new workflow
        await workflowService.createWorkflow(workflowData);
        showToast('Workflow created successfully', 'success');
      }
      
      setViewMode('list');
      setSelectedWorkflow(null);
      
    } catch (error) {
      console.error('Failed to save workflow:', error);
      showToast('Failed to save workflow', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [selectedWorkflow, showToast]);

  // Handle workflow delete
  const handleWorkflowDelete = useCallback(async (workflowId: string) => {
    try {
      await workflowService.deleteWorkflow(workflowId);
      showToast('Workflow deleted successfully', 'success');
    } catch (error) {
      console.error('Failed to delete workflow:', error);
      showToast('Failed to delete workflow', 'error');
    }
  }, [showToast]);

  // Render header based on view mode
  const renderHeader = () => {
    switch (viewMode) {
      case 'workflow-detail':
        return (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBack}
                icon={<ArrowLeft className="w-4 h-4" />}
              >
                Back
              </Button>
              <Workflow className="w-8 h-8 text-purple-500" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {selectedWorkflow?.title}
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Workflow Details
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleWorkflowEdit(selectedWorkflow!)}
                icon={<Settings className="w-4 h-4" />}
              >
                Edit
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleWorkflowExecute(selectedWorkflow!.id)}
                icon={<Zap className="w-4 h-4" />}
                accentColor="purple"
                disabled={isLoading}
              >
                Execute
              </Button>
            </div>
          </div>
        );

      case 'workflow-builder':
        return null; // Builder has its own header

      case 'execution-detail':
        return (
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBack}
              icon={<ArrowLeft className="w-4 h-4" />}
            >
              Back to Dashboard
            </Button>
            <Activity className="w-8 h-8 text-blue-500" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Execution Monitor
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Real-time execution monitoring
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // Render main content based on view mode
  const renderContent = () => {
    switch (viewMode) {
      case 'list':
        return (
          <WorkflowList
            onWorkflowSelect={handleWorkflowSelect}
            onWorkflowEdit={handleWorkflowEdit}
            onWorkflowDelete={handleWorkflowDelete}
            onWorkflowExecute={handleWorkflowExecute}
          />
        );

      case 'executions':
        return (
          <WorkflowExecutionDashboard
            onExecutionSelect={handleExecutionSelect}
          />
        );

      case 'execution-detail':
        return selectedExecution ? (
          <WorkflowExecutionMonitor
            execution={selectedExecution}
            stepExecutions={selectedStepExecutions}
          />
        ) : (
          <div className="flex items-center justify-center py-12">
            <p className="text-gray-500">No execution selected</p>
          </div>
        );

      case 'workflow-detail':
        return selectedWorkflow ? (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Workflow Information</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Name:</span>
                  <p className="font-medium">{selectedWorkflow.name}</p>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Category:</span>
                  <p className="font-medium">{selectedWorkflow.category}</p>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Status:</span>
                  <p className="font-medium">{selectedWorkflow.status}</p>
                </div>
                <div>
                  <span className="text-gray-600 dark:text-gray-400">Version:</span>
                  <p className="font-medium">{selectedWorkflow.version}</p>
                </div>
              </div>
              <div className="mt-4">
                <span className="text-gray-600 dark:text-gray-400">Description:</span>
                <p className="mt-1">{selectedWorkflow.description}</p>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Steps ({selectedWorkflow.steps.length})</h3>
              <div className="space-y-3">
                {selectedWorkflow.steps.map((step, index) => (
                  <div key={index} className="border border-gray-200 dark:border-gray-700 rounded p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">{step.title}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {step.type} {step.tool_name && `• ${step.tool_name}`}
                        </p>
                      </div>
                      <span className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                        Step {index + 1}
                      </span>
                    </div>
                    {step.description && (
                      <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                        {step.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center py-12">
            <p className="text-gray-500">No workflow selected</p>
          </div>
        );

      case 'workflow-builder':
        return (
          <WorkflowBuilder
            workflow={selectedWorkflow || undefined}
            onSave={handleWorkflowSave}
            onCancel={handleBack}
            onPreview={(workflow) => {
              // Handle workflow preview
              console.log('Preview workflow:', workflow);
            }}
            onTest={(workflow) => {
              // Handle workflow test
              console.log('Test workflow:', workflow);
            }}
            isLoading={isLoading}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        {(viewMode === 'list' || viewMode === 'executions') && (
          <div className="mb-8">
            <Tabs
              tabs={[
                {
                  id: 'workflows',
                  label: 'Workflows',
                  icon: <Workflow className="w-4 h-4" />,
                  active: viewMode === 'list'
                },
                {
                  id: 'executions',
                  label: 'Executions',
                  icon: <Activity className="w-4 h-4" />,
                  active: viewMode === 'executions'
                }
              ]}
              onTabChange={(tabId) => setViewMode(tabId as ViewMode)}
              accentColor="purple"
            />
          </div>
        )}

        {/* Header */}
        {renderHeader() && (
          <div className="mb-8">
            {renderHeader()}
          </div>
        )}

        {/* Main Content */}
        {renderContent()}
      </div>
    </div>
  );
};
