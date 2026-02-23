import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

const LAST_UPDATED = '23/02/2026';

export default function TermsOfService() {
  const { t } = useTranslation('legal');

  const accountItems: string[] = t('terms.sections.account.items', {
    returnObjects: true,
  }) as string[];
  const serviceItems: string[] = t('terms.sections.service.items', {
    returnObjects: true,
  }) as string[];

  const sections = [
    { key: 'object', hasItems: false },
    { key: 'acceptance', hasItems: false },
    { key: 'usage', hasItems: false },
    { key: 'ip', hasItems: false },
    { key: 'liability', hasItems: false },
    { key: 'termination', hasItems: false },
    { key: 'changes', hasItems: false },
    { key: 'law', hasItems: false },
  ] as const;

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
          <h1 className="text-3xl font-bold text-gray-900">{t('terms.title')}</h1>
          <p className="text-sm text-gray-500 mt-2">
            {t('terms.lastUpdated', { date: LAST_UPDATED })}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 space-y-8 text-gray-700 leading-relaxed">
          {/* 1. Objet */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('terms.sections.object.title')}
            </h2>
            <p>{t('terms.sections.object.content')}</p>
          </section>

          {/* 2. Acceptation */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('terms.sections.acceptance.title')}
            </h2>
            <p>{t('terms.sections.acceptance.content')}</p>
          </section>

          {/* 3. Compte */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('terms.sections.account.title')}
            </h2>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              {accountItems.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>

          {/* 4. Service */}
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              {t('terms.sections.service.title')}
            </h2>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              {serviceItems.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>

          {/* Remaining sections (content-only) */}
          {sections.map(({ key }) => (
            <section key={key}>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                {t(`terms.sections.${key}.title`)}
              </h2>
              <p>{t(`terms.sections.${key}.content`)}</p>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
