import { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { Card, Button, Toggle, Select, Input, Spinner, Breadcrumb } from '@/components/ui';
import { preferencesApi, usersApi } from '@/api';
import type { UserPreferences, UserPreferencesUpdate, WebhookType } from '@/types';
import type { Language } from '@/types/preferences';
import { WEBHOOK_TYPES } from '@/utils';
import { useToast } from '@/contexts/ToastContext';
import { useAuth } from '@/hooks/useAuth';
import i18n from '@/i18n';

type PreferencesFormData = Omit<UserPreferences, 'id' | 'user_id'>;

export default function Settings() {
  const { t } = useTranslation('settings');
  const { t: tl } = useTranslation('legal');
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
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
      language: (i18n.language as Language) || 'fr',
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
        language: data.language || 'fr',
      });
    } catch {
      info(t('loadingError'));
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
        language: data.language,
      };

      let updatedPreferences: UserPreferences;
      if (preferences) {
        updatedPreferences = await preferencesApi.update(updateData);
        success(t('saveSuccess'));
      } else {
        updatedPreferences = await preferencesApi.create(updateData);
        success(t('createSuccess'));
      }

      // Sync i18n language
      if (data.language && data.language !== i18n.language) {
        i18n.changeLanguage(data.language);
      }

      setPreferences(updatedPreferences);
      reset({
        email_notifications: updatedPreferences.email_notifications,
        webhook_notifications: updatedPreferences.webhook_notifications,
        webhook_url: updatedPreferences.webhook_url,
        webhook_type: updatedPreferences.webhook_type,
        price_drop_alerts: updatedPreferences.price_drop_alerts,
        weekly_summary: updatedPreferences.weekly_summary,
        language: updatedPreferences.language || 'fr',
      });
    } catch {
      error(t('saveError'));
    } finally {
      setIsSaving(false);
    }
  };

  const handleExportData = async () => {
    try {
      setIsExporting(true);
      const blob = await usersApi.exportData();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'pricewatch_data.json';
      a.click();
      URL.revokeObjectURL(url);
      success(tl('settings.gdpr.exportSuccess'));
    } catch {
      error(tl('settings.gdpr.exportError'));
    } finally {
      setIsExporting(false);
    }
  };

  const handleDeleteAccount = async () => {
    try {
      setIsDeleting(true);
      const isGoogleOnly = user?.auth_provider === 'google';
      await usersApi.deleteAccount(isGoogleOnly ? undefined : deletePassword);
      success(tl('settings.gdpr.deleteSuccess'));
      logout();
      navigate('/');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || tl('settings.gdpr.deleteError'));
    } finally {
      setIsDeleting(false);
      setIsDeleteModalOpen(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Breadcrumb
            items={[
              { label: t('common:breadcrumb.dashboard'), href: '/dashboard', icon: 'home' },
              { label: t('breadcrumb'), icon: 'settings' },
            ]}
          />
        </div>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">{t('title')}</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">{t('subtitle')}</p>
        </div>
        <div className="flex justify-center items-center py-20">
          <Spinner size="lg" variant="primary" label={t('loading')} />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <Breadcrumb
          items={[
            { label: t('common:breadcrumb.dashboard'), href: '/dashboard', icon: 'home' },
            { label: t('breadcrumb'), icon: 'settings' },
          ]}
        />
      </div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">{t('title')}</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">{t('subtitle')}</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Section Langue */}
        <Card>
          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary-600">language</span>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {t('language.title')}
                </h2>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                {t('language.description')}
              </p>
            </div>

            <Controller
              name="language"
              control={control}
              render={({ field }) => (
                <Select
                  id="language"
                  label={t('language.label')}
                  leftIcon="translate"
                  options={[
                    { value: 'fr', label: t('language.fr') },
                    { value: 'en', label: t('language.en') },
                  ]}
                  value={field.value || 'fr'}
                  onChange={(e) => field.onChange(e.target.value as Language)}
                />
              )}
            />
          </div>
        </Card>

        {/* Section Notifications Email */}
        <Card>
          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary-600">mail</span>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {t('email.title')}
                </h2>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                {t('email.description')}
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
                  label={t('email.toggle')}
                  description={t('email.toggleDescription')}
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
                      label={t('email.priceAlerts')}
                      description={t('email.priceAlertsDescription')}
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
                      label={t('email.weeklySummary')}
                      description={t('email.weeklySummaryDescription')}
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
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {t('webhooks.title')}
                </h2>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                {t('webhooks.description')}
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
                  label={t('webhooks.toggle')}
                  description={t('webhooks.toggleDescription')}
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
                      label={t('webhooks.typeLabel')}
                      helperText={t('webhooks.typeHelper')}
                      leftIcon="settings"
                      options={WEBHOOK_TYPES}
                      placeholder={t('webhooks.typePlaceholder')}
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
                      label={t('webhooks.urlLabel')}
                      placeholder={t('webhooks.urlPlaceholder')}
                      helperText={t('webhooks.urlHelper')}
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

        {/* Section RGPD */}
        <Card>
          <div className="space-y-6">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-primary-600">shield_person</span>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {tl('settings.gdpr.title')}
                </h2>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                {tl('settings.gdpr.description')}
              </p>
            </div>

            {/* Export */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {tl('settings.gdpr.exportTitle')}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  {tl('settings.gdpr.exportDescription')}
                </p>
              </div>
              <Button
                type="button"
                variant="secondary"
                isLoading={isExporting}
                onClick={handleExportData}
                className="shrink-0"
              >
                <span className="material-symbols-outlined">download</span>
                {tl('settings.gdpr.exportButton')}
              </Button>
            </div>

            {/* Delete */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 bg-red-50 dark:bg-red-950 rounded-lg border border-red-100 dark:border-red-900">
              <div>
                <p className="text-sm font-medium text-red-700 dark:text-red-400">
                  {tl('settings.gdpr.deleteTitle')}
                </p>
                <p className="text-xs text-red-500 dark:text-red-500 mt-0.5">
                  {tl('settings.gdpr.deleteDescription')}
                </p>
              </div>
              <Button
                type="button"
                variant="danger"
                onClick={() => setIsDeleteModalOpen(true)}
                className="shrink-0"
              >
                <span className="material-symbols-outlined">delete_forever</span>
                {tl('settings.gdpr.deleteButton')}
              </Button>
            </div>
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
            {t('common:buttons.cancel')}
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={isSaving}
            disabled={!isDirty || isSaving}
          >
            <span className="material-symbols-outlined">save</span>
            {t('common:buttons.save')}
          </Button>
        </div>
      </form>

      {/* Delete account modal */}
      {isDeleteModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="material-symbols-outlined text-red-600 text-2xl">warning</span>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {tl('settings.gdpr.deleteModal.title')}
              </h3>
            </div>

            <p className="text-sm text-red-600 dark:text-red-400 mb-4">
              {tl('settings.gdpr.deleteModal.warning')}
            </p>

            {user?.auth_provider === 'google' ? (
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 italic">
                {tl('settings.gdpr.deleteModal.googleNote')}
              </p>
            ) : (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  {tl('settings.gdpr.deleteModal.passwordLabel')}
                </label>
                <input
                  type="password"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-red-500"
                  placeholder={tl('settings.gdpr.deleteModal.passwordPlaceholder')}
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                />
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  setIsDeleteModalOpen(false);
                  setDeletePassword('');
                }}
                disabled={isDeleting}
              >
                {tl('settings.gdpr.deleteModal.cancel')}
              </Button>
              <Button
                type="button"
                variant="danger"
                isLoading={isDeleting}
                onClick={handleDeleteAccount}
              >
                {tl('settings.gdpr.deleteModal.confirm')}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
