import { WorkflowTaskGroup, WorkflowTask, WorkflowExecution } from '../types/workflow';
import { ALL_TASK_GROUPS } from '../data/workflowTaskGroups';

/**
 * Task Group Service
 * 
 * Manages reusable workflow task groups that can be integrated into projects.
 * Provides standardized operational workflows for documentation, deployment,
 * infrastructure, and homelab operations.
 */
export class TaskGroupService {
  private static instance: TaskGroupService;
  private taskGroups: Map<string, WorkflowTaskGroup> = new Map();
  private executions: Map<string, WorkflowExecution> = new Map();

  private constructor() {
    // Load predefined task groups
    ALL_TASK_GROUPS.forEach(group => {
      this.taskGroups.set(group.id, group);
    });
  }

  public static getInstance(): TaskGroupService {
    if (!TaskGroupService.instance) {
      TaskGroupService.instance = new TaskGroupService();
    }
    return TaskGroupService.instance;
  }

  /**
   * Get all available task groups
   */
  public getTaskGroups(): WorkflowTaskGroup[] {
    return Array.from(this.taskGroups.values());
  }

  /**
   * Get task groups by category
   */
  public getTaskGroupsByCategory(category: string): WorkflowTaskGroup[] {
    return this.getTaskGroups().filter(group => group.category === category);
  }

  /**
   * Get task groups applicable to a specific project phase
   */
  public getTaskGroupsByPhase(phase: string): WorkflowTaskGroup[] {
    return this.getTaskGroups().filter(group => 
      group.applicablePhases.includes(phase as any)
    );
  }

  /**
   * Get a specific task group by ID
   */
  public getTaskGroup(id: string): WorkflowTaskGroup | undefined {
    return this.taskGroups.get(id);
  }

  /**
   * Get task groups that require specific MCP tools
   */
  public getTaskGroupsByTool(toolName: string): WorkflowTaskGroup[] {
    return this.getTaskGroups().filter(group => 
      group.requiredTools.includes(toolName)
    );
  }

