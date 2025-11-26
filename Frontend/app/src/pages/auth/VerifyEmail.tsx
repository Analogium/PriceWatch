import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { Button, Card, Spinner } from '@/components/ui';
import { authApi } from '@/api';

type VerificationState = 'loading' | 'success' | 'error';

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const [state, setState] = useState<VerificationState>('loading');
  const [errorMessage, setErrorMessage] = useState('');

  const token = searchParams.get('token');

  useEffect(() => {
    const verifyEmail = async () => {
      if (!token) {
        setState('error');
        setErrorMessage('Le lien de vérification est invalide');
        return;
      }

      try {
        await authApi.verifyEmail(token);
        setState('success');
      } catch (err: unknown) {
        setState('error');
        const message =
          err && typeof err === 'object' && 'response' in err
            ? (err.response as { data?: { detail?: string } })?.data?.detail
            : undefined;
        setErrorMessage(message || 'Le lien de vérification est invalide ou a expiré');
      }
    };

    verifyEmail();
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full">
        <Card padding="lg" className="max-w-[480px] mx-auto">
          {state === 'loading' && (
            <div className="text-center space-y-4 py-8">
              <Spinner size="lg" variant="primary" />
              <h2 className="text-2xl font-bold text-gray-900">Vérification en cours...</h2>
              <p className="text-gray-600 text-sm">Nous vérifions votre adresse email</p>
            </div>
          )}

          {state === 'success' && (
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-success-100 rounded-full mb-2">
                <span className="material-symbols-outlined text-success-600 text-3xl">
                  mark_email_read
                </span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Email vérifié avec succès !</h2>
              <p className="text-gray-600">
                Votre adresse email a été confirmée. Vous pouvez maintenant vous connecter à votre
                compte PriceWatch.
              </p>
              <div className="pt-4">
                <Link to="/login">
                  <Button variant="primary" fullWidth className="h-12">
                    Se connecter
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {state === 'error' && (
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-danger-100 rounded-full mb-2">
                <span className="material-symbols-outlined text-danger-600 text-3xl">error</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Vérification échouée</h2>
              <p className="text-gray-600">{errorMessage}</p>
              <div className="pt-4 space-y-3">
                <Link to="/register">
                  <Button variant="primary" fullWidth className="h-12">
                    Créer un nouveau compte
                  </Button>
                </Link>
                <Link to="/login">
                  <Button variant="secondary" fullWidth className="h-12">
                    Retour à la connexion
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </Card>

        {/* Help text */}
        {state !== 'loading' && (
          <p className="text-center text-sm text-gray-600 mt-6">
            Besoin d'aide ? Contactez le support
          </p>
        )}
      </div>
    </div>
  );
}
