# Archon Plus - Complete Documentation Index

**Generated:** 2025-08-22
**Version:** 2.0

## Overview
This documentation covers the complete Archon Plus system, including the knowledge base functionality, project management, MCP integration, workflow orchestration, and all supporting components, services, and utilities. This index now includes both the original codebase documentation and the comprehensive system documentation relocated from the docs directory.

## 📄 Pages

### Knowledge Base
- **[KnowledgeBasePage](./pages/KnowledgeBasePage.md)** - Main knowledge base management page with crawling, upload, and item management

### Project Management
- **[ProjectPage](./pages/ProjectPage.md)** - Comprehensive project lifecycle management with real-time updates and task tracking

### MCP (Model Context Protocol)
- **[MCPPage](./pages/MCPPage.md)** - MCP server dashboard with control, configuration, and IDE integration

### Workflow Management
- **[WorkflowPage](./pages/WorkflowPage.md)** - Comprehensive workflow management with creation, execution, and analytics

## 📚 Guides & Getting Started

### Core Guides
- **[Welcome to Archon](./guides/intro.md)** - Main introduction and overview of Archon's capabilities
- **[Getting Started](./guides/getting-started.md)** - Complete setup guide from prerequisites to first crawl
- **[Coding Best Practices](./guides/coding-best-practices.md)** - Development standards and patterns
- **[Code Extraction Rules](./guides/code-extraction-rules.md)** - Guidelines for code analysis and extraction

## ⚙️ Configuration & Deployment

### Configuration
- **[Configuration](./configuration/configuration.md)** - Environment variables, database setup, and service configuration
- **[Provider Combinations](./configuration/provider-combinations.md)** - Multi-provider setup and configuration
- **[Split Providers](./configuration/split-providers.md)** - Advanced provider splitting strategies
- **[Split Providers Migration](./configuration/split-providers-migration.md)** - Migration guide for provider splitting

### Deployment
- **[Deployment](./deployment/deployment.md)** - Production deployment with Docker and scaling
- **[Server Deployment](./deployment/server-deployment.md)** - Detailed server deployment procedures

## 🔌 MCP Integration

### MCP Core
- **[MCP Overview](./mcp/mcp-overview.md)** - Model Context Protocol integration overview
- **[MCP Server](./mcp/mcp-server.md)** - MCP server implementation and management
- **[MCP Tools](./mcp/mcp-tools.md)** - Available MCP tools and their usage

## 🧠 Knowledge Management

### Knowledge Base
- **[Knowledge Overview](./knowledge/knowledge-overview.md)** - Knowledge base system overview
- **[Knowledge Features](./knowledge/knowledge-features.md)** - Detailed feature documentation
- **[RAG Strategies](./knowledge/rag.md)** - Retrieval Augmented Generation configuration
- **[Crawling Configuration](./knowledge/crawling-configuration.md)** - Web crawling setup and options

## 📊 Projects & Tasks

### Project Management
- **[Projects Overview](./projects/projects-overview.md)** - Project management system overview
- **[Projects Features](./projects/projects-features.md)** - Detailed project management features

## 🤖 AI Agents

### Agent System
- **[Agents Overview](./agents/agents-overview.md)** - AI agent system architecture
- **[Agent Chat](./agents/agent-chat.md)** - Chat agent implementation
- **[Agent Document](./agents/agent-document.md)** - Document processing agents
- **[Agent RAG](./agents/agent-rag.md)** - RAG-enabled agent capabilities
- **[Agent Task](./agents/agent-task.md)** - Task management agents

## 🔄 Workflow Orchestration

### Workflow System
- **[Workflows Overview](./workflows/workflows-overview.md)** - Workflow orchestration system overview
- **[Workflows Getting Started](./workflows/workflows-getting-started.md)** - Quick start guide for workflows
- **[Workflows Designer](./workflows/workflows-designer.md)** - Visual workflow designer documentation
- **[Workflows API](./workflows/workflows-api.md)** - Workflow API reference
- **[Workflows Best Practices](./workflows/workflows-best-practices.md)** - Workflow development best practices
- **[Workflows MCP Tools](./workflows/workflows-mcp-tools.md)** - MCP tool integration in workflows
- **[Workflows Troubleshooting](./workflows/workflows-troubleshooting.md)** - Common issues and solutions

