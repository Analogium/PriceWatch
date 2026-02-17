import { useState, useMemo } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router';
import { GoogleLogin } from '@react-oauth/google';
import { useTranslation } from 'react-i18next';
import { Button, Input, Card } from '@/components/ui';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/contexts/ToastContext';
import { createRegisterSchema } from '@/utils/validators';
import type { RegisterData } from '@/types';

export default function Register() {
  const { t, i18n } = useTranslation('auth');
  const navigate = useNavigate();
  const { register: registerUser, loginWithGoogle } = useAuth();
  const { success, error } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // eslint-disable-next-line react-hooks/exhaustive-deps -- rebuild schema when language changes
  const schema = useMemo(() => createRegisterSchema(), [i18n.language]);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterData>({
    resolver: zodResolver(schema),
  });

  const password = watch('password', '');

  // Password strength validation indicators
  const passwordChecks = {
    minLength: password.length >= 8,
    hasUpperCase: /[A-Z]/.test(password),
    hasLowerCase: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password),
    hasSpecialChar: /[^A-Za-z0-9]/.test(password),
  };

  const onSubmit = async (data: RegisterData) => {
    setIsLoading(true);
    try {
      await registerUser(data);
      success(t('register.successMessage'), t('register.successTitle'));
      navigate('/login');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || t('register.errorGeneric'), t('register.errorTitle'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleRegister = async (credential: string | undefined) => {
    if (!credential) return;
    setIsLoading(true);
    try {
      await loginWithGoogle(credential);
      success(t('register.googleSuccessTitle'), t('register.googleSuccessMessage'));
      navigate('/dashboard');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || t('register.googleError'), t('register.errorTitle'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full">
        {/* Card Container */}
        <Card padding="lg" className="max-w-[480px] mx-auto">
          {/* Header with Logo */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-2 mb-6">
              <span className="material-symbols-outlined text-primary-600 text-3xl">
                monitoring
              </span>
              <h1 className="text-2xl font-bold text-gray-900">PriceWatch</h1>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('register.title')}</h2>
            <p className="text-gray-600 text-sm">{t('register.description')}</p>
          </div>

          {/* Register Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-1.5">
                {t('register.emailLabel')}
              </label>
              <Input
                type="email"
                placeholder={t('register.emailPlaceholder')}
                error={errors.email?.message}
                leftIcon={<span className="material-symbols-outlined text-xl">mail</span>}
                fullWidth
                {...register('email')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 mb-1.5">
                {t('register.passwordLabel')}
              </label>
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder={t('register.passwordPlaceholder')}
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

            <div>
              <label className="block text-sm font-medium text-gray-900 mb-1.5">
                {t('register.confirmPasswordLabel')}
              </label>
              <Input
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder={t('register.confirmPasswordPlaceholder')}
                error={errors.confirmPassword?.message}
                leftIcon={<span className="material-symbols-outlined text-xl">lock</span>}
                rightIcon={
                  <span className="material-symbols-outlined text-xl">
                    {showConfirmPassword ? 'visibility' : 'visibility_off'}
                  </span>
                }
                rightIconClickable
                onRightIconClick={() => setShowConfirmPassword(!showConfirmPassword)}
                fullWidth
                {...register('confirmPassword')}
              />
            </div>

            {/* Password strength indicators */}
            {password && (
              <div className="space-y-2">
                <div className="space-y-1.5">
                  <PasswordRequirement
                    met={passwordChecks.minLength}
                    text={t('passwordRequirements.minLength')}
                  />
                  <PasswordRequirement
                    met={passwordChecks.hasUpperCase}
                    text={t('passwordRequirements.uppercase')}
                  />
                  <PasswordRequirement
                    met={passwordChecks.hasLowerCase}
                    text={t('passwordRequirements.lowercase')}
                  />
                  <PasswordRequirement
                    met={passwordChecks.hasNumber}
                    text={t('passwordRequirements.number')}
                  />
                  <PasswordRequirement
                    met={passwordChecks.hasSpecialChar}
                    text={t('passwordRequirements.specialChar')}
                  />
                </div>
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              fullWidth
              isLoading={isLoading}
              className="h-12 mt-6"
            >
              {t('register.submit')}
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">{t('register.oauthDivider')}</span>
            </div>
          </div>

          {/* Google OAuth */}
          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={(credentialResponse) => {
                handleGoogleRegister(credentialResponse.credential);
              }}
              onError={() => {
                error(t('register.googleError'), t('register.errorTitle'));
              }}
              text="signup_with"
              shape="rectangular"
              width="400"
            />
          </div>

          {/* Login Link */}
          <p className="text-center text-gray-600 text-sm mt-6">
            {t('register.hasAccount')}{' '}
            <Link to="/login" className="font-semibold text-primary-600 hover:text-primary-700">
              {t('register.loginLink')}
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}

// Helper component for password requirements
function PasswordRequirement({ met, text }: { met: boolean; text: string }) {
  return (
    <div className="flex items-center gap-2.5">
      {met ? (
        <svg className="w-5 h-5 text-success-600 shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clipRule="evenodd"
          />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-gray-300 shrink-0" fill="none" viewBox="0 0 20 20">
          <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />
        </svg>
      )}
      <span className={`text-sm ${met ? 'text-gray-900' : 'text-gray-600'}`}>{text}</span>
    </div>
  );
}
