// Component Management UI Components
// Export all component management related components

export { ComponentHierarchy } from './ComponentHierarchy';
export { ComponentForm } from './ComponentForm';
export { DependencyGraph } from './DependencyGraph';

// Template Management Components
export { TemplateManagement } from '../project-tasks/TemplateManagement';
export { TemplateEditor } from '../project-tasks/TemplateEditor';
export { ComponentLibrary } from '../project-tasks/ComponentLibrary';
export { AssignmentManager } from '../project-tasks/AssignmentManager';

// Re-export types for convenience
export type {
  Component,
  ComponentType,
  ComponentStatus,
  ComponentDependency,
  CreateComponentRequest,
  UpdateComponentRequest,
  ComponentResponse,
  ComponentHierarchyValidation,
  ComponentExecutionOrder
} from '../../types/component';

// Template Management Types
export type {
  TemplateManagementProps,
  TemplateEditorProps,
  ComponentLibraryProps,
  AssignmentManagerProps,
  TemplateAssignment,
  TemplateResolution,
  HierarchyLevel,
  AssignmentScope,
  TemplateOperationType
} from '../../types/templateManagement';
