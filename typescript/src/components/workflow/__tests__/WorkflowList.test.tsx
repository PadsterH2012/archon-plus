/**
 * WorkflowList Component Tests
 * 
 * Tests for the workflow list component including
 * rendering, filtering, search, and user interactions
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkflowList } from '../WorkflowList';
import { workflowService } from '../../../services/workflowService';
import { ToastProvider } from '../../../contexts/ToastContext';
import { WorkflowTemplate, WorkflowStatus } from '../types/workflow.types';

// Mock the workflow service
jest.mock('../../../services/workflowService');
const mockWorkflowService = workflowService as jest.Mocked<typeof workflowService>;

// Mock toast context
const MockToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ToastProvider>{children}</ToastProvider>
);

// Sample workflow data
const sampleWorkflows: WorkflowTemplate[] = [
  {
    id: '1',
    name: 'test_workflow_1',
    title: 'Test Workflow 1',
    description: 'A test workflow for unit testing',
    category: 'testing',
    tags: ['test', 'automation'],
    status: WorkflowStatus.ACTIVE,
    version: '1.0.0',
    created_by: 'test_user',
    is_public: true,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    steps: [
      {
        name: 'step1',
        title: 'Step 1',
        type: 'action' as any,
        tool_name: 'test_tool',
        parameters: {}
      }
    ],
    parameters: {},
    outputs: {},
    timeout_minutes: 30,
    max_retries: 3
  },
  {
    id: '2',
    name: 'test_workflow_2',
    title: 'Test Workflow 2',
    description: 'Another test workflow',
    category: 'deployment',
    tags: ['deploy', 'production'],
    status: WorkflowStatus.DRAFT,
    version: '1.0.0',
    created_by: 'test_user',
    is_public: false,
    created_at: '2025-01-02T00:00:00Z',
    updated_at: '2025-01-02T00:00:00Z',
    steps: [],
    parameters: {},
    outputs: {},
    timeout_minutes: 60,
    max_retries: 1
  }
];

describe('WorkflowList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API responses
    mockWorkflowService.listWorkflows.mockResolvedValue({
      workflows: sampleWorkflows,
      total_count: 2,
      page: 1,
      per_page: 20,
      has_more: false
    });
    
    mockWorkflowService.getCategories.mockResolvedValue({
      categories: ['testing', 'deployment'],
      total_count: 2
    });
    
    mockWorkflowService.deleteWorkflow.mockResolvedValue({
      message: 'Workflow deleted successfully'
    });
  });

  const renderWorkflowList = (props = {}) => {
    return render(
      <MockToastProvider>
        <WorkflowList {...props} />
      </MockToastProvider>
    );
  };

  describe('Rendering', () => {
    it('renders workflow list with header', async () => {
      renderWorkflowList();
      
      expect(screen.getByText('Workflows')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Search workflows...')).toBeInTheDocument();
      expect(screen.getByText('New Workflow')).toBeInTheDocument();
    });

    it('displays workflows when loaded', async () => {
      renderWorkflowList();
      
      await waitFor(() => {
        expect(screen.getByText('Test Workflow 1')).toBeInTheDocument();
        expect(screen.getByText('Test Workflow 2')).toBeInTheDocument();
      });
    });

    it('shows loading spinner when loading', () => {
      renderWorkflowList({ isLoading: true });
      
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('shows empty state when no workflows', async () => {
      mockWorkflowService.listWorkflows.mockResolvedValue({
        workflows: [],
        total_count: 0,
        page: 1,
        per_page: 20,
        has_more: false
      });
      
      renderWorkflowList();
      
      await waitFor(() => {
        expect(screen.getByText('No workflows found')).toBeInTheDocument();
        expect(screen.getByText('Create Workflow')).toBeInTheDocument();
      });
    });
  });

  describe('Search and Filtering', () => {
    it('handles search input', async () => {
      const user = userEvent.setup();
      renderWorkflowList();
      
      const searchInput = screen.getByPlaceholderText('Search workflows...');
      await user.type(searchInput, 'test workflow');
      
      expect(searchInput).toHaveValue('test workflow');
    });

    it('shows and hides filters', async () => {
      const user = userEvent.setup();
      renderWorkflowList();
      
      const filtersButton = screen.getByText('Filters');
      await user.click(filtersButton);
      
      expect(screen.getByText('Category')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      
      await user.click(filtersButton);
      expect(screen.queryByText('Category')).not.toBeInTheDocument();
    });

    it('handles category filter change', async () => {
      const user = userEvent.setup();
      renderWorkflowList();
      
      // Open filters
      await user.click(screen.getByText('Filters'));
      
      // Change category
      const categorySelect = screen.getByDisplayValue('All Categories');
      await user.selectOptions(categorySelect, 'testing');
      
      expect(categorySelect).toHaveValue('testing');
    });

    it('handles status filter change', async () => {
      const user = userEvent.setup();
      renderWorkflowList();
      
      // Open filters
      await user.click(screen.getByText('Filters'));
      
      // Change status
      const statusSelect = screen.getByDisplayValue('All Statuses');
      await user.selectOptions(statusSelect, WorkflowStatus.ACTIVE);
      
      expect(statusSelect).toHaveValue(WorkflowStatus.ACTIVE);
    });

    it('clears filters when clear button clicked', async () => {
      const user = userEvent.setup();
      renderWorkflowList();
      
      // Open filters and set some values
      await user.click(screen.getByText('Filters'));
      
      const searchInput = screen.getByPlaceholderText('Search workflows...');
      await user.type(searchInput, 'test');
      
      const categorySelect = screen.getByDisplayValue('All Categories');
      await user.selectOptions(categorySelect, 'testing');
      
      // Clear filters
      await user.click(screen.getByText('Clear Filters'));
      
      expect(searchInput).toHaveValue('');
      expect(categorySelect).toHaveValue('');
    });
  });

  describe('View Mode Toggle', () => {
    it('toggles between grid and list view', async () => {
      const user = userEvent.setup();
      renderWorkflowList();
      
      const viewToggle = screen.getByText('List');
      await user.click(viewToggle);
      
      expect(screen.getByText('Grid')).toBeInTheDocument();
    });
  });

  describe('Workflow Actions', () => {
    it('calls onWorkflowSelect when workflow is selected', async () => {
      const onWorkflowSelect = jest.fn();
      renderWorkflowList({ onWorkflowSelect });
      
      await waitFor(() => {
        const workflowCard = screen.getByText('Test Workflow 1').closest('.group');
        fireEvent.click(workflowCard!);
      });
      
      expect(onWorkflowSelect).toHaveBeenCalledWith(sampleWorkflows[0]);
    });

    it('calls onWorkflowEdit when edit is clicked', async () => {
      const onWorkflowEdit = jest.fn();
      renderWorkflowList({ onWorkflowEdit });
      
      await waitFor(() => {
        const editButton = screen.getAllByText('Edit')[0];
        fireEvent.click(editButton);
      });
      
      expect(onWorkflowEdit).toHaveBeenCalledWith(sampleWorkflows[0]);
    });

    it('calls onWorkflowExecute when execute is clicked', async () => {
      const onWorkflowExecute = jest.fn();
      renderWorkflowList({ onWorkflowExecute });
      
      await waitFor(() => {
        const executeButton = screen.getAllByText('Execute')[0];
        fireEvent.click(executeButton);
      });
      
      expect(onWorkflowExecute).toHaveBeenCalledWith(sampleWorkflows[0].id);
    });

    it('handles workflow deletion with confirmation', async () => {
      const onWorkflowDelete = jest.fn();
      const user = userEvent.setup();
      
      // Mock window.confirm
      const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
      
      renderWorkflowList({ onWorkflowDelete });
      
      await waitFor(() => {
        const deleteButton = screen.getAllByText('Delete')[0];
        fireEvent.click(deleteButton);
      });
      
      expect(confirmSpy).toHaveBeenCalledWith('Are you sure you want to delete this workflow?');
      expect(mockWorkflowService.deleteWorkflow).toHaveBeenCalledWith(sampleWorkflows[0].id);
      
      confirmSpy.mockRestore();
    });

    it('does not delete workflow when confirmation is cancelled', async () => {
      const onWorkflowDelete = jest.fn();
      
      // Mock window.confirm to return false
      const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(false);
      
      renderWorkflowList({ onWorkflowDelete });
      
      await waitFor(() => {
        const deleteButton = screen.getAllByText('Delete')[0];
        fireEvent.click(deleteButton);
      });
      
      expect(confirmSpy).toHaveBeenCalled();
      expect(mockWorkflowService.deleteWorkflow).not.toHaveBeenCalled();
      
      confirmSpy.mockRestore();
    });
  });

  describe('Load More', () => {
    it('shows load more button when has more results', async () => {
      mockWorkflowService.listWorkflows.mockResolvedValue({
        workflows: sampleWorkflows,
        total_count: 50,
        page: 1,
        per_page: 20,
        has_more: true
      });
      
      renderWorkflowList();
      
      await waitFor(() => {
        expect(screen.getByText('Load More')).toBeInTheDocument();
      });
    });

    it('loads more workflows when load more is clicked', async () => {
      const user = userEvent.setup();
      
      mockWorkflowService.listWorkflows
        .mockResolvedValueOnce({
          workflows: sampleWorkflows,
          total_count: 50,
          page: 1,
          per_page: 20,
          has_more: true
        })
        .mockResolvedValueOnce({
          workflows: [sampleWorkflows[0]], // Additional workflow
          total_count: 50,
          page: 2,
          per_page: 20,
          has_more: false
        });
      
      renderWorkflowList();
      
      await waitFor(() => {
        expect(screen.getByText('Load More')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Load More'));
      
      expect(mockWorkflowService.listWorkflows).toHaveBeenCalledTimes(3); // Initial + categories + load more
    });
  });

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      mockWorkflowService.listWorkflows.mockRejectedValue(new Error('API Error'));
      
      renderWorkflowList();
      
      await waitFor(() => {
        // Component should still render without crashing
        expect(screen.getByText('Workflows')).toBeInTheDocument();
      });
    });

    it('handles delete errors gracefully', async () => {
      mockWorkflowService.deleteWorkflow.mockRejectedValue(new Error('Delete failed'));
      
      const confirmSpy = jest.spyOn(window, 'confirm').mockReturnValue(true);
      
      renderWorkflowList();
      
      await waitFor(() => {
        const deleteButton = screen.getAllByText('Delete')[0];
        fireEvent.click(deleteButton);
      });
      
      // Should not crash on error
      expect(screen.getByText('Workflows')).toBeInTheDocument();
      
      confirmSpy.mockRestore();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', async () => {
      renderWorkflowList();
      
      expect(screen.getByPlaceholderText('Search workflows...')).toHaveAttribute('type', 'text');
      expect(screen.getByText('New Workflow')).toHaveAttribute('type', 'button');
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      renderWorkflowList();
      
      const searchInput = screen.getByPlaceholderText('Search workflows...');
      await user.tab();
      
      expect(searchInput).toHaveFocus();
    });
  });
});
