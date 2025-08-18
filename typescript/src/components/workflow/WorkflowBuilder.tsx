/**
 * WorkflowBuilder Component
 * 
 * Comprehensive workflow builder that combines form and visual designer
 * Provides a complete workflow creation and editing experience
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Settings,
  Workflow,
  Eye,
  Play,
  Save,
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  Info,
  Layers
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Tabs } from '../ui/Tabs';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import { WorkflowForm } from './WorkflowForm';
import { WorkflowDesigner } from './WorkflowDesigner';
import {
  WorkflowTemplate,
  MCPTool,
  WorkflowValidationResult,
  ValidationError
} from './types/workflow.types';

interface WorkflowBuilderProps {
  workflow?: WorkflowTemplate;
  onSave?: (workflow: Partial<WorkflowTemplate>) => void;
  onCancel?: () => void;
  onPreview?: (workflow: Partial<WorkflowTemplate>) => void;
  onTest?: (workflow: Partial<WorkflowTemplate>) => void;
  isLoading?: boolean;
  isDarkMode?: boolean;
}

type BuilderTab = 'metadata' | 'designer' | 'validation';

export const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  workflow,
  onSave,
  onCancel,
  onPreview,
  onTest,
  isLoading = false,
  isDarkMode = false
}) => {
  // State management
  const [activeTab, setActiveTab] = useState<BuilderTab>('metadata');
  const [workflowData, setWorkflowData] = useState<Partial<WorkflowTemplate>>(
    workflow || {
      name: '',
      title: '',
      description: '',
      category: '',
      tags: [],
      steps: [],
      parameters: {},
      outputs: {},
      timeout_minutes: 30,
      max_retries: 3
    }
  );
  const [availableTools, setAvailableTools] = useState<MCPTool[]>([]);
  const [validationResult, setValidationResult] = useState<WorkflowValidationResult | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const { showToast } = useToast();

  // Load available MCP tools
  useEffect(() => {
    const loadTools = async () => {
      try {
        const response = await workflowService.getMCPTools();
        setAvailableTools(response.tools);
      } catch (error) {
        console.error('Failed to load MCP tools:', error);
        showToast('Failed to load available tools', 'error');
      }
    };
    
    loadTools();
  }, [showToast]);

  // Validate workflow when data changes
  useEffect(() => {
    if (workflowData.steps && workflowData.steps.length > 0) {
      validateWorkflow();
    }
  }, [workflowData.steps]);

  // Handle workflow data changes
  const handleWorkflowChange = useCallback((updates: Partial<WorkflowTemplate>) => {
    setWorkflowData(prev => ({ ...prev, ...updates }));
    setHasUnsavedChanges(true);
  }, []);

  // Validate workflow
  const validateWorkflow = useCallback(async () => {
    if (!workflowData.steps || workflowData.steps.length === 0) {
      setValidationResult(null);
      return;
    }

    try {
      // Create a temporary workflow for validation
      const tempWorkflow = {
        ...workflowData,
        id: workflow?.id || 'temp',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        created_by: 'user',
        is_public: false,
        status: 'draft' as any,
        version: '1.0.0'
      } as WorkflowTemplate;

      // For now, we'll do client-side validation
      // In a real implementation, this would call the API
      const errors: ValidationError[] = [];
      const warnings: ValidationError[] = [];
      const info: ValidationError[] = [];

      // Basic validation
      if (!tempWorkflow.name) {
        errors.push({ code: 'MISSING_NAME', message: 'Workflow name is required' });
      }
      
      if (!tempWorkflow.title) {
        errors.push({ code: 'MISSING_TITLE', message: 'Workflow title is required' });
      }
      
      if (!tempWorkflow.description) {
        warnings.push({ code: 'MISSING_DESCRIPTION', message: 'Workflow description is recommended' });
      }

      // Step validation
      tempWorkflow.steps.forEach((step, index) => {
        if (!step.name) {
          errors.push({ 
            code: 'MISSING_STEP_NAME', 
            message: `Step ${index + 1} is missing a name`,
            step_name: step.title 
          });
        }
        
        if (step.type === 'action' && !step.tool_name) {
          warnings.push({ 
            code: 'MISSING_TOOL', 
            message: `Action step "${step.title}" should specify a tool`,
            step_name: step.title 
          });
        }
      });

      // Performance analysis
      if (tempWorkflow.steps.length > 10) {
        info.push({ 
          code: 'COMPLEX_WORKFLOW', 
          message: `Workflow has ${tempWorkflow.steps.length} steps - consider breaking into smaller workflows` 
        });
      }

      setValidationResult({
        is_valid: errors.length === 0,
        errors,
        warnings,
        info
      });

    } catch (error) {
      console.error('Failed to validate workflow:', error);
      showToast('Failed to validate workflow', 'error');
    }
  }, [workflowData, workflow?.id, showToast]);

  // Handle save
  const handleSave = useCallback(async () => {
    try {
      await onSave?.(workflowData);
      setHasUnsavedChanges(false);
      showToast('Workflow saved successfully', 'success');
    } catch (error) {
      console.error('Failed to save workflow:', error);
      showToast('Failed to save workflow', 'error');
    }
  }, [workflowData, onSave, showToast]);

  // Handle preview
  const handlePreview = useCallback(() => {
    onPreview?.(workflowData);
  }, [workflowData, onPreview]);

  // Handle test
  const handleTest = useCallback(() => {
    onTest?.(workflowData);
  }, [workflowData, onTest]);

  // Get validation status
  const getValidationStatus = () => {
    if (!validationResult) return null;
    
    if (validationResult.errors.length > 0) {
      return { color: 'red', icon: AlertCircle, label: `${validationResult.errors.length} errors` };
    }
    
    if (validationResult.warnings.length > 0) {
      return { color: 'orange', icon: AlertCircle, label: `${validationResult.warnings.length} warnings` };
    }
    
    return { color: 'green', icon: CheckCircle, label: 'Valid' };
  };

  const validationStatus = getValidationStatus();

  // Tab configuration
  const tabs = [
    {
      id: 'metadata' as BuilderTab,
      label: 'Metadata',
      icon: <Settings className="w-4 h-4" />,
      active: activeTab === 'metadata'
    },
    {
      id: 'designer' as BuilderTab,
      label: 'Designer',
      icon: <Workflow className="w-4 h-4" />,
      active: activeTab === 'designer'
    },
    {
      id: 'validation' as BuilderTab,
      label: 'Validation',
      icon: validationStatus?.icon ? <validationStatus.icon className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />,
      active: activeTab === 'validation',
      badge: validationStatus ? {
        color: validationStatus.color,
        text: validationStatus.label
      } : undefined
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={onCancel}
              icon={<ArrowLeft className="w-4 h-4" />}
            >
              Back
            </Button>
            
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                {workflow ? 'Edit Workflow' : 'Create Workflow'}
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {workflowData.title || 'Untitled Workflow'}
                {hasUnsavedChanges && <span className="text-orange-500 ml-2">• Unsaved changes</span>}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {validationStatus && (
              <Badge 
                color={validationStatus.color}
                icon={<validationStatus.icon className="w-3 h-3" />}
              >
                {validationStatus.label}
              </Badge>
            )}
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handlePreview}
              icon={<Eye className="w-4 h-4" />}
              disabled={!workflowData.steps || workflowData.steps.length === 0}
            >
              Preview
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handleTest}
              icon={<Play className="w-4 h-4" />}
              disabled={!validationResult?.is_valid}
            >
              Test
            </Button>
            
            <Button
              variant="primary"
              size="sm"
              onClick={handleSave}
              disabled={isLoading || !workflowData.name || !workflowData.title}
              icon={<Save className="w-4 h-4" />}
              accentColor="purple"
            >
              {isLoading ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6">
        <Tabs
          tabs={tabs}
          onTabChange={(tabId) => setActiveTab(tabId as BuilderTab)}
          accentColor="purple"
        />
      </div>

      {/* Content */}
      <div className="flex-1">
        {activeTab === 'metadata' && (
          <WorkflowForm
            workflow={workflowData as WorkflowTemplate}
            onSave={handleWorkflowChange}
            onCancel={onCancel}
            isLoading={isLoading}
            availableTools={availableTools}
            isDarkMode={isDarkMode}
          />
        )}

        {activeTab === 'designer' && (
          <WorkflowDesigner
            workflow={workflowData as WorkflowTemplate}
            onSave={handleWorkflowChange}
            onCancel={onCancel}
            onPreview={handlePreview}
            onTest={handleTest}
            isLoading={isLoading}
            isDarkMode={isDarkMode}
          />
        )}

        {activeTab === 'validation' && (
          <div className="max-w-4xl mx-auto p-6">
            <Card accentColor="blue" className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Workflow Validation
              </h2>
              
              {!validationResult ? (
                <div className="text-center py-8">
                  <Layers className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Add workflow steps to see validation results
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Overall Status */}
                  <div className={`p-4 rounded-lg ${
                    validationResult.is_valid 
                      ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                      : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                  }`}>
                    <div className="flex items-center space-x-2">
                      {validationResult.is_valid ? (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-red-500" />
                      )}
                      <span className={`font-medium ${
                        validationResult.is_valid ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'
                      }`}>
                        {validationResult.is_valid ? 'Workflow is valid and ready to execute' : 'Workflow has validation errors'}
                      </span>
                    </div>
                  </div>

                  {/* Errors */}
                  {validationResult.errors.length > 0 && (
                    <div>
                      <h3 className="text-md font-medium text-red-800 dark:text-red-200 mb-3">
                        Errors ({validationResult.errors.length})
                      </h3>
                      <div className="space-y-2">
                        {validationResult.errors.map((error, index) => (
                          <div key={index} className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
                            <div className="flex items-start space-x-2">
                              <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                              <div>
                                <p className="text-red-800 dark:text-red-200 font-medium">{error.message}</p>
                                {error.step_name && (
                                  <p className="text-red-600 dark:text-red-400 text-sm">Step: {error.step_name}</p>
                                )}
                                {error.suggestion && (
                                  <p className="text-red-600 dark:text-red-400 text-sm mt-1">💡 {error.suggestion}</p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Warnings */}
                  {validationResult.warnings.length > 0 && (
                    <div>
                      <h3 className="text-md font-medium text-orange-800 dark:text-orange-200 mb-3">
                        Warnings ({validationResult.warnings.length})
                      </h3>
                      <div className="space-y-2">
                        {validationResult.warnings.map((warning, index) => (
                          <div key={index} className="p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded">
                            <div className="flex items-start space-x-2">
                              <AlertCircle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                              <div>
                                <p className="text-orange-800 dark:text-orange-200 font-medium">{warning.message}</p>
                                {warning.step_name && (
                                  <p className="text-orange-600 dark:text-orange-400 text-sm">Step: {warning.step_name}</p>
                                )}
                                {warning.suggestion && (
                                  <p className="text-orange-600 dark:text-orange-400 text-sm mt-1">💡 {warning.suggestion}</p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Info */}
                  {validationResult.info.length > 0 && (
                    <div>
                      <h3 className="text-md font-medium text-blue-800 dark:text-blue-200 mb-3">
                        Information ({validationResult.info.length})
                      </h3>
                      <div className="space-y-2">
                        {validationResult.info.map((info, index) => (
                          <div key={index} className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded">
                            <div className="flex items-start space-x-2">
                              <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                              <div>
                                <p className="text-blue-800 dark:text-blue-200 font-medium">{info.message}</p>
                                {info.step_name && (
                                  <p className="text-blue-600 dark:text-blue-400 text-sm">Step: {info.step_name}</p>
                                )}
                                {info.suggestion && (
                                  <p className="text-blue-600 dark:text-blue-400 text-sm mt-1">💡 {info.suggestion}</p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Summary */}
                  <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                          {workflowData.steps?.length || 0}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Steps</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                          {Object.keys(workflowData.parameters || {}).length}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Parameters</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                          {workflowData.timeout_minutes || 0}m
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">Timeout</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};
