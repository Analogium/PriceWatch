import { cn } from '@/utils';

export interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'danger';
  title?: string;
  children: React.ReactNode;
  icon?: string;
  onClose?: () => void;
  className?: string;
}

const variantClasses = {
  info: {
    container: 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800',
    icon: 'text-primary-600 dark:text-primary-400',
    title: 'text-primary-900 dark:text-primary-100',
    text: 'text-primary-800 dark:text-primary-200',
    closeButton:
      'text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-200',
  },
  success: {
    container: 'bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800',
    icon: 'text-success-600 dark:text-success-400',
    title: 'text-success-900 dark:text-success-100',
    text: 'text-success-800 dark:text-success-200',
    closeButton:
      'text-success-600 hover:text-success-800 dark:text-success-400 dark:hover:text-success-200',
  },
  warning: {
    container: 'bg-warning-50 dark:bg-warning-900/20 border-warning-200 dark:border-warning-800',
    icon: 'text-warning-600 dark:text-warning-400',
    title: 'text-warning-900 dark:text-warning-100',
    text: 'text-warning-800 dark:text-warning-200',
    closeButton:
      'text-warning-600 hover:text-warning-800 dark:text-warning-400 dark:hover:text-warning-200',
  },
  danger: {
    container: 'bg-danger-50 dark:bg-danger-900/20 border-danger-200 dark:border-danger-800',
    icon: 'text-danger-600 dark:text-danger-400',
    title: 'text-danger-900 dark:text-danger-100',
    text: 'text-danger-800 dark:text-danger-200',
    closeButton:
      'text-danger-600 hover:text-danger-800 dark:text-danger-400 dark:hover:text-danger-200',
  },
};

const defaultIcons = {
  info: 'info',
  success: 'check_circle',
  warning: 'warning',
  danger: 'error',
};

export default function Alert({
  variant = 'info',
  title,
  children,
  icon,
  onClose,
  className,
}: AlertProps) {
  const styles = variantClasses[variant];
  const displayIcon = icon || defaultIcons[variant];

  return (
    <div className={cn('rounded-lg border p-4', styles.container, className)} role="alert">
      <div className="flex items-start gap-3">
        {displayIcon && (
          <span
            className={cn('material-symbols-outlined flex-shrink-0', styles.icon)}
            aria-hidden="true"
          >
            {displayIcon}
          </span>
        )}
        <div className="flex-1 min-w-0">
          {title && <h3 className={cn('text-sm font-semibold mb-1', styles.title)}>{title}</h3>}
          <div className={cn('text-sm', styles.text)}>{children}</div>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className={cn(
              'flex-shrink-0 inline-flex rounded-lg p-1 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors',
              styles.closeButton
            )}
            aria-label="Fermer"
          >
            <span className="material-symbols-outlined text-xl" aria-hidden="true">
              close
            </span>
          </button>
        )}
      </div>
    </div>
  );
}
