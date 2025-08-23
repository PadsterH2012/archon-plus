import React, { useState, useEffect, useCallback } from 'react';
import { 
  Settings, 
  Plus, 
  Search, 
  Filter, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle,
  FileText,
  Layers,
  GitBranch,
  BarChart3
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Badge } from '../ui/Badge';
import { ArchonLoadingSpinner } from '../animations/Animations';
import { TemplateEditor } from './TemplateEditor';
import { ComponentLibrary } from './ComponentLibrary';
import { AssignmentManager } from './AssignmentManager';
import { templateService } from '../../services/templateService';
import { templateManagementService } from '../../services/templateManagementService';
import type { 
  TemplateManagementProps,
  TemplateManagementState,
  TemplateOperationType
} from '../../types/templateManagement';
import type { TemplateDefinition, TemplateComponent } from '../../types/component';

export const TemplateManagement: React.FC<TemplateManagementProps> = ({
  projectId,
  className = '',
  onTemplateSelect,
  onComponentSelect,
  onAssignmentSelect
}) => {
  // State management with comprehensive defensive initialization
  const [state, setState] = useState<TemplateManagementState>({
    activeTab: 'templates',
    isLoading: true, // Start with loading state to prevent premature rendering
    isSaving: false,
    isDeleting: false,
    templates: [], // Always initialize as empty array
    components: [], // Always initialize as empty array
    assignments: [], // Always initialize as empty array
    showTemplateEditor: false,
    showComponentEditor: false,
    showAssignmentEditor: false,
    showDeleteConfirmation: false,
    templateFilter: '',
    componentFilter: '',
    assignmentFilter: '',
    searchQuery: ''
  });

  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // Load data on mount and when refresh key changes
  useEffect(() => {
    loadData();
  }, [projectId, refreshKey]);

  const loadData = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true }));
    setError(null);

    try {
      // Load templates and components with proper error handling
      let templatesResult = { templates: [] };
      let componentsResult = { components: [] };

      try {
        templatesResult = await templateService.listTemplates({ includeInheritance: true });
      } catch (templateError) {
        console.warn('Failed to load templates:', templateError);
        // Continue with empty templates array
      }

      try {
        componentsResult = await templateManagementService.listComponents();
      } catch (componentError) {
        console.warn('Failed to load components:', componentError);
        // Continue with empty components array
      }

      setState(prev => ({
        ...prev,
        templates: Array.isArray(templatesResult.templates) ? templatesResult.templates : [],
        components: Array.isArray(componentsResult.components) ? componentsResult.components : [],
        assignments: [], // TODO: Implement assignments API endpoint
        isLoading: false
      }));
    } catch (err) {
      console.error('Failed to load template management data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [projectId]);

  const handleRefresh = useCallback(() => {
    setRefreshKey(prev => prev + 1);
  }, []);

  const handleTabChange = useCallback((tab: TemplateManagementState['activeTab']) => {
    setState(prev => ({ ...prev, activeTab: tab }));
  }, []);

  const handleTemplateCreate = useCallback(() => {
    setState(prev => ({
      ...prev,
      selectedTemplate: undefined,
      showTemplateEditor: true
    }));
  }, []);

  const handleTemplateEdit = useCallback((template: TemplateDefinition) => {
    setState(prev => ({
      ...prev,
      selectedTemplate: template,
      showTemplateEditor: true
    }));
    onTemplateSelect?.(template);
  }, [onTemplateSelect]);

  const handleTemplateEditorClose = useCallback(() => {
    setState(prev => ({
      ...prev,
      showTemplateEditor: false,
      selectedTemplate: undefined
    }));
  }, []);

  const handleTemplateSave = useCallback(async (template: TemplateDefinition) => {
    setState(prev => ({ ...prev, isSaving: true }));
    
    try {
      if (template.id) {
        await templateService.updateTemplate(template.id, template);
      } else {
        await templateService.createTemplate(template);
      }
      
      handleTemplateEditorClose();
      handleRefresh();
    } catch (err) {
      console.error('Failed to save template:', err);
      setError(err instanceof Error ? err.message : 'Failed to save template');
    } finally {
      setState(prev => ({ ...prev, isSaving: false }));
    }
  }, [handleTemplateEditorClose, handleRefresh]);

  const handleSearchChange = useCallback((query: string) => {
    setState(prev => ({ ...prev, searchQuery: query }));
  }, []);

  const handleFilterChange = useCallback((filter: string, type: 'template' | 'component' | 'assignment') => {
    setState(prev => ({
      ...prev,
      [`${type}Filter`]: filter
    }));
  }, []);

  // Filter data based on search and filters
  const filteredTemplates = React.useMemo(() => {
    try {
      // Comprehensive state safety check
      if (!state || typeof state !== 'object') {
        return [];
      }

      // Ensure templates is always an array
      const templates = Array.isArray(state.templates) ? state.templates : [];

      return templates.filter(template => {
        // Ensure template object exists and has required properties
        if (!template || typeof template !== 'object') {
          return false;
        }

        const templateName = template.name || '';
        const templateTitle = template.title || '';
        const templateType = template.template_type || '';

        const matchesSearch = !state.searchQuery ||
          templateName.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
          templateTitle.toLowerCase().includes(state.searchQuery.toLowerCase());

        const matchesFilter = !state.templateFilter ||
      template.status === state.templateFilter ||
          templateType === state.templateFilter;

        return matchesSearch && matchesFilter;
      });
    } catch (error) {
      console.error('Error filtering templates:', error);
      return [];
    }
  }, [state?.templates, state?.searchQuery, state?.templateFilter]);

  const filteredAssignments = React.useMemo(() => {
    try {
      // Comprehensive state safety check
      if (!state || typeof state !== 'object') {
        return [];
      }

      // Ensure assignments is always an array
      const assignments = Array.isArray(state.assignments) ? state.assignments : [];

      return assignments.filter(assignment => {
        // Ensure assignment object exists and has required properties
        if (!assignment || typeof assignment !== 'object') {
          return false;
        }

        const templateName = assignment.template_name || '';
        const hierarchyLevel = assignment.hierarchy_level || '';
        const assignmentScope = assignment.assignment_scope || '';

        const matchesSearch = !state.searchQuery ||
          templateName.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
          hierarchyLevel.toLowerCase().includes(state.searchQuery.toLowerCase());

        const matchesFilter = !state.assignmentFilter ||
          hierarchyLevel === state.assignmentFilter ||
          assignmentScope === state.assignmentFilter;

        return matchesSearch && matchesFilter;
      });
    } catch (error) {
      console.error('Error filtering assignments:', error);
      return [];
    }
  }, [state?.assignments, state?.searchQuery, state?.assignmentFilter]);

  if (state.isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArchonLoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Template Management Error
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {error}
          </p>
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // Additional safety check to ensure state is properly initialized
  if (!state || typeof state !== 'object') {
    console.error('TemplateManagement: Invalid state object', state);
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            State Initialization Error
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Component state is not properly initialized. Please refresh the page.
          </p>
          <Button variant="outline" onClick={() => window.location.reload()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reload Page
          </Button>
        </div>
      </div>
    );
  }

  // Final safety wrapper for render
  try {
    return (
      <div className={`template-management ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Template Management
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Manage workflow templates, components, and assignments
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={state.isLoading}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          
          {state.activeTab === 'templates' && (
            <Button
              variant="primary"
              size="sm"
              onClick={handleTemplateCreate}
            >
              <Plus className="h-4 w-4 mr-2" />
              New Template
            </Button>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="mb-6" accentColor="red">
          <div className="p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100">
                  Error
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {error}
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Search and Filters */}
      <Card className="mb-6">
        <div className="p-4">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search templates, components, or assignments..."
                  value={state.searchQuery}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            {state.activeTab === 'templates' && (
              <Select
                value={state.templateFilter}
                onChange={(value) => handleFilterChange(value, 'template')}
                placeholder="Filter by status"
                className="w-48"
              >
                <option value="">All Templates</option>
                <option value="active">Active</option>
                <option value="draft">Draft</option>
                <option value="deprecated">Deprecated</option>
              </Select>
            )}
            
            {state.activeTab === 'assignments' && (
              <Select
                value={state.assignmentFilter}
                onChange={(value) => handleFilterChange(value, 'assignment')}
                placeholder="Filter by level"
                className="w-48"
              >
                <option value="">All Levels</option>
                <option value="global">Global</option>
                <option value="project">Project</option>
                <option value="milestone">Milestone</option>
                <option value="phase">Phase</option>
                <option value="task">Task</option>
              </Select>
            )}
          </div>
        </div>
      </Card>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
        {[
          { id: 'templates', label: 'Templates', icon: FileText, count: filteredTemplates.length },
          { id: 'components', label: 'Components', icon: Layers, count: (state.components || []).length },
          { id: 'assignments', label: 'Assignments', icon: GitBranch, count: filteredAssignments.length },
          { id: 'analytics', label: 'Analytics', icon: BarChart3, count: 0 }
        ].map((tab) => (
          <button
            key={tab?.id || Math.random()}
            onClick={() => tab?.id && handleTabChange(tab.id as TemplateManagementState['activeTab'])}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 font-medium text-sm transition-colors ${
              state.activeTab === tab.id
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
            {tab.count > 0 && (
              <Badge variant="secondary" size="sm">
                {tab.count}
              </Badge>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {state.activeTab === 'templates' && (
          <div className="templates-tab">
            {filteredTemplates.length === 0 ? (
              <Card>
                <div className="p-8 text-center">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                    No templates found
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {state.searchQuery || state.templateFilter 
                      ? 'No templates match your current filters.'
                      : 'Get started by creating your first template.'
                    }
                  </p>
                  {!state.searchQuery && !state.templateFilter && (
                    <Button variant="primary" onClick={handleTemplateCreate}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Template
                    </Button>
                  )}
                </div>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {(filteredTemplates || []).map((template) => (
                  <Card key={template?.id || Math.random()} className="cursor-pointer hover:shadow-md transition-shadow">
                    <div className="p-4" onClick={() => template && handleTemplateEdit(template)}>
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                            {template.title}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {template.name}
                          </p>
                        </div>
                        <Badge 
                          variant={template.status === 'active' ? 'success' : 'secondary'}
                          size="sm"
                        >
                          {template.status}
                        </Badge>
                      </div>
                      
                      {template.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                          {template.description}
                        </p>
                      )}
                      
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{template.template_type}</span>
                        <span>
                          {template.is_public ? 'Public' : 'Private'}
                        </span>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {state.activeTab === 'components' && (
          <ComponentLibrary
            projectId={projectId}
            onComponentSelect={onComponentSelect}
            showUsageStats={true}
          />
        )}

        {state.activeTab === 'assignments' && (
          <AssignmentManager
            projectId={projectId}
            hierarchyData={[]} // This would be loaded from the service
            assignments={filteredAssignments}
            onAssignmentSelect={onAssignmentSelect}
          />
        )}

        {state.activeTab === 'analytics' && (
          <Card>
            <div className="p-8 text-center">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                Analytics Coming Soon
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Template usage analytics and performance insights will be available soon.
              </p>
            </div>
          </Card>
        )}
      </div>

      {/* Template Editor Modal */}
      {state.showTemplateEditor && (
        <TemplateEditor
          template={state.selectedTemplate}
          mode={state.selectedTemplate ? 'edit' : 'create'}
          isOpen={state.showTemplateEditor}
          onClose={handleTemplateEditorClose}
          onSave={handleTemplateSave}
        />
      )}
    </div>
    );
  } catch (renderError) {
    console.error('TemplateManagement render error:', renderError);
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            Render Error
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            An error occurred while rendering the template management interface.
          </p>
          <Button
            onClick={() => window.location.reload()}
            variant="outline"
            size="sm"
          >
            Reload Page
          </Button>
        </div>
      </div>
    );
  }
};
