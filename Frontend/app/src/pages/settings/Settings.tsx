import { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Card, Button, Toggle, Select, Input, Spinner, Breadcrumb } from '@/components/ui';
import { preferencesApi } from '@/api';
import type { UserPreferences, UserPreferencesUpdate, WebhookType } from '@/types';
import { WEBHOOK_TYPES } from '@/utils';
import { useToast } from '@/contexts/ToastContext';

type PreferencesFormData = Omit<UserPreferences, 'id' | 'user_id'>;

export default function Settings() {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const { success, error, info } = useToast();

  const {
    control,
    handleSubmit,
    reset,
    watch,
    formState: { isDirty },
  } = useForm<PreferencesFormData>({
    defaultValues: {
      email_notifications: false,
      webhook_notifications: false,
      webhook_url: null,
      webhook_type: null,
      price_drop_alerts: false,
      weekly_summary: false,
    },
  });

  const emailNotificationsEnabled = watch('email_notifications');
  const webhookNotificationsEnabled = watch('webhook_notifications');

  const loadPreferences = async () => {
    try {
      setIsLoading(true);
      const data = await preferencesApi.get();
      setPreferences(data);
      reset({
        email_notifications: data.email_notifications,
        webhook_notifications: data.webhook_notifications,
        webhook_url: data.webhook_url,
        webhook_type: data.webhook_type,
        price_drop_alerts: data.price_drop_alerts,
        weekly_summary: data.weekly_summary,
      });
    } catch {
      info('Impossible de charger les préférences. Utilisation des valeurs par défaut.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPreferences();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSubmit = async (data: PreferencesFormData) => {
    try {
      setIsSaving(true);

      const updateData: UserPreferencesUpdate = {
        email_notifications: data.email_notifications,
        webhook_notifications: data.webhook_notifications,
        webhook_url: data.webhook_url || null,
        webhook_type: data.webhook_type || null,
        price_drop_alerts: data.price_drop_alerts,
        weekly_summary: data.weekly_summary,
      };

      let updatedPreferences: UserPreferences;
      if (preferences) {
        updatedPreferences = await preferencesApi.update(updateData);
        success('Préférences mises à jour avec succès !');
      } else {
        updatedPreferences = await preferencesApi.create(updateData);
        success('Préférences créées avec succès !');
      }

      setPreferences(updatedPreferences);
      reset({
        email_notifications: updatedPreferences.email_notifications,
        webhook_notifications: updatedPreferences.webhook_notifications,
        webhook_url: updatedPreferences.webhook_url,
        webhook_type: updatedPreferences.webhook_type,
        price_drop_alerts: updatedPreferences.price_drop_alerts,
        weekly_summary: updatedPreferences.weekly_summary,
      });
    } catch {
      error('Impossible de sauvegarder les préférences');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Breadcrumb
            items={[
              { label: 'Tableau de bord', href: '/dashboard', icon: 'home' },
              { label: 'Paramètres', icon: 'settings' },
            ]}
          />
        </div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Paramètres</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Gérez vos préférences de notifications et webhooks
          </p>
        </div>
        <div className="flex justify-center items-center py-20">
          <Spinner size="lg" variant="primary" label="Chargement des préférences..." />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <Breadcrumb
          items={[
            { label: 'Tableau de bord', href: '/dashboard', icon: 'home' },
            { label: 'Paramètres', icon: 'settings' },
          ]}
        />
      </div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Paramètres</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Gérez vos préférences de notifications et webhooks
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Section Notifications Email */}
        <Card>
          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary-600">mail</span>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  Notifications par email
                </h2>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                Recevez des notifications par email pour suivre vos produits
              </p>
            </div>

            <Controller
              name="email_notifications"
              control={control}
              render={({ field }) => (
                <Toggle
                  id="email_notifications"
                  checked={field.value}
                  onChange={field.onChange}
                  label="Activer les notifications par email"
                  description="Recevez des emails pour les alertes de prix et de disponibilité"
                />
              )}
            />

            {emailNotificationsEnabled && (
              <div className="pl-14 space-y-4 border-l-2 border-gray-200 dark:border-gray-700">
                <Controller
                  name="price_drop_alerts"
                  control={control}
                  render={({ field }) => (
                    <Toggle
                      id="price_drop_alerts"
                      checked={field.value}
                      onChange={field.onChange}
                      label="Alertes de baisse de prix"
                      description="Recevoir un email quand un produit atteint le prix cible"
                    />
                  )}
                />

                <Controller
                  name="weekly_summary"
                  control={control}
                  render={({ field }) => (
                    <Toggle
                      id="weekly_summary"
                      checked={field.value}
                      onChange={field.onChange}
                      label="Résumé hebdomadaire"
                      description="Recevoir un résumé hebdomadaire de vos produits suivis"
                    />
                  )}
                />
              </div>
            )}
          </div>
        </Card>

        {/* Section Webhooks */}
        <Card>
          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary-600">webhook</span>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Webhooks</h2>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                Envoyez des notifications vers vos services externes (Slack, Discord, etc.)
              </p>
            </div>

            <Controller
              name="webhook_notifications"
              control={control}
              render={({ field }) => (
                <Toggle
                  id="webhook_notifications"
                  checked={field.value}
                  onChange={field.onChange}
                  label="Activer les notifications webhook"
                  description="Envoyez des alertes vers une URL webhook externe"
                />
              )}
            />

            {webhookNotificationsEnabled && (
              <div className="pl-14 space-y-4 border-l-2 border-gray-200 dark:border-gray-700">
                <Controller
                  name="webhook_type"
                  control={control}
                  render={({ field }) => (
                    <Select
                      id="webhook_type"
                      label="Type de webhook"
                      helperText="Sélectionnez le type de webhook (Slack, Discord ou Custom)"
                      leftIcon="settings"
                      options={WEBHOOK_TYPES}
                      placeholder="Sélectionnez un type"
                      value={field.value || ''}
                      onChange={(e) =>
                        field.onChange(e.target.value ? (e.target.value as WebhookType) : null)
                      }
                    />
                  )}
                />

                <Controller
                  name="webhook_url"
                  control={control}
                  render={({ field }) => (
                    <Input
                      id="webhook_url"
                      type="url"
                      label="URL du webhook"
                      placeholder="https://hooks.slack.com/services/..."
                      helperText="L'URL complète de votre webhook"
                      leftIcon="link"
                      value={field.value || ''}
                      onChange={field.onChange}
                    />
                  )}
                />
              </div>
            )}
          </div>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-3">
          <Button
            type="button"
            variant="secondary"
            onClick={() => reset()}
            disabled={!isDirty || isSaving}
          >
            Annuler
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={isSaving}
            disabled={!isDirty || isSaving}
          >
            <span className="material-symbols-outlined">save</span>
            Sauvegarder
          </Button>
        </div>
      </form>
    </div>
  );
}
