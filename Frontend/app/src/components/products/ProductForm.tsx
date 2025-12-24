import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { productCreateSchema, type ProductCreateFormData } from '@/utils/validators';
import { Input, Button } from '@/components/ui';

interface ProductFormProps {
  onSubmit: (data: ProductCreateFormData) => void;
  isLoading?: boolean;
}

const CHECK_FREQUENCY_OPTIONS = [
  { value: 6, label: 'Toutes les 6 heures' },
  { value: 12, label: 'Toutes les 12 heures' },
  { value: 24, label: 'Toutes les 24 heures' },
];

export function ProductForm({ onSubmit, isLoading = false }: ProductFormProps) {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<ProductCreateFormData>({
    resolver: zodResolver(productCreateSchema),
    defaultValues: {
      url: '',
      target_price: undefined,
      check_frequency: 24,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* URL du produit */}
      <div>
        <Input
          label="URL du produit"
          type="url"
          placeholder="https://www.exemple.com/produit"
          leftIcon={<span className="material-symbols-outlined">link</span>}
          error={errors.url?.message}
          disabled={isLoading}
          {...register('url')}
        />
        <p className="mt-2 text-sm text-gray-500">
          Collez l'URL complète du produit que vous souhaitez suivre
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
          disabled={isLoading}
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
        <Controller
          name="check_frequency"
          control={control}
          render={({ field }) => (
            <div className="space-y-3">
              {CHECK_FREQUENCY_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-3 p-4 border border-gray-300 rounded-lg cursor-pointer hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <input
                    type="radio"
                    name={field.name}
                    value={option.value}
                    disabled={isLoading}
                    checked={field.value === option.value}
                    onChange={() => field.onChange(option.value)}
                    onBlur={field.onBlur}
                    className="w-4 h-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                  />
                  <span className="flex items-center gap-2 text-gray-900 font-medium">
                    <span className="material-symbols-outlined text-gray-400 text-xl">schedule</span>
                    {option.label}
                  </span>
                </label>
              ))}
            </div>
          )}
        />
        {errors.check_frequency && (
          <p className="mt-2 text-sm text-danger-600">{errors.check_frequency.message}</p>
        )}
        <p className="mt-2 text-sm text-gray-500">
          À quelle fréquence souhaitez-vous que nous vérifiions le prix ?
        </p>
      </div>

      {/* Bouton de soumission */}
      <div className="flex items-center gap-4 pt-4">
        <Button
          type="submit"
          isLoading={isLoading}
          fullWidth
          leftIcon={<span className="material-symbols-outlined">add_shopping_cart</span>}
        >
          Ajouter le produit
        </Button>
      </div>
    </form>
  );
}
