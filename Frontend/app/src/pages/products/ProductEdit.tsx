import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { productUpdateSchema, type ProductUpdateFormData } from '@/utils/validators';
import { productsApi } from '@/api';
import { Input, Button, Card, Breadcrumb } from '@/components/ui';
import { useToast } from '@/contexts/ToastContext';
import type { Product } from '@/types';

const CHECK_FREQUENCY_OPTIONS = [
  { value: 6, label: 'Toutes les 6 heures' },
  { value: 12, label: 'Toutes les 12 heures' },
  { value: 24, label: 'Toutes les 24 heures' },
];

export default function ProductEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { success, error } = useToast();

  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ProductUpdateFormData>({
    resolver: zodResolver(productUpdateSchema),
  });

  // Load product data
  useEffect(() => {
    const fetchProduct = async () => {
      if (!id) return;
      try {
        setIsLoading(true);
        const data = await productsApi.getById(Number(id));
        setProduct(data);
        // Pre-fill form with product data
        reset({
          name: data.name,
          target_price: data.target_price,
          check_frequency: data.check_frequency,
        });
      } catch {
        error('Impossible de charger le produit');
        navigate('/dashboard');
      } finally {
        setIsLoading(false);
      }
    };
    fetchProduct();
  }, [id, navigate, error, reset]);

  const onSubmit = async (data: ProductUpdateFormData) => {
    if (!product) return;

    try {
      setIsSubmitting(true);
      const updatedProduct = await productsApi.update(product.id, data);
      setProduct(updatedProduct);
      success('Produit modifié avec succès !');
      navigate(`/products/${product.id}`);
    } catch {
      error('Impossible de modifier le produit');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="space-y-4">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return null;
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Breadcrumb navigation */}
      <div className="mb-6">
        <Breadcrumb
          items={[
            { label: 'Tableau de bord', href: '/dashboard', icon: 'home' },
            { label: product.name, href: `/products/${product.id}`, icon: 'shopping_bag' },
            { label: 'Modifier', icon: 'edit' },
          ]}
        />
      </div>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Modifier le produit</h1>
        <p className="text-gray-600 mt-2">Modifiez les informations de votre produit</p>
      </div>

      {/* Form */}
      <Card>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Nom du produit */}
          <div>
            <Input
              label="Nom du produit"
              type="text"
              placeholder="Nom du produit"
              leftIcon={<span className="material-symbols-outlined">shopping_bag</span>}
              error={errors.name?.message}
              disabled={isSubmitting}
              {...register('name')}
            />
            <p className="mt-2 text-sm text-gray-500">
              Vous pouvez personnaliser le nom du produit
            </p>
          </div>

          {/* Prix cible */}
          <div>
            <Input
              label="Prix cible (€)"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="99.99"
              leftIcon={<span className="material-symbols-outlined">euro</span>}
              error={errors.target_price?.message}
              disabled={isSubmitting}
              {...register('target_price', { valueAsNumber: true })}
            />
            <p className="mt-2 text-sm text-gray-500">
              Vous serez notifié lorsque le prix descendra en dessous de ce montant
            </p>
          </div>

          {/* Fréquence de vérification */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fréquence de vérification
            </label>
            <div className="space-y-3">
              {CHECK_FREQUENCY_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-3 p-4 border border-gray-300 rounded-lg cursor-pointer hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <input
                    type="radio"
                    value={option.value}
                    disabled={isSubmitting}
                    {...register('check_frequency')}
                    className="w-4 h-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                  />
                  <span className="flex items-center gap-2 text-gray-900 font-medium">
                    <span className="material-symbols-outlined text-gray-400 text-xl">
                      schedule
                    </span>
                    {option.label}
                  </span>
                </label>
              ))}
            </div>
            {errors.check_frequency && (
              <p className="mt-2 text-sm text-danger-600">{errors.check_frequency.message}</p>
            )}
            <p className="mt-2 text-sm text-gray-500">
              À quelle fréquence souhaitez-vous que nous vérifiions le prix ?
            </p>
          </div>

          {/* Boutons d'action */}
          <div className="flex items-center gap-4 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate(`/products/${product.id}`)}
              disabled={isSubmitting}
            >
              Annuler
            </Button>
            <Button
              type="submit"
              isLoading={isSubmitting}
              fullWidth
              leftIcon={<span className="material-symbols-outlined">save</span>}
            >
              Sauvegarder
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
