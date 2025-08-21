// Template Management Service
// Provides API integration for template management UI components

import { callMCPTool } from '../utils/mcpClient';
import type {
  TemplateAssignment,
  TemplateResolution,
  CreateTemplateAssignmentRequest,
  UpdateTemplateAssignmentRequest,
  BulkAssignmentRequest,
  TemplateResolutionRequest,
  TemplateUsageAnalytics,
  ComponentUsageAnalytics,
  TemplateTestResult,
  ComponentTestResult,
  HierarchyLevel,
  AssignmentScope
} from '../types/templateManagement';
import type { TemplateDefinition, TemplateComponent } from '../types/component';

// =====================================================
// ERROR HANDLING
// =====================================================

export class TemplateManagementServiceError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'TemplateManagementServiceError';
  }
}

// =====================================================
// TEMPLATE ASSIGNMENT MANAGEMENT
// =====================================================

export const templateAssignmentService = {
  /**
   * Create a new template assignment
   */
  async createAssignment(assignmentData: CreateTemplateAssignmentRequest): Promise<TemplateAssignment> {
    try {
      const response = await callMCPTool('manage_template_assignment', {
        action: 'assign',
        template_name: assignmentData.template_name,
        hierarchy_level: assignmentData.hierarchy_level,
        entity_id: assignmentData.entity_id,
        assignment_scope: assignmentData.assignment_scope || 'all',
        priority: assignmentData.priority || 0,
        entity_type: assignmentData.entity_type,
        conditional_logic: assignmentData.conditional_logic,
        metadata: assignmentData.metadata,
        effective_from: assignmentData.effective_from,
        effective_until: assignmentData.effective_until,
        created_by: 'ui_user'
      });

      if (!response.assignment) {
        throw new TemplateManagementServiceError(
          'Failed to create assignment: No assignment returned',
          'CREATION_FAILED',
          500
        );
      }

      return response.assignment;
    } catch (error) {
      console.error('Failed to create template assignment:', error);
      throw error;
    }
  },

  /**
   * List template assignments with filtering
   */
  async listAssignments(options: {
    hierarchyLevel?: HierarchyLevel;
    entityId?: string;
    templateName?: string;
    isActive?: boolean;
    includeExpired?: boolean;
  } = {}): Promise<TemplateAssignment[]> {
    try {
      const response = await callMCPTool('manage_template_assignment', {
        action: 'list',
        hierarchy_level: options.hierarchyLevel,
        entity_id: options.entityId,
        template_name: options.templateName,
        is_active: options.isActive,
        include_expired: options.includeExpired || false
      });

      return response.assignments || [];
    } catch (error) {
      console.error('Failed to list template assignments:', error);
      throw error;
    }
  },

  /**
   * Get a specific template assignment
   */
  async getAssignment(assignmentId: string): Promise<TemplateAssignment> {
    try {
      const response = await callMCPTool('manage_template_assignment', {
        action: 'get',
        assignment_id: assignmentId
      });

      if (!response.assignment) {
        throw new TemplateManagementServiceError(
          `Assignment ${assignmentId} not found`,
          'NOT_FOUND',
          404
        );
      }

      return response.assignment;
    } catch (error) {
      console.error(`Failed to get assignment ${assignmentId}:`, error);
      throw error;
    }
  },

  /**
   * Update a template assignment
   */
  async updateAssignment(
    assignmentId: string,
    updates: UpdateTemplateAssignmentRequest
  ): Promise<TemplateAssignment> {
    try {
      const response = await callMCPTool('manage_template_assignment', {
        action: 'update',
        assignment_id: assignmentId,
        ...updates,
        updated_by: 'ui_user'
      });

      if (!response.assignment) {
        throw new TemplateManagementServiceError(
          'Failed to update assignment: No assignment returned',
          'UPDATE_FAILED',
          500
        );
      }

      return response.assignment;
    } catch (error) {
      console.error(`Failed to update assignment ${assignmentId}:`, error);
      throw error;
    }
  },

  /**
   * Delete a template assignment
   */
  async deleteAssignment(assignmentId: string): Promise<void> {
    try {
      const response = await callMCPTool('manage_template_assignment', {
        action: 'remove',
        assignment_id: assignmentId
      });

      if (!response.success) {
        throw new TemplateManagementServiceError(
          'Failed to delete assignment',
          'DELETE_FAILED',
          500
        );
      }
    } catch (error) {
      console.error(`Failed to delete assignment ${assignmentId}:`, error);
      throw error;
    }
  },

  /**
   * Create multiple assignments in bulk
   */
  async bulkCreateAssignments(bulkRequest: BulkAssignmentRequest): Promise<TemplateAssignment[]> {
    try {
      const response = await callMCPTool('manage_template_assignment', {
        action: 'bulk_assign',
        assignments: bulkRequest.assignments,
        created_by: bulkRequest.created_by || 'ui_user'
      });

      return response.assignments || [];
    } catch (error) {
      console.error('Failed to bulk create assignments:', error);
      throw error;
    }
  },

  /**
   * Validate all template assignments
   */
  async validateAssignments(): Promise<{
    totalAssignments: number;
    validAssignments: number;
    invalidAssignments: number;
    validationResults: Array<{
      assignmentId: string;
      templateName: string;
      valid: boolean;
      message: string;
    }>;
  }> {
    try {
      const response = await callMCPTool('manage_template_assignment', {
        action: 'validate'
      });

      return {
        totalAssignments: response.total_assignments || 0,
        validAssignments: response.valid_assignments || 0,
        invalidAssignments: response.invalid_assignments || 0,
        validationResults: response.validation_results || []
      };
    } catch (error) {
      console.error('Failed to validate assignments:', error);
      throw error;
    }
  }
};

