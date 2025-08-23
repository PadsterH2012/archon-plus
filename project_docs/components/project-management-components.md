# Project Management Components Documentation

**File Path:** `archon-ui-main/src/components/project-tasks/` directory
**Last Updated:** 2025-08-23

## Purpose
Comprehensive documentation of advanced project management components that provide sophisticated project features including template management, component libraries, data visualization, document management, task handling, and workflow integration patterns.

## Core Project Management Components

### 1. TemplateManagement
**File:** `TemplateManagement.tsx`
**Purpose:** Central hub for managing workflow templates, components, and assignments

**Key Features:**
- **Multi-tab Interface:** Templates, Components, and Assignments tabs
- **Template CRUD Operations:** Create, read, update, delete templates
- **Component Integration:** Links to ComponentLibrary for reusable components
- **Assignment Management:** Template assignment across hierarchy levels
- **Search and Filtering:** Real-time filtering for all content types
- **State Management:** Comprehensive state with loading and error handling

**Props Interface:**
```typescript
interface TemplateManagementProps {
  projectId: string;
  className?: string;
  onTemplateSelect?: (template: TemplateDefinition) => void;
  onComponentSelect?: (component: TemplateComponent) => void;
  onAssignmentSelect?: (assignment: TemplateAssignment) => void;
}
```

**State Structure:**
```typescript
interface TemplateManagementState {
  activeTab: 'templates' | 'components' | 'assignments' | 'analytics';
  isLoading: boolean;
  isSaving: boolean;
  isDeleting: boolean;
  templates: TemplateDefinition[];
  components: TemplateComponent[];
  assignments: TemplateAssignment[];
  showTemplateEditor: boolean;
  showComponentEditor: boolean;
  showAssignmentEditor: boolean;
  showDeleteConfirmation: boolean;
  templateFilter: string;
  componentFilter: string;
  assignmentFilter: string;
  searchQuery: string; // Global search across all tabs
}
```

### 2. TemplateEditor
**File:** `TemplateEditor.tsx`
**Purpose:** Advanced editor for creating and modifying workflow templates

**Key Features:**
- **Multi-tab Editor:** Basic Info, Content, Components, Settings, Testing
- **Template Content Editing:** Rich text editor with component placeholders
- **Component Integration:** Drag-and-drop component references
- **Live Preview:** Real-time template preview and validation
- **Testing Framework:** Built-in template testing and validation
- **Version Control:** Template versioning and change tracking

**Props Interface:**
```typescript
interface TemplateEditorProps {
  template?: TemplateDefinition;
  mode: TemplateOperationType; // 'create' | 'edit' | 'copy' | 'delete' | 'activate' | 'deactivate'
  isOpen: boolean;
  onClose: () => void;
  onSave: (template: TemplateDefinition) => void; // Required callback
  onTest?: (template: TemplateDefinition, testTask: string) => Promise<TemplateTestResult>;
  className?: string;
}
```

**Template Syntax:**
```typescript
// Component references
{{group::component_name}}
{{action::action_name}}
{{sequence::sequence_name}}

// User task insertion point
{{USER_TASK}}

// Context variables
{{PROJECT_ID}}
{{TASK_ID}}
{{USER_NAME}}
```

### 3. ComponentLibrary
**File:** `ComponentLibrary.tsx`
**Purpose:** Library of reusable template components with usage analytics

**Key Features:**
- **Component Catalog:** Browse and search reusable components
- **Usage Analytics:** Track component usage across projects
- **Category Filtering:** Filter by component type and category
- **Component Selection:** Multi-select for template building
- **Component Creation:** Create new reusable components
- **Performance Metrics:** Component performance and reliability stats

**Props Interface:**
```typescript
interface ComponentLibraryProps {
  projectId: string;
  selectedComponents?: string[];
  onComponentSelect?: (component: TemplateComponent) => void;
  onComponentEdit?: (component: TemplateComponent) => void;
  onComponentCreate?: () => void;
  showUsageStats?: boolean;
  className?: string;
}
```

**Component Types:**
- **Action Components:** Single-purpose workflow actions
- **Group Components:** Collections of related actions
- **Sequence Components:** Ordered workflow sequences
- **Conditional Components:** Logic-based workflow branches

