# ComponentsTab

**File Path:** `archon-ui-main/src/components/project-tasks/ComponentsTab.tsx`
**Last Updated:** 2025-01-22

## Purpose
Component management tab for projects providing component hierarchy visualization, dependency tracking, template management, and architectural oversight.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| project | Project | yes | - | Project object containing component data |
| className | string | no | "" | Additional CSS classes |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect } from 'react';
import { Plus, Package, AlertCircle, Settings, Layers, GitBranch, FileText } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { TemplateManagement } from './TemplateManagement';
import type { Project } from '../../types/project';
```

### Exports
```javascript
export const ComponentsTab: React.FC<ComponentsTabProps>;
```

## Key Functions/Methods
- **getStatusColor**: Returns appropriate color for component status
- **getTypeIcon**: Returns appropriate icon for component type
- **handleError**: Global error handler for template management errors

## Usage Example
```javascript
import { ComponentsTab } from '../components/project-tasks/ComponentsTab';

<ComponentsTab
  project={selectedProject}
  className="custom-styling"
/>
```

## State Management
- **selectedComponent**: Currently selected component for detail view
- **activeView**: 'hierarchy' | 'graph' - Component visualization mode
- **error**: Error message string for display
- **activeTab**: 'components' | 'templates' - Current tab selection

## Side Effects
- **Error handling**: Global error event listener for template system errors
- **Component visualization**: Renders component hierarchy and dependency graphs

## Related Files
- **Parent components:** ProjectPage
- **Child components:** 
  - TemplateManagement
  - Card, Button, Badge (UI components)
- **Shared utilities:** 
  - Project type definitions

## Notes
- Currently uses mock component data for demonstration
- Supports multiple component types: foundation, feature, integration, infrastructure
- Component status tracking: completed, in_progress, not_started, blocked
- Dependency visualization and management
- Template management integration with error handling
- Tab-based interface for components and templates
- Hierarchical and graph view modes for component visualization
- Completion gates tracking for component development phases
- Defensive programming for template management errors

---
*Auto-generated documentation - verify accuracy before use*
