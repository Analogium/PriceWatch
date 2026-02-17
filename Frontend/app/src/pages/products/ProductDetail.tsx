import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { productsApi } from '@/api/products';
import { Card, Button, Badge, Modal, Breadcrumb, Tabs } from '@/components/ui';
import { PriceChart, PriceHistoryList, PriceStats } from '@/components/products';
import { useToast } from '@/contexts/ToastContext';
import { usePriceCheck } from '@/contexts/PriceCheckContext';
import { formatPrice, formatDateTime, formatRelativeTime } from '@/utils/formatters';
import type { Product } from '@/types';
import type { PriceHistory, PriceStats as PriceStatsType } from '@/types/product';

export default function ProductDetail() {
  const { t } = useTranslation('products');
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { success, error, info } = useToast();
  const { isChecking, startChecking, finishChecking } = usePriceCheck();

  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [priceHistory, setPriceHistory] = useState<PriceHistory[]>([]);
  const [priceStats, setPriceStats] = useState<PriceStatsType | null>(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Load product data
  useEffect(() => {
    const fetchProduct = async () => {
      if (!id) return;

      try {
        setIsLoading(true);
        const data = await productsApi.getById(Number(id));
        setProduct(data);
      } catch {
        error(t('detail.error.loading'));
        navigate('/dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProduct();
  }, [id, navigate, error, t]);

  // Load price history and stats
  useEffect(() => {
    const fetchPriceData = async () => {
      if (!id) return;

      try {
        setIsLoadingHistory(true);
        const [history, stats] = await Promise.all([
          productsApi.getHistory(Number(id)),
          productsApi.getStats(Number(id)),
        ]);
        setPriceHistory(history);
        setPriceStats(stats);
      } catch {
        error(t('detail.error.history'));
      } finally {
        setIsLoadingHistory(false);
      }
    };

    fetchPriceData();
  }, [id, error, t]);

  // Check price now
  const handleCheckPrice = async () => {
    if (!product) return;

    // Start checking and show info toast
    startChecking(product);
    info(t('detail.checkPrice.info'), undefined, 10000);

    try {
      const updatedProduct = await productsApi.checkPrice(product.id);
      setProduct(updatedProduct);
      success(t('detail.checkPrice.success'));

      // Reload price history and stats
      const [history, stats] = await Promise.all([
        productsApi.getHistory(product.id),
        productsApi.getStats(product.id),
      ]);
      setPriceHistory(history);
      setPriceStats(stats);
    } catch {
      error(t('detail.error.checkPrice'));
    } finally {
      finishChecking(product.id);
    }
  };

  // Delete product
  const handleDelete = async () => {
    if (!product) return;

    try {
      setIsDeleting(true);
      await productsApi.delete(product.id);
      success(t('dashboard:success.delete'));
      navigate('/dashboard');
    } catch {
      error(t('detail.error.delete'));
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <Card>
            <div className="space-y-4">
              <div className="h-64 bg-gray-200 rounded"></div>
              <div className="h-6 bg-gray-200 rounded w-2/3"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (!product) {
    return null;
  }

  const isPriceReached = product.current_price <= product.target_price;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Breadcrumb navigation */}
      <div className="mb-6">
        <Breadcrumb
          items={[
            { label: t('common:breadcrumb.dashboard'), href: '/dashboard', icon: 'home' },
            { label: product.name, icon: 'shopping_bag' },
          ]}
        />
      </div>

      {/* Main content */}
      <Card>
        <div className="space-y-6">
          {/* Product image and basic info */}
          <div className="flex flex-col md:flex-row gap-6">
            {/* Image */}
            {product.image ? (
              <div className="shrink-0">
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-full md:w-64 h-64 object-cover rounded-lg border border-gray-200"
                />
              </div>
            ) : (
              <div className="shrink-0 w-full md:w-64 h-64 bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center">
                <span className="material-symbols-outlined text-6xl text-gray-400">image</span>
              </div>
            )}

            {/* Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold text-gray-900 mb-4">{product.name}</h1>

              {/* Status badge */}
              <div className="mb-4">
                {!product.is_available ? (
                  <Badge variant="danger">
                    <span className="material-symbols-outlined text-sm">block</span>
                    {t('detail.status.unavailable')}
                  </Badge>
                ) : isPriceReached ? (
                  <Badge variant="success">
                    <span className="material-symbols-outlined text-sm">check_circle</span>
                    {t('detail.status.priceReached')}
                  </Badge>
                ) : (
                  <Badge variant="neutral">
                    <span className="material-symbols-outlined text-sm">trending_down</span>
                    {t('detail.status.monitoring')}
                  </Badge>
                )}
              </div>

              {/* Prices */}
              <div className="space-y-3 mb-6">
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <span className="text-gray-600">{t('detail.price.current')}</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {formatPrice(product.current_price)}
                  </span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <span className="text-gray-600">{t('detail.price.target')}</span>
                  <span className="text-xl font-semibold text-primary-600">
                    {formatPrice(product.target_price)}
                  </span>
                </div>
              </div>

              {/* External link */}
              <a
                href={product.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium transition-colors"
              >
                <span className="material-symbols-outlined text-xl">open_in_new</span>
                <span>{t('detail.link')}</span>
              </a>
            </div>
          </div>

          {/* Divider */}
          <div className="border-t border-gray-200"></div>

          {/* Additional details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3">
              <span className="material-symbols-outlined text-gray-400 text-xl">schedule</span>
              <div>
                <p className="text-sm font-medium text-gray-900">{t('detail.frequencyLabel')}</p>
                <p className="text-sm text-gray-600">
                  {t('detail.frequencyText', { hours: product.check_frequency })}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="material-symbols-outlined text-gray-400 text-xl">update</span>
              <div>
                <p className="text-sm font-medium text-gray-900">{t('detail.lastChecked')}</p>
                <p className="text-sm text-gray-600" title={formatDateTime(product.last_checked)}>
                  {formatRelativeTime(product.last_checked)}
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="material-symbols-outlined text-gray-400 text-xl">
                calendar_today
              </span>
              <div>
                <p className="text-sm font-medium text-gray-900">{t('detail.createdAt')}</p>
                <p className="text-sm text-gray-600">{formatDateTime(product.created_at)}</p>
              </div>
            </div>

            {product.unavailable_since && (
              <div className="flex items-start gap-3">
                <span className="material-symbols-outlined text-danger-600 text-xl">error</span>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {t('detail.unavailableSince')}
                  </p>
                  <p className="text-sm text-gray-600">
                    {formatDateTime(product.unavailable_since)}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="border-t border-gray-200"></div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={handleCheckPrice}
              isLoading={product ? isChecking(product.id) : false}
              leftIcon={<span className="material-symbols-outlined">refresh</span>}
            >
              {t('detail.action.checkPrice')}
            </Button>

            <Button
              variant="secondary"
              onClick={() => navigate(`/products/${product.id}/edit`)}
              leftIcon={<span className="material-symbols-outlined">edit</span>}
            >
              {t('detail.action.edit')}
            </Button>

            <Button
              variant="danger"
              onClick={() => setShowDeleteModal(true)}
              leftIcon={<span className="material-symbols-outlined">delete</span>}
            >
              {t('detail.action.delete')}
            </Button>
          </div>
        </div>
      </Card>

      {/* Price History Section with Tabs */}
      {!isLoadingHistory && priceStats && (
        <div className="mt-8">
          <Tabs
            items={[
              {
                id: 'stats',
                label: t('detail.tabs.stats'),
                icon: 'bar_chart',
                content: <PriceStats stats={priceStats} />,
              },
              {
                id: 'chart',
                label: t('detail.tabs.chart'),
                icon: 'show_chart',
                content: (
                  <PriceChart priceHistory={priceHistory} targetPrice={product.target_price} />
                ),
              },
              {
                id: 'history',
                label: t('detail.tabs.history'),
                icon: 'history',
                content: <PriceHistoryList priceHistory={priceHistory} />,
              },
            ]}
            defaultTab="stats"
            variant="underline"
          />
        </div>
      )}

      {isLoadingHistory && (
        <div className="mt-8 space-y-6">
          <div className="animate-pulse bg-gray-200 rounded-xl h-64"></div>
          <div className="animate-pulse bg-gray-200 rounded-xl h-80"></div>
          <div className="animate-pulse bg-gray-200 rounded-xl h-96"></div>
        </div>
      )}

      {/* Delete confirmation modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title={t('detail.deleteConfirm.title')}
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-700">{t('detail.deleteConfirm.message')}</p>

          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <p className="text-sm font-medium text-gray-900 mb-1">
              {t('detail.deleteConfirm.product')}
            </p>
            <p className="text-sm text-gray-600 line-clamp-2">{product.name}</p>
          </div>

          <div className="flex gap-3 justify-end">
            <Button
              variant="secondary"
              onClick={() => setShowDeleteModal(false)}
              disabled={isDeleting}
            >
              {t('detail.deleteConfirm.cancel')}
            </Button>
            <Button
              variant="danger"
              onClick={handleDelete}
              isLoading={isDeleting}
              leftIcon={<span className="material-symbols-outlined">delete</span>}
            >
              {t('detail.deleteConfirm.delete')}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
