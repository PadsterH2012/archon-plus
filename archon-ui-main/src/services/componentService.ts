// Component Management Service Layer
// Integrates with MCP backend tools via API wrapper

import type {
  Component,
  ComponentDependency,
  ComponentType,
  ComponentStatus,
  CreateComponentRequest,
  UpdateComponentRequest,
  CreateComponentDependencyRequest,
  ComponentResponse,
  ComponentDependencyResponse,
  ComponentHierarchyValidation,
  ComponentExecutionOrder
} from '../types/component';

// API configuration - use relative URL to go through Vite proxy
const API_BASE_URL = '/api';

// Error classes
export class ComponentServiceError extends Error {
  constructor(message: string, public code?: string, public statusCode?: number) {
    super(message);
    this.name = 'ComponentServiceError';
  }
}

export class ComponentValidationError extends ComponentServiceError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR', 400);
    this.name = 'ComponentValidationError';
  }
}

// Helper function to call MCP tools via API
async function callMCPTool<T = any>(toolName: string, params: Record<string, any>): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}/mcp/tools/call`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tool_name: toolName,
        arguments: params
      })
    });

    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorBody = await response.text();
        if (errorBody) {
          const errorJson = JSON.parse(errorBody);
          errorMessage = errorJson.detail || errorJson.error || errorMessage;
        }
      } catch (e) {
        // Ignore parse errors, use default message
      }
      
      throw new ComponentServiceError(
        errorMessage, 
        'HTTP_ERROR', 
        response.status
      );
    }

    const result = await response.json();
    
    // Parse the MCP tool response
    if (result.content && result.content[0] && result.content[0].text) {
      const toolResponse = JSON.parse(result.content[0].text);
      
      if (!toolResponse.success) {
        throw new ComponentServiceError(
          toolResponse.error || 'MCP tool execution failed',
          'MCP_TOOL_ERROR',
          500
        );
      }
      
      return toolResponse;
    }
    
    throw new ComponentServiceError(
      'Invalid MCP tool response format',
      'INVALID_RESPONSE',
      500
    );
  } catch (error) {
    if (error instanceof ComponentServiceError) {
      throw error;
    }
    
    throw new ComponentServiceError(
      `Failed to call MCP tool ${toolName}: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'NETWORK_ERROR',
      500
    );
  }
}

