# DocsTab

**File Path:** `archon-ui-main/src/components/project-tasks/DocsTab.tsx`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive document management tab for projects providing PRP (Product Requirement Prompt) creation, markdown editing, knowledge source linking, and document versioning capabilities.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tasks | Task[] | yes | - | Array of project tasks for context |
| project | Project | yes | - | Project object containing documents and metadata |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect } from 'react';
import { Plus, X, Search, Upload, Link as LinkIcon, Check, Brain, Save, History, Eye, Edit3, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';
import { knowledgeBaseService, KnowledgeItem } from '../../services/knowledgeBaseService';
import { projectService } from '../../services/projectService';
import { useToast } from '../../contexts/ToastContext';
import { Input } from '../ui/Input';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Select } from '../ui/Select';
import { CrawlProgressData, crawlProgressService } from '../../services/crawlProgressService';
import { WebSocketState } from '../../services/socketIOService';
import { MilkdownEditor } from './MilkdownEditor';
import { VersionHistoryModal } from './VersionHistoryModal';
import { PRPViewer } from '../prp';
import { DocumentCard, NewDocumentCard } from './DocumentCard';
```

### Exports
```javascript
export const DocsTab: React.FC<DocsTabProps>;
```

## Key Functions/Methods
- **loadProjectDocuments**: Loads documents from project data
- **createDocumentFromTemplate**: Creates new document from predefined templates
- **saveDocument**: Saves document changes with version control
- **loadProjectData**: Loads project data including linked knowledge sources
- **loadKnowledgeItems**: Loads available knowledge base items for linking
- **transformToLegacyFormat**: Converts knowledge items to legacy format
- **toggleTechnicalSource/toggleBusinessSource**: Toggles knowledge source selection
- **saveTechnicalSources/saveBusinessSources**: Saves linked knowledge sources
- **handleProgressComplete/Error/Update**: Handles crawl progress events
- **handleStartCrawl**: Initiates knowledge source crawling
- **openAddSourceModal**: Opens modal for adding new knowledge sources

## Usage Example
```javascript
import { DocsTab } from '../components/project-tasks/DocsTab';

<DocsTab
  tasks={tasks}
  project={selectedProject}
/>
```

## State Management
- **documents**: Array of ProjectDoc objects
- **selectedDocument**: Currently selected document for editing
- **isEditing**: Boolean for edit mode
- **isSaving**: Boolean for save operation
- **loading**: Boolean for loading state
- **showTemplateModal**: Boolean for template selection modal
- **showVersionHistory**: Boolean for version history modal
- **viewMode**: 'beautiful' | 'markdown' - Document view mode
- **isDarkMode**: Boolean for dark mode detection
- **selectedTechnicalSources/selectedBusinessSources**: Arrays of linked knowledge source IDs
- **knowledgeItems**: Array of available knowledge base items
- **progressItems**: Array of active crawl progress items

## Side Effects
- **Dark mode detection**: Monitors system and manual dark mode changes
- **Document loading**: Loads project documents on mount
- **Knowledge source management**: Links and manages knowledge base sources
- **Real-time crawl progress**: Tracks knowledge source crawling progress
- **Version control**: Automatic document versioning on save

## Related Files
- **Parent components:** ProjectPage
- **Child components:** 
  - MilkdownEditor
  - VersionHistoryModal
  - PRPViewer
  - DocumentCard, NewDocumentCard
  - TemplateSelectionModal (internal)
  - SourceSelectionModal (internal)
  - AddKnowledgeModal (internal)
- **Shared utilities:** 
  - knowledgeBaseService
  - projectService
  - crawlProgressService
  - useToast context

## Notes
- Supports multiple document types including PRP (Product Requirement Prompt)
- Comprehensive PRP templates with structured implementation blueprints
- Real-time markdown editing with Milkdown editor
- Knowledge source linking for technical and business documentation
- Document versioning with history and restoration
- Beautiful/markdown view modes for different editing preferences
- Dark mode support with automatic detection
- Progress tracking for knowledge source crawling
- Template-based document creation for consistency
- Integration with knowledge base for source management

---
*Auto-generated documentation - verify accuracy before use*
