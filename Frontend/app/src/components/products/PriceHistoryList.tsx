import { useTranslation } from 'react-i18next';
import type { PriceHistory } from '@/types/product';
import { formatPrice, formatDateTime, formatPercentage } from '@/utils';

interface PriceHistoryListProps {
  priceHistory: PriceHistory[];
}

export const PriceHistoryList = ({ priceHistory }: PriceHistoryListProps) => {
  const { t } = useTranslation('products');

  // Calculate price variation between consecutive records
  const calculateVariation = (
    currentPrice: number,
    previousPrice: number | null
  ): number | null => {
    if (previousPrice === null || previousPrice === 0) return null;
    return ((currentPrice - previousPrice) / previousPrice) * 100;
  };

  if (priceHistory.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-8">
        <div className="text-center">
          <span className="material-symbols-outlined text-gray-400 dark:text-gray-600 text-5xl mb-3 block">
            history
          </span>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            {t('priceHistory.empty.title')}
          </h3>
          <p className="text-gray-600 dark:text-gray-400">{t('priceHistory.empty.description')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {t('priceHistory.title')}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {t('priceHistory.count', { count: priceHistory.length })}
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {t('priceHistory.table.date')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {t('priceHistory.table.price')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {t('priceHistory.table.variation')}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {priceHistory.map((record, index) => {
              const previousPrice =
                index < priceHistory.length - 1 ? priceHistory[index + 1].price : null;
              const variation = calculateVariation(record.price, previousPrice);

              return (
                <tr
                  key={record.id}
                  className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-gray-400 dark:text-gray-600 text-lg">
                        schedule
                      </span>
                      <span className="text-sm text-gray-900 dark:text-gray-100">
                        {formatDateTime(record.recorded_at)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                      {formatPrice(record.price)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {variation !== null ? (
                      <div className="flex items-center gap-1">
                        <span
                          className={`material-symbols-outlined text-lg ${
                            variation > 0
                              ? 'text-danger-600 dark:text-danger-400'
                              : variation < 0
                                ? 'text-success-600 dark:text-success-400'
                                : 'text-gray-400 dark:text-gray-600'
                          }`}
                        >
                          {variation > 0
                            ? 'trending_up'
                            : variation < 0
                              ? 'trending_down'
                              : 'trending_flat'}
                        </span>
                        <span
                          className={`text-sm font-medium ${
                            variation > 0
                              ? 'text-danger-700 dark:text-danger-300'
                              : variation < 0
                                ? 'text-success-700 dark:text-success-300'
                                : 'text-gray-600 dark:text-gray-400'
                          }`}
                        >
                          {formatPercentage(variation / 100)}
                        </span>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400 dark:text-gray-600">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
