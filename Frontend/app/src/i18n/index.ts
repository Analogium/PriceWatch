import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import frCommon from './locales/fr/common.json';
import frAuth from './locales/fr/auth.json';
import frDashboard from './locales/fr/dashboard.json';
import frProducts from './locales/fr/products.json';
import frSettings from './locales/fr/settings.json';
import frValidation from './locales/fr/validation.json';

import enCommon from './locales/en/common.json';
import enAuth from './locales/en/auth.json';
import enDashboard from './locales/en/dashboard.json';
import enProducts from './locales/en/products.json';
import enSettings from './locales/en/settings.json';
import enValidation from './locales/en/validation.json';

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
      },
      en: {
        common: enCommon,
        auth: enAuth,
        dashboard: enDashboard,
        products: enProducts,
        settings: enSettings,
        validation: enValidation,
      },
    },
    fallbackLng: 'fr',
    defaultNS: 'common',
    ns: ['common', 'auth', 'dashboard', 'products', 'settings', 'validation'],
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
