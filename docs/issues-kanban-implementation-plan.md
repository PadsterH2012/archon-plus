# Issues Kanban Board Implementation Plan

## 🎯 **Project Overview**

**Objective**: Add an "Issues" tab to the Archon project page with a Kanban board layout, mirroring the existing Tasks tab functionality.

**Approach**: Use the existing TasksTab components as templates to minimize development time and ensure consistency.

**Timeline**: 2-8 hours depending on feature scope

---

## 📋 **Current State Analysis**

### **✅ Available Foundation**
- **Tasks Tab**: Fully functional with table and board views
- **Kanban Components**: `TaskBoardView.tsx` with drag-and-drop
- **Issue Management Backend**: Complete PostgreSQL integration with MCP tools
- **UI Components**: Cards, columns, modals, state management patterns
- **Project Page Structure**: Tab system ready for new tab addition

### **🔧 Available MCP Tools**
- `query_issues_by_project_archon-dev` - Get issues by project
- `update_issue_status_archon-dev` - Update issue status with comments
- `get_issue_history_archon-dev` - Get complete issue history
- `create_issue_from_task_archon-dev` - Create new issues
- `sync_task_to_issue_archon-dev` - Bidirectional sync

---

## 🚀 **Implementation Phases**

### **Phase 1: Basic Issues Kanban (2-3 hours) - RECOMMENDED START**

#### **Scope**
- Read-only kanban board with issue status columns
- Basic issue cards with key information
- Priority color coding
- Project filtering

#### **Deliverables**
- `IssuesTab.tsx` - Main issues tab component
- `IssueBoardView.tsx` - Kanban board layout
- `IssueCard.tsx` - Individual issue card component
- Updated `ProjectPage.tsx` with issues tab

#### **Technical Tasks**
1. **Copy & Rename Components (30 min)**
   - Copy `TasksTab.tsx` → `IssuesTab.tsx`
   - Copy `TaskBoardView.tsx` → `IssueBoardView.tsx`
   - Copy task card components → issue card components

2. **Create Issue Data Types (30 min)**
   ```typescript
   interface Issue {
     issue_key: string;        // ARCH-123
     title: string;
     status: 'open' | 'in_progress' | 'testing' | 'closed' | 'reopened';
     priority: 'critical' | 'high' | 'medium' | 'low';
     severity: 'critical' | 'major' | 'minor' | 'trivial';
     assignee_username: string;
     project_name: string;
     task_id?: string;
     created_date: string;
     updated_date: string;
   }
   ```

3. **Update API Integration (45 min)**
   - Replace task API calls with issue MCP tools
   - Implement `loadIssues()` using `query_issues_by_project`
   - Add error handling and loading states

4. **Update UI Components (45 min)**
   - Change column definitions to issue statuses
   - Update card content for issue-specific fields
   - Add priority color coding
   - Update styling and layout

5. **Add to Project Page (15 min)**
   - Add "Issues" tab to tab list
   - Add tab content with loading/error states
   - Test basic functionality

#### **Success Criteria**
- ✅ Issues tab appears in project page
- ✅ Kanban board shows issues in correct status columns
- ✅ Issue cards display key information clearly
- ✅ Priority color coding works
- ✅ Loading and error states function properly

---

### **Phase 2: Interactive Kanban (4-5 hours total)**

#### **Additional Scope**
- Drag-and-drop status updates
- Click to view issue history
- Issue creation from kanban
- Enhanced filtering options

#### **Technical Tasks**
1. **Implement Drag-and-Drop (2 hours)**
   - Add drag-and-drop handlers using existing DnD infrastructure
   - Integrate with `update_issue_status` MCP tool
   - Add optimistic UI updates
   - Handle drag validation and error states

2. **Add Issue History Integration (1 hour)**
   - Create issue detail modal/sidebar
   - Integrate `get_issue_history` MCP tool
   - Display complete timeline and comments
   - Add edit capabilities

3. **Issue Creation (1-2 hours)**
   - Add "Create Issue" button/modal
   - Form for new issue creation
   - Integration with `create_issue_from_task` if applicable
   - Validation and error handling

#### **Success Criteria**
- ✅ Drag-and-drop updates issue status in database
- ✅ Issue history accessible from cards
- ✅ New issues can be created from kanban
- ✅ Real-time updates reflect changes

---

### **Phase 3: Advanced Features (6-8 hours total)**

