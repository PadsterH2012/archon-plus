/**
 * WorkflowForm Component
 * 
 * Form component for creating and editing workflow metadata
 * Integrates with the visual workflow designer
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Save,
  X,
  Plus,
  Trash2,
  Settings,
  Info,
  Tag,
  Clock,
  RefreshCw,
  Eye,
  Play
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import {
  WorkflowTemplate,
  WorkflowFormProps,
  WorkflowStatus,
  WorkflowParameter,
  WorkflowOutput,
  MCPTool
} from './types/workflow.types';

export const WorkflowForm: React.FC<WorkflowFormProps> = ({
  workflow,
  onSave,
  onCancel,
  isLoading = false,
  availableTools = [],
  isDarkMode = false
}) => {
  // Form state
  const [formData, setFormData] = useState<Partial<WorkflowTemplate>>({
    name: '',
    title: '',
    description: '',
    category: '',
    tags: [],
    status: WorkflowStatus.DRAFT,
    version: '1.0.0',
    is_public: false,
    timeout_minutes: 30,
    max_retries: 3,
    parameters: {},
    outputs: {},
    steps: [],
    ...workflow
  });

  const [categories, setCategories] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');
  const [newParameterKey, setNewParameterKey] = useState('');
  const [newParameterType, setNewParameterType] = useState<'string' | 'integer' | 'boolean' | 'object' | 'array'>('string');
  const [newOutputKey, setNewOutputKey] = useState('');
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const { showToast } = useToast();

  // Load categories
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await workflowService.getCategories();
        setCategories(response.categories);
      } catch (error) {
        console.error('Failed to load categories:', error);
      }
    };
    
    loadCategories();
  }, []);

  // Validate form
  const validateForm = useCallback(() => {
    const errors: Record<string, string> = {};
    
    if (!formData.name?.trim()) {
      errors.name = 'Workflow name is required';
    } else if (!/^[a-z0-9_]+$/.test(formData.name)) {
      errors.name = 'Name must contain only lowercase letters, numbers, and underscores';
    }
    
    if (!formData.title?.trim()) {
      errors.title = 'Workflow title is required';
    }
    
    if (!formData.description?.trim()) {
      errors.description = 'Workflow description is required';
    }
    
    if (!formData.category?.trim()) {
      errors.category = 'Category is required';
    }
    
    if (formData.timeout_minutes && formData.timeout_minutes < 1) {
      errors.timeout_minutes = 'Timeout must be at least 1 minute';
    }
    
    if (formData.max_retries && formData.max_retries < 0) {
      errors.max_retries = 'Max retries cannot be negative';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  }, [formData]);

  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      showToast('Please fix validation errors', 'error');
      return;
    }
    
    try {
      await onSave(formData);
    } catch (error) {
      console.error('Failed to save workflow:', error);
      showToast('Failed to save workflow', 'error');
    }
  }, [formData, validateForm, onSave, showToast]);

  // Handle input changes
  const handleInputChange = useCallback((field: keyof WorkflowTemplate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  }, [validationErrors]);

  // Handle tag management
  const addTag = useCallback(() => {
    if (newTag.trim() && !formData.tags?.includes(newTag.trim())) {
      handleInputChange('tags', [...(formData.tags || []), newTag.trim()]);
      setNewTag('');
    }
  }, [newTag, formData.tags, handleInputChange]);

  const removeTag = useCallback((tagToRemove: string) => {
    handleInputChange('tags', formData.tags?.filter(tag => tag !== tagToRemove) || []);
  }, [formData.tags, handleInputChange]);

  // Handle parameter management
  const addParameter = useCallback(() => {
    if (newParameterKey.trim() && !formData.parameters?.[newParameterKey]) {
      const newParameter: WorkflowParameter = {
        type: newParameterType,
        required: false,
        description: ''
      };
      
      handleInputChange('parameters', {
        ...formData.parameters,
        [newParameterKey]: newParameter
      });
      
      setNewParameterKey('');
    }
  }, [newParameterKey, newParameterType, formData.parameters, handleInputChange]);

  const removeParameter = useCallback((paramKey: string) => {
    const newParameters = { ...formData.parameters };
    delete newParameters[paramKey];
    handleInputChange('parameters', newParameters);
  }, [formData.parameters, handleInputChange]);

  const updateParameter = useCallback((paramKey: string, updates: Partial<WorkflowParameter>) => {
    handleInputChange('parameters', {
      ...formData.parameters,
      [paramKey]: { ...formData.parameters?.[paramKey], ...updates }
    });
  }, [formData.parameters, handleInputChange]);

  // Handle output management
  const addOutput = useCallback(() => {
    if (newOutputKey.trim() && !formData.outputs?.[newOutputKey]) {
      const newOutput: WorkflowOutput = {
        type: 'string',
        description: ''
      };
      
      handleInputChange('outputs', {
        ...formData.outputs,
        [newOutputKey]: newOutput
      });
      
      setNewOutputKey('');
    }
  }, [newOutputKey, formData.outputs, handleInputChange]);

  const removeOutput = useCallback((outputKey: string) => {
    const newOutputs = { ...formData.outputs };
    delete newOutputs[outputKey];
    handleInputChange('outputs', newOutputs);
  }, [formData.outputs, handleInputChange]);

  const updateOutput = useCallback((outputKey: string, updates: Partial<WorkflowOutput>) => {
    handleInputChange('outputs', {
      ...formData.outputs,
      [outputKey]: { ...formData.outputs?.[outputKey], ...updates }
    });
  }, [formData.outputs, handleInputChange]);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {workflow ? 'Edit Workflow' : 'Create New Workflow'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Configure workflow metadata and parameters
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            onClick={onCancel}
            icon={<X className="w-4 h-4" />}
          >
            Cancel
          </Button>
          
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={isLoading}
            icon={<Save className="w-4 h-4" />}
            accentColor="purple"
          >
            {isLoading ? 'Saving...' : 'Save Workflow'}
          </Button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <Card accentColor="purple" className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Info className="w-5 h-5 mr-2" />
            Basic Information
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Input
                label="Workflow Name *"
                value={formData.name || ''}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="e.g., data_processing_workflow"
                error={validationErrors.name}
                accentColor="purple"
              />
              <p className="text-xs text-gray-500 mt-1">
                Lowercase letters, numbers, and underscores only
              </p>
            </div>
            
            <div>
              <Input
                label="Display Title *"
                value={formData.title || ''}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="e.g., Data Processing Workflow"
                error={validationErrors.title}
                accentColor="purple"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-gray-600 dark:text-zinc-400 text-sm mb-1.5">
                Description *
              </label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe what this workflow does..."
                rows={3}
                className={`
                  w-full px-3 py-2 border rounded-md transition-all duration-200
                  ${validationErrors.description 
                    ? 'border-red-300 dark:border-red-600' 
                    : 'border-gray-300 dark:border-gray-600'
                  }
                  bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                  focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent
                `}
              />
              {validationErrors.description && (
                <p className="text-red-500 text-xs mt-1">{validationErrors.description}</p>
              )}
            </div>
            
            <div>
              <label className="block text-gray-600 dark:text-zinc-400 text-sm mb-1.5">
                Category *
              </label>
              <select
                value={formData.category || ''}
                onChange={(e) => handleInputChange('category', e.target.value)}
                className={`
                  w-full px-3 py-2 border rounded-md transition-all duration-200
                  ${validationErrors.category 
                    ? 'border-red-300 dark:border-red-600' 
                    : 'border-gray-300 dark:border-gray-600'
                  }
                  bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                  focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent
                `}
              >
                <option value="">Select a category...</option>
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
                <option value="custom">Custom Category</option>
              </select>
              {validationErrors.category && (
                <p className="text-red-500 text-xs mt-1">{validationErrors.category}</p>
              )}
            </div>
            
            <div>
              <label className="block text-gray-600 dark:text-zinc-400 text-sm mb-1.5">
                Status
              </label>
              <select
                value={formData.status || WorkflowStatus.DRAFT}
                onChange={(e) => handleInputChange('status', e.target.value as WorkflowStatus)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              >
                <option value={WorkflowStatus.DRAFT}>Draft</option>
                <option value={WorkflowStatus.ACTIVE}>Active</option>
                <option value={WorkflowStatus.DEPRECATED}>Deprecated</option>
                <option value={WorkflowStatus.ARCHIVED}>Archived</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Tags */}
        <Card accentColor="blue" className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Tag className="w-5 h-5 mr-2" />
            Tags
          </h2>
          
          <div className="flex flex-wrap gap-2 mb-4">
            {formData.tags?.map(tag => (
              <Badge
                key={tag}
                color="blue"
                className="flex items-center space-x-1"
              >
                <span>{tag}</span>
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="ml-1 hover:text-red-500"
                >
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            ))}
          </div>
          
          <div className="flex items-center space-x-2">
            <Input
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Add a tag..."
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              accentColor="blue"
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={addTag}
              icon={<Plus className="w-4 h-4" />}
            >
              Add
            </Button>
          </div>
        </Card>

        {/* Configuration */}
        <Card accentColor="orange" className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Configuration
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Input
                label="Version"
                value={formData.version || ''}
                onChange={(e) => handleInputChange('version', e.target.value)}
                placeholder="1.0.0"
                accentColor="orange"
              />
            </div>
            
            <div>
              <Input
                label="Timeout (minutes)"
                type="number"
                value={formData.timeout_minutes || ''}
                onChange={(e) => handleInputChange('timeout_minutes', parseInt(e.target.value) || 30)}
                placeholder="30"
                error={validationErrors.timeout_minutes}
                accentColor="orange"
                icon={<Clock className="w-4 h-4" />}
              />
            </div>
            
            <div>
              <Input
                label="Max Retries"
                type="number"
                value={formData.max_retries || ''}
                onChange={(e) => handleInputChange('max_retries', parseInt(e.target.value) || 3)}
                placeholder="3"
                error={validationErrors.max_retries}
                accentColor="orange"
                icon={<RefreshCw className="w-4 h-4" />}
              />
            </div>
          </div>
          
          <div className="mt-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.is_public || false}
                onChange={(e) => handleInputChange('is_public', e.target.checked)}
                className="rounded border-gray-300 text-orange-500 focus:ring-orange-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                Make this workflow public
              </span>
            </label>
          </div>
        </Card>

        {/* Parameters */}
        <Card accentColor="green" className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Input Parameters
          </h2>
          
          <div className="space-y-3">
            {Object.entries(formData.parameters || {}).map(([key, param]) => (
              <div key={key} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex-1 grid grid-cols-4 gap-3">
                  <div>
                    <span className="font-medium text-gray-900 dark:text-white">{key}</span>
                  </div>
                  <div>
                    <select
                      value={param.type}
                      onChange={(e) => updateParameter(key, { type: e.target.value as any })}
                      className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                    >
                      <option value="string">String</option>
                      <option value="integer">Integer</option>
                      <option value="boolean">Boolean</option>
                      <option value="object">Object</option>
                      <option value="array">Array</option>
                    </select>
                  </div>
                  <div>
                    <input
                      type="text"
                      value={param.description}
                      onChange={(e) => updateParameter(key, { description: e.target.value })}
                      placeholder="Description..."
                      className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <label className="flex items-center space-x-1">
                      <input
                        type="checkbox"
                        checked={param.required}
                        onChange={(e) => updateParameter(key, { required: e.target.checked })}
                        className="rounded border-gray-300 text-green-500 focus:ring-green-500"
                      />
                      <span className="text-xs">Required</span>
                    </label>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeParameter(key)}
                  icon={<Trash2 className="w-4 h-4" />}
                />
              </div>
            ))}
          </div>
          
          <div className="flex items-center space-x-2 mt-4">
            <Input
              value={newParameterKey}
              onChange={(e) => setNewParameterKey(e.target.value)}
              placeholder="Parameter name..."
              accentColor="green"
            />
            <select
              value={newParameterType}
              onChange={(e) => setNewParameterType(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            >
              <option value="string">String</option>
              <option value="integer">Integer</option>
              <option value="boolean">Boolean</option>
              <option value="object">Object</option>
              <option value="array">Array</option>
            </select>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={addParameter}
              icon={<Plus className="w-4 h-4" />}
            >
              Add Parameter
            </Button>
          </div>
        </Card>

        {/* Outputs */}
        <Card accentColor="cyan" className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Output Variables
          </h2>
          
          <div className="space-y-3">
            {Object.entries(formData.outputs || {}).map(([key, output]) => (
              <div key={key} className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex-1 grid grid-cols-3 gap-3">
                  <div>
                    <span className="font-medium text-gray-900 dark:text-white">{key}</span>
                  </div>
                  <div>
                    <select
                      value={output.type}
                      onChange={(e) => updateOutput(key, { type: e.target.value as any })}
                      className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                    >
                      <option value="string">String</option>
                      <option value="integer">Integer</option>
                      <option value="boolean">Boolean</option>
                      <option value="object">Object</option>
                      <option value="array">Array</option>
                    </select>
                  </div>
                  <div>
                    <input
                      type="text"
                      value={output.description}
                      onChange={(e) => updateOutput(key, { description: e.target.value })}
                      placeholder="Description..."
                      className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
                    />
                  </div>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeOutput(key)}
                  icon={<Trash2 className="w-4 h-4" />}
                />
              </div>
            ))}
          </div>
          
          <div className="flex items-center space-x-2 mt-4">
            <Input
              value={newOutputKey}
              onChange={(e) => setNewOutputKey(e.target.value)}
              placeholder="Output name..."
              accentColor="cyan"
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={addOutput}
              icon={<Plus className="w-4 h-4" />}
            >
              Add Output
            </Button>
          </div>
        </Card>
      </form>
    </div>
  );
};
