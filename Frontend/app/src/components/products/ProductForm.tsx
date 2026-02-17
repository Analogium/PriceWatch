import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createProductCreateSchema, type ProductCreateFormData } from '@/utils/validators';
import { Input, Button } from '@/components/ui';

interface ProductFormProps {
  onSubmit: (data: ProductCreateFormData) => void;
  isLoading?: boolean;
}

export function ProductForm({ onSubmit, isLoading = false }: ProductFormProps) {
  const { t } = useTranslation('products');

  const productCreateSchema = useMemo(() => createProductCreateSchema(), []);

  const CHECK_FREQUENCY_OPTIONS = useMemo(
    () => [
      { value: 6, label: t('frequency.every6h') },
      { value: 12, label: t('frequency.every12h') },
      { value: 24, label: t('frequency.every24h') },
    ],
    [t]
  );

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
          label={t('form.urlLabel')}
          type="url"
          placeholder={t('form.urlPlaceholder')}
          leftIcon={<span className="material-symbols-outlined">link</span>}
          error={errors.url?.message}
          disabled={isLoading}
          {...register('url')}
        />
        <p className="mt-2 text-sm text-gray-500">{t('form.urlHint')}</p>
      </div>

      {/* Prix cible */}
      <div>
        <Input
          label={t('form.priceLabel')}
          type="number"
          step="0.01"
          min="0.01"
          placeholder={t('form.pricePlaceholder')}
          leftIcon={<span className="material-symbols-outlined">euro</span>}
          error={errors.target_price?.message}
          disabled={isLoading}
          {...register('target_price', { valueAsNumber: true })}
        />
        <p className="mt-2 text-sm text-gray-500">{t('form.priceHint')}</p>
      </div>

      {/* Fréquence de vérification */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('form.frequencyLabel')}
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
                    <span className="material-symbols-outlined text-gray-400 text-xl">
                      schedule
                    </span>
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
        <p className="mt-2 text-sm text-gray-500">{t('form.frequencyHint')}</p>
      </div>

      {/* Bouton de soumission */}
      <div className="flex items-center gap-4 pt-4">
        <Button
          type="submit"
          isLoading={isLoading}
          fullWidth
          leftIcon={<span className="material-symbols-outlined">add_shopping_cart</span>}
        >
          {t('form.submit')}
        </Button>
      </div>
    </form>
  );
}
