import type { PriceStats as PriceStatsType } from '@/types/product';
import { formatPrice, formatPercentage } from '@/utils';

interface PriceStatsProps {
  stats: PriceStatsType;
}

interface StatCardProps {
  icon: string;
  label: string;
  value: string;
  variant?: 'default' | 'success' | 'danger' | 'primary';
  subValue?: string;
}

const StatCard = ({ icon, label, value, variant = 'default', subValue }: StatCardProps) => {
  const variantClasses = {
    default: 'bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100',
    success: 'bg-success-50 dark:bg-success-900/20 text-success-700 dark:text-success-300',
    danger: 'bg-danger-50 dark:bg-danger-900/20 text-danger-700 dark:text-danger-300',
    primary: 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300',
  };

  return (
    <div
      className={`rounded-xl border border-gray-200 dark:border-gray-800 p-4 ${variantClasses[variant]}`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`p-2 rounded-lg ${
            variant === 'default'
              ? 'bg-gray-200 dark:bg-gray-700'
              : variant === 'success'
                ? 'bg-success-100 dark:bg-success-800'
                : variant === 'danger'
                  ? 'bg-danger-100 dark:bg-danger-800'
                  : 'bg-primary-100 dark:bg-primary-800'
          }`}
        >
          <span
            className={`material-symbols-outlined ${
              variant === 'default'
                ? 'text-gray-700 dark:text-gray-300'
                : variant === 'success'
                  ? 'text-success-700 dark:text-success-300'
                  : variant === 'danger'
                    ? 'text-danger-700 dark:text-danger-300'
                    : 'text-primary-700 dark:text-primary-300'
            }`}
          >
            {icon}
          </span>
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
          {subValue && <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{subValue}</p>}
        </div>
      </div>
    </div>
  );
};

export const PriceStats = ({ stats }: PriceStatsProps) => {
  const getPriceChangeVariant = (): 'success' | 'danger' | 'default' => {
    if (stats.price_change_percentage === null) return 'default';
    if (stats.price_change_percentage < 0) return 'success';
    if (stats.price_change_percentage > 0) return 'danger';
    return 'default';
  };

  const getPriceChangeIcon = (): string => {
    if (stats.price_change_percentage === null) return 'trending_flat';
    if (stats.price_change_percentage < 0) return 'trending_down';
    if (stats.price_change_percentage > 0) return 'trending_up';
    return 'trending_flat';
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-6">
      <div className="flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-primary-600 dark:text-primary-400">
          analytics
        </span>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Statistiques</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Current Price */}
        <StatCard
          icon="price_check"
          label="Prix actuel"
          value={formatPrice(stats.current_price)}
          variant="primary"
        />

        {/* Lowest Price */}
        <StatCard
          icon="arrow_downward"
          label="Prix minimum"
          value={formatPrice(stats.lowest_price)}
          variant="success"
          subValue="Meilleur prix observé"
        />

        {/* Highest Price */}
        <StatCard
          icon="arrow_upward"
          label="Prix maximum"
          value={formatPrice(stats.highest_price)}
          variant="danger"
          subValue="Prix le plus élevé"
        />

        {/* Average Price */}
        <StatCard
          icon="show_chart"
          label="Prix moyen"
          value={formatPrice(stats.average_price)}
          variant="default"
        />

        {/* Price Change Percentage */}
        <StatCard
          icon={getPriceChangeIcon()}
          label="Variation globale"
          value={
            stats.price_change_percentage !== null
              ? formatPercentage(stats.price_change_percentage / 100)
              : 'N/A'
          }
          variant={getPriceChangeVariant()}
          subValue={
            stats.price_change_percentage !== null && stats.price_change_percentage < 0
              ? 'Prix en baisse'
              : stats.price_change_percentage !== null && stats.price_change_percentage > 0
                ? 'Prix en hausse'
                : undefined
          }
        />

        {/* Total Records */}
        <StatCard
          icon="data_usage"
          label="Nombre de relevés"
          value={stats.total_records.toString()}
          variant="default"
          subValue={`${stats.total_records} ${stats.total_records > 1 ? 'vérifications' : 'vérification'}`}
        />
      </div>
    </div>
  );
};
