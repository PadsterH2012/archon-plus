import React, { useState, useEffect, useRef, useMemo } from 'react';
import { AlertCircle, ZoomIn, ZoomOut, RotateCcw, Package } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { ArchonLoadingSpinner } from '../animations/Animations';
import { componentService } from '../../services/componentService';
import type { Component, ComponentStatus, ComponentType } from '../../types/component';

interface DependencyGraphProps {
  projectId: string;
  selectedComponentId?: string;
  onComponentSelect?: (component: Component) => void;
  className?: string;
}

interface GraphNode {
  id: string;
  component: Component;
  x: number;
  y: number;
  level: number;
}

interface GraphEdge {
  from: string;
  to: string;
}

const STATUS_COLORS = {
  not_started: '#6B7280',
  in_progress: '#3B82F6',
  gates_passed: '#10B981',
  completed: '#059669',
  blocked: '#EF4444'
} as const;

const TYPE_COLORS = {
  foundation: '#8B5CF6',
  feature: '#3B82F6',
  integration: '#06B6D4',
  infrastructure: '#F59E0B',
  testing: '#10B981'
} as const;

export const DependencyGraph: React.FC<DependencyGraphProps> = ({
  projectId,
  selectedComponentId,
  onComponentSelect,
  className = ''
}) => {
  const [components, setComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

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

  // Calculate graph layout
  const { nodes, edges } = useMemo(() => {
    if (!components.length) return { nodes: [], edges: [] };

    const componentMap = new Map(components.map(c => [c.id!, c]));
    const nodes: GraphNode[] = [];
    const edges: GraphEdge[] = [];
    const levels = new Map<string, number>();
    
    // Calculate dependency levels using topological sort
    const visited = new Set<string>();
    const visiting = new Set<string>();
    
    const calculateLevel = (componentId: string): number => {
      if (levels.has(componentId)) {
        return levels.get(componentId)!;
      }
      
      if (visiting.has(componentId)) {
        // Circular dependency detected
        levels.set(componentId, 0);
        return 0;
      }
      
      if (visited.has(componentId)) {
        return levels.get(componentId) || 0;
      }
      
      visiting.add(componentId);
      
      const component = componentMap.get(componentId);
      if (!component) {
        levels.set(componentId, 0);
        return 0;
      }
      
      let maxDepLevel = -1;
      for (const depId of component.dependencies) {
        if (componentMap.has(depId)) {
          maxDepLevel = Math.max(maxDepLevel, calculateLevel(depId));
        }
      }
      
      const level = maxDepLevel + 1;
      levels.set(componentId, level);
      visiting.delete(componentId);
      visited.add(componentId);
      
      return level;
    };
    
    // Calculate levels for all components
    for (const component of components) {
      calculateLevel(component.id!);
    }
    
    // Group components by level
    const levelGroups = new Map<number, Component[]>();
    for (const component of components) {
      const level = levels.get(component.id!) || 0;
      if (!levelGroups.has(level)) {
        levelGroups.set(level, []);
      }
      levelGroups.get(level)!.push(component);
    }
    
    // Position nodes
    const nodeWidth = 200;
    const nodeHeight = 80;
    const levelSpacing = 250;
    const nodeSpacing = 120;
    
    for (const [level, levelComponents] of levelGroups) {
      const startY = -(levelComponents.length - 1) * nodeSpacing / 2;
      
      levelComponents.forEach((component, index) => {
        nodes.push({
          id: component.id!,
          component,
          x: level * levelSpacing,
          y: startY + index * nodeSpacing,
          level
        });
      });
    }
    
    // Create edges
    for (const component of components) {
      for (const depId of component.dependencies) {
        if (componentMap.has(depId)) {
          edges.push({
            from: depId,
            to: component.id!
          });
        }
      }
    }
    
    return { nodes, edges };
  }, [components]);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.2, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.2, 0.3));
  };

  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleNodeClick = (component: Component) => {
    onComponentSelect?.(component);
  };

  if (loading) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="flex items-center justify-center">
          <ArchonLoadingSpinner />
          <span className="ml-2 text-gray-600 dark:text-gray-400">Loading dependency graph...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`p-6 ${className}`} accentColor="red">
        <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
          <AlertCircle className="h-5 w-5" />
          <span>Error loading dependency graph: {error}</span>
        </div>
      </Card>
    );
  }

  if (nodes.length === 0) {
    return (
      <Card className={`p-6 ${className}`}>
        <div className="text-center text-gray-500 dark:text-gray-400">
          <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>No components to display</p>
          <p className="text-sm">Create components to see the dependency graph</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`${className}`} accentColor="purple">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Dependency Graph
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {nodes.length} component{nodes.length !== 1 ? 's' : ''}, {edges.length} dependenc{edges.length !== 1 ? 'ies' : 'y'}
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomOut}
              className="h-8 w-8 p-0"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="text-sm text-gray-600 dark:text-gray-400 min-w-[3rem] text-center">
              {Math.round(zoom * 100)}%
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomIn}
              className="h-8 w-8 p-0"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              className="h-8 w-8 p-0"
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
      
      <div 
        ref={containerRef}
        className="relative h-96 overflow-hidden bg-gray-50 dark:bg-gray-900"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        <svg
          ref={svgRef}
          className="absolute inset-0 w-full h-full"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`
          }}
        >
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3.5, 0 7"
                fill="#6B7280"
                className="dark:fill-gray-400"
              />
            </marker>
          </defs>
          
          {/* Center the graph */}
          <g transform={`translate(${400}, ${200})`}>
            {/* Render edges */}
            {edges.map((edge, index) => {
              const fromNode = nodes.find(n => n.id === edge.from);
              const toNode = nodes.find(n => n.id === edge.to);
              
              if (!fromNode || !toNode) return null;
              
              return (
                <line
                  key={`${edge.from}-${edge.to}-${index}`}
                  x1={fromNode.x + 100}
                  y1={fromNode.y}
                  x2={toNode.x - 100}
                  y2={toNode.y}
                  stroke="#6B7280"
                  strokeWidth="2"
                  markerEnd="url(#arrowhead)"
                  className="dark:stroke-gray-400"
                />
              );
            })}
            
            {/* Render nodes */}
            {nodes.map(node => {
              const isSelected = selectedComponentId === node.id;
              const statusColor = STATUS_COLORS[node.component.status];
              const typeColor = TYPE_COLORS[node.component.component_type];
              
              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x - 100}, ${node.y - 40})`}
                  className="cursor-pointer"
                  onClick={() => handleNodeClick(node.component)}
                >
                  {/* Node background */}
                  <rect
                    width="200"
                    height="80"
                    rx="8"
                    fill="white"
                    stroke={isSelected ? '#3B82F6' : '#E5E7EB'}
                    strokeWidth={isSelected ? '3' : '1'}
                    className="dark:fill-gray-800 dark:stroke-gray-600"
                  />
                  
                  {/* Status indicator */}
                  <rect
                    width="200"
                    height="4"
                    rx="2"
                    fill={statusColor}
                  />
                  
                  {/* Component icon */}
                  <circle
                    cx="20"
                    cy="30"
                    r="8"
                    fill={typeColor}
                  />
                  
                  {/* Component name */}
                  <text
                    x="35"
                    y="25"
                    fontSize="14"
                    fontWeight="600"
                    fill="#111827"
                    className="dark:fill-gray-100"
                  >
                    {node.component.name.length > 20 
                      ? `${node.component.name.substring(0, 20)}...` 
                      : node.component.name}
                  </text>
                  
                  {/* Component type */}
                  <text
                    x="35"
                    y="40"
                    fontSize="12"
                    fill="#6B7280"
                    className="dark:fill-gray-400"
                  >
                    {node.component.component_type}
                  </text>
                  
                  {/* Status */}
                  <text
                    x="35"
                    y="55"
                    fontSize="11"
                    fill={statusColor}
                  >
                    {node.component.status.replace('_', ' ')}
                  </text>
                  
                  {/* Dependency count */}
                  {node.component.dependencies.length > 0 && (
                    <text
                      x="170"
                      y="25"
                      fontSize="11"
                      fill="#6B7280"
                      textAnchor="end"
                      className="dark:fill-gray-400"
                    >
                      {node.component.dependencies.length} dep{node.component.dependencies.length !== 1 ? 's' : ''}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>
      </div>
    </Card>
  );
};
