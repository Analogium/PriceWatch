import { Link } from 'react-router-dom';
import { Button } from '@/components/ui';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* 404 Icon */}
        <span className="material-symbols-outlined text-primary-600 dark:text-primary-400 text-6xl mb-4 block">
          search_off
        </span>

        {/* Error Code */}
        <div className="text-6xl font-bold text-gray-900 dark:text-gray-100 mb-2">404</div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Page introuvable
        </h1>

        {/* Description */}
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Désolé, la page que vous recherchez n'existe pas ou a été déplacée.
        </p>

        {/* Actions */}
        <div className="flex gap-3 justify-center">
          <Button variant="secondary" onClick={() => window.history.back()}>
            <span className="material-symbols-outlined">arrow_back</span>
            Retour
          </Button>
          <Link to="/dashboard">
            <Button variant="primary">
              <span className="material-symbols-outlined">home</span>
              Tableau de bord
            </Button>
          </Link>
        </div>

        {/* Help Link */}
        <div className="mt-8">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Besoin d'aide ?{' '}
            <Link to="/support" className="text-primary-600 dark:text-primary-400 hover:underline">
              Contactez le support
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
