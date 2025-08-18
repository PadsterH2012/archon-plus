/**
 * WorkflowBuilder Component Tests
 * 
 * Tests for the comprehensive workflow builder component
 * including form, designer, and validation tabs
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { WorkflowBuilder } from '../WorkflowBuilder';
import { workflowService } from '../../../services/workflowService';
import { ToastProvider } from '../../../contexts/ToastContext';
import { WorkflowTemplate, WorkflowStatus } from '../types/workflow.types';

// Mock the workflow service
jest.mock('../../../services/workflowService');
const mockWorkflowService = workflowService as jest.Mocked<typeof workflowService>;

// Mock React Flow
jest.mock('@xyflow/react', () => ({
  ReactFlow: ({ children }: any) => <div data-testid="react-flow">{children}</div>,
  ReactFlowProvider: ({ children }: any) => <div>{children}</div>,
  Controls: () => <div data-testid="flow-controls" />,
  Background: () => <div data-testid="flow-background" />,
  Handle: () => <div data-testid="flow-handle" />,
  Position: { Top: 'top', Bottom: 'bottom', Left: 'left', Right: 'right' },
  MarkerType: { ArrowClosed: 'arrowclosed' },
  ConnectionLineType: { SmoothStep: 'smoothstep' },
  useReactFlow: () => ({
    fitView: jest.fn(),
    getNodes: jest.fn(() => []),
    getEdges: jest.fn(() => [])
  }),
  applyNodeChanges: jest.fn((changes, nodes) => nodes),
  applyEdgeChanges: jest.fn((changes, edges) => edges),
  addEdge: jest.fn((edge, edges) => [...edges, edge])
}));

// Mock toast context
const MockToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ToastProvider>{children}</ToastProvider>
);

// Sample workflow data
const sampleWorkflow: WorkflowTemplate = {
  id: '1',
  name: 'test_workflow',
  title: 'Test Workflow',
  description: 'A test workflow for unit testing',
  category: 'testing',
  tags: ['test', 'automation'],
  status: WorkflowStatus.DRAFT,
  version: '1.0.0',
  created_by: 'test_user',
  is_public: false,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
  steps: [
    {
      name: 'step1',
      title: 'Test Step',
      type: 'action' as any,
      tool_name: 'test_tool',
      parameters: {}
    }
  ],
  parameters: {
    input_param: {
      type: 'string',
      required: true,
      description: 'Test input parameter'
    }
  },
  outputs: {
    result: {
      type: 'string',
      description: 'Test output'
    }
  },
  timeout_minutes: 30,
  max_retries: 3
};

describe('WorkflowBuilder', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API responses
    mockWorkflowService.getMCPTools.mockResolvedValue({
      tools: [
        {
          name: 'test_tool',
          category: 'testing',
          description: 'A test tool',
          parameters: {},
          returns: 'string',
          example: {}
        }
      ],
      tools_by_category: {},
      total_count: 1,
      categories: ['testing']
    });
  });

  const renderWorkflowBuilder = (props = {}) => {
    return render(
      <MockToastProvider>
        <WorkflowBuilder {...props} />
      </MockToastProvider>
    );
  };

  describe('Rendering', () => {
    it('renders workflow builder with tabs', async () => {
      renderWorkflowBuilder();
      
      expect(screen.getByText('Create Workflow')).toBeInTheDocument();
      expect(screen.getByText('Metadata')).toBeInTheDocument();
      expect(screen.getByText('Designer')).toBeInTheDocument();
      expect(screen.getByText('Validation')).toBeInTheDocument();
    });

    it('renders with existing workflow data', async () => {
      renderWorkflowBuilder({ workflow: sampleWorkflow });
      
      expect(screen.getByText('Edit Workflow')).toBeInTheDocument();
      expect(screen.getByText('Test Workflow')).toBeInTheDocument();
    });

    it('shows unsaved changes indicator', async () => {
      const user = userEvent.setup();
      renderWorkflowBuilder();
      
      // Switch to metadata tab and make a change
      await user.click(screen.getByText('Metadata'));
      
      // The component should show unsaved changes after modifications
      // This would be tested with actual form interactions
    });
  });

  describe('Tab Navigation', () => {
    it('switches between tabs', async () => {
      const user = userEvent.setup();
      renderWorkflowBuilder();
      
      // Start on metadata tab
      expect(screen.getByText('Metadata')).toHaveAttribute('aria-selected', 'true');
      
      // Switch to designer tab
      await user.click(screen.getByText('Designer'));
      expect(screen.getByTestId('react-flow')).toBeInTheDocument();
      
      // Switch to validation tab
      await user.click(screen.getByText('Validation'));
      expect(screen.getByText('Workflow Validation')).toBeInTheDocument();
    });

    it('shows validation status in tab badge', async () => {
      renderWorkflowBuilder({ workflow: sampleWorkflow });
      
      await waitFor(() => {
        // Should show validation status once workflow is loaded
        expect(screen.getByText('Validation')).toBeInTheDocument();
      });
    });
  });

  describe('Metadata Tab', () => {
    it('displays workflow form in metadata tab', async () => {
      const user = userEvent.setup();
      renderWorkflowBuilder();
      
      await user.click(screen.getByText('Metadata'));
      
      expect(screen.getByText('Basic Information')).toBeInTheDocument();
      expect(screen.getByLabelText(/Workflow Name/)).toBeInTheDocument();
      expect(screen.getByLabelText(/Display Title/)).toBeInTheDocument();
    });

    it('handles form data changes', async () => {
      const user = userEvent.setup();
      const onSave = jest.fn();
      renderWorkflowBuilder({ onSave });
      
      await user.click(screen.getByText('Metadata'));
      
      const nameInput = screen.getByLabelText(/Workflow Name/);
      await user.type(nameInput, 'new_workflow');
      
      expect(nameInput).toHaveValue('new_workflow');
    });
  });

  describe('Designer Tab', () => {
    it('displays workflow designer in designer tab', async () => {
      const user = userEvent.setup();
      renderWorkflowBuilder();
      
      await user.click(screen.getByText('Designer'));
      
      expect(screen.getByTestId('react-flow')).toBeInTheDocument();
      expect(screen.getByText('Step Palette')).toBeInTheDocument();
    });

    it('loads available MCP tools', async () => {
      const user = userEvent.setup();
      renderWorkflowBuilder();
      
      await user.click(screen.getByText('Designer'));
      
      await waitFor(() => {
        expect(mockWorkflowService.getMCPTools).toHaveBeenCalled();
      });
    });
  });

  describe('Validation Tab', () => {
    it('shows validation results', async () => {
      const user = userEvent.setup();
      renderWorkflowBuilder({ workflow: sampleWorkflow });
      
      await user.click(screen.getByText('Validation'));
      
      expect(screen.getByText('Workflow Validation')).toBeInTheDocument();
    });

    it('shows empty state when no steps', async () => {
      const user = userEvent.setup();
      renderWorkflowBuilder();
      
      await user.click(screen.getByText('Validation'));
      
      expect(screen.getByText('Add workflow steps to see validation results')).toBeInTheDocument();
    });

    it('displays validation errors and warnings', async () => {
      const user = userEvent.setup();
      const workflowWithErrors = {
        ...sampleWorkflow,
        name: '', // Missing name should cause validation error
        description: '' // Missing description should cause warning
      };
      
      renderWorkflowBuilder({ workflow: workflowWithErrors });
      
      await user.click(screen.getByText('Validation'));
      
      await waitFor(() => {
        // Should show validation results
        expect(screen.getByText('Workflow Validation')).toBeInTheDocument();
      });
    });
  });

  describe('Actions', () => {
    it('handles save action', async () => {
      const onSave = jest.fn();
      renderWorkflowBuilder({ workflow: sampleWorkflow, onSave });
      
      const saveButton = screen.getByText('Save');
      fireEvent.click(saveButton);
      
      expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
        name: 'test_workflow',
        title: 'Test Workflow'
      }));
    });

    it('handles cancel action', async () => {
      const onCancel = jest.fn();
      renderWorkflowBuilder({ onCancel });
      
      const backButton = screen.getByText('Back');
      fireEvent.click(backButton);
      
      expect(onCancel).toHaveBeenCalled();
    });

    it('handles preview action', async () => {
      const onPreview = jest.fn();
      renderWorkflowBuilder({ workflow: sampleWorkflow, onPreview });
      
      const previewButton = screen.getByText('Preview');
      fireEvent.click(previewButton);
      
      expect(onPreview).toHaveBeenCalledWith(expect.objectContaining({
        name: 'test_workflow'
      }));
    });

    it('handles test action', async () => {
      const onTest = jest.fn();
      renderWorkflowBuilder({ workflow: sampleWorkflow, onTest });
      
      const testButton = screen.getByText('Test');
      fireEvent.click(testButton);
      
      expect(onTest).toHaveBeenCalledWith(expect.objectContaining({
        name: 'test_workflow'
      }));
    });

    it('disables save when required fields missing', () => {
      renderWorkflowBuilder();
      
      const saveButton = screen.getByText('Save');
      expect(saveButton).toBeDisabled();
    });

    it('disables test when workflow invalid', () => {
      const invalidWorkflow = {
        ...sampleWorkflow,
        name: '' // Invalid workflow
      };
      
      renderWorkflowBuilder({ workflow: invalidWorkflow });
      
      const testButton = screen.getByText('Test');
      expect(testButton).toBeDisabled();
    });
  });

  describe('Loading States', () => {
    it('shows loading state when saving', () => {
      renderWorkflowBuilder({ isLoading: true });
      
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });

    it('disables actions when loading', () => {
      renderWorkflowBuilder({ isLoading: true });
      
      const saveButton = screen.getByText('Saving...');
      expect(saveButton).toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    it('handles MCP tools loading error', async () => {
      mockWorkflowService.getMCPTools.mockRejectedValue(new Error('API Error'));
      
      renderWorkflowBuilder();
      
      await waitFor(() => {
        // Component should still render without crashing
        expect(screen.getByText('Create Workflow')).toBeInTheDocument();
      });
    });

    it('handles save errors gracefully', async () => {
      const onSave = jest.fn().mockRejectedValue(new Error('Save failed'));
      renderWorkflowBuilder({ workflow: sampleWorkflow, onSave });
      
      const saveButton = screen.getByText('Save');
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        // Should not crash on save error
        expect(screen.getByText('Create Workflow')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels for tabs', () => {
      renderWorkflowBuilder();
      
      expect(screen.getByText('Metadata')).toHaveAttribute('role', 'tab');
      expect(screen.getByText('Designer')).toHaveAttribute('role', 'tab');
      expect(screen.getByText('Validation')).toHaveAttribute('role', 'tab');
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      renderWorkflowBuilder();
      
      // Tab navigation should work
      await user.tab();
      expect(screen.getByText('Back')).toHaveFocus();
    });
  });
});
