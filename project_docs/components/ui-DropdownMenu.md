# DropdownMenu Component

**File Path:** `archon-ui-main/src/components/ui/DropdownMenu.tsx`
**Last Updated:** 2025-08-22

## Purpose
A flexible dropdown menu component with customizable items, positioning, and click-outside handling. Provides context menus, action menus, and navigation dropdowns with accessibility features.

## Props/Parameters

### DropdownMenuProps Interface
```typescript
export interface DropdownMenuProps {
  trigger: ReactNode;
  items: DropdownMenuItem[];
  align?: 'left' | 'right';
  className?: string;
}

export interface DropdownMenuItem {
  id: string;
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'default' | 'danger';
}
```

### Props Details
- **trigger** (ReactNode, required): Element that triggers the dropdown
- **items** (DropdownMenuItem[], required): Array of menu items
- **align** ('left' | 'right', default: 'right'): Dropdown alignment
- **className** (string, default: ''): Additional CSS classes

### DropdownMenuItem Details
- **id** (string, required): Unique item identifier
- **label** (string, required): Display text for the item
- **icon** (ReactNode, optional): Icon to display before label
- **onClick** (() => void, required): Click handler function
- **disabled** (boolean, default: false): Disable item interaction
- **variant** ('default' | 'danger', default: 'default'): Visual style variant

## Dependencies

### Imports
```typescript
import React, { useState, useRef, useEffect, ReactNode } from 'react';
import { clsx } from 'clsx';
```

### Exports
```typescript
export const DropdownMenu: React.FC<DropdownMenuProps>
export interface DropdownMenuItem
export interface DropdownMenuProps
```

## Key Functions/Methods

### State Management
```typescript
const [isOpen, setIsOpen] = useState(false);
const dropdownRef = useRef<HTMLDivElement>(null);
```

### Click Outside Handler
```typescript
useEffect(() => {
  const handleClickOutside = (event: MouseEvent) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
      setIsOpen(false);
    }
  };

  if (isOpen) {
    document.addEventListener('mousedown', handleClickOutside);
  }

  return () => {
    document.removeEventListener('mousedown', handleClickOutside);
  };
}, [isOpen]);
```

### Item Click Handler
```typescript
const handleItemClick = (item: DropdownMenuItem) => {
  if (!item.disabled) {
    item.onClick();
    setIsOpen(false);
  }
};
```

## Usage Example
```typescript
import { DropdownMenu } from '@/components/ui/DropdownMenu';
import { MoreVertical, Edit, Trash, Copy, Share } from 'lucide-react';

// Basic dropdown menu
const basicItems = [
  {
    id: 'edit',
    label: 'Edit',
    icon: <Edit size={16} />,
    onClick: () => handleEdit()
  },
  {
    id: 'copy',
    label: 'Copy',
    icon: <Copy size={16} />,
    onClick: () => handleCopy()
  },
  {
    id: 'delete',
    label: 'Delete',
    icon: <Trash size={16} />,
    onClick: () => handleDelete(),
    variant: 'danger'
  }
];

<DropdownMenu 
  trigger={<MoreVertical size={20} />}
  items={basicItems}
/>

// User profile dropdown
const profileItems = [
  {
    id: 'profile',
    label: 'View Profile',
    icon: <User size={16} />,
    onClick: () => navigate('/profile')
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: <Settings size={16} />,
    onClick: () => navigate('/settings')
  },
  {
    id: 'logout',
    label: 'Logout',
    icon: <LogOut size={16} />,
    onClick: () => handleLogout(),
    variant: 'danger'
  }
];

<DropdownMenu 
  trigger={
    <div className="flex items-center space-x-2 cursor-pointer">
      <Avatar src={user.avatar} />
      <ChevronDown size={16} />
    </div>
  }
  items={profileItems}
  align="right"
/>

// Action menu with disabled items
const actionItems = [
  {
    id: 'share',
    label: 'Share',
    icon: <Share size={16} />,
    onClick: () => handleShare()
  },
  {
    id: 'export',
    label: 'Export',
    icon: <Download size={16} />,
    onClick: () => handleExport(),
    disabled: !hasExportPermission
  },
  {
    id: 'archive',
    label: 'Archive',
    icon: <Archive size={16} />,
    onClick: () => handleArchive()
  }
];

<DropdownMenu 
  trigger={<Button variant="outline">Actions</Button>}
  items={actionItems}
  align="left"
/>

// Context menu for table rows
const TableRow = ({ item }) => {
  const contextItems = [
    {
      id: 'view',
      label: 'View Details',
      icon: <Eye size={16} />,
      onClick: () => viewItem(item.id)
    },
    {
      id: 'edit',
      label: 'Edit',
      icon: <Edit size={16} />,
      onClick: () => editItem(item.id),
      disabled: !item.canEdit
    },
    {
      id: 'duplicate',
      label: 'Duplicate',
      icon: <Copy size={16} />,
      onClick: () => duplicateItem(item.id)
    },
    {
      id: 'delete',
      label: 'Delete',
      icon: <Trash size={16} />,
      onClick: () => deleteItem(item.id),
      variant: 'danger',
      disabled: !item.canDelete
    }
  ];

  return (
    <tr>
      <td>{item.name}</td>
      <td>{item.status}</td>
      <td>
        <DropdownMenu 
          trigger={<MoreVertical size={16} className="cursor-pointer" />}
          items={contextItems}
        />
      </td>
    </tr>
  );
};

// Navigation dropdown
const navItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <Home size={16} />,
    onClick: () => navigate('/dashboard')
  },
  {
    id: 'projects',
    label: 'Projects',
    icon: <Folder size={16} />,
    onClick: () => navigate('/projects')
  },
  {
    id: 'tasks',
    label: 'Tasks',
    icon: <CheckSquare size={16} />,
    onClick: () => navigate('/tasks')
  }
];

<DropdownMenu 
  trigger={
    <Button variant="ghost">
      Menu <ChevronDown size={16} className="ml-1" />
    </Button>
  }
  items={navItems}
  align="left"
/>
```

