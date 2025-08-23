# Tabs Component

**File Path:** `archon-ui-main/src/components/ui/Tabs.tsx`
**Last Updated:** 2025-08-22

## Purpose
A flexible tabs component with multiple variants, sizes, and icon support. Provides navigation between different content panels with accessibility features and smooth transitions.

## Props/Parameters

### TabsProps Interface
```typescript
export interface TabsProps {
  tabs: TabItem[];
  defaultTab?: string;
  activeTab?: string;
  onTabChange?: (tabId: string) => void;
  className?: string;
  variant?: 'default' | 'pills' | 'underline';
  size?: 'sm' | 'md' | 'lg';
}

export interface TabItem {
  id: string;
  label: string;
  content: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
}
```

### Props Details
- **tabs** (TabItem[], required): Array of tab items with content
- **defaultTab** (string, optional): Default active tab ID
- **activeTab** (string, optional): Controlled active tab ID
- **onTabChange** ((tabId: string) => void, optional): Callback when tab changes
- **className** (string, optional): Additional CSS classes for tab list
- **variant** ('default' | 'pills' | 'underline', default: 'default'): Visual style variant
- **size** ('sm' | 'md' | 'lg', default: 'md'): Tab size

### TabItem Interface
- **id** (string, required): Unique tab identifier
- **label** (string, required): Tab display text
- **content** (ReactNode, required): Tab panel content
- **icon** (ReactNode, optional): Icon to display before label
- **disabled** (boolean, optional): Disable tab interaction

## Dependencies

### Imports
```typescript
import React, { useState, ReactNode } from 'react';
import { clsx } from 'clsx';
```

### Exports
```typescript
export const Tabs: React.FC<TabsProps>
export interface TabItem
export interface TabsProps
```

## Key Functions/Methods

### Tab State Management
```typescript
const [internalActiveTab, setInternalActiveTab] = useState(defaultTab || tabs[0]?.id || '');
const activeTab = controlledActiveTab !== undefined ? controlledActiveTab : internalActiveTab;
```

### Tab Click Handler
```typescript
const handleTabClick = (tabId: string) => {
  if (controlledActiveTab === undefined) {
    setInternalActiveTab(tabId);
  }
  onTabChange?.(tabId);
};
```

### Dynamic Class Generation
```typescript
const tabClasses = (tab: TabItem, isActive: boolean) => clsx(
  'flex items-center gap-2 font-medium transition-colors duration-200 cursor-pointer',
  {
    // Size variants
    'px-3 py-2 text-sm': size === 'sm',
    'px-4 py-2.5 text-base': size === 'md',
    'px-6 py-3 text-lg': size === 'lg',
    
    // Variant-specific styling
    'border-b-2 -mb-px': variant === 'default' || variant === 'underline',
    'rounded-md': variant === 'pills',
    
    // Active/inactive states per variant
    // ... detailed styling logic
  }
);
```

## Usage Example
```typescript
import { Tabs } from '@/components/ui/Tabs';
import { Settings, User, Bell, Shield } from 'lucide-react';

// Basic tabs
const basicTabs = [
  {
    id: 'overview',
    label: 'Overview',
    content: <div>Overview content here...</div>
  },
  {
    id: 'details',
    label: 'Details',
    content: <div>Details content here...</div>
  },
  {
    id: 'settings',
    label: 'Settings',
    content: <div>Settings content here...</div>
  }
];

<Tabs tabs={basicTabs} defaultTab="overview" />

// Tabs with icons
const iconTabs = [
  {
    id: 'profile',
    label: 'Profile',
    icon: <User size={16} />,
    content: <ProfileSettings />
  },
  {
    id: 'notifications',
    label: 'Notifications',
    icon: <Bell size={16} />,
    content: <NotificationSettings />
  },
  {
    id: 'security',
    label: 'Security',
    icon: <Shield size={16} />,
    content: <SecuritySettings />
  }
];

<Tabs 
  tabs={iconTabs} 
  variant="pills" 
  size="lg"
  defaultTab="profile"
/>

// Controlled tabs
const [activeTab, setActiveTab] = useState('tab1');

<Tabs 
  tabs={controlledTabs}
  activeTab={activeTab}
  onTabChange={setActiveTab}
  variant="underline"
/>

// Tabs with disabled items
const tabsWithDisabled = [
  {
    id: 'available',
    label: 'Available',
    content: <div>Available content</div>
  },
  {
    id: 'coming-soon',
    label: 'Coming Soon',
    content: <div>Coming soon content</div>,
    disabled: true
  },
  {
    id: 'beta',
    label: 'Beta Features',
    content: <div>Beta features</div>
  }
];

<Tabs tabs={tabsWithDisabled} variant="default" />

// Project management tabs
const projectTabs = [
  {
    id: 'tasks',
    label: 'Tasks',
    icon: <CheckSquare size={16} />,
    content: <TaskList />
  },
  {
    id: 'documents',
    label: 'Documents',
    icon: <FileText size={16} />,
    content: <DocumentList />
  },
  {
    id: 'team',
    label: 'Team',
    icon: <Users size={16} />,
    content: <TeamMembers />
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: <Settings size={16} />,
    content: <ProjectSettings />
  }
];

<Tabs 
  tabs={projectTabs}
  variant="pills"
  size="md"
  className="bg-gray-50 dark:bg-gray-900 p-1 rounded-lg"
/>
```

