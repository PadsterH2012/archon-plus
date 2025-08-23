# TaskTableView

**File Path:** `archon-ui-main/src/components/project-tasks/TaskTableView.tsx`
**Last Updated:** 2025-01-22

## Purpose
Advanced table view for task management with drag-and-drop reordering, inline editing, visual priority indicators, and smooth scroll effects.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tasks | Task[] | yes | - | Array of tasks to display |
| onTaskView | (task: Task) => void | yes | - | Callback when task is viewed |
| onTaskComplete | (taskId: string) => void | yes | - | Callback when task is completed |
| onTaskDelete | (task: Task) => void | yes | - | Callback when task is deleted |
| onTaskReorder | (taskId: string, newOrder: number, status: Task['status']) => void | yes | - | Callback when task is reordered |
| onTaskCreate | (task: Omit<Task, 'id'>) => Promise<void> | no | - | Callback for creating new tasks |
| onTaskUpdate | (taskId: string, updates: Partial<Task>) => Promise<void> | no | - | Callback for updating tasks |

## Dependencies

### Imports
```javascript
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { Check, Trash2, Edit, Tag, User, Bot, Clipboard, Save, Plus } from 'lucide-react';
import { useToast } from '../../contexts/ToastContext';
import { DeleteConfirmModal } from '../../pages/ProjectPage';
import { projectService } from '../../services/projectService';
import { ItemTypes, getAssigneeIcon, getAssigneeGlow, getOrderColor, getOrderGlow } from '../../lib/task-utils';
import { DraggableTaskCard } from './DraggableTaskCard';
```

### Exports
```javascript
export const TaskTableView: React.FC<TaskTableViewProps>;
export interface Task;
```

## Key Functions/Methods
- **getAssigneeGlassStyle**: Returns glass morphism styles based on assignee type
- **getOrderGlassStyle/getOrderTextColor**: Returns priority-based styling (lower order = higher priority)
- **reorderTasks**: Reorders tasks and updates sequential order numbers
- **EditableCell**: Inline editable cell component with keyboard shortcuts
- **DraggableTaskRow**: Individual draggable table row with hover effects
- **AddTaskRow**: Always-visible row for creating new tasks
- **calculateOpacity**: Calculates scroll-based opacity for fade effects
- **updateOpacities**: Updates row opacities on scroll
- **getTasksByStatus**: Filters and sorts tasks by status
- **getHeaderColor/getHeaderGlow**: Returns status-based header styling

## Usage Example
```javascript
import { TaskTableView } from '../components/project-tasks/TaskTableView';

<TaskTableView
  tasks={tasks}
  onTaskView={openEditModal}
  onTaskComplete={completeTask}
  onTaskDelete={deleteTask}
  onTaskReorder={handleTaskReorder}
  onTaskCreate={createTaskInline}
  onTaskUpdate={updateTaskInline}
/>
```

## State Management
- **statusFilter**: Current status filter ('backlog' | 'in-progress' | 'review' | 'complete' | 'all')
- **showDeleteConfirm**: Boolean for delete confirmation modal
- **taskToDelete**: Task marked for deletion
- **scrollOpacities**: Map of row opacities for scroll effects
- **editingField**: Currently editing field in inline editor
- **isHovering**: Hover state for visual feedback

## Side Effects
- **Scroll effects**: Monitors scroll position for fade effects
- **Drag and drop**: Handles task reordering with visual feedback
- **Inline editing**: Real-time field editing with keyboard shortcuts
- **Opacity calculations**: Smooth fade effects based on scroll position

## Related Files
- **Parent components:** TasksTab
- **Child components:** 
  - EditableCell (internal)
  - DraggableTaskRow (internal)
  - AddTaskRow (internal)
  - DeleteConfirmModal
  - DraggableTaskCard
- **Shared utilities:** 
  - projectService
  - task-utils library
  - useToast context

## Notes
- Advanced drag-and-drop with react-dnd
- Inline editing with keyboard shortcuts (Enter/Tab to save, Escape to cancel)
- Visual priority indicators with glass morphism styling
- Smooth scroll-based fade effects for better UX
- Status-based filtering and organization
- Assignee-specific styling (User: blue, AI IDE Agent: emerald, Archon: pink)
- Priority-based coloring (lower order = warmer colors)
- Always-visible add task row for quick task creation
- Comprehensive keyboard navigation support
- Real-time visual feedback for all interactions

---
*Auto-generated documentation - verify accuracy before use*
