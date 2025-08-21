import React, { useState, useEffect, useCallback } from 'react';
import { 
  X, 
  Save, 
  Eye, 
  Play, 
  AlertCircle, 
  CheckCircle, 
  FileText,
  Code,
  Settings,
  TestTube
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Badge } from '../ui/Badge';
import { ArchonLoadingSpinner } from '../animations/Animations';
import { templateManagementService } from '../../services/templateManagementService';
import type { 
  TemplateEditorProps,
  TemplateEditorState,
  TemplateTestResult
} from '../../types/templateManagement';
import type { TemplateDefinition, TemplateType, TemplateStatus } from '../../types/component';

export const TemplateEditor: React.FC<TemplateEditorProps> = ({
  template,
  mode,
  isOpen,
  onClose,
  onSave,
  onTest,
  className = ''
}) => {
  const [state, setState] = useState<TemplateEditorState>({
    template: template || {
      name: '',
      title: '',
      description: '',
      template_type: 'personal' as TemplateType,
      status: 'draft' as TemplateStatus,
      workflow_assignments: {},
      component_templates: {},
      inheritance_rules: {},
      is_active: true,
      is_public: false
    },
    originalTemplate: template,
    mode,
    isDirty: false,
    isValid: false,
    validationErrors: [],
    templateContent: '',
    selectedComponents: [],
    componentOrder: [],
    showPreview: false,
    previewContent: '',
    testTaskDescription: 'Create a new API endpoint for user authentication with proper validation and error handling.',
    testResults: undefined
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [activeTab, setActiveTab] = useState<'basic' | 'content' | 'components' | 'preview' | 'test'>('basic');

  // Initialize template content from template data
  useEffect(() => {
    if (template?.workflow_assignments) {
      const content = template.workflow_assignments.template_content || '';
      setState(prev => ({
        ...prev,
        templateContent: content,
        template: { ...template }
      }));
    }
  }, [template]);

  // Validate template
  useEffect(() => {
    const errors: string[] = [];
    
    if (!state.template.name?.trim()) {
      errors.push('Template name is required');
    }
    
    if (!state.template.title?.trim()) {
      errors.push('Template title is required');
    }
    
    if (state.template.name && !/^[a-z0-9_]+$/.test(state.template.name)) {
      errors.push('Template name must contain only lowercase letters, numbers, and underscores');
    }

    setState(prev => ({
      ...prev,
      validationErrors: errors,
      isValid: errors.length === 0,
      isDirty: JSON.stringify(prev.template) !== JSON.stringify(prev.originalTemplate)
    }));
  }, [state.template, state.originalTemplate]);

  const handleFieldChange = useCallback((field: keyof TemplateDefinition, value: any) => {
    setState(prev => ({
      ...prev,
      template: {
        ...prev.template,
        [field]: value
      }
    }));
  }, []);

  const handleContentChange = useCallback((content: string) => {
    setState(prev => ({
      ...prev,
      templateContent: content,
      template: {
        ...prev.template,
        workflow_assignments: {
          ...prev.template.workflow_assignments,
          template_content: content
        }
      }
    }));
  }, []);

  const handlePreview = useCallback(async () => {
    if (!state.templateContent) {
      setState(prev => ({ ...prev, previewContent: 'No template content to preview' }));
      return;
    }

    setIsLoading(true);
    try {
      // Generate preview by expanding template with sample data
      const preview = state.templateContent
        .replace(/\{\{USER_TASK\}\}/g, state.testTaskDescription)
        .replace(/\{\{group::([^}]+)\}\}/g, (match, groupName) => {
          return `[${groupName.replace(/_/g, ' ').toUpperCase()}]\n- Component instructions would appear here\n- Based on the ${groupName} component definition\n`;
        });

      setState(prev => ({
        ...prev,
        previewContent: preview,
        showPreview: true
      }));
    } catch (error) {
      console.error('Failed to generate preview:', error);
      setState(prev => ({
        ...prev,
        previewContent: 'Failed to generate preview: ' + (error instanceof Error ? error.message : 'Unknown error')
      }));
    } finally {
      setIsLoading(false);
    }
  }, [state.templateContent, state.testTaskDescription]);

  const handleTest = useCallback(async () => {
    if (!state.template.name || !state.testTaskDescription) {
      return;
    }

    setIsTesting(true);
    try {
      let testResult: TemplateTestResult;
      
      if (onTest) {
        testResult = await onTest(state.template as TemplateDefinition, state.testTaskDescription);
      } else {
        testResult = await templateManagementService.testing.testTemplate(
          state.template.name,
          state.testTaskDescription
        );
      }

      setState(prev => ({
        ...prev,
        testResults: testResult
      }));
    } catch (error) {
      console.error('Failed to test template:', error);
      setState(prev => ({
        ...prev,
        testResults: {
          success: false,
          expanded_content: '',
          expansion_time_ms: 0,
          component_count: 0,
          validation_errors: [error instanceof Error ? error.message : 'Unknown error'],
          performance_score: 0,
          quality_score: 0
        }
      }));
    } finally {
      setIsTesting(false);
    }
  }, [state.template, state.testTaskDescription, onTest]);

  const handleSave = useCallback(async () => {
    if (!state.isValid) {
      return;
    }

    setIsLoading(true);
    try {
      await onSave(state.template as TemplateDefinition);
    } catch (error) {
      console.error('Failed to save template:', error);
    } finally {
      setIsLoading(false);
    }
  }, [state.template, state.isValid, onSave]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-6xl h-5/6 flex flex-col ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              {mode === 'create' ? 'Create Template' : 'Edit Template'}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {mode === 'create' 
                ? 'Create a new workflow template'
                : `Editing: ${state.template.title || state.template.name}`
              }
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            {state.isDirty && (
              <Badge variant="warning" size="sm">
                Unsaved Changes
              </Badge>
            )}
            
            <Button
              variant="outline"
              size="sm"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            
            <Button
              variant="primary"
              size="sm"
              onClick={handleSave}
              disabled={!state.isValid || isLoading}
            >
              {isLoading ? (
                <ArchonLoadingSpinner size="sm" className="mr-2" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              Save Template
            </Button>
          </div>
        </div>

        {/* Validation Errors */}
        {state.validationErrors.length > 0 && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm font-medium text-red-700 dark:text-red-300">
                Please fix the following errors:
              </span>
            </div>
            <ul className="mt-2 text-sm text-red-600 dark:text-red-400 list-disc list-inside">
              {state.validationErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 px-6">
          {[
            { id: 'basic', label: 'Basic Info', icon: FileText },
            { id: 'content', label: 'Template Content', icon: Code },
            { id: 'components', label: 'Components', icon: Settings },
            { id: 'preview', label: 'Preview', icon: Eye },
            { id: 'test', label: 'Test', icon: TestTube }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'basic' && (
            <div className="p-6 space-y-6 overflow-y-auto h-full">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Template Name *
                  </label>
                  <Input
                    value={state.template.name || ''}
                    onChange={(e) => handleFieldChange('name', e.target.value)}
                    placeholder="workflow_custom_name"
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Unique identifier (lowercase, numbers, underscores only)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Template Title *
                  </label>
                  <Input
                    value={state.template.title || ''}
                    onChange={(e) => handleFieldChange('title', e.target.value)}
                    placeholder="Custom Workflow Template"
                    className="w-full"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={state.template.description || ''}
                    onChange={(e) => handleFieldChange('description', e.target.value)}
                    placeholder="Describe what this template is used for..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Template Type
                  </label>
                  <Select
                    value={state.template.template_type || 'personal'}
                    onChange={(value) => handleFieldChange('template_type', value)}
                    className="w-full"
                  >
                    <option value="personal">Personal</option>
                    <option value="team">Team</option>
                    <option value="industry">Industry</option>
                    <option value="community">Community</option>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Status
                  </label>
                  <Select
                    value={state.template.status || 'draft'}
                    onChange={(value) => handleFieldChange('status', value)}
                    className="w-full"
                  >
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="deprecated">Deprecated</option>
                    <option value="archived">Archived</option>
                  </Select>
                </div>

                <div className="md:col-span-2">
                  <div className="flex items-center gap-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={state.template.is_active || false}
                        onChange={(e) => handleFieldChange('is_active', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                        Active
                      </span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={state.template.is_public || false}
                        onChange={(e) => handleFieldChange('is_public', e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                        Public
                      </span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'content' && (
            <div className="p-6 h-full flex flex-col">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Template Content
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Use {`{{USER_TASK}}`} for user task insertion and {`{{group::component_name}}`} for component references
                </p>
              </div>
              
              <div className="flex-1">
                <textarea
                  value={state.templateContent}
                  onChange={(e) => handleContentChange(e.target.value)}
                  placeholder={`{{group::understand_homelab_env}}

{{group::documentation_update}}

{{USER_TASK}}

{{group::create_tests}}

{{group::deployment_validation}}`}
                  className="w-full h-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100 font-mono text-sm resize-none"
                />
              </div>
            </div>
          )}

          {activeTab === 'preview' && (
            <div className="p-6 h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                  Template Preview
                </h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePreview}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <ArchonLoadingSpinner size="sm" className="mr-2" />
                  ) : (
                    <Eye className="h-4 w-4 mr-2" />
                  )}
                  Generate Preview
                </Button>
              </div>
              
              <div className="flex-1 border border-gray-300 dark:border-gray-600 rounded-md p-4 bg-gray-50 dark:bg-gray-900 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300">
                  {state.previewContent || 'Click "Generate Preview" to see how this template will look when expanded.'}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'test' && (
            <div className="p-6 h-full flex flex-col">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Test Task Description
                </label>
                <textarea
                  value={state.testTaskDescription}
                  onChange={(e) => setState(prev => ({ ...prev, testTaskDescription: e.target.value }))}
                  placeholder="Enter a sample task description to test template expansion..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-gray-100"
                />
              </div>

              <div className="flex items-center gap-3 mb-4">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleTest}
                  disabled={isTesting || !state.template.name || !state.testTaskDescription}
                >
                  {isTesting ? (
                    <ArchonLoadingSpinner size="sm" className="mr-2" />
                  ) : (
                    <Play className="h-4 w-4 mr-2" />
                  )}
                  Test Template
                </Button>
              </div>

              {state.testResults && (
                <div className="flex-1 space-y-4 overflow-y-auto">
                  <Card accentColor={state.testResults.success ? 'green' : 'red'}>
                    <div className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        {state.testResults.success ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : (
                          <AlertCircle className="h-5 w-5 text-red-500" />
                        )}
                        <span className="font-medium">
                          Test {state.testResults.success ? 'Passed' : 'Failed'}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Expansion Time:</span>
                          <div className="font-medium">{state.testResults.expansion_time_ms}ms</div>
                        </div>
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Components:</span>
                          <div className="font-medium">{state.testResults.component_count}</div>
                        </div>
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Performance:</span>
                          <div className="font-medium">{state.testResults.performance_score}/100</div>
                        </div>
                        <div>
                          <span className="text-gray-600 dark:text-gray-400">Quality:</span>
                          <div className="font-medium">{state.testResults.quality_score}/100</div>
                        </div>
                      </div>
                    </div>
                  </Card>

                  {state.testResults.validation_errors.length > 0 && (
                    <Card accentColor="red">
                      <div className="p-4">
                        <h4 className="font-medium text-red-700 dark:text-red-300 mb-2">
                          Validation Errors
                        </h4>
                        <ul className="text-sm text-red-600 dark:text-red-400 list-disc list-inside">
                          {state.testResults.validation_errors.map((error, index) => (
                            <li key={index}>{error}</li>
                          ))}
                        </ul>
                      </div>
                    </Card>
                  )}

                  {state.testResults.expanded_content && (
                    <Card>
                      <div className="p-4">
                        <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                          Expanded Content
                        </h4>
                        <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-3 max-h-64 overflow-y-auto">
                          <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300">
                            {state.testResults.expanded_content}
                          </pre>
                        </div>
                      </div>
                    </Card>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
