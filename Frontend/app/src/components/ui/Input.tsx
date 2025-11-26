import React, { useId } from 'react';
import { cn } from '@/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  rightIconClickable?: boolean;
  onRightIconClick?: () => void;
  fullWidth?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      rightIconClickable = false,
      onRightIconClick,
      fullWidth = false,
      className,
      id,
      type = 'text',
      disabled,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const inputId = id || generatedId;

    const baseInputStyles =
      'form-input rounded-lg border bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 transition-colors focus:outline-none h-12 px-4 py-2.5 disabled:opacity-50 disabled:cursor-not-allowed';

    const stateStyles = error
      ? 'border-danger-600 focus:border-danger-600 focus:ring-2 focus:ring-danger-600/20'
      : 'border-gray-300 dark:border-gray-700 focus:border-primary-600 focus:ring-2 focus:ring-primary-600/20';

    const iconPaddingStyles = leftIcon ? 'pl-10' : rightIcon ? 'pr-10' : '';

    const widthStyles = fullWidth ? 'w-full' : '';

    return (
      <div className={cn('flex flex-col gap-2', widthStyles)}>
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            type={type}
            disabled={disabled}
            className={cn(baseInputStyles, stateStyles, iconPaddingStyles, widthStyles, className)}
            {...props}
          />
          {rightIcon &&
            (rightIconClickable ? (
              <button
                type="button"
                onClick={onRightIconClick}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                {rightIcon}
              </button>
            ) : (
              <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
                {rightIcon}
              </div>
            ))}
        </div>
        {error && <p className="text-sm text-danger-600">{error}</p>}
        {!error && helperText && (
          <p className="text-sm text-gray-500 dark:text-gray-400">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
