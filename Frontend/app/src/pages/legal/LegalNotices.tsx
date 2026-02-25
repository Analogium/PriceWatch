import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';
import { useAuth } from '@/hooks/useAuth';

export default function LegalNotices() {
  const { t } = useTranslation('legal');
  const { isAuthenticated } = useAuth();

  const ownerName = import.meta.env.VITE_LEGAL_OWNER_NAME || '[NOM / RAISON SOCIALE]';
  const ownerAddress = import.meta.env.VITE_LEGAL_OWNER_ADDRESS || '[ADRESSE]';
  const ownerEmail = import.meta.env.VITE_LEGAL_OWNER_EMAIL || '[EMAIL DE CONTACT]';
  const hostName = import.meta.env.VITE_LEGAL_HOST_NAME || '[HÉBERGEUR]';
  const hostAddress = import.meta.env.VITE_LEGAL_HOST_ADDRESS || '[ADRESSE HÉBERGEUR]';
  const hostUrl = import.meta.env.VITE_LEGAL_HOST_URL || '[URL HÉBERGEUR]';

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <Link
            to={isAuthenticated ? '/dashboard' : '/'}
            className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 mb-6"
          >
            <span className="material-symbols-outlined text-lg">arrow_back</span>
            PriceWatch
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">{t('legal.title')}</h1>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 space-y-8 text-gray-700 leading-relaxed">
          {/* Éditeur */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-3">
              {t('legal.sections.editor.title')}
            </h2>
            <div className="space-y-2 text-sm">
              <p>
                <span className="font-medium">{t('legal.sections.editor.name')}</span> {ownerName}
              </p>
              <p>
                <span className="font-medium">{t('legal.sections.editor.address')}</span>{' '}
                {ownerAddress}
              </p>
              <p>
                <span className="font-medium">{t('legal.sections.editor.email')}</span>{' '}
                <a href={`mailto:${ownerEmail}`} className="text-primary-600 hover:underline">
                  {ownerEmail}
                </a>
              </p>
            </div>
          </section>

          {/* Hébergeur */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-3">
              {t('legal.sections.host.title')}
            </h2>
            <div className="space-y-2 text-sm">
              <p>
                <span className="font-medium">{t('legal.sections.host.name')}</span> {hostName}
              </p>
              <p>
                <span className="font-medium">{t('legal.sections.host.address')}</span>{' '}
                {hostAddress}
              </p>
              <p>
                <span className="font-medium">{t('legal.sections.host.url')}</span>{' '}
                {hostUrl !== '[URL HÉBERGEUR]' ? (
                  <a
                    href={hostUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:underline"
                  >
                    {hostUrl}
                  </a>
                ) : (
                  hostUrl
                )}
              </p>
            </div>
          </section>

          {/* Propriété intellectuelle */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('legal.sections.ip.title')}
            </h2>
            <p>{t('legal.sections.ip.content')}</p>
          </section>

          {/* Données personnelles */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('legal.sections.data.title')}
            </h2>
            <p>
              {t('legal.sections.data.content')}{' '}
              <Link to="/privacy" className="text-primary-600 hover:underline">
                {t('footer.privacy', { ns: 'common' })}
              </Link>
            </p>
          </section>

          {/* Cookies */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('legal.sections.cookies.title')}
            </h2>
            <p>{t('legal.sections.cookies.content')}</p>
          </section>
        </div>
      </div>
    </div>
  );
}
