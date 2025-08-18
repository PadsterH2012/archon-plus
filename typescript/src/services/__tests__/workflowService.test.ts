/**
 * WorkflowService Tests
 * 
 * Tests for the workflow service API communication layer
 */

import { workflowService } from '../workflowService';
import { WorkflowStatus, WorkflowExecutionStatus } from '../../components/workflow/types/workflow.types';

// Mock fetch globally
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('WorkflowService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const createMockResponse = (data: any, ok = true, status = 200) => ({
    ok,
    status,
    json: jest.fn().mockResolvedValue(data),
    statusText: ok ? 'OK' : 'Error'
  });

  describe('Workflow Template Operations', () => {
    describe('listWorkflows', () => {
      it('fetches workflows with default parameters', async () => {
        const mockData = {
          workflows: [],
          total_count: 0,
          page: 1,
          per_page: 20,
          has_more: false
        };

        mockFetch.mockResolvedValue(createMockResponse(mockData) as any);

        const result = await workflowService.listWorkflows();

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows?page=1&per_page=20');
        expect(result).toEqual(mockData);
      });

      it('fetches workflows with filters', async () => {
        const mockData = { workflows: [], total_count: 0, page: 1, per_page: 20, has_more: false };
        mockFetch.mockResolvedValue(createMockResponse(mockData) as any);

        const filters = {
          search: 'test',
          category: 'automation',
          status: WorkflowStatus.ACTIVE
        };

        await workflowService.listWorkflows(filters, 2, 10);

        expect(mockFetch).toHaveBeenCalledWith(
          '/api/workflows?page=2&per_page=10&search=test&category=automation&status=active'
        );
      });

      it('handles API errors', async () => {
        mockFetch.mockResolvedValue(createMockResponse({}, false, 500) as any);

        await expect(workflowService.listWorkflows()).rejects.toThrow('Failed to list workflows: Error');
      });
    });

    describe('getWorkflow', () => {
      it('fetches a specific workflow', async () => {
        const mockData = {
          workflow: { id: '1', name: 'test' },
          validation_result: { is_valid: true, errors: [], warnings: [], info: [] }
        };

        mockFetch.mockResolvedValue(createMockResponse(mockData) as any);

        const result = await workflowService.getWorkflow('1');

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/1');
        expect(result).toEqual(mockData);
      });

      it('handles not found errors', async () => {
        mockFetch.mockResolvedValue(createMockResponse({}, false, 404) as any);

        await expect(workflowService.getWorkflow('nonexistent')).rejects.toThrow('Failed to get workflow: Error');
      });
    });

    describe('createWorkflow', () => {
      it('creates a new workflow', async () => {
        const workflowData = {
          name: 'test_workflow',
          title: 'Test Workflow',
          description: 'A test workflow',
          category: 'testing',
          steps: []
        };

        const mockResponse = {
          message: 'Workflow created successfully',
          workflow: { id: '1', ...workflowData }
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.createWorkflow(workflowData);

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(workflowData)
        });
        expect(result).toEqual(mockResponse);
      });

      it('handles validation errors', async () => {
        const errorResponse = { error: 'Validation failed' };
        mockFetch.mockResolvedValue(createMockResponse(errorResponse, false, 400) as any);

        await expect(workflowService.createWorkflow({})).rejects.toThrow('Validation failed');
      });
    });

    describe('updateWorkflow', () => {
      it('updates an existing workflow', async () => {
        const updates = { title: 'Updated Title' };
        const mockResponse = {
          message: 'Workflow updated successfully',
          workflow: { id: '1', title: 'Updated Title' }
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.updateWorkflow('1', updates);

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/1', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updates)
        });
        expect(result).toEqual(mockResponse);
      });
    });

    describe('deleteWorkflow', () => {
      it('deletes a workflow', async () => {
        const mockResponse = { message: 'Workflow deleted successfully' };
        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.deleteWorkflow('1');

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/1', { method: 'DELETE' });
        expect(result).toEqual(mockResponse);
      });
    });

    describe('validateWorkflow', () => {
      it('validates a workflow', async () => {
        const mockResponse = {
          is_valid: true,
          errors: [],
          warnings: [],
          info: []
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.validateWorkflow('1');

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/1/validate', { method: 'POST' });
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('Workflow Execution Operations', () => {
    describe('executeWorkflow', () => {
      it('executes a workflow', async () => {
        const mockResponse = {
          message: 'Workflow execution started',
          execution_id: 'exec-1',
          status: 'pending',
          workflow_id: '1'
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.executeWorkflow('1', { param1: 'value1' });

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/1/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            workflow_template_id: '1',
            triggered_by: 'user',
            input_parameters: { param1: 'value1' },
            trigger_context: undefined
          })
        });
        expect(result).toEqual(mockResponse);
      });

      it('executes workflow with custom trigger context', async () => {
        const mockResponse = {
          message: 'Workflow execution started',
          execution_id: 'exec-1',
          status: 'pending',
          workflow_id: '1'
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        await workflowService.executeWorkflow(
          '1', 
          { param1: 'value1' }, 
          'api_user',
          { source: 'api' }
        );

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/1/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            workflow_template_id: '1',
            triggered_by: 'api_user',
            input_parameters: { param1: 'value1' },
            trigger_context: { source: 'api' }
          })
        });
      });
    });

    describe('getExecutionStatus', () => {
      it('gets execution status', async () => {
        const mockResponse = {
          execution: { id: 'exec-1', status: 'running' },
          step_executions: [],
          total_steps: 3
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.getExecutionStatus('exec-1');

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/executions/exec-1');
        expect(result).toEqual(mockResponse);
      });
    });

    describe('listExecutions', () => {
      it('lists executions with filters', async () => {
        const mockResponse = {
          executions: [],
          total_count: 0,
          page: 1,
          per_page: 20,
          has_more: false
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const filters = {
          workflow_id: '1',
          status: WorkflowExecutionStatus.RUNNING
        };

        await workflowService.listExecutions(filters);

        expect(mockFetch).toHaveBeenCalledWith(
          '/api/workflows/executions?page=1&per_page=20&workflow_id=1&status=running'
        );
      });
    });

    describe('cancelExecution', () => {
      it('cancels an execution', async () => {
        const mockResponse = {
          message: 'Execution cancelled successfully',
          execution_id: 'exec-1',
          status: 'cancelled'
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.cancelExecution('exec-1');

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/executions/exec-1/cancel', {
          method: 'POST'
        });
        expect(result).toEqual(mockResponse);
      });
    });

    describe('pauseExecution', () => {
      it('pauses an execution', async () => {
        const mockResponse = {
          message: 'Execution paused successfully',
          execution_id: 'exec-1',
          status: 'paused'
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.pauseExecution('exec-1');

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/executions/exec-1/pause', {
          method: 'POST'
        });
        expect(result).toEqual(mockResponse);
      });
    });

    describe('resumeExecution', () => {
      it('resumes an execution', async () => {
        const mockResponse = {
          message: 'Execution resumed successfully',
          execution_id: 'exec-1',
          status: 'running'
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.resumeExecution('exec-1');

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/executions/exec-1/resume', {
          method: 'POST'
        });
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('MCP Tool Operations', () => {
    describe('getMCPTools', () => {
      it('gets available MCP tools', async () => {
        const mockResponse = {
          tools: [],
          tools_by_category: {},
          total_count: 0,
          categories: []
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.getMCPTools();

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/tools');
        expect(result).toEqual(mockResponse);
      });
    });

    describe('suggestMCPTools', () => {
      it('suggests MCP tools based on description', async () => {
        const mockResponse = {
          suggestions: [],
          description: 'test description',
          total_count: 0
        };

        mockFetch.mockResolvedValue(createMockResponse(mockResponse) as any);

        const result = await workflowService.suggestMCPTools('test description');

        expect(mockFetch).toHaveBeenCalledWith('/api/workflows/tools/suggest', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description: 'test description' })
        });
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('Utility Methods', () => {
    describe('formatExecutionDuration', () => {
      it('formats duration correctly', () => {
        const start = '2025-01-01T10:00:00Z';
        const end = '2025-01-01T10:05:30Z';
        
        const result = workflowService.formatExecutionDuration(start, end);
        expect(result).toBe('5m 30s');
      });

      it('handles missing start time', () => {
        const result = workflowService.formatExecutionDuration();
        expect(result).toBe('Not started');
      });

      it('uses current time when end time is missing', () => {
        const start = new Date(Date.now() - 5000).toISOString(); // 5 seconds ago
        const result = workflowService.formatExecutionDuration(start);
        expect(result).toMatch(/\d+s/);
      });
    });

    describe('getStatusColor', () => {
      it('returns correct colors for different statuses', () => {
        expect(workflowService.getStatusColor('completed')).toBe('green');
        expect(workflowService.getStatusColor('running')).toBe('blue');
        expect(workflowService.getStatusColor('failed')).toBe('red');
        expect(workflowService.getStatusColor('pending')).toBe('orange');
        expect(workflowService.getStatusColor('cancelled')).toBe('gray');
        expect(workflowService.getStatusColor('unknown')).toBe('gray');
      });
    });

    describe('getStepTypeIcon', () => {
      it('returns correct icons for different step types', () => {
        expect(workflowService.getStepTypeIcon('action')).toBe('⚡');
        expect(workflowService.getStepTypeIcon('condition')).toBe('🔀');
        expect(workflowService.getStepTypeIcon('parallel')).toBe('⚡⚡');
        expect(workflowService.getStepTypeIcon('loop')).toBe('🔄');
        expect(workflowService.getStepTypeIcon('workflow_link')).toBe('🔗');
        expect(workflowService.getStepTypeIcon('unknown')).toBe('📋');
      });
    });
  });

  describe('Error Handling', () => {
    it('handles network errors', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'));

      await expect(workflowService.listWorkflows()).rejects.toThrow('Network error');
    });

    it('handles API error responses', async () => {
      const errorResponse = { error: 'API Error' };
      mockFetch.mockResolvedValue(createMockResponse(errorResponse, false, 400) as any);

      await expect(workflowService.createWorkflow({})).rejects.toThrow('API Error');
    });

    it('handles responses without error field', async () => {
      mockFetch.mockResolvedValue(createMockResponse({}, false, 500) as any);

      await expect(workflowService.listWorkflows()).rejects.toThrow('Failed to list workflows: Error');
    });
  });
});
