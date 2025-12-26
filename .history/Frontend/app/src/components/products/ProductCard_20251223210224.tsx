import { memo } from 'react';
import { Link } from 'react-router-dom';
import { usePriceCheck } from '@/contexts/PriceCheckContext';
import type { Product } from '@/types';

interface ProductCardProps {
  product: Product;
  onDelete?: (id: number) => void;
  onCheckPrice?: (id: number) => void;
}

export const ProductCard = memo(function ProductCard({ product, onDelete, onCheckPrice }: ProductCardProps) {
  const { isChecking } = usePriceCheck();
  const isPriceBelowTarget = product.current_price <= product.target_price;
  const priceColor = isPriceBelowTarget ? 'text-green-600' : 'text-gray-900';

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const getFrequencyLabel = (hours: number) => {
    if (hours === 6) return 'Toutes les 6h';
    if (hours === 12) return 'Toutes les 12h';
    return 'Toutes les 24h';
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:shadow-lg transition-shadow overflow-hidden">
      {/* Image */}
      <div className="aspect-square bg-gray-100 relative">
        {product.image ? (
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-full object-contain p-4"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="material-symbols-outlined text-gray-400 text-6xl">image</span>
          </div>
        )}
        {isChecking(product.id) && (
          <div className="absolute top-2 left-2 bg-primary-100 text-primary-800 text-xs font-medium px-2 py-1 rounded flex items-center gap-1 animate-pulse">
            <span className="material-symbols-outlined text-sm">refresh</span>
            Vérification...
          </div>
        )}
        {!product.is_available && (
          <div className="absolute top-2 right-2 bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded">
            Indisponible
          </div>
        )}
        {isPriceBelowTarget && product.is_available && (
          <div className="absolute top-2 right-2 bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded flex items-center gap-1">
            <span className="material-symbols-outlined text-sm">trending_down</span>
            Prix atteint !
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 min-h-[3rem]">
          {product.name}
        </h3>

        {/* Prices */}
        <div className="space-y-2 mb-4">
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-gray-600">Prix actuel :</span>
            <span className={`text-2xl font-bold ${priceColor}`}>
              {formatPrice(product.current_price)}
            </span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-sm text-gray-600">Prix cible :</span>
            <span className="text-lg font-medium text-gray-700">
              {formatPrice(product.target_price)}
            </span>
          </div>
        </div>

        {/* Info */}
        <div className="space-y-1 mb-4 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-base">schedule</span>
            <span>{getFrequencyLabel(product.check_frequency)}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-base">update</span>
            <span>Vérifié le {formatDate(product.last_checked)}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Link
            to={`/products/${product.id}`}
            className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-center text-sm font-medium"
          >
            Détails
          </Link>
          <button
            onClick={() => onCheckPrice?.(product.id)}
            disabled={isChecking(product.id)}
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Vérifier le prix maintenant"
          >
            <span
              className={`material-symbols-outlined text-gray-700 ${isChecking(product.id) ? 'animate-spin' : ''}`}
            >
              refresh
            </span>
          </button>
          <button
            onClick={() => onDelete?.(product.id)}
            className="px-3 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
            title="Supprimer"
          >
            <span className="material-symbols-outlined">delete</span>
          </button>
        </div>
      </div>
    </div>
  );
});
