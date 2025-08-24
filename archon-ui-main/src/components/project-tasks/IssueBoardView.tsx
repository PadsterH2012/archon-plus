import React, { useRef, useState, useCallback } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { useToast } from '../../contexts/ToastContext';
import { DeleteConfirmModal } from '../../pages/ProjectPage';
import { CheckSquare, Square, Trash2, ArrowRight } from 'lucide-react';
import { Issue, IssueStatus } from '../../types/issue';
import { ItemTypes } from '../../lib/task-utils';
import { DraggableIssueCard } from './DraggableIssueCard';

interface IssueBoardViewProps {
  issues: Issue[];
  onIssueView: (issue: Issue) => void;
  onIssueDelete: (issue: Issue) => void;
  onIssueMove: (issueKey: string, newStatus: IssueStatus) => void;
}

interface ColumnDropZoneProps {
  status: IssueStatus;
  title: string;
  issues: Issue[];
  onIssueMove: (issueKey: string, newStatus: IssueStatus) => void;
  onIssueView: (issue: Issue) => void;
  onIssueDelete: (issue: Issue) => void;
  allIssues: Issue[];
  hoveredIssueKey: string | null;
  onIssueHover: (issueKey: string | null) => void;
  selectedIssues: Set<string>;
  onIssueSelect: (issueKey: string) => void;
}