## State Management
- Supports both controlled and uncontrolled patterns
- Internal state for uncontrolled usage
- External state control via activeTab prop

## Side Effects
- Smooth color transitions on tab changes
- Content panel switching with proper ARIA attributes
- Focus management for keyboard navigation

## Visual Features

### Variant Styles

#### Default Variant
- Border bottom for tab list
- Active tab has colored bottom border
- Hover effects on inactive tabs

#### Pills Variant
- Rounded background container
- Active tab has solid background
- Compact pill-like appearance

#### Underline Variant
- Similar to default but with enhanced underline styling
- Hover effects include border changes

### Size Variants
- **Small (sm)**: Compact padding and text
- **Medium (md)**: Standard size for most use cases
- **Large (lg)**: Prominent tabs for important navigation

### Animation Features
- 200ms color transitions
- Smooth hover state changes
- Focus ring animations

## Accessibility Features
- **Tab Role**: Proper ARIA tab/tablist/tabpanel roles
- **Keyboard Navigation**: Arrow key navigation between tabs
- **Focus Management**: Proper focus indicators
- **Screen Reader Support**: Proper labeling and relationships
- **Disabled State**: Proper disabled handling

## Theme Support

### Light Mode
- Light backgrounds and borders
- Gray text for inactive tabs
- Blue accent for active states

### Dark Mode
- Dark backgrounds and borders
- Light text colors
- Consistent accent colors

## Advanced Usage

### Dynamic Tab Content
```typescript
const DynamicTabs = () => {
  const [tabs, setTabs] = useState(initialTabs);
  const [activeTab, setActiveTab] = useState('tab1');

  const addTab = () => {
    const newTab = {
      id: `tab-${Date.now()}`,
      label: `New Tab ${tabs.length + 1}`,
      content: <div>Dynamic content</div>
    };
    setTabs(prev => [...prev, newTab]);
  };

  const removeTab = (tabId: string) => {
    setTabs(prev => prev.filter(tab => tab.id !== tabId));
    if (activeTab === tabId) {
      setActiveTab(tabs[0]?.id || '');
    }
  };

  return (
    <div>
      <button onClick={addTab}>Add Tab</button>
      <Tabs 
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
    </div>
  );
};
```

### Conditional Tab Rendering
```typescript
const ConditionalTabs = ({ userRole, permissions }) => {
  const allTabs = [
    {
      id: 'overview',
      label: 'Overview',
      content: <Overview />
    },
    {
      id: 'admin',
      label: 'Admin',
      content: <AdminPanel />,
      disabled: userRole !== 'admin'
    },
    {
      id: 'settings',
      label: 'Settings',
      content: <Settings />
    }
  ];

  const visibleTabs = allTabs.filter(tab => 
    !tab.disabled || permissions.includes(tab.id)
  );

  return <Tabs tabs={visibleTabs} />;
};
```

### Tab with Loading States
```typescript
const TabWithLoading = ({ isLoading, data }) => {
  const tabs = [
    {
      id: 'data',
      label: 'Data',
      content: isLoading ? <LoadingSpinner /> : <DataTable data={data} />
    },
    {
      id: 'charts',
      label: 'Charts',
      content: isLoading ? <LoadingSpinner /> : <Charts data={data} />
    }
  ];

  return <Tabs tabs={tabs} />;
};
```

## Related Files
- **Parent components:** Pages, modals, settings panels, dashboards
- **Child components:** Tab content components, icons
- **Shared utilities:** clsx for class management, Tailwind CSS

## Notes
- Supports both controlled and uncontrolled patterns
- Flexible content system with ReactNode support
- Icon integration with proper spacing
- Disabled state handling with visual feedback
- Responsive design works on all screen sizes
- Keyboard accessible with proper ARIA support
- Smooth animations enhance user experience
- Consistent with overall design system
- Performance optimized with minimal re-renders

---
*Auto-generated documentation - verify accuracy before use*
