/**
 * Workflow Service
 * 
 * Service for communicating with the workflow API endpoints
 * Handles all workflow-related API operations
 */

import { 
  WorkflowTemplate, 
  WorkflowExecution, 
  StepExecution,
  WorkflowListResponse,
  ExecutionListResponse,
  WorkflowFilters,
  ExecutionFilters,
  WorkflowValidationResult,
  MCPTool
} from '../components/workflow/types/workflow.types';

const API_BASE = '/api/workflows';

class WorkflowService {
  
  // =====================================================
  // WORKFLOW TEMPLATE OPERATIONS
  // =====================================================

  /**
   * List workflow templates with filtering and pagination
   */
  async listWorkflows(filters: WorkflowFilters = {}, page = 1, perPage = 20): Promise<WorkflowListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
      ...(filters.search && { search: filters.search }),
      ...(filters.category && { category: filters.category }),
      ...(filters.status && { status: filters.status }),
      ...(filters.created_by && { created_by: filters.created_by }),
      ...(filters.is_public !== undefined && { is_public: filters.is_public.toString() })
    });

    const response = await fetch(`${API_BASE}?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to list workflows: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get a specific workflow template by ID
   */
  async getWorkflow(workflowId: string): Promise<{ workflow: WorkflowTemplate; validation_result?: WorkflowValidationResult }> {
    const response = await fetch(`${API_BASE}/${workflowId}`);
    if (!response.ok) {
      throw new Error(`Failed to get workflow: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Create a new workflow template
   */
  async createWorkflow(workflow: Partial<WorkflowTemplate>): Promise<{ message: string; workflow: WorkflowTemplate }> {
    const response = await fetch(API_BASE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(workflow),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `Failed to create workflow: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Update an existing workflow template
   */
  async updateWorkflow(workflowId: string, updates: Partial<WorkflowTemplate>): Promise<{ message: string; workflow: WorkflowTemplate }> {
    const response = await fetch(`${API_BASE}/${workflowId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `Failed to update workflow: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Delete a workflow template
   */
  async deleteWorkflow(workflowId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE}/${workflowId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `Failed to delete workflow: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Validate a workflow template
   */
  async validateWorkflow(workflowId: string): Promise<WorkflowValidationResult> {
    const response = await fetch(`${API_BASE}/${workflowId}/validate`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to validate workflow: ${response.statusText}`);
    }
    return response.json();
  }

  // =====================================================
  // WORKFLOW EXECUTION OPERATIONS
  // =====================================================

  /**
   * Execute a workflow template
   */
  async executeWorkflow(
    workflowId: string, 
    parameters: Record<string, any>, 
    triggeredBy = 'user',
    triggerContext?: Record<string, any>
  ): Promise<{ message: string; execution_id: string; status: string; workflow_id: string }> {
    const response = await fetch(`${API_BASE}/${workflowId}/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        workflow_template_id: workflowId,
        triggered_by: triggeredBy,
        input_parameters: parameters,
        trigger_context: triggerContext
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `Failed to execute workflow: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get workflow execution status and details
   */
  async getExecutionStatus(executionId: string): Promise<{ execution: WorkflowExecution; step_executions: StepExecution[]; total_steps: number }> {
    const response = await fetch(`${API_BASE}/executions/${executionId}`);
    if (!response.ok) {
      throw new Error(`Failed to get execution status: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * List workflow executions with filtering
   */
  async listExecutions(filters: ExecutionFilters = {}, page = 1, perPage = 20): Promise<ExecutionListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
      ...(filters.workflow_id && { workflow_id: filters.workflow_id }),
      ...(filters.status && { status: filters.status }),
      ...(filters.triggered_by && { triggered_by: filters.triggered_by })
    });

    const response = await fetch(`${API_BASE}/executions?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to list executions: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Cancel a running workflow execution
   */
  async cancelExecution(executionId: string): Promise<{ message: string; execution_id: string; status: string }> {
    const response = await fetch(`${API_BASE}/executions/${executionId}/cancel`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `Failed to cancel execution: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Pause a running workflow execution
   */
  async pauseExecution(executionId: string): Promise<{ message: string; execution_id: string; status: string }> {
    const response = await fetch(`${API_BASE}/executions/${executionId}/pause`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `Failed to pause execution: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Resume a paused workflow execution
   */
  async resumeExecution(executionId: string): Promise<{ message: string; execution_id: string; status: string }> {
    const response = await fetch(`${API_BASE}/executions/${executionId}/resume`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `Failed to resume execution: ${response.statusText}`);
    }
    return response.json();
  }

  // =====================================================
  // SEARCH AND DISCOVERY OPERATIONS
  // =====================================================

  /**
   * Search workflow templates
   */
  async searchWorkflows(query: string, filters: Partial<WorkflowFilters> = {}): Promise<{ workflows: WorkflowTemplate[]; total_count: number; query: string }> {
    const response = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        ...filters
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to search workflows: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get available workflow categories
   */
  async getCategories(): Promise<{ categories: string[]; total_count: number }> {
    const response = await fetch(`${API_BASE}/categories`);
    if (!response.ok) {
      throw new Error(`Failed to get categories: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get example workflows
   */
  async getExamples(): Promise<{ examples: any[]; total_count: number; standard_count: number; mcp_count: number }> {
    const response = await fetch(`${API_BASE}/examples`);
    if (!response.ok) {
      throw new Error(`Failed to get examples: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get a specific example workflow
   */
  async getExample(exampleName: string): Promise<{ example: WorkflowTemplate; name: string; type: string }> {
    const response = await fetch(`${API_BASE}/examples/${exampleName}`);
    if (!response.ok) {
      throw new Error(`Failed to get example: ${response.statusText}`);
    }
    return response.json();
  }

  // =====================================================
  // MCP TOOL INTEGRATION OPERATIONS
  // =====================================================

  /**
   * Get available MCP tools
   */
  async getMCPTools(): Promise<{ tools: MCPTool[]; tools_by_category: Record<string, MCPTool[]>; total_count: number; categories: string[] }> {
    const response = await fetch(`${API_BASE}/tools`);
    if (!response.ok) {
      throw new Error(`Failed to get MCP tools: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get specific MCP tool information
   */
  async getMCPTool(toolName: string): Promise<{ tool: MCPTool }> {
    const response = await fetch(`${API_BASE}/tools/${toolName}`);
    if (!response.ok) {
      throw new Error(`Failed to get MCP tool: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get MCP tools by category
   */
  async getMCPToolsByCategory(category: string): Promise<{ tools: MCPTool[]; category: string; total_count: number }> {
    const response = await fetch(`${API_BASE}/tools/categories/${category}`);
    if (!response.ok) {
      throw new Error(`Failed to get tools by category: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get MCP tool suggestions based on description
   */
  async suggestMCPTools(description: string): Promise<{ suggestions: any[]; description: string; total_count: number }> {
    const response = await fetch(`${API_BASE}/tools/suggest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ description }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get tool suggestions: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Validate workflow MCP tools
   */
  async validateWorkflowTools(workflowId: string): Promise<{ workflow_id: string; validation: any; steps_validated: number }> {
    const response = await fetch(`${API_BASE}/${workflowId}/validate-tools`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to validate workflow tools: ${response.statusText}`);
    }
    return response.json();
  }

  // =====================================================
  // UTILITY METHODS
  // =====================================================

  /**
   * Check workflow API health
   */
  async checkHealth(): Promise<{ status: string; service: string; timestamp: string }> {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Format execution duration
   */
  formatExecutionDuration(startedAt?: string, completedAt?: string): string {
    if (!startedAt) return 'Not started';
    
    const start = new Date(startedAt);
    const end = completedAt ? new Date(completedAt) : new Date();
    const duration = end.getTime() - start.getTime();
    
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }

  /**
   * Get status color for UI components
   */
  getStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'green';
      case 'running':
        return 'blue';
      case 'pending':
        return 'orange';
      case 'failed':
        return 'red';
      case 'cancelled':
        return 'gray';
      case 'paused':
        return 'yellow';
      default:
        return 'gray';
    }
  }

  /**
   * Get step type icon
   */
  getStepTypeIcon(stepType: string): string {
    switch (stepType) {
      case 'action':
        return '⚡';
      case 'condition':
        return '🔀';
      case 'parallel':
        return '⚡⚡';
      case 'loop':
        return '🔄';
      case 'workflow_link':
        return '🔗';
      default:
        return '📋';
    }
  }
}

// Export singleton instance
export const workflowService = new WorkflowService();
export default workflowService;
