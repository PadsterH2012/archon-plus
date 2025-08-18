/**
 * WorkflowDesigner Component
 * 
 * Visual drag-and-drop workflow designer interface
 * Built with React Flow for node-based workflow creation
 */

import React, { useState, useCallback, useMemo, useRef } from 'react';
import '@xyflow/react/dist/style.css';
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  Background,
  MarkerType,
  NodeChange,
  EdgeChange,
  Connection,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Handle,
  Position,
  NodeProps,
  ConnectionLineType,
  useReactFlow,
  ReactFlowProvider
} from '@xyflow/react';
import {
  Zap,
  GitBranch,
  RotateCcw,
  Link,
  List,
  Plus,
  Save,
  Play,
  Eye,
  Settings,
  Trash2,
  Copy,
  Download,
  Upload,
  Grid,
  Layers
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import {
  WorkflowTemplate,
  WorkflowStep,
  WorkflowStepType,
  MCPTool,
  AccentColor
} from './types/workflow.types';

// Node data types for React Flow
interface WorkflowNodeData {
  label: string;
  stepType: WorkflowStepType;
  toolName?: string;
  description?: string;
  parameters?: Record<string, any>;
  isValid?: boolean;
  errors?: string[];
}

interface WorkflowDesignerProps {
  workflow?: WorkflowTemplate;
  onSave?: (workflow: Partial<WorkflowTemplate>) => void;
  onCancel?: () => void;
  onPreview?: (workflow: Partial<WorkflowTemplate>) => void;
  onTest?: (workflow: Partial<WorkflowTemplate>) => void;
  isLoading?: boolean;
  isDarkMode?: boolean;
}

// Custom node components
const ActionNode: React.FC<NodeProps<WorkflowNodeData>> = ({ data, id, selected }) => {
  const isValid = data.isValid !== false;
  
  return (
    <div className={`
      relative group min-w-[200px] p-4 rounded-lg border-2 transition-all duration-200
      ${selected ? 'border-purple-500 shadow-lg' : 'border-gray-300 dark:border-gray-600'}
      ${isValid ? 'bg-white dark:bg-gray-800' : 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-600'}
      hover:shadow-md cursor-pointer
    `}>
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-purple-500 !border-2 !border-white"
      />
      
      <div className="flex items-center space-x-2 mb-2">
        <Zap className="w-4 h-4 text-purple-500" />
        <span className="font-medium text-gray-900 dark:text-white">
          {data.label}
        </span>
      </div>
      
      {data.toolName && (
        <Badge color="blue" size="sm" className="mb-2">
          {data.toolName}
        </Badge>
      )}
      
      {data.description && (
        <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
          {data.description}
        </p>
      )}
      
      {!isValid && data.errors && (
        <div className="text-xs text-red-600 dark:text-red-400">
          {data.errors.join(', ')}
        </div>
      )}
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-purple-500 !border-2 !border-white"
      />
    </div>
  );
};

const ConditionNode: React.FC<NodeProps<WorkflowNodeData>> = ({ data, id, selected }) => {
  const isValid = data.isValid !== false;
  
  return (
    <div className={`
      relative group min-w-[180px] p-4 rounded-lg border-2 transition-all duration-200
      ${selected ? 'border-orange-500 shadow-lg' : 'border-gray-300 dark:border-gray-600'}
      ${isValid ? 'bg-white dark:bg-gray-800' : 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-600'}
      hover:shadow-md cursor-pointer transform rotate-45 origin-center
    `}>
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-orange-500 !border-2 !border-white"
      />
      
      <div className="transform -rotate-45 text-center">
        <div className="flex items-center justify-center space-x-1 mb-1">
          <GitBranch className="w-4 h-4 text-orange-500" />
          <span className="font-medium text-gray-900 dark:text-white text-sm">
            {data.label}
          </span>
        </div>
        
        {data.description && (
          <p className="text-xs text-gray-600 dark:text-gray-400">
            {data.description}
          </p>
        )}
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        id="success"
        className="w-3 h-3 !bg-green-500 !border-2 !border-white"
      />
      <Handle
        type="source"
        position={Position.Left}
        id="failure"
        className="w-3 h-3 !bg-red-500 !border-2 !border-white"
      />
    </div>
  );
};

const ParallelNode: React.FC<NodeProps<WorkflowNodeData>> = ({ data, id, selected }) => {
  return (
    <div className={`
      relative group min-w-[200px] p-4 rounded-lg border-2 transition-all duration-200
      ${selected ? 'border-blue-500 shadow-lg' : 'border-gray-300 dark:border-gray-600'}
      bg-white dark:bg-gray-800 hover:shadow-md cursor-pointer
    `}>
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-blue-500 !border-2 !border-white"
      />
      
      <div className="flex items-center space-x-2 mb-2">
        <List className="w-4 h-4 text-blue-500" />
        <span className="font-medium text-gray-900 dark:text-white">
          {data.label}
        </span>
      </div>
      
      <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
        Parallel Execution
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-blue-500 !border-2 !border-white"
      />
    </div>
  );
};

const LoopNode: React.FC<NodeProps<WorkflowNodeData>> = ({ data, id, selected }) => {
  return (
    <div className={`
      relative group min-w-[200px] p-4 rounded-lg border-2 transition-all duration-200
      ${selected ? 'border-green-500 shadow-lg' : 'border-gray-300 dark:border-gray-600'}
      bg-white dark:bg-gray-800 hover:shadow-md cursor-pointer
    `}>
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-green-500 !border-2 !border-white"
      />
      
      <div className="flex items-center space-x-2 mb-2">
        <RotateCcw className="w-4 h-4 text-green-500" />
        <span className="font-medium text-gray-900 dark:text-white">
          {data.label}
        </span>
      </div>
      
      <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
        Loop Iteration
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-green-500 !border-2 !border-white"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="loop"
        className="w-3 h-3 !bg-green-500 !border-2 !border-white"
      />
    </div>
  );
};

const WorkflowLinkNode: React.FC<NodeProps<WorkflowNodeData>> = ({ data, id, selected }) => {
  return (
    <div className={`
      relative group min-w-[200px] p-4 rounded-lg border-2 transition-all duration-200
      ${selected ? 'border-cyan-500 shadow-lg' : 'border-gray-300 dark:border-gray-600'}
      bg-white dark:bg-gray-800 hover:shadow-md cursor-pointer
    `}>
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-cyan-500 !border-2 !border-white"
      />
      
      <div className="flex items-center space-x-2 mb-2">
        <Link className="w-4 h-4 text-cyan-500" />
        <span className="font-medium text-gray-900 dark:text-white">
          {data.label}
        </span>
      </div>
      
      <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
        Sub-workflow
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-cyan-500 !border-2 !border-white"
      />
    </div>
  );
};

// Node types mapping
const nodeTypes = {
  action: ActionNode,
  condition: ConditionNode,
  parallel: ParallelNode,
  loop: LoopNode,
  workflow_link: WorkflowLinkNode,
};

// Step palette component
const StepPalette: React.FC<{
  onAddStep: (stepType: WorkflowStepType) => void;
  availableTools: MCPTool[];
}> = ({ onAddStep, availableTools }) => {
  const stepTypes = [
    { type: WorkflowStepType.ACTION, icon: Zap, label: 'Action', color: 'purple' as AccentColor },
    { type: WorkflowStepType.CONDITION, icon: GitBranch, label: 'Condition', color: 'orange' as AccentColor },
    { type: WorkflowStepType.PARALLEL, icon: List, label: 'Parallel', color: 'blue' as AccentColor },
    { type: WorkflowStepType.LOOP, icon: RotateCcw, label: 'Loop', color: 'green' as AccentColor },
    { type: WorkflowStepType.WORKFLOW_LINK, icon: Link, label: 'Sub-workflow', color: 'cyan' as AccentColor },
  ];

  return (
    <Card accentColor="purple" className="p-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Step Palette
      </h3>
      
      <div className="space-y-2">
        {stepTypes.map(({ type, icon: Icon, label, color }) => (
          <Button
            key={type}
            variant="ghost"
            size="sm"
            onClick={() => onAddStep(type)}
            icon={<Icon className="w-4 h-4" />}
            accentColor={color}
            className="w-full justify-start"
          >
            {label}
          </Button>
        ))}
      </div>
      
      <div className="mt-6">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Available Tools ({availableTools.length})
        </h4>
        <div className="max-h-40 overflow-y-auto space-y-1">
          {availableTools.slice(0, 10).map((tool) => (
            <div
              key={tool.name}
              className="text-xs p-2 bg-gray-50 dark:bg-gray-700 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
              onClick={() => onAddStep(WorkflowStepType.ACTION)}
            >
              <div className="font-medium">{tool.name}</div>
              <div className="text-gray-600 dark:text-gray-400">{tool.category}</div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};

// Main workflow designer component
const WorkflowDesignerInner: React.FC<WorkflowDesignerProps> = ({
  workflow,
  onSave,
  onCancel,
  onPreview,
  onTest,
  isLoading = false,
  isDarkMode = false
}) => {
  const [nodes, setNodes] = useState<Node<WorkflowNodeData>[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node<WorkflowNodeData> | null>(null);
  const [availableTools, setAvailableTools] = useState<MCPTool[]>([]);
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

  const { showToast } = useToast();
  const reactFlowInstance = useReactFlow();
  const nodeIdCounter = useRef(0);

  // Load available MCP tools
  React.useEffect(() => {
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

  // Convert workflow steps to nodes and edges
  React.useEffect(() => {
    if (workflow?.steps) {
      const newNodes: Node<WorkflowNodeData>[] = [];
      const newEdges: Edge[] = [];
      
      workflow.steps.forEach((step, index) => {
        const nodeId = `step-${index}`;
        newNodes.push({
          id: nodeId,
          type: step.type,
          position: { x: 100 + (index % 3) * 250, y: 100 + Math.floor(index / 3) * 150 },
          data: {
            label: step.title,
            stepType: step.type,
            toolName: step.tool_name,
            description: step.description,
            parameters: step.parameters,
            isValid: true
          }
        });
        
        // Create edges based on step connections
        if (index > 0) {
          newEdges.push({
            id: `edge-${index}`,
            source: `step-${index - 1}`,
            target: nodeId,
            type: 'smoothstep',
            animated: true,
            markerEnd: { type: MarkerType.ArrowClosed }
          });
        }
      });
      
      setNodes(newNodes);
      setEdges(newEdges);
      nodeIdCounter.current = workflow.steps.length;
    }
  }, [workflow]);

  // Handle node changes
  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  // Handle edge changes
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  // Handle new connections
  const onConnect = useCallback(
    (connection: Connection) => {
      const edge = {
        ...connection,
        type: 'smoothstep',
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed }
      };
      setEdges((eds) => addEdge(edge, eds));
    },
    []
  );

  // Add new step to canvas
  const handleAddStep = useCallback((stepType: WorkflowStepType) => {
    const nodeId = `step-${nodeIdCounter.current++}`;
    const newNode: Node<WorkflowNodeData> = {
      id: nodeId,
      type: stepType,
      position: { x: 100 + (nodes.length % 3) * 250, y: 100 + Math.floor(nodes.length / 3) * 150 },
      data: {
        label: `New ${stepType}`,
        stepType,
        isValid: false,
        errors: ['Step needs configuration']
      }
    };
    
    setNodes((nds) => [...nds, newNode]);
    setSelectedNode(newNode);
  }, [nodes.length]);

  // Handle node selection
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node<WorkflowNodeData>) => {
    setSelectedNode(node);
  }, []);

  // Convert nodes and edges back to workflow steps
  const convertToWorkflowSteps = useCallback((): WorkflowStep[] => {
    return nodes.map((node, index) => ({
      name: `step_${index + 1}`,
      title: node.data.label,
      type: node.data.stepType,
      description: node.data.description,
      tool_name: node.data.toolName,
      parameters: node.data.parameters || {},
      on_success: edges.find(e => e.source === node.id)?.target,
      on_failure: edges.find(e => e.source === node.id && e.sourceHandle === 'failure')?.target
    }));
  }, [nodes, edges]);

  // Handle save
  const handleSave = useCallback(async () => {
    try {
      const steps = convertToWorkflowSteps();
      const updatedWorkflow = {
        ...workflowData,
        steps
      };
      
      await onSave?.(updatedWorkflow);
      showToast('Workflow saved successfully', 'success');
    } catch (error) {
      console.error('Failed to save workflow:', error);
      showToast('Failed to save workflow', 'error');
    }
  }, [workflowData, convertToWorkflowSteps, onSave, showToast]);

  // Handle preview
  const handlePreview = useCallback(() => {
    const steps = convertToWorkflowSteps();
    const updatedWorkflow = {
      ...workflowData,
      steps
    };
    onPreview?.(updatedWorkflow);
  }, [workflowData, convertToWorkflowSteps, onPreview]);

  return (
    <div className="h-screen flex">
      {/* Left Sidebar - Step Palette */}
      <div className="w-80 border-r border-gray-200 dark:border-gray-700 p-4 overflow-y-auto">
        <StepPalette onAddStep={handleAddStep} availableTools={availableTools} />
        
        {/* Node Properties Panel */}
        {selectedNode && (
          <Card accentColor="blue" className="p-4 mt-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Step Properties
            </h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={selectedNode.data.label}
                  onChange={(e) => {
                    const updatedNode = {
                      ...selectedNode,
                      data: { ...selectedNode.data, label: e.target.value }
                    };
                    setSelectedNode(updatedNode);
                    setNodes(nds => nds.map(n => n.id === selectedNode.id ? updatedNode : n));
                  }}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={selectedNode.data.description || ''}
                  onChange={(e) => {
                    const updatedNode = {
                      ...selectedNode,
                      data: { ...selectedNode.data, description: e.target.value }
                    };
                    setSelectedNode(updatedNode);
                    setNodes(nds => nds.map(n => n.id === selectedNode.id ? updatedNode : n));
                  }}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>
              
              {selectedNode.data.stepType === WorkflowStepType.ACTION && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Tool
                  </label>
                  <select
                    value={selectedNode.data.toolName || ''}
                    onChange={(e) => {
                      const updatedNode = {
                        ...selectedNode,
                        data: { ...selectedNode.data, toolName: e.target.value }
                      };
                      setSelectedNode(updatedNode);
                      setNodes(nds => nds.map(n => n.id === selectedNode.id ? updatedNode : n));
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    <option value="">Select a tool...</option>
                    {availableTools.map(tool => (
                      <option key={tool.name} value={tool.name}>
                        {tool.name} ({tool.category})
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>

      {/* Main Canvas Area */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Workflow Designer
              </h2>
              <Badge color="blue" size="sm">
                {nodes.length} steps
              </Badge>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handlePreview}
                icon={<Eye className="w-4 h-4" />}
              >
                Preview
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onTest?.(workflowData)}
                icon={<Play className="w-4 h-4" />}
              >
                Test
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={onCancel}
              >
                Cancel
              </Button>
              
              <Button
                variant="primary"
                size="sm"
                onClick={handleSave}
                disabled={isLoading}
                icon={<Save className="w-4 h-4" />}
                accentColor="purple"
              >
                Save Workflow
              </Button>
            </div>
          </div>
        </div>

        {/* React Flow Canvas */}
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            connectionLineType={ConnectionLineType.SmoothStep}
            defaultEdgeOptions={{
              type: 'smoothstep',
              animated: true,
              markerEnd: { type: MarkerType.ArrowClosed }
            }}
            fitView
            attributionPosition="bottom-right"
          >
            <Background color="#aaa" gap={16} />
            <Controls className="!bg-white/70 dark:!bg-black/70 !border-gray-300 dark:!border-gray-800" />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
};

// Wrapper component with ReactFlowProvider
export const WorkflowDesigner: React.FC<WorkflowDesignerProps> = (props) => {
  return (
    <ReactFlowProvider>
      <WorkflowDesignerInner {...props} />
    </ReactFlowProvider>
  );
};
