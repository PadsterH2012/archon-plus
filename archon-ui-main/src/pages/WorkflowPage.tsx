import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Workflow, Activity, Plus, History, GitBranch, Users, Clock, BarChart3, Edit, Copy, Trash2, Info, X } from 'lucide-react';
import { WorkflowBuilder } from '../components/workflow/WorkflowBuilder';
import { WorkflowExecutionDashboard } from '../components/workflow/WorkflowExecutionDashboard';
import { WorkflowAnalytics } from '../components/workflow/WorkflowAnalytics';
import { WorkflowScheduler } from '../components/workflow/WorkflowScheduler';
import { workflowService } from '../services/workflowService';

// Wrapper component for WorkflowBuilder that handles route state
const WorkflowBuilderWrapper: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const workflow = location.state?.workflow;
  const initialTab = location.state?.tab || 'metadata';

  const handleSave = async (workflowData: any) => {
    try {
      if (workflow?.id) {
        // Update existing workflow
        await workflowService.updateWorkflow(workflow.id, workflowData);
        alert('✅ Workflow updated successfully!');
      } else {
        // Create new workflow
        await workflowService.createWorkflow(workflowData);
        alert('✅ Workflow created successfully!');
      }
      navigate('/workflows');
    } catch (error) {
      alert(`❌ Error saving workflow: ${error}`);
    }
  };

  const handleCancel = () => {
    navigate('/workflows');
  };

  return (
    <WorkflowBuilder
      workflow={workflow}
      initialTab={initialTab as any}
      onSave={handleSave}
      onCancel={handleCancel}
    />
  );
};