## 🖥️ User Interface

### UI Documentation
- **[UI Overview](./ui/ui.md)** - User interface architecture and design
- **[UI Components](./ui/ui-components.md)** - Reusable UI component library

## 🏗️ Server Architecture

### Server Components
- **[Server Overview](./server/server-overview.md)** - Backend architecture overview
- **[Server Services](./server/server-services.md)** - Core server services documentation
- **[Server Monitoring](./server/server-monitoring.md)** - Monitoring and observability
- **[Socket.IO Communication](./server/socketio.md)** - Real-time communication implementation
- **[Background Tasks](./server/background-tasks.md)** - Asynchronous task processing

## 📋 API Reference

### API Documentation
- **[API Reference](./api/api-reference.md)** - Complete REST API documentation with examples

## 🏛️ Architecture

### System Architecture
- **[Architecture](./architecture/architecture.md)** - Overall system architecture and design patterns

## 🧪 Testing

### Testing Strategies
- **[Testing Overview](./testing/testing.md)** - Testing framework and strategies
- **[Python Testing Strategy](./testing/testing-python-strategy.md)** - Backend testing with Python
- **[Vitest Testing Strategy](./testing/testing-vitest-strategy.md)** - Frontend testing with Vitest

## 🧩 Components

### Knowledge Base Components
- **[KnowledgeTable](./components/KnowledgeTable.md)** - Table view for knowledge items with grouping and actions
- **[KnowledgeItemCard](./components/KnowledgeItemCard.md)** - Card component for individual knowledge items with interactive features
- **[CrawlingProgressCard](./components/CrawlingProgressCard.md)** - Real-time progress tracking for crawl and upload operations
- **[KnowledgeItemSkeleton](./components/KnowledgeItemSkeleton.md)** - Loading skeleton components with shimmer animations

### Project Management Components
- **[TasksTab](./components/TasksTab.md)** - Comprehensive task management with table/board views and real-time updates

### MCP Components
- **[MCPClients](./components/MCPClients.md)** - MCP client management with connection monitoring and tool testing

### Workflow Components
- **[WorkflowBuilder](./components/WorkflowBuilder.md)** - Comprehensive workflow builder with form and visual designer
- **[WorkflowDesigner](./components/WorkflowDesigner.md)** - Visual drag-and-drop workflow designer with React Flow
- **[WorkflowExecutionDashboard](./components/WorkflowExecutionDashboard.md)** - Real-time execution monitoring with statistics and control
- **[WorkflowAnalytics](./components/WorkflowAnalytics.md)** - Performance analytics dashboard with trends and insights
- **[WorkflowScheduler](./components/WorkflowScheduler.md)** - Advanced scheduling with cron, intervals, and triggers
- **[WorkflowForm](./components/WorkflowForm.md)** - Metadata editing form with validation and parameter management
- **[RealTimeExecutionMonitor](./components/RealTimeExecutionMonitor.md)** - WebSocket-based real-time execution monitoring

### UI Components
- **[TagInput](./components/TagInput.md)** - Enhanced tag input with autocomplete and keyboard navigation

### Additional Components (Documented)
- **[DocsTab](./components/DocsTab.md)** - Document management with PRP creation and knowledge source linking
- **[ComponentsTab](./components/ComponentsTab.md)** - Component hierarchy visualization and template management
- **[TaskTableView](./components/TaskTableView.md)** - Advanced table view with drag-and-drop and inline editing
- **[TaskBoardView](./components/TaskBoardView.md)** - Kanban-style board view with multi-select operations
- **[EditTaskModal](./components/EditTaskModal.md)** - Modal for editing task details with debounced inputs
- **[EditKnowledgeItemModal](./components/EditKnowledgeItemModal.md)** - Modal for editing knowledge item metadata and group management
- **[ClientCard](./components/ClientCard.md)** - Interactive MCP client card with bioluminescent effects

