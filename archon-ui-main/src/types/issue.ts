// Issue types based on MCP tools API response structure

export interface Issue {
  issue_key: string;           // e.g., "ARCH-123"
  title: string;
  status: IssueStatus;
  priority: IssuePriority;
  severity: IssueSeverity;
  task_id?: string | null;     // external_id from database (linked task)
  created_date: string;        // ISO date string
  updated_date: string;        // ISO date string
  project_name: string;
  project_key: string;
  reporter_username: string | null;
  assignee_username: string | null;
}

export type IssueStatus = 
  | 'open'
  | 'in_progress' 
  | 'testing'
  | 'closed'
  | 'reopened';

export type IssuePriority = 
  | 'critical'
  | 'high'
  | 'medium'
  | 'low';

export type IssueSeverity = 
  | 'critical'
  | 'major'
  | 'minor'
  | 'trivial';

// API Response types for MCP tools

export interface QueryIssuesResponse {
  success: boolean;
  project_name: string;
  status_filter: string | null;
  limit: number;
  issues_count: number;
  issues: Issue[];
  message: string;
  error?: string;
}

export interface UpdateIssueStatusResponse {
  success: boolean;
  issue_key: string;
  old_status: string;
  new_status: string;
  comment: string;
  project_name: string;
  title: string;
  message: string;
  error?: string;
}

export interface CreateIssueResponse {
  success: boolean;
  issue_key: string;
  issue_id: number;
  project_name: string;
  project_was_created: boolean;
  task_id?: string;
  message: string;
  error?: string;
}

export interface IssueHistoryEntry {
  history_id: number;
  issue_id: number;
  user_id: number;
  username: string;
  action_type: string;
  field_changed?: string;
  old_value?: string;
  new_value?: string;
  notes?: string;
  created_date: string;
}

export interface GetIssueHistoryResponse {
  success: boolean;
  issue_key: string;
  issue_info: {
    issue_id: number;
    title: string;
    status: string;
    priority: string;
    severity: string;
    created_date: string;
    updated_date: string;
    task_id?: string;
    project_name: string;
    project_key: string;
  };
  history_count: number;
  history: IssueHistoryEntry[];
  message: string;
  error?: string;
}

// UI-specific types

export interface IssueColumn {
  id: IssueStatus;
  title: string;
  color: string;
  count: number;
}

export interface IssueFilters {
  status?: IssueStatus;
  priority?: IssuePriority;
  severity?: IssueSeverity;
  assignee?: string;
  search?: string;
}

// Form types for creating/editing issues

export interface CreateIssueRequest {
  title: string;
  description?: string;
  project_name: string;
  priority: IssuePriority;
  severity: IssueSeverity;
  assignee_username?: string;
  task_id?: string;
  tags?: string[];
  environment?: string;
}

export interface UpdateIssueRequest {
  title?: string;
  description?: string;
  status?: IssueStatus;
  priority?: IssuePriority;
  severity?: IssueSeverity;
  assignee_username?: string;
  task_id?: string;
  comment?: string;
}

// Constants for UI

export const ISSUE_STATUS_COLUMNS: IssueColumn[] = [
  { id: 'open', title: 'Open', color: 'blue', count: 0 },
  { id: 'in_progress', title: 'In Progress', color: 'yellow', count: 0 },
  { id: 'testing', title: 'Testing', color: 'purple', count: 0 },
  { id: 'closed', title: 'Closed', color: 'green', count: 0 },
  { id: 'reopened', title: 'Reopened', color: 'orange', count: 0 }
];

export const ISSUE_PRIORITIES: IssuePriority[] = ['low', 'medium', 'high', 'critical'];
export const ISSUE_SEVERITIES: IssueSeverity[] = ['trivial', 'minor', 'major', 'critical'];

// Utility functions

export const getIssueStatusColor = (status: IssueStatus): string => {
  switch (status) {
    case 'open': return 'text-blue-600 dark:text-blue-400';
    case 'in_progress': return 'text-yellow-600 dark:text-yellow-400';
    case 'testing': return 'text-purple-600 dark:text-purple-400';
    case 'closed': return 'text-green-600 dark:text-green-400';
    case 'reopened': return 'text-orange-600 dark:text-orange-400';
    default: return 'text-gray-600 dark:text-gray-400';
  }
};

export const getIssuePriorityColor = (priority: IssuePriority): string => {
  switch (priority) {
    case 'critical': return 'text-red-600 dark:text-red-400';
    case 'high': return 'text-orange-600 dark:text-orange-400';
    case 'medium': return 'text-yellow-600 dark:text-yellow-400';
    case 'low': return 'text-green-600 dark:text-green-400';
    default: return 'text-gray-600 dark:text-gray-400';
  }
};

export const getIssuePriorityBadgeColor = (priority: IssuePriority): string => {
  switch (priority) {
    case 'critical': return 'bg-red-500';
    case 'high': return 'bg-orange-500';
    case 'medium': return 'bg-yellow-500';
    case 'low': return 'bg-green-500';
    default: return 'bg-gray-500';
  }
};

export const formatIssueDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  } catch {
    return 'Invalid date';
  }
};

export const formatIssueDateTime = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleString();
  } catch {
    return 'Invalid date';
  }
};
