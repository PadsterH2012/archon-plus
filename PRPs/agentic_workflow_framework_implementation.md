name: "Agentic Workflow Framework with Dynamic Plan Adaptation - Phase 1 Implementation"
description: |

---

## Goal

**Feature Goal**: Implement component-based project hierarchy with dependency gates and template inheritance system to enable flexible project organization and reusable workflow patterns in Archon.

**Deliverable**: Complete component management system with database schema, API endpoints, UI components, and template application engine that supports hierarchical project organization and dynamic plan adaptation.

**Success Definition**: Users can create projects with multiple components (foundation, features), define dependencies between components with completion gates, apply templates to components, and have agents receive dynamically compiled context based on component hierarchy and current codebase state.

## User Persona

**Target User**: Development teams and project managers using Archon for complex multi-component software projects

**Use Case**: Setting up a new project with authentication foundation, multiple feature components, and integration components where features depend on foundation completion but can be developed in parallel once foundation gates pass.

**User Journey**: 
1. Create new project and select base template
2. Define project components (foundation, feature-a, feature-b, integration)
3. Set component dependencies and completion gates
4. Apply component-specific templates with customizations
5. Agents receive tasks with rich context from component hierarchy
6. System adapts plans dynamically based on actual codebase state

**Pain Points Addressed**: 
- Eliminates rigid linear project structures that block parallel development
- Reduces manual task creation through intelligent template application
- Prevents agent confusion from incomplete or conflicting context
- Enables organizational learning through reusable component templates

## Why

- **Scalable Project Organization**: Support complex projects with multiple parallel workstreams while maintaining clear dependencies
- **Intelligent Template System**: Capture and reuse successful project patterns across teams and organizations
- **Dynamic Context Compilation**: Provide agents with accurate, current context that adapts to actual codebase state rather than static assumptions
- **Enhanced Agent Effectiveness**: Reduce manual task definition overhead while improving agent instruction quality through hierarchical context aggregation

## What

Component-based project hierarchy system that extends Archon's existing project/task structure with:

### Core Components
- **Component Management**: Create, organize, and manage project components with types (foundation, feature, integration)
- **Dependency System**: Define and validate component dependencies with completion gates
- **Template Engine**: Apply and inherit templates at component and project levels
- **Dynamic Context Compilation**: Aggregate context from component hierarchy for agent instruction generation
- **Codebase State Assessment**: Analyze current implementation state to adapt plans dynamically

### Success Criteria

- [ ] Component CRUD operations functional with proper validation
- [ ] Dependency graph validation prevents circular dependencies
- [ ] Template inheritance system supports 3 levels of inheritance
- [ ] Context compilation performance <100ms for typical projects
- [ ] Dynamic plan adaptation completes within 2 seconds
- [ ] All existing projects migrate successfully to component structure
- [ ] Agent task assignment works with component-scoped context
- [ ] Template marketplace foundation supports community templates

## All Needed Context

### Context Completeness Check

_This PRP provides complete context for implementing a component-based hierarchy system that builds on Archon's existing project/task architecture, workflow system, and MCP tool integration._

### Documentation & References

```yaml
# MUST READ - Include these in your context window
- file: migration/complete_setup.sql
  why: Current database schema for projects, tasks, and workflow system
  pattern: Table structure, relationships, and indexing patterns
  gotcha: JSONB fields used extensively, UUID primary keys, soft delete patterns

- file: python/src/mcp/modules/project_module.py
  why: Existing project and task management MCP tools and patterns
  pattern: Tool structure, parameter validation, response formatting
  critical: Task lifecycle management (todo→doing→review→done) must be preserved

- file: migration/add_workflow_system.sql
  why: Workflow template system architecture and patterns
  pattern: Template versioning, step execution, parameter schemas
  gotcha: JSONB configuration storage, enum types for status tracking

- file: python/src/server/models/workflow_models.py
  why: Pydantic models for workflow system - pattern for new component models
  pattern: BaseModel inheritance, field validation, enum definitions
  critical: UUID field handling, optional fields with defaults

- file: archon-ui-main/src/types/project.ts
  why: Frontend TypeScript interfaces for projects and tasks
  pattern: Interface definitions, JSONB field typing, status enums
  gotcha: Database schema must match TypeScript interfaces exactly

- file: python/src/server/services/threading_service.py
  why: Performance patterns for concurrent operations and caching
  pattern: Adaptive concurrency, rate limiting, memory management
  critical: Context compilation must use similar performance patterns
```

