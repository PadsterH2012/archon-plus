/**
 * Workflow UI Component Types
 * 
 * Type definitions for workflow management UI components
 * following Archon design system patterns
 */

import { ReactNode } from 'react';

// Base workflow types
export interface WorkflowTemplate {
  id: string;
  name: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  status: WorkflowStatus;
  version: string;
  created_by: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  steps: WorkflowStep[];
  parameters: Record<string, WorkflowParameter>;
  outputs: Record<string, WorkflowOutput>;
  timeout_minutes: number;
  max_retries: number;
}

export interface WorkflowStep {
  name: string;
  title: string;
  type: WorkflowStepType;
  description?: string;
  tool_name?: string;
  parameters?: Record<string, any>;
  condition?: string;
  on_success?: string;
  on_failure?: string;
  retry_count?: number;
  timeout_minutes?: number;
  steps?: WorkflowStep[]; // For parallel and loop steps
  collection?: string; // For loop steps
  item_variable?: string; // For loop steps
  max_iterations?: number; // For loop steps
  wait_for_all?: boolean; // For parallel steps
  workflow_name?: string; // For workflow link steps
}

export interface WorkflowExecution {
  id: string;
  workflow_template_id: string;
  status: WorkflowExecutionStatus;
  triggered_by: string;
  input_parameters: Record<string, any>;
  output_data?: Record<string, any>;
  current_step_index: number;
  total_steps: number;
  progress_percentage: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  execution_log: ExecutionLogEntry[];
  trigger_context?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface StepExecution {
  id: string;
  workflow_execution_id: string;
  step_index: number;
  step_name: string;
  step_type: WorkflowStepType;
  status: StepExecutionStatus;
  started_at?: string;
  completed_at?: string;
  input_data?: Record<string, any>;
  output_data?: Record<string, any>;
  error_message?: string;
  tool_name?: string;
  tool_parameters?: Record<string, any>;
  tool_result?: Record<string, any>;
  attempt_number: number;
  max_attempts: number;
  created_at: string;
  updated_at: string;
}

export interface WorkflowParameter {
  type: 'string' | 'integer' | 'boolean' | 'object' | 'array';
  required: boolean;
  default?: any;
  description: string;
  enum?: string[];
  minimum?: number;
  maximum?: number;
}

export interface WorkflowOutput {
  type: 'string' | 'integer' | 'boolean' | 'object' | 'array';
  description: string;
}

export interface ExecutionLogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  step_index?: number;
  step_name?: string;
  details?: Record<string, any>;
}

export interface MCPTool {
  name: string;
  category: string;
  description: string;
  parameters: Record<string, WorkflowParameter>;
  returns: string;
  example: Record<string, any>;
}

// Enums
export enum WorkflowStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  DEPRECATED = 'deprecated',
  ARCHIVED = 'archived'
}

export enum WorkflowExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum StepExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  SKIPPED = 'skipped'
}

export enum WorkflowStepType {
  ACTION = 'action',
  CONDITION = 'condition',
  PARALLEL = 'parallel',
  LOOP = 'loop',
  WORKFLOW_LINK = 'workflow_link'
}

// UI Component Props
export interface WorkflowListProps {
  workflows: WorkflowTemplate[];
  isLoading?: boolean;
  onWorkflowSelect?: (workflow: WorkflowTemplate) => void;
  onWorkflowEdit?: (workflow: WorkflowTemplate) => void;
  onWorkflowDelete?: (workflowId: string) => void;
  onWorkflowExecute?: (workflowId: string) => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
  categoryFilter?: string;
  onCategoryChange?: (category: string) => void;
  statusFilter?: WorkflowStatus;
  onStatusChange?: (status: WorkflowStatus) => void;
}

export interface WorkflowCardProps {
  workflow: WorkflowTemplate;
  onSelect?: (workflow: WorkflowTemplate) => void;
  onEdit?: (workflow: WorkflowTemplate) => void;
  onDelete?: (workflowId: string) => void;
  onExecute?: (workflowId: string) => void;
  isSelected?: boolean;
  accentColor?: 'purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange';
}

export interface WorkflowDetailProps {
  workflow: WorkflowTemplate;
  onEdit?: (workflow: WorkflowTemplate) => void;
  onExecute?: (workflowId: string) => void;
  onClose?: () => void;
  isDarkMode?: boolean;
}

export interface WorkflowExecutionProps {
  execution: WorkflowExecution;
  stepExecutions: StepExecution[];
  onCancel?: (executionId: string) => void;
  onPause?: (executionId: string) => void;
  onResume?: (executionId: string) => void;
  onRefresh?: (executionId: string) => void;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export interface WorkflowStepBuilderProps {
  steps: WorkflowStep[];
  availableTools: MCPTool[];
  onStepsChange: (steps: WorkflowStep[]) => void;
  onStepAdd: (step: WorkflowStep) => void;
  onStepEdit: (index: number, step: WorkflowStep) => void;
  onStepDelete: (index: number) => void;
  onStepReorder: (fromIndex: number, toIndex: number) => void;
  isDarkMode?: boolean;
}

export interface WorkflowFormProps {
  workflow?: WorkflowTemplate;
  onSave: (workflow: Partial<WorkflowTemplate>) => void;
  onCancel: () => void;
  isLoading?: boolean;
  availableTools: MCPTool[];
  isDarkMode?: boolean;
}

export interface ExecutionDashboardProps {
  executions: WorkflowExecution[];
  isLoading?: boolean;
  onExecutionSelect?: (execution: WorkflowExecution) => void;
  onExecutionCancel?: (executionId: string) => void;
  onExecutionPause?: (executionId: string) => void;
  onExecutionResume?: (executionId: string) => void;
  onRefresh?: () => void;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

// Filter and search types
export interface WorkflowFilters {
  search?: string;
  category?: string;
  status?: WorkflowStatus;
  tags?: string[];
  created_by?: string;
  is_public?: boolean;
}

export interface ExecutionFilters {
  workflow_id?: string;
  status?: WorkflowExecutionStatus;
  triggered_by?: string;
  date_from?: string;
  date_to?: string;
}

// API response types
export interface WorkflowListResponse {
  workflows: WorkflowTemplate[];
  total_count: number;
  page: number;
  per_page: number;
  has_more: boolean;
}

export interface ExecutionListResponse {
  executions: WorkflowExecution[];
  total_count: number;
  page: number;
  per_page: number;
  has_more: boolean;
}

export interface WorkflowValidationResult {
  is_valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  info: ValidationError[];
}

export interface ValidationError {
  code: string;
  message: string;
  step_name?: string;
  field?: string;
  suggestion?: string;
}

// Utility types
export type AccentColor = 'purple' | 'green' | 'pink' | 'blue' | 'cyan' | 'orange';

export interface ComponentProps {
  className?: string;
  accentColor?: AccentColor;
  isDarkMode?: boolean;
  children?: ReactNode;
}
