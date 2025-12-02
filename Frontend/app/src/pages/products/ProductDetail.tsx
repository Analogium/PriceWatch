import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { productsApi } from '@/api/products';
import { Card, Button, Badge, Modal } from '@/components/ui';
import { useToast } from '@/contexts/ToastContext';
import { formatPrice, formatDateTime, formatRelativeTime } from '@/utils/formatters';
import type { Product } from '@/types';

export default function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { success, error } = useToast();

  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCheckingPrice, setIsCheckingPrice] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Load product data
  useEffect(() => {
    const fetchProduct = async () => {
      if (!id) return;

      try {
        setIsLoading(true);
        const data = await productsApi.getById(Number(id));
        setProduct(data);
      } catch {
        error('Impossible de charger le produit');
        navigate('/dashboard');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProduct();
  }, [id, navigate, error]);

  // Check price now
  const handleCheckPrice = async () => {
    if (!product) return;

    try {
      setIsCheckingPrice(true);
      const updatedProduct = await productsApi.checkPrice(product.id);
      setProduct(updatedProduct);
      success('Prix vérifié avec succès !');
    } catch {
      error('Impossible de vérifier le prix');
    } finally {
      setIsCheckingPrice(false);
    }
  };

  // Delete product
  const handleDelete = async () => {
    if (!product) return;

    try {
      setIsDeleting(true);
      await productsApi.delete(product.id);
      success('Produit supprimé avec succès');
      navigate('/dashboard');
    } catch {
      error('Impossible de supprimer le produit');
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
      {/* Back button */}
      <div className="mb-6">
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <span className="material-symbols-outlined text-xl">arrow_back</span>
          <span>Retour au tableau de bord</span>
        </Link>
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
                    Indisponible
                  </Badge>
                ) : isPriceReached ? (
                  <Badge variant="success">
                    <span className="material-symbols-outlined text-sm">check_circle</span>
                    Prix cible atteint
                  </Badge>
                ) : (
                  <Badge variant="neutral">
                    <span className="material-symbols-outlined text-sm">trending_down</span>
                    En surveillance
                  </Badge>
                )}
              </div>

              {/* Prices */}
              <div className="space-y-3 mb-6">
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <span className="text-gray-600">Prix actuel</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {formatPrice(product.current_price)}
                  </span>
                </div>
                <div className="flex items-center justify-between py-3 border-b border-gray-200">
                  <span className="text-gray-600">Prix cible</span>
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
                <span>Voir sur le site marchand</span>
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
                <p className="text-sm font-medium text-gray-900">Fréquence de vérification</p>
                <p className="text-sm text-gray-600">Toutes les {product.check_frequency} heures</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <span className="material-symbols-outlined text-gray-400 text-xl">update</span>
              <div>
                <p className="text-sm font-medium text-gray-900">Dernière vérification</p>
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
                <p className="text-sm font-medium text-gray-900">Date de création</p>
                <p className="text-sm text-gray-600">{formatDateTime(product.created_at)}</p>
              </div>
            </div>

            {product.unavailable_since && (
              <div className="flex items-start gap-3">
                <span className="material-symbols-outlined text-danger-600 text-xl">error</span>
                <div>
                  <p className="text-sm font-medium text-gray-900">Indisponible depuis</p>
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
              isLoading={isCheckingPrice}
              leftIcon={<span className="material-symbols-outlined">refresh</span>}
            >
              Vérifier le prix maintenant
            </Button>

            <Button
              variant="secondary"
              onClick={() => navigate(`/products/${product.id}/edit`)}
              leftIcon={<span className="material-symbols-outlined">edit</span>}
            >
              Modifier
            </Button>

            <Button
              variant="danger"
              onClick={() => setShowDeleteModal(true)}
              leftIcon={<span className="material-symbols-outlined">delete</span>}
            >
              Supprimer
            </Button>
          </div>
        </div>
      </Card>

      {/* Delete confirmation modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Confirmer la suppression"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            Êtes-vous sûr de vouloir supprimer ce produit ? Cette action est irréversible.
          </p>

          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <p className="text-sm font-medium text-gray-900 mb-1">Produit à supprimer :</p>
            <p className="text-sm text-gray-600 line-clamp-2">{product.name}</p>
          </div>

          <div className="flex gap-3 justify-end">
            <Button
              variant="secondary"
              onClick={() => setShowDeleteModal(false)}
              disabled={isDeleting}
            >
              Annuler
            </Button>
            <Button
              variant="danger"
              onClick={handleDelete}
              isLoading={isDeleting}
              leftIcon={<span className="material-symbols-outlined">delete</span>}
            >
              Supprimer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
