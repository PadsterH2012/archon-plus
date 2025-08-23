# WorkflowAnalytics

**File Path:** `archon-ui-main/src/components/workflow/WorkflowAnalytics.tsx`
**Last Updated:** 2025-01-22

## Purpose
Comprehensive analytics dashboard for workflow performance insights including execution statistics, success rates, trends, and top-performing workflows.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| className | string | no | "" | Additional CSS classes |

## Dependencies

### Imports
```javascript
import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Clock, CheckCircle, XCircle, AlertTriangle, Activity, Users, Calendar, Zap } from 'lucide-react';
import { Card } from '../ui/Card';
```

### Exports
```javascript
export const WorkflowAnalytics: React.FC<WorkflowAnalyticsProps>;
```

## Key Functions/Methods
- **Mock data generation**: Simulates analytics data for demonstration
- **Time range filtering**: Supports 7d, 30d, 90d time ranges
- **MetricCard**: Internal component for displaying key metrics
- **TopWorkflowsTable**: Internal component for top workflows display
- **TrendsChart**: Internal component for execution trends visualization

## Usage Example
```javascript
import { WorkflowAnalytics } from '../components/workflow/WorkflowAnalytics';

<WorkflowAnalytics className="custom-analytics" />
```

## State Management
- **analytics**: AnalyticsData object containing all metrics
- **loading**: Boolean for loading state
- **timeRange**: Selected time range ('7d' | '30d' | '90d')

## Side Effects
- **Data loading**: Simulates API call to load analytics data
- **Time range updates**: Reloads data when time range changes

## Related Files
- **Parent components:** WorkflowPage
- **Child components:** 
  - MetricCard, TopWorkflowsTable, TrendsChart (internal)
  - Card (UI component)
- **Shared utilities:** None

## Notes
- Currently uses mock data for demonstration
- Comprehensive metrics including execution counts, success rates, and timing
- Top workflows ranking by execution count and success rate
- Execution trends over time with success/failure breakdown
- Time range selection for different analysis periods
- Responsive card-based layout
- Loading states with spinner animation
- Error handling for missing data
- Color-coded metrics with appropriate icons
- Ready for integration with real analytics API

---
*Auto-generated documentation - verify accuracy before use*
