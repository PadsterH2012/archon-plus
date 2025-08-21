import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus,
  Search,
  Filter,
  Edit,
  Trash2,
  Copy,
  Clock,
  Wrench,
  Tag,
  BarChart3,
  Layers
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { Badge } from '../ui/Badge';
import { ArchonLoadingSpinner } from '../animations/Animations';
import type { 
  ComponentLibraryProps,
  ComponentUsageAnalytics
} from '../../types/templateManagement';
import type { TemplateComponent } from '../../types/component';

export const ComponentLibrary: React.FC<ComponentLibraryProps> = ({
  projectId,
  selectedComponents = [],
  onComponentSelect,
  onComponentEdit,
  onComponentCreate,
  showUsageStats = false,
  className = ''
}) => {
  const [components, setComponents] = useState<TemplateComponent[]>([]);
  const [usageStats, setUsageStats] = useState<ComponentUsageAnalytics[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Load components on mount
  useEffect(() => {
    loadComponents();
    if (showUsageStats) {
      loadUsageStats();
    }
  }, [projectId, showUsageStats]);

  const loadComponents = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Try to load components from the API first, fall back to mock data
      let components: TemplateComponent[] = [];

      try {
        // Attempt to load from API
        const response = await templateManagementService.testing.testComponent('group::understand_homelab_env');
        // If successful, we know the API is working, so we could load real components here
        // For now, still use mock data but log that API is available
        console.log('Template API is available');
      } catch (apiError) {
        console.warn('Template API not available, using mock data:', apiError);
      }

      // Mock data for now - would be replaced with actual API call
      const mockComponents: TemplateComponent[] = [
        {
          id: '1',
          name: 'group::understand_homelab_env',
          description: 'Understand the homelab environment and constraints',
          component_type: 'group',
          instruction_text: 'Before implementing any changes, understand the homelab environment...',
          required_tools: ['homelab-vault', 'view'],
          estimated_duration: 10,
          category: 'environment',
          priority: 'high',
          tags: ['homelab', 'environment', 'setup'],
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: '2',
          name: 'group::documentation_update',
          description: 'Update relevant documentation',
          component_type: 'group',
          instruction_text: 'Update documentation to reflect changes...',
          required_tools: ['str-replace-editor', 'view'],
          estimated_duration: 15,
          category: 'documentation',
          priority: 'medium',
          tags: ['documentation', 'update'],
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: '3',
          name: 'group::create_tests',
          description: 'Create comprehensive tests',
          component_type: 'group',
          instruction_text: 'Create tests to validate functionality...',
          required_tools: ['str-replace-editor', 'launch-process'],
          estimated_duration: 20,
          category: 'testing',
          priority: 'high',
          tags: ['testing', 'validation'],
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ];

      setComponents(mockComponents);
    } catch (err) {
      console.error('Failed to load components:', err);
      setError(err instanceof Error ? err.message : 'Failed to load components');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const loadUsageStats = useCallback(async () => {
    try {
      // Mock usage stats - would be replaced with actual API call
      const mockStats: ComponentUsageAnalytics[] = [
        {
          component_name: 'group::understand_homelab_env',
          usage_count: 45,
          templates_using: ['workflow_default', 'workflow_hotfix'],
          average_effectiveness: 85,
          user_feedback_score: 4.2,
          optimization_suggestions: ['Consider adding more specific environment checks']
        },
        {
          component_name: 'group::documentation_update',
          usage_count: 38,
          templates_using: ['workflow_default', 'workflow_milestone_pass'],
          average_effectiveness: 78,
          user_feedback_score: 3.9,
          optimization_suggestions: ['Add automated documentation generation']
        }
      ];

      setUsageStats(mockStats);
    } catch (err) {
      console.error('Failed to load usage stats:', err);
    }
  }, []);

  const handleComponentSelect = useCallback((component: TemplateComponent) => {
    onComponentSelect?.(component);
  }, [onComponentSelect]);

  const handleComponentEdit = useCallback((component: TemplateComponent) => {
    onComponentEdit?.(component);
  }, [onComponentEdit]);

  const handleComponentCreate = useCallback(() => {
    onComponentCreate?.();
  }, [onComponentCreate]);

  // Filter components based on search and filters
  const filteredComponents = React.useMemo(() => {
    try {
      // Ensure components is always an array
      const componentsArray = Array.isArray(components) ? components : [];

      return componentsArray.filter(component => {
        // Ensure component object exists and has required properties
        if (!component || typeof component !== 'object') {
          return false;
        }

        const componentName = component.name || '';
        const componentDescription = component.description || '';
        const componentTags = Array.isArray(component.tags) ? component.tags : [];

        const matchesSearch = !searchQuery ||
          componentName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          componentDescription.toLowerCase().includes(searchQuery.toLowerCase()) ||
          componentTags.some(tag => tag && tag.toLowerCase().includes(searchQuery.toLowerCase()));

        const matchesCategory = !categoryFilter || component.category === categoryFilter;
        const matchesType = !typeFilter || component.component_type === typeFilter;

        return matchesSearch && matchesCategory && matchesType;
      });
    } catch (error) {
      console.error('Error filtering components:', error);
      return [];
    }
  }, [components, searchQuery, categoryFilter, typeFilter]);

  // Get unique categories and types for filters
  const categories = Array.from(new Set((Array.isArray(components) ? components : []).map(c => c?.category).filter(Boolean)));
  const types = Array.from(new Set((Array.isArray(components) ? components : []).map(c => c?.component_type).filter(Boolean)));

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArchonLoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className={`component-library ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            Component Library
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Reusable template components for workflow automation
          </p>
        </div>
        
        {onComponentCreate && (
          <Button
            variant="primary"
            size="sm"
            onClick={handleComponentCreate}
          >
            <Plus className="h-4 w-4 mr-2" />
            New Component
          </Button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <Card className="mb-6" accentColor="red">
          <div className="p-4">
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
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
                  placeholder="Search components..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select
              value={categoryFilter}
              onChange={setCategoryFilter}
              placeholder="All Categories"
              className="w-48"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </Select>
            
            <Select
              value={typeFilter}
              onChange={setTypeFilter}
              placeholder="All Types"
              className="w-48"
            >
              <option value="">All Types</option>
              {types.map(type => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </Select>
          </div>
        </div>
      </Card>

      {/* Components Grid */}
      {filteredComponents.length === 0 ? (
        <Card>
          <div className="p-8 text-center">
            <Layers className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No components found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {searchQuery || categoryFilter || typeFilter
                ? 'No components match your current filters.'
                : 'No components available in the library.'
              }
            </p>
            {onComponentCreate && !searchQuery && !categoryFilter && !typeFilter && (
              <Button variant="primary" onClick={handleComponentCreate}>
                <Plus className="h-4 w-4 mr-2" />
                Create Component
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filteredComponents.map((component) => {
            const isSelected = selectedComponents.includes(component.id);
            const stats = usageStats.find(s => s.component_name === component.name);
            
            return (
              <Card 
                key={component.id} 
                className={`cursor-pointer transition-all ${
                  isSelected ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'hover:shadow-md'
                }`}
                onClick={() => handleComponentSelect(component)}
              >
                <div className="p-4">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                        {component.name}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {component.description}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-2 ml-3">
                      <Badge 
                        variant={component.priority === 'high' ? 'error' : component.priority === 'medium' ? 'warning' : 'secondary'}
                        size="sm"
                      >
                        {component.priority}
                      </Badge>
                      
                      {onComponentEdit && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleComponentEdit(component);
                          }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Metadata */}
                  <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {component.estimated_duration}m
                    </div>
                    <div className="flex items-center gap-1">
                      <Wrench className="h-3 w-3" />
                      {component.required_tools?.length || 0} tools
                    </div>
                    <div className="flex items-center gap-1">
                      <Tag className="h-3 w-3" />
                      {component.category}
                    </div>
                  </div>

                  {/* Tags */}
                  {component.tags && component.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {component.tags.slice(0, 3).map(tag => (
                        <Badge key={tag} variant="secondary" size="xs">
                          {tag}
                        </Badge>
                      ))}
                      {component.tags.length > 3 && (
                        <Badge variant="secondary" size="xs">
                          +{component.tags.length - 3}
                        </Badge>
                      )}
                    </div>
                  )}

                  {/* Usage Stats */}
                  {showUsageStats && stats && (
                    <div className="border-t border-gray-200 dark:border-gray-700 pt-3 mt-3">
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-3">
                          <span className="text-gray-600 dark:text-gray-400">
                            Used {stats.usage_count} times
                          </span>
                          <span className="text-gray-600 dark:text-gray-400">
                            {stats.average_effectiveness}% effective
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <BarChart3 className="h-3 w-3 text-gray-400" />
                          <span className="text-gray-600 dark:text-gray-400">
                            {stats.user_feedback_score}/5
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Required Tools */}
                  {component.required_tools && component.required_tools.length > 0 && (
                    <div className="border-t border-gray-200 dark:border-gray-700 pt-3 mt-3">
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        <span className="font-medium">Tools:</span> {component.required_tools.join(', ')}
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};