### Current Codebase tree (relevant sections)

```bash
archon-plus/
├── migration/
│   ├── complete_setup.sql              # Core database schema
│   └── add_workflow_system.sql         # Workflow system tables
├── python/src/
│   ├── mcp/modules/
│   │   └── project_module.py           # Project/task MCP tools
│   ├── server/
│   │   ├── models/
│   │   │   └── workflow_models.py      # Pydantic models
│   │   └── services/
│   │       ├── client_manager.py       # Database connections
│   │       └── threading_service.py    # Performance utilities
│   └── tools/                          # MCP tool implementations
├── archon-ui-main/src/
│   ├── types/
│   │   └── project.ts                  # TypeScript interfaces
│   ├── services/
│   │   └── projectService.ts           # API client patterns
│   └── components/
│       └── projects/                   # Project UI components
└── docs/
    └── workflow-database-schema.md     # Workflow system documentation
```

### Desired Codebase tree with files to be added

```bash
# Database Schema Extensions
migration/
└── add_component_hierarchy.sql         # Component tables, dependencies, templates

# Backend Models and Services  
python/src/server/
├── models/
│   ├── component_models.py             # Component, dependency, template models
│   └── template_models.py              # Template inheritance and application models
├── services/
│   ├── component_service.py            # Component CRUD and dependency validation
│   ├── template_service.py             # Template inheritance and application
│   └── context_compilation_service.py  # Dynamic context aggregation
└── tools/
    ├── component_management.py         # MCP tools for component operations
    └── template_management.py          # MCP tools for template operations

# Frontend Extensions
archon-ui-main/src/
├── types/
│   ├── component.ts                    # Component and dependency interfaces
│   └── template.ts                     # Template system interfaces
├── services/
│   ├── componentService.ts             # Component API client
│   └── templateService.ts              # Template API client
└── components/
    ├── components/                     # Component management UI
    │   ├── ComponentHierarchy.tsx      # Visual component tree
    │   ├── DependencyGraph.tsx         # Dependency visualization
    │   └── ComponentForm.tsx           # Component creation/editing
    └── templates/
        ├── TemplateSelector.tsx        # Template selection and preview
        └── TemplateCustomizer.tsx      # Template customization interface
```

### Known Gotchas of our codebase & Library Quirks

```python
# CRITICAL: Archon uses UUID primary keys everywhere - maintain consistency
# Example: All new tables must use UUID DEFAULT gen_random_uuid()

# CRITICAL: JSONB fields used extensively for flexible data storage
# Example: Component context, template configurations stored as JSONB

# CRITICAL: Supabase/PostgreSQL specific features used
# Example: Row Level Security (RLS), pgvector for embeddings

# CRITICAL: MCP tools must return JSON strings, not objects
# Example: return json.dumps({"success": True, "data": result})

# CRITICAL: Async/await patterns required throughout
# Example: All database operations and service methods must be async

# CRITICAL: Existing task lifecycle (todo→doing→review→done) must be preserved
# Example: Component status should complement, not replace task status

# CRITICAL: Performance considerations for context compilation
# Example: Use caching, avoid N+1 queries, implement pagination
```

## Implementation Blueprint

### Data models and structure

Create the core data models to ensure type safety and consistency across component hierarchy, dependency management, and template system.