### 4. AssignmentManager
**File:** `AssignmentManager.tsx`
**Purpose:** Manage template assignments across project hierarchy levels

**Key Features:**
- **Hierarchy Management:** Project, task, and component level assignments
- **Conflict Resolution:** Detect and resolve assignment conflicts
- **Priority Management:** Set assignment priorities and inheritance
- **Visual Hierarchy:** Tree view of assignment structure
- **Bulk Operations:** Mass assignment and modification tools

**Props Interface:**
```typescript
interface AssignmentManagerProps {
  projectId: string;
  hierarchyData: HierarchyNode[];
  assignments: TemplateAssignment[];
  onAssignmentCreate?: (assignment: CreateTemplateAssignmentRequest) => void;
  onAssignmentUpdate?: (id: string, updates: UpdateTemplateAssignmentRequest) => void;
  onAssignmentDelete?: (id: string) => void;
  onConflictResolve?: (conflict: AssignmentConflict) => void;
  className?: string;
}
```

**Hierarchy Levels:**
```typescript
type HierarchyLevel = 'project' | 'task' | 'component' | 'user';

interface TemplateAssignment {
  id: string;
  template_name: string;
  hierarchy_level: HierarchyLevel;
  entity_id: string;
  assignment_scope: 'all' | 'specific' | 'conditional';
  priority: number;
  conditions?: AssignmentCondition[];
}
```

## Document Management Components

### 5. DocumentCard
**File:** `DocumentCard.tsx`
**Purpose:** Card component for displaying and managing project documents

**Key Features:**
- **Document Preview:** Thumbnail and metadata display
- **Quick Actions:** Edit, delete, duplicate, share actions
- **Version Indicators:** Show document version and status
- **Type-specific Icons:** Different icons for different document types
- **Drag and Drop:** Support for document reordering

### 6. VersionHistoryModal
**File:** `VersionHistoryModal.tsx`
**Purpose:** Modal for viewing and managing document version history

**Key Features:**
- **Version Timeline:** Chronological list of document versions
- **Diff Visualization:** Side-by-side comparison of versions
- **Restore Functionality:** Rollback to previous versions
- **Change Tracking:** Detailed change summaries and authors
- **Confirmation Dialogs:** Safe restore operations with confirmation

**Props Interface:**
```typescript
interface VersionHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  documentId?: string;
  fieldName?: string;
  onRestore?: () => void;
}
```

**Version Structure:**
```typescript
interface Version {
  id: string;
  version_number: number;
  change_summary: string;
  change_type: string;
  created_by: string;
  created_at: string;
  content: any;
  document_id?: string;
}
```

### 7. MilkdownEditor
**File:** `MilkdownEditor.tsx`
**Purpose:** Rich text editor for document creation and editing

**Key Features:**
- **WYSIWYG Editing:** Rich text editing with live preview
- **Markdown Support:** Full markdown syntax support
- **Plugin System:** Extensible with custom plugins
- **Collaborative Editing:** Real-time collaborative features
- **Auto-save:** Automatic document saving with debouncing

## Data Visualization Components

### 8. DataTab
**File:** `DataTab.tsx`
**Purpose:** Interactive data visualization and database schema management

**Key Features:**
- **ReactFlow Integration:** Interactive node-based data visualization
- **Database Schema:** Visual representation of database tables and relationships
- **Custom Node Types:** Table nodes with column information
- **Relationship Mapping:** Visual foreign key relationships
- **Interactive Editing:** Drag-and-drop schema modification

**Node Types:**
```typescript
interface TableNode extends Node {
  type: 'table';
  data: {
    label: string;
    columns: string[];
  };
}
```

**Default Schema:**
```typescript
const defaultNodes: Node[] = [
  createTableNode('users', 'Users', [
    'id (PK) - UUID',
    'email - VARCHAR(255)',
    'password - VARCHAR(255)',
    'firstName - VARCHAR(100)',
    'lastName - VARCHAR(100)',
    'createdAt - TIMESTAMP',
    'updatedAt - TIMESTAMP'
  ], 150, 100),
  createTableNode('projects', 'Projects', [
    'id (PK) - UUID',
    'title - VARCHAR(255)',
    'description - TEXT',
    'status - VARCHAR(50)',
    'userId (FK) - UUID',
    'createdAt - TIMESTAMP',
    'updatedAt - TIMESTAMP'
  ], 500, 100)
];
```