#### **Additional Scope**
- Real-time updates via WebSocket
- Advanced filtering and search
- Bulk operations
- Performance optimization
- Issue-task linking visualization

#### **Technical Tasks**
1. **Real-time Updates (2-3 hours)**
   - WebSocket integration for live updates
   - Optimistic UI with conflict resolution
   - Multi-user collaboration indicators

2. **Advanced Filtering (2 hours)**
   - Filter by priority, assignee, date range
   - Search functionality
   - Saved filter presets

3. **Bulk Operations (2 hours)**
   - Multi-select functionality
   - Bulk status updates
   - Bulk assignment changes

4. **Performance Optimization (1-2 hours)**
   - Virtual scrolling for large issue lists
   - Pagination and lazy loading
   - Caching strategies

---

## 🛠️ **Technical Implementation Details**

### **File Structure**
```
archon-ui-main/src/components/
├── project-tasks/
│   ├── IssuesTab.tsx           # Main issues tab (copy of TasksTab)
│   ├── IssueBoardView.tsx      # Kanban board (copy of TaskBoardView)
│   ├── IssueTableView.tsx      # Table view (copy of TaskTableView)
│   ├── IssueCard.tsx           # Issue card component
│   └── IssueModal.tsx          # Issue detail/edit modal
└── ui/
    └── (existing components)
```

### **Data Flow**
```
ProjectPage.tsx
    ↓
IssuesTab.tsx (state management)
    ↓
IssueBoardView.tsx (layout)
    ↓
IssueCard.tsx (individual issues)
    ↓
MCP Tools (query_issues_by_project, update_issue_status)
    ↓
PostgreSQL Issues Database
```

### **Status Column Mapping**
```typescript
const issueColumns = [
  { id: 'open', title: 'Open', color: 'blue', count: 0 },
  { id: 'in_progress', title: 'In Progress', color: 'yellow', count: 0 },
  { id: 'testing', title: 'Testing', color: 'purple', count: 0 },
  { id: 'closed', title: 'Closed', color: 'green', count: 0 },
  { id: 'reopened', title: 'Reopened', color: 'orange', count: 0 }
];
```

### **Priority Color Scheme**
```css
.priority-critical { background: #ef4444; color: white; }
.priority-high     { background: #f97316; color: white; }
.priority-medium   { background: #eab308; color: black; }
.priority-low      { background: #22c55e; color: white; }
```

---

## 📊 **Risk Assessment**

### **Low Risk ✅**
- Using existing components as templates
- Proven UI patterns and state management
- Backend MCP tools already working
- No breaking changes to existing functionality

### **Medium Risk ⚠️**
- Drag-and-drop integration complexity
- Real-time update synchronization
- Performance with large issue lists

### **Mitigation Strategies**
- Start with Phase 1 (read-only) to validate approach
- Incremental development with testing at each phase
- Fallback to table view if kanban performance issues
- Use existing error handling patterns

---

## 🎯 **Success Metrics**

### **Phase 1 Success**
- Issues tab loads without errors
- All project issues display correctly
- Status columns organize issues properly
- Priority colors are clearly visible
- User can navigate between table/board views

### **Phase 2 Success**
- Drag-and-drop updates database correctly
- Issue history accessible and complete
- New issues can be created successfully
- UI remains responsive during operations

### **Phase 3 Success**
- Real-time updates work across multiple users
- Advanced filtering improves usability
- Performance remains good with 100+ issues
- Integration with task system is seamless

---

## 📅 **Recommended Timeline**

**Week 1**: Phase 1 Implementation (2-3 hours)
- Focus on basic functionality and validation
- Get user feedback on layout and usability

**Week 2**: Phase 2 Implementation (4-5 hours)
- Add interactivity based on Phase 1 feedback
- Test with real project data

**Week 3**: Phase 3 Implementation (6-8 hours)
- Advanced features based on user needs
- Performance optimization and polish

**Total Estimated Time**: 12-16 hours across 3 weeks

---

## 🚀 **Getting Started**

### **Prerequisites**
- Archon development environment set up
- Access to archon-ui-main codebase
- PostgreSQL issues database accessible
- MCP tools deployed and tested

### **First Steps**
1. Create feature branch: `git checkout -b feature/issues-kanban`
2. Copy TasksTab components to IssuesTab equivalents
3. Update data types and API calls
4. Test basic functionality
5. Iterate based on feedback

**Ready to begin Phase 1 implementation!** 🎯
