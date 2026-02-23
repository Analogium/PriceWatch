import { useState } from 'react';
import { useTranslation } from 'react-i18next';

const CONSENT_KEY = 'cookie_consent';

export default function CookieBanner() {
  const { t } = useTranslation('legal');
  const [visible, setVisible] = useState(() => !localStorage.getItem(CONSENT_KEY));

  const handleAccept = () => {
    localStorage.setItem(CONSENT_KEY, 'accepted');
    setVisible(false);
  };

  const handleDecline = () => {
    localStorage.setItem(CONSENT_KEY, 'declined');
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 sm:p-6">
      <div className="max-w-4xl mx-auto bg-white border border-gray-200 rounded-xl shadow-lg p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <span className="material-symbols-outlined text-primary-600 text-2xl shrink-0">cookie</span>

        <p className="text-sm text-gray-700 flex-1">
          {t('cookieBanner.message')}{' '}
          <a href="/privacy" className="text-primary-600 hover:underline font-medium">
            {t('cookieBanner.learnMore')}
          </a>
        </p>

        <div className="flex gap-2 shrink-0">
          <button
            onClick={handleDecline}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            {t('cookieBanner.decline')}
          </button>
          <button
            onClick={handleAccept}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors"
          >
            {t('cookieBanner.accept')}
          </button>
        </div>
      </div>
    </div>
  );
}
