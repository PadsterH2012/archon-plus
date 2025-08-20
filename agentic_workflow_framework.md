# Agentic Workflow Framework - Project Design

## Executive Summary

A hierarchical workflow orchestration system that enables agents to dynamically compile contextual instructions from modular, reusable components. The framework bridges traditional project management structures with intelligent agent execution through a composable action/workflow library.

## Core Concepts

### Hierarchical Task Structure
- **Projects** → **Milestones** → **Phases** → **Tasks** → **Subtasks**
- Each level can have attached workflows, groups, and actions
- Context flows down the hierarchy, enriching agent instructions
- Reference system: `ProjectName::MilestoneName::TaskId`

### Workflow Components
- **Actions**: Atomic operations with natural language instructions
- **Sequences**: Ordered steps of related actions (cannot contain workflows)
- **Workflows**: Orchestrated processes that can contain actions, sequences, or other workflows

### Dynamic Compilation
Agent receives a hierarchical reference and automatically builds comprehensive, contextual instructions by traversing the hierarchy and assembling applicable workflows.

---

## Template System Architecture

### Template Inheritance Hierarchy
```
Global Default Template
├── Industry Templates (Web Dev, Mobile, Research, etc.)
│   └── Team Templates (Frontend Team, Backend Team)
│       └── Project-Specific Customizations
```

### Template Categories
- **Global Default**: Applied to ALL new projects automatically
- **Industry Templates**: Specialized for project types (inherits from Global + adds specific workflows)
- **Team Templates**: Department/role-specific workflows
- **Personal Templates**: User-created custom templates
- **Community Templates**: Shared templates from other users

### Template Application Rules
1. **Inheritance**: Lower levels inherit from higher levels
2. **Override Capability**: Can add/modify workflows, add skip conditions
3. **Protection**: Cannot remove "Important" workflows (safety mechanism)
4. **Dynamic Application**: Context-aware template selection based on project parameters

---

## Database Schema Design

### Template Tables

#### template_definitions
```sql
id (UUID, primary key)
name (VARCHAR, unique)
description (TEXT)
template_type (ENUM: global_default, industry, team, personal, community)
parent_template_id (UUID, foreign key → template_definitions.id)
is_active (BOOLEAN)
is_public (BOOLEAN) -- for community sharing
created_by (UUID) -- user who created it
usage_count (INTEGER) -- popularity tracking
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### template_workflows
```sql
id (UUID, primary key)
template_id (UUID, foreign key → template_definitions.id)
workflow_type (ENUM: action, group, workflow)
workflow_id (UUID) -- polymorphic reference
hierarchy_level (ENUM: project, milestone, phase, task, subtask)
execution_trigger (ENUM: on_start, on_completion, repeating, conditional)
repeat_pattern (JSONB)
condition_logic (JSONB)
is_required (BOOLEAN) -- "Important" workflows
is_inherited (BOOLEAN) -- inherited from parent template
override_allowed (BOOLEAN)
order_index (INTEGER)
```

#### template_customizations
```sql
id (UUID, primary key)
base_template_id (UUID, foreign key → template_definitions.id)
project_id (UUID, foreign key → projects.id)
customization_data (JSONB) -- what was changed from template
applied_at (TIMESTAMP)
```

### Core Hierarchy Tables

#### projects
```sql
id (UUID, primary key)
name (VARCHAR, unique)
description (TEXT)
context_data (JSONB) -- project-wide context
template_id (UUID, foreign key → template_definitions.id)
template_applied_at (TIMESTAMP)
template_customizations (JSONB) -- deviations from template
status (ENUM: active, paused, completed, archived)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### milestones
```sql
id (UUID, primary key)
project_id (UUID, foreign key → projects.id)
name (VARCHAR)
description (TEXT)
context_data (JSONB) -- milestone-specific context
order_index (INTEGER) -- ordering within project
status (ENUM: not_started, in_progress, completed)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### phases
```sql
id (UUID, primary key)
milestone_id (UUID, foreign key → milestones.id)
name (VARCHAR)
description (TEXT)
context_data (JSONB)
order_index (INTEGER)
status (ENUM: not_started, in_progress, completed)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### tasks
```sql
id (UUID, primary key)
phase_id (UUID, foreign key → phases.id)
name (VARCHAR)
description (TEXT)
context_data (JSONB)
task_number (VARCHAR) -- e.g., "1.1", "2.3"
order_index (INTEGER)
status (ENUM: not_started, in_progress, completed, blocked)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### subtasks
```sql
id (UUID, primary key)
task_id (UUID, foreign key → tasks.id)
name (VARCHAR)
description (TEXT)
context_data (JSONB)
order_index (INTEGER)
status (ENUM: not_started, in_progress, completed)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### Workflow Component Tables

