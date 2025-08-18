import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Workflow, Activity, Plus } from 'lucide-react';

// Simple fallback component while we debug the workflow components
const SimpleWorkflowDashboard: React.FC = () => {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [executing, setExecuting] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

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
            <button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Plus className="h-4 w-4" />
              Create Workflow
            </button>
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
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => executeWorkflow(workflow.id)}
                      disabled={executing === workflow.id}
                      className="flex items-center gap-1 px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {executing === workflow.id ? (
                        <>
                          <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                          Executing...
                        </>
                      ) : (
                        <>
                          <Activity className="h-3 w-3" />
                          Execute
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
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
        <Route path="builder" element={<SimpleWorkflowDashboard />} />
        <Route path="executions" element={<SimpleWorkflowDashboard />} />
        <Route path="catalog" element={<SimpleWorkflowDashboard />} />
        <Route path="*" element={<Navigate to="/workflows" replace />} />
      </Routes>
    </div>
  );
};
