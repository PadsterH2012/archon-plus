import React, { useRef, useState } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { Edit, Trash2, RefreshCw, Tag, User, Bot, Clipboard, AlertTriangle, Bug, CheckCircle } from 'lucide-react';
import { Issue, IssueStatus, getIssueStatusColor, getIssuePriorityColor, getIssuePriorityBadgeColor, formatIssueDate } from '../../types/issue';
import { ItemTypes } from '../../lib/task-utils';

export interface DraggableIssueCardProps {
  issue: Issue;
  index: number;
  onView: () => void;
  onDelete: (issue: Issue) => void;
  hoveredIssueKey?: string | null;
  onIssueHover?: (issueKey: string | null) => void;
}

export const DraggableIssueCard = ({
  issue,
  index,
  onView,
  onDelete,
  hoveredIssueKey,
  onIssueHover,
}: DraggableIssueCardProps) => {
  
  const [{ isDragging }, drag] = useDrag({
    type: ItemTypes.TASK, // Reusing task item type for now
    item: { id: issue.issue_key, status: issue.status, index },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging()
    })
  });

  const [, drop] = useDrop({
    accept: ItemTypes.TASK,
    hover: (draggedItem: { id: string; status: IssueStatus; index: number }, monitor) => {
      if (!monitor.isOver({ shallow: true })) return;
      if (draggedItem.id === issue.issue_key) return;
      if (draggedItem.status !== issue.status) return;
      
      const draggedIndex = draggedItem.index;
      const hoveredIndex = index;
      
      if (draggedIndex === hoveredIndex) return;
      
      console.log('BOARD HOVER: Moving issue', draggedItem.id, 'from index', draggedIndex, 'to', hoveredIndex, 'in status', issue.status);
      
      // Update the dragged item's index to prevent re-triggering
      draggedItem.index = hoveredIndex;
    }
  });

  const [isFlipped, setIsFlipped] = useState(false);
  
  const handleMouseEnter = () => {
    onIssueHover?.(issue.issue_key);
  };
  
  const handleMouseLeave = () => {
    onIssueHover?.(null);
  };

  // Use utility functions from types
  const getPriorityColor = getIssuePriorityBadgeColor;
  const getPriorityTextColor = getIssuePriorityColor;

  // Get severity icon
  const getSeverityIcon = (severity: Issue['severity']) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'major': return <Bug className="w-4 h-4 text-orange-500" />;
      case 'minor': return <CheckCircle className="w-4 h-4 text-yellow-500" />;
      case 'trivial': return <CheckCircle className="w-4 h-4 text-green-500" />;
      default: return <Bug className="w-4 h-4 text-gray-500" />;
    }
  };

  // Use utility functions from types
  const getStatusColor = getIssueStatusColor;

  // Card scaling and opacity effects
  const isHighlighted = hoveredIssueKey === issue.issue_key;
  const cardScale = isHighlighted ? 'scale-105' : 'scale-100';
  const cardOpacity = isDragging ? 'opacity-50' : 'opacity-100';
  
  // Simplified hover effect - just a glowing border
  const hoverEffectClasses = 'group-hover:border-cyan-400/70 dark:group-hover:border-cyan-500/50 group-hover:shadow-[0_0_15px_rgba(34,211,238,0.4)] dark:group-hover:shadow-[0_0_15px_rgba(34,211,238,0.6)]';
  
  // Base card styles with proper rounded corners
  const cardBaseStyles = 'bg-gradient-to-b from-white/80 to-white/60 dark:from-white/10 dark:to-black/30 border border-gray-200 dark:border-gray-700 rounded-lg';
  
  // Transition settings
  const transitionStyles = 'transition-all duration-200 ease-in-out';

  return (
    <div 
      ref={(node) => drag(drop(node))}
      style={{ 
        perspective: '1000px',
        transformStyle: 'preserve-3d'
      }}
      className={`flip-card w-full min-h-[140px] cursor-move relative ${cardScale} ${cardOpacity} ${isDragging ? 'opacity-50 scale-90' : ''} ${transitionStyles} group`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div 
        className={`relative w-full min-h-[140px] transform-style-preserve-3d ${isFlipped ? 'rotate-y-180' : ''}`}
      >
        {/* Front side with subtle hover effect */}
        <div className={`absolute w-full h-full backface-hidden ${cardBaseStyles} ${transitionStyles} ${hoverEffectClasses} rounded-lg`}>
          {/* Priority indicator */}
          <div className={`absolute top-2 left-2 w-3 h-3 rounded-full ${getPriorityColor(issue.priority)}`}></div>
          
          {/* Issue key */}
          <div className="absolute top-2 right-2 text-xs font-mono text-gray-500 dark:text-gray-400">
            {issue.issue_key}
          </div>
          
          {/* Content */}
          <div className="p-4 pt-8">
            {/* Title */}
            <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2 line-clamp-2">
              {issue.title}
            </h4>
            
            {/* Status and Priority */}
            <div className="flex items-center gap-2 mb-2">
              <span className={`text-xs font-medium ${getStatusColor(issue.status)}`}>
                {issue.status.replace('_', ' ').toUpperCase()}
              </span>
              <span className={`text-xs ${getPriorityTextColor(issue.priority)}`}>
                {issue.priority.toUpperCase()}
              </span>
            </div>
            
            {/* Severity and Assignee */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1">
                {getSeverityIcon(issue.severity)}
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  {issue.severity}
                </span>
              </div>
              
              <div className="flex items-center gap-1">
                <User className="w-3 h-3 text-gray-500" />
                <span className="text-xs text-gray-600 dark:text-gray-400 truncate max-w-[80px]">
                  {issue.assignee_username || 'Unassigned'}
                </span>
              </div>
            </div>
            
            {/* Created date */}
            <div className="text-xs text-gray-500 dark:text-gray-500 mt-2">
              Created: {formatIssueDate(issue.created_date)}
            </div>
          </div>
        </div>

        {/* Back side with actions */}
        <div className={`absolute w-full h-full backface-hidden rotate-y-180 ${cardBaseStyles} ${transitionStyles} rounded-lg`}>
          <div className="p-4 h-full flex flex-col justify-center items-center space-y-3">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onView();
              }}
              className="w-full px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-md transition-colors duration-200 flex items-center justify-center gap-2"
            >
              <Edit className="w-4 h-4" />
              View Details
            </button>
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(issue);
              }}
              className="w-full px-3 py-2 bg-red-500 hover:bg-red-600 text-white text-sm rounded-md transition-colors duration-200 flex items-center justify-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
            
            {issue.task_id && (
              <div className="text-xs text-gray-600 dark:text-gray-400 text-center">
                Linked to task: {issue.task_id}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
