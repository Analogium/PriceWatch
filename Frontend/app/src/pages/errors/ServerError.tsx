import { Button, LinkButton } from '@/components/ui';

export default function ServerError() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* Error Icon */}
        <span className="material-symbols-outlined text-danger-600 dark:text-danger-400 text-6xl mb-4 block">
          error
        </span>

        {/* Error Code */}
        <div className="text-6xl font-bold text-gray-900 dark:text-gray-100 mb-2">500</div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Erreur serveur</h1>

        {/* Description */}
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Désolé, une erreur s'est produite sur nos serveurs. Nous travaillons à résoudre le
          problème. Veuillez réessayer dans quelques instants.
        </p>

        {/* Actions */}
        <div className="flex gap-3 justify-center">
          <Button
            variant="secondary"
            onClick={() => window.location.reload()}
            leftIcon={<span className="material-symbols-outlined">refresh</span>}
          >
            Recharger la page
          </Button>
          <LinkButton
            to="/dashboard"
            variant="primary"
            leftIcon={<span className="material-symbols-outlined">home</span>}
          >
            Tableau de bord
          </LinkButton>
        </div>

        {/* Status Link */}
        <div className="mt-8">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Vérifier l'état du service :{' '}
            <a
              href="https://status.pricewatch.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 dark:text-primary-400 hover:underline"
            >
              status.pricewatch.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
