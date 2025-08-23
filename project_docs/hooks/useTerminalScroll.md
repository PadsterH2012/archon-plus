# useTerminalScroll

**File Path:** `archon-ui-main/src/hooks/useTerminalScroll.ts`
**Last Updated:** 2025-01-22

## Purpose
React hook for intelligent terminal-style auto-scrolling that automatically scrolls to bottom when content changes but respects user scroll position.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| dependencies | T[] | yes | - | Array of dependencies that trigger auto-scroll |
| enabled | boolean | no | true | Flag to enable/disable auto-scrolling |

## Dependencies

### Imports
```javascript
import { useEffect, useRef, useState } from 'react';
```

### Exports
```javascript
export const useTerminalScroll: <T = any>(dependencies: T[], enabled?: boolean) => React.RefObject<HTMLDivElement>;
```

## Key Functions/Methods
- **isAtBottom**: Checks if user is at bottom of scroll container (with 50px threshold)
- **handleScroll**: Handles user scroll events and manages auto-scroll state
- **Auto-scroll effect**: Automatically scrolls to bottom when dependencies change
- **User scroll detection**: Detects when user manually scrolls away from bottom

## Usage Example
```javascript
import { useTerminalScroll } from '../hooks/useTerminalScroll';

const TerminalComponent = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  
  // Auto-scroll when logs change, but only if enabled and user hasn't scrolled up
  const terminalRef = useTerminalScroll([logs], isConnected);

  return (
    <div
      ref={terminalRef}
      className="terminal-container overflow-y-auto h-64"
    >
      {logs.map((log, index) => (
        <div key={index} className="terminal-line">
          {log}
        </div>
      ))}
    </div>
  );
};
```

## State Management
- **isUserScrolling**: Boolean indicating if user has manually scrolled away from bottom
- **scrollTimeoutRef**: Ref to timeout for re-enabling auto-scroll
- **scrollContainerRef**: Ref to the scrollable container element

## Side Effects
- **Scroll event listener**: Monitors user scroll behavior
- **Auto-scroll trigger**: Scrolls to bottom when dependencies change
- **User scroll detection**: Temporarily disables auto-scroll when user scrolls up
- **Re-enable auto-scroll**: Re-enables auto-scroll when user returns to bottom
- **Cleanup**: Removes event listeners and clears timeouts on unmount

## Related Files
- **Parent components:** CrawlingProgressCard, ToolTestingPanel, MCPPage
- **Child components:** None - this is a hook
- **Shared utilities:** None

## Notes
- Intelligent auto-scroll that respects user interaction
- 50px threshold for "at bottom" detection to handle minor scroll variations
- Uses requestAnimationFrame for smooth scrolling performance
- Timeout-based re-enabling of auto-scroll when user returns to bottom
- Generic type support for any dependency array
- Optional enable/disable flag for conditional scrolling
- Prevents scroll conflicts during user interaction
- Automatic cleanup of event listeners and timeouts
- Optimized for terminal-style interfaces with frequent content updates

---
*Auto-generated documentation - verify accuracy before use*
