import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Table, LayoutGrid, Plus, Wifi, WifiOff, List } from 'lucide-react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Toggle } from '../ui/Toggle';

// Issue-specific imports
import { Issue, IssueStatus, QueryIssuesResponse, UpdateIssueStatusResponse } from '../../types/issue';
import { issueService } from '../../services/issueService';
import { IssueTableView } from './IssueTableView';
import { IssueBoardView } from './IssueBoardView';
import { EditIssueModal } from './EditIssueModal';

// Issue status mapping (status values are the same between UI and DB)
const mapUIStatusToDBStatus = (uiStatus: IssueStatus): string => {
  return uiStatus; // Direct mapping since they're the same
};

const mapDBStatusToUIStatus = (dbStatus: string): IssueStatus => {
  // Validate and return the status, defaulting to 'open' if invalid
  const validStatuses: IssueStatus[] = ['open', 'in_progress', 'testing', 'closed', 'reopened'];
  return validStatuses.includes(dbStatus as IssueStatus) ? dbStatus as IssueStatus : 'open';
};

// Helper function to map database issue format to UI issue format
const mapDatabaseIssueToUIIssue = (dbIssue: any): Issue => {
  return {
    issue_key: dbIssue.issue_key,
    title: dbIssue.title,
    status: mapDBStatusToUIStatus(dbIssue.status),
    priority: dbIssue.priority || 'medium',
    severity: dbIssue.severity || 'minor',
    assignee_username: dbIssue.assignee_username || null,
    project_name: dbIssue.project_name,
    project_key: dbIssue.project_key,
    reporter_username: dbIssue.reporter_username || null,
    task_id: dbIssue.task_id || null,
    created_date: dbIssue.created_date,
    updated_date: dbIssue.updated_date,
  };
};

