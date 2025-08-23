# Project Management Services

**File Path:** `python/src/server/services/projects/` directory
**Last Updated:** 2025-08-22

## Purpose
Documentation of project management services that handle project lifecycle, task management, document operations, and progress tracking. These services provide the core business logic for project-related operations.

## Project Management Services

### 1. Project Service
**File:** `project_service.py`
**Purpose:** Core project operations and lifecycle management

**Key Features:**
- Project CRUD operations
- Project metadata management
- Project status tracking
- Team member management
- Project settings configuration

**Usage:**
```python
from services.projects.project_service import ProjectService

project_service = ProjectService()

# Create new project
project = await project_service.create_project({
    'title': 'OAuth2 Implementation',
    'description': 'Implement OAuth2 authentication system',
    'status': 'active',
    'team_members': ['user1', 'user2']
})

# Update project
await project_service.update_project(project.id, {
    'status': 'in_progress',
    'progress_percentage': 25
})

# Get project with full details
project_details = await project_service.get_project_with_details(project.id)
```

**Project Operations:**
- `create_project()` - Initialize new project with metadata
- `update_project()` - Modify project properties
- `delete_project()` - Archive project (preserves data)
- `get_project()` - Retrieve project by ID
- `list_projects()` - Get projects with filtering
- `get_project_statistics()` - Project analytics and metrics

### 2. Project Creation Service
**File:** `project_creation_service.py`
**Purpose:** Project initialization workflows and setup automation

**Key Features:**
- Template-based project creation
- Automated task generation from PRPs
- Initial document setup
- Team assignment workflows
- Integration with knowledge sources

**Usage:**
```python
from services.projects.project_creation_service import ProjectCreationService

creation_service = ProjectCreationService()

# Create project from PRP
project = await creation_service.create_project_from_prp({
    'title': 'API Development',
    'prp_content': prp_document,
    'template': 'software_development',
    'auto_generate_tasks': True
})

# Create project from template
project = await creation_service.create_from_template({
    'template_id': 'web_app_template',
    'project_name': 'E-commerce Platform',
    'customizations': {
        'tech_stack': ['React', 'Node.js', 'PostgreSQL'],
        'team_size': 'medium'
    }
})
```

**Creation Workflows:**
- **PRP-Based Creation** - Generate project from Product Requirement Prompt
- **Template-Based Creation** - Use predefined project templates
- **Custom Creation** - Manual project setup with guided workflow
- **Import Creation** - Create project from external data

### 3. Task Service
**File:** `task_service.py`
**Purpose:** Task management operations and workflow coordination

**Key Features:**
- Task CRUD operations
- Task status workflow management
- Task assignment and scheduling
- Dependency management
- Progress tracking and reporting

**Usage:**
```python
from services.projects.task_service import TaskService

task_service = TaskService()

# Create task
task = await task_service.create_task({
    'project_id': project.id,
    'title': 'Implement OAuth2 provider',
    'description': 'Set up Google OAuth2 integration',
    'assignee': 'developer1',
    'status': 'todo',
    'priority': 'high'
})

# Update task status
await task_service.update_task_status(task.id, 'doing')

# Get tasks with filtering
tasks = await task_service.get_tasks_by_status(project.id, 'review')
```

**Task Workflows:**
- **todo** → **doing** → **review** → **done**
- Automatic status transitions based on conditions
- Dependency resolution and blocking
- Assignment notifications and updates

### 4. Document Service
**File:** `document_service.py`
**Purpose:** Project document management and version control

**Key Features:**
- Document CRUD operations
- Version control and history
- Document type management (PRP, specs, notes)
- Content validation and processing
- Document linking and relationships

**Usage:**
```python
from services.projects.document_service import DocumentService

doc_service = DocumentService()

# Create PRP document
prp_doc = await doc_service.create_document({
    'project_id': project.id,
    'document_type': 'prp',
    'title': 'OAuth2 Requirements',
    'content': prp_content,
    'metadata': {
        'version': '1.0',
        'author': 'product_manager',
        'status': 'draft'
    }
})

# Update document with versioning
await doc_service.update_document(prp_doc.id, {
    'content': updated_content,
    'metadata': {'version': '1.1', 'status': 'review'}
})
```