#### actions
```sql
id (UUID, primary key)
name (VARCHAR, unique) -- e.g., "git-commit", "send-email"
description (TEXT)
instruction_template (TEXT) -- natural language instructions
input_schema (JSONB) -- expected inputs
output_schema (JSONB) -- produced outputs
side_effects (JSONB) -- what this action changes
error_patterns (JSONB) -- common failure modes
is_active (BOOLEAN)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### groups
```sql
id (UUID, primary key)
name (VARCHAR, unique) -- e.g., "validation-suite"
description (TEXT)
context_template (TEXT) -- how this group fits into larger context
input_schema (JSONB)
output_schema (JSONB)
is_active (BOOLEAN)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

#### workflows
```sql
id (UUID, primary key)
name (VARCHAR, unique) -- e.g., "ci-pipeline"
description (TEXT)
context_template (TEXT)
input_schema (JSONB)
output_schema (JSONB)
execution_order (JSONB) -- defines sequence and branching
is_active (BOOLEAN)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### Association Tables

#### hierarchy_workflows
```sql
id (UUID, primary key)
hierarchy_type (ENUM: project, milestone, phase, task, subtask)
hierarchy_id (UUID) -- polymorphic reference
workflow_type (ENUM: action, group, workflow)
workflow_id (UUID) -- polymorphic reference
execution_trigger (ENUM: on_start, on_completion, repeating, conditional)
repeat_pattern (JSONB) -- for repeating workflows
condition_logic (JSONB) -- for conditional execution
order_index (INTEGER)
is_active (BOOLEAN)
```

#### group_components
```sql
id (UUID, primary key)
group_id (UUID, foreign key → groups.id)
component_type (ENUM: action, group)
component_id (UUID) -- polymorphic reference
order_index (INTEGER)
is_parallel (BOOLEAN) -- can run in parallel with others
```

#### workflow_components
```sql
id (UUID, primary key)
workflow_id (UUID, foreign key → workflows.id)
component_type (ENUM: action, group, workflow)
component_id (UUID) -- polymorphic reference
order_index (INTEGER)
is_parallel (BOOLEAN)
condition_logic (JSONB) -- conditional execution
error_handling (JSONB) -- what to do on failure
```

---

## Dynamic Compilation Algorithm

### 1. Reference Resolution
```
Input: "Website Redesign::Design Phase::1.1"

Parse hierarchy path:
- Project: "Website Redesign"
- Milestone: "Design Phase" 
- Task: "1.1"

Resolve to database IDs through cascade lookups
```

### 2. Context Aggregation
```
Traverse hierarchy upward, collecting:
- Project context_data
- Milestone context_data  
- Phase context_data
- Task context_data

Merge with inheritance (lower levels override higher)
```

### 3. Workflow Collection
```
For each hierarchy level (project → task):
  Query hierarchy_workflows WHERE hierarchy_id = level_id
  Collect all attached workflows, groups, actions
  Apply execution_trigger filters (what should run now?)