### Additional Components (Completed)
- **[GroupedKnowledgeItemCard](./components/GroupedKnowledgeItemCard.md)** - Advanced card for grouped knowledge items with shuffling animations
- **[GroupCreationModal](./components/GroupCreationModal.md)** - Modal for creating knowledge item groups with batch operations
- **[ToolTestingPanel](./components/ToolTestingPanel.md)** - Interactive MCP tool testing panel with terminal interface

## 🔧 Services

### Core Services
- **[knowledgeBaseService](./services/knowledgeBaseService.md)** - Main service for knowledge base CRUD operations, crawling, and search
- **[projectService](./services/projectService.md)** - Comprehensive project management service with validation and real-time updates

### Additional Services (Documented)
- **[mcpServerService](./services/mcpServerService.md)** - MCP server lifecycle management with real-time logging
- **[crawlProgressService](./services/crawlProgressService.md)** - Real-time progress tracking via Socket.IO
- **[socketIOService](./services/socketIOService.md)** - Comprehensive WebSocket service with automatic reconnection

### Additional Services (Completed)
- **[mcpClientService](./services/mcpClientService.md)** - Universal MCP client service with tool execution and connection management
- **[workflowService](./services/workflowService.md)** - Comprehensive workflow management with execution control and MCP integration

### Additional Services (Completed)
- **[projectCreationProgressService](./services/projectCreationProgressService.md)** - Specialized streaming service for project creation progress

## 🛠️ Utilities

### Documented Hooks (Complete)
- **[useTaskSocket](./hooks/useTaskSocket.md)** - Real-time task synchronization via WebSocket
- **[useStaggeredEntrance](./hooks/useStaggeredEntrance.md)** - Staggered entrance animations with Framer Motion
- **[useCardTilt](./hooks/useCardTilt.md)** - Interactive 3D card tilt effects with mouse tracking
- **[useTerminalScroll](./hooks/useTerminalScroll.md)** - Intelligent terminal auto-scrolling with user interaction respect

## 📊 Data Models

### Knowledge Base Types
```typescript
interface KnowledgeItem {
  id: string;
  title: string;
  url: string;
  source_id: string;
  metadata: KnowledgeItemMetadata;
  created_at: string;
  updated_at: string;
  code_examples?: any[];
}

interface KnowledgeItemMetadata {
  knowledge_type?: 'technical' | 'business';
  tags?: string[];
  source_type?: 'url' | 'file';
  status?: 'active' | 'processing' | 'error';
  description?: string;
  last_scraped?: string;
  chunks_count?: number;
  word_count?: number;
  file_name?: string;
  file_type?: string;
  page_count?: number;
  update_frequency?: number;
  next_update?: string;
  group_name?: string;
  original_url?: string;
}
```

## 🔄 Workflows

### Knowledge Item Management
1. **Add Knowledge Source** → URL validation → Crawling/Upload → Progress tracking → Item creation
2. **View Knowledge Items** → Filtering → Display (Grid/Table) → Actions (Edit/Delete/Refresh)
3. **Search Knowledge** → Query processing → Results display → Item interaction

### Real-time Operations
1. **Crawl Progress** → WebSocket connection → Progress updates → Completion handling
2. **Bulk Operations** → Selection mode → Multi-item actions → Batch processing

## 🎯 Key Features

### Knowledge Management
- ✅ URL crawling with configurable depth
- ✅ Document upload (PDF, DOCX, TXT, MD)
- ✅ Real-time progress tracking
- ✅ Tagging and categorization
- ✅ Search and filtering
- ✅ Bulk operations
- ✅ Code example extraction

### Workflow Management
- ✅ Visual drag-and-drop workflow designer
- ✅ Form-based workflow builder
- ✅ MCP tool integration for workflow steps
- ✅ Real-time workflow execution and monitoring
- ✅ Workflow templates and examples
- ✅ Advanced validation and error checking

### User Experience
- ✅ Responsive grid and table views
- ✅ Interactive card animations
- ✅ Real-time WebSocket updates
- ✅ Keyboard shortcuts
- ✅ Loading states and skeletons
- ✅ Error handling and retry mechanisms

## 📝 Documentation Status

### Completed ✅ (100% COMPLETE!)

