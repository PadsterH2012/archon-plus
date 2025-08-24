/**
 * Issue Service
 *
 * Service for managing issues through MCP tools integration.
 * Provides methods for querying, creating, updating, and managing issues.
 */

import {
  Issue,
  QueryIssuesResponse,
  UpdateIssueStatusResponse,
  CreateIssueResponse,
  GetIssueHistoryResponse,
  CreateIssueRequest,
  UpdateIssueRequest
} from '../types/issue';
import { mcpClientService } from './mcpClientService';

// Use relative API path to go through Vite proxy and avoid CORS issues
const API_BASE_URL = '/api';

export class IssueServiceError extends Error {
  constructor(
    message: string,
    public code: string = 'UNKNOWN_ERROR',
    public statusCode: number = 500
  ) {
    super(message);
    this.name = 'IssueServiceError';
  }
}

// Helper function to call MCP tools via MCP Client Service (follows Archon standards)
async function callMCPTool<T = any>(toolName: string, params: Record<string, any>): Promise<T> {
  try {
    console.log(`[IssueService] Calling MCP tool via client service: ${toolName}`, params);

    // Get the default Archon MCP client
    const clients = await mcpClientService.getClients();
    const archonClient = clients.find(client => client.is_default || client.name.toLowerCase().includes('archon'));

    if (!archonClient) {
      throw new IssueServiceError(
        'No Archon MCP client found. Please ensure the MCP client is configured.',
        'CLIENT_NOT_FOUND'
      );
    }

    // Call the tool using the MCP client service (follows Archon standards)
    const result = await mcpClientService.callClientTool({
      client_id: archonClient.id,
      tool_name: toolName,
      arguments: params
    });

    console.log(`[IssueService] MCP tool ${toolName} result:`, result);

    // Parse the JSON response from MCP tool (it returns a JSON string)
    if (typeof result === 'string') {
      return JSON.parse(result);
    }

    return result;
  } catch (error) {
    if (error instanceof IssueServiceError) {
      throw error;
    }

    console.error(`[IssueService] Failed to call MCP tool ${toolName}:`, error);
    throw new IssueServiceError(
      `Failed to call MCP tool: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'MCP_CALL_FAILED'
    );
  }
}

export const issueService = {
  /**
   * Query issues by project name
   */
  async queryIssuesByProject(
    projectName: string,
    statusFilter?: string,
    limit: number = 100
  ): Promise<QueryIssuesResponse> {
    try {
      const params: Record<string, any> = {
        project_name: projectName,
        limit
      };
      
      if (statusFilter) {
        params.status_filter = statusFilter;
      }

      const response = await callMCPTool<QueryIssuesResponse>('query_issues_by_project_archon-dev', params);
      
      if (!response.success) {
        throw new IssueServiceError(
          response.error || 'Failed to query issues',
          'QUERY_FAILED'
        );
      }
      
      return response;
    } catch (error) {
      console.error('Failed to query issues by project:', error);
      throw error;
    }
  },

  /**
   * Update issue status
   */
  async updateIssueStatus(
    issueKey: string,
    newStatus: string,
    comment?: string
  ): Promise<UpdateIssueStatusResponse> {
    try {
      const params: Record<string, any> = {
        issue_key: issueKey,
        new_status: newStatus
      };
      
      if (comment) {
        params.comment = comment;
      }

      const response = await callMCPTool<UpdateIssueStatusResponse>('update_issue_status_archon-dev', params);
      
      if (!response.success) {
        throw new IssueServiceError(
          response.error || 'Failed to update issue status',
          'UPDATE_FAILED'
        );
      }
      
      return response;
    } catch (error) {
      console.error('Failed to update issue status:', error);
      throw error;
    }
  },

  /**
   * Get issue history
   */
  async getIssueHistory(
    issueKey: string,
    limit: number = 20
  ): Promise<GetIssueHistoryResponse> {
    try {
      const params = {
        issue_key: issueKey,
        limit
      };

      const response = await callMCPTool<GetIssueHistoryResponse>('get_issue_history_archon-dev', params);
      
      if (!response.success) {
        throw new IssueServiceError(
          response.error || 'Failed to get issue history',
          'HISTORY_FAILED'
        );
      }
      
      return response;
    } catch (error) {
      console.error('Failed to get issue history:', error);
      throw error;
    }
  },

  /**
   * Create issue from task
   */
  async createIssueFromTask(
    taskId: string,
    projectName: string,
    syncEnabled: boolean = true
  ): Promise<CreateIssueResponse> {
    try {
      const params = {
        task_id: taskId,
        project_name: projectName,
        sync_enabled: syncEnabled
      };

      const response = await callMCPTool<CreateIssueResponse>('create_issue_from_task_archon-dev', params);
      
      if (!response.success) {
        throw new IssueServiceError(
          response.error || 'Failed to create issue from task',
          'CREATE_FAILED'
        );
      }
      
      return response;
    } catch (error) {
      console.error('Failed to create issue from task:', error);
      throw error;
    }
  },

  /**
   * Sync task to issue
   */
  async syncTaskToIssue(
    taskId: string,
    issueStatus?: string
  ): Promise<any> {
    try {
      const params: Record<string, any> = {
        task_id: taskId
      };
      
      if (issueStatus) {
        params.issue_status = issueStatus;
      }

      const response = await callMCPTool('sync_task_to_issue_archon-dev', params);
      
      if (!response.success) {
        throw new IssueServiceError(
          response.error || 'Failed to sync task to issue',
          'SYNC_FAILED'
        );
      }
      
      return response;
    } catch (error) {
      console.error('Failed to sync task to issue:', error);
      throw error;
    }
  }
};

export default issueService;
