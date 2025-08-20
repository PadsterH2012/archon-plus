// Template Management Service Layer
// Integrates with MCP backend tools via API wrapper

import type {
  TemplateDefinition,
  TemplateApplication,
  TemplateType,
  TemplateStatus,
  CreateTemplateDefinitionRequest,
  UpdateTemplateDefinitionRequest,
  ApplyTemplateRequest,
  TemplateDefinitionResponse,
  TemplateApplicationResponse,
  TemplateInheritanceChain
} from '../types/component';

// API configuration - use relative URL to go through Vite proxy
const API_BASE_URL = '/api';

// Error classes
export class TemplateServiceError extends Error {
  constructor(message: string, public code?: string, public statusCode?: number) {
    super(message);
    this.name = 'TemplateServiceError';
  }
}

export class TemplateValidationError extends TemplateServiceError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR', 400);
    this.name = 'TemplateValidationError';
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
      
      throw new TemplateServiceError(
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
        throw new TemplateServiceError(
          toolResponse.error || 'MCP tool execution failed',
          'MCP_TOOL_ERROR',
          500
        );
      }
      
      return toolResponse;
    }
    
    throw new TemplateServiceError(
      'Invalid MCP tool response format',
      'INVALID_RESPONSE',
      500
    );
  } catch (error) {
    if (error instanceof TemplateServiceError) {
      throw error;
    }
    
    throw new TemplateServiceError(
      `Failed to call MCP tool ${toolName}: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'NETWORK_ERROR',
      500
    );
  }
}

// Template Management Service
export const templateService = {
  // ==================== TEMPLATE OPERATIONS ====================

  /**
   * List templates with filtering
   */
  async listTemplates(
    options: {
      filterBy?: 'type' | 'status' | 'public';
      filterValue?: string;
      includeInheritance?: boolean;
      page?: number;
      perPage?: number;
    } = {}
  ): Promise<{ templates: TemplateDefinition[]; totalCount: number; pagination?: any }> {
    try {
      const params = {
        action: 'list',
        filter_by: options.filterBy,
        filter_value: options.filterValue,
        include_inheritance: options.includeInheritance ?? true,
        page: options.page ?? 1,
        per_page: options.perPage ?? 50
      };

      const response = await callMCPTool('manage_template', params);
      
      return {
        templates: response.templates || [],
        totalCount: response.total_count || 0,
        pagination: response.pagination
      };
    } catch (error) {
      console.error('Failed to list templates:', error);
      throw error;
    }
  },

  /**
   * Get a specific template by ID
   */
  async getTemplate(
    templateId: string,
    includeInheritance: boolean = true
  ): Promise<TemplateDefinition> {
    try {
      const response = await callMCPTool('manage_template', {
        action: 'get',
        template_id: templateId,
        include_inheritance: includeInheritance
      });
      
      if (!response.template) {
        throw new TemplateServiceError(
          `Template ${templateId} not found`,
          'NOT_FOUND',
          404
        );
      }
      
      return response.template;
    } catch (error) {
      console.error(`Failed to get template ${templateId}:`, error);
      throw error;
    }
  },

  /**
   * Create a new template
   */
  async createTemplate(templateData: CreateTemplateDefinitionRequest): Promise<TemplateDefinition> {
    try {
      const response = await callMCPTool('manage_template', {
        action: 'create',
        ...templateData
      });
      
      if (!response.template) {
        throw new TemplateServiceError(
          'Failed to create template: No template returned',
          'CREATION_FAILED',
          500
        );
      }
      
      return response.template;
    } catch (error) {
      console.error('Failed to create template:', error);
      throw error;
    }
  },

  /**
   * Update an existing template
   */
  async updateTemplate(
    templateId: string, 
    updates: UpdateTemplateDefinitionRequest
  ): Promise<TemplateDefinition> {
    try {
      const response = await callMCPTool('manage_template', {
        action: 'update',
        template_id: templateId,
        ...updates
      });
      
      if (!response.template) {
        throw new TemplateServiceError(
          'Failed to update template: No template returned',
          'UPDATE_FAILED',
          500
        );
      }
      
      return response.template;
    } catch (error) {
      console.error(`Failed to update template ${templateId}:`, error);
      throw error;
    }
  },

  /**
   * Delete a template
   */
  async deleteTemplate(templateId: string): Promise<void> {
    try {
      await callMCPTool('manage_template', {
        action: 'delete',
        template_id: templateId
      });
    } catch (error) {
      console.error(`Failed to delete template ${templateId}:`, error);
      throw error;
    }
  },

  /**
   * Resolve template inheritance chain
   */
  async resolveTemplateInheritance(templateId: string): Promise<TemplateInheritanceChain> {
    try {
      const response = await callMCPTool('manage_template', {
        action: 'resolve',
        template_id: templateId
      });
      
      return {
        templates: response.inheritance_chain || [],
        resolved_config: response.resolved_config || {
          workflow_assignments: {},
          component_templates: {},
          inheritance_rules: {}
        },
        conflicts: response.conflicts || []
      };
    } catch (error) {
      console.error(`Failed to resolve template inheritance for ${templateId}:`, error);
      throw error;
    }
  },

  // ==================== TEMPLATE APPLICATION OPERATIONS ====================

  /**
   * Apply template to project or component
   */
  async applyTemplate(
    templateId: string,
    options: {
      projectId?: string;
      componentId?: string;
      customizations?: Record<string, any>;
      previewOnly?: boolean;
      appliedBy?: string;
    }
  ): Promise<TemplateApplication | { preview: any; conflicts: string[] }> {
    try {
      const params = {
        template_id: templateId,
        project_id: options.projectId,
        component_id: options.componentId,
        customizations: options.customizations || {},
        preview_only: options.previewOnly || false,
        applied_by: options.appliedBy || 'user'
      };

      const response = await callMCPTool('apply_template', params);
      
      if (options.previewOnly) {
        return {
          preview: response.preview,
          conflicts: response.conflicts || []
        };
      }
      
      if (!response.application) {
        throw new TemplateServiceError(
          'Failed to apply template: No application returned',
          'APPLICATION_FAILED',
          500
        );
      }
      
      return response.application;
    } catch (error) {
      console.error(`Failed to apply template ${templateId}:`, error);
      throw error;
    }
  },

  /**
   * Preview template application without applying
   */
  async previewTemplateApplication(
    templateId: string,
    options: {
      projectId?: string;
      componentId?: string;
      customizations?: Record<string, any>;
    }
  ): Promise<{ preview: any; conflicts: string[] }> {
    return this.applyTemplate(templateId, {
      ...options,
      previewOnly: true
    }) as Promise<{ preview: any; conflicts: string[] }>;
  },

  // ==================== UTILITY METHODS ====================

  /**
   * Get templates by type
   */
  async getTemplatesByType(templateType: TemplateType): Promise<TemplateDefinition[]> {
    const { templates } = await this.listTemplates({
      filterBy: 'type',
      filterValue: templateType
    });
    return templates;
  },

  /**
   * Get public templates
   */
  async getPublicTemplates(): Promise<TemplateDefinition[]> {
    const { templates } = await this.listTemplates({
      filterBy: 'public',
      filterValue: 'true'
    });
    return templates;
  },

  /**
   * Search templates by name or description
   */
  async searchTemplates(query: string): Promise<TemplateDefinition[]> {
    const { templates } = await this.listTemplates();
    
    const searchTerm = query.toLowerCase();
    return templates.filter(template => 
      template.name.toLowerCase().includes(searchTerm) ||
      template.title.toLowerCase().includes(searchTerm) ||
      template.description.toLowerCase().includes(searchTerm)
    );
  },

  /**
   * Validate template inheritance chain for circular dependencies
   */
  async validateTemplateInheritance(templateId: string): Promise<{ isValid: boolean; errors: string[] }> {
    try {
      const inheritanceChain = await this.resolveTemplateInheritance(templateId);
      
      // Check for circular dependencies
      const templateIds = inheritanceChain.templates.map(t => t.id).filter(Boolean);
      const uniqueIds = new Set(templateIds);
      
      if (templateIds.length !== uniqueIds.size) {
        return {
          isValid: false,
          errors: ['Circular dependency detected in template inheritance chain']
        };
      }
      
      return {
        isValid: true,
        errors: []
      };
    } catch (error) {
      return {
        isValid: false,
        errors: [error instanceof Error ? error.message : 'Unknown validation error']
      };
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