## State Management
- Internal state for open/closed status
- Click outside detection for auto-close
- No external state dependencies

## Side Effects
- Document event listeners for click outside
- Automatic cleanup on unmount
- Menu positioning based on alignment

## Visual Features

### Menu Positioning
- **Right Alignment**: Menu appears to the right of trigger (default)
- **Left Alignment**: Menu appears to the left of trigger
- **Absolute Positioning**: Positioned relative to trigger element

### Item Styling
- **Default Variant**: Standard menu item styling
- **Danger Variant**: Red text for destructive actions
- **Disabled State**: Grayed out with no interaction
- **Hover Effects**: Background color changes on hover

### Menu Container
- **Backdrop Blur**: Glassmorphism effect
- **Shadow**: Elevated appearance
- **Border**: Subtle border for definition
- **Rounded Corners**: Consistent with design system

## Accessibility Features
- **Keyboard Navigation**: Arrow keys for navigation (if implemented)
- **Focus Management**: Proper focus handling
- **ARIA Attributes**: Menu and menuitem roles
- **Screen Reader Support**: Accessible labels and structure

## Theme Support

### Light Mode
- White/light background
- Gray borders and text
- Subtle shadows

### Dark Mode
- Dark background with transparency
- Light text colors
- Enhanced shadows for depth

## Advanced Usage

### Dynamic Menu Items
```typescript
const DynamicDropdown = ({ user, permissions }) => {
  const items = [
    {
      id: 'profile',
      label: 'Profile',
      icon: <User size={16} />,
      onClick: () => navigate('/profile')
    }
  ];

  // Add admin items if user has permission
  if (permissions.includes('admin')) {
    items.push({
      id: 'admin',
      label: 'Admin Panel',
      icon: <Shield size={16} />,
      onClick: () => navigate('/admin')
    });
  }

  // Add delete option if user owns the item
  if (user.canDelete) {
    items.push({
      id: 'delete',
      label: 'Delete',
      icon: <Trash size={16} />,
      onClick: () => handleDelete(),
      variant: 'danger'
    });
  }

  return (
    <DropdownMenu 
      trigger={<MoreVertical size={20} />}
      items={items}
    />
  );
};
```

### Nested Menus (Conceptual)
```typescript
// For future enhancement - nested menu support
const NestedDropdown = () => {
  const items = [
    {
      id: 'export',
      label: 'Export',
      icon: <Download size={16} />,
      submenu: [
        { id: 'pdf', label: 'PDF', onClick: () => exportPDF() },
        { id: 'csv', label: 'CSV', onClick: () => exportCSV() },
        { id: 'json', label: 'JSON', onClick: () => exportJSON() }
      ]
    }
  ];
  
  // Implementation would require additional logic
};
```

### Confirmation Integration
```typescript
const ConfirmationDropdown = () => {
  const [showConfirm, setShowConfirm] = useState(false);

  const items = [
    {
      id: 'edit',
      label: 'Edit',
      icon: <Edit size={16} />,
      onClick: () => handleEdit()
    },
    {
      id: 'delete',
      label: 'Delete',
      icon: <Trash size={16} />,
      onClick: () => setShowConfirm(true),
      variant: 'danger'
    }
  ];

  return (
    <>
      <DropdownMenu 
        trigger={<MoreVertical size={20} />}
        items={items}
      />
      
      {showConfirm && (
        <ConfirmDialog 
          onConfirm={handleDelete}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </>
  );
};
```

## Related Files
- **Parent components:** Tables, cards, navigation, toolbars
- **Child components:** Icons from lucide-react, buttons, avatars
- **Shared utilities:** clsx for class management, Tailwind CSS

## Notes
- Automatic click-outside detection for UX
- Flexible trigger system accepts any ReactNode
- Icon support for visual clarity
- Disabled state handling with visual feedback
- Danger variant for destructive actions
- Consistent with overall design system
- Performance optimized with proper cleanup
- Extensible for future enhancements

---
*Auto-generated documentation - verify accuracy before use*
