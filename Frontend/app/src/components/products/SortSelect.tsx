import type { SortBy, SortOrder } from '@/types';

interface SortSelectProps {
  sortBy: SortBy;
  order: SortOrder;
  onSortChange: (sortBy: SortBy, order: SortOrder) => void;
}

const sortOptions: { value: SortBy; label: string }[] = [
  { value: 'name', label: 'Nom' },
  { value: 'current_price', label: 'Prix actuel' },
  { value: 'target_price', label: 'Prix cible' },
  { value: 'created_at', label: "Date d'ajout" },
  { value: 'last_checked', label: 'Dernière vérification' },
];

export function SortSelect({ sortBy, order, onSortChange }: SortSelectProps) {
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
        Trier par :
      </label>
      <select
        id="sort-by"
        value={sortBy}
        onChange={(e) => handleSortByChange(e.target.value as SortBy)}
        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white text-sm"
      >
        {sortOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <button
        onClick={handleOrderToggle}
        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        title={order === 'asc' ? 'Croissant' : 'Décroissant'}
      >
        <span className="material-symbols-outlined text-gray-700">
          {order === 'asc' ? 'arrow_upward' : 'arrow_downward'}
        </span>
      </button>
    </div>
  );
}
