import React from 'react';
import { clsx } from 'clsx';

export interface ProgressProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  label?: string;
  className?: string;
  animated?: boolean;
}

/**
 * Progress Component
 * 
 * A flexible progress bar component with multiple variants and sizes
 */
export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  size = 'md',
  variant = 'default',
  showLabel = false,
  label,
  className = '',
  animated = false
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const containerClasses = clsx(
    'w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden',
    {
      'h-1': size === 'sm',
      'h-2': size === 'md',
      'h-3': size === 'lg',
    },
    className
  );

  const barClasses = clsx(
    'h-full transition-all duration-300 ease-out rounded-full',
    {
      // Default variant
      'bg-blue-500': variant === 'default',
      
      // Success variant
      'bg-green-500': variant === 'success',
      
      // Warning variant
      'bg-yellow-500': variant === 'warning',
      
      // Error variant
      'bg-red-500': variant === 'error',
      
      // Animated variant
      'bg-gradient-to-r from-blue-400 to-blue-600 bg-size-200 animate-pulse': animated && variant === 'default',
      'bg-gradient-to-r from-green-400 to-green-600 bg-size-200 animate-pulse': animated && variant === 'success',
      'bg-gradient-to-r from-yellow-400 to-yellow-600 bg-size-200 animate-pulse': animated && variant === 'warning',
      'bg-gradient-to-r from-red-400 to-red-600 bg-size-200 animate-pulse': animated && variant === 'error',
    }
  );

  const displayLabel = label || `${Math.round(percentage)}%`;

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {displayLabel}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {Math.round(percentage)}%
          </span>
        </div>
      )}
      
      <div className={containerClasses} role="progressbar" aria-valuenow={value} aria-valuemax={max}>
        <div 
          className={barClasses}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
