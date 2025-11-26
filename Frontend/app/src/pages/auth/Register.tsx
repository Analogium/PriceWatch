import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router';
import { Button, Input, Card } from '@/components/ui';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/useToast';
import { registerSchema } from '@/utils/validators';
import type { RegisterData } from '@/types';

export default function Register() {
  const navigate = useNavigate();
  const { register: registerUser } = useAuth();
  const { success, error } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterData>({
    resolver: zodResolver(registerSchema),
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
      success(
        'Un email de vérification a été envoyé à votre adresse',
        'Inscription réussie !'
      );
      navigate('/login');
    } catch (err: any) {
      error(
        err?.response?.data?.detail || 'Une erreur est survenue lors de l\'inscription',
        'Erreur'
      );
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
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Créez votre compte
            </h2>
            <p className="text-gray-600 text-sm">
              Ne manquez plus jamais une bonne affaire.
            </p>
          </div>

          {/* Register Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-1.5">
                Adresse e-mail
              </label>
              <Input
                type="email"
                placeholder="vous@email.com"
                error={errors.email?.message}
                leftIcon={
                  <span className="material-symbols-outlined text-xl">
                    mail
                  </span>
                }
                fullWidth
                {...register('email')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-900 mb-1.5">
                Mot de passe
              </label>
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder="Entrez votre mot de passe"
                error={errors.password?.message}
                leftIcon={
                  <span className="material-symbols-outlined text-xl">
                    lock
                  </span>
                }
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
                Confirmer le mot de passe
              </label>
              <Input
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="Confirmez votre mot de passe"
                error={errors.confirmPassword?.message}
                leftIcon={
                  <span className="material-symbols-outlined text-xl">
                    lock
                  </span>
                }
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
                  <PasswordRequirement
                    met={passwordChecks.hasNumber}
                    text="Un chiffre"
                  />
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
              Créer mon compte
            </Button>
          </form>

          {/* Login Link */}
          <p className="text-center text-gray-600 text-sm mt-6">
            Déjà un compte ?{' '}
            <Link
              to="/login"
              className="font-semibold text-primary-600 hover:text-primary-700"
            >
              Se connecter
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
        <svg
          className="w-5 h-5 text-success-600 shrink-0"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clipRule="evenodd"
          />
        </svg>
      ) : (
        <svg
          className="w-5 h-5 text-gray-300 shrink-0"
          fill="none"
          viewBox="0 0 20 20"
        >
          <circle
            cx="10"
            cy="10"
            r="8"
            stroke="currentColor"
            strokeWidth="1.5"
          />
        </svg>
      )}
      <span
        className={`text-sm ${met ? 'text-gray-900' : 'text-gray-600'}`}
      >
        {text}
      </span>
    </div>
  );
}
