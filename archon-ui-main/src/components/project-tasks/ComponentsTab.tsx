import React, { useState, useEffect } from 'react';
import { Plus, Package, AlertCircle, Settings, Layers, GitBranch, FileText } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { TemplateManagement } from './TemplateManagement';
import type { Project } from '../../types/project';

interface ComponentsTabProps {
  project: Project;
  className?: string;
}

// Mock component data for demonstration
const mockComponents = [
  {
    id: '1',
    name: 'Authentication Service',
    type: 'foundation',
    status: 'completed',
    description: 'Core authentication and authorization system',
    dependencies: [],
    completion_gates: ['architecture', 'implementation', 'testing']
  },
  {
    id: '2',
    name: 'User Management API',
    type: 'feature',
    status: 'in_progress',
    description: 'REST API for user CRUD operations',
    dependencies: ['1'],
    completion_gates: ['design', 'implementation']
  },
  {
    id: '3',
    name: 'Frontend Dashboard',
    type: 'integration',
    status: 'not_started',
    description: 'React-based admin dashboard',
    dependencies: ['1', '2'],
    completion_gates: ['design']
  }
];

export const ComponentsTab: React.FC<ComponentsTabProps> = ({
  project,
  className = ''
}) => {
  const [selectedComponent, setSelectedComponent] = useState<any>(null);
  const [activeView, setActiveView] = useState<'hierarchy' | 'graph'>('hierarchy');
  const [error, setError] = useState<string | null>(null);

  // Add error handling for template management
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      if (event.error && event.error.message) {
        console.error('ComponentsTab error:', event.error);
        setError(`Template system error: ${event.error.message}`);
      }
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);
  const [activeTab, setActiveTab] = useState<'components' | 'templates'>('templates');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'in_progress': return 'blue';
      case 'not_started': return 'gray';
      case 'blocked': return 'red';
      default: return 'gray';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'foundation': return <Layers className="h-4 w-4" />;
      case 'feature': return <Package className="h-4 w-4" />;
      case 'integration': return <GitBranch className="h-4 w-4" />;
      case 'infrastructure': return <Settings className="h-4 w-4" />;
      default: return <Package className="h-4 w-4" />;
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Package className="h-6 w-6 text-purple-500" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Component Management
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Manage project components, dependencies, and architecture
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* View Toggle */}
          <div className="flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setActiveView('hierarchy')}
              className={`px-3 py-1 text-sm rounded-md transition-all ${
                activeView === 'hierarchy'
                  ? 'bg-white dark:bg-gray-700 text-purple-600 dark:text-purple-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              Hierarchy
            </button>
            <button
              onClick={() => setActiveView('graph')}
              className={`px-3 py-1 text-sm rounded-md transition-all ${
                activeView === 'graph'
                  ? 'bg-white dark:bg-gray-700 text-purple-600 dark:text-purple-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              Graph
            </button>
          </div>
          
          {/* Create Component Button */}
          <Button
            onClick={() => alert('Create component functionality coming soon!')}
            variant="primary"
            accentColor="purple"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            New Component
          </Button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('templates')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'templates'
                ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Template Management
            </div>
          </button>
          <button
            onClick={() => setActiveTab('components')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'components'
                ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4" />
              Component Hierarchy
            </div>
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'templates' ? (
        <div className="mt-6">
          {error ? (
            <Card className="p-6" accentColor="red">
              <div className="text-center">
                <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                  Template Management Error
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {error}
                </p>
                <Button
                  onClick={() => setError(null)}
                  variant="outline"
                  size="sm"
                >
                  Try Again
                </Button>
              </div>
            </Card>
          ) : (
            {/* Temporarily disabled TemplateManagement for debugging */}
            <Card className="p-8 text-center">
              <Layers className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                Template Management Temporarily Disabled
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Template management is temporarily disabled for debugging. This will be restored shortly.
              </p>
              <Button
                onClick={() => window.location.reload()}
                variant="outline"
                size="sm"
              >
                Refresh Page
              </Button>
            </Card>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Original Components Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Component List/Graph */}
        <div className="lg:col-span-2">
          {activeView === 'hierarchy' ? (
            <Card className="h-full" accentColor="purple">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Component Hierarchy
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {mockComponents.length} component{mockComponents.length !== 1 ? 's' : ''} in project
                </p>
              </div>

              <div className="p-4 space-y-3">
                {mockComponents.map((component) => (
                  <div
                    key={component.id}
                    onClick={() => setSelectedComponent(component)}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedComponent?.id === component.id
                        ? 'border-purple-300 bg-purple-50 dark:border-purple-600 dark:bg-purple-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-purple-500">
                          {getTypeIcon(component.type)}
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-gray-100">
                            {component.name}
                          </h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {component.description}
                          </p>
                        </div>
                      </div>
                      <Badge color={getStatusColor(component.status)} size="sm">
                        {component.status.replace('_', ' ')}
                      </Badge>
                    </div>

                    {component.dependencies.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800">
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Depends on: {component.dependencies.length} component{component.dependencies.length !== 1 ? 's' : ''}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          ) : (
            <Card className="h-full" accentColor="purple">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Dependency Graph
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Visual representation of component dependencies
                </p>
              </div>

              <div className="p-8 flex items-center justify-center h-64">
                <div className="text-center">
                  <GitBranch className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Dependency graph visualization coming soon
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                    Interactive SVG graph with pan/zoom controls
                  </p>
                </div>
              </div>
            </Card>
          )}
        </div>

        {/* Right Panel - Component Details */}
        <div className="lg:col-span-1">
          {selectedComponent ? (
            <Card className="h-full" accentColor="purple">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Component Details
                  </h4>
                  <Button
                    onClick={() => alert('Edit functionality coming soon!')}
                    variant="outline"
                    size="sm"
                  >
                    Edit
                  </Button>
                </div>
              </div>

              <div className="p-4 space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
                  <p className="text-gray-900 dark:text-gray-100 font-medium">{selectedComponent.name}</p>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Type</label>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="text-purple-500">
                      {getTypeIcon(selectedComponent.type)}
                    </div>
                    <p className="text-gray-900 dark:text-gray-100 capitalize">{selectedComponent.type}</p>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Status</label>
                  <div className="mt-1">
                    <Badge color={getStatusColor(selectedComponent.status)} size="sm">
                      {selectedComponent.status.replace('_', ' ')}
                    </Badge>
                  </div>
                </div>

                {selectedComponent.description && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
                    <p className="text-gray-900 dark:text-gray-100 text-sm mt-1">{selectedComponent.description}</p>
                  </div>
                )}

                {selectedComponent.dependencies.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Dependencies</label>
                    <p className="text-gray-900 dark:text-gray-100 text-sm mt-1">
                      {selectedComponent.dependencies.length} component{selectedComponent.dependencies.length !== 1 ? 's' : ''}
                    </p>
                    <div className="mt-2 space-y-1">
                      {selectedComponent.dependencies.map((depId: string) => {
                        const dep = mockComponents.find(c => c.id === depId);
                        return dep ? (
                          <div key={depId} className="text-xs text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                            {dep.name}
                          </div>
                        ) : null;
                      })}
                    </div>
                  </div>
                )}

                {selectedComponent.completion_gates.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Completion Gates</label>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {selectedComponent.completion_gates.map((gate: string) => (
                        <span
                          key={gate}
                          className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded"
                        >
                          {gate}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          ) : (
            <Card className="h-full" accentColor="none">
              <div className="p-8 text-center">
                <Package className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 dark:text-gray-400">
                  Select a component to view details
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                  Click on any component in the hierarchy to see its information
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>

          {/* Coming Soon Notice */}
          <Card className="mt-6" accentColor="blue">
        <div className="p-4">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-blue-500" />
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100">
                Component Management System
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                This is a preview of the component management interface. Full functionality including create, edit,
                dependency management, and real-time synchronization will be available soon.
              </p>
            </div>
          </div>
        </div>
      </Card>
        </div>
      )}
    </div>
  );
};

// Error Boundary for TemplateManagement
class TemplateManagementErrorBoundary extends React.Component<
  {
    children: React.ReactNode;
    onError: (error: string) => void;
  },
  { hasError: boolean }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('TemplateManagement Error Boundary caught error:', error, errorInfo);
    this.props.onError(`Template management error: ${error.message}`);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Card className="p-6" accentColor="red">
          <div className="text-center">
            <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Template Management Unavailable
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              The template management system is currently unavailable. This may be due to missing backend services.
            </p>
            <Button
              onClick={() => {
                this.setState({ hasError: false });
                window.location.reload();
              }}
              variant="outline"
              size="sm"
            >
              Reload Page
            </Button>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}

// Safe wrapper for TemplateManagement to catch errors
const SafeTemplateManagement: React.FC<{
  projectId: string;
  onError: (error: string) => void;
  onTemplateSelect?: (template: any) => void;
  onComponentSelect?: (component: any) => void;
  onAssignmentSelect?: (assignment: any) => void;
}> = ({ projectId, onError, onTemplateSelect, onComponentSelect, onAssignmentSelect }) => {
  return (
    <TemplateManagementErrorBoundary onError={onError}>
      <TemplateManagement
        projectId={projectId}
        onTemplateSelect={onTemplateSelect}
        onComponentSelect={onComponentSelect}
        onAssignmentSelect={onAssignmentSelect}
      />
    </TemplateManagementErrorBoundary>
  );
};
