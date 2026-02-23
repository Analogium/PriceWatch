import { Link } from 'react-router';
import { useTranslation } from 'react-i18next';

export function Footer() {
  const { t } = useTranslation('common');
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Logo & Copyright */}
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary-600 text-2xl">monitoring</span>
            <div>
              <p className="text-sm font-semibold text-gray-900">PriceWatch</p>
              <p className="text-xs text-gray-600">
                &copy; {currentYear} {t('footer.allRightsReserved')}
              </p>
            </div>
          </div>

          {/* Links */}
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
            <Link
              to="/about"
              className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
            >
              {t('footer.about')}
            </Link>
            <Link
              to="/terms"
              className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
            >
              {t('footer.terms')}
            </Link>
            <Link
              to="/privacy"
              className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
            >
              {t('footer.privacy')}
            </Link>
            <Link
              to="/legal"
              className="text-sm text-gray-600 hover:text-primary-600 transition-colors"
            >
              {t('footer.legalNotices')}
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
