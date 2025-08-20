# Archon Issue/Bug Tracker - Comprehensive Design Document

## 🎯 Executive Summary

This document outlines the design and implementation strategy for a comprehensive issue/bug tracker feature within the Archon system. The tracker will be implemented as a new module parallel to the existing task management system, featuring an "Issues" tab in the main navigation alongside Docs and Tasks.

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Data Model Design](#data-model-design)
3. [API Design](#api-design)
4. [UI/UX Design](#uiux-design)
5. [Knowledge Base Integration](#knowledge-base-integration)
6. [Implementation Strategy](#implementation-strategy)
7. [Testing Strategy](#testing-strategy)
8. [Migration & Deployment](#migration--deployment)

## 🏗️ System Architecture

### Core Principles
- **Parallel Module Design**: Issue tracker operates independently alongside task management
- **Consistent Patterns**: Follows existing Archon architectural patterns and conventions
- **Knowledge Integration**: Deep integration with Archon's knowledge base for contextual linking
- **Real-time Updates**: Socket.IO integration for live collaboration
- **Audit Trail**: Complete historical tracking for compliance and debugging

### Component Architecture
```
Issues Module
├── Frontend (React/TypeScript)
│   ├── IssuesTab.tsx (Main tab component)
│   ├── IssueBoard.tsx (Kanban-style board view)
│   ├── IssueTable.tsx (Table view with filtering)
│   ├── IssueModal.tsx (Create/edit modal)
│   ├── IssueDetails.tsx (Detailed issue view)
│   └── components/
│       ├── IssueCard.tsx
│       ├── IssueFilters.tsx
│       ├── AttachmentUpload.tsx
│       └── KnowledgeLinker.tsx
├── Backend (FastAPI/Python)
│   ├── issue_service.py (Core business logic)
│   ├── issue_api.py (REST endpoints)
│   ├── issue_models.py (Pydantic models)
│   └── issue_repository.py (Database operations)
└── Database (PostgreSQL/Supabase)
    ├── archon_issues (Main issues table)
    ├── archon_issue_attachments (File attachments)
    ├── archon_issue_comments (Comments/updates)
    └── archon_issue_knowledge_links (KB connections)
```

## 🗄️ Data Model Design

### Core Issue Fields

#### Primary Issue Entity
```sql
CREATE TABLE archon_issues (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES archon_projects(id) ON DELETE CASCADE,
  
  -- Basic Information
  title TEXT NOT NULL CHECK (length(title) >= 3 AND length(title) <= 255),
  description TEXT DEFAULT '',
  issue_type issue_type_enum DEFAULT 'bug',
  
  -- Classification
  severity severity_enum DEFAULT 'medium',
  priority priority_enum DEFAULT 'medium',
  category TEXT, -- e.g., 'frontend', 'backend', 'database', 'ui/ux'
  component TEXT, -- Specific component/module affected
  
  -- Workflow
  status issue_status_enum DEFAULT 'open',
  assignee TEXT DEFAULT 'Unassigned',
  reporter TEXT NOT NULL DEFAULT 'User',
  
  -- Technical Details
  environment TEXT, -- 'development', 'staging', 'production'
  browser_info JSONB DEFAULT '{}',
  reproduction_steps TEXT DEFAULT '',
  expected_behavior TEXT DEFAULT '',
  actual_behavior TEXT DEFAULT '',
  
  -- Metadata
  tags JSONB DEFAULT '[]',
  labels JSONB DEFAULT '[]',
  metadata JSONB DEFAULT '{}',
  
  -- Relationships
  parent_issue_id UUID REFERENCES archon_issues(id),
  related_task_ids JSONB DEFAULT '[]',
  duplicate_of UUID REFERENCES archon_issues(id),
  
  -- Tracking
  estimated_hours DECIMAL(5,2),
  actual_hours DECIMAL(5,2),
  resolution_notes TEXT,
  
  -- Audit
  archived BOOLEAN DEFAULT false,
  archived_at TIMESTAMPTZ,
  archived_by TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  resolved_at TIMESTAMPTZ,
  closed_at TIMESTAMPTZ
);
```

#### Supporting Enums
```sql
-- Issue Types
CREATE TYPE issue_type_enum AS ENUM (
  'bug',           -- Software defects
  'feature',       -- Feature requests
  'enhancement',   -- Improvements to existing features
  'task',          -- General tasks
  'epic',          -- Large features spanning multiple issues
  'story',         -- User stories
  'spike',         -- Research/investigation tasks
  'hotfix',        -- Critical production fixes
  'documentation', -- Documentation updates
  'security',      -- Security-related issues
  'performance',   -- Performance improvements
  'refactor'       -- Code refactoring
);

-- Severity Levels
CREATE TYPE severity_enum AS ENUM (
  'critical',   -- System down, data loss, security breach
  'high',       -- Major functionality broken, workaround exists
  'medium',     -- Minor functionality issues, easy workaround
  'low',        -- Cosmetic issues, nice-to-have fixes
  'trivial'     -- Documentation, minor UI tweaks
);

-- Priority Levels  
CREATE TYPE priority_enum AS ENUM (
  'urgent',     -- Must be fixed immediately
  'high',       -- Should be fixed in current sprint
  'medium',     -- Should be fixed in next sprint
  'low',        -- Can be fixed when time permits
  'backlog'     -- Future consideration
);

-- Issue Status Workflow
CREATE TYPE issue_status_enum AS ENUM (
  'open',           -- Newly created, needs triage
  'triaged',        -- Reviewed and categorized
  'in_progress',    -- Actively being worked on
  'blocked',        -- Cannot proceed due to dependencies
  'review',         -- Solution implemented, needs review
  'testing',        -- In QA/testing phase
  'resolved',       -- Fixed but not yet verified
  'closed',         -- Verified as fixed and closed
  'duplicate',      -- Duplicate of another issue
  'wont_fix',       -- Decided not to fix
  'invalid',        -- Not a valid issue
  'deferred'        -- Postponed to future release
);
```

### Supporting Tables

#### Issue Attachments
```sql
CREATE TABLE archon_issue_attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id UUID REFERENCES archon_issues(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  original_filename TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  mime_type TEXT NOT NULL,
  file_path TEXT NOT NULL, -- Storage path
  attachment_type attachment_type_enum DEFAULT 'file',
  description TEXT DEFAULT '',
  uploaded_by TEXT NOT NULL DEFAULT 'User',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TYPE attachment_type_enum AS ENUM (
  'screenshot',
  'log_file', 
  'document',
  'video',
  'file',
  'code_snippet'
);
```

#### Issue Comments/Updates
```sql
CREATE TABLE archon_issue_comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id UUID REFERENCES archon_issues(id) ON DELETE CASCADE,
  comment_type comment_type_enum DEFAULT 'comment',
  content TEXT NOT NULL,
  author TEXT NOT NULL DEFAULT 'User',
  is_internal BOOLEAN DEFAULT false, -- Internal team comments
  metadata JSONB DEFAULT '{}', -- For system-generated updates
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TYPE comment_type_enum AS ENUM (
  'comment',        -- User comment
  'status_change',  -- Status transition
  'assignment',     -- Assignment change
  'system',         -- System-generated update
  'resolution'      -- Resolution notes
);
```

#### Knowledge Base Links
```sql
CREATE TABLE archon_issue_knowledge_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issue_id UUID REFERENCES archon_issues(id) ON DELETE CASCADE,
  knowledge_item_id TEXT NOT NULL, -- References knowledge base
  link_type knowledge_link_type_enum DEFAULT 'reference',
  relevance_score DECIMAL(3,2) DEFAULT 0.0, -- 0.0 to 1.0
  description TEXT DEFAULT '',
  created_by TEXT NOT NULL DEFAULT 'User',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TYPE knowledge_link_type_enum AS ENUM (
  'reference',      -- General reference
  'solution',       -- Known solution
  'workaround',     -- Temporary workaround
  'related_issue',  -- Related problem
  'documentation',  -- Relevant documentation
  'example'         -- Code example
);
```

## 🔌 API Design

### REST Endpoints

#### Issue Management
```python
# Core CRUD operations
POST   /api/issues                    # Create new issue
GET    /api/issues                    # List issues with filtering
GET    /api/issues/{issue_id}         # Get specific issue
PUT    /api/issues/{issue_id}         # Update issue
DELETE /api/issues/{issue_id}         # Archive issue

# Workflow operations
POST   /api/issues/{issue_id}/assign  # Assign issue
POST   /api/issues/{issue_id}/status  # Change status
POST   /api/issues/{issue_id}/close   # Close issue
POST   /api/issues/{issue_id}/reopen  # Reopen issue

# Relationships
POST   /api/issues/{issue_id}/link    # Link to another issue
POST   /api/issues/{issue_id}/duplicate # Mark as duplicate
```

#### Comments & Updates
```python
GET    /api/issues/{issue_id}/comments     # Get comments
POST   /api/issues/{issue_id}/comments     # Add comment
PUT    /api/issues/{issue_id}/comments/{comment_id} # Update comment
DELETE /api/issues/{issue_id}/comments/{comment_id} # Delete comment
```

#### Attachments
```python
POST   /api/issues/{issue_id}/attachments  # Upload attachment
GET    /api/issues/{issue_id}/attachments  # List attachments
DELETE /api/issues/{issue_id}/attachments/{attachment_id} # Delete attachment
```

#### Knowledge Integration
```python
POST   /api/issues/{issue_id}/knowledge-links    # Link to knowledge item
GET    /api/issues/{issue_id}/knowledge-links    # Get linked knowledge
DELETE /api/issues/{issue_id}/knowledge-links/{link_id} # Remove link
GET    /api/issues/{issue_id}/suggested-knowledge # AI-suggested links
```

### Request/Response Models

#### Create Issue Request
```python
class CreateIssueRequest(BaseModel):
    project_id: str
    title: str = Field(..., min_length=3, max_length=255)
    description: str = ""
    issue_type: IssueType = IssueType.BUG
    severity: Severity = Severity.MEDIUM
    priority: Priority = Priority.MEDIUM
    category: Optional[str] = None
    component: Optional[str] = None
    assignee: str = "Unassigned"
    environment: Optional[str] = None
    reproduction_steps: str = ""
    expected_behavior: str = ""
    actual_behavior: str = ""
    tags: List[str] = []
    labels: List[str] = []
    browser_info: Dict[str, Any] = {}
    estimated_hours: Optional[Decimal] = None
```

#### Issue Response
```python
class IssueResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    issue_type: IssueType
    severity: Severity
    priority: Priority
    status: IssueStatus
    assignee: str
    reporter: str
    category: Optional[str]
    component: Optional[str]
    environment: Optional[str]
    tags: List[str]
    labels: List[str]
    
    # Relationships
    parent_issue_id: Optional[str]
    related_task_ids: List[str]
    duplicate_of: Optional[str]
    
    # Tracking
    estimated_hours: Optional[Decimal]
    actual_hours: Optional[Decimal]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    # Computed fields
    attachments_count: int
    comments_count: int
    knowledge_links_count: int
    age_in_days: int
```

## 🎨 UI/UX Design

### Navigation Integration
- Add "Issues" tab to main project navigation (alongside Docs and Tasks)
- Use existing tab component patterns from `ProjectPage.tsx`
- Maintain consistent styling with current Archon design system

### Main Issues Interface

#### View Modes
1. **Board View** (Default)
   - Kanban-style columns by status
   - Drag-and-drop status changes
   - Color-coded by severity/priority
   - Quick actions on hover

2. **Table View**
   - Sortable columns
   - Advanced filtering
   - Bulk operations
   - Export capabilities

3. **Detail View**
   - Full issue information
   - Comment thread
   - Attachment gallery
   - Knowledge links panel

#### Key UI Components

##### IssueCard Component
```tsx
interface IssueCardProps {
  issue: Issue;
  onEdit: (issue: Issue) => void;
  onStatusChange: (issueId: string, status: IssueStatus) => void;
  onAssign: (issueId: string, assignee: string) => void;
  compact?: boolean;
}

// Features:
// - Severity/priority indicators
// - Assignee avatar
// - Tag badges
// - Attachment/comment counts
// - Quick action buttons
// - Drag handle for reordering
```

##### IssueModal Component
```tsx
interface IssueModalProps {
  isOpen: boolean;
  issue?: Issue; // undefined for create mode
  onClose: () => void;
  onSave: (issue: Partial<Issue>) => Promise<void>;
  project: Project;
}

// Features:
// - Multi-step form for complex issues
// - Rich text editor for description
// - File upload for attachments
// - Knowledge base search/link
// - Template selection
// - Auto-save drafts
```

##### IssueFilters Component
```tsx
interface IssueFiltersProps {
  filters: IssueFilters;
  onFiltersChange: (filters: IssueFilters) => void;
  availableOptions: {
    assignees: string[];
    categories: string[];
    components: string[];
    tags: string[];
  };
}

// Features:
// - Multi-select dropdowns
// - Date range pickers
// - Search input
// - Saved filter presets
// - Clear all filters
```

### Design System Integration

#### Color Coding
- **Severity**: Critical (red), High (orange), Medium (yellow), Low (blue), Trivial (gray)
- **Priority**: Urgent (red pulse), High (red), Medium (blue), Low (gray), Backlog (muted)
- **Status**: Open (blue), In Progress (yellow), Blocked (red), Resolved (green), Closed (gray)

#### Icons
- Bug: `Bug` from Lucide React
- Feature: `Lightbulb`
- Enhancement: `TrendingUp`
- Task: `CheckSquare`
- Epic: `Layers`
- Security: `Shield`
- Performance: `Zap`

#### Responsive Design
- Mobile-first approach
- Collapsible sidebar filters
- Touch-friendly drag and drop
- Optimized for tablet use

## 🧠 Knowledge Base Integration

### Automatic Linking
- **AI-Powered Suggestions**: Use RAG service to suggest relevant knowledge items
- **Semantic Search**: Match issue descriptions with existing documentation
- **Code Example Linking**: Connect issues to relevant code snippets
- **Solution Discovery**: Find previous resolutions for similar issues

### Manual Linking Interface
```tsx
interface KnowledgeLinkerProps {
  issueId: string;
  onLinkAdded: (link: KnowledgeLink) => void;
  existingLinks: KnowledgeLink[];
}

// Features:
// - Search knowledge base
// - Preview knowledge items
// - Select link type (solution, reference, etc.)
// - Add relevance notes
// - Bulk link operations
```

### Knowledge Integration Features

#### Smart Suggestions
```python
async def suggest_knowledge_for_issue(issue: Issue) -> List[KnowledgeSuggestion]:
    """
    Use RAG service to find relevant knowledge items for an issue.
    
    Combines:
    - Issue title and description
    - Error messages and stack traces
    - Component/category information
    - Similar resolved issues
    """
    
    # Build search query from issue context
    search_query = f"""
    {issue.title}
    {issue.description}
    {issue.actual_behavior}
    Component: {issue.component}
    Category: {issue.category}
    """
    
    # Search knowledge base
    rag_results = await rag_service.search_documents(
        query=search_query,
        match_count=10,
        filter_metadata={"project_id": issue.project_id}
    )
    
    # Search code examples
    code_results = await rag_service.search_code_examples(
        query=search_query,
        match_count=5
    )
    
    # Combine and rank suggestions
    return rank_knowledge_suggestions(rag_results, code_results, issue)
```

#### Resolution Knowledge Capture
- Automatically create knowledge entries from resolved issues
- Extract solutions and workarounds
- Build searchable resolution database
- Link related issues for pattern recognition

## 🚀 Implementation Strategy

### Phase 1: Core Infrastructure (Week 1-2)
1. Database schema creation and migrations
2. Basic API endpoints (CRUD operations)
3. Core service layer implementation
4. Basic UI components and routing

### Phase 2: Essential Features (Week 3-4)
1. Issue creation and editing
2. Status workflow implementation
3. Basic filtering and search
4. File attachment support

### Phase 3: Advanced Features (Week 5-6)
1. Knowledge base integration
2. Real-time updates via Socket.IO
3. Advanced filtering and views
4. Comment system

### Phase 4: Polish & Integration (Week 7-8)
1. UI/UX refinements
2. Performance optimization
3. Comprehensive testing
4. Documentation and training

### Development Priorities
1. **Data Integrity**: Robust validation and constraints
2. **Performance**: Efficient queries and caching
3. **User Experience**: Intuitive interface and workflows
4. **Integration**: Seamless knowledge base connectivity
5. **Scalability**: Support for large issue volumes

## 🧪 Testing Strategy

### Unit Tests
- Service layer business logic
- API endpoint validation
- Data model constraints
- Utility functions

### Integration Tests
- Database operations
- Knowledge base integration
- File upload/download
- Real-time updates

### E2E Tests
- Complete issue lifecycle
- User workflows
- Cross-browser compatibility
- Mobile responsiveness

### Performance Tests
- Large dataset handling
- Concurrent user scenarios
- Search performance
- File upload limits

## 📦 Migration & Deployment

### Database Migration
```sql
-- Migration script: 001_create_issues_tables.sql
-- Includes all table creation, indexes, and constraints
-- Rollback procedures for safe deployment
```

### Feature Flags
- Gradual rollout capability
- A/B testing for UI changes
- Emergency disable switch
- User-specific enablement

### Monitoring & Metrics
- Issue creation/resolution rates
- User engagement metrics
- Performance monitoring
- Error tracking and alerting

---

## 📋 Next Steps

1. **Stakeholder Review**: Present design for feedback and approval
2. **Technical Validation**: Verify integration points with existing systems
3. **Resource Planning**: Allocate development team and timeline
4. **Prototype Development**: Build minimal viable version for validation
5. **Implementation Planning**: Detailed sprint planning and task breakdown

This design document provides a comprehensive foundation for implementing a robust issue/bug tracker that seamlessly integrates with the existing Archon ecosystem while providing powerful new capabilities for project management and knowledge discovery.

## 🔧 Technical Implementation Details

### Service Layer Architecture

#### IssueService Class
```python
class IssueService:
    """Core business logic for issue management"""

    def __init__(self, supabase_client=None):
        self.supabase_client = supabase_client or get_supabase_client()
        self.knowledge_service = KnowledgeItemService(supabase_client)
        self.rag_service = RAGService()

    async def create_issue(self, issue_data: CreateIssueRequest) -> tuple[bool, dict]:
        """Create new issue with validation and knowledge suggestions"""

        # Validate issue data
        validation_result = self.validate_issue_data(issue_data)
        if not validation_result.is_valid:
            return False, {"error": validation_result.errors}

        # Create issue record
        issue_id = str(uuid.uuid4())
        issue_record = {
            "id": issue_id,
            "project_id": issue_data.project_id,
            "title": issue_data.title,
            "description": issue_data.description,
            "issue_type": issue_data.issue_type,
            "severity": issue_data.severity,
            "priority": issue_data.priority,
            "status": "open",
            "assignee": issue_data.assignee,
            "reporter": "User",  # TODO: Get from auth context
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Insert into database
        result = self.supabase_client.table("archon_issues").insert(issue_record).execute()

        # Generate knowledge suggestions asynchronously
        asyncio.create_task(self.generate_knowledge_suggestions(issue_id, issue_data))

        return True, {"issue": result.data[0]}

    async def generate_knowledge_suggestions(self, issue_id: str, issue_data: CreateIssueRequest):
        """Generate AI-powered knowledge suggestions for new issue"""

        search_query = f"{issue_data.title} {issue_data.description} {issue_data.actual_behavior}"

        # Search existing knowledge
        knowledge_results = await self.rag_service.search_documents(
            query=search_query,
            match_count=5,
            filter_metadata={"project_id": issue_data.project_id}
        )

        # Search code examples
        code_results = await self.rag_service.search_code_examples(
            query=search_query,
            match_count=3
        )

        # Create suggested links
        suggestions = []
        for result in knowledge_results:
            if result.get("similarity", 0) > 0.7:  # High relevance threshold
                suggestions.append({
                    "issue_id": issue_id,
                    "knowledge_item_id": result["source_id"],
                    "link_type": "reference",
                    "relevance_score": result["similarity"],
                    "description": f"Auto-suggested based on content similarity",
                    "created_by": "system"
                })

        # Insert suggestions
        if suggestions:
            self.supabase_client.table("archon_issue_knowledge_links").insert(suggestions).execute()
```

#### Real-time Updates with Socket.IO
```python
class IssueSocketService:
    """Handle real-time issue updates"""

    def __init__(self, socketio_instance):
        self.sio = socketio_instance

    async def broadcast_issue_update(self, issue_id: str, update_type: str, data: dict):
        """Broadcast issue updates to connected clients"""

        room = f"project_{data.get('project_id')}"
        await self.sio.emit('issue_updated', {
            'issue_id': issue_id,
            'update_type': update_type,  # 'created', 'updated', 'status_changed', etc.
            'data': data,
            'timestamp': datetime.now().isoformat()
        }, room=room)

    async def join_project_room(self, sid: str, project_id: str):
        """Add client to project-specific room for issue updates"""
        await self.sio.enter_room(sid, f"project_{project_id}")
```

### Frontend Component Architecture

#### IssuesTab Main Component
```tsx
export const IssuesTab: React.FC<IssuesTabProps> = ({ project }) => {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [viewMode, setViewMode] = useState<'board' | 'table'>('board');
  const [filters, setFilters] = useState<IssueFilters>({});
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Real-time updates
  useEffect(() => {
    const socket = getSocketInstance();

    socket.on('issue_updated', (data) => {
      handleIssueUpdate(data);
    });

    socket.emit('join_project', project.id);

    return () => {
      socket.off('issue_updated');
      socket.emit('leave_project', project.id);
    };
  }, [project.id]);

  const handleIssueUpdate = (updateData: IssueUpdateData) => {
    setIssues(prevIssues => {
      switch (updateData.update_type) {
        case 'created':
          return [...prevIssues, updateData.data];
        case 'updated':
          return prevIssues.map(issue =>
            issue.id === updateData.issue_id
              ? { ...issue, ...updateData.data }
              : issue
          );
        case 'deleted':
          return prevIssues.filter(issue => issue.id !== updateData.issue_id);
        default:
          return prevIssues;
      }
    });
  };

  return (
    <div className="space-y-6">
      {/* Header with actions */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold">Issues</h2>
          <Badge variant="secondary">{issues.length} total</Badge>
        </div>

        <div className="flex items-center gap-2">
          <IssueFilters
            filters={filters}
            onFiltersChange={setFilters}
            availableOptions={getFilterOptions(issues)}
          />

          <Button
            onClick={() => setViewMode(viewMode === 'board' ? 'table' : 'board')}
            variant="outline"
            size="sm"
          >
            {viewMode === 'board' ? <Table className="w-4 h-4" /> : <Kanban className="w-4 h-4" />}
          </Button>

          <Button
            onClick={() => setShowCreateModal(true)}
            accentColor="blue"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Issue
          </Button>
        </div>
      </div>

      {/* Main content */}
      {viewMode === 'board' ? (
        <IssueBoard
          issues={filteredIssues}
          onIssueUpdate={handleIssueUpdate}
          onIssueSelect={setSelectedIssue}
        />
      ) : (
        <IssueTable
          issues={filteredIssues}
          onIssueUpdate={handleIssueUpdate}
          onIssueSelect={setSelectedIssue}
        />
      )}

      {/* Modals */}
      <IssueModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSave={handleCreateIssue}
        project={project}
      />

      <IssueDetailModal
        issue={selectedIssue}
        isOpen={!!selectedIssue}
        onClose={() => setSelectedIssue(null)}
        onUpdate={handleIssueUpdate}
      />
    </div>
  );
};
```

#### Knowledge Integration Component
```tsx
export const KnowledgeLinker: React.FC<KnowledgeLinkerProps> = ({
  issueId,
  existingLinks,
  onLinkAdded
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<KnowledgeItem[]>([]);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [isSearching, setIsSearching] = useState(false);

  const searchKnowledge = useCallback(
    debounce(async (query: string) => {
      if (!query.trim()) {
        setSearchResults([]);
        return;
      }

      setIsSearching(true);
      try {
        const results = await knowledgeBaseService.searchKnowledgeBase(query, {
          match_count: 10,
          include_code_examples: true
        });
        setSearchResults(results.results || []);
      } catch (error) {
        console.error('Knowledge search failed:', error);
      } finally {
        setIsSearching(false);
      }
    }, 300),
    []
  );

  useEffect(() => {
    searchKnowledge(searchQuery);
  }, [searchQuery, searchKnowledge]);

  const handleLinkKnowledge = async (linkType: KnowledgeLinkType) => {
    const selectedItemIds = Array.from(selectedItems);

    for (const itemId of selectedItemIds) {
      try {
        await issueService.linkKnowledge(issueId, {
          knowledge_item_id: itemId,
          link_type: linkType,
          description: `Linked via search: "${searchQuery}"`
        });

        onLinkAdded({
          knowledge_item_id: itemId,
          link_type: linkType
        });
      } catch (error) {
        console.error('Failed to link knowledge item:', error);
      }
    }

    setSelectedItems(new Set());
    setSearchQuery('');
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Search className="w-4 h-4 text-gray-500" />
        <Input
          placeholder="Search knowledge base..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1"
        />
        {isSearching && <Loader className="w-4 h-4 animate-spin" />}
      </div>

      {searchResults.length > 0 && (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {searchResults.map((item) => (
            <div
              key={item.id}
              className={`p-3 border rounded-md cursor-pointer transition-colors ${
                selectedItems.has(item.id)
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => {
                const newSelected = new Set(selectedItems);
                if (newSelected.has(item.id)) {
                  newSelected.delete(item.id);
                } else {
                  newSelected.add(item.id);
                }
                setSelectedItems(newSelected);
              }}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-sm">{item.title}</h4>
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                    {item.metadata.description || 'No description available'}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline" size="sm">
                      {item.metadata.knowledge_type}
                    </Badge>
                    {item.metadata.tags?.map((tag) => (
                      <Badge key={tag} variant="secondary" size="sm">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
                {selectedItems.has(item.id) && (
                  <Check className="w-4 h-4 text-blue-500 flex-shrink-0" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedItems.size > 0 && (
        <div className="flex items-center gap-2 pt-2 border-t">
          <span className="text-sm text-gray-600">
            {selectedItems.size} item(s) selected
          </span>
          <div className="flex gap-1 ml-auto">
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleLinkKnowledge('reference')}
            >
              Link as Reference
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleLinkKnowledge('solution')}
            >
              Link as Solution
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
```

## 🔍 Advanced Features

### AI-Powered Issue Analysis
```python
class IssueAnalysisService:
    """AI-powered issue analysis and suggestions"""

    async def analyze_issue_patterns(self, project_id: str) -> dict:
        """Analyze patterns in project issues for insights"""

        # Get recent issues
        issues = await self.get_project_issues(project_id, limit=100)

        # Analyze patterns
        patterns = {
            "common_components": self.analyze_component_frequency(issues),
            "severity_trends": self.analyze_severity_trends(issues),
            "resolution_time_patterns": self.analyze_resolution_times(issues),
            "recurring_keywords": self.extract_recurring_keywords(issues)
        }

        return patterns

    async def suggest_similar_issues(self, issue: Issue) -> List[Issue]:
        """Find similar issues using semantic search"""

        search_query = f"{issue.title} {issue.description}"

        # Use RAG service to find similar issues
        similar_issues = await self.rag_service.search_documents(
            query=search_query,
            match_count=5,
            filter_metadata={
                "project_id": issue.project_id,
                "table": "archon_issues",
                "status": ["resolved", "closed"]
            }
        )

        return similar_issues

    async def predict_resolution_time(self, issue: Issue) -> dict:
        """Predict resolution time based on historical data"""

        # Get similar resolved issues
        similar_issues = await self.get_similar_resolved_issues(issue)

        if not similar_issues:
            return {"prediction": None, "confidence": 0}

        # Calculate average resolution time
        resolution_times = [
            (issue.resolved_at - issue.created_at).total_seconds() / 3600  # hours
            for issue in similar_issues
            if issue.resolved_at and issue.created_at
        ]

        if resolution_times:
            avg_time = sum(resolution_times) / len(resolution_times)
            confidence = min(len(resolution_times) / 10, 1.0)  # More data = higher confidence

            return {
                "prediction_hours": round(avg_time, 1),
                "confidence": confidence,
                "based_on_issues": len(resolution_times)
            }

        return {"prediction": None, "confidence": 0}
```

### Automated Workflows
```python
class IssueWorkflowService:
    """Automated issue workflow management"""

    async def auto_triage_issue(self, issue: Issue) -> dict:
        """Automatically triage new issues based on content analysis"""

        suggestions = {}

        # Analyze title and description for keywords
        content = f"{issue.title} {issue.description}".lower()

        # Severity detection
        if any(keyword in content for keyword in ['crash', 'error', 'exception', 'broken']):
            suggestions['severity'] = 'high'
        elif any(keyword in content for keyword in ['slow', 'performance', 'timeout']):
            suggestions['severity'] = 'medium'

        # Component detection
        component_keywords = {
            'frontend': ['ui', 'interface', 'button', 'form', 'display'],
            'backend': ['api', 'server', 'database', 'endpoint'],
            'authentication': ['login', 'auth', 'password', 'token'],
            'performance': ['slow', 'timeout', 'memory', 'cpu']
        }

        for component, keywords in component_keywords.items():
            if any(keyword in content for keyword in keywords):
                suggestions['component'] = component
                break

        # Auto-assign based on component
        assignee_mapping = {
            'frontend': 'frontend-team',
            'backend': 'backend-team',
            'authentication': 'security-team',
            'performance': 'devops-team'
        }

        if suggestions.get('component') in assignee_mapping:
            suggestions['assignee'] = assignee_mapping[suggestions['component']]

        return suggestions

    async def auto_close_stale_issues(self, project_id: str, days_threshold: int = 30):
        """Automatically close stale issues"""

        cutoff_date = datetime.now() - timedelta(days=days_threshold)

        stale_issues = await self.supabase_client.table("archon_issues").select("*").eq(
            "project_id", project_id
        ).eq("status", "resolved").lt("resolved_at", cutoff_date.isoformat()).execute()

        for issue in stale_issues.data:
            await self.close_issue(
                issue["id"],
                resolution_notes="Auto-closed due to inactivity after resolution",
                closed_by="system"
            )
```

## 📊 Analytics & Reporting

### Issue Metrics Dashboard
```tsx
export const IssueAnalytics: React.FC<{ projectId: string }> = ({ projectId }) => {
  const [metrics, setMetrics] = useState<IssueMetrics | null>(null);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  useEffect(() => {
    loadMetrics();
  }, [projectId, timeRange]);

  const loadMetrics = async () => {
    const data = await issueService.getProjectMetrics(projectId, timeRange);
    setMetrics(data);
  };

  if (!metrics) return <LoadingSpinner />;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Key Metrics Cards */}
      <MetricCard
        title="Open Issues"
        value={metrics.openIssues}
        change={metrics.openIssuesChange}
        icon={<AlertCircle className="w-5 h-5" />}
        color="blue"
      />

      <MetricCard
        title="Avg Resolution Time"
        value={`${metrics.avgResolutionHours}h`}
        change={metrics.resolutionTimeChange}
        icon={<Clock className="w-5 h-5" />}
        color="green"
      />

      <MetricCard
        title="Issues Resolved"
        value={metrics.resolvedIssues}
        change={metrics.resolvedIssuesChange}
        icon={<CheckCircle className="w-5 h-5" />}
        color="purple"
      />

      <MetricCard
        title="Critical Issues"
        value={metrics.criticalIssues}
        change={metrics.criticalIssuesChange}
        icon={<AlertTriangle className="w-5 h-5" />}
        color="red"
      />

      {/* Charts */}
      <div className="col-span-full grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Issue Trends</h3>
          <IssuesTrendChart data={metrics.trendData} />
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Issues by Component</h3>
          <ComponentBreakdownChart data={metrics.componentData} />
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Resolution Time Distribution</h3>
          <ResolutionTimeChart data={metrics.resolutionTimeData} />
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Top Contributors</h3>
          <ContributorsList data={metrics.contributorData} />
        </Card>
      </div>
    </div>
  );
};
```

This comprehensive design document now provides complete technical specifications for implementing a robust issue/bug tracker that seamlessly integrates with the existing Archon ecosystem. The design emphasizes consistency with current patterns while introducing powerful new capabilities for issue management and knowledge discovery.