**Document Types:**
- **PRP** - Product Requirement Prompts
- **Specification** - Technical specifications
- **Design** - Design documents and mockups
- **Notes** - Meeting notes and general documentation

### 5. Versioning Service
**File:** `versioning_service.py`
**Purpose:** Document version control and history management

**Key Features:**
- Automatic version snapshots
- Version comparison and diff generation
- Rollback and restore capabilities
- Branch and merge operations
- Audit trail and change tracking

**Usage:**
```python
from services.projects.versioning_service import VersioningService

version_service = VersioningService()

# Create version snapshot
version = await version_service.create_version(
    document_id=doc.id,
    change_summary='Added validation section',
    created_by='developer1'
)

# Get version history
history = await version_service.get_version_history(doc.id)

# Restore previous version
await version_service.restore_version(doc.id, version_number=3)
```

**Version Operations:**
- `create_version()` - Manual version snapshot
- `auto_version()` - Automatic versioning on changes
- `compare_versions()` - Generate diff between versions
- `restore_version()` - Rollback to previous version
- `merge_versions()` - Merge changes from different versions

### 6. Progress Service
**File:** `progress_service.py`
**Purpose:** Project progress tracking and analytics

**Key Features:**
- Progress calculation algorithms
- Milestone tracking
- Velocity measurements
- Burndown chart data
- Predictive analytics

**Usage:**
```python
from services.projects.progress_service import ProgressService

progress_service = ProgressService()

# Calculate project progress
progress = await progress_service.calculate_project_progress(project.id)

# Get milestone status
milestones = await progress_service.get_milestone_progress(project.id)

# Generate burndown data
burndown = await progress_service.generate_burndown_chart(project.id)
```

**Progress Metrics:**
- **Task Completion Rate** - Percentage of completed tasks
- **Velocity** - Tasks completed per time period
- **Burndown** - Remaining work over time
- **Milestone Progress** - Progress toward key milestones
- **Quality Metrics** - Code quality and review metrics

### 7. Export Service
**File:** `export_service.py`
**Purpose:** Project data export and reporting

**Key Features:**
- Multiple export formats (PDF, JSON, CSV, Markdown)
- Customizable export templates
- Scheduled export automation
- Data filtering and selection
- Secure export with access control

**Usage:**
```python
from services.projects.export_service import ExportService

export_service = ExportService()

# Export project to PDF
pdf_data = await export_service.export_project_pdf(
    project_id=project.id,
    include_sections=['overview', 'tasks', 'documents'],
    template='professional'
)

# Export tasks to CSV
csv_data = await export_service.export_tasks_csv(
    project_id=project.id,
    filters={'status': ['done', 'review']},
    columns=['title', 'assignee', 'completed_date']
)
```

### 8. Import Service
**File:** `import_service.py`
**Purpose:** Project data import and migration

**Key Features:**
- Multiple import formats support
- Data validation and transformation
- Conflict resolution strategies
- Import progress tracking
- Rollback capabilities

**Usage:**
```python
from services.projects.import_service import ImportService

import_service = ImportService()

# Import project from JSON
result = await import_service.import_project_json(
    json_data=project_data,
    conflict_strategy='merge',
    validate_data=True
)

# Import tasks from CSV
task_result = await import_service.import_tasks_csv(
    project_id=project.id,
    csv_data=task_csv,
    mapping={
        'title': 'Task Name',
        'assignee': 'Assigned To',
        'due_date': 'Due Date'
    }
)
```

### 9. Source Linking Service
**File:** `source_linking_service.py`
**Purpose:** Knowledge source linking and integration

**Key Features:**
- Link projects to knowledge sources
- Automatic content synchronization
- Source relevance scoring
- Content change detection
- Integration with RAG system

