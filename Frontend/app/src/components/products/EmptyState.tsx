import { useTranslation } from 'react-i18next';
import { LinkButton, Button } from '@/components/ui';

interface EmptyStateProps {
  hasSearch?: boolean;
  onClearSearch?: () => void;
}

export function EmptyState({ hasSearch = false, onClearSearch }: EmptyStateProps) {
  const { t } = useTranslation('products');

  if (hasSearch) {
    return (
      <div className="text-center py-12">
        <span className="material-symbols-outlined text-gray-400 text-6xl mb-4 block">
          search_off
        </span>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('emptyState.search.title')}</h3>
        <p className="text-gray-600 mb-6">{t('emptyState.search.description')}</p>
        <Button
          onClick={onClearSearch}
          variant="ghost"
          className="text-primary-600 hover:text-primary-700 border-0"
        >
          {t('emptyState.search.clearButton')}
        </Button>
      </div>
    );
  }

  return (
    <div className="text-center py-12">
      <span className="material-symbols-outlined text-gray-400 text-6xl mb-4 block">
        inventory_2
      </span>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {t('emptyState.noProducts.title')}
      </h3>
      <p className="text-gray-600 mb-6">{t('emptyState.noProducts.description')}</p>
      <LinkButton
        to="/products/add"
        variant="primary"
        size="lg"
        leftIcon={<span className="material-symbols-outlined">add</span>}
      >
        {t('emptyState.noProducts.action')}
      </LinkButton>
    </div>
  );
}