export const IssuesTab = ({
  projectId,
  projectName
}: {
  projectId: string;
  projectName: string;
}) => {
  const [viewMode, setViewMode] = useState<'table' | 'board'>('board');
  const [issues, setIssues] = useState<Issue[]>([]);
  const [editingIssue, setEditingIssue] = useState<Issue | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoadingIssues, setIsLoadingIssues] = useState(false);
  const [isSavingIssue, setIsSavingIssue] = useState<boolean>(false);
  const [issuesError, setIssuesError] = useState<string | null>(null);
  
  // Load issues on component mount
  useEffect(() => {
    loadIssues();
  }, [projectId, projectName]);

  const loadIssues = async () => {
    if (!projectName) return;

    setIsLoadingIssues(true);
    setIssuesError(null);
    try {
      // Call issue service to get issues by project
      const response = await issueService.queryIssuesByProject(projectName, undefined, 100);

      if (response.success && response.issues) {
        const mappedIssues = response.issues.map(mapDatabaseIssueToUIIssue);
        setIssues(mappedIssues);
      } else {
        throw new Error(response.error || 'Failed to load issues');
      }
    } catch (error) {
      console.error('Failed to load issues:', error);
      setIssuesError(error instanceof Error ? error.message : 'Unknown error');
      setIssues([]);
    } finally {
      setIsLoadingIssues(false);
    }
  };

  // Modal management functions
  const openEditModal = async (issue: Issue) => {
    setEditingIssue(issue);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingIssue(null);
  };

  const saveIssue = async (issue: Issue) => {
    setEditingIssue(issue);
    
    setIsSavingIssue(true);
    try {
      // For now, just close the modal - actual save functionality to be implemented
      closeModal();
      // Reload issues to get latest data
      await loadIssues();
    } catch (error) {
      console.error('Failed to save issue:', error);
      alert(`Failed to save issue: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSavingIssue(false);
    }
  };

  // Issue move function (for board view)
  const moveIssue = async (issueKey: string, newStatus: IssueStatus) => {
    console.log(`[IssuesTab] Attempting to move issue ${issueKey} to new status: ${newStatus}`);
    try {
      const movingIssue = issues.find(issue => issue.issue_key === issueKey);
      if (!movingIssue) {
        console.warn(`[IssuesTab] Issue ${issueKey} not found for move operation.`);
        return;
      }
      
      const oldStatus = movingIssue.status;
      console.log(`[IssuesTab] Moving issue ${movingIssue.title} from ${oldStatus} to ${newStatus}`);

      // Call issue service to update issue status
      const response = await issueService.updateIssueStatus(
        issueKey,
        mapUIStatusToDBStatus(newStatus),
        `Status changed from ${oldStatus} to ${newStatus} via kanban board`
      );
      
      console.log(`[IssuesTab] Successfully updated issue ${issueKey} status in backend.`);
      
      // Reload issues to get latest data
      await loadIssues();
      
    } catch (error) {
      console.error(`[IssuesTab] Failed to move issue ${issueKey}:`, error);
      alert(`Failed to move issue: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const deleteIssue = async (issue: Issue) => {
    try {
      // For now, just show alert - actual delete functionality to be implemented
      alert('Issue deletion not yet implemented');
    } catch (error) {
      console.error('Failed to delete issue:', error);
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="min-h-[70vh] relative">
        {/* Main content - Table or Board view */}
        <div className="relative h-[calc(100vh-220px)] overflow-auto">
          {isLoadingIssues ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="w-6 h-6 text-orange-500 mx-auto mb-4 animate-spin border-2 border-orange-500 border-t-transparent rounded-full" />
                <p className="text-gray-600 dark:text-gray-400">Loading issues...</p>
              </div>
            </div>
          ) : issuesError ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="w-6 h-6 text-red-500 mx-auto mb-4">⚠️</div>
                <p className="text-red-600 dark:text-red-400 mb-4">{issuesError}</p>
                <button 
                  onClick={loadIssues} 
                  className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : viewMode === 'table' ? (
            <IssueTableView
              issues={issues}
              onIssueView={openEditModal}
              onIssueDelete={deleteIssue}
            />
          ) : (
            <IssueBoardView
              issues={issues}
              onIssueView={openEditModal}
              onIssueDelete={deleteIssue}
              onIssueMove={moveIssue}
            />
          )}
        </div>

        {/* Fixed View Controls */}
        <div className="fixed bottom-6 left-0 right-0 flex justify-center z-50 pointer-events-none">
          <div className="flex items-center gap-4">
            {/* Add Issue Button */}
            <button 
              onClick={() => {
                setEditingIssue({
                  issue_key: '',
                  title: '',
                  status: 'open',
                  priority: 'medium',
                  severity: 'minor',
                  assignee_username: null,
                  project_name: projectName,
                  project_key: '',
                  reporter_username: null,
                  task_id: null,
                  created_date: new Date().toISOString(),
                  updated_date: new Date().toISOString()
                });
                setIsModalOpen(true);
              }}
              className="relative px-5 py-2.5 flex items-center gap-2 bg-white/80 dark:bg-black/90 border border-gray-200 dark:border-gray-800 rounded-lg shadow-[0_0_20px_rgba(0,0,0,0.1)] dark:shadow-[0_0_20px_rgba(0,0,0,0.5)] backdrop-blur-md pointer-events-auto text-cyan-600 dark:text-cyan-400 hover:text-cyan-700 dark:hover:text-cyan-300 transition-all duration-300"
            >
              <Plus className="w-4 h-4 mr-1" />
              <span>Add Issue</span>
              <span className="absolute bottom-0 left-[0%] right-[0%] w-[95%] mx-auto h-[2px] bg-cyan-500 shadow-[0_0_10px_2px_rgba(34,211,238,0.4)] dark:shadow-[0_0_20px_5px_rgba(34,211,238,0.7)]"></span>
            </button>
          
            {/* View Toggle Controls */}
            <div className="flex items-center bg-white/80 dark:bg-black/90 border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden shadow-[0_0_20px_rgba(0,0,0,0.1)] dark:shadow-[0_0_20px_rgba(0,0,0,0.5)] backdrop-blur-md pointer-events-auto">
              <button 
                onClick={() => setViewMode('table')} 
                className={`px-5 py-2.5 flex items-center gap-2 relative transition-all duration-300 ${viewMode === 'table' ? 'text-cyan-600 dark:text-cyan-400' : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-300'}`}
              >
                <Table className="w-4 h-4" />
                <span>Table</span>
                {viewMode === 'table' && <span className="absolute bottom-0 left-[15%] right-[15%] w-[70%] mx-auto h-[2px] bg-cyan-500 shadow-[0_0_10px_2px_rgba(34,211,238,0.4)] dark:shadow-[0_0_20px_5px_rgba(34,211,238,0.7)]"></span>}
              </button>
              <button 
                onClick={() => setViewMode('board')} 
                className={`px-5 py-2.5 flex items-center gap-2 relative transition-all duration-300 ${viewMode === 'board' ? 'text-purple-600 dark:text-purple-400' : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-300'}`}
              >
                <LayoutGrid className="w-4 h-4" />
                <span>Board</span>
                {viewMode === 'board' && <span className="absolute bottom-0 left-[15%] right-[15%] w-[70%] mx-auto h-[2px] bg-purple-500 shadow-[0_0_10px_2px_rgba(168,85,247,0.4)] dark:shadow-[0_0_20px_5px_rgba(168,85,247,0.7)]"></span>}
              </button>
            </div>
          </div>
        </div>

        {/* Edit Issue Modal */}
        <EditIssueModal
          isModalOpen={isModalOpen}
          editingIssue={editingIssue}
          isSavingIssue={isSavingIssue}
          onClose={closeModal}
          onSave={saveIssue}
        />
      </div>
    </DndProvider>
  );
};
