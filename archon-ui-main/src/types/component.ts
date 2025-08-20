// TypeScript interfaces for Component and Template Management system
// Based on Python models in python/src/server/models/component_models.py and template_models.py

// =====================================================
// COMPONENT ENUMS - Match Python enum definitions exactly
// =====================================================

export enum ComponentType {
  FOUNDATION = "foundation",
  FEATURE = "feature", 
  INTEGRATION = "integration",
  INFRASTRUCTURE = "infrastructure",
  TESTING = "testing"
}

export enum ComponentStatus {
  NOT_STARTED = "not_started",
  IN_PROGRESS = "in_progress",
  GATES_PASSED = "gates_passed",
  COMPLETED = "completed",
  BLOCKED = "blocked"
}

export enum DependencyType {
  HARD = "hard",        // Must be completed before this component can start
  SOFT = "soft",        // Should be completed but not strictly required
  OPTIONAL = "optional" // Nice to have but not required
}

// =====================================================
// TEMPLATE ENUMS - Match Python enum definitions exactly
// =====================================================

export enum TemplateType {
  GLOBAL_DEFAULT = "global_default",
  INDUSTRY = "industry",
  TEAM = "team", 
  PERSONAL = "personal",
  COMMUNITY = "community"
}

export enum TemplateStatus {
  DRAFT = "draft",
  ACTIVE = "active",
  DEPRECATED = "deprecated",
  ARCHIVED = "archived"
}

// =====================================================
// COMPONENT INTERFACES - Match Python models exactly
// =====================================================

export interface Component {
  // Basic Information
  id?: string; // UUID - optional for creation
  project_id: string; // UUID - required
  name: string; // min_length=1, max_length=255
  description: string; // default=""
  
  // Classification
  component_type: ComponentType; // default=ComponentType.FEATURE
  status: ComponentStatus; // default=ComponentStatus.NOT_STARTED
  
  // Dependencies and Gates
  dependencies: string[]; // List of component UUIDs - default=[]
  completion_gates: string[]; // Gates that must be passed - default=[]
  
  // Context and Ordering
  context_data: Record<string, any>; // JSONB field - default={}
  order_index: number; // Display order - default=0
  
  // Timestamps
  created_at?: string; // ISO datetime string - optional
  updated_at?: string; // ISO datetime string - optional
}

export interface ComponentDependency {
  // Basic Information
  id?: string; // UUID - optional for creation
  component_id: string; // UUID - required
  depends_on_component_id: string; // UUID - required
  
  // Dependency Configuration
  dependency_type: DependencyType; // default=DependencyType.HARD
  gate_requirements: string[]; // Specific gates required - default=[]
  
  // Timestamps
  created_at?: string; // ISO datetime string - optional
}

// =====================================================
// TEMPLATE INTERFACES - Match Python models exactly
// =====================================================

export interface TemplateDefinition {
  // Basic Information
  id?: string; // UUID - optional for creation
  name: string; // min_length=1, max_length=255
  title: string; // min_length=1, max_length=500
  description: string; // default=""
  
  // Classification
  template_type: TemplateType; // default=TemplateType.PERSONAL
  status: TemplateStatus; // default=TemplateStatus.DRAFT
  
  // Inheritance
  parent_template_id?: string; // UUID - optional
  inheritance_rules: Record<string, any>; // JSONB field - default={}
  
  // Template Content
  workflow_assignments: Record<string, any>; // JSONB field - default={}
  component_templates: Record<string, any>; // JSONB field - default={}
  
  // Configuration
  is_active: boolean; // default=true
  is_public: boolean; // default=false
  
  // Metadata
  created_by: string; // default="system"
  usage_count: number; // default=0
  
  // Timestamps
  created_at?: string; // ISO datetime string - optional
  updated_at?: string; // ISO datetime string - optional
}

export interface TemplateApplication {
  // Basic Information
  id?: string; // UUID - optional for creation
  project_id: string; // UUID - required
  template_id: string; // UUID - required
  
  // Application Details
  applied_at?: string; // ISO datetime string - optional
  applied_by: string; // default="system"
  customizations: Record<string, any>; // JSONB field - default={}
}

// =====================================================
// REQUEST/RESPONSE MODELS FOR API - Match Python models exactly
// =====================================================

export interface CreateComponentRequest {
  project_id: string; // UUID
  name: string; // min_length=1, max_length=255
  description?: string; // default=""
  component_type?: ComponentType; // default=ComponentType.FEATURE
  dependencies?: string[]; // default=[]
  completion_gates?: string[]; // default=[]
  context_data?: Record<string, any>; // default={}
  order_index?: number; // default=0
}

export interface UpdateComponentRequest {
  name?: string; // min_length=1, max_length=255
  description?: string;
  component_type?: ComponentType;
  status?: ComponentStatus;
  dependencies?: string[];
  completion_gates?: string[];
  context_data?: Record<string, any>;
  order_index?: number;
}

export interface CreateComponentDependencyRequest {
  component_id: string; // UUID
  depends_on_component_id: string; // UUID
  dependency_type?: DependencyType; // default=DependencyType.HARD
  gate_requirements?: string[]; // default=[]
}

export interface ComponentResponse {
  success: boolean;
  component?: Component;
  message: string;
  error?: string;
}

export interface ComponentDependencyResponse {
  success: boolean;
  dependency?: ComponentDependency;
  message: string;
  error?: string;
}

export interface CreateTemplateDefinitionRequest {
  name: string; // min_length=1, max_length=255
  title: string; // min_length=1, max_length=500
  description?: string; // default=""
  template_type?: TemplateType; // default=TemplateType.PERSONAL
  parent_template_id?: string; // UUID - optional
  workflow_assignments?: Record<string, any>; // default={}
  component_templates?: Record<string, any>; // default={}
  inheritance_rules?: Record<string, any>; // default={}
  is_public?: boolean; // default=false
}

export interface UpdateTemplateDefinitionRequest {
  name?: string; // min_length=1, max_length=255
  title?: string; // min_length=1, max_length=500
  description?: string;
  template_type?: TemplateType;
  status?: TemplateStatus;
  parent_template_id?: string; // UUID - optional
  workflow_assignments?: Record<string, any>;
  component_templates?: Record<string, any>;
  inheritance_rules?: Record<string, any>;
  is_active?: boolean;
  is_public?: boolean;
}

export interface ApplyTemplateRequest {
  project_id: string; // UUID
  template_id: string; // UUID
  customizations?: Record<string, any>; // default={}
  applied_by?: string; // default="system"
}

export interface TemplateDefinitionResponse {
  success: boolean;
  template?: TemplateDefinition;
  message: string;
  error?: string;
}

export interface TemplateApplicationResponse {
  success: boolean;
  application?: TemplateApplication;
  message: string;
  error?: string;
}

// =====================================================
// UTILITY TYPES FOR FRONTEND USE
// =====================================================

// Valid completion gates (matches Python validation)
export const VALID_COMPLETION_GATES = [
  "architecture",
  "design", 
  "implementation",
  "testing",
  "integration",
  "documentation",
  "review",
  "deployment"
] as const;

export type CompletionGate = typeof VALID_COMPLETION_GATES[number];

// Component hierarchy validation result
export interface ComponentHierarchyValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

// Template inheritance chain
export interface TemplateInheritanceChain {
  templates: TemplateDefinition[];
  resolved_config: {
    workflow_assignments: Record<string, any>;
    component_templates: Record<string, any>;
    inheritance_rules: Record<string, any>;
  };
  conflicts: string[];
}

// Component execution order result
export interface ComponentExecutionOrder {
  components: Component[];
  cycles: string[];
}
