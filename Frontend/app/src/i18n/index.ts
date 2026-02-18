import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import frCommon from './locales/fr/common.json';
import frAuth from './locales/fr/auth.json';
import frDashboard from './locales/fr/dashboard.json';
import frProducts from './locales/fr/products.json';
import frSettings from './locales/fr/settings.json';
import frValidation from './locales/fr/validation.json';
import frLanding from './locales/fr/landing.json';

import enCommon from './locales/en/common.json';
import enAuth from './locales/en/auth.json';
import enDashboard from './locales/en/dashboard.json';
import enProducts from './locales/en/products.json';
import enSettings from './locales/en/settings.json';
import enValidation from './locales/en/validation.json';
import enLanding from './locales/en/landing.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      fr: {
        common: frCommon,
        auth: frAuth,
        dashboard: frDashboard,
        products: frProducts,
        settings: frSettings,
        validation: frValidation,
        landing: frLanding,
      },
      en: {
        common: enCommon,
        auth: enAuth,
        dashboard: enDashboard,
        products: enProducts,
        settings: enSettings,
        validation: enValidation,
        landing: enLanding,
      },
    },
    fallbackLng: 'fr',
    defaultNS: 'common',
    ns: ['common', 'auth', 'dashboard', 'products', 'settings', 'validation', 'landing'],
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
    },
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
