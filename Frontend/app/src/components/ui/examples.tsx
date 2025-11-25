/**
 * Exemples d'utilisation des composants UI
 *
 * Ce fichier contient des exemples pratiques pour chaque composant.
 * Utilisez ces exemples comme référence lors de l'implémentation.
 */

import React, { useState } from 'react';
import {
  Button,
  Input,
  Card,
  Badge,
  Modal,
  Spinner,
  ToastContainer,
} from '@/components/ui';
import { useToast } from '@/hooks/useToast';

// ============================================
// EXEMPLE 1 : BUTTONS
// ============================================
export function ButtonExamples() {
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  };

  return (
    <div className="space-y-4">
      {/* Variantes */}
      <div className="flex gap-3">
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="danger">Danger</Button>
      </div>

      {/* Tailles */}
      <div className="flex items-center gap-3">
        <Button size="sm">Small</Button>
        <Button size="md">Medium</Button>
        <Button size="lg">Large</Button>
      </div>

      {/* Avec icônes */}
      <div className="flex gap-3">
        <Button
          variant="primary"
          leftIcon={<span className="material-symbols-outlined">add</span>}
        >
          Ajouter
        </Button>
        <Button
          variant="secondary"
          rightIcon={<span className="material-symbols-outlined">arrow_forward</span>}
        >
          Suivant
        </Button>
      </div>

      {/* Loading state */}
      <Button variant="primary" isLoading={isLoading} onClick={handleSubmit}>
        {isLoading ? 'Chargement...' : 'Soumettre'}
      </Button>

      {/* Disabled */}
      <Button variant="primary" disabled>
        Désactivé
      </Button>

      {/* Full width */}
      <Button variant="primary" fullWidth>
        Bouton pleine largeur
      </Button>
    </div>
  );
}

// ============================================
// EXEMPLE 2 : INPUTS
// ============================================
export function InputExamples() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <div className="max-w-md space-y-4">
      {/* Input simple */}
      <Input
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="votre@email.com"
        fullWidth
      />

      {/* Input avec icône gauche */}
      <Input
        label="Rechercher"
        type="text"
        leftIcon={<span className="material-symbols-outlined">search</span>}
        placeholder="Rechercher un produit..."
        fullWidth
      />

      {/* Input avec icône droite */}
      <Input
        label="Mot de passe"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        rightIcon={<span className="material-symbols-outlined">visibility</span>}
        fullWidth
      />

      {/* Input avec erreur */}
      <Input
        label="Nom d'utilisateur"
        type="text"
        error="Ce champ est requis"
        fullWidth
      />

      {/* Input avec helper text */}
      <Input
        label="Prix cible"
        type="number"
        helperText="Saisissez le prix en euros"
        placeholder="0.00"
        fullWidth
      />
    </div>
  );
}

// ============================================
// EXEMPLE 3 : CARDS
// ============================================
export function CardExamples() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Card simple */}
      <Card>
        <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
          Card Simple
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Ceci est une card avec le padding par défaut (md)
        </p>
      </Card>

      {/* Card avec hover */}
      <Card hover>
        <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
          Card Hover
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Passez la souris pour voir l'effet hover
        </p>
      </Card>

      {/* Card avec padding personnalisé */}
      <Card padding="lg">
        <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
          Large Padding
        </h3>
        <p className="text-gray-600 dark:text-gray-400">
          Card avec padding large (lg)
        </p>
      </Card>

      {/* Card produit exemple */}
      <Card hover padding="md">
        <div className="space-y-3">
          <div className="flex items-start justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              iPhone 15 Pro
            </h3>
            <Badge variant="success">En stock</Badge>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold text-primary-600">1199€</p>
            <p className="text-sm text-gray-500">Prix cible : 1099€</p>
          </div>
          <Button variant="primary" size="sm" fullWidth>
            Voir les détails
          </Button>
        </div>
      </Card>
    </div>
  );
}

// ============================================
// EXEMPLE 4 : BADGES
// ============================================
export function BadgeExamples() {
  return (
    <div className="flex flex-wrap gap-3">
      {/* Variantes */}
      <Badge variant="success">Succès</Badge>
      <Badge variant="primary">Primaire</Badge>
      <Badge variant="warning">Avertissement</Badge>
      <Badge variant="danger">Danger</Badge>
      <Badge variant="neutral">Neutre</Badge>

      {/* Avec dot */}
      <Badge variant="success" dot>
        Actif
      </Badge>
      <Badge variant="warning" dot>
        En attente
      </Badge>

      {/* Avec icône */}
      <Badge
        variant="primary"
        icon={<span className="material-symbols-outlined !text-sm">star</span>}
      >
        Premium
      </Badge>
      <Badge
        variant="success"
        icon={<span className="material-symbols-outlined !text-sm">check</span>}
      >
        Vérifié
      </Badge>

      {/* États de produit */}
      <Badge variant="success">Prix cible atteint</Badge>
      <Badge variant="danger">Indisponible</Badge>
      <Badge variant="neutral">Vérification en cours</Badge>
    </div>
  );
}

