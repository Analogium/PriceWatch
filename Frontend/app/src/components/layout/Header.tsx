import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router';
import { useAuth } from '@/hooks/useAuth';
import { usePriceCheck } from '@/contexts/PriceCheckContext';
import { Button, Avatar } from '@/components/ui';

export function Header() {
  const { user, logout } = useAuth();
  const { checkingProducts } = usePriceCheck();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setIsUserMenuOpen(false);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link
            to="/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <span className="material-symbols-outlined text-primary-600 text-3xl">monitoring</span>
            <span className="text-xl font-bold text-gray-900">PriceWatch</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            <Link
              to="/dashboard"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/dashboard')
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              Tableau de bord
            </Link>
            <Link
              to="/products/add"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/products/add')
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              Ajouter un produit
            </Link>
            <Link
              to="/settings"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/settings')
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              Paramètres
            </Link>
          </nav>

          {/* Desktop User Menu */}
          <div className="hidden md:flex items-center gap-3">
            {/* Price check indicator */}
            {checkingProducts.length > 0 && (
              <div className="flex items-center gap-2 px-3 py-2 bg-primary-50 text-primary-700 rounded-lg border border-primary-200">
                <span className="material-symbols-outlined text-lg animate-spin">refresh</span>
                <span className="text-sm font-medium">
                  {checkingProducts.length} vérification{checkingProducts.length > 1 ? 's' : ''} en
                  cours
                </span>
              </div>
            )}

            {user && (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                  aria-label="Menu utilisateur"
                >
                  <Avatar
                    fallback={user.email.charAt(0).toUpperCase()}
                    size="sm"
                    variant="circle"
                    alt={user.email}
                  />
                  <span className="text-sm text-gray-700">{user.email}</span>
                  <span className="material-symbols-outlined text-gray-500 text-lg">
                    {isUserMenuOpen ? 'expand_less' : 'expand_more'}
                  </span>
                </button>

                {/* Dropdown Menu */}
                {isUserMenuOpen && (
                  <>
                    {/* Backdrop */}
                    <div className="fixed inset-0 z-10" onClick={() => setIsUserMenuOpen(false)} />
                    {/* Menu */}
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                      <div className="px-4 py-3 border-b border-gray-100">
                        <p className="text-sm font-medium text-gray-900">Connecté en tant que</p>
                        <p className="text-sm text-gray-600 truncate">{user.email}</p>
                      </div>
                      <Link
                        to="/settings"
                        className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        onClick={() => setIsUserMenuOpen(false)}
                      >
                        <span className="material-symbols-outlined text-lg">settings</span>
                        <span>Paramètres</span>
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-danger-600 hover:bg-danger-50"
                      >
                        <span className="material-symbols-outlined text-lg">logout</span>
                        <span>Déconnexion</span>
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Menu"
          >
            <span className="material-symbols-outlined text-2xl text-gray-700">
              {isMenuOpen ? 'close' : 'menu'}
            </span>
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200">
            <nav className="flex flex-col gap-1">
              <Link
                to="/dashboard"
                className={`px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive('/dashboard')
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Tableau de bord
              </Link>
              <Link
                to="/products/add"
                className={`px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive('/products/add')
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Ajouter un produit
              </Link>
              <Link
                to="/settings"
                className={`px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive('/settings')
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Paramètres
              </Link>
            </nav>

            {/* Mobile User Info */}
            {user && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="px-4 py-2">
                  <p className="text-sm font-medium text-gray-900">Connecté en tant que</p>
                  <p className="text-sm text-gray-600 truncate">{user.email}</p>
                </div>
                <Button onClick={handleLogout} variant="danger" fullWidth className="mt-3">
                  <span className="material-symbols-outlined text-lg">logout</span>
                  <span>Déconnexion</span>
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;
