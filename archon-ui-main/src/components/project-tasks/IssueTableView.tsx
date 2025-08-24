import React from 'react';
import { Issue, getIssueStatusColor, getIssuePriorityColor, formatIssueDate } from '../../types/issue';

interface IssueTableViewProps {
  issues: Issue[];
  onIssueView: (issue: Issue) => void;
  onIssueDelete: (issue: Issue) => void;
}

export const IssueTableView = ({ 
  issues, 
  onIssueView, 
  onIssueDelete 
}: IssueTableViewProps) => {
  
  // Use utility functions from types
  const getPriorityColor = getIssuePriorityColor;
  const getStatusColor = getIssueStatusColor;

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700">
            <th className="text-left p-3 text-sm font-medium text-gray-900 dark:text-gray-100">
              Issue Key
            </th>
            <th className="text-left p-3 text-sm font-medium text-gray-900 dark:text-gray-100">
              Title
            </th>
            <th className="text-left p-3 text-sm font-medium text-gray-900 dark:text-gray-100">
              Status
            </th>
            <th className="text-left p-3 text-sm font-medium text-gray-900 dark:text-gray-100">
              Priority
            </th>
            <th className="text-left p-3 text-sm font-medium text-gray-900 dark:text-gray-100">
              Severity
            </th>
            <th className="text-left p-3 text-sm font-medium text-gray-900 dark:text-gray-100">
              Assignee
            </th>
            <th className="text-left p-3 text-sm font-medium text-gray-900 dark:text-gray-100">
              Created
            </th>
            <th className="text-left p-3 text-sm font-medium text-gray-900 dark:text-gray-100">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          {issues.map((issue) => (
            <tr 
              key={issue.issue_key}
              className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
            >
              <td className="p-3 text-sm font-mono text-gray-900 dark:text-gray-100">
                {issue.issue_key}
              </td>
              <td className="p-3 text-sm text-gray-900 dark:text-gray-100">
                <button
                  onClick={() => onIssueView(issue)}
                  className="text-left hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                >
                  {issue.title}
                </button>
              </td>
              <td className="p-3 text-sm">
                <span className={`font-medium ${getStatusColor(issue.status)}`}>
                  {issue.status.replace('_', ' ').toUpperCase()}
                </span>
              </td>
              <td className="p-3 text-sm">
                <span className={`font-medium ${getPriorityColor(issue.priority)}`}>
                  {issue.priority.toUpperCase()}
                </span>
              </td>
              <td className="p-3 text-sm text-gray-600 dark:text-gray-400">
                {issue.severity}
              </td>
              <td className="p-3 text-sm text-gray-600 dark:text-gray-400">
                {issue.assignee_username || 'Unassigned'}
              </td>
              <td className="p-3 text-sm text-gray-600 dark:text-gray-400">
                {formatIssueDate(issue.created_date)}
              </td>
              <td className="p-3 text-sm">
                <div className="flex gap-2">
                  <button
                    onClick={() => onIssueView(issue)}
                    className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                  >
                    View
                  </button>
                  <button
                    onClick={() => onIssueDelete(issue)}
                    className="px-2 py-1 text-xs bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {issues.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 dark:text-gray-400">No issues found</p>
        </div>
      )}
    </div>
  );
};
