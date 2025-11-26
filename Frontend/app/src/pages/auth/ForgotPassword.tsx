import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router';
import { Button, Input, Card } from '@/components/ui';
import { useToast } from '@/hooks/useToast';
import { forgotPasswordSchema } from '@/utils/validators';
import { authApi } from '@/api';

type ForgotPasswordFormData = {
  email: string;
};

export default function ForgotPassword() {
  const { success, error } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsLoading(true);
    try {
      await authApi.forgotPassword(data.email);
      setEmailSent(true);
      success(
        'Si cette adresse email est associée à un compte, vous recevrez un email avec les instructions',
        'Email envoyé'
      );
    } catch (err: any) {
      error(
        err?.response?.data?.detail || 'Une erreur est survenue',
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
          {emailSent ? (
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-success-100 rounded-full mb-2">
                <span className="material-symbols-outlined text-success-600 text-3xl">
                  mark_email_read
                </span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">
                Vérifiez votre boîte email
              </h2>
              <p className="text-gray-600">
                Si votre adresse email est enregistrée, vous recevrez un email
                avec les instructions pour réinitialiser votre mot de passe.
              </p>
              <div className="pt-4">
                <Link to="/login">
                  <Button variant="primary" fullWidth className="h-12">
                    Retour à la connexion
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
                  Mot de passe oublié ?
                </h2>
                <p className="text-gray-600 text-sm">
                  Entrez votre email pour recevoir un lien de réinitialisation
                </p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-1.5">
                    Adresse e-mail
                  </label>
                  <Input
                    type="email"
                    placeholder="exemple@domaine.com"
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

                <Button
                  type="submit"
                  variant="primary"
                  fullWidth
                  isLoading={isLoading}
                  className="h-12"
                >
                  Envoyer le lien de réinitialisation
                </Button>
              </form>

              {/* Back to Login Link */}
              <div className="text-center mt-6">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
                >
                  <span className="material-symbols-outlined text-sm">
                    arrow_back
                  </span>
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
