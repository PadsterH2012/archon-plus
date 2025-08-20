import React, { useState } from 'react';
import { Plus, Package } from 'lucide-react';
import { Button } from '../ui/Button';
import { ComponentHierarchy, ComponentForm, DependencyGraph } from '../component-management';
import type { Component } from '../../types/component';
import type { Project } from '../../types/project';

interface ComponentsTabProps {
  project: Project;
  className?: string;
}

export const ComponentsTab: React.FC<ComponentsTabProps> = ({
  project,
  className = ''
}) => {
  const [selectedComponent, setSelectedComponent] = useState<Component | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingComponent, setEditingComponent] = useState<Component | null>(null);
  const [activeView, setActiveView] = useState<'hierarchy' | 'graph'>('hierarchy');

  const handleComponentSelect = (component: Component) => {
    setSelectedComponent(component);
  };

  const handleComponentEdit = (component: Component) => {
    setEditingComponent(component);
    setIsFormOpen(true);
  };

  const handleCreateComponent = () => {
    setEditingComponent(null);
    setIsFormOpen(true);
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingComponent(null);
  };

  const handleFormSave = (component: Component) => {
    // The form will handle the API call, we just need to refresh the view
    // This could trigger a refresh of the ComponentHierarchy
    setSelectedComponent(component);
    handleFormClose();
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
            onClick={handleCreateComponent}
            variant="primary"
            accentColor="purple"
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            New Component
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Component List/Graph */}
        <div className="lg:col-span-2">
          {activeView === 'hierarchy' ? (
            <ComponentHierarchy
              projectId={project.id}
              onComponentSelect={handleComponentSelect}
              onComponentEdit={handleComponentEdit}
              selectedComponentId={selectedComponent?.id}
            />
          ) : (
            <DependencyGraph
              projectId={project.id}
              selectedComponentId={selectedComponent?.id}
              onComponentSelect={handleComponentSelect}
            />
          )}
        </div>

        {/* Right Panel - Component Details */}
        <div className="lg:col-span-1">
          {selectedComponent ? (
            <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Component Details
                </h4>
                <Button
                  onClick={() => handleComponentEdit(selectedComponent)}
                  variant="outline"
                  size="sm"
                >
                  Edit
                </Button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
                  <p className="text-gray-900 dark:text-gray-100">{selectedComponent.name}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Type</label>
                  <p className="text-gray-900 dark:text-gray-100 capitalize">{selectedComponent.component_type}</p>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Status</label>
                  <p className="text-gray-900 dark:text-gray-100 capitalize">{selectedComponent.status.replace('_', ' ')}</p>
                </div>
                
                {selectedComponent.description && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
                    <p className="text-gray-900 dark:text-gray-100 text-sm">{selectedComponent.description}</p>
                  </div>
                )}
                
                {selectedComponent.dependencies.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Dependencies</label>
                    <p className="text-gray-900 dark:text-gray-100 text-sm">{selectedComponent.dependencies.length} component(s)</p>
                  </div>
                )}
                
                {selectedComponent.completion_gates.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Completion Gates</label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedComponent.completion_gates.map(gate => (
                        <span
                          key={gate}
                          className="px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs rounded"
                        >
                          {gate}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700 p-6 text-center">
              <Package className="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 dark:text-gray-400">
                Select a component to view details
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Component Form Modal */}
      <ComponentForm
        projectId={project.id}
        component={editingComponent}
        isOpen={isFormOpen}
        onClose={handleFormClose}
        onSave={handleFormSave}
      />
    </div>
  );
};
