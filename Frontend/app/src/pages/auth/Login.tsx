import { useState, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router';
import { GoogleLogin } from '@react-oauth/google';
import { useTranslation } from 'react-i18next';
import { Button, Input, Card } from '@/components/ui';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/contexts/ToastContext';
import { createLoginSchema } from '@/utils/validators';
import type { LoginCredentials } from '@/types';

export default function Login() {
  const { t, i18n } = useTranslation('auth');
  const navigate = useNavigate();
  const { login, loginWithGoogle } = useAuth();
  const { success, error } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // eslint-disable-next-line react-hooks/exhaustive-deps -- rebuild schema when language changes
  const schema = useMemo(() => createLoginSchema(), [i18n.language]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: LoginCredentials) => {
    setIsLoading(true);
    try {
      await login(data);
      success(t('login.successTitle'), t('login.successMessage'));
      navigate('/dashboard');
    } catch (err: unknown) {
      const detail =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      const isGoogleOnly = detail?.includes('Google sign-in');
      error(
        isGoogleOnly ? t('login.errorGoogleOnly') : detail || t('login.errorInvalid'),
        t('login.errorTitle')
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async (credential: string | undefined) => {
    if (!credential) return;
    setIsLoading(true);
    try {
      await loginWithGoogle(credential);
      success(t('login.successTitle'), t('login.successMessage'));
      navigate('/dashboard');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || t('login.errorGoogleFailed'), t('login.errorGeneric'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full">
        <Card padding="lg" className="max-w-[480px] mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-primary-600 mb-6">PriceWatch</h1>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('login.title')}</h2>
            <p className="text-gray-600 text-sm">{t('login.description')}</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <Input
                label={t('login.emailLabel')}
                type="email"
                placeholder={t('login.emailPlaceholder')}
                error={errors.email?.message}
                leftIcon={<span className="material-symbols-outlined text-xl">mail</span>}
                fullWidth
                {...register('email')}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-900">
                  {t('login.passwordLabel')}
                </label>
                <Link
                  to="/forgot-password"
                  className="text-sm font-medium text-primary-600 hover:text-primary-700"
                >
                  {t('login.forgotPassword')}
                </Link>
              </div>
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder={t('login.passwordPlaceholder')}
                error={errors.password?.message}
                leftIcon={<span className="material-symbols-outlined text-xl">lock</span>}
                rightIcon={
                  <span className="material-symbols-outlined text-xl">
                    {showPassword ? 'visibility' : 'visibility_off'}
                  </span>
                }
                rightIconClickable
                onRightIconClick={() => setShowPassword(!showPassword)}
                fullWidth
                {...register('password')}
              />
            </div>

            <Button
              type="submit"
              variant="primary"
              fullWidth
              isLoading={isLoading}
              className="h-12"
            >
              {t('login.submit')}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">{t('login.oauthDivider')}</span>
            </div>
          </div>

          {/* Google OAuth */}
          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={(credentialResponse) => {
                handleGoogleLogin(credentialResponse.credential);
              }}
              onError={() => {
                error(t('login.errorGoogleFailed'), t('login.errorGeneric'));
              }}
              text="continue_with"
              shape="rectangular"
              width="400"
            />
          </div>

          {/* Register Link */}
          <p className="text-center text-gray-600 text-sm mt-6">
            {t('login.noAccount')}{' '}
            <Link to="/register" className="font-semibold text-primary-600 hover:text-primary-700">
              {t('login.registerLink')}
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
