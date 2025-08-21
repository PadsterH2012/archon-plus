// TypeScript interfaces for Template Management UI
// Extends existing component.ts types with template management specific interfaces

import { TemplateDefinition, TemplateApplication, TemplateComponent } from './component';

// =====================================================
// TEMPLATE MANAGEMENT ENUMS
// =====================================================

export enum HierarchyLevel {
  GLOBAL = "global",
  PROJECT = "project", 
  MILESTONE = "milestone",
  PHASE = "phase",
  TASK = "task"
}

export enum AssignmentScope {
  ALL = "all",
  SPECIFIC_TYPES = "specific_types",
  CONDITIONAL = "conditional"
}

export enum TemplateOperationType {
  CREATE = "create",
  EDIT = "edit",
  COPY = "copy",
  DELETE = "delete",
  ACTIVATE = "activate",
  DEACTIVATE = "deactivate"
}

// =====================================================
// TEMPLATE ASSIGNMENT INTERFACES
// =====================================================

export interface TemplateAssignment {
  id: string;
  entity_id?: string;
  template_name: string;
  hierarchy_level: HierarchyLevel;
  assignment_scope: AssignmentScope;
  priority: number;
  inheritance_enabled: boolean;
  entity_type?: string;
  conditional_logic?: Record<string, any>;
  metadata?: Record<string, any>;
  effective_from?: string; // ISO date string
  effective_until?: string; // ISO date string
  is_active: boolean;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
}

export interface TemplateResolution {
  template_name: string;
  hierarchy_level: HierarchyLevel;
  assignment_id?: string;
  priority: number;
  resolution_path: ResolutionStep[];
  cached: boolean;
  cache_hit: boolean;
}

export interface ResolutionStep {
  level: string;
  assignment_id?: string;
  template_name: string;
  priority: number;
  source?: string;
}

// =====================================================
// TEMPLATE MANAGEMENT UI INTERFACES
// =====================================================

export interface TemplateManagementState {
  // Current view state
  activeTab: 'templates' | 'components' | 'assignments' | 'analytics';
  selectedTemplate?: TemplateDefinition;
  selectedComponent?: TemplateComponent;
  selectedAssignment?: TemplateAssignment;
  
  // Loading states
  isLoading: boolean;
  isSaving: boolean;
  isDeleting: boolean;
  
  // Data
  templates: TemplateDefinition[];
  components: TemplateComponent[];
  assignments: TemplateAssignment[];
  
  // UI state
  showTemplateEditor: boolean;
  showComponentEditor: boolean;
  showAssignmentEditor: boolean;
  showDeleteConfirmation: boolean;
  
  // Filters and search
  templateFilter: string;
  componentFilter: string;
  assignmentFilter: string;
  searchQuery: string;
}

export interface TemplateEditorState {
  // Template being edited
  template: Partial<TemplateDefinition>;
  originalTemplate?: TemplateDefinition;
  
  // Editor state
  mode: TemplateOperationType;
  isDirty: boolean;
  isValid: boolean;
  validationErrors: string[];
  
  // Content editing
  templateContent: string;
  selectedComponents: string[];
  componentOrder: string[];
  
  // Preview and testing
  showPreview: boolean;
  previewContent: string;
  testTaskDescription: string;
  testResults?: TemplateTestResult;
}

export interface ComponentEditorState {
  // Component being edited
  component: Partial<TemplateComponent>;
  originalComponent?: TemplateComponent;
  
  // Editor state
  mode: 'create' | 'edit';
  isDirty: boolean;
  isValid: boolean;
  validationErrors: string[];
  
  // Content editing
  instructionText: string;
  requiredTools: string[];
  estimatedDuration: number;
  
  // Testing
  showTesting: boolean;
  testResults?: ComponentTestResult;
}

export interface AssignmentEditorState {
  // Assignment being edited
  assignment: Partial<TemplateAssignment>;
  originalAssignment?: TemplateAssignment;
  
  // Editor state
  mode: 'create' | 'edit';
  isDirty: boolean;
  isValid: boolean;
  validationErrors: string[];
  
  // Assignment configuration
  selectedEntities: string[];
  conditionalRules: ConditionalRule[];
  
  // Preview
  showPreview: boolean;
  previewResolution?: TemplateResolution;
}

// =====================================================
// TESTING AND VALIDATION INTERFACES
// =====================================================

export interface TemplateTestResult {
  success: boolean;
  expanded_content: string;
  expansion_time_ms: number;
  component_count: number;
  validation_errors: string[];
  performance_score: number;
  quality_score: number;
}

export interface ComponentTestResult {
  success: boolean;
  instruction_quality: number;
  tool_availability: ToolAvailabilityResult[];
  estimated_accuracy: number;
  validation_errors: string[];
}

