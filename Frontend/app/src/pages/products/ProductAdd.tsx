import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useCreateProduct } from '@/hooks/useProducts';
import { ProductForm } from '@/components/products';
import { Card, Button, Breadcrumb } from '@/components/ui';
import { useToast } from '@/contexts/ToastContext';
import type { ProductCreateFormData } from '@/utils/validators';
import type { Product } from '@/types';

export default function ProductAdd() {
  const { t } = useTranslation('products');
  const navigate = useNavigate();
  const { success, error } = useToast();
  const createProduct = useCreateProduct();
  const [scrapedProduct, setScrapedProduct] = useState<Product | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (data: ProductCreateFormData) => {
    try {
      setScrapedProduct(null);
      setErrorMessage(null);

      // Appel à l'API pour créer le produit (le backend va scraper automatiquement)
      // Le hook useCreateProduct va automatiquement invalider le cache React Query
      const newProduct = await createProduct.mutateAsync({
        url: data.url,
        target_price: data.target_price,
        check_frequency: data.check_frequency,
      });

      setScrapedProduct(newProduct);
      success(t('add.success'));

      // Redirection vers le dashboard après 2 secondes pour laisser le temps de voir le produit
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      const finalMessage = message || t('add.errorGeneric');
      setErrorMessage(finalMessage);
      error(finalMessage);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
    }).format(price);
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Breadcrumb navigation */}
      <div className="mb-6">
        <Breadcrumb
          items={[
            { label: t('common:breadcrumb.dashboard'), href: '/dashboard', icon: 'home' },
            { label: t('add.breadcrumb'), icon: 'add_shopping_cart' },
          ]}
        />
      </div>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{t('add.title')}</h1>
        <p className="text-gray-600">{t('add.description')}</p>
      </div>

      {/* Formulaire */}
      <Card>
        <ProductForm onSubmit={handleSubmit} isLoading={createProduct.isPending} />
      </Card>

      {/* Affichage du produit créé (feedback visuel) */}
      {scrapedProduct && (
        <Card className="mt-6 border-success-200 bg-success-50">
          <div className="flex items-start gap-4">
            <span className="material-symbols-outlined text-success-600 text-3xl">
              check_circle
            </span>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('add.preview.title')}</h3>
              <p className="text-sm text-gray-600 mb-4">{t('add.redirect')}</p>

              {/* Aperçu du produit */}
              <div className="bg-white rounded-lg border border-success-200 overflow-hidden">
                <div className="flex gap-4 p-4">
                  {/* Image */}
                  {scrapedProduct.image && (
                    <div className="shrink-0">
                      <img
                        src={scrapedProduct.image}
                        alt={scrapedProduct.name}
                        className="w-20 h-20 object-cover rounded"
                      />
                    </div>
                  )}

                  {/* Informations */}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900 mb-1 line-clamp-2">
                      {scrapedProduct.name}
                    </h4>
                    <div className="flex flex-wrap items-center gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">{t('add.preview.currentPrice')}</span>
                        <span className="font-semibold text-gray-900">
                          {formatPrice(scrapedProduct.current_price)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">{t('add.preview.targetPrice')}</span>
                        <span className="font-semibold text-primary-600">
                          {formatPrice(scrapedProduct.target_price)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">{t('add.preview.frequency')}</span>
                        <span className="font-medium text-gray-900">
                          {scrapedProduct.check_frequency}h
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Message d'information pendant le scraping */}
      {createProduct.isPending && (
        <Card className="mt-6 border-primary-200 bg-primary-50">
          <div className="flex items-start gap-4">
            <div className="shrink-0">
              <div className="animate-spin h-6 w-6 border-2 border-primary-600 border-t-transparent rounded-full" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">{t('add.loading.title')}</h3>
              <p className="text-sm text-gray-600">{t('add.loading.description')}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Message d'erreur */}
      {errorMessage && !createProduct.isPending && (
        <Card className="mt-6 border-danger-200 bg-danger-50">
          <div className="flex items-start gap-4">
            <span className="material-symbols-outlined text-danger-600 text-3xl">error</span>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{t('add.error.title')}</h3>
              <p className="text-sm text-gray-700 mb-4">{errorMessage}</p>
              <div className="flex flex-col gap-2 text-sm text-gray-600">
                <p className="font-medium">{t('add.error.suggestions')}</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>{t('add.error.suggestion1')}</li>
                  <li>{t('add.error.suggestion2')}</li>
                  <li>{t('add.error.suggestion3')}</li>
                  <li>{t('add.error.suggestion4')}</li>
                </ul>
              </div>
              <button
                onClick={() => setErrorMessage(null)}
                className="mt-4 px-4 py-2 bg-danger-600 text-white rounded-lg hover:bg-danger-700 transition-colors font-medium inline-flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-sm">close</span>
                {t('common:buttons.close')}
              </button>
            </div>
          </div>
        </Card>
      )}

      {/* Bouton retour */}
      <div className="mt-6 flex justify-center">
        <Button
          variant="secondary"
          onClick={() => navigate('/dashboard')}
          disabled={createProduct.isPending}
          leftIcon={<span className="material-symbols-outlined">arrow_back</span>}
        >
          {t('common:buttons.backToDashboard')}
        </Button>
      </div>
    </div>
  );
}