#### Codebase Documentation (40 files)
- **Pages (4/4):** KnowledgeBasePage, ProjectPage, MCPPage, WorkflowPage
- **Knowledge Base (7/7):** KnowledgeTable, KnowledgeItemCard, CrawlingProgressCard, KnowledgeItemSkeleton, EditKnowledgeItemModal, GroupedKnowledgeItemCard, GroupCreationModal
- **Project Management (6/6):** TasksTab, DocsTab, ComponentsTab, TaskTableView, TaskBoardView, EditTaskModal
- **MCP (3/3):** MCPClients, ClientCard, ToolTestingPanel
- **Workflow (7/7):** WorkflowBuilder, WorkflowDesigner, WorkflowExecutionDashboard, WorkflowAnalytics, WorkflowScheduler, WorkflowForm, RealTimeExecutionMonitor
- **UI Components (1/1):** TagInput
- **Services (8/8):** knowledgeBaseService, projectService, mcpServerService, crawlProgressService, socketIOService, mcpClientService, workflowService, projectCreationProgressService
- **Hooks (4/4):** useTaskSocket, useStaggeredEntrance, useCardTilt, useTerminalScroll

#### System Documentation (40 files)
- **Guides (4/4):** intro, getting-started, coding-best-practices, code-extraction-rules
- **Configuration (4/4):** configuration, provider-combinations, split-providers, split-providers-migration
- **Deployment (2/2):** deployment, server-deployment
- **MCP Integration (3/3):** mcp-overview, mcp-server, mcp-tools
- **Knowledge Management (4/4):** knowledge-overview, knowledge-features, rag, crawling-configuration
- **Projects & Tasks (2/2):** projects-overview, projects-features
- **AI Agents (5/5):** agents-overview, agent-chat, agent-document, agent-rag, agent-task
- **Workflow Orchestration (7/7):** workflows-overview, workflows-getting-started, workflows-designer, workflows-api, workflows-best-practices, workflows-mcp-tools, workflows-troubleshooting
- **User Interface (2/2):** ui, ui-components
- **Server Architecture (5/5):** server-overview, server-services, server-monitoring, socketio, background-tasks
- **API Reference (1/1):** api-reference
- **Architecture (1/1):** architecture
- **Testing (3/3):** testing, testing-python-strategy, testing-vitest-strategy

#### Database Documentation (6/6) ✅ **NEW!**
- **Schema & Architecture (4/4):** core-database-tables, database-schema-erd, database-models-schemas, database-services-repositories
- **Operations & Management (2/2):** database-migrations, database-operations-query-patterns

### Final Progress Summary
- **Total Codebase Documentation:** 40 files
- **Total System Documentation:** 40 files
- **Total Database Documentation:** 6 files ✅
- **Total UI Components:** 17 files ✅
- **Total PRP System:** 4 files ✅
- **Total Services Documentation:** 4 files ✅ **NEW!**
- **Grand Total:** 111 files documented
- **Remaining:** ~10 files (layouts, specialized components, utilities)
- **Completion:** ~92% COMPLETE! 🎉
- **All Major Systems:** Knowledge Base, Project Management, MCP Integration, Workflow Management, AI Agents, Server Architecture, Database Architecture, **UI Components**, **PRP System**, **Services Layer**

## 🗄️ Database Documentation

### Database Schema & Architecture
- **[Core Database Tables](./database/core-database-tables.md)** - Complete table documentation with field definitions and relationships
- **[Database Schema ERD](./database/database-schema-erd.md)** - Visual Entity Relationship Diagram with Mermaid
- **[Database Models & Schemas](./database/database-models-schemas.md)** - Pydantic models and validation rules
- **[Database Services & Repositories](./database/database-services-repositories.md)** - Data access layer and service patterns

### Database Operations & Management
- **[Database Migrations](./database/database-migrations.md)** - Migration procedures, rollback strategies, and validation
- **[Database Operations & Query Patterns](./database/database-operations-query-patterns.md)** - Vector searches, joins, aggregations, and optimization

## 🧩 Component Documentation

