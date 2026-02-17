import { useTranslation } from 'react-i18next';
import { Button, LinkButton } from '@/components/ui';

export default function ServerError() {
  const { t } = useTranslation('common');

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* Error Icon */}
        <span className="material-symbols-outlined text-danger-600 dark:text-danger-400 text-6xl mb-4 block">
          error
        </span>

        {/* Error Code */}
        <div className="text-6xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('errors.serverError.code')}
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('errors.serverError.title')}
        </h1>

        {/* Description */}
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          {t('errors.serverError.description')}
        </p>

        {/* Actions */}
        <div className="flex gap-3 justify-center">
          <Button
            variant="secondary"
            onClick={() => window.location.reload()}
            leftIcon={<span className="material-symbols-outlined">refresh</span>}
          >
            {t('buttons.reloadPage')}
          </Button>
          <LinkButton
            to="/dashboard"
            variant="primary"
            leftIcon={<span className="material-symbols-outlined">home</span>}
          >
            {t('nav.dashboard')}
          </LinkButton>
        </div>

        {/* Status Link */}
        <div className="mt-8">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {t('errors.serverError.checkStatus')}{' '}
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
