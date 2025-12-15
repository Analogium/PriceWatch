import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { productsApi } from '@/api/products';
import { ProductForm } from '@/components/products';
import { Card, Button, Breadcrumb } from '@/components/ui';
import { useToast } from '@/contexts/ToastContext';
import type { ProductCreateFormData } from '@/utils/validators';
import type { Product } from '@/types';

export default function ProductAdd() {
  const navigate = useNavigate();
  const { success, error } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [scrapedProduct, setScrapedProduct] = useState<Product | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (data: ProductCreateFormData) => {
    try {
      setIsLoading(true);
      setScrapedProduct(null);
      setErrorMessage(null);

      // Appel à l'API pour créer le produit (le backend va scraper automatiquement)
      const newProduct = await productsApi.create({
        url: data.url,
        target_price: data.target_price,
        check_frequency: data.check_frequency,
      });

      setScrapedProduct(newProduct);
      success('Produit ajouté avec succès !');

      // Redirection vers le dashboard après 2 secondes pour laisser le temps de voir le produit
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      const finalMessage =
        message ||
        "Impossible d'ajouter le produit. Vérifiez que l'URL est valide et que le site est accessible.";
      setErrorMessage(finalMessage);
      error(finalMessage);
    } finally {
      setIsLoading(false);
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
            { label: 'Tableau de bord', href: '/dashboard', icon: 'home' },
            { label: 'Ajouter un produit', icon: 'add_shopping_cart' },
          ]}
        />
      </div>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Ajouter un produit</h1>
        <p className="text-gray-600">
          Ajoutez un produit à suivre en collant son URL. Nous allons automatiquement récupérer son
          nom, son image et son prix actuel.
        </p>
      </div>

      {/* Formulaire */}
      <Card>
        <ProductForm onSubmit={handleSubmit} isLoading={isLoading} />
      </Card>

      {/* Affichage du produit créé (feedback visuel) */}
      {scrapedProduct && (
        <Card className="mt-6 border-success-200 bg-success-50">
          <div className="flex items-start gap-4">
            <span className="material-symbols-outlined text-success-600 text-3xl">
              check_circle
            </span>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Produit ajouté avec succès !
              </h3>
              <p className="text-sm text-gray-600 mb-4">Redirection vers le tableau de bord...</p>

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
                        <span className="text-gray-500">Prix actuel : </span>
                        <span className="font-semibold text-gray-900">
                          {formatPrice(scrapedProduct.current_price)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Prix cible : </span>
                        <span className="font-semibold text-primary-600">
                          {formatPrice(scrapedProduct.target_price)}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Fréquence : </span>
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
      {isLoading && (
        <Card className="mt-6 border-primary-200 bg-primary-50">
          <div className="flex items-start gap-4">
            <div className="shrink-0">
              <div className="animate-spin h-6 w-6 border-2 border-primary-600 border-t-transparent rounded-full" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                Analyse du produit en cours...
              </h3>
              <p className="text-sm text-gray-600">
                Nous récupérons les informations du produit depuis le site marchand. Cela peut
                prendre quelques secondes.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Message d'erreur */}
      {errorMessage && !isLoading && (
        <Card className="mt-6 border-danger-200 bg-danger-50">
          <div className="flex items-start gap-4">
            <span className="material-symbols-outlined text-danger-600 text-3xl">error</span>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Échec de l'ajout du produit
              </h3>
              <p className="text-sm text-gray-700 mb-4">{errorMessage}</p>
              <div className="flex flex-col gap-2 text-sm text-gray-600">
                <p className="font-medium">Suggestions :</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Vérifiez que l'URL est correcte et complète</li>
                  <li>Assurez-vous que le site est accessible</li>
                  <li>Certains sites bloquent le scraping automatique</li>
                  <li>Essayez avec une URL différente</li>
                </ul>
              </div>
              <button
                onClick={() => setErrorMessage(null)}
                className="mt-4 px-4 py-2 bg-danger-600 text-white rounded-lg hover:bg-danger-700 transition-colors font-medium inline-flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-sm">close</span>
                Fermer
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
          disabled={isLoading}
          leftIcon={<span className="material-symbols-outlined">arrow_back</span>}
        >
          Retour au tableau de bord
        </Button>
      </div>
    </div>
  );
}
