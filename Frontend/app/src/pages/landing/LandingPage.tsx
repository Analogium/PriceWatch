import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import SEO from '@/components/seo/SEO';
import { Footer } from '@/components/layout';
import { cn } from '@/utils/cn';

export default function LandingPage() {
  const { t, i18n } = useTranslation('landing');
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const scrollToFeatures = () => {
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === 'fr' ? 'en' : 'fr');
  };

  return (
    <>
      <SEO
        title={t('hero.title')}
        description={t('hero.subtitle')}
        canonical="/"
      />

      <div className="min-h-screen flex flex-col bg-gray-50">
        {/* Header */}
        <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2 text-xl font-bold text-primary">
              <span className="material-symbols-outlined text-3xl">trending_down</span>
              PriceWatch
            </Link>
            <div className="flex items-center gap-4">
              <button
                onClick={toggleLanguage}
                className="px-3 py-2 text-sm font-medium text-gray-700 hover:text-primary transition-colors"
              >
                {i18n.language === 'fr' ? 'EN' : 'FR'}
              </button>
              <Link
                to="/login"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary transition-colors"
              >
                {i18n.language === 'fr' ? 'Connexion' : 'Login'}
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary/90 transition-colors"
              >
                {i18n.language === 'fr' ? 'Inscription' : 'Sign Up'}
              </Link>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-white to-primary/10 py-20 md:py-32">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="text-4xl md:text-6xl font-black text-gray-900 mb-6 leading-tight">
                {t('hero.title')}
              </h1>
              <p className="text-lg md:text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                {t('hero.subtitle')}
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/register"
                  className="px-8 py-4 text-lg font-semibold text-white bg-primary rounded-lg hover:bg-primary/90 transition-all shadow-lg hover:shadow-xl"
                >
                  {t('hero.cta_primary')}
                </Link>
                <button
                  onClick={scrollToFeatures}
                  className="px-8 py-4 text-lg font-semibold text-primary bg-white border-2 border-primary rounded-lg hover:bg-primary/5 transition-all"
                >
                  {t('hero.cta_secondary')}
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Supported Sites */}
        <section className="py-16 bg-white">
          <div className="container mx-auto px-4">
            <h2 className="text-2xl md:text-3xl font-bold text-center text-gray-900 mb-4">
              {t('sites.title')}
            </h2>
            <p className="text-center text-gray-600 mb-8">{t('sites.subtitle')}</p>
            <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
              {['Amazon.fr', 'Fnac', 'Darty', 'Cdiscount', 'Boulanger', 'E.Leclerc'].map((site) => (
                <div
                  key={site}
                  className="px-6 py-3 text-lg font-semibold text-gray-700 bg-gray-100 rounded-lg"
                >
                  {site}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                {t('features.title')}
              </h2>
              <p className="text-lg text-gray-600">{t('features.subtitle')}</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {[
                { key: 'auto_tracking', icon: 'autorenew' },
                { key: 'instant_alerts', icon: 'notifications_active' },
                { key: 'price_history', icon: 'show_chart' },
                { key: 'multi_sites', icon: 'public' },
                { key: 'custom_frequency', icon: 'schedule' },
                { key: 'intuitive_dashboard', icon: 'dashboard' },
              ].map((feature) => (
                <div
                  key={feature.key}
                  className="bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                    <span className="material-symbols-outlined text-primary text-3xl">
                      {feature.icon}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {t(`features.${feature.key}.title`)}
                  </h3>
                  <p className="text-gray-600">{t(`features.${feature.key}.description`)}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-20 bg-white">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                {t('how_it_works.title')}
              </h2>
              <p className="text-lg text-gray-600">{t('how_it_works.subtitle')}</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-5xl mx-auto">
              {['step1', 'step2', 'step3'].map((step, index) => (
                <div key={step} className="text-center">
                  <div className="w-16 h-16 bg-primary text-white text-2xl font-bold rounded-full flex items-center justify-center mx-auto mb-6">
                    {index + 1}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">
                    {t(`how_it_works.${step}.title`)}
                  </h3>
                  <p className="text-gray-600">{t(`how_it_works.${step}.description`)}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-20 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                {t('faq.title')}
              </h2>
              <p className="text-lg text-gray-600">{t('faq.subtitle')}</p>
            </div>
            <div className="max-w-3xl mx-auto space-y-4">
              {['q1', 'q2', 'q3', 'q4', 'q5', 'q6'].map((q, index) => (
                <div key={q} className="bg-white rounded-lg shadow-sm overflow-hidden">
                  <button
                    onClick={() => setOpenFaq(openFaq === index ? null : index)}
                    className="w-full px-6 py-5 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                  >
                    <span className="font-semibold text-gray-900">
                      {t(`faq.${q}.question`)}
                    </span>
                    <span
                      className={cn(
                        'material-symbols-outlined text-gray-400 transition-transform',
                        openFaq === index && 'rotate-180'
                      )}
                    >
                      expand_more
                    </span>
                  </button>
                  {openFaq === index && (
                    <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
                      <p className="text-gray-600">{t(`faq.${q}.answer`)}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-20 bg-gradient-to-br from-primary to-primary/80">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              {t('cta_final.title')}
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              {t('cta_final.subtitle')}
            </p>
            <Link
              to="/register"
              className="inline-block px-8 py-4 text-lg font-semibold text-primary bg-white rounded-lg hover:bg-gray-100 transition-all shadow-xl"
            >
              {t('cta_final.button')}
            </Link>
          </div>
        </section>

        <Footer />
      </div>
    </>
  );
}
