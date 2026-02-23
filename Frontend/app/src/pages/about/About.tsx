import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

const CONTACT_EMAIL = import.meta.env.VITE_LEGAL_OWNER_EMAIL || '[EMAIL DE CONTACT]';

const SUPPORTED_SITES = [
  { name: 'Amazon.fr', icon: '🛒' },
  { name: 'Fnac', icon: '📦' },
  { name: 'Darty', icon: '🔌' },
  { name: 'Cdiscount', icon: '🏷️' },
  { name: 'Boulanger', icon: '💡' },
  { name: 'E.Leclerc', icon: '🛍️' },
];

export default function About() {
  const { t } = useTranslation('legal');

  const steps: string[] = t('about.howItWorks.steps', { returnObjects: true }) as string[];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/"
            className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 mb-6"
          >
            <span className="material-symbols-outlined text-lg">arrow_back</span>
            PriceWatch
          </Link>
          <div className="flex items-center gap-3 mb-3">
            <span className="material-symbols-outlined text-primary-600 text-4xl">monitoring</span>
            <h1 className="text-3xl font-bold text-gray-900">{t('about.title')}</h1>
          </div>
          <p className="text-lg text-gray-600">{t('about.subtitle')}</p>
        </div>

        <div className="space-y-6">
          {/* Description */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <p className="text-gray-700 leading-relaxed">{t('about.description')}</p>
          </div>

          {/* Comment ça fonctionne */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary-600">help_outline</span>
              {t('about.howItWorks.title')}
            </h2>
            <ol className="space-y-4">
              {steps.map((step, i) => (
                <li key={i} className="flex gap-4">
                  <span className="flex-shrink-0 w-7 h-7 rounded-full bg-primary-100 text-primary-700 text-sm font-bold flex items-center justify-center">
                    {i + 1}
                  </span>
                  <p className="text-gray-700 pt-0.5">{step}</p>
                </li>
              ))}
            </ol>
          </div>

          {/* Sites supportés */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary-600">storefront</span>
              {t('about.supportedSites.title')}
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {SUPPORTED_SITES.map((site) => (
                <div
                  key={site.name}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg border border-gray-100"
                >
                  <span className="text-xl">{site.icon}</span>
                  <span className="text-sm font-medium text-gray-700">{site.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Technologies */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary-600">code</span>
              {t('about.tech.title')}
            </h2>
            <p className="text-gray-700">{t('about.tech.content')}</p>
          </div>

          {/* Contact */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary-600">mail</span>
              {t('about.contact.title')}
            </h2>
            <p className="text-gray-700">
              {t('about.contact.content')}{' '}
              <a
                href={`mailto:${CONTACT_EMAIL}`}
                className="text-primary-600 hover:underline font-medium"
              >
                {CONTACT_EMAIL}
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
