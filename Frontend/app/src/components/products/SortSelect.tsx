import { useTranslation } from 'react-i18next';
import type { SortBy, SortOrder } from '@/types';

interface SortSelectProps {
  sortBy: SortBy;
  order: SortOrder;
  onSortChange: (sortBy: SortBy, order: SortOrder) => void;
}

const sortOptionKeys: { value: SortBy; labelKey: string }[] = [
  { value: 'name', labelKey: 'sort.name' },
  { value: 'current_price', labelKey: 'sort.currentPrice' },
  { value: 'target_price', labelKey: 'sort.targetPrice' },
  { value: 'created_at', labelKey: 'sort.createdAt' },
  { value: 'last_checked', labelKey: 'sort.lastChecked' },
];

export function SortSelect({ sortBy, order, onSortChange }: SortSelectProps) {
  const { t } = useTranslation('common');

  const handleSortByChange = (newSortBy: SortBy) => {
    onSortChange(newSortBy, order);
  };

  const handleOrderToggle = () => {
    const newOrder: SortOrder = order === 'asc' ? 'desc' : 'asc';
    onSortChange(sortBy, newOrder);
  };

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="sort-by" className="text-sm font-medium text-gray-700 whitespace-nowrap">
        {t('sort.label')}
      </label>
      <select
        id="sort-by"
        value={sortBy}
        onChange={(e) => handleSortByChange(e.target.value as SortBy)}
        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white text-sm"
      >
        {sortOptionKeys.map((option) => (
          <option key={option.value} value={option.value}>
            {t(option.labelKey)}
          </option>
        ))}
      </select>
      <button
        onClick={handleOrderToggle}
        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        title={order === 'asc' ? t('sort.ascending') : t('sort.descending')}
      >
        <span className="material-symbols-outlined text-gray-700">
          {order === 'asc' ? 'arrow_upward' : 'arrow_downward'}
        </span>
      </button>
    </div>
  );
}