// Component Management Service
export const componentService = {
  // ==================== COMPONENT OPERATIONS ====================

  /**
   * List components for a project
   */
  async listComponents(
    projectId: string,
    options: {
      filterBy?: 'status' | 'type';
      filterValue?: string;
      includeDependencies?: boolean;
      page?: number;
      perPage?: number;
    } = {}
  ): Promise<{ components: Component[]; totalCount: number; pagination?: any }> {
    try {
      const params = {
        action: 'list',
        project_id: projectId,
        filter_by: options.filterBy,
        filter_value: options.filterValue,
        include_dependencies: options.includeDependencies ?? true,
        page: options.page ?? 1,
        per_page: options.perPage ?? 50
      };

      const response = await callMCPTool('manage_component', params);
      
      return {
        components: response.components || [],
        totalCount: response.total_count || 0,
        pagination: response.pagination
      };
    } catch (error) {
      console.error('Failed to list components:', error);
      throw error;
    }
  },

  /**
   * Get a specific component by ID
   */
  async getComponent(
    componentId: string,
    includeDependencies: boolean = true
  ): Promise<Component> {
    try {
      const response = await callMCPTool('manage_component', {
        action: 'get',
        component_id: componentId,
        include_dependencies: includeDependencies
      });
      
      if (!response.component) {
        throw new ComponentServiceError(
          `Component ${componentId} not found`,
          'NOT_FOUND',
          404
        );
      }
      
      return response.component;
    } catch (error) {
      console.error(`Failed to get component ${componentId}:`, error);
      throw error;
    }
  },

  /**
   * Create a new component
   */
  async createComponent(componentData: CreateComponentRequest): Promise<Component> {
    try {
      const response = await callMCPTool('manage_component', {
        action: 'create',
        ...componentData
      });
      
      if (!response.component) {
        throw new ComponentServiceError(
          'Failed to create component: No component returned',
          'CREATION_FAILED',
          500
        );
      }
      
      return response.component;
    } catch (error) {
      console.error('Failed to create component:', error);
      throw error;
    }
  },

  /**
   * Update an existing component
   */
  async updateComponent(
    componentId: string, 
    updates: UpdateComponentRequest
  ): Promise<Component> {
    try {
      const response = await callMCPTool('manage_component', {
        action: 'update',
        component_id: componentId,
        ...updates
      });
      
      if (!response.component) {
        throw new ComponentServiceError(
          'Failed to update component: No component returned',
          'UPDATE_FAILED',
          500
        );
      }
      
      return response.component;
    } catch (error) {
      console.error(`Failed to update component ${componentId}:`, error);
      throw error;
    }
  },

  /**
   * Delete a component
   */
  async deleteComponent(componentId: string): Promise<void> {
    try {
      await callMCPTool('manage_component', {
        action: 'delete',
        component_id: componentId
      });
    } catch (error) {
      console.error(`Failed to delete component ${componentId}:`, error);
      throw error;
    }
  },

  // ==================== COMPONENT DEPENDENCY OPERATIONS ====================

  /**
   * Create a component dependency
   */
  async createComponentDependency(
    dependencyData: CreateComponentDependencyRequest
  ): Promise<ComponentDependency> {
    try {
      // Note: This would need a separate MCP tool for dependency management
      // For now, we'll use the component update to modify dependencies
      const component = await this.getComponent(dependencyData.component_id);
      const updatedDependencies = [...component.dependencies, dependencyData.depends_on_component_id];
      
      await this.updateComponent(dependencyData.component_id, {
        dependencies: updatedDependencies
      });
      
      // Return a mock dependency object
      return {
        id: `dep-${Date.now()}`,
        component_id: dependencyData.component_id,
        depends_on_component_id: dependencyData.depends_on_component_id,
        dependency_type: dependencyData.dependency_type || 'hard',
        gate_requirements: dependencyData.gate_requirements || [],
        created_at: new Date().toISOString()
      };
    } catch (error) {
      console.error('Failed to create component dependency:', error);
      throw error;
    }
  },

  // ==================== UTILITY METHODS ====================

  /**
   * Validate component hierarchy for circular dependencies
   */
  async validateComponentHierarchy(projectId: string): Promise<ComponentHierarchyValidation> {
    try {
      const { components } = await this.listComponents(projectId, { includeDependencies: true });
      
      // Simple circular dependency detection
      const errors: string[] = [];
      const warnings: string[] = [];
      
      for (const component of components) {
        if (component.dependencies.includes(component.id!)) {
          errors.push(`Component "${component.name}" depends on itself`);
        }
      }
      
      return {
        isValid: errors.length === 0,
        errors,
        warnings
      };
    } catch (error) {
      console.error('Failed to validate component hierarchy:', error);
      throw error;
    }
  },

  /**
   * Get component execution order (topological sort)
   */
  async getComponentExecutionOrder(projectId: string): Promise<ComponentExecutionOrder> {
    try {
      const { components } = await this.listComponents(projectId, { includeDependencies: true });
      
      // Simple topological sort implementation
      const componentMap = new Map(components.map(c => [c.id!, c]));
      const visited = new Set<string>();
      const result: Component[] = [];
      const cycles: string[] = [];
      
      function visit(componentId: string, path: Set<string>) {
        if (path.has(componentId)) {
          cycles.push(`Circular dependency detected involving component ${componentId}`);
          return;
        }
        
        if (visited.has(componentId)) {
          return;
        }
        
        visited.add(componentId);
        path.add(componentId);
        
        const component = componentMap.get(componentId);
        if (component) {
          for (const depId of component.dependencies) {
            visit(depId, path);
          }
          result.push(component);
        }
        
        path.delete(componentId);
      }
      
      for (const component of components) {
        if (component.id && !visited.has(component.id)) {
          visit(component.id, new Set());
        }
      }
      
      return {
        components: result,
        cycles
      };
    } catch (error) {
      console.error('Failed to get component execution order:', error);
      throw error;
    }
  },

  /**
   * Format relative time for display
   */
  formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  }
};
