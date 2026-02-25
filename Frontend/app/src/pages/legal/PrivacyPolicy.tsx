import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';

const LAST_UPDATED = '23/02/2026';
const CONTACT_EMAIL = import.meta.env.VITE_LEGAL_OWNER_EMAIL || '[EMAIL DE CONTACT]';

export default function PrivacyPolicy() {
  const { t } = useTranslation('legal');
  const navigate = useNavigate();

  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate(localStorage.getItem('access_token') ? '/dashboard' : '/');
    }
  };

  const dataItems: string[] = t('privacy.sections.dataCollected.items', {
    returnObjects: true,
  }) as string[];
  const purposeItems: string[] = t('privacy.sections.purposes.items', {
    returnObjects: true,
  }) as string[];
  const subprocessorItems: string[] = t('privacy.sections.subprocessors.items', {
    returnObjects: true,
  }) as string[];
  const rightsItems: string[] = t('privacy.sections.rights.items', {
    returnObjects: true,
  }) as string[];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={handleBack}
            className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 mb-6"
          >
            <span className="material-symbols-outlined text-lg">arrow_back</span>
            PriceWatch
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{t('privacy.title')}</h1>
          <p className="text-sm text-gray-500 mt-2">
            {t('privacy.lastUpdated', { date: LAST_UPDATED })}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 space-y-8 text-gray-700 leading-relaxed">
          <p>{t('privacy.intro')}</p>

          {/* 1. Responsable */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.controller.title')}
            </h2>
            <p>{t('privacy.sections.controller.content')}</p>
            <div className="mt-2 pl-4 border-l-2 border-primary-200 space-y-1 text-sm">
              <p>
                <span className="font-medium">{t('legal.sections.editor.name')}</span>{' '}
                {import.meta.env.VITE_LEGAL_OWNER_NAME || '[NOM / RAISON SOCIALE]'}
              </p>
              <p>
                <span className="font-medium">{t('legal.sections.editor.address')}</span>{' '}
                {import.meta.env.VITE_LEGAL_OWNER_ADDRESS || '[ADRESSE]'}
              </p>
              <p>
                <span className="font-medium">{t('legal.sections.editor.email')}</span>{' '}
                <a href={`mailto:${CONTACT_EMAIL}`} className="text-primary-600 hover:underline">
                  {CONTACT_EMAIL}
                </a>
              </p>
            </div>
          </section>

          {/* 2. Données collectées */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.dataCollected.title')}
            </h2>
            <p className="mb-2">{t('privacy.sections.dataCollected.intro')}</p>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              {dataItems.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>

          {/* 3. Finalités */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.purposes.title')}
            </h2>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              {purposeItems.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>

          {/* 4. Base légale */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.legalBasis.title')}
            </h2>
            <p>{t('privacy.sections.legalBasis.content')}</p>
          </section>

          {/* 5. Conservation */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.retention.title')}
            </h2>
            <p>{t('privacy.sections.retention.content')}</p>
          </section>

          {/* 6. Sous-traitants */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.subprocessors.title')}
            </h2>
            <p className="mb-2">{t('privacy.sections.subprocessors.intro')}</p>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              {subprocessorItems.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>

          {/* 7. Droits */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.rights.title')}
            </h2>
            <p className="mb-2">{t('privacy.sections.rights.intro')}</p>
            <ul className="list-disc pl-6 space-y-1 text-sm mb-3">
              {rightsItems.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <p>
              {t('privacy.sections.rights.exercise')}{' '}
              <a href={`mailto:${CONTACT_EMAIL}`} className="text-primary-600 hover:underline">
                {CONTACT_EMAIL}
              </a>
            </p>
          </section>

          {/* 8. Sécurité */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.security.title')}
            </h2>
            <p>{t('privacy.sections.security.content')}</p>
          </section>

          {/* 9. Cookies */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.cookies.title')}
            </h2>
            <p>{t('privacy.sections.cookies.content')}</p>
          </section>

          {/* 10. Contact */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('privacy.sections.contact.title')}
            </h2>
            <p>
              {t('privacy.sections.contact.content')}{' '}
              <a href={`mailto:${CONTACT_EMAIL}`} className="text-primary-600 hover:underline">
                {CONTACT_EMAIL}
              </a>
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