  /**
   * Create a new workflow execution from a task group
   */
  public async createExecution(
    projectId: string,
    taskGroupId: string,
    context: Record<string, any> = {}
  ): Promise<WorkflowExecution> {
    const taskGroup = this.getTaskGroup(taskGroupId);
    if (!taskGroup) {
      throw new Error(`Task group ${taskGroupId} not found`);
    }

    const execution: WorkflowExecution = {
      id: `exec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      projectId,
      taskGroupId,
      status: 'pending',
      completedTasks: [],
      failedTasks: [],
      context,
      results: {}
    };

    this.executions.set(execution.id, execution);
    return execution;
  }

  /**
   * Get the next executable tasks based on dependencies
   */
  public getNextExecutableTasks(
    execution: WorkflowExecution,
    taskGroup: WorkflowTaskGroup
  ): WorkflowTask[] {
    return taskGroup.tasks.filter(task => {
      // Skip if already completed or failed
      if (execution.completedTasks.includes(task.id) || 
          execution.failedTasks.includes(task.id)) {
        return false;
      }

      // Check if all dependencies are completed
      return task.dependencies.every(depId => 
        execution.completedTasks.includes(depId)
      );
    });
  }

  /**
   * Get execution status
   */
  public getExecution(executionId: string): WorkflowExecution | undefined {
    return this.executions.get(executionId);
  }

  /**
   * Get all executions for a project
   */
  public getProjectExecutions(projectId: string): WorkflowExecution[] {
    return Array.from(this.executions.values()).filter(
      execution => execution.projectId === projectId
    );
  }

  /**
   * Integration with Archon task system
   * Convert workflow tasks to Archon tasks
   */
  public async convertToArchonTasks(
    execution: WorkflowExecution,
    taskGroup: WorkflowTaskGroup
  ): Promise<any[]> {
    return taskGroup.tasks.map((task, index) => ({
      title: task.title,
      description: task.description,
      assignee: task.assignee,
      task_order: index * 10, // Space out for insertion
      feature: taskGroup.category,
      sources: task.tools?.map(tool => ({
        url: `tool://${tool}`,
        type: 'tool',
        relevance: `Required tool for ${task.title}`
      })) || [],
      code_examples: [],
      metadata: {
        workflowTaskId: task.id,
        workflowExecutionId: execution.id,
        estimatedDuration: task.estimatedDuration,
        prerequisites: task.prerequisites,
        validationSteps: task.validationSteps,
        category: task.metadata?.category,
        priority: task.metadata?.priority,
        tags: task.metadata?.tags
      }
    }));
  }

  /**
   * Validate that all required tools are available for a task group
   */
  public async validateTaskGroupTools(taskGroupId: string): Promise<{
    valid: boolean;
    missingTools: string[];
    availableTools: string[];
  }> {
    const taskGroup = this.getTaskGroup(taskGroupId);
    if (!taskGroup) {
      throw new Error(`Task group ${taskGroupId} not found`);
    }

    // In a real implementation, this would check with the MCP service
    // For now, we'll assume all tools are available
    const availableTools = taskGroup.requiredTools;
    const missingTools: string[] = [];

    return {
      valid: missingTools.length === 0,
      missingTools,
      availableTools
    };
  }

  /**
   * Get task group statistics
   */
  public getTaskGroupStats(taskGroupId: string): {
    totalTasks: number;
    estimatedDuration: number;
    requiredTools: string[];
    categories: string[];
    priorities: string[];
  } | null {
    const taskGroup = this.getTaskGroup(taskGroupId);
    if (!taskGroup) {
      return null;
    }

    const totalTasks = taskGroup.tasks.length;
    const estimatedDuration = taskGroup.tasks.reduce(
      (sum, task) => sum + task.estimatedDuration, 0
    );
    const categories = [...new Set(taskGroup.tasks.map(t => t.metadata?.category).filter(Boolean))];
    const priorities = [...new Set(taskGroup.tasks.map(t => t.metadata?.priority).filter(Boolean))];

    return {
      totalTasks,
      estimatedDuration,
      requiredTools: taskGroup.requiredTools,
      categories,
      priorities
    };
  }

  /**
   * Search task groups by name, description, or tags
   */
  public searchTaskGroups(query: string): WorkflowTaskGroup[] {
    const lowerQuery = query.toLowerCase();
    return this.getTaskGroups().filter(group => 
      group.name.toLowerCase().includes(lowerQuery) ||
      group.description.toLowerCase().includes(lowerQuery) ||
      group.tasks.some(task => 
        task.title.toLowerCase().includes(lowerQuery) ||
        task.description.toLowerCase().includes(lowerQuery) ||
        task.metadata?.tags?.some(tag => tag.toLowerCase().includes(lowerQuery))
      )
    );
  }

  /**
   * Get recommended task groups for a project context
   */
  public getRecommendedTaskGroups(context: {
    projectType?: string;
    phase?: string;
    hasAPI?: boolean;
    hasDatabase?: boolean;
    requiresDeployment?: boolean;
    isHomelabProject?: boolean;
  }): WorkflowTaskGroup[] {
    let recommended = this.getTaskGroups();

    // Filter by phase if specified
    if (context.phase) {
      recommended = recommended.filter(group => 
        group.applicablePhases.includes(context.phase as any)
      );
    }

    // Recommend based on project characteristics
    if (context.hasAPI || context.hasDatabase) {
      // Prioritize documentation and testing groups
      recommended = recommended.filter(group => 
        ['documentation', 'testing'].includes(group.category)
      );
    }

    if (context.requiresDeployment) {
      // Include deployment and infrastructure groups
      recommended = recommended.filter(group => 
        ['deployment', 'infrastructure'].includes(group.category)
      );
    }

    if (context.isHomelabProject) {
      // Include homelab operations
      recommended = recommended.filter(group => 
        group.category === 'operations' || group.id === 'homelab-operations'
      );
    }

    return recommended;
  }
}
