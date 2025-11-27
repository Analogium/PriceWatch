export function Footer() {
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
              <p className="text-xs text-gray-600">© {currentYear} Tous droits réservés</p>
            </div>
          </div>

          {/* Links */}
          <div className="flex items-center gap-6">
            <a href="#" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
              À propos
            </a>
            <a href="#" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
              Support
            </a>
            <a href="#" className="text-sm text-gray-600 hover:text-primary-600 transition-colors">
              Confidentialité
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
