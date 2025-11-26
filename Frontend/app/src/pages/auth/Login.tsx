import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router';
import { Button, Input, Card } from '@/components/ui';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/useToast';
import { loginSchema } from '@/utils/validators';
import type { LoginCredentials } from '@/types';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { success, error } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginCredentials) => {
    setIsLoading(true);
    try {
      await login(data);
      success('Connexion réussie !', 'Bienvenue sur PriceWatch');
      navigate('/dashboard');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'response' in err
          ? (err.response as { data?: { detail?: string } })?.data?.detail
          : undefined;
      error(message || 'Email ou mot de passe incorrect', 'Erreur de connexion');
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
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Connectez-vous à votre compte</h2>
            <p className="text-gray-600 text-sm">
              Suivez vos produits, ne manquez aucune baisse de prix.
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <Input
                label="Adresse e-mail"
                type="email"
                placeholder="exemple@domaine.com"
                error={errors.email?.message}
                leftIcon={<span className="material-symbols-outlined text-xl">mail</span>}
                fullWidth
                {...register('email')}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-900">Mot de passe</label>
                <Link
                  to="/forgot-password"
                  className="text-sm font-medium text-primary-600 hover:text-primary-700"
                >
                  Mot de passe oublié ?
                </Link>
              </div>
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder="Entrez votre mot de passe"
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
              Se connecter
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">Ou continuez avec</span>
            </div>
          </div>

          {/* OAuth Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              className="flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              <span className="text-sm font-medium text-gray-700">Google</span>
            </button>

            <button
              type="button"
              className="flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
              </svg>
              <span className="text-sm font-medium text-gray-700">Apple</span>
            </button>
          </div>

          {/* Register Link */}
          <p className="text-center text-gray-600 text-sm mt-6">
            Pas encore de compte ?{' '}
            <Link to="/register" className="font-semibold text-primary-600 hover:text-primary-700">
              S'inscrire
            </Link>
          </p>
        </Card>
      </div>
    </div>
  );
}
