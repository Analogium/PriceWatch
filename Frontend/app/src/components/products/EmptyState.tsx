import { LinkButton, Button } from '@/components/ui';

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
        <Button
          onClick={onClearSearch}
          variant="ghost"
          className="text-primary-600 hover:text-primary-700 border-0"
        >
          Effacer la recherche
        </Button>
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
      <LinkButton
        to="/products/add"
        variant="primary"
        size="lg"
        leftIcon={<span className="material-symbols-outlined">add</span>}
      >
        Ajouter mon premier produit
      </LinkButton>
    </div>
  );
}
