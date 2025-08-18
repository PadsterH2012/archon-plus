import React, { useState, useRef, useEffect, ReactNode } from 'react';
import { clsx } from 'clsx';

export interface DropdownMenuItem {
  id: string;
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'default' | 'danger';
}

export interface DropdownMenuProps {
  trigger: ReactNode;
  items: DropdownMenuItem[];
  align?: 'left' | 'right';
  className?: string;
}

/**
 * DropdownMenu Component
 * 
 * A flexible dropdown menu component with customizable items and positioning
 */
export const DropdownMenu: React.FC<DropdownMenuProps> = ({
  trigger,
  items,
  align = 'right',
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  const handleItemClick = (item: DropdownMenuItem) => {
    if (!item.disabled) {
      item.onClick();
      setIsOpen(false);
    }
  };

  const menuClasses = clsx(
    'absolute z-50 mt-2 w-48 rounded-md bg-white dark:bg-gray-800 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none',
    {
      'right-0': align === 'right',
      'left-0': align === 'left',
    }
  );

  const itemClasses = (item: DropdownMenuItem) => clsx(
    'flex items-center gap-2 px-4 py-2 text-sm cursor-pointer transition-colors',
    {
      'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700': 
        item.variant !== 'danger' && !item.disabled,
      'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20': 
        item.variant === 'danger' && !item.disabled,
      'text-gray-400 dark:text-gray-600 cursor-not-allowed': item.disabled,
    }
  );

  return (
    <div className={clsx('relative inline-block text-left', className)} ref={dropdownRef}>
      <div onClick={() => setIsOpen(!isOpen)}>
        {trigger}
      </div>

      {isOpen && (
        <div className={menuClasses}>
          <div className="py-1">
            {items.map((item) => (
              <div
                key={item.id}
                className={itemClasses(item)}
                onClick={() => handleItemClick(item)}
              >
                {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
