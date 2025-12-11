import { forwardRef } from 'react';
import { cn } from '@/utils';

export interface ToggleProps {
  id?: string;
  name?: string;
  checked?: boolean;
  disabled?: boolean;
  onChange?: (checked: boolean) => void;
  label?: string;
  description?: string;
  className?: string;
}

export const Toggle = forwardRef<HTMLInputElement, ToggleProps>(
  (
    { id, name, checked = false, disabled = false, onChange, label, description, className },
    ref
  ) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (!disabled && onChange) {
        onChange(e.target.checked);
      }
    };

    return (
      <div className={cn('flex items-start gap-3', className)}>
        <button
          type="button"
          role="switch"
          aria-checked={checked}
          disabled={disabled}
          onClick={() => onChange?.(!checked)}
          className={cn(
            'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-600 focus:ring-offset-2',
            checked ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          <span className="sr-only">{label || 'Toggle'}</span>
          <span
            aria-hidden="true"
            className={cn(
              'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
              checked ? 'translate-x-5' : 'translate-x-0'
            )}
          />
        </button>
        <input
          ref={ref}
          type="checkbox"
          id={id}
          name={name}
          checked={checked}
          onChange={handleChange}
          disabled={disabled}
          className="sr-only"
        />
        {(label || description) && (
          <div className="flex-1">
            {label && (
              <label
                htmlFor={id}
                className={cn(
                  'block text-sm font-medium text-gray-900 dark:text-gray-100',
                  disabled && 'opacity-50'
                )}
              >
                {label}
              </label>
            )}
            {description && (
              <p
                className={cn(
                  'text-sm text-gray-600 dark:text-gray-400 mt-0.5',
                  disabled && 'opacity-50'
                )}
              >
                {description}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Toggle.displayName = 'Toggle';