**Usage:**
```python
from services.projects.source_linking_service import SourceLinkingService

linking_service = SourceLinkingService()

# Link knowledge source to project
await linking_service.link_source_to_project(
    project_id=project.id,
    source_url='https://docs.example.com',
    relevance_score=0.9,
    auto_sync=True
)

# Get linked sources
sources = await linking_service.get_project_sources(project.id)

# Sync source content
await linking_service.sync_source_content(project.id, source_id)
```

## Service Integration Patterns

### 1. Project Lifecycle Orchestration
```python
class ProjectOrchestrator:
    def __init__(self):
        self.project_service = ProjectService()
        self.creation_service = ProjectCreationService()
        self.task_service = TaskService()
        self.document_service = DocumentService()
    
    async def create_complete_project(self, project_data, prp_content):
        # Create project
        project = await self.creation_service.create_project_from_prp({
            **project_data,
            'prp_content': prp_content
        })
        
        # Generate initial documents
        prp_doc = await self.document_service.create_prp_document(
            project.id, prp_content
        )
        
        # Generate tasks from PRP
        tasks = await self.task_service.generate_tasks_from_prp(
            project.id, prp_content
        )
        
        return project, prp_doc, tasks
```

### 2. Progress Tracking Integration
```python
class ProgressTracker:
    def __init__(self):
        self.progress_service = ProgressService()
        self.task_service = TaskService()
        self.document_service = DocumentService()
    
    async def update_project_progress(self, project_id):
        # Calculate task-based progress
        task_progress = await self.progress_service.calculate_task_progress(project_id)
        
        # Calculate document completion
        doc_progress = await self.progress_service.calculate_document_progress(project_id)
        
        # Update overall project progress
        overall_progress = (task_progress + doc_progress) / 2
        await self.project_service.update_project(project_id, {
            'progress_percentage': overall_progress
        })
```

### 3. Event-Driven Updates
```python
class ProjectEventHandler:
    async def on_task_status_changed(self, task_id, old_status, new_status):
        task = await self.task_service.get_task(task_id)
        
        # Update project progress
        await self.progress_service.recalculate_project_progress(task.project_id)
        
        # Notify team members
        await self.notification_service.notify_task_update(task, old_status, new_status)
        
        # Update related tasks
        if new_status == 'done':
            await self.task_service.check_dependent_tasks(task_id)
```

## Error Handling and Validation

### 1. Project Validation
```python
class ProjectValidator:
    def validate_project_data(self, project_data):
        errors = []
        
        if not project_data.get('title'):
            errors.append('Project title is required')
        
        if len(project_data.get('title', '')) > 200:
            errors.append('Project title too long')
        
        if project_data.get('status') not in ['active', 'inactive', 'completed']:
            errors.append('Invalid project status')
        
        if errors:
            raise ValidationError(errors)
```

### 2. Transaction Management
```python
class ProjectTransactionManager:
    async def create_project_with_rollback(self, project_data, prp_content):
        async with self.db.transaction():
            try:
                project = await self.project_service.create_project(project_data)
                document = await self.document_service.create_document({
                    'project_id': project.id,
                    'content': prp_content
                })
                tasks = await self.task_service.generate_tasks(project.id, prp_content)
                
                return project, document, tasks
            except Exception as e:
                # Transaction will automatically rollback
                logger.error(f"Project creation failed: {e}")
                raise
```

## Related Files
- **Parent components:** API endpoints, background tasks, webhooks
- **Child components:** Database repositories, notification services, file storage
- **Shared utilities:** Validation, formatting, type definitions

## Notes
- All services implement comprehensive error handling
- Async patterns for I/O operations
- Transaction support for data consistency
- Event-driven architecture for real-time updates
- Comprehensive validation and business rules
- Performance optimization with caching
- Audit logging for all operations
- Integration with external services and APIs

---
*Auto-generated documentation - verify accuracy before use*
