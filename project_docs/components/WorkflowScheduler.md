# WorkflowScheduler

**File Path:** `archon-ui-main/src/components/workflow/WorkflowScheduler.tsx`
**Last Updated:** 2025-01-22

## Purpose
Advanced workflow scheduling interface supporting multiple trigger types including cron expressions, intervals, webhooks, and event-based triggers with comprehensive schedule management.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| className | string | no | "" | Additional CSS classes |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect } from 'react';
import { Clock, Calendar, Play, Pause, Trash2, Plus, Edit, AlertCircle, CheckCircle, Zap, GitBranch } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
```

### Exports
```javascript
export const WorkflowScheduler: React.FC<WorkflowSchedulerProps>;
```

## Key Functions/Methods
- **getScheduleTypeInfo**: Returns schedule type information with icons and colors
- **formatCronExpression**: Formats cron expressions into human-readable text
- **formatNextExecution**: Formats next execution time for display
- **handleToggleSchedule**: Toggles schedule enabled/disabled state
- **handleEditSchedule**: Opens schedule editing interface
- **handleDeleteSchedule**: Deletes scheduled workflow
- **ScheduleCard**: Internal component for individual schedule display

## Usage Example
```javascript
import { WorkflowScheduler } from '../components/workflow/WorkflowScheduler';

<WorkflowScheduler className="custom-scheduler" />
```

## State Management
- **schedules**: Array of ScheduledWorkflow objects
- **loading**: Boolean for loading state
- **showCreateForm**: Boolean for create form visibility

## Side Effects
- **Mock data loading**: Simulates API call to load scheduled workflows
- **Schedule management**: Handles schedule CRUD operations

## Related Files
- **Parent components:** WorkflowPage
- **Child components:** 
  - ScheduleCard (internal)
  - Card, Button, Badge (UI components)
- **Shared utilities:** None

## Notes
- Supports multiple schedule types: cron, interval, webhook, event
- Cron expression support with human-readable formatting
- Interval-based scheduling with minute precision
- Webhook triggers for external system integration
- Event-based triggers for reactive workflows
- Schedule enable/disable functionality
- Execution count tracking and history
- Next execution time calculation and display
- Color-coded schedule types with appropriate icons
- Comprehensive schedule management interface
- Mock data implementation ready for API integration

---
*Auto-generated documentation - verify accuracy before use*
