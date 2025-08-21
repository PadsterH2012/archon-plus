// This file is now deprecated - workflow types have been moved to the template management system
// All workflow functionality is now handled through Template Management
// Legacy types kept for backward compatibility during migration

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  taskGroups: string[]; // task group IDs
  defaultContext: Record<string, any>;
  applicableProjectTypes: string[];
}
