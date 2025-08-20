import React, { useState, useEffect, useMemo } from 'react';
import { ChevronDown, ChevronRight, Package, AlertCircle, CheckCircle, Clock, Play, Pause } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { ArchonLoadingSpinner } from '../animations/Animations';
import { componentService } from '../../services/componentService';
import type { Component, ComponentStatus, ComponentType } from '../../types/component';

interface ComponentHierarchyProps {
  projectId: string;
  onComponentSelect?: (component: Component) => void;
  onComponentEdit?: (component: Component) => void;
  selectedComponentId?: string;
  className?: string;
}

interface ComponentNode extends Component {
  children: ComponentNode[];
  level: number;
}

const STATUS_ICONS = {
  not_started: Clock,
  in_progress: Play,
  gates_passed: CheckCircle,
  completed: CheckCircle,
  blocked: Pause
} as const;

const STATUS_COLORS = {
  not_started: 'gray',
  in_progress: 'blue',
  gates_passed: 'green',
  completed: 'green',
  blocked: 'red'
} as const;

const TYPE_COLORS = {
  foundation: 'purple',
  feature: 'blue',
  integration: 'cyan',
  infrastructure: 'orange',
  testing: 'green'
} as const;

export const ComponentHierarchy: React.FC<ComponentHierarchyProps> = ({
  projectId,
  onComponentSelect,
  onComponentEdit,
  selectedComponentId,
  className = ''
}) => {
  const [components, setComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  // Load components
  useEffect(() => {
    const loadComponents = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const result = await componentService.listComponents(projectId, {
          includeDependencies: true,
          perPage: 100
        });
        
        setComponents(result.components);
      } catch (err) {
        console.error('Failed to load components:', err);
        setError(err instanceof Error ? err.message : 'Failed to load components');
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      loadComponents();
    }
  }, [projectId]);

  // Build component hierarchy tree
  const componentTree = useMemo(() => {
    if (!components.length) return [];

    const componentMap = new Map(components.map(c => [c.id!, c]));
    const roots: ComponentNode[] = [];
    const processed = new Set<string>();

    // Helper function to build tree recursively
    const buildNode = (component: Component, level: number = 0): ComponentNode => {
      const node: ComponentNode = {
        ...component,
        children: [],
        level
      };

      // Find components that depend on this one
      const dependents = components.filter(c => 
        c.dependencies.includes(component.id!) && !processed.has(c.id!)
      );

      for (const dependent of dependents) {
        if (!processed.has(dependent.id!)) {
          processed.add(dependent.id!);
          node.children.push(buildNode(dependent, level + 1));
        }
      }

      return node;
    };

    // Find root components (no dependencies or dependencies not in current project)
    const rootComponents = components.filter(c => 
      c.dependencies.length === 0 || 
      !c.dependencies.some(depId => componentMap.has(depId))
    );

    for (const rootComponent of rootComponents) {
      if (!processed.has(rootComponent.id!)) {
        processed.add(rootComponent.id!);
        roots.push(buildNode(rootComponent));
      }
    }

    // Add any remaining components as separate roots (in case of circular dependencies)
    for (const component of components) {
      if (!processed.has(component.id!)) {
        roots.push(buildNode(component));
      }
    }

    return roots;
  }, [components]);

  const toggleExpanded = (componentId: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(componentId)) {
      newExpanded.delete(componentId);
    } else {
      newExpanded.add(componentId);
    }
    setExpandedNodes(newExpanded);
  };

  const handleComponentClick = (component: Component) => {
    onComponentSelect?.(component);
  };

  const handleComponentEdit = (component: Component, e: React.MouseEvent) => {
    e.stopPropagation();
    onComponentEdit?.(component);
  };

  const renderComponentNode = (node: ComponentNode) => {
    const StatusIcon = STATUS_ICONS[node.status];
    const hasChildren = node.children.length > 0;
    const isExpanded = expandedNodes.has(node.id!);
    const isSelected = selectedComponentId === node.id;

    return (
      <div key={node.id} className="select-none">
        <div
          className={`
            flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-all duration-200
            hover:bg-gray-100 dark:hover:bg-gray-800
            ${isSelected ? 'bg-blue-100 dark:bg-blue-900/30 ring-2 ring-blue-500/50' : ''}
            ${node.level > 0 ? 'ml-6' : ''}
          `}
          onClick={() => handleComponentClick(node)}
          style={{ paddingLeft: `${node.level * 24 + 8}px` }}
        >
          {/* Expand/Collapse Button */}
          {hasChildren ? (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                toggleExpanded(node.id!);
              }}
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
          ) : (
            <div className="w-6" />
          )}

          {/* Component Icon */}
          <Package className="h-4 w-4 text-gray-500" />

          {/* Component Name */}
          <span className="font-medium text-gray-900 dark:text-gray-100 flex-1">
            {node.name}
          </span>

          {/* Component Type Badge */}
          <Badge 
            variant="secondary" 
            className={`text-xs bg-${TYPE_COLORS[node.component_type]}-100 text-${TYPE_COLORS[node.component_type]}-800 dark:bg-${TYPE_COLORS[node.component_type]}-900/30 dark:text-${TYPE_COLORS[node.component_type]}-300`}
          >
            {node.component_type}
          </Badge>

          {/* Status Icon and Badge */}
          <div className="flex items-center gap-1">
            <StatusIcon className={`h-4 w-4 text-${STATUS_COLORS[node.status]}-500`} />
            <Badge 
              variant="secondary"
              className={`text-xs bg-${STATUS_COLORS[node.status]}-100 text-${STATUS_COLORS[node.status]}-800 dark:bg-${STATUS_COLORS[node.status]}-900/30 dark:text-${STATUS_COLORS[node.status]}-300`}
            >
              {node.status.replace('_', ' ')}
            </Badge>
          </div>

          {/* Edit Button */}
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={(e) => handleComponentEdit(node, e)}
          >
            <Package className="h-3 w-3" />
          </Button>
        </div>

        {/* Children */}
        {hasChildren && isExpanded && (
          <div className="mt-1">
            {node.children.map(child => renderComponentNode(child))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="flex items-center justify-center">
          <ArchonLoadingSpinner />
          <span className="ml-2 text-gray-600 dark:text-gray-400">Loading components...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`p-6 ${className}`} accentColor="red">
        <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
          <AlertCircle className="h-5 w-5" />
          <span>Error loading components: {error}</span>
        </div>
      </Card>
    );
  }

  if (componentTree.length === 0) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="text-center text-gray-500 dark:text-gray-400">
          <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>No components found</p>
          <p className="text-sm">Create your first component to get started</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`${className}`} accentColor="blue">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Component Hierarchy
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {components.length} component{components.length !== 1 ? 's' : ''} in project
        </p>
      </div>
      
      <div className="p-4 space-y-1 max-h-96 overflow-y-auto">
        {componentTree.map(node => renderComponentNode(node))}
      </div>
    </Card>
  );
};
