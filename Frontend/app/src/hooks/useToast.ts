import { useState, useCallback } from 'react';
import type { ToastProps, ToastVariant } from '@/components/ui/Toast';

interface ToastOptions {
  variant?: ToastVariant;
  title?: string;
  duration?: number;
}

export const useToast = () => {
  const [toasts, setToasts] = useState<ToastProps[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = useCallback(
    (message: string, options: ToastOptions = {}) => {
      const id = `toast-${Date.now()}-${Math.random()}`;
      const newToast: ToastProps = {
        id,
        message,
        variant: options.variant || 'info',
        title: options.title,
        duration: options.duration || 5000,
        onClose: removeToast,
      };

      setToasts((prev) => [...prev, newToast]);
    },
    [removeToast],
  );

  const success = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast(message, { variant: 'success', title, duration });
    },
    [addToast],
  );

  const error = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast(message, { variant: 'error', title, duration });
    },
    [addToast],
  );

  const warning = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast(message, { variant: 'warning', title, duration });
    },
    [addToast],
  );

  const info = useCallback(
    (message: string, title?: string, duration?: number) => {
      addToast(message, { variant: 'info', title, duration });
    },
    [addToast],
  );

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
  };
};