const ColumnDropZone = ({
  status,
  title,
  issues,
  onIssueMove,
  onIssueView,
  onIssueDelete,
  allIssues,
  hoveredIssueKey,
  onIssueHover,
  selectedIssues,
  onIssueSelect
}: ColumnDropZoneProps) => {
  const ref = useRef<HTMLDivElement>(null);
  
  const [{ isOver }, drop] = useDrop({
    accept: ItemTypes.TASK, // Reusing task item type for now
    drop: (item: { id: string; status: string }) => {
      if (item.status !== status) {
        // Moving to different status
        onIssueMove(item.id, status);
      }
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver()
    })
  });

  drop(ref);

  // Get column header color based on status
  const getColumnColor = () => {
    switch (status) {
      case 'open':
        return 'text-blue-600 dark:text-blue-400';
      case 'in_progress':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'testing':
        return 'text-purple-600 dark:text-purple-400';
      case 'closed':
        return 'text-green-600 dark:text-green-400';
      case 'reopened':
        return 'text-orange-600 dark:text-orange-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  // Get column header glow based on status
  const getColumnGlow = () => {
    switch (status) {
      case 'open':
        return 'bg-blue-500/30 shadow-[0_0_10px_2px_rgba(59,130,246,0.2)]';
      case 'in_progress':
        return 'bg-yellow-500/30 shadow-[0_0_10px_2px_rgba(234,179,8,0.2)]';
      case 'testing':
        return 'bg-purple-500/30 shadow-[0_0_10px_2px_rgba(168,85,247,0.2)]';
      case 'closed':
        return 'bg-green-500/30 shadow-[0_0_10px_2px_rgba(16,185,129,0.2)]';
      case 'reopened':
        return 'bg-orange-500/30 shadow-[0_0_10px_2px_rgba(249,115,22,0.2)]';
      default:
        return 'bg-gray-500/30';
    }
  };

  return (
    <div 
      ref={ref} 
      className={`flex flex-col bg-white/20 dark:bg-black/30 ${isOver ? 'bg-gray-100/50 dark:bg-gray-800/20 border-t-2 border-t-[#00ff00] shadow-[inset_0_1px_10px_rgba(0,255,0,0.1)]' : ''} transition-colors duration-200 h-full`}
    >
      <div className="text-center py-3 sticky top-0 z-10 bg-white/80 dark:bg-black/80 backdrop-blur-sm">
        <h3 className={`font-mono ${getColumnColor()} text-sm`}>{title} ({issues.length})</h3>
        {/* Column header divider with glow */}
        <div className={`absolute bottom-0 left-[15%] right-[15%] w-[70%] mx-auto h-[1px] ${getColumnGlow()}`}></div>
      </div>
      
      <div className="px-1 flex-1 overflow-y-auto space-y-3 py-3">
        {issues.map((issue, index) => (
          <DraggableIssueCard
            key={issue.issue_key}
            issue={issue}
            index={index}
            onView={() => onIssueView(issue)}
            onDelete={onIssueDelete}
            hoveredIssueKey={hoveredIssueKey}
            onIssueHover={onIssueHover}
          />
        ))}
      </div>
    </div>
  );
};

export const IssueBoardView = ({
  issues,
  onIssueView,
  onIssueDelete,
  onIssueMove
}: IssueBoardViewProps) => {
  const [hoveredIssueKey, setHoveredIssueKey] = useState<string | null>(null);
  const [selectedIssues, setSelectedIssues] = useState<Set<string>>(new Set());

  // State for delete confirmation modal
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [issueToDelete, setIssueToDelete] = useState<Issue | null>(null);

  const { showToast } = useToast();

  // Multi-select handlers
  const toggleIssueSelection = useCallback((issueKey: string) => {
    setSelectedIssues(prev => {
      const newSet = new Set(prev);
      if (newSet.has(issueKey)) {
        newSet.delete(issueKey);
      } else {
        newSet.add(issueKey);
      }
      return newSet;
    });
  }, []);

  // Get issues by status
  const getIssuesByStatus = (status: IssueStatus) => {
    return issues.filter(issue => issue.status === status);
  };

  // Handle delete confirmation
  const handleDeleteIssue = (issue: Issue) => {
    setIssueToDelete(issue);
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (issueToDelete) {
      try {
        await onIssueDelete(issueToDelete);
        showToast(`Issue ${issueToDelete.issue_key} deleted successfully`, 'success');
      } catch (error) {
        showToast(`Failed to delete issue: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      }
    }
    setShowDeleteConfirm(false);
    setIssueToDelete(null);
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(false);
    setIssueToDelete(null);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Board Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Issues Board ({issues.length} total)
        </h2>
      </div>

      {/* Board Columns */}
      <div className="grid grid-cols-5 gap-0 flex-1">
        {/* Open Column */}
        <ColumnDropZone
          status="open"
          title="Open"
          issues={getIssuesByStatus('open')}
          onIssueMove={onIssueMove}
          onIssueView={onIssueView}
          onIssueDelete={handleDeleteIssue}
          allIssues={issues}
          hoveredIssueKey={hoveredIssueKey}
          onIssueHover={setHoveredIssueKey}
          selectedIssues={selectedIssues}
          onIssueSelect={toggleIssueSelection}
        />

        {/* In Progress Column */}
        <ColumnDropZone
          status="in_progress"
          title="In Progress"
          issues={getIssuesByStatus('in_progress')}
          onIssueMove={onIssueMove}
          onIssueView={onIssueView}
          onIssueDelete={handleDeleteIssue}
          allIssues={issues}
          hoveredIssueKey={hoveredIssueKey}
          onIssueHover={setHoveredIssueKey}
          selectedIssues={selectedIssues}
          onIssueSelect={toggleIssueSelection}
        />

        {/* Testing Column */}
        <ColumnDropZone
          status="testing"
          title="Testing"
          issues={getIssuesByStatus('testing')}
          onIssueMove={onIssueMove}
          onIssueView={onIssueView}
          onIssueDelete={handleDeleteIssue}
          allIssues={issues}
          hoveredIssueKey={hoveredIssueKey}
          onIssueHover={setHoveredIssueKey}
          selectedIssues={selectedIssues}
          onIssueSelect={toggleIssueSelection}
        />

        {/* Closed Column */}
        <ColumnDropZone
          status="closed"
          title="Closed"
          issues={getIssuesByStatus('closed')}
          onIssueMove={onIssueMove}
          onIssueView={onIssueView}
          onIssueDelete={handleDeleteIssue}
          allIssues={issues}
          hoveredIssueKey={hoveredIssueKey}
          onIssueHover={setHoveredIssueKey}
          selectedIssues={selectedIssues}
          onIssueSelect={toggleIssueSelection}
        />

        {/* Reopened Column */}
        <ColumnDropZone
          status="reopened"
          title="Reopened"
          issues={getIssuesByStatus('reopened')}
          onIssueMove={onIssueMove}
          onIssueView={onIssueView}
          onIssueDelete={handleDeleteIssue}
          allIssues={issues}
          hoveredIssueKey={hoveredIssueKey}
          onIssueHover={setHoveredIssueKey}
          selectedIssues={selectedIssues}
          onIssueSelect={toggleIssueSelection}
        />
      </div>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmModal
        isOpen={showDeleteConfirm}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
        itemName={issueToDelete?.title || ''}
        itemType="issue"
      />
    </div>
  );
};
