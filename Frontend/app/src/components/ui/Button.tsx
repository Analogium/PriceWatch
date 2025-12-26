import React from 'react';
import { cn } from '@/utils';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  iconOnly?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      iconOnly = false,
      className,
      disabled,
      type = 'button',
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center gap-2 font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

    const variantStyles = {
      primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-600',
      secondary:
        'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-gray-300 dark:focus:ring-gray-700',
      danger: 'bg-danger-600 text-white hover:bg-danger-700 focus:ring-danger-600',
      ghost: 'border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-300',
    };

    const sizeStyles = iconOnly
      ? {
          sm: 'h-9 w-9 p-2',
          md: 'h-10 w-10 p-2',
          lg: 'h-12 w-12 p-3',
        }
      : {
          sm: 'h-9 px-3 py-1.5 text-sm',
          md: 'h-10 px-4 py-2 text-base',
          lg: 'h-12 px-6 py-3 text-lg',
        };

    const widthStyles = fullWidth ? 'w-full' : '';

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variantStyles[variant], sizeStyles[size], widthStyles, className)}
        {...props}
      >
        {isLoading ? (
          <>
            <span className="material-symbols-outlined animate-spin !text-xl inline-flex items-center">
              progress_activity
            </span>
            {children}
          </>
        ) : (
          <>
            {leftIcon && <span className="flex-shrink-0 inline-flex items-center">{leftIcon}</span>}
            {children}
            {rightIcon && (
              <span className="flex-shrink-0 inline-flex items-center">{rightIcon}</span>
            )}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