```

### 4. Instruction Compilation
```
For each collected workflow component:
  1. Resolve component definition
  2. Apply context data to instruction_template
  3. Check input/output schema compatibility
  4. Build execution graph (handle dependencies)
  5. Generate final natural language instructions
```

### 5. Agent Instruction Generation
```
Output comprehensive instruction set:
- Contextual background (why this task matters)
- Specific actions to take (step-by-step)
- Success criteria (how to know it's done)
- Error handling (what to do if things go wrong)
- Next steps (what comes after)
```

---

## Template System Implementation

### Project Creation with Templates

#### 1. Template Selection Process
```
User creates new project:
1. System presents template options:
   ├── Global Default (always available)
   ├── Industry Templates (Web Dev, Mobile, Research)
   ├── Team Templates (if user belongs to teams)
   ├── Personal Templates (user's saved templates)
   └── Community Templates (popular public templates)

2. User selects template or chooses "Custom"

3. System applies template hierarchy:
   ├── Start with Global Default workflows
   ├── Layer on selected template workflows
   ├── Apply any team-specific additions
   └── Allow user customizations before finalizing
```

#### 2. Template Application Algorithm
```
For selected template:
1. Resolve inheritance chain (template → parent → global)
2. Collect all workflow assignments per hierarchy level
3. Apply override rules (required vs. optional workflows)
4. Check for conflicts and dependencies
5. Present final configuration for user approval
6. Apply to new project with customization tracking
```

### Template Management Features

#### 1. Template Creation
```
From Existing Project:
- "Save Project as Template" 
- System extracts workflow configuration
- User defines template scope (personal/team/public)
- Set inheritance rules and required workflows

From Scratch:
- Start with base template or empty
- Add workflows at each hierarchy level
- Define default skip conditions
- Set execution triggers and repetition patterns
```

#### 2. Template Evolution
```
Template Updates:
- Modify existing template definitions
- System tracks version history
- Option to apply updates to existing projects
- Rollback capability for problematic updates

Learning Integration:
- System analyzes project success patterns
- Suggests template improvements
- Identifies commonly added/removed workflows
- Proposes new template variants
```

#### 3. Template Sharing and Discovery
```
Community Features:
- Publish templates publicly
- Browse template marketplace
- Rate and review templates
- Fork popular templates for customization
- Contribute improvements back to originals

Team Collaboration:
- Share templates within organization
- Team template inheritance
- Approval workflows for template changes
- Template usage analytics
```

### Smart Template Features

#### 1. Context-Aware Template Selection
```json
{
  "project_type": "e-commerce",
  "budget": "< $10k",
  "timeline": "< 2 months", 
  "team_size": 3,
  "suggested_template": "lean_ecommerce_variant",
  "reason": "Optimized for small team, tight timeline projects"
}
```

#### 2. Dynamic Template Customization
```
Automatic Adjustments:
- Budget constraints → Remove expensive workflows
- Timeline pressure → Defer non-critical workflows  
- Team expertise → Add/remove skill-specific workflows
- Client type → Apply compliance/process requirements

User Notification:
"Based on your project parameters, I've suggested modifications 
to the Web Development template. Review changes before applying."
```

#### 3. Template Validation and Warnings
```
Pre-Application Checks:
├── Dependency validation (required tools/skills)
├── Resource requirement warnings
├── Timeline feasibility analysis
├── Budget impact assessment
└── Team capacity considerations

Example Warning:
"This template includes advanced security workflows requiring 
specialized tools. Estimated additional cost: $500/month."
```

## Component Composition Rules

### Containment Hierarchy
```
Workflows CAN contain:
  ├── Actions (atomic operations)
  ├── Groups (clustered actions)  
  └── Other Workflows (nested orchestration)

Groups CAN contain:
  ├── Actions (atomic operations)
  └── Other Groups (nested clustering)
  └── CANNOT contain Workflows (maintains clear separation)

Actions:
  └── Leaf nodes only (no composition)
```

### Interface Contracts
Every component must define:
- **Input Schema**: What data/context it expects
- **Output Schema**: What it produces
- **Side Effects**: What it changes in the environment
- **Error Patterns**: How it can fail and recovery strategies

### Execution Patterns
- **Sequential**: `A → B → C` (default)
- **Parallel**: `A || B || C` (where dependencies allow)
- **Conditional**: `A → if(condition) B else C`
- **Error Handling**: `A catch B` (fallback actions)
- **Loops**: `repeat A until condition`

---

## Agent Integration Points

### 1. Task Request Processing
```
Agent Request: "What should I do for Website Redesign::Design Phase::1.1?"

System Response:
1. Resolve hierarchy reference
2. Compile contextual instructions
3. Return comprehensive task definition
```

### 2. Progress Tracking
```
Agent Reports: "Completed action X with result Y"

System Processing:
1. Update task/subtask status
2. Check completion triggers
3. Activate next workflow components
4. Update project timeline
```

### 3. Context Queries
```
Agent Request: "What's the background context for this task?"

System Response:
1. Aggregate hierarchy context
2. Include relevant project constraints
3. Provide stakeholder information
4. Surface related completed work
```

### 4. Dynamic Adaptation
```
Agent Request: "This approach isn't working, what are alternatives?"

System Response:
1. Query alternative workflows for same outcome
2. Suggest fallback actions from error_patterns
3. Escalate to higher hierarchy level if needed
4. Provide troubleshooting workflows
```

---

## User Experience Design

### Project Setup Flow
```
1. CREATE PROJECT
   ├── Enter basic project details
   └── System suggests template based on project type/context

2. TEMPLATE SELECTION
   ├── Browse available templates with previews
   ├── See workflow summary for each template
   ├── Compare templates side-by-side
   └── Preview expected timeline and resource requirements

3. CUSTOMIZATION
   ├── Review inherited workflows from template
   ├── Add project-specific workflows
   ├── Set skip conditions for known constraints
   ├── Configure repetition patterns
   └── Set team permissions and responsibilities

4. VALIDATION & LAUNCH
   ├── System validates workflow dependencies
   ├── Estimates resource requirements
   ├── Identifies potential conflicts or issues
   ├── User approves final configuration
   └── Project created with agent ready to execute
```

### Daily Usage Patterns
```
MORNING ROUTINE:
Agent: "Good morning! Here's what's planned for today:"
├── Reviews overnight progress
├── Surfaces today's scheduled workflows
├── Highlights any blockers or issues
├── Suggests priority adjustments
└── Asks for any urgent changes to the plan

TASK EXECUTION:
Agent: "Starting work on Website Redesign::Design Phase::1.1"
├── Loads complete context from hierarchy
├── Executes applicable workflows in sequence
├── Reports progress and asks for guidance when needed
├── Handles exceptions using defined skip logic
└── Updates project status and triggers next actions

END-OF-DAY REVIEW:
Agent: "Here's what we accomplished today:"
├── Summarizes completed workflows
├── Notes any skipped or deferred items
├── Identifies tomorrow's priorities
├── Suggests template improvements based on today's experience
└── Updates project timeline and stakeholder communications
```

### Configuration Interfaces

#### Simple User (Basic Templates)
```
PROJECT SETUP:
"What type of project is this?"
├── Website Development
├── Mobile App
├── Research Project
├── Marketing Campaign
└── Custom

"Any special requirements?"
├── Tight timeline ☐
├── Limited budget ☐  
├── High security needs ☐
├── Client has specific processes ☐

System auto-configures based on selections.
```

#### Power User (Workflow Customization)
```
WORKFLOW BUILDER:
├── Drag-and-drop workflow assignment
├── Conditional logic builder (visual)
├── Skip condition templates
├── Custom action creation
├── Workflow testing and simulation
└── Template creation from projects
```

#### Admin User (Organization Management)
```
TEMPLATE GOVERNANCE:
├── Organization-wide template management
├── Workflow library administration  
├── Usage analytics and optimization
├── Team template permissions
├── Compliance workflow enforcement
└── System-wide configuration management
```

## Advanced Features

### 1. Template Analytics and Learning
```
Template Performance Tracking:
├── Success rate by template type
├── Common customizations made by users
├── Frequently skipped workflows (suggests template updates)
├── Timeline accuracy (actual vs. estimated)
├── Resource utilization patterns
└── User satisfaction ratings

Intelligent Suggestions:
"I notice teams using the 'Web Development' template often add 
accessibility audits. Should this be included by default?"

"Projects using the 'Startup MVP' template have 40% faster 
completion when 'documentation' workflows are deferred to 
post-launch. Update template to reflect this?"
```

### 2. Template Marketplace and Sharing
```
Public Template Library:
├── Community-contributed templates
├── Industry-specific template collections
├── Template ratings and reviews
├── Usage statistics and success stories
├── Template evolution tracking
└── Best practice documentation

Template Contribution System:
├── Submit templates for community review
├── Template quality scoring
├── Attribution and credit system
├── Version control for template improvements
├── Template certification for enterprise use
└── Revenue sharing for premium templates
```

### 3. Dynamic Template Adaptation
```
Real-Time Template Optimization:
├── Machine learning from project outcomes
├── A/B testing different workflow sequences
├── Automatic template parameter tuning
├── Context-aware workflow suggestions
├── Predictive skip condition recommendations
└── Template performance forecasting

Adaptive Execution:
Agent: "Based on similar projects, I recommend adjusting 
the testing workflow sequence. This change typically 
reduces timeline by 15% with no quality impact."
```

### 4. Cross-Project Learning
```
Knowledge Transfer:
├── Extract successful patterns from completed projects
├── Identify workflow optimizations across project types
├── Share lessons learned between teams
├── Build organizational workflow intelligence
├── Create custom templates from successful project patterns
└── Predict project risks based on workflow choices

Organizational Memory:
"Similar projects in your organization typically encounter 
issues during Phase 3. I've added additional checkpoints 
based on past experience."
```

### 5. Integration and Ecosystem
```
Tool Integration Templates:
├── Templates that configure external tool workflows
├── API integration patterns for common services
├── Authentication and permission templates
├── Data pipeline and ETL workflow templates
├── Monitoring and alerting configuration templates
└── Deployment and infrastructure templates

Ecosystem Partnerships:
├── Pre-built templates for popular project management tools
├── Integration with development environments
├── CRM and business process templates
├── Industry compliance templates (SOX, HIPAA, GDPR)
├── Cloud platform optimization templates
└── Third-party service integration templates
```

## Implementation Considerations

### Template System Performance
- Template compilation caching for faster project creation
- Lazy loading of workflow definitions
- Optimized template inheritance resolution
- Background template validation and conflict detection
- Efficient template search and discovery indexing

### Template Governance and Compliance
- Role-based access control for template creation/modification
- Audit trails for all template changes
- Mandatory workflow enforcement for compliance requirements
- Template approval workflows for enterprise environments
- Data privacy and security controls for sensitive workflows

### Template Migration and Versioning
- Seamless template updates for existing projects
- Rollback capabilities for problematic template changes
- Migration scripts for major template structure changes
- Backward compatibility maintenance
- Change impact analysis before template updates

---

This enhanced framework now provides a complete template ecosystem that solves the core problem of "remembering everything" while maintaining maximum flexibility. The template system ensures every project starts with intelligent defaults based on proven patterns, while the skip logic and customization options provide the flexibility needed for real-world project variations.

The key innovation is that your agent becomes not just a task executor, but an organizational memory system that learns and improves over time, ensuring that hard-won project management knowledge is captured, shared, and automatically applied to future projects.