// ============================================
// EXEMPLE 5 : TOASTS
// ============================================
export function ToastExamples() {
  const { toasts, success, error, warning, info } = useToast();

  return (
    <div className="space-y-4">
      <ToastContainer toasts={toasts} />

      <div className="flex flex-wrap gap-3">
        <Button
          variant="primary"
          onClick={() => success('Produit ajouté avec succès !', 'Succès')}
        >
          Toast Succès
        </Button>

        <Button
          variant="danger"
          onClick={() =>
            error('Impossible de récupérer les données', 'Erreur')
          }
        >
          Toast Erreur
        </Button>

        <Button
          variant="secondary"
          onClick={() =>
            warning('Le prix a augmenté de 10%', 'Attention')
          }
        >
          Toast Warning
        </Button>

        <Button
          variant="secondary"
          onClick={() =>
            info('Nouvelle vérification dans 6 heures', 'Information')
          }
        >
          Toast Info
        </Button>

        {/* Toast avec durée personnalisée */}
        <Button
          variant="secondary"
          onClick={() =>
            success('Ce message disparaîtra après 10 secondes', 'Long toast', 10000)
          }
        >
          Toast 10s
        </Button>
      </div>
    </div>
  );
}

// ============================================
// EXEMPLE 6 : MODAL
// ============================================
export function ModalExamples() {
  const [isOpen, setIsOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  return (
    <div className="space-y-4">
      {/* Modal simple */}
      <Button variant="primary" onClick={() => setIsOpen(true)}>
        Ouvrir Modal Simple
      </Button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Détails du produit"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            Voici les détails du produit. Cette modal peut contenir n'importe quel contenu.
          </p>
          <div className="flex gap-3">
            <Button variant="primary" onClick={() => setIsOpen(false)}>
              Confirmer
            </Button>
            <Button variant="secondary" onClick={() => setIsOpen(false)}>
              Annuler
            </Button>
          </div>
        </div>
      </Modal>

      {/* Modal de confirmation */}
      <Button variant="danger" onClick={() => setConfirmOpen(true)}>
        Supprimer
      </Button>

      <Modal
        isOpen={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        title="Confirmer la suppression"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            Êtes-vous sûr de vouloir supprimer ce produit ? Cette action est irréversible.
          </p>
          <div className="flex gap-3">
            <Button variant="danger" onClick={() => setConfirmOpen(false)}>
              Supprimer
            </Button>
            <Button variant="secondary" onClick={() => setConfirmOpen(false)}>
              Annuler
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

// ============================================
// EXEMPLE 7 : SPINNERS
// ============================================
export function SpinnerExamples() {
  return (
    <div className="space-y-6">
      {/* Tailles */}
      <div className="flex items-center gap-8">
        <Spinner size="xs" />
        <Spinner size="sm" />
        <Spinner size="md" />
        <Spinner size="lg" />
        <Spinner size="xl" />
      </div>

      {/* Avec label */}
      <Spinner size="md" label="Chargement des produits..." />

      {/* Variantes */}
      <div className="flex items-center gap-8">
        <Spinner size="md" variant="primary" />
        <div className="rounded bg-gray-800 p-4">
          <Spinner size="md" variant="white" />
        </div>
      </div>

      {/* Dans une card */}
      <Card>
        <div className="flex min-h-[200px] items-center justify-center">
          <Spinner size="lg" label="Chargement..." />
        </div>
      </Card>
    </div>
  );
}

// ============================================
// EXEMPLE COMPLET : Formulaire
// ============================================
export function CompleteFormExample() {
  const [isLoading, setIsLoading] = useState(false);
  const { toasts, success } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      success('Produit ajouté avec succès !');
    }, 2000);
  };

  return (
    <div className="mx-auto max-w-2xl">
      <ToastContainer toasts={toasts} />

      <Card>
        <h2 className="mb-6 text-2xl font-bold text-gray-900 dark:text-gray-100">
          Ajouter un produit
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="URL du produit"
            type="url"
            placeholder="https://exemple.com/produit"
            leftIcon={<span className="material-symbols-outlined">link</span>}
            helperText="Collez l'URL du produit à suivre"
            fullWidth
            required
          />

          <Input
            label="Prix cible (€)"
            type="number"
            placeholder="99.99"
            leftIcon={<span className="material-symbols-outlined">euro</span>}
            helperText="Vous serez notifié quand ce prix sera atteint"
            fullWidth
            required
          />

          <div className="flex gap-3">
            <Button
              type="submit"
              variant="primary"
              isLoading={isLoading}
              leftIcon={<span className="material-symbols-outlined">add</span>}
            >
              {isLoading ? 'Ajout en cours...' : 'Ajouter le produit'}
            </Button>
            <Button type="button" variant="secondary">
              Annuler
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
