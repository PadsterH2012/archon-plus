# useStaggeredEntrance

**File Path:** `archon-ui-main/src/hooks/useStaggeredEntrance.ts`
**Last Updated:** 2025-01-22

## Purpose
React hook for creating smooth staggered entrance animations using Framer Motion with configurable delays and reanimation support.

## Props/Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| items | T[] | yes | - | Array of items to animate |
| staggerDelay | number | no | 0.15 | Delay between each item animation (in seconds) |
| forceReanimateCounter | number | no | - | Optional counter to force reanimation when it changes |

## Dependencies

### Imports
```javascript
import { useEffect, useState } from 'react';
```

### Exports
```javascript
export const useStaggeredEntrance: <T>(items: T[], staggerDelay?: number, forceReanimateCounter?: number) => {
  isVisible: boolean;
  containerVariants: object;
  itemVariants: object;
  titleVariants: object;
};
```

## Key Functions/Methods
- **Animation trigger**: Sets visibility state after component mount
- **Reanimation logic**: Resets and triggers animation when counter changes
- **Variant generation**: Creates Framer Motion variants for different animation types

## Usage Example
```javascript
import { useStaggeredEntrance } from '../hooks/useStaggeredEntrance';
import { motion } from 'framer-motion';

const MyComponent = ({ items }) => {
  const { isVisible, containerVariants, itemVariants, titleVariants } = useStaggeredEntrance(
    items,
    0.1, // 100ms delay between items
    refreshCounter // Force reanimation when this changes
  );

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate={isVisible ? "visible" : "hidden"}
    >
      <motion.h1 variants={titleVariants}>
        Title Animation
      </motion.h1>
      
      {items.map((item, index) => (
        <motion.div
          key={index}
          variants={itemVariants}
        >
          {item.content}
        </motion.div>
      ))}
    </motion.div>
  );
};
```

## State Management
- **isVisible**: Boolean state controlling animation trigger

## Side Effects
- **Mount animation**: Triggers animation after component mounts
- **Reanimation**: Resets and retriggers animation when counter changes
- **Cleanup**: Clears timeout on unmount or dependency change

## Related Files
- **Parent components:** KnowledgeBasePage, ProjectPage, MCPPage
- **Child components:** None - this is a hook
- **Shared utilities:** 
  - Framer Motion animation library

## Notes
- Generic hook supporting any item type
- Three animation variants: container, item, and title
- Configurable stagger delay for timing control
- Force reanimation capability for dynamic content
- Smooth easeOut transitions for natural feel
- 50ms reset delay prevents animation conflicts
- Y-axis and scale transforms for depth
- Compatible with Framer Motion's stagger system
- Lightweight with minimal state management

---
*Auto-generated documentation - verify accuracy before use*