```python
# Component Models (python/src/server/models/component_models.py)
class ComponentType(str, Enum):
    FOUNDATION = "foundation"
    FEATURE = "feature"
    INTEGRATION = "integration"
    INFRASTRUCTURE = "infrastructure"
    TESTING = "testing"

class ComponentStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    GATES_PASSED = "gates_passed"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class Component(BaseModel):
    id: Optional[UUID] = None
    project_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    component_type: ComponentType = ComponentType.FEATURE
    status: ComponentStatus = ComponentStatus.NOT_STARTED
    dependencies: List[UUID] = Field(default_factory=list)
    completion_gates: List[str] = Field(default_factory=list)
    context_data: Dict[str, Any] = Field(default_factory=dict)
    order_index: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ComponentDependency(BaseModel):
    id: Optional[UUID] = None
    component_id: UUID
    depends_on_component_id: UUID
    dependency_type: str = "hard"  # hard, soft, optional
    gate_requirements: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None

# Template Models (python/src/server/models/template_models.py)
class TemplateType(str, Enum):
    GLOBAL_DEFAULT = "global_default"
    INDUSTRY = "industry"
    TEAM = "team"
    PERSONAL = "personal"
    COMMUNITY = "community"

class TemplateDefinition(BaseModel):
    id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    template_type: TemplateType = TemplateType.PERSONAL
    parent_template_id: Optional[UUID] = None
    workflow_assignments: Dict[str, Any] = Field(default_factory=dict)
    inheritance_rules: Dict[str, Any] = Field(default_factory=dict)
    component_templates: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    is_public: bool = False
    created_by: str = "system"
    usage_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### Implementation Tasks (ordered by dependencies)

```yaml
Task 1: CREATE migration/add_component_hierarchy.sql
  - IMPLEMENT: Component tables, dependency tables, template tables with proper constraints
  - FOLLOW pattern: migration/add_workflow_system.sql (enum types, UUID keys, JSONB fields)
  - NAMING: archon_components, archon_component_dependencies, archon_template_definitions
  - CONSTRAINTS: Unique component names per project, no circular dependencies, valid enum values
  - PLACEMENT: Database migration in migration/ directory

Task 2: CREATE python/src/server/models/component_models.py
  - IMPLEMENT: Component, ComponentDependency Pydantic models with validation
  - FOLLOW pattern: python/src/server/models/workflow_models.py (BaseModel inheritance, field validation)
  - NAMING: CamelCase for classes, snake_case for fields, descriptive enum values
  - VALIDATION: Component name uniqueness, dependency cycle prevention, gate format validation
  - PLACEMENT: Server models in python/src/server/models/

Task 3: CREATE python/src/server/models/template_models.py
  - IMPLEMENT: TemplateDefinition, TemplateApplication Pydantic models
  - FOLLOW pattern: python/src/server/models/workflow_models.py (optional fields, JSONB handling)
  - NAMING: Template-prefixed classes, clear inheritance relationship fields
  - DEPENDENCIES: Import UUID, datetime, Enum from component_models
  - PLACEMENT: Server models in python/src/server/models/

Task 4: CREATE python/src/server/services/component_service.py
  - IMPLEMENT: ComponentService class with CRUD operations and dependency validation
  - FOLLOW pattern: python/src/server/services/client_manager.py (async methods, error handling)
  - NAMING: ComponentService class, async def create_component, get_*, update_*, delete_* methods
  - DEPENDENCIES: Import models from Tasks 2-3, use Supabase client pattern
  - VALIDATION: Circular dependency detection, gate requirement validation
  - PLACEMENT: Service layer in python/src/server/services/

Task 5: CREATE python/src/server/services/template_service.py
  - IMPLEMENT: TemplateService class with inheritance resolution and application logic
  - FOLLOW pattern: python/src/server/services/component_service.py (service structure)
  - NAMING: TemplateService class, resolve_inheritance, apply_template methods
  - DEPENDENCIES: Import template models, component service for application
  - LOGIC: Template inheritance chain resolution, conflict detection, customization merging
  - PLACEMENT: Service layer in python/src/server/services/

Task 6: CREATE python/src/server/services/context_compilation_service.py
  - IMPLEMENT: ContextCompilationService for hierarchical context aggregation
  - FOLLOW pattern: python/src/server/services/threading_service.py (performance optimization)
  - NAMING: ContextCompilationService, compile_component_context, aggregate_project_context
  - DEPENDENCIES: Component service, template service, existing RAG capabilities
  - PERFORMANCE: Implement caching, avoid N+1 queries, use async patterns
  - PLACEMENT: Service layer in python/src/server/services/

Task 7: CREATE python/src/tools/component_management.py
  - IMPLEMENT: MCP tools for component CRUD operations
  - FOLLOW pattern: python/src/mcp/modules/project_module.py (MCP tool structure, JSON responses)
  - NAMING: manage_component tool with action parameter (create, list, get, update, delete)
  - DEPENDENCIES: Import ComponentService from Task 4
  - VALIDATION: Input parameter validation, proper error handling and responses
  - PLACEMENT: MCP tools in python/src/tools/

