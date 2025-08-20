/**
 * WorkflowCard Component
 * 
 * Individual workflow card component for displaying workflow information
 * Supports both grid and list view modes
 */

import React, { useState } from 'react';
import {
  Edit,
  Trash2,
  Clock,
  User,
  Tag,
  Calendar,
  MoreVertical,
  CheckCircle,
  AlertCircle,
  Archive,
  FileText,
  Copy
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { DropdownMenu } from '../ui/DropdownMenu';
import { 
  WorkflowCardProps, 
  WorkflowStatus,
  WorkflowStepType 
} from './types/workflow.types';

export const WorkflowCard: React.FC<WorkflowCardProps> = ({
  workflow,
  onSelect,
  onEdit,
  onDelete,
  onExecute,
  onClone,
  isSelected = false,
  accentColor = 'purple'
}) => {
  const [showMenu, setShowMenu] = useState(false);

  // Get status color and icon
  const getStatusInfo = (status: WorkflowStatus) => {
    switch (status) {
      case WorkflowStatus.ACTIVE:
        return { color: 'green', icon: <CheckCircle className="w-3 h-3" />, label: 'Active' };
      case WorkflowStatus.DRAFT:
        return { color: 'orange', icon: <FileText className="w-3 h-3" />, label: 'Draft' };
      case WorkflowStatus.DEPRECATED:
        return { color: 'red', icon: <AlertCircle className="w-3 h-3" />, label: 'Deprecated' };
      case WorkflowStatus.ARCHIVED:
        return { color: 'gray', icon: <Archive className="w-3 h-3" />, label: 'Archived' };
      default:
        return { color: 'gray', icon: <FileText className="w-3 h-3" />, label: 'Unknown' };
    }
  };

  // Get step type summary
  const getStepTypeSummary = () => {
    const stepTypes = workflow.steps.reduce((acc, step) => {
      acc[step.type] = (acc[step.type] || 0) + 1;
      return acc;
    }, {} as Record<WorkflowStepType, number>);

    return Object.entries(stepTypes).map(([type, count]) => ({
      type: type as WorkflowStepType,
      count,
      icon: getStepTypeIcon(type as WorkflowStepType)
    }));
  };

  const getStepTypeIcon = (stepType: WorkflowStepType): string => {
    switch (stepType) {
      case WorkflowStepType.ACTION:
        return '⚡';
      case WorkflowStepType.CONDITION:
        return '🔀';
      case WorkflowStepType.PARALLEL:
        return '⚡⚡';
      case WorkflowStepType.LOOP:
        return '🔄';
      case WorkflowStepType.WORKFLOW_LINK:
        return '🔗';
      default:
        return '📋';
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Get complexity level
  const getComplexity = () => {
    const stepCount = workflow.steps.length;
    if (stepCount <= 3) return { level: 'Simple', color: 'green' };
    if (stepCount <= 6) return { level: 'Moderate', color: 'orange' };
    return { level: 'Complex', color: 'red' };
  };

  const statusInfo = getStatusInfo(workflow.status);
  const stepSummary = getStepTypeSummary();
  const complexity = getComplexity();

  const menuItems = [
    {
      label: 'Edit',
      icon: <Edit className="w-4 h-4" />,
      onClick: () => onEdit?.(workflow)
    },
    {
      label: 'Clone',
      icon: <Copy className="w-4 h-4" />,
      onClick: () => onClone?.(workflow.id)
    },
    {
      label: 'Delete',
      icon: <Trash2 className="w-4 h-4" />,
      onClick: () => onDelete?.(workflow.id),
      variant: 'danger' as const
    }
  ];

  return (
    <Card 
      accentColor={accentColor}
      className={`group cursor-pointer transition-all duration-200 hover:shadow-lg ${
        isSelected ? 'ring-2 ring-purple-500 ring-opacity-50' : ''
      }`}
      onClick={() => onSelect?.(workflow)}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                {workflow.title}
              </h3>
              <Badge 
                color={statusInfo.color}
                size="sm"
                icon={statusInfo.icon}
              >
                {statusInfo.label}
              </Badge>
            </div>
            
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              {workflow.name}
            </p>
            
            <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
              {workflow.description}
            </p>
          </div>

          <div className="relative ml-4">
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              icon={<MoreVertical className="w-4 h-4" />}
              className="hover:bg-gray-100 dark:hover:bg-gray-700"
            />
            
            {showMenu && (
              <DropdownMenu
                items={menuItems}
                onClose={() => setShowMenu(false)}
                position="bottom-right"
              />
            )}
          </div>
        </div>

        {/* Metadata */}
        <div className="space-y-3 mb-4">
          {/* Category and Tags */}
          <div className="flex items-center flex-wrap gap-2">
            <Badge color={accentColor} size="sm">
              {workflow.category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </Badge>
            
            {workflow.tags.slice(0, 3).map(tag => (
              <Badge key={tag} color="gray" size="sm" variant="outline">
                {tag}
              </Badge>
            ))}
            
            {workflow.tags.length > 3 && (
              <Badge color="gray" size="sm" variant="outline">
                +{workflow.tags.length - 3}
              </Badge>
            )}
          </div>

          {/* Step Summary */}
          <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-center space-x-1">
              <span className="font-medium">{workflow.steps.length}</span>
              <span>steps</span>
            </div>
            
            <div className="flex items-center space-x-2">
              {stepSummary.slice(0, 3).map(({ type, count, icon }) => (
                <div key={type} className="flex items-center space-x-1">
                  <span>{icon}</span>
                  <span>{count}</span>
                </div>
              ))}
            </div>
            
            <Badge 
              color={complexity.color} 
              size="sm" 
              variant="outline"
            >
              {complexity.level}
            </Badge>
          </div>

          {/* Creator and Date */}
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-1">
              <User className="w-3 h-3" />
              <span>{workflow.created_by}</span>
            </div>
            
            <div className="flex items-center space-x-1">
              <Calendar className="w-3 h-3" />
              <span>{formatDate(workflow.created_at)}</span>
            </div>
          </div>

          {/* Version and Timeout */}
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-1">
              <Tag className="w-3 h-3" />
              <span>v{workflow.version}</span>
            </div>
            
            <div className="flex items-center space-x-1">
              <Clock className="w-3 h-3" />
              <span>{workflow.timeout_minutes}m timeout</span>
            </div>
          </div>
        </div>

        {/* Actions - Removed per user preference for minimal workflow UI */}
      </div>
    </Card>
  );
};
