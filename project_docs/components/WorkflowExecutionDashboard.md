# WorkflowExecutionDashboard

**File Path:** `archon-ui-main/src/components/workflow/WorkflowExecutionDashboard.tsx`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive dashboard for monitoring all workflow executions with real-time updates, execution statistics, filtering capabilities, and execution control actions.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| executions | WorkflowExecution[] | no | [] | Initial array of workflow executions |
| isLoading | boolean | no | false | External loading state |
| onExecutionSelect | (execution: WorkflowExecution) => void | no | - | Callback when execution is selected |
| onExecutionCancel | (executionId: string) => void | no | - | Callback when execution is cancelled |
| onExecutionPause | (executionId: string) => void | no | - | Callback when execution is paused |
| onExecutionResume | (executionId: string) => void | no | - | Callback when execution is resumed |
| onRefresh | () => void | no | - | Callback when data is refreshed |
| autoRefresh | boolean | no | true | Whether to auto-refresh execution data |
| refreshInterval | number | no | 10000 | Auto-refresh interval in milliseconds |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect, useCallback } from 'react';
import { Activity, RefreshCw, Filter, Search, Play, Pause, Square, Eye, Clock, CheckCircle, XCircle, AlertCircle, User, Calendar, TrendingUp, BarChart3 } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { LoadingSpinner } from '../animations/Animations';
import { useToast } from '../../contexts/ToastContext';
import { workflowService } from '../../services/workflowService';
import { ExecutionDashboardProps, WorkflowExecution, WorkflowExecutionStatus, ExecutionFilters } from './types/workflow.types';
```

### Exports
```javascript
export const WorkflowExecutionDashboard: React.FC<ExecutionDashboardProps>;
```

## Key Functions/Methods
- **loadExecutions**: Loads executions from API and calculates statistics
- **handleExecutionAction**: Handles execution control actions (cancel, pause, resume)
- **filteredExecutions**: Filters executions based on search query
- **getStatusInfo**: Returns status information with colors and icons
- **formatExecutionDuration**: Formats execution duration for display
- **StatsCard**: Internal component for displaying execution statistics
- **ExecutionCard**: Internal component for individual execution display

## Usage Example
```javascript
import { WorkflowExecutionDashboard } from '../components/workflow/WorkflowExecutionDashboard';

<WorkflowExecutionDashboard
  executions={executions}
  onExecutionSelect={handleSelectExecution}
  onExecutionCancel={handleCancelExecution}
  onExecutionPause={handlePauseExecution}
  onExecutionResume={handleResumeExecution}
  onRefresh={handleRefreshData}
  autoRefresh={true}
  refreshInterval={5000}
/>
```

## State Management
- **executions**: Array of workflow executions
- **isLoading**: Boolean for loading state
- **filters**: ExecutionFilters object for filtering
- **searchQuery**: String for search functionality
- **showFilters**: Boolean for filter panel visibility
- **selectedExecution**: Currently selected execution
- **stats**: Execution statistics (total, running, completed, failed, pending)

## Side Effects
- **Auto-refresh**: Automatically refreshes execution data at specified intervals
- **Real-time updates**: Updates execution status and progress
- **Statistics calculation**: Calculates and displays execution statistics
- **Search filtering**: Filters executions based on search criteria

## Related Files
- **Parent components:** WorkflowPage
- **Child components:** 
  - StatsCard, ExecutionCard (internal)
  - Button, Input, Card, Badge, Progress (UI components)
  - LoadingSpinner
- **Shared utilities:** 
  - workflowService
  - useToast context
  - WorkflowExecution types

## Notes
- Real-time execution monitoring with auto-refresh
- Comprehensive execution statistics dashboard
- Search and filtering capabilities
- Execution control actions (cancel, pause, resume)
- Status-based color coding and icons
- Progress tracking for running executions
- Duration formatting and display
- Responsive design with card-based layout
- Error handling with toast notifications
- Configurable refresh intervals

---
*Auto-generated documentation - verify accuracy before use*
