/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { ToastProps } from '@/components/ui';

interface ToastContextValue {
  toasts: ToastProps[];
  addToast: (
    message: string,
    variant?: ToastProps['variant'],
    title?: string,
    duration?: number
  ) => void;
  removeToast: (id: string) => void;
  success: (message: string, title?: string, duration?: number) => void;
  error: (message: string, title?: string, duration?: number) => void;
  warning: (message: string, title?: string, duration?: number) => void;
  info: (message: string, title?: string, duration?: number) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<ToastProps[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = useCallback(
    (message: string, variant: ToastProps['variant'] = 'info', title?: string, duration = 5000) => {
      const id = `toast-${Date.now()}-${Math.random()}`;
      const newToast: ToastProps = {
        id,
        message,
        variant,
        title,
        duration,
        onClose: removeToast,
      };

      setToasts((prev) => [...prev, newToast]);
    },
    [removeToast]
  );

  const success = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast(message, 'success', title, duration);
    },
    [addToast]
  );

  const error = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast(message, 'error', title, duration);
    },
    [addToast]
  );

  const warning = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast(message, 'warning', title, duration);
    },
    [addToast]
  );

  const info = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast(message, 'info', title, duration);
    },
    [addToast]
  );

  return (
    <ToastContext.Provider
      value={{
        toasts,
        addToast,
        removeToast,
        success,
        error,
        warning,
        info,
      }}
    >
      {children}
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
