import React, { useState, ReactNode } from 'react';
import { clsx } from 'clsx';

export interface TabItem {
  id: string;
  label: string;
  content: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
}

export interface TabsProps {
  tabs: TabItem[];
  defaultTab?: string;
  activeTab?: string;
  onTabChange?: (tabId: string) => void;
  className?: string;
  variant?: 'default' | 'pills' | 'underline';
  size?: 'sm' | 'md' | 'lg';
}

/**
 * Tabs Component
 * 
 * A flexible tabs component with multiple variants and sizes
 */
export const Tabs: React.FC<TabsProps> = ({
  tabs,
  defaultTab,
  activeTab: controlledActiveTab,
  onTabChange,
  className = '',
  variant = 'default',
  size = 'md'
}) => {
  const [internalActiveTab, setInternalActiveTab] = useState(defaultTab || tabs[0]?.id || '');
  
  const activeTab = controlledActiveTab !== undefined ? controlledActiveTab : internalActiveTab;
  
  const handleTabClick = (tabId: string) => {
    if (controlledActiveTab === undefined) {
      setInternalActiveTab(tabId);
    }
    onTabChange?.(tabId);
  };

  const activeTabContent = tabs.find(tab => tab.id === activeTab)?.content;

  const tabListClasses = clsx(
    'flex',
    {
      'border-b border-gray-200 dark:border-gray-700': variant === 'default' || variant === 'underline',
      'bg-gray-100 dark:bg-gray-800 rounded-lg p-1': variant === 'pills',
    },
    className
  );

  const tabClasses = (tab: TabItem, isActive: boolean) => clsx(
    'flex items-center gap-2 font-medium transition-colors duration-200 cursor-pointer',
    {
      // Size variants
      'px-3 py-2 text-sm': size === 'sm',
      'px-4 py-2.5 text-base': size === 'md',
      'px-6 py-3 text-lg': size === 'lg',
      
      // Default and Underline variants (both use border-b-2)
      'border-b-2 -mb-px': variant === 'default' || variant === 'underline',

      // Active states
      'border-blue-500 text-blue-600 dark:text-blue-400': (variant === 'default' || variant === 'underline') && isActive,
      'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm': variant === 'pills' && isActive,

      // Inactive states
      'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300': variant === 'default' && !isActive,
      'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600': variant === 'underline' && !isActive,
      'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300': variant === 'pills' && !isActive,

      // Pills variant
      'rounded-md': variant === 'pills',
      
      // Disabled state
      'opacity-50 cursor-not-allowed': tab.disabled,
    }
  );

  return (
    <div className="w-full">
      {/* Tab List */}
      <div className={tabListClasses} role="tablist">
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tabpanel-${tab.id}`}
              disabled={tab.disabled}
              className={tabClasses(tab, isActive)}
              onClick={() => !tab.disabled && handleTabClick(tab.id)}
            >
              {tab.icon && <span className="flex-shrink-0">{tab.icon}</span>}
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="mt-4">
        {tabs.map((tab) => (
          <div
            key={tab.id}
            id={`tabpanel-${tab.id}`}
            role="tabpanel"
            aria-labelledby={`tab-${tab.id}`}
            className={clsx(
              'focus:outline-none',
              tab.id === activeTab ? 'block' : 'hidden'
            )}
          >
            {tab.content}
          </div>
        ))}
      </div>
    </div>
  );
};
