import { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '@/components/ui';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
          <div className="max-w-md w-full text-center">
            <span className="material-symbols-outlined text-danger-600 text-6xl mb-4 block">
              error
            </span>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Une erreur est survenue
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Désolé, une erreur inattendue s'est produite. Veuillez réessayer.
            </p>

            {this.state.error && process.env.NODE_ENV === 'development' && (
              <div className="mb-6 p-4 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg text-left">
                <p className="text-sm font-mono text-danger-900 dark:text-danger-100 break-all">
                  {this.state.error.message}
                </p>
              </div>
            )}

            <div className="flex gap-3 justify-center">
              <Button variant="secondary" onClick={this.handleReset}>
                Réessayer
              </Button>
              <Button variant="primary" onClick={() => (window.location.href = '/dashboard')}>
                Retour au tableau de bord
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
