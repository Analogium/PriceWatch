import React, { useEffect } from 'react';
import { cn } from '@/utils';

export type ToastVariant = 'success' | 'error' | 'info' | 'warning';

export interface ToastProps {
  id: string;
  variant?: ToastVariant;
  title?: string;
  message: string;
  duration?: number;
  onClose: (id: string) => void;
}

const Toast: React.FC<ToastProps> = ({
  id,
  variant = 'info',
  title,
  message,
  duration = 5000,
  onClose,
}) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  const variantConfig = {
    success: {
      icon: 'check_circle',
      bgColor: 'bg-success-50 dark:bg-success-900/20',
      borderColor: 'border-success-200 dark:border-success-800',
      iconColor: 'text-success-600 dark:text-success-400',
      textColor: 'text-success-900 dark:text-success-100',
    },
    error: {
      icon: 'error',
      bgColor: 'bg-danger-50 dark:bg-danger-900/20',
      borderColor: 'border-danger-200 dark:border-danger-800',
      iconColor: 'text-danger-600 dark:text-danger-400',
      textColor: 'text-danger-900 dark:text-danger-100',
    },
    warning: {
      icon: 'warning',
      bgColor: 'bg-warning-50 dark:bg-warning-900/20',
      borderColor: 'border-warning-200 dark:border-warning-800',
      iconColor: 'text-warning-600 dark:text-warning-400',
      textColor: 'text-warning-900 dark:text-warning-100',
    },
    info: {
      icon: 'info',
      bgColor: 'bg-primary-50 dark:bg-primary-900/20',
      borderColor: 'border-primary-200 dark:border-primary-800',
      iconColor: 'text-primary-600 dark:text-primary-400',
      textColor: 'text-primary-900 dark:text-primary-100',
    },
  };

  const config = variantConfig[variant];

  return (
    <div
      className={cn(
        'pointer-events-auto flex w-full max-w-md gap-3 rounded-lg border p-4 shadow-lg',
        config.bgColor,
        config.borderColor,
      )}
      role="alert"
    >
      <span className={cn('material-symbols-outlined flex-shrink-0', config.iconColor)}>
        {config.icon}
      </span>
      <div className="flex flex-1 flex-col gap-1">
        {title && (
          <h3 className={cn('text-sm font-semibold', config.textColor)}>{title}</h3>
        )}
        <p className={cn('text-sm', config.textColor)}>{message}</p>
      </div>
      <button
        onClick={() => onClose(id)}
        className={cn(
          'material-symbols-outlined flex-shrink-0 text-xl hover:opacity-70',
          config.iconColor,
        )}
        aria-label="Close notification"
      >
        close
      </button>
    </div>
  );
};

export interface ToastContainerProps {
  toasts: ToastProps[];
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts }) => {
  return (
    <div className="pointer-events-none fixed right-0 top-0 z-50 flex flex-col gap-3 p-4">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} />
      ))}
    </div>
  );
};

export default Toast;
