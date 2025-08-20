/**
 * WorkflowList Component
 * 
 * Main component for displaying and managing workflow templates
 * Includes search, filtering, and CRUD operations
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Search, 
  Filter, 
  Plus, 
  RefreshCw, 
  Grid, 
  List as ListIcon,
  ChevronDown,
  Workflow,
  Play,
  Edit,
  Trash2,
  Eye
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card } from '../ui/Card';
import { LoadingSpinner } from '../animations/Animations';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import { 
  WorkflowTemplate, 
  WorkflowListProps, 
  WorkflowFilters,
  WorkflowStatus,
  AccentColor 
} from './types/workflow.types';
import { WorkflowCard } from './WorkflowCard';

export const WorkflowList: React.FC<WorkflowListProps> = ({
  workflows: initialWorkflows = [],
  isLoading: externalLoading = false,
  onWorkflowSelect,
  onWorkflowEdit,
  onWorkflowDelete,
  onWorkflowExecute,
  onWorkflowClone,
  searchQuery: externalSearchQuery = '',
  onSearchChange,
  categoryFilter: externalCategoryFilter = '',
  onCategoryChange,
  statusFilter: externalStatusFilter,
  onStatusChange
}) => {
  // State management
  const [workflows, setWorkflows] = useState<WorkflowTemplate[]>(initialWorkflows);
  const [isLoading, setIsLoading] = useState(externalLoading);
  const [searchQuery, setSearchQuery] = useState(externalSearchQuery);
  const [categoryFilter, setCategoryFilter] = useState(externalCategoryFilter);
  const [statusFilter, setStatusFilter] = useState<WorkflowStatus | undefined>(externalStatusFilter);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowTemplate | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const { showToast } = useToast();

  // Load workflows from API
  const loadWorkflows = useCallback(async (resetPage = false) => {
    try {
      setIsLoading(true);
      const currentPage = resetPage ? 1 : page;
      
      const filters: WorkflowFilters = {
        search: searchQuery || undefined,
        category: categoryFilter || undefined,
        status: statusFilter
      };

      const response = await workflowService.listWorkflows(filters, currentPage, 20);
      
      if (resetPage) {
        setWorkflows(response.workflows);
        setPage(1);
      } else {
        setWorkflows(prev => [...prev, ...response.workflows]);
      }
      
      setHasMore(response.has_more);
      setTotalCount(response.total_count);
      
    } catch (error) {
      console.error('Failed to load workflows:', error);
      showToast('Failed to load workflows', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, categoryFilter, statusFilter, page, showToast]);

  // Load categories
  const loadCategories = useCallback(async () => {
    try {
      const response = await workflowService.getCategories();
      setCategories(response.categories);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  }, []);

  // Initial load
  useEffect(() => {
    if (initialWorkflows.length === 0) {
      loadWorkflows(true);
    }
    loadCategories();
  }, []);

  // Handle search changes
  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value);
    onSearchChange?.(value);
    // Debounce search
    const timeoutId = setTimeout(() => {
      loadWorkflows(true);
    }, 500);
    return () => clearTimeout(timeoutId);
  }, [onSearchChange, loadWorkflows]);

  // Handle filter changes
  const handleCategoryChange = useCallback((category: string) => {
    setCategoryFilter(category);
    onCategoryChange?.(category);
    loadWorkflows(true);
  }, [onCategoryChange, loadWorkflows]);

  const handleStatusChange = useCallback((status: WorkflowStatus | undefined) => {
    setStatusFilter(status);
    onStatusChange?.(status);
    loadWorkflows(true);
  }, [onStatusChange, loadWorkflows]);

  // Handle workflow actions
  const handleWorkflowSelect = useCallback((workflow: WorkflowTemplate) => {
    setSelectedWorkflow(workflow);
    onWorkflowSelect?.(workflow);
  }, [onWorkflowSelect]);

  const handleWorkflowEdit = useCallback((workflow: WorkflowTemplate) => {
    onWorkflowEdit?.(workflow);
  }, [onWorkflowEdit]);

  const handleWorkflowDelete = useCallback(async (workflowId: string) => {
    if (!confirm('Are you sure you want to delete this workflow?')) return;
    
    try {
      await workflowService.deleteWorkflow(workflowId);
      setWorkflows(prev => prev.filter(w => w.id !== workflowId));
      showToast('Workflow deleted successfully', 'success');
      onWorkflowDelete?.(workflowId);
    } catch (error) {
      console.error('Failed to delete workflow:', error);
      showToast('Failed to delete workflow', 'error');
    }
  }, [onWorkflowDelete, showToast]);

  const handleWorkflowExecute = useCallback((workflowId: string) => {
    onWorkflowExecute?.(workflowId);
  }, [onWorkflowExecute]);

  // Load more workflows
  const loadMore = useCallback(() => {
    if (!isLoading && hasMore) {
      setPage(prev => prev + 1);
      loadWorkflows();
    }
  }, [isLoading, hasMore, loadWorkflows]);

  // Get accent color based on category
  const getCategoryColor = (category: string): AccentColor => {
    const colorMap: Record<string, AccentColor> = {
      'automation': 'blue',
      'deployment': 'green',
      'testing': 'orange',
      'monitoring': 'purple',
      'research': 'pink',
      'project_management': 'cyan'
    };
    return colorMap[category] || 'purple';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Workflow className="w-8 h-8 text-purple-500" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Workflows
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {totalCount} workflow{totalCount !== 1 ? 's' : ''} available
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            icon={viewMode === 'grid' ? <ListIcon className="w-4 h-4" /> : <Grid className="w-4 h-4" />}
          >
            {viewMode === 'grid' ? 'List' : 'Grid'}
          </Button>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => loadWorkflows(true)}
            icon={<RefreshCw className="w-4 h-4" />}
            disabled={isLoading}
          >
            Refresh
          </Button>
          
          <Button
            variant="primary"
            size="sm"
            onClick={() => onWorkflowEdit?.(undefined as any)}
            icon={<Plus className="w-4 h-4" />}
            accentColor="purple"
          >
            New Workflow
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card accentColor="purple" className="p-4">
        <div className="space-y-4">
          {/* Search Bar */}
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <Input
                placeholder="Search workflows..."
                value={searchQuery}
                onChange={(e) => handleSearchChange(e.target.value)}
                icon={<Search className="w-4 h-4" />}
                accentColor="purple"
              />
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              icon={<Filter className="w-4 h-4" />}
            >
              Filters
              <ChevronDown className={`w-4 h-4 ml-1 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </Button>
          </div>

          {/* Filter Controls */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Category
                </label>
                <select
                  value={categoryFilter}
                  onChange={(e) => handleCategoryChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value="">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={statusFilter || ''}
                  onChange={(e) => handleStatusChange(e.target.value as WorkflowStatus || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value="">All Statuses</option>
                  <option value={WorkflowStatus.ACTIVE}>Active</option>
                  <option value={WorkflowStatus.DRAFT}>Draft</option>
                  <option value={WorkflowStatus.DEPRECATED}>Deprecated</option>
                  <option value={WorkflowStatus.ARCHIVED}>Archived</option>
                </select>
              </div>

              {/* Clear Filters */}
              <div className="flex items-end">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSearchQuery('');
                    setCategoryFilter('');
                    setStatusFilter(undefined);
                    onSearchChange?.('');
                    onCategoryChange?.('');
                    onStatusChange?.(undefined);
                    loadWorkflows(true);
                  }}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Workflow Grid/List */}
      {isLoading && workflows.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : workflows.length === 0 ? (
        <Card accentColor="gray" className="p-12 text-center">
          <Workflow className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No workflows found
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {searchQuery || categoryFilter || statusFilter 
              ? 'Try adjusting your search criteria or filters'
              : 'Get started by creating your first workflow'
            }
          </p>
          <Button
            variant="primary"
            onClick={() => onWorkflowEdit?.(undefined as any)}
            icon={<Plus className="w-4 h-4" />}
            accentColor="purple"
          >
            Create Workflow
          </Button>
        </Card>
      ) : (
        <div className={viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
          : 'space-y-4'
        }>
          {workflows.map((workflow) => (
            <WorkflowCard
              key={workflow.id}
              workflow={workflow}
              onSelect={handleWorkflowSelect}
              onEdit={handleWorkflowEdit}
              onDelete={handleWorkflowDelete}
              onExecute={handleWorkflowExecute}
              onClone={onWorkflowClone}
              isSelected={selectedWorkflow?.id === workflow.id}
              accentColor={getCategoryColor(workflow.category)}
            />
          ))}
        </div>
      )}

      {/* Load More */}
      {hasMore && (
        <div className="flex justify-center pt-6">
          <Button
            variant="ghost"
            onClick={loadMore}
            disabled={isLoading}
            icon={isLoading ? <LoadingSpinner size="sm" /> : undefined}
          >
            {isLoading ? 'Loading...' : 'Load More'}
          </Button>
        </div>
      )}
    </div>
  );
};
