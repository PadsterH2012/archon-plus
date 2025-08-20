import React, { useState, useEffect } from 'react';
import { X, Plus, Trash2, AlertCircle } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { ArchonLoadingSpinner } from '../animations/Animations';
import { componentService } from '../../services/componentService';
import type { 
  Component, 
  ComponentType, 
  ComponentStatus, 
  CreateComponentRequest, 
  UpdateComponentRequest 
} from '../../types/component';

interface ComponentFormProps {
  projectId: string;
  component?: Component | null; // null for create, Component for edit
  isOpen: boolean;
  onClose: () => void;
  onSave: (component: Component) => void;
  className?: string;
}

const COMPONENT_TYPES: { value: ComponentType; label: string; description: string }[] = [
  { value: 'foundation', label: 'Foundation', description: 'Core system components' },
  { value: 'feature', label: 'Feature', description: 'User-facing functionality' },
  { value: 'integration', label: 'Integration', description: 'External service connections' },
  { value: 'infrastructure', label: 'Infrastructure', description: 'Deployment and operations' },
  { value: 'testing', label: 'Testing', description: 'Quality assurance components' }
];

const COMPONENT_STATUSES: { value: ComponentStatus; label: string }[] = [
  { value: 'not_started', label: 'Not Started' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'gates_passed', label: 'Gates Passed' },
  { value: 'completed', label: 'Completed' },
  { value: 'blocked', label: 'Blocked' }
];

const COMMON_COMPLETION_GATES = [
  'architecture',
  'design',
  'implementation',
  'testing',
  'integration',
  'documentation',
  'review',
  'deployment'
];