### UI Components (17/21 = 81% Complete)
- **[UI Components Summary](./components/ui-components-summary.md)** - Complete design system overview and component catalog
- **[Button](./components/ui-Button.md)** - Customizable buttons with variants, sizes, and neon effects
- **[Card](./components/ui-Card.md)** - Container component with accent colors and glow effects
- **[Input](./components/ui-Input.md)** - Form input with icons, labels, and focus effects
- **[Badge](./components/ui-Badge.md)** - Status and category labels with color variants
- **[Progress](./components/ui-Progress.md)** - Progress bars with animations and variants
- **[Checkbox](./components/ui-Checkbox.md)** - Animated checkbox with indeterminate state support
- **[Select](./components/ui-Select.md)** - Dropdown select with accent colors and custom arrow
- **[Toggle](./components/ui-Toggle.md)** - Switch component with icon support and CSS animations
- **[Tabs](./components/ui-Tabs.md)** - Tab navigation with variants, icons, and accessibility
- **[NeonButton](./components/ui-NeonButton.md)** - Advanced button with layered neon effects
- **[ThemeToggle](./components/ui-ThemeToggle.md)** - Dark/light mode toggle with accent colors
- **[TagInput](./components/ui-TagInput.md)** - Tag input with autocomplete and keyboard navigation
- **[DropdownMenu](./components/ui-DropdownMenu.md)** - Flexible dropdown menu with positioning
- **[PowerButton](./components/ui-PowerButton.md)** - Power button with on/off states and glow effects
- **[CollapsibleSettingsCard](./components/ui-CollapsibleSettingsCard.md)** - Expandable settings container
- **[Remaining Components](./components/ui-remaining-components.md)** - Testing and utility components overview

### PRP System Components (Complete)
- **[PRP System Overview](./components/prp-system-overview.md)** - Complete Product Requirement Prompt system architecture
- **[PRPViewer](./components/prp-PRPViewer.md)** - Main viewer component with intelligent content routing
- **[Section Components](./components/prp-section-components.md)** - 13+ specialized section components for different content types
- **[Renderers & Utilities](./components/prp-renderers-utilities.md)** - Rendering engine and utility functions

## 🔧 Services Documentation

### Service Architecture & Infrastructure
- **[Services Overview](./services/services-overview.md)** - Complete service layer architecture with 50+ services
- **[Core Infrastructure Services](./services/core-infrastructure-services.md)** - 8 foundational services (client management, task orchestration, MCP integration)
- **[Project Management Services](./services/project-management-services.md)** - 9 project lifecycle services (CRUD, workflows, progress tracking)
- **[Search & Embedding Services](./services/search-embedding-services.md)** - 10 RAG and AI services (vector search, embeddings, reranking)

## 🔗 Related Documentation
- **[API Reference](./api/api-reference.md)** - Complete REST API documentation with examples
- **[Architecture](./architecture/architecture.md)** - System architecture and design patterns
- **[Server Monitoring](./server/server-monitoring.md)** - Monitoring, logging, and observability
- **[Socket.IO Communication](./server/socketio.md)** - Real-time event specifications and implementation
- **[Testing Strategies](./testing/testing.md)** - Comprehensive testing documentation
- **[Deployment Guide](./deployment/deployment.md)** - Production deployment procedures

## 🎯 Quick Navigation

### For Developers
- Start with **[Getting Started](./guides/getting-started.md)** for initial setup
- Review **[Architecture](./architecture/architecture.md)** for system understanding
- Check **[API Reference](./api/api-reference.md)** for integration details
- Follow **[Coding Best Practices](./guides/coding-best-practices.md)** for development

### For System Administrators
- Begin with **[Configuration](./configuration/configuration.md)** for setup
- Review **[Deployment](./deployment/deployment.md)** for production deployment
- Monitor with **[Server Monitoring](./server/server-monitoring.md)**
- Troubleshoot using **[Workflows Troubleshooting](./workflows/workflows-troubleshooting.md)**

### For End Users
- Start with **[Welcome to Archon](./guides/intro.md)** for overview
- Learn **[Knowledge Management](./knowledge/knowledge-overview.md)** features
- Explore **[Project Management](./projects/projects-overview.md)** capabilities
- Discover **[Workflow Orchestration](./workflows/workflows-overview.md)** power

---
*This comprehensive index covers all Archon Plus documentation. Last updated: 2025-08-22*