## Import/Export Components

### 9. ExportDialog
**File:** `ExportDialog.tsx`
**Purpose:** Modal for configuring and executing project exports

**Key Features:**
- **Export Options:** Full, partial, and selective export types
- **Version Control:** Include/exclude version history
- **Source Management:** Include/exclude knowledge sources
- **Attachment Handling:** Optional attachment inclusion
- **Progress Tracking:** Real-time export progress
- **Download Management:** Automatic download initiation

**Export Options:**
```typescript
interface ExportOptions {
  export_type?: 'full' | 'selective' | 'incremental';
  include_versions?: boolean;
  include_sources?: boolean;
  include_attachments?: boolean;
  version_limit?: number;
  date_range?: [string, string]; // Tuple format: [start_date, end_date]
  selective_components?: string[];
}
```

### 10. ImportDialog
**File:** `ImportDialog.tsx`
**Purpose:** Modal for importing projects and handling conflicts

**Key Features:**
- **File Upload:** Drag-and-drop file upload interface
- **Conflict Resolution:** Handle naming and data conflicts
- **Validation:** Pre-import validation and error checking
- **Progress Tracking:** Real-time import progress
- **Rollback Support:** Ability to rollback failed imports

### 11. ExportImportProgress
**File:** `ExportImportProgress.tsx`
**Purpose:** Progress tracking component for export/import operations

**Key Features:**
- **Real-time Progress:** Live progress updates via WebSocket
- **Step Breakdown:** Detailed progress for each operation step
- **Error Handling:** Display and handle operation errors
- **Cancellation:** Ability to cancel long-running operations
- **Completion Actions:** Post-operation actions and cleanup

### 12. ProjectExportImportActions
**File:** `ProjectExportImportActions.tsx`
**Purpose:** Action buttons and controls for project export/import operations

**Key Features:**
- **Quick Actions:** One-click export/import buttons
- **Batch Operations:** Multiple project operations
- **Template Integration:** Export/import with template preservation
- **Validation Checks:** Pre-operation validation
- **History Tracking:** Operation history and logs

## Task Management Components

### 13. DraggableTaskCard
**File:** `DraggableTaskCard.tsx`
**Purpose:** Draggable card component for task management interfaces

**Key Features:**
- **Drag and Drop:** Full drag-and-drop functionality for task reordering
- **Status Indicators:** Visual status badges and progress indicators
- **Quick Actions:** Inline edit, delete, and status change actions
- **Assignment Display:** Show task assignee and due dates
- **Priority Visualization:** Color-coded priority levels

**Props Interface:**
```typescript
interface DraggableTaskCardProps {
  task: Task;
  onTaskUpdate?: (taskId: string, updates: Partial<Task>) => void;
  onTaskDelete?: (taskId: string) => void;
  isDragging?: boolean;
  className?: string;
}
```

### 14. TaskInputComponents
**File:** `TaskInputComponents.tsx`
**Purpose:** Collection of specialized input components for task creation and editing

**Key Features:**
- **Task Title Input:** Auto-complete and validation
- **Description Editor:** Rich text description editing
- **Assignee Selector:** User selection with search
- **Priority Selector:** Visual priority selection
- **Due Date Picker:** Calendar-based date selection
- **Tag Input:** Multi-tag selection and creation

**Component Types:**
```typescript
// Task title with validation
<TaskTitleInput
  value={title}
  onChange={setTitle}
  placeholder="Enter task title..."
  validation={titleValidation}
/>

// Rich description editor
<TaskDescriptionEditor
  value={description}
  onChange={setDescription}
  placeholder="Describe the task..."
  maxLength={2000}
/>

// Assignee selection
<TaskAssigneeSelector
  selectedAssignee={assignee}
  onAssigneeChange={setAssignee}
  availableUsers={users}
/>
```

## Tab and Navigation Components

### 15. Tabs
**File:** `Tabs.tsx`
**Purpose:** Generic tab component for organizing project content

**Key Features:**
- **Dynamic Tab Creation:** Programmatically add/remove tabs
- **Tab State Management:** Active tab tracking and persistence
- **Custom Tab Content:** Flexible content rendering
- **Tab Validation:** Validate tab content before switching
- **Responsive Design:** Mobile-friendly tab navigation