// Enhanced workflow dashboard with navigation to advanced features
const SimpleWorkflowDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [executing, setExecuting] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [recentExecutions, setRecentExecutions] = useState<any[]>([]);
  const [showMCPWorkflowForm, setShowMCPWorkflowForm] = useState(false);
  const [selectedWorkflowInfo, setSelectedWorkflowInfo] = useState<any>(null);

  useEffect(() => {
    // Test API connection
    fetch('/api/workflows')
      .then(response => response.json())
      .then(data => {
        setWorkflows(data.workflows || []);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const executeWorkflow = async (workflowId: string) => {
    setExecuting(workflowId);
    try {
      const response = await fetch(`/api/workflows/${workflowId}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_template_id: workflowId,
          parameters: {},
          triggered_by: 'user'
        })
      });

      if (response.ok) {
        const result = await response.json();

        // Add to recent executions
        const execution = {
          id: result.execution_id,
          workflow_id: workflowId,
          workflow_title: workflows.find(w => w.id === workflowId)?.title || 'Unknown',
          status: result.status,
          started_at: new Date().toISOString(),
          message: result.message
        };
        setRecentExecutions(prev => [execution, ...prev.slice(0, 4)]); // Keep last 5

        alert(`✅ Workflow execution started successfully!\n\n📋 Execution ID: ${result.execution_id}\n📊 Status: ${result.status}\n🔄 Message: ${result.message}`);
      } else {
        const error = await response.text();
        alert(`Execution failed: ${error}`);
      }
    } catch (err) {
      alert(`Execution error: ${err}`);
    } finally {
      setExecuting(null);
    }
  };

  const createMCPWorkflow = async (workflowData: any) => {
    try {
      const response = await fetch('/api/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowData)
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ MCP Workflow created successfully!\n\n📋 Workflow ID: ${result.id}\n📝 Title: ${result.title}`);
        // Refresh workflows list
        window.location.reload();
      } else {
        const error = await response.text();
        alert(`❌ Failed to create workflow: ${error}`);
      }
    } catch (err) {
      alert(`❌ Error creating workflow: ${err}`);
    }
  };

  // Handler functions for workflow actions
  const handleEditWorkflow = async (workflow: any) => {
    try {
      // Navigate to the builder with the workflow (metadata tab)
      navigate('/workflows/builder', { state: { workflow, tab: 'metadata' } });
    } catch (error) {
      alert(`❌ Error opening workflow editor: ${error}`);
    }
  };

  const handleDesignWorkflow = async (workflow: any) => {
    try {
      // Navigate to the builder with the workflow (designer tab)
      navigate('/workflows/builder', { state: { workflow, tab: 'designer' } });
    } catch (error) {
      alert(`❌ Error opening workflow designer: ${error}`);
    }
  };

  const handleCloneWorkflow = async (workflow: any) => {
    try {
      const newTitle = `${workflow.title} (Copy)`;
      const newName = `${workflow.name}_copy_${Date.now()}`;

      const result = await workflowService.cloneWorkflow(workflow.id, newName, newTitle);
      alert(`✅ Workflow cloned successfully!\n\n📋 New Workflow: ${result.cloned_workflow.title}`);

      // Refresh the workflows list
      window.location.reload();
    } catch (error) {
      alert(`❌ Error cloning workflow: ${error}`);
    }
  };

  const handleDeleteWorkflow = async (workflow: any) => {
    if (!confirm(`⚠️ Are you sure you want to delete "${workflow.title}"?\n\nThis action cannot be undone.`)) {
      return;
    }

    try {
      await workflowService.deleteWorkflow(workflow.id);
      alert(`✅ Workflow "${workflow.title}" deleted successfully!`);

      // Refresh the workflows list
      window.location.reload();
    } catch (error) {
      alert(`❌ Error deleting workflow: ${error}`);
    }
  };

  const handleShowWorkflowInfo = (workflow: any) => {
    setSelectedWorkflowInfo(workflow);
  };

  const handleCloseWorkflowInfo = () => {
    setSelectedWorkflowInfo(null);
  };

  return (
    <div className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <Workflow className="h-8 w-8 text-blue-500" />
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Workflow Management
        </h1>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading workflows...</span>
        </div>
      )}

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6">
          <p className="text-red-600 dark:text-red-400">Error loading workflows: {error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-gray-600 dark:text-gray-400">
              Found {workflows.length} workflows
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
              <button
                onClick={() => navigate('/workflows/builder')}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <Plus className="h-4 w-4" />
                Visual Designer
              </button>
              <button
                onClick={() => navigate('/workflows/executions')}
                className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                <Activity className="h-4 w-4" />
                Execution Monitor
              </button>
              <button
                onClick={() => setShowMCPWorkflowForm(true)}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
              >
                <Plus className="h-4 w-4" />
                MCP Workflow
              </button>
              <button
                onClick={() => navigate('/workflows/scheduler')}
                className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
              >
                <Clock className="h-4 w-4" />
                Scheduler
              </button>
              <button
                onClick={() => navigate('/workflows/analytics')}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors"
              >
                <BarChart3 className="h-4 w-4" />
                Analytics
              </button>
              <button
                onClick={() => setShowCreateForm(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                <Plus className="h-4 w-4" />
                API Docs
              </button>
            </div>
          </div>

          <div className="grid gap-6">
            {workflows.map((workflow) => (
              <div key={workflow.id} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                {/* Top section: Title and Info Icon */}
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white leading-tight">
                    {workflow.title}
                  </h3>
                  <button
                    onClick={() => handleShowWorkflowInfo(workflow)}
                    className="flex items-center justify-center w-6 h-6 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                    title="View workflow details"
                  >
                    <Info className="w-4 h-4" />
                  </button>
                </div>

                {/* Middle section: Status Badge */}
                <div className="mb-4">
                  <span className="inline-flex items-center px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-medium rounded-full">
                    {workflow.status}
                  </span>
                </div>

                {/* Bottom section: Action Buttons */}
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleEditWorkflow(workflow)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </button>
                  <button
                    onClick={() => handleDesignWorkflow(workflow)}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white text-sm font-medium rounded-lg hover:bg-purple-600 transition-colors"
                  >
                    <GitBranch className="w-4 h-4" />
                    Designer
                  </button>
                  <button
                    onClick={() => handleCloneWorkflow(workflow)}
                    className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white text-sm font-medium rounded-lg hover:bg-green-600 transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                    Clone
                  </button>
                  <button
                    onClick={() => handleDeleteWorkflow(workflow)}
                    className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white text-sm font-medium rounded-lg hover:bg-red-600 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Recent Executions */}
          {recentExecutions.length > 0 && (
            <div className="mt-8">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Recent Executions
              </h2>
              <div className="space-y-3">
                {recentExecutions.map((execution) => (
                  <div key={execution.id} className="bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {execution.workflow_title}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          ID: {execution.id}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500">
                          Started: {new Date(execution.started_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 text-xs rounded ${
                          execution.status === 'pending' ? 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400' :
                          execution.status === 'running' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' :
                          execution.status === 'completed' ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' :
                          'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
                        }`}>
                          {execution.status}
                        </span>
                        <button
                          onClick={() => navigate('/workflows/executions')}
                          className="text-blue-500 hover:text-blue-600 text-sm"
                        >
                          Monitor
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Simple Create Workflow Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 max-w-full mx-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Create New Workflow
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              The visual workflow builder is coming soon! For now, you can use the API to create workflows or modify the example workflows.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowCreateForm(false)}
                className="flex-1 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setShowCreateForm(false);
                  window.open('http://localhost:8181/docs', '_blank');
                }}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                View API Docs
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MCP Workflow Creation Modal */}
      {showMCPWorkflowForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-96 max-w-full mx-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Create MCP Workflow
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Workflow Title
                </label>
                <input
                  type="text"
                  id="mcpWorkflowTitle"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="e.g., Knowledge Base Health Check"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  id="mcpWorkflowDescription"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Describe what this workflow does..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  MCP Tools to Include
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm">health_check_archon - System health monitoring</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span className="text-sm">get_available_sources_archon - Knowledge base sources</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm">perform_rag_query_archon - Knowledge search</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span className="text-sm">manage_project_archon - Project management</span>
                  </label>
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowMCPWorkflowForm(false)}
                className="flex-1 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const title = (document.getElementById('mcpWorkflowTitle') as HTMLInputElement)?.value;
                  const description = (document.getElementById('mcpWorkflowDescription') as HTMLTextAreaElement)?.value;

                  if (!title) {
                    alert('Please enter a workflow title');
                    return;
                  }

                  const mcpWorkflow = {
                    title,
                    description: description || 'MCP-powered workflow',
                    category: 'mcp-integration',
                    status: 'active',
                    steps: [
                      {
                        id: 'health-check',
                        name: 'System Health Check',
                        type: 'mcp_tool',
                        tool_name: 'health_check_archon',
                        parameters: {},
                        order: 1
                      },
                      {
                        id: 'get-sources',
                        name: 'Get Knowledge Sources',
                        type: 'mcp_tool',
                        tool_name: 'get_available_sources_archon',
                        parameters: {},
                        order: 2
                      }
                    ],
                    triggers: [],
                    metadata: {
                      created_by: 'user',
                      mcp_integration: true,
                      auto_generated: false
                    }
                  };

                  createMCPWorkflow(mcpWorkflow);
                  setShowMCPWorkflowForm(false);
                }}
                className="flex-1 px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition-colors"
              >
                Create MCP Workflow
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Workflow Info Modal */}
      {selectedWorkflowInfo && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Workflow Details
              </h2>
              <button
                onClick={handleCloseWorkflowInfo}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Basic Information */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                  {selectedWorkflowInfo.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {selectedWorkflowInfo.description || 'No description provided.'}
                </p>
              </div>

              {/* Metadata Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Category</label>
                    <p className="text-gray-900 dark:text-white">{selectedWorkflowInfo.category || 'Uncategorized'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Status</label>
                    <p className="text-gray-900 dark:text-white">
                      <span className="inline-flex items-center px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm rounded-full">
                        {selectedWorkflowInfo.status}
                      </span>
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Created By</label>
                    <p className="text-gray-900 dark:text-white">{selectedWorkflowInfo.created_by || 'Unknown'}</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Step Count</label>
                    <p className="text-gray-900 dark:text-white">{selectedWorkflowInfo.steps?.length || 0} steps</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Version</label>
                    <p className="text-gray-900 dark:text-white">{selectedWorkflowInfo.version || '1.0.0'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Visibility</label>
                    <p className="text-gray-900 dark:text-white">{selectedWorkflowInfo.is_public ? 'Public' : 'Private'}</p>
                  </div>
                </div>
              </div>

              {/* Tags */}
              {selectedWorkflowInfo.tags && selectedWorkflowInfo.tags.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400 block mb-2">Tags</label>
                  <div className="flex flex-wrap gap-2">
                    {selectedWorkflowInfo.tags.map((tag: string, index: number) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Timestamps */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Created</label>
                  <p className="text-gray-900 dark:text-white text-sm">
                    {selectedWorkflowInfo.created_at ? new Date(selectedWorkflowInfo.created_at).toLocaleString() : 'Unknown'}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Last Updated</label>
                  <p className="text-gray-900 dark:text-white text-sm">
                    {selectedWorkflowInfo.updated_at ? new Date(selectedWorkflowInfo.updated_at).toLocaleString() : 'Unknown'}
                  </p>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end p-6 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={handleCloseWorkflowInfo}
                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * WorkflowPage - Main workflow page component with sub-routing
 *
 * This component serves as the main entry point for workflow functionality
 * in the Archon application. It handles sub-routing for different workflow views:
 * - /workflows - Main workflow management dashboard
 * - /workflows/builder - Visual workflow designer
 * - /workflows/executions - Execution monitoring dashboard
 * - /workflows/catalog - Workflow catalog and examples
 */
export const WorkflowPage: React.FC = () => {
  return (
    <div className="workflow-page">
      <Routes>
        <Route index element={<SimpleWorkflowDashboard />} />
        <Route path="builder" element={<WorkflowBuilderWrapper />} />
        <Route path="executions" element={<WorkflowExecutionDashboard />} />
        <Route path="analytics" element={<WorkflowAnalytics />} />
        <Route path="scheduler" element={<WorkflowScheduler />} />
        <Route path="catalog" element={<SimpleWorkflowDashboard />} />
        <Route path="*" element={<Navigate to="/workflows" replace />} />
      </Routes>
    </div>
  );
};