// =====================================================
// TEMPLATE RESOLUTION SERVICE
// =====================================================

export const templateResolutionService = {
  /**
   * Resolve template for an entity
   */
  async resolveTemplate(request: TemplateResolutionRequest): Promise<TemplateResolution> {
    try {
      const response = await callMCPTool('resolve_template', {
        entity_id: request.entity_id,
        entity_type: request.entity_type,
        project_id: request.project_id,
        milestone_id: request.milestone_id,
        phase_id: request.phase_id,
        context_data: request.context_data,
        show_resolution_path: request.show_resolution_path || false
      });

      if (!response.success) {
        throw new TemplateManagementServiceError(
          'Failed to resolve template',
          'RESOLUTION_FAILED',
          500
        );
      }

      return {
        template_name: response.template_name,
        hierarchy_level: response.hierarchy_level as HierarchyLevel,
        assignment_id: response.assignment_id,
        priority: response.priority,
        resolution_path: response.resolution_path || [],
        cached: response.cached || false,
        cache_hit: response.cache_hit || false
      };
    } catch (error) {
      console.error('Failed to resolve template:', error);
      throw error;
    }
  },

  /**
   * Get resolution path for debugging
   */
  async getResolutionPath(
    entityId: string,
    entityType: string,
    projectId?: string
  ): Promise<TemplateResolution> {
    return this.resolveTemplate({
      entity_id: entityId,
      entity_type: entityType,
      project_id: projectId,
      show_resolution_path: true
    });
  }
};

// =====================================================
// TEMPLATE CACHE MANAGEMENT
// =====================================================

export const templateCacheService = {
  /**
   * Invalidate template cache
   */
  async invalidateCache(entityId?: string, hierarchyLevel?: HierarchyLevel): Promise<number> {
    try {
      const response = await callMCPTool('template_assignment_cache', {
        action: 'invalidate',
        entity_id: entityId,
        hierarchy_level: hierarchyLevel
      });

      return response.invalidated_entries || 0;
    } catch (error) {
      console.error('Failed to invalidate cache:', error);
      throw error;
    }
  },

  /**
   * Clean up expired cache entries
   */
  async cleanupCache(): Promise<number> {
    try {
      const response = await callMCPTool('template_assignment_cache', {
        action: 'cleanup'
      });

      return response.cleaned_entries || 0;
    } catch (error) {
      console.error('Failed to cleanup cache:', error);
      throw error;
    }
  },

  /**
   * Get cache statistics
   */
  async getCacheStats(): Promise<{
    totalEntries: number;
    activeEntries: number;
    expiredEntries: number;
    avgHitCount: number;
    maxHitCount: number;
    entityTypes: number;
    hierarchyLevels: number;
    cacheTtlMinutes: number;
  }> {
    try {
      const response = await callMCPTool('template_assignment_cache', {
        action: 'stats'
      });

      const stats = response.cache_statistics || {};
      return {
        totalEntries: stats.total_entries || 0,
        activeEntries: stats.active_entries || 0,
        expiredEntries: stats.expired_entries || 0,
        avgHitCount: stats.avg_hit_count || 0,
        maxHitCount: stats.max_hit_count || 0,
        entityTypes: stats.entity_types || 0,
        hierarchyLevels: stats.hierarchy_levels || 0,
        cacheTtlMinutes: stats.cache_ttl_minutes || 30
      };
    } catch (error) {
      console.error('Failed to get cache stats:', error);
      throw error;
    }
  }
};