Task 8: CREATE python/src/tools/template_management.py
  - IMPLEMENT: MCP tools for template operations and application
  - FOLLOW pattern: python/src/tools/component_management.py (consistent tool structure)
  - NAMING: manage_template, apply_template tools with descriptive parameters
  - DEPENDENCIES: Import TemplateService from Task 5
  - FUNCTIONALITY: Template CRUD, inheritance resolution, application to components
  - PLACEMENT: MCP tools in python/src/tools/

Task 9: MODIFY python/src/mcp/modules/project_module.py
  - INTEGRATE: Extend existing project management tools with component awareness
  - FIND pattern: Existing manage_project, manage_task tool registrations
  - ADD: Component context to task creation, project component listing
  - PRESERVE: Existing project and task functionality, backward compatibility
  - ENHANCE: Task assignment with component-scoped context compilation

Task 10: CREATE archon-ui-main/src/types/component.ts
  - IMPLEMENT: TypeScript interfaces matching Python models exactly
  - FOLLOW pattern: archon-ui-main/src/types/project.ts (interface structure, enum definitions)
  - NAMING: Component, ComponentDependency, ComponentType, ComponentStatus interfaces
  - CONSISTENCY: Field names and types must match Python models exactly
  - PLACEMENT: Frontend types in archon-ui-main/src/types/

Task 11: CREATE archon-ui-main/src/types/template.ts
  - IMPLEMENT: TypeScript interfaces for template system
  - FOLLOW pattern: archon-ui-main/src/types/component.ts (consistent interface patterns)
  - NAMING: TemplateDefinition, TemplateApplication, TemplateType interfaces
  - DEPENDENCIES: Import Component types for template application
  - PLACEMENT: Frontend types in archon-ui-main/src/types/

Task 12: CREATE archon-ui-main/src/services/componentService.ts
  - IMPLEMENT: API client for component operations
  - FOLLOW pattern: archon-ui-main/src/services/projectService.ts (API client structure, error handling)
  - NAMING: ComponentService class with CRUD methods matching backend
  - DEPENDENCIES: Import component types from Task 10
  - ERROR_HANDLING: Consistent error response handling, loading states
  - PLACEMENT: Frontend services in archon-ui-main/src/services/
```

### Implementation Patterns & Key Details

```python
# Component Service Pattern (python/src/server/services/component_service.py)
class ComponentService:
    def __init__(self):
        self.supabase = get_supabase_client()
        self._dependency_cache = {}  # Cache for dependency graphs

    async def create_component(self, component: Component) -> Component:
        # PATTERN: Validate dependencies before creation
        await self._validate_dependencies(component.project_id, component.dependencies)

        # GOTCHA: Must check for circular dependencies in entire project
        if await self._creates_circular_dependency(component):
            raise ValueError("Component would create circular dependency")

        # PATTERN: Use JSONB for flexible context storage
        result = await self.supabase.table("archon_components").insert({
            "project_id": str(component.project_id),
            "name": component.name,
            "component_type": component.component_type.value,
            "context_data": component.context_data,
            "dependencies": [str(dep) for dep in component.dependencies]
        }).execute()

        return Component(**result.data[0])

# Context Compilation Pattern (python/src/server/services/context_compilation_service.py)
async def compile_component_context(self, component_id: UUID) -> Dict[str, Any]:
    # PATTERN: Multi-level context aggregation with caching
    cache_key = f"component_context:{component_id}"
    if cached := await self._get_cached_context(cache_key):
        return cached

    # CRITICAL: Aggregate context from component → project hierarchy
    component_context = await self._get_component_context(component_id)
    dependency_context = await self._get_dependency_context(component_id)
    template_context = await self._get_template_context(component_id)
    project_context = await self._get_project_context(component.project_id)

    # PATTERN: Merge contexts with proper precedence (component > template > project)
    compiled_context = self._merge_contexts([
        project_context, template_context, dependency_context, component_context
    ])

    # PERFORMANCE: Cache compiled context for 15 minutes
    await self._cache_context(cache_key, compiled_context, ttl=900)
    return compiled_context

