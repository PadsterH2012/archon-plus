export interface WorkflowTask {
  id: string;
  title: string;
  description: string;
  assignee: 'User' | 'Archon' | 'AI IDE Agent' | 'prp-executor' | 'prp-validator' | 'archon-task-manager';
  estimatedDuration: number; // in minutes
  dependencies: string[]; // task IDs this task depends on
  prerequisites: string[]; // conditions that must be met
  validationSteps: string[]; // steps to verify task completion
  tools?: string[]; // MCP tools or external tools needed
  conditional?: {
    condition: string; // condition to check
    onTrue?: string[]; // task IDs to execute if true
    onFalse?: string[]; // task IDs to execute if false
  };
  metadata?: {
    category: string;
    priority: 'low' | 'medium' | 'high' | 'critical';
    tags: string[];
  };
}

export interface WorkflowTaskGroup {
  id: string;
  name: string;
  description: string;
  category: 'documentation' | 'deployment' | 'infrastructure' | 'operations' | 'testing' | 'security';
  version: string;
  author: string;
  tasks: WorkflowTask[];
  entryPoints: string[]; // task IDs that can be started first
  exitPoints: string[]; // task IDs that complete the group
  requiredTools: string[]; // MCP tools or external tools needed for this group
  applicablePhases: ('planning' | 'development' | 'testing' | 'deployment' | 'maintenance')[];
  metadata: {
    created: string;
    updated: string;
    usageCount: number;
    successRate: number;
  };
}

export interface WorkflowExecution {
  id: string;
  projectId: string;
  taskGroupId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt?: string;
  completedAt?: string;
  currentTask?: string;
  completedTasks: string[];
  failedTasks: string[];
  context: Record<string, any>; // project-specific context
  results: Record<string, any>; // task execution results
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  taskGroups: string[]; // task group IDs
  defaultContext: Record<string, any>;
  applicableProjectTypes: string[];
}
