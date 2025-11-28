import { Link } from 'react-router-dom';

interface EmptyStateProps {
  hasSearch?: boolean;
  onClearSearch?: () => void;
}

export function EmptyState({ hasSearch = false, onClearSearch }: EmptyStateProps) {
  if (hasSearch) {
    return (
      <div className="text-center py-12">
        <span className="material-symbols-outlined text-gray-400 text-6xl mb-4 block">
          search_off
        </span>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucun produit trouvé</h3>
        <p className="text-gray-600 mb-6">Essayez de modifier votre recherche ou vos filtres</p>
        <button
          onClick={onClearSearch}
          className="px-4 py-2 text-primary-600 hover:text-primary-700 font-medium"
        >
          Effacer la recherche
        </button>
      </div>
    );
  }

  return (
    <div className="text-center py-12">
      <span className="material-symbols-outlined text-gray-400 text-6xl mb-4 block">
        inventory_2
      </span>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucun produit suivi</h3>
      <p className="text-gray-600 mb-6">
        Commencez à suivre des produits pour être notifié des baisses de prix
      </p>
      <Link
        to="/products/add"
        className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
      >
        <span className="material-symbols-outlined">add</span>
        Ajouter mon premier produit
      </Link>
    </div>
  );
}
