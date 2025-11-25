import React from 'react';
import { cn } from '@/utils';

export type BadgeVariant = 'success' | 'primary' | 'warning' | 'danger' | 'neutral';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  icon?: React.ReactNode;
  dot?: boolean;
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ children, variant = 'neutral', icon, dot = false, className, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium';

    const variantStyles = {
      success:
        'bg-success-100 dark:bg-success-900/50 text-success-700 dark:text-success-300',
      primary:
        'bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300',
      warning:
        'bg-warning-100 dark:bg-warning-900/50 text-warning-700 dark:text-warning-300',
      danger: 'bg-danger-100 dark:bg-danger-900/50 text-danger-700 dark:text-danger-300',
      neutral: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300',
    };

    const dotColors = {
      success: 'bg-success-600',
      primary: 'bg-primary-600',
      warning: 'bg-warning-600',
      danger: 'bg-danger-600',
      neutral: 'bg-gray-600',
    };

    return (
      <span
        ref={ref}
        className={cn(baseStyles, variantStyles[variant], className)}
        {...props}
      >
        {dot && <span className={cn('h-1.5 w-1.5 rounded-full', dotColors[variant])} />}
        {icon && <span className="flex-shrink-0">{icon}</span>}
        {children}
      </span>
    );
  },
);

Badge.displayName = 'Badge';

export default Badge;
