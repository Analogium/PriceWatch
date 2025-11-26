import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useSearchParams } from 'react-router';
import { Button, Input, Card } from '@/components/ui';
import { useToast } from '@/hooks/useToast';
import { resetPasswordSchema } from '@/utils/validators';
import { authApi } from '@/api';

type ResetPasswordFormData = {
  password: string;
  confirmPassword: string;
};

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const { success, error } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  const token = searchParams.get('token');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
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

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) {
      error('Le lien de réinitialisation est invalide', 'Erreur');
      return;
    }

    setIsLoading(true);
    try {
      await authApi.resetPassword(token, data.password);
      setResetSuccess(true);
      success(
        'Vous pouvez maintenant vous connecter avec votre nouveau mot de passe',
        'Mot de passe réinitialisé !'
      );
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || 'Le lien de réinitialisation est invalide ou expiré', 'Erreur');
    } finally {
      setIsLoading(false);
    }
  };

  // Check if token is present
  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
        <div className="max-w-md w-full">
          <Card padding="lg">
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-danger-100 rounded-full mb-2">
                <span className="material-symbols-outlined text-danger-600 text-3xl">error</span>
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Lien invalide</h2>
              <p className="text-gray-600">Le lien de réinitialisation est invalide ou a expiré.</p>
              <div className="pt-4">
                <Link to="/forgot-password">
                  <Button variant="primary" fullWidth>
                    Demander un nouveau lien
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full">
        {/* Card Container */}
        <Card padding="lg" className="max-w-[480px] mx-auto">
          {resetSuccess ? (
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-success-100 rounded-full mb-2">
                <span className="material-symbols-outlined text-success-600 text-3xl">
                  check_circle
                </span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Mot de passe réinitialisé !</h2>
              <p className="text-gray-600">
                Votre mot de passe a été modifié avec succès. Vous pouvez maintenant vous connecter.
              </p>
              <div className="pt-4">
                <Link to="/login">
                  <Button variant="primary" fullWidth className="h-12">
                    Se connecter
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
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Nouveau mot de passe</h2>
                <p className="text-gray-600 text-sm">Choisissez un mot de passe sécurisé</p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-1.5">
                    Nouveau mot de passe
                  </label>
                  <Input
                    type="password"
                    placeholder="Entrez votre nouveau mot de passe"
                    error={errors.password?.message}
                    leftIcon={<span className="material-symbols-outlined text-xl">lock</span>}
                    fullWidth
                    {...register('password')}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-1.5">
                    Confirmer le mot de passe
                  </label>
                  <Input
                    type="password"
                    placeholder="Confirmez votre mot de passe"
                    error={errors.confirmPassword?.message}
                    leftIcon={<span className="material-symbols-outlined text-xl">lock</span>}
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
                        text="Au moins 8 caractères"
                      />
                      <PasswordRequirement
                        met={passwordChecks.hasUpperCase}
                        text="Une lettre majuscule"
                      />
                      <PasswordRequirement
                        met={passwordChecks.hasLowerCase}
                        text="Une lettre minuscule"
                      />
                      <PasswordRequirement met={passwordChecks.hasNumber} text="Un chiffre" />
                      <PasswordRequirement
                        met={passwordChecks.hasSpecialChar}
                        text="Un caractère spécial (!@#$%)"
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
                  Réinitialiser le mot de passe
                </Button>
              </form>

              {/* Back to Login Link */}
              <div className="text-center mt-6">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
                >
                  <span className="material-symbols-outlined text-sm">arrow_back</span>
                  <span>Retour à la connexion</span>
                </Link>
              </div>
            </>
          )}
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
