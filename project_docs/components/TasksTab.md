# TasksTab

**File Path:** `archon-ui-main/src/components/project-tasks/TasksTab.tsx`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive task management component providing both table and board views with real-time updates, drag-and-drop reordering, and inline editing capabilities.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| initialTasks | Task[] | yes | - | Initial array of tasks to display |
| onTasksChange | (tasks: Task[]) => void | yes | - | Callback when tasks array changes |
| projectId | string | yes | - | Project ID for task operations |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Table, LayoutGrid, Plus, Wifi, WifiOff, List } from 'lucide-react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Toggle } from '../ui/Toggle';
import { projectService } from '../../services/projectService';
import { useTaskSocket } from '../../hooks/useTaskSocket';
import type { CreateTaskRequest, UpdateTaskRequest, DatabaseTaskStatus } from '../../types/project';
import { TaskTableView, Task } from './TaskTableView';
import { TaskBoardView } from './TaskBoardView';
import { EditTaskModal } from './EditTaskModal';
```

### Exports
```javascript
export const TasksTab: React.FC<TasksTabProps>;
```

## Key Functions/Methods
- **mapUIStatusToDBStatus/mapDBStatusToUIStatus**: Converts between UI and database status formats
- **mapDatabaseTaskToUITask**: Maps database task format to UI task format
- **handleTaskUpdated/Created/Deleted/Archived**: Real-time WebSocket event handlers
- **loadProjectFeatures**: Loads project features for task categorization
- **openEditModal/closeModal**: Modal management for task editing
- **saveTask**: Saves task changes with conflict resolution
- **updateTasks**: Updates task state and notifies parent
- **handleTaskReorder**: Handles drag-and-drop task reordering
- **moveTask**: Moves task between status columns
- **createTaskInline/updateTaskInline**: Inline task creation and updates
- **getTasksForPrioritySelection**: Gets tasks for priority/order selection

## Usage Example
```javascript
import { TasksTab } from '../components/project-tasks/TasksTab';

<TasksTab
  initialTasks={tasks}
  onTasksChange={setTasks}
  projectId={selectedProject.id}
/>
```

## State Management
- **viewMode**: 'table' | 'board' - Current view mode
- **tasks**: Array of Task objects with real-time updates
- **editingTask**: Currently editing task for modal
- **isModalOpen**: Boolean for edit modal visibility
- **projectFeatures**: Array of project features for categorization
- **isLoadingFeatures**: Boolean for features loading state
- **isSavingTask**: Boolean for task save operation
- **isWebSocketConnected**: Boolean for WebSocket connection status

## Side Effects
- **Real-time updates**: WebSocket connection for live task updates
- **Task synchronization**: Syncs local state with server changes
- **Conflict resolution**: Handles concurrent edits with timestamps
- **Feature loading**: Loads project features on mount
- **Debounced persistence**: Optimized task order persistence

## Related Files
- **Parent components:** ProjectPage
- **Child components:** 
  - TaskTableView, TaskBoardView
  - EditTaskModal
  - Toggle (UI component)
- **Shared utilities:** 
  - projectService
  - useTaskSocket hook
  - DndProvider for drag-and-drop

## Notes
- Supports both table and board (Kanban) views
- Real-time collaboration with conflict resolution
- Drag-and-drop task reordering within and between columns
- Inline task creation and editing
- WebSocket-based live updates
- Optimistic UI updates with server reconciliation
- Debounced persistence for performance
- Feature-based task categorization
- Assignee management with predefined options
- Task status workflow: backlog → in-progress → review → complete

---
*Auto-generated documentation - verify accuracy before use*
