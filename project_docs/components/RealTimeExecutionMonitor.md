# RealTimeExecutionMonitor

**File Path:** `archon-ui-main/src/components/workflow/RealTimeExecutionMonitor.tsx`
**Last Updated:** 2025-01-22

## Purpose
Enhanced real-time monitoring component with WebSocket integration providing live workflow execution updates, streaming logs, performance metrics, and execution control.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| executionId | string | yes | - | ID of the workflow execution to monitor |
| onCancel | (executionId: string) => void | no | - | Callback when execution is cancelled |
| onPause | (executionId: string) => void | no | - | Callback when execution is paused |
| onResume | (executionId: string) => void | no | - | Callback when execution is resumed |
| autoScroll | boolean | no | true | Whether to auto-scroll logs |
| showMetrics | boolean | no | true | Whether to show performance metrics |
| showLogs | boolean | no | true | Whether to show execution logs |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Wifi, WifiOff, RefreshCw, Pause, Play, Square, AlertTriangle, TrendingUp, Clock, Zap, Eye, EyeOff, Download, Filter, Search } from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Progress } from '../ui/Progress';
import { LoadingSpinner } from '../animations/Animations';
import { useToast } from '../../contexts/ToastContext';
import { useWorkflowMonitoring } from '../../hooks/useWorkflowMonitoring';
import { workflowService } from '../../services/workflowService';
import { WorkflowExecution, StepExecution, ExecutionLogEntry, WorkflowExecutionStatus, StepExecutionStatus } from './types/workflow.types';
```

### Exports
```javascript
export const RealTimeExecutionMonitor: React.FC<RealTimeExecutionMonitorProps>;
```

## Key Functions/Methods
- **useWorkflowMonitoring**: Custom hook for real-time monitoring with WebSocket
- **calculateMetrics**: Calculates performance metrics from execution data
- **handleExecutionControl**: Handles execution control actions (cancel, pause, resume)
- **filterLogs**: Filters logs based on level and search criteria
- **downloadLogs**: Downloads execution logs as file
- **MetricsCard**: Internal component for displaying performance metrics
- **LogEntry**: Internal component for individual log entries
- **StepProgressCard**: Internal component for step execution progress

## Usage Example
```javascript
import { RealTimeExecutionMonitor } from '../components/workflow/RealTimeExecutionMonitor';

<RealTimeExecutionMonitor
  executionId="exec-123"
  onCancel={handleCancelExecution}
  onPause={handlePauseExecution}
  onResume={handleResumeExecution}
  autoScroll={true}
  showMetrics={true}
  showLogs={true}
/>
```

## State Management
- **monitoringState**: Real-time monitoring state from useWorkflowMonitoring hook
- **isLoading**: Boolean for loading state
- **showAllLogs**: Boolean for log display mode
- **logFilter**: Log level filter ('all' | 'error' | 'warning' | 'info')
- **logSearch**: String for log search functionality
- **metrics**: Performance metrics object

## Side Effects
- **Real-time monitoring**: WebSocket connection for live updates
- **Metrics calculation**: Calculates performance metrics from execution data
- **Log filtering**: Filters and searches through execution logs
- **Auto-scroll**: Automatically scrolls logs to bottom
- **Connection status**: Monitors WebSocket connection status

## Related Files
- **Parent components:** WorkflowExecutionDashboard, WorkflowPage
- **Child components:** 
  - MetricsCard, LogEntry, StepProgressCard (internal)
  - Button, Card, Badge, Progress, LoadingSpinner (UI components)
- **Shared utilities:** 
  - useWorkflowMonitoring hook
  - workflowService
  - useToast context

## Notes
- Real-time WebSocket integration for live updates
- Comprehensive performance metrics calculation
- Log filtering and search capabilities
- Execution control actions (cancel, pause, resume)
- Auto-scroll functionality for logs
- Connection status monitoring with reconnection
- Downloadable execution logs
- Step-by-step progress tracking
- Error rate and performance analytics
- Responsive design with collapsible sections
- Dark mode support with proper theming

---
*Auto-generated documentation - verify accuracy before use*
