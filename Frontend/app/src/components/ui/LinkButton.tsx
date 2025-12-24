import React from 'react';
import { Link, type LinkProps } from 'react-router-dom';
import { cn } from '@/utils';
import type { ButtonVariant, ButtonSize } from './Button';

export interface LinkButtonProps extends Omit<LinkProps, 'className'> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  className?: string;
}

const LinkButton = React.forwardRef<HTMLAnchorElement, LinkButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      leftIcon,
      rightIcon,
      fullWidth = false,
      className,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center gap-2 font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';

    const variantStyles = {
      primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-600',
      secondary:
        'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-gray-300 dark:focus:ring-gray-700',
      danger: 'bg-danger-600 text-white hover:bg-danger-700 focus:ring-danger-600',
    };

    const sizeStyles = {
      sm: 'h-9 px-3 py-1.5 text-sm',
      md: 'h-10 px-4 py-2 text-base',
      lg: 'h-12 px-6 py-3 text-lg',
    };

    const widthStyles = fullWidth ? 'w-full' : '';

    return (
      <Link
        ref={ref}
        className={cn(baseStyles, variantStyles[variant], sizeStyles[size], widthStyles, className)}
        {...props}
      >
        {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
        {children}
        {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
      </Link>
    );
  }
);

LinkButton.displayName = 'LinkButton';

export default LinkButton;