export interface ToolAvailabilityResult {
  tool_name: string;
  available: boolean;
  version?: string;
  issues?: string[];
}

// =====================================================
// ASSIGNMENT AND HIERARCHY INTERFACES
// =====================================================

export interface ConditionalRule {
  id: string;
  condition: string;
  operator: 'equals' | 'contains' | 'matches' | 'greater_than' | 'less_than';
  value: string;
  template_name: string;
  priority: number;
}

export interface HierarchyNode {
  id: string;
  name: string;
  type: HierarchyLevel;
  parent_id?: string;
  children: HierarchyNode[];
  assigned_template?: string;
  inherited_template?: string;
  assignment_priority?: number;
  has_conflicts: boolean;
}

export interface AssignmentConflict {
  entity_id: string;
  entity_name: string;
  hierarchy_level: HierarchyLevel;
  conflicting_assignments: TemplateAssignment[];
  recommended_resolution: 'use_highest_priority' | 'manual_review' | 'merge_assignments';
  impact_assessment: string;
}

// =====================================================
// ANALYTICS AND REPORTING INTERFACES
// =====================================================

export interface TemplateUsageAnalytics {
  template_name: string;
  usage_count: number;
  success_rate: number;
  average_expansion_time: number;
  agent_satisfaction_score: number;
  most_used_components: string[];
  performance_trend: PerformanceDataPoint[];
  usage_by_project: ProjectUsageData[];
}

export interface PerformanceDataPoint {
  timestamp: string;
  expansion_time_ms: number;
  success_rate: number;
  usage_count: number;
}

export interface ProjectUsageData {
  project_id: string;
  project_name: string;
  usage_count: number;
  success_rate: number;
  last_used: string;
}

export interface ComponentUsageAnalytics {
  component_name: string;
  usage_count: number;
  templates_using: string[];
  average_effectiveness: number;
  user_feedback_score: number;
  optimization_suggestions: string[];
}

// =====================================================
// API REQUEST/RESPONSE INTERFACES
// =====================================================

export interface CreateTemplateAssignmentRequest {
  template_name: string;
  hierarchy_level: HierarchyLevel;
  entity_id?: string;
  assignment_scope?: AssignmentScope;
  priority?: number;
  entity_type?: string;
  conditional_logic?: Record<string, any>;
  metadata?: Record<string, any>;
  effective_from?: string;
  effective_until?: string;
}

export interface UpdateTemplateAssignmentRequest {
  template_name?: string;
  priority?: number;
  assignment_scope?: AssignmentScope;
  entity_type?: string;
  conditional_logic?: Record<string, any>;
  metadata?: Record<string, any>;
  effective_from?: string;
  effective_until?: string;
  is_active?: boolean;
}

export interface BulkAssignmentRequest {
  assignments: CreateTemplateAssignmentRequest[];
  created_by?: string;
}

export interface TemplateResolutionRequest {
  entity_id: string;
  entity_type: string;
  project_id?: string;
  milestone_id?: string;
  phase_id?: string;
  context_data?: Record<string, any>;
  show_resolution_path?: boolean;
}

// =====================================================
// UI COMPONENT PROPS INTERFACES
// =====================================================

export interface TemplateManagementProps {
  projectId: string;
  className?: string;
  onTemplateSelect?: (template: TemplateDefinition) => void;
  onComponentSelect?: (component: TemplateComponent) => void;
  onAssignmentSelect?: (assignment: TemplateAssignment) => void;
}

export interface TemplateEditorProps {
  template?: TemplateDefinition;
  mode: TemplateOperationType;
  isOpen: boolean;
  onClose: () => void;
  onSave: (template: TemplateDefinition) => void;
  onTest?: (template: TemplateDefinition, testTask: string) => Promise<TemplateTestResult>;
  className?: string;
}

export interface ComponentLibraryProps {
  projectId?: string;
  selectedComponents?: string[];
  onComponentSelect?: (component: TemplateComponent) => void;
  onComponentEdit?: (component: TemplateComponent) => void;
  onComponentCreate?: () => void;
  showUsageStats?: boolean;
  className?: string;
}

export interface AssignmentManagerProps {
  projectId: string;
  hierarchyData: HierarchyNode[];
  assignments: TemplateAssignment[];
  onAssignmentCreate?: (assignment: CreateTemplateAssignmentRequest) => void;
  onAssignmentUpdate?: (id: string, updates: UpdateTemplateAssignmentRequest) => void;
  onAssignmentDelete?: (id: string) => void;
  onConflictResolve?: (conflict: AssignmentConflict) => void;
  className?: string;
}

// =====================================================
// ERROR HANDLING INTERFACES
// =====================================================

export interface TemplateManagementError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface ValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}
