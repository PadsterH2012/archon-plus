# TaskBoardView

**File Path:** `archon-ui-main/src/components/project-tasks/TaskBoardView.tsx`
**Last Updated:** 2025-01-22

## Purpose
Kanban-style board view for task management with drag-and-drop between columns, multi-select operations, and visual status indicators for agile project workflows.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tasks | Task[] | yes | - | Array of tasks to display |
| onTaskView | (task: Task) => void | yes | - | Callback when task is viewed |
| onTaskComplete | (taskId: string) => void | yes | - | Callback when task is completed |
| onTaskDelete | (task: Task) => void | yes | - | Callback when task is deleted |
| onTaskMove | (taskId: string, newStatus: Task['status']) => void | yes | - | Callback when task is moved between columns |
| onTaskReorder | (taskId: string, targetIndex: number, status: Task['status']) => void | yes | - | Callback when task is reordered within column |

## Dependencies

### Imports
```javascript
import React, { useRef, useState, useCallback } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { useToast } from '../../contexts/ToastContext';
import { DeleteConfirmModal } from '../../pages/ProjectPage';
import { CheckSquare, Square, Trash2, ArrowRight } from 'lucide-react';
import { projectService } from '../../services/projectService';
import { Task } from './TaskTableView';
import { ItemTypes, getAssigneeIcon, getAssigneeGlow, getOrderColor, getOrderGlow } from '../../lib/task-utils';
import { DraggableTaskCard } from './DraggableTaskCard';
```

### Exports
```javascript
export const TaskBoardView: React.FC<TaskBoardViewProps>;
```

## Key Functions/Methods
- **ColumnDropZone**: Individual column component with drop zone functionality
- **getColumnColor/getColumnGlow**: Returns status-based styling for column headers
- **toggleTaskSelection**: Handles multi-select task operations
- **selectAllTasks/clearSelection**: Bulk selection operations
- **handleMassDelete**: Deletes multiple selected tasks
- **handleMassStatusChange**: Changes status for multiple selected tasks
- **mapUIStatusToDBStatus**: Converts UI status to database format
- **handleDeleteTask/confirmDeleteTask**: Task deletion with confirmation
- **getTasksByStatus**: Filters and sorts tasks by status column

## Usage Example
```javascript
import { TaskBoardView } from '../components/project-tasks/TaskBoardView';

<TaskBoardView
  tasks={tasks}
  onTaskView={openEditModal}
  onTaskComplete={completeTask}
  onTaskDelete={deleteTask}
  onTaskMove={moveTaskToStatus}
  onTaskReorder={reorderTaskInColumn}
/>
```

## State Management
- **hoveredTaskId**: Currently hovered task for visual feedback
- **selectedTasks**: Set of selected task IDs for bulk operations
- **showDeleteConfirm**: Boolean for delete confirmation modal
- **taskToDelete**: Task marked for deletion

## Side Effects
- **Drag and drop**: Handles task movement between columns and reordering
- **Multi-select**: Supports bulk operations on multiple tasks
- **Visual feedback**: Provides hover states and selection indicators
- **Status mapping**: Converts between UI and database status formats

## Related Files
- **Parent components:** TasksTab
- **Child components:** 
  - ColumnDropZone (internal)
  - DraggableTaskCard
  - DeleteConfirmModal
- **Shared utilities:** 
  - projectService
  - task-utils library
  - useToast context

## Notes
- Four-column Kanban layout: Backlog → In Progress → Review → Complete
- Drag-and-drop with react-dnd for smooth interactions
- Multi-select with Ctrl/Cmd+click for bulk operations
- Status-based color coding with glow effects
- Visual drop zones with hover feedback
- Task reordering within columns maintains priority
- Bulk status changes and deletions
- Responsive design with proper column spacing
- Confirmation dialogs for destructive operations
- Real-time visual feedback for all interactions

---
*Auto-generated documentation - verify accuracy before use*
