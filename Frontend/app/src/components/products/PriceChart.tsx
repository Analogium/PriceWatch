import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { PriceHistory } from '@/types/product';
import { formatPrice, formatDate } from '@/utils';
import { Button } from '@/components/ui';

interface PriceChartProps {
  priceHistory: PriceHistory[];
  targetPrice: number;
}

type PeriodFilter = '7d' | '30d' | '90d' | 'all';

const PERIOD_LABELS: Record<PeriodFilter, string> = {
  '7d': '7 jours',
  '30d': '30 jours',
  '90d': '90 jours',
  all: 'Tout',
};

// Custom tooltip component (must be outside of PriceChart to avoid React hooks issues)
const CustomTooltip = ({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: { date: string; price: number } }>;
}) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-lg">
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{data.date}</p>
        <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          {formatPrice(data.price)}
        </p>
      </div>
    );
  }
  return null;
};

export const PriceChart = ({ priceHistory, targetPrice }: PriceChartProps) => {
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodFilter>('30d');

  // Filter data based on selected period
  const getFilteredData = () => {
    if (selectedPeriod === 'all') {
      return priceHistory;
    }

    const now = new Date();
    const daysMap: Record<Exclude<PeriodFilter, 'all'>, number> = {
      '7d': 7,
      '30d': 30,
      '90d': 90,
    };

    const days = daysMap[selectedPeriod];
    const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);

    return priceHistory.filter((item) => new Date(item.recorded_at) >= cutoffDate);
  };

  const filteredData = getFilteredData();

  // Prepare data for the chart - sort by timestamp (oldest to newest)
  const chartData = filteredData
    .map((item) => ({
      date: formatDate(item.recorded_at),
      price: item.price,
      timestamp: new Date(item.recorded_at).getTime(),
    }))
    .sort((a, b) => a.timestamp - b.timestamp);

  if (filteredData.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-8">
        <div className="text-center">
          <span className="material-symbols-outlined text-gray-400 dark:text-gray-600 text-5xl mb-3 block">
            show_chart
          </span>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            Aucune donnée disponible
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            L'historique des prix pour cette période n'est pas encore disponible.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm p-6">
      {/* Header with period filters */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Évolution du prix
        </h3>
        <div className="flex gap-2">
          {(Object.keys(PERIOD_LABELS) as PeriodFilter[]).map((period) => (
            <Button
              key={period}
              variant={selectedPeriod === period ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setSelectedPeriod(period)}
            >
              {PERIOD_LABELS[period]}
            </Button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
            <XAxis
              dataKey="date"
              className="text-gray-600 dark:text-gray-400"
              style={{ fontSize: '0.75rem' }}
            />
            <YAxis
              className="text-gray-600 dark:text-gray-400"
              style={{ fontSize: '0.75rem' }}
              tickFormatter={(value) => `${value}€`}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              y={targetPrice}
              stroke="#16A34A"
              strokeDasharray="5 5"
              label={{
                value: `Prix cible: ${formatPrice(targetPrice)}`,
                position: 'right',
                fill: '#16A34A',
                fontSize: 12,
              }}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#2563EB"
              strokeWidth={2}
              dot={{ fill: '#2563EB', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-primary-600 rounded"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">Prix actuel</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-success-600 rounded" style={{ borderTop: '1px dashed' }}></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">Prix cible</span>
        </div>
      </div>
    </div>
  );
};
