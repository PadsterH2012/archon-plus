import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Workflow, Activity, Plus, History, GitBranch, Users, Clock, BarChart3 } from 'lucide-react';
import { WorkflowBuilder } from '../components/workflow/WorkflowBuilder';
import { WorkflowExecutionDashboard } from '../components/workflow/WorkflowExecutionDashboard';
import { WorkflowAnalytics } from '../components/workflow/WorkflowAnalytics';
import { WorkflowScheduler } from '../components/workflow/WorkflowScheduler';

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

          <div className="grid gap-4">
            {workflows.map((workflow) => (
              <div key={workflow.id} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {workflow.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {workflow.description}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-xs rounded">
                        {workflow.category}
                      </span>
                      <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs rounded">
                        {workflow.status}
                      </span>
                    </div>
                  </div>
                  {/* Action buttons removed per user preference for minimal workflow UI */}
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
        <Route path="builder" element={<WorkflowBuilder />} />
        <Route path="executions" element={<WorkflowExecutionDashboard />} />
        <Route path="analytics" element={<WorkflowAnalytics />} />
        <Route path="scheduler" element={<WorkflowScheduler />} />
        <Route path="catalog" element={<SimpleWorkflowDashboard />} />
        <Route path="*" element={<Navigate to="/workflows" replace />} />
      </Routes>
    </div>
  );
};
