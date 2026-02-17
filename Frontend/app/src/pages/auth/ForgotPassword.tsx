import { useState, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router';
import { useTranslation } from 'react-i18next';
import { Button, Input, Card } from '@/components/ui';
import { useToast } from '@/contexts/ToastContext';
import { createForgotPasswordSchema } from '@/utils/validators';
import { authApi } from '@/api';

type ForgotPasswordFormData = {
  email: string;
};

export default function ForgotPassword() {
  const { t, i18n } = useTranslation('auth');
  const { success, error } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  // eslint-disable-next-line react-hooks/exhaustive-deps -- rebuild schema when language changes
  const schema = useMemo(() => createForgotPasswordSchema(), [i18n.language]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    try {
      await authApi.forgotPassword(data.email);
      setEmailSent(true);
      success(t('forgotPassword.successMessage'), t('forgotPassword.successTitle'));
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || t('forgotPassword.errorGeneric'), t('forgotPassword.errorTitle'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full">
        {/* Card Container */}
        <Card padding="lg" className="max-w-[480px] mx-auto">
          {emailSent ? (
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-success-100 rounded-full mb-2">
                <span className="material-symbols-outlined text-success-600 text-3xl">
                  mark_email_read
                </span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">
                {t('forgotPassword.successPageTitle')}
              </h2>
              <p className="text-gray-600">{t('forgotPassword.successPageDescription')}</p>
              <div className="pt-4">
                <Link to="/login">
                  <Button variant="primary" fullWidth className="h-12">
                    {t('forgotPassword.successPageButton')}
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            <>
              {/* Header with Logo */}
              <div className="text-center mb-8">
                <div className="flex items-center justify-center gap-2 mb-6">
                  <span className="material-symbols-outlined text-primary-600 text-3xl">
                    monitoring
                  </span>
                  <h1 className="text-2xl font-bold text-gray-900">PriceWatch</h1>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {t('forgotPassword.title')}
                </h2>
                <p className="text-gray-600 text-sm">{t('forgotPassword.description')}</p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-1.5">
                    {t('forgotPassword.emailLabel')}
                  </label>
                  <Input
                    type="email"
                    placeholder={t('forgotPassword.emailPlaceholder')}
                    error={errors.email?.message}
                    leftIcon={<span className="material-symbols-outlined text-xl">mail</span>}
                    fullWidth
                    {...register('email')}
                  />
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  fullWidth
                  isLoading={isLoading}
                  className="h-12"
                >
                  {t('forgotPassword.submit')}
                </Button>
              </form>

              {/* Back to Login Link */}
              <div className="text-center mt-6">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
                >
                  <span className="material-symbols-outlined text-sm">arrow_back</span>
                  <span>{t('forgotPassword.backToLogin')}</span>
                </Link>
              </div>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}