// =====================================================
// TEMPLATE TESTING SERVICE
// =====================================================

export const templateTestingService = {
  /**
   * Test template expansion with sample task
   */
  async testTemplate(
    templateName: string,
    testTaskDescription: string,
    contextData?: Record<string, any>
  ): Promise<TemplateTestResult> {
    try {
      // Use the template injection service to test expansion
      const response = await callMCPTool('expand_template', {
        original_description: testTaskDescription,
        template_name: templateName,
        context_data: contextData || {},
        test_mode: true
      });

      if (!response.success) {
        throw new TemplateManagementServiceError(
          'Template test failed',
          'TEST_FAILED',
          500
        );
      }

      const result = response.result || {};
      return {
        success: true,
        expanded_content: result.expanded_description || '',
        expansion_time_ms: result.expansion_time_ms || 0,
        component_count: result.component_count || 0,
        validation_errors: result.validation_errors || [],
        performance_score: this.calculatePerformanceScore(result.expansion_time_ms || 0),
        quality_score: this.calculateQualityScore(result.expanded_description || '')
      };
    } catch (error) {
      console.error('Failed to test template:', error);
      return {
        success: false,
        expanded_content: '',
        expansion_time_ms: 0,
        component_count: 0,
        validation_errors: [error.message || 'Unknown error'],
        performance_score: 0,
        quality_score: 0
      };
    }
  },

  /**
   * Test component expansion
   */
  async testComponent(
    componentName: string,
    contextData?: Record<string, any>
  ): Promise<ComponentTestResult> {
    try {
      // This would test individual component expansion
      // For now, return a mock result
      return {
        success: true,
        instruction_quality: 85,
        tool_availability: [],
        estimated_accuracy: 90,
        validation_errors: []
      };
    } catch (error) {
      console.error('Failed to test component:', error);
      return {
        success: false,
        instruction_quality: 0,
        tool_availability: [],
        estimated_accuracy: 0,
        validation_errors: [error.message || 'Unknown error']
      };
    }
  },

  /**
   * Calculate performance score based on expansion time
   */
  calculatePerformanceScore(expansionTimeMs: number): number {
    if (expansionTimeMs <= 50) return 100;
    if (expansionTimeMs <= 100) return 90;
    if (expansionTimeMs <= 200) return 75;
    if (expansionTimeMs <= 500) return 50;
    return 25;
  },

  /**
   * Calculate quality score based on content analysis
   */
  calculateQualityScore(expandedContent: string): number {
    if (!expandedContent) return 0;
    
    let score = 50; // Base score
    
    // Check for structure
    if (expandedContent.includes('1.') || expandedContent.includes('- ')) score += 15;
    
    // Check for tool references
    if (expandedContent.includes('{{') && expandedContent.includes('}}')) score += 10;
    
    // Check for length (should be substantial)
    if (expandedContent.length > 500) score += 15;
    if (expandedContent.length > 1000) score += 10;
    
    return Math.min(score, 100);
  }
};

// =====================================================
// COMBINED TEMPLATE MANAGEMENT SERVICE
// =====================================================

export const templateManagementService = {
  assignments: templateAssignmentService,
  resolution: templateResolutionService,
  cache: templateCacheService,
  testing: templateTestingService
};
