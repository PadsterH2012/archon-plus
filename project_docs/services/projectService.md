# projectService

**File Path:** `archon-ui-main/src/services/projectService.ts`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive project management service providing API integration for projects, tasks, documents, and real-time updates with validation and error handling.

## Props/Parameters
No props required - this is a service object with methods.

## Dependencies

### Imports
```javascript
import type { 
  Project, Task, CreateProjectRequest, UpdateProjectRequest,
  CreateTaskRequest, UpdateTaskRequest, DatabaseTaskStatus, UITaskStatus,
  ProjectManagementEvent
} from '../types/project';
import { 
  validateCreateProject, validateUpdateProject, validateCreateTask, 
  validateUpdateTask, validateUpdateTaskStatus, formatValidationErrors
} from '../lib/projectSchemas';
import { dbTaskToUITask, uiStatusToDBStatus } from '../types/project';
```

### Exports
```javascript
export const projectService: ProjectService;
export class ProjectServiceError extends Error;
export class ValidationError extends ProjectServiceError;
export class MCPToolError extends ProjectServiceError;
```

## Key Functions/Methods

### Project Operations
- **listProjects**: Retrieves all projects with sorting and filtering
- **getProject**: Gets single project by ID with full details
- **createProject**: Creates new project with validation
- **createProjectWithStreaming**: Creates project with real-time progress tracking
- **updateProject**: Updates project properties with validation
- **deleteProject**: Deletes project and associated data
- **getProjectFeatures**: Retrieves project features for categorization

### Task Operations
- **getTasksByProject**: Gets all tasks for a specific project
- **getTask**: Gets single task by ID
- **createTask**: Creates new task with validation
- **updateTask**: Updates task properties
- **updateTaskStatus**: Updates task status with UI/DB conversion
- **deleteTask**: Deletes task with cleanup
- **updateTaskOrder**: Updates task order and optionally status
- **getTasksByStatus**: Gets tasks filtered by status

### Document Operations
- **listProjectDocuments**: Gets all documents for a project
- **getDocument**: Gets single document by ID
- **createDocument**: Creates new document
- **updateDocument**: Updates document content
- **deleteDocument**: Deletes document
- **getDocumentVersionHistory**: Gets version history for documents
- **getVersionContent**: Gets specific version content
- **restoreDocumentVersion**: Restores document to previous version

## Usage Example
```javascript
import { projectService } from '../services/projectService';

// Project operations
const projects = await projectService.listProjects();
const project = await projectService.createProject({
  title: "New Project",
  description: "Project description"
});

// Task operations
const tasks = await projectService.getTasksByProject(projectId);
const task = await projectService.createTask({
  project_id: projectId,
  title: "New Task",
  description: "Task description",
  status: "todo"
});

// Document operations
const docs = await projectService.listProjectDocuments(projectId);
const doc = await projectService.createDocument(projectId, {
  title: "New Document",
  content: { sections: [] }
});
```

## State Management
No state management - stateless service with methods

## Side Effects
- **API requests**: Makes HTTP requests to backend project API
- **Validation**: Validates all input data before API calls
- **Error handling**: Comprehensive error handling with custom error types
- **WebSocket**: Manages WebSocket connections for real-time updates
- **Type conversion**: Converts between UI and database formats

## Related Files
- **Parent components:** ProjectPage, TasksTab, DocsTab
- **Child components:** None - this is a service layer
- **Shared utilities:** 
  - Project type definitions
  - Validation schemas
  - API configuration

## Notes
- Comprehensive validation using Zod schemas
- Custom error classes for different error types
- Real-time WebSocket integration for live updates
- Type-safe API calls with TypeScript
- Automatic UI/database status conversion
- Streaming project creation with progress tracking
- Document versioning and restoration capabilities
- Robust error handling and logging
- RESTful API design with proper HTTP methods

---
*Auto-generated documentation - verify accuracy before use*