**Props Interface:**
```typescript
interface TabsProps {
  tabs: TabDefinition[];
  activeTab?: string;
  onTabChange?: (tabId: string) => void;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

interface TabDefinition {
  id: string;
  label: string;
  content: React.ReactNode;
  icon?: React.ReactNode;
  disabled?: boolean;
  badge?: string | number;
}
```

### 16. FeaturesTab
**File:** `FeaturesTab.tsx`
**Purpose:** Tab component for managing project features and capabilities

**Key Features:**
- **Feature Toggle:** Enable/disable project features
- **Feature Configuration:** Configure feature-specific settings
- **Dependency Management:** Handle feature dependencies
- **Feature Analytics:** Track feature usage and performance
- **Permission Control:** Role-based feature access

## Workflow Integration Patterns

### Template Workflow Integration
```typescript
// Template assignment workflow
const assignTemplate = async (
  templateName: string,
  hierarchyLevel: HierarchyLevel,
  entityId: string
) => {
  const assignment = await templateManagementService.assignments.createAssignment({
    template_name: templateName,
    hierarchy_level: hierarchyLevel,
    entity_id: entityId,
    assignment_scope: 'all',
    priority: 0
  });

  return assignment;
};
```

### Component Reuse Patterns
```typescript
// Component library integration
const useComponentLibrary = (projectId: string) => {
  const [components, setComponents] = useState<Component[]>([]);

  const loadComponents = useCallback(async () => {
    const response = await componentService.listComponents(projectId, {
      includeDependencies: true
    });
    setComponents(response.components);
  }, [projectId]);

  return { components, loadComponents };
};
```

### Task Integration Patterns
```typescript
// Task creation from templates
const createTaskFromTemplate = async (
  templateName: string,
  taskData: Partial<Task>
) => {
  const template = await templateManagementService.testing.getTemplate(templateName);
  const testResult = await templateManagementService.testing.testTemplate(
    templateName,
    taskData.description || '',
    taskData
  );

  return {
    ...taskData,
    description: testResult.expanded_content,
    template_metadata: {
      template_name: templateName,
      original_description: taskData.description
    }
  };
};
```

## State Management Patterns

### Centralized State Management
```typescript
// Project management context
interface ProjectManagementState {
  activeProject: Project | null;
  templates: TemplateDefinition[];
  components: TemplateComponent[];
  assignments: TemplateAssignment[];
  tasks: Task[];
  documents: Document[];
  isLoading: boolean;
  error: string | null;
}

const useProjectManagement = (projectId: string) => {
  const [state, setState] = useState<ProjectManagementState>(initialState);

  // State management methods
  const loadProject = useCallback(async () => {
    // Load project data
  }, [projectId]);

  return { state, loadProject };
};
```

### Real-time Updates
```typescript
// WebSocket integration for real-time updates
useEffect(() => {
  const socket = taskUpdateSocketIO.connect();

  socket.on('task_updated', (task: Task) => {
    setState(prev => ({
      ...prev,
      tasks: prev.tasks.map(t => t.id === task.id ? task : t)
    }));
  });

  socket.on('template_assigned', (assignment: TemplateAssignment) => {
    setState(prev => ({
      ...prev,
      assignments: [...prev.assignments, assignment]
    }));
  });

  return () => socket.disconnect();
}, [projectId]);
```

## Integration Notes

### Service Dependencies
- **projectService:** Core project operations
- **templateManagementService:** Template and component management
- **taskUpdateSocketIO:** Real-time task updates
- **exportImportService:** Project export/import functionality

### Component Relationships
- **TemplateManagement** orchestrates **TemplateEditor**, **ComponentLibrary**, and **AssignmentManager**
- **DataTab** provides data visualization for project analytics
- **DocumentCard** and **VersionHistoryModal** handle document lifecycle
- **ExportDialog** and **ImportDialog** manage project portability

### Performance Considerations
- **Lazy Loading:** Components loaded on demand
- **Virtual Scrolling:** Large lists use virtual scrolling
- **Debounced Inputs:** Search and filter inputs are debounced
- **Memoization:** Expensive calculations are memoized
- **WebSocket Optimization:** Selective event subscription
