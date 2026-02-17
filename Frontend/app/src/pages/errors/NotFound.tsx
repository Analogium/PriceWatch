import { useTranslation } from 'react-i18next';
import { Button, LinkButton } from '@/components/ui';

export default function NotFound() {
  const { t } = useTranslation('common');

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full text-center">
        {/* 404 Icon */}
        <span className="material-symbols-outlined text-primary-600 dark:text-primary-400 text-6xl mb-4 block">
          search_off
        </span>

        {/* Error Code */}
        <div className="text-6xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('errors.notFound.code')}
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('errors.notFound.title')}
        </h1>

        {/* Description */}
        <p className="text-gray-600 dark:text-gray-400 mb-8">{t('errors.notFound.description')}</p>

        {/* Actions */}
        <div className="flex gap-3 justify-center">
          <Button
            variant="secondary"
            onClick={() => window.history.back()}
            leftIcon={<span className="material-symbols-outlined">arrow_back</span>}
          >
            {t('buttons.back')}
          </Button>
          <LinkButton
            to="/dashboard"
            variant="primary"
            leftIcon={<span className="material-symbols-outlined">home</span>}
          >
            {t('nav.dashboard')}
          </LinkButton>
        </div>

        {/* Help Link */}
        <div className="mt-8">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {t('errors.notFound.needHelp')}{' '}
            <a href="/support" className="text-primary-600 dark:text-primary-400 hover:underline">
              {t('errors.notFound.contactSupport')}
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