export const ComponentForm: React.FC<ComponentFormProps> = ({
  projectId,
  component,
  isOpen,
  onClose,
  onSave,
  className = ''
}) => {
  const [formData, setFormData] = useState<CreateComponentRequest | UpdateComponentRequest>({
    name: '',
    description: '',
    component_type: 'feature',
    dependencies: [],
    completion_gates: [],
    context_data: {},
    order_index: 0
  });

  const [availableComponents, setAvailableComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newGate, setNewGate] = useState('');

  const isEditing = !!component;

  // Initialize form data
  useEffect(() => {
    if (component) {
      setFormData({
        name: component.name,
        description: component.description,
        component_type: component.component_type,
        status: component.status,
        dependencies: component.dependencies,
        completion_gates: component.completion_gates,
        context_data: component.context_data,
        order_index: component.order_index
      });
    } else {
      setFormData({
        name: '',
        description: '',
        component_type: 'feature',
        dependencies: [],
        completion_gates: [],
        context_data: {},
        order_index: 0
      });
    }
  }, [component]);

  // Load available components for dependencies
  useEffect(() => {
    const loadComponents = async () => {
      if (!isOpen) return;
      
      try {
        setLoading(true);
        const result = await componentService.listComponents(projectId, {
          perPage: 100
        });
        
        // Filter out current component if editing
        const filtered = component 
          ? result.components.filter(c => c.id !== component.id)
          : result.components;
          
        setAvailableComponents(filtered);
      } catch (err) {
        console.error('Failed to load components:', err);
        setError('Failed to load available components');
      } finally {
        setLoading(false);
      }
    };

    loadComponents();
  }, [isOpen, projectId, component]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('Component name is required');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      let savedComponent: Component;

      if (isEditing && component) {
        savedComponent = await componentService.updateComponent(
          component.id!,
          formData as UpdateComponentRequest
        );
      } else {
        savedComponent = await componentService.createComponent({
          project_id: projectId,
          ...formData
        } as CreateComponentRequest);
      }

      onSave(savedComponent);
      onClose();
    } catch (err) {
      console.error('Failed to save component:', err);
      setError(err instanceof Error ? err.message : 'Failed to save component');
    } finally {
      setSaving(false);
    }
  };

  const addDependency = (componentId: string) => {
    if (!formData.dependencies.includes(componentId)) {
      setFormData(prev => ({
        ...prev,
        dependencies: [...prev.dependencies, componentId]
      }));
    }
  };

  const removeDependency = (componentId: string) => {
    setFormData(prev => ({
      ...prev,
      dependencies: prev.dependencies.filter(id => id !== componentId)
    }));
  };

  const addCompletionGate = () => {
    if (newGate.trim() && !formData.completion_gates.includes(newGate.trim())) {
      setFormData(prev => ({
        ...prev,
        completion_gates: [...prev.completion_gates, newGate.trim()]
      }));
      setNewGate('');
    }
  };

  const removeCompletionGate = (gate: string) => {
    setFormData(prev => ({
      ...prev,
      completion_gates: prev.completion_gates.filter(g => g !== gate)
    }));
  };

  const addCommonGate = (gate: string) => {
    if (!formData.completion_gates.includes(gate)) {
      setFormData(prev => ({
        ...prev,
        completion_gates: [...prev.completion_gates, gate]
      }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className={`w-full max-w-2xl max-h-[90vh] overflow-y-auto ${className}`} accentColor="blue">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
              {isEditing ? 'Edit Component' : 'Create Component'}
            </h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg">
              <div className="flex items-center gap-2 text-red-700 dark:text-red-300">
                <AlertCircle className="h-4 w-4" />
                <span className="text-sm">{error}</span>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Basic Information
              </h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Component Name *
                </label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter component name"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe the component's purpose and functionality"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 resize-none"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Component Type
                  </label>
                  <Select
                    value={formData.component_type}
                    onValueChange={(value) => setFormData(prev => ({ 
                      ...prev, 
                      component_type: value as ComponentType 
                    }))}
                  >
                    {COMPONENT_TYPES.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </Select>
                </div>

                {isEditing && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Status
                    </label>
                    <Select
                      value={(formData as UpdateComponentRequest).status || 'not_started'}
                      onValueChange={(value) => setFormData(prev => ({ 
                        ...prev, 
                        status: value as ComponentStatus 
                      }))}
                    >
                      {COMPONENT_STATUSES.map(status => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </Select>
                  </div>
                )}
              </div>
            </div>

            {/* Dependencies */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Dependencies
              </h3>
              
              {loading ? (
                <div className="flex items-center gap-2">
                  <ArchonLoadingSpinner />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Loading components...</span>
                </div>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Add Dependency
                    </label>
                    <Select
                      value=""
                      onValueChange={addDependency}
                      placeholder="Select a component"
                    >
                      <option value="" disabled>Select a component</option>
                      {availableComponents
                        .filter(c => !formData.dependencies.includes(c.id!))
                        .map(comp => (
                          <option key={comp.id} value={comp.id}>
                            {comp.name} ({comp.component_type})
                          </option>
                        ))}
                    </Select>
                  </div>

                  {formData.dependencies.length > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Current Dependencies
                      </label>
                      <div className="space-y-2">
                        {formData.dependencies.map(depId => {
                          const dep = availableComponents.find(c => c.id === depId);
                          return (
                            <div key={depId} className="flex items-center justify-between p-2 bg-gray-100 dark:bg-gray-800 rounded-lg">
                              <span className="text-sm">
                                {dep ? `${dep.name} (${dep.component_type})` : `Unknown component (${depId})`}
                              </span>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => removeDependency(depId)}
                                className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Completion Gates */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                Completion Gates
              </h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Common Gates
                </label>
                <div className="flex flex-wrap gap-2">
                  {COMMON_COMPLETION_GATES.map(gate => (
                    <Button
                      key={gate}
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => addCommonGate(gate)}
                      disabled={formData.completion_gates.includes(gate)}
                      className="text-xs"
                    >
                      <Plus className="h-3 w-3 mr-1" />
                      {gate}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Add Custom Gate
                </label>
                <div className="flex gap-2">
                  <Input
                    value={newGate}
                    onChange={(e) => setNewGate(e.target.value)}
                    placeholder="Enter gate name"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCompletionGate())}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={addCompletionGate}
                    disabled={!newGate.trim()}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {formData.completion_gates.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Current Gates
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {formData.completion_gates.map(gate => (
                      <Badge
                        key={gate}
                        variant="secondary"
                        className="flex items-center gap-1"
                      >
                        {gate}
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeCompletionGate(gate)}
                          className="h-4 w-4 p-0 ml-1 text-red-500 hover:text-red-700"
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Form Actions */}
            <div className="flex justify-end gap-3 pt-6 border-t border-gray-200 dark:border-gray-700">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={saving}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={saving || !formData.name.trim()}
              >
                {saving ? (
                  <>
                    <ArchonLoadingSpinner />
                    <span className="ml-2">
                      {isEditing ? 'Updating...' : 'Creating...'}
                    </span>
                  </>
                ) : (
                  isEditing ? 'Update Component' : 'Create Component'
                )}
              </Button>
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
};