# MCP Tool Pattern (python/src/tools/component_management.py)
@app.tool()
async def manage_component(
    action: str,
    project_id: Optional[str] = None,
    component_id: Optional[str] = None,
    name: Optional[str] = None,
    component_type: Optional[str] = None,
    dependencies: Optional[List[str]] = None
) -> str:
    # PATTERN: Action-based tool with comprehensive parameter validation
    service = ComponentService()

    try:
        if action == "create":
            # VALIDATION: Required parameters for creation
            if not all([project_id, name, component_type]):
                return json.dumps({"success": False, "error": "Missing required parameters"})

            component = Component(
                project_id=UUID(project_id),
                name=name,
                component_type=ComponentType(component_type),
                dependencies=[UUID(dep) for dep in (dependencies or [])]
            )
            result = await service.create_component(component)
            return json.dumps({"success": True, "component": result.dict()})

        elif action == "list":
            # PATTERN: List with optional filtering
            components = await service.list_components(
                project_id=UUID(project_id) if project_id else None
            )
            return json.dumps({"success": True, "components": [c.dict() for c in components]})

        # ... other actions

    except Exception as e:
        # CRITICAL: Proper error handling with informative messages
        return json.dumps({"success": False, "error": str(e)})
```

### Integration Points

```yaml
DATABASE:
  - migration: "Run migration/add_component_hierarchy.sql to add component tables"
  - indexes: "CREATE INDEX idx_components_project_id ON archon_components(project_id)"
  - constraints: "Add foreign key constraints and circular dependency prevention"

EXISTING_SYSTEMS:
  - extend: python/src/mcp/modules/project_module.py
  - pattern: "Add component_id parameter to task creation tools"
  - preserve: "Maintain all existing project and task functionality"

MCP_REGISTRATION:
  - add to: python/src/main.py or appropriate MCP server registration
  - pattern: "Register component_management and template_management tools"
  - follow: "Existing tool registration patterns in codebase"

FRONTEND_INTEGRATION:
  - extend: archon-ui-main/src/components/projects/
  - pattern: "Add component management to existing project views"
  - consistency: "Follow existing UI patterns and design system"

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)

```bash
# Run after each file creation - fix before proceeding
ruff check python/src/server/models/ --fix
ruff check python/src/server/services/ --fix
ruff check python/src/tools/ --fix
mypy python/src/server/models/
mypy python/src/server/services/
mypy python/src/tools/
ruff format python/src/

# Database migration validation
psql $DATABASE_URL -f migration/add_component_hierarchy.sql --dry-run

# TypeScript validation
cd archon-ui-main && npm run type-check
cd archon-ui-main && npm run lint

# Expected: Zero errors. If errors exist, READ output and fix before proceeding.
```

### Level 2: Unit Tests (Component Validation)

```bash
# Test each service as it's created
uv run pytest python/src/server/services/tests/test_component_service.py -v
uv run pytest python/src/server/services/tests/test_template_service.py -v
uv run pytest python/src/server/services/tests/test_context_compilation_service.py -v

# Test MCP tools
uv run pytest python/src/tools/tests/test_component_management.py -v
uv run pytest python/src/tools/tests/test_template_management.py -v

# Full test suite for affected areas
uv run pytest python/src/server/ -v
uv run pytest python/src/tools/ -v

# Frontend tests
cd archon-ui-main && npm test -- --testPathPattern=component
cd archon-ui-main && npm test -- --testPathPattern=template

# Expected: All tests pass. If failing, debug root cause and fix implementation.
```

### Level 3: Integration Testing (System Validation)

```bash
# Database migration and validation
psql $DATABASE_URL -f migration/add_component_hierarchy.sql
psql $DATABASE_URL -c "SELECT COUNT(*) FROM archon_components;" # Should work without error

# Service startup validation
cd python && uv run python -m src.main &
sleep 5  # Allow startup time

# Health check validation
curl -f http://localhost:8181/health || echo "Service health check failed"

# Component management MCP tool testing
echo '{"method": "tools/call", "params": {"name": "manage_component", "arguments": {"action": "list"}}}' | \
  uv run python -m src.mcp_server

# Template system testing
echo '{"method": "tools/call", "params": {"name": "manage_template", "arguments": {"action": "list"}}}' | \
  uv run python -m src.mcp_server

# Frontend integration testing
cd archon-ui-main && npm start &
sleep 10
curl -f http://localhost:3737 || echo "Frontend startup failed"

# Test component creation through UI
# Manual: Navigate to project page, create component, verify in database

# Expected: All integrations working, proper responses, no connection errors
```

