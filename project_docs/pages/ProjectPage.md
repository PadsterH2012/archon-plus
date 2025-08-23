# ProjectPage

**File Path:** `archon-ui-main/src/pages/ProjectPage.tsx`
**Last Updated:** 2025-01-22

## Purpose
Main project management page providing comprehensive project lifecycle management with real-time updates, task tracking, document management, and streaming project creation capabilities.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| className | string | no | "" | Additional CSS classes |
| data-id | string | no | - | Data identifier for testing/tracking |

## Dependencies

### Imports
```javascript
import { useState, useEffect, useCallback } from 'react';
import { useToast } from '../contexts/ToastContext';
import { motion, AnimatePresence } from 'framer-motion';
import { useStaggeredEntrance } from '../hooks/useStaggeredEntrance';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/project-tasks/Tabs';
import { DocsTab } from '../components/project-tasks/DocsTab';
import { ComponentsTab } from '../components/project-tasks/ComponentsTab';
import { TasksTab } from '../components/project-tasks/TasksTab';
import { Button } from '../components/ui/Button';
import { projectService } from '../services/projectService';
import type { Project, CreateProjectRequest } from '../types/project';
import type { Task } from '../components/project-tasks/TaskTableView';
import { ProjectCreationProgressCard } from '../components/ProjectCreationProgressCard';
import { projectCreationProgressService } from '../services/projectCreationProgressService';
import type { ProjectCreationProgressData } from '../services/projectCreationProgressService';
import { projectListSocketIO, taskUpdateSocketIO } from '../services/socketIOService';
import { ProjectExportImportActions } from '../components/project-tasks/ProjectExportImportActions';
```

### Exports
```javascript
export function ProjectPage(props: ProjectPageProps);
export const DeleteConfirmModal: React.FC<DeleteConfirmModalProps>;
```

## Key Functions/Methods
- **getProjectIcon**: Maps icon names to React components for project display
- **loadProjectsData**: Loads and sorts projects with pinned projects first
- **loadTaskCountsForAllProjects**: Loads task counts for project overview cards
- **loadTasksForProject**: Loads tasks for selected project
- **handleProjectSelect**: Selects project and shows details view
- **handleDeleteProject**: Initiates project deletion with confirmation
- **handleTogglePin**: Toggles project pinned status (only one pinned at a time)
- **handleCreateProject**: Creates new project with streaming progress tracking
- **handleRetryProjectCreation**: Retries failed project creation

## Usage Example
```javascript
import { ProjectPage } from './pages/ProjectPage';

// Used as a route component
<Route path="/projects" component={ProjectPage} />
```

## State Management
- **projects**: Array of Project objects with real-time updates
- **selectedProject**: Currently selected project for detail view
- **tasks**: Array of tasks for selected project
- **projectTaskCounts**: Task count summaries for all projects
- **isLoadingProjects/isLoadingTasks**: Loading states
- **projectsError/tasksError**: Error states
- **activeTab**: Current tab in project details ('tasks', 'docs', 'components')
- **showProjectDetails**: Boolean for project details panel visibility
- **isNewProjectModalOpen**: Boolean for new project modal
- **newProjectForm**: Form state for project creation
- **isCreatingProject**: Boolean for project creation loading
- **showDeleteConfirm**: Boolean for delete confirmation modal
- **projectToDelete**: Project data for deletion confirmation

## Side Effects
- **Initial project load**: Loads projects and selects pinned project on mount
- **Real-time project updates**: WebSocket connection for project list changes
- **Real-time task updates**: WebSocket connection for task count updates
- **Task loading**: Loads tasks when project is selected
- **Streaming project creation**: Real-time progress tracking for new projects

## Related Files
- **Parent components:** App routing system
- **Child components:** 
  - Tabs, TabsList, TabsTrigger, TabsContent
  - DocsTab, ComponentsTab, TasksTab
  - ProjectCreationProgressCard
  - ProjectExportImportActions
  - DeleteConfirmModal (internal)
- **Shared utilities:** 
  - projectService
  - projectCreationProgressService
  - projectListSocketIO, taskUpdateSocketIO
  - useStaggeredEntrance hook
  - useToast context

## Notes
- Supports pinned projects (only one can be pinned at a time)
- Real-time updates via WebSocket for projects and tasks
- Streaming project creation with progress tracking
- Comprehensive error handling and retry mechanisms
- Responsive design with animated transitions
- Export/import functionality for project data
- Task count summaries on project cards
- Automatic selection of pinned project on page load
- Supports project deletion with confirmation dialog

---
*Auto-generated documentation - verify accuracy before use*