### Level 4: Creative & Domain-Specific Validation

```bash
# Component Hierarchy Validation
# Create test project with foundation and feature components
curl -X POST http://localhost:8181/api/components \
  -H "Content-Type: application/json" \
  -d '{"project_id": "test-uuid", "name": "foundation", "component_type": "foundation"}' \
  | jq .

# Test dependency validation (should prevent circular dependencies)
curl -X POST http://localhost:8181/api/components \
  -H "Content-Type: application/json" \
  -d '{"project_id": "test-uuid", "name": "feature-a", "component_type": "feature", "dependencies": ["foundation-uuid"]}' \
  | jq .

# Template Inheritance Testing
# Apply template to component and verify inheritance chain resolution
curl -X POST http://localhost:8181/api/templates/apply \
  -H "Content-Type: application/json" \
  -d '{"component_id": "component-uuid", "template_id": "template-uuid", "customizations": {}}' \
  | jq .

# Context Compilation Performance Testing
# Measure context compilation time for complex component hierarchy
time curl -X GET "http://localhost:8181/api/components/context/compile?component_id=test-uuid"

# Dynamic Plan Adaptation Testing (if implemented)
# Test codebase state assessment and plan adaptation
curl -X POST http://localhost:8181/api/components/adapt-plan \
  -H "Content-Type: application/json" \
  -d '{"component_id": "test-uuid", "trigger": "codebase_change"}' \
  | jq .

# Load Testing for Context Compilation
ab -n 100 -c 10 http://localhost:8181/api/components/context/compile?component_id=test-uuid

# Database Performance Testing
# Verify no N+1 queries in component hierarchy operations
EXPLAIN ANALYZE SELECT * FROM archon_components WHERE project_id = 'test-uuid';

# Expected: All creative validations pass, performance meets <100ms target for context compilation
```

## Final Validation Checklist

### Technical Validation

- [ ] All 4 validation levels completed successfully
- [ ] All tests pass: `uv run pytest python/src/ -v`
- [ ] No linting errors: `uv run ruff check python/src/`
- [ ] No type errors: `uv run mypy python/src/`
- [ ] No formatting issues: `uv run ruff format python/src/ --check`
- [ ] Database migration runs successfully without errors
- [ ] Frontend builds and starts without TypeScript errors

### Feature Validation

- [ ] Component CRUD operations work through MCP tools
- [ ] Dependency validation prevents circular dependencies
- [ ] Template inheritance resolves correctly for 3 levels
- [ ] Context compilation completes within 100ms performance target
- [ ] All existing projects migrate to component structure successfully
- [ ] Agent task assignment receives component-scoped context
- [ ] UI components render and function correctly

### Code Quality Validation

- [ ] Follows existing Archon patterns (UUID keys, JSONB fields, async methods)
- [ ] File placement matches desired codebase tree structure
- [ ] MCP tools return proper JSON string responses
- [ ] Database schema follows Archon conventions (table naming, constraints)
- [ ] Frontend TypeScript interfaces match backend models exactly
- [ ] Performance patterns implemented (caching, query optimization)

### Documentation & Deployment

- [ ] Database migration documented with rollback procedures
- [ ] New MCP tools documented with parameter descriptions
- [ ] Frontend components follow existing design system patterns
- [ ] Environment variables documented if new ones added
- [ ] API endpoints documented for component and template operations

---

## Anti-Patterns to Avoid

- ❌ Don't create parallel hierarchies - use component-based approach only
- ❌ Don't skip dependency validation - circular dependencies will break the system
- ❌ Don't ignore performance requirements - context compilation must be <100ms
- ❌ Don't break existing project/task functionality - maintain backward compatibility
- ❌ Don't use sync functions in async context - all database operations must be async
- ❌ Don't hardcode component types - use enums for extensibility
- ❌ Don't skip caching for context compilation - performance will degrade
- ❌ Don't ignore JSONB field validation - malformed data will cause runtime errors
```
```
