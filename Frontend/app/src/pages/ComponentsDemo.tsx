import React, { useState } from 'react';
import { Button, Input, Card, Badge, Modal, Spinner, ToastContainer } from '@/components/ui';
import { useToast } from '@/hooks/useToast';

const ComponentsDemo: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { toasts, success, error, warning, info } = useToast();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-background-dark p-8">
      <ToastContainer toasts={toasts} />

      <div className="mx-auto max-w-7xl space-y-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100">
          Design System - Composants de Base
        </h1>

        {/* Buttons */}
        <Card>
          <h2 className="mb-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">Buttons</h2>
          <div className="flex flex-wrap gap-4">
            <Button variant="primary">Primary Button</Button>
            <Button variant="secondary">Secondary Button</Button>
            <Button variant="danger">Danger Button</Button>
            <Button variant="primary" size="sm">
              Small
            </Button>
            <Button variant="primary" size="lg">
              Large
            </Button>
            <Button variant="primary" disabled>
              Disabled
            </Button>
            <Button variant="primary" isLoading>
              Loading
            </Button>
            <Button
              variant="primary"
              leftIcon={<span className="material-symbols-outlined">add</span>}
            >
              With Icon
            </Button>
          </div>
        </Card>

        {/* Inputs */}
        <Card>
          <h2 className="mb-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">Inputs</h2>
          <div className="space-y-4">
            <Input label="Email" type="email" placeholder="Entrez votre email" fullWidth />
            <Input
              label="Password"
              type="password"
              placeholder="Entrez votre mot de passe"
              fullWidth
            />
            <Input
              label="Search"
              type="text"
              placeholder="Rechercher..."
              leftIcon={<span className="material-symbols-outlined">search</span>}
              fullWidth
            />
            <Input
              label="With Error"
              type="text"
              placeholder="Test"
              error="Ce champ est requis"
              fullWidth
            />
            <Input
              label="With Helper Text"
              type="text"
              placeholder="Test"
              helperText="Texte d'aide pour cet input"
              fullWidth
            />
          </div>
        </Card>

        {/* Badges */}
        <Card>
          <h2 className="mb-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">Badges</h2>
          <div className="flex flex-wrap gap-3">
            <Badge variant="success">Success</Badge>
            <Badge variant="primary">Primary</Badge>
            <Badge variant="warning">Warning</Badge>
            <Badge variant="danger">Danger</Badge>
            <Badge variant="neutral">Neutral</Badge>
            <Badge variant="success" dot>
              With Dot
            </Badge>
            <Badge
              variant="primary"
              icon={<span className="material-symbols-outlined !text-sm">star</span>}
            >
              With Icon
            </Badge>
          </div>
        </Card>

        {/* Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
              Default Card
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Ceci est une card avec padding par défaut (md)
            </p>
          </Card>
          <Card hover>
            <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
              Hover Card
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Passez la souris pour voir l'effet hover
            </p>
          </Card>
          <Card padding="sm">
            <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
              Small Padding
            </h3>
            <p className="text-gray-600 dark:text-gray-400">Card avec padding sm</p>
          </Card>
        </div>

        {/* Toasts */}
        <Card>
          <h2 className="mb-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">
            Toasts / Notifications
          </h2>
          <div className="flex flex-wrap gap-4">
            <Button variant="primary" onClick={() => success('Opération réussie !')}>
              Success Toast
            </Button>
            <Button variant="danger" onClick={() => error('Une erreur est survenue')}>
              Error Toast
            </Button>
            <Button variant="secondary" onClick={() => warning('Attention, vérifiez vos données')}>
              Warning Toast
            </Button>
            <Button variant="secondary" onClick={() => info('Information importante')}>
              Info Toast
            </Button>
          </div>
        </Card>

        {/* Modal */}
        <Card>
          <h2 className="mb-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">Modal</h2>
          <Button variant="primary" onClick={() => setIsModalOpen(true)}>
            Ouvrir la Modal
          </Button>

          <Modal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            title="Titre de la Modal"
            size="md"
          >
            <div className="space-y-4">
              <p className="text-gray-600 dark:text-gray-400">
                Ceci est le contenu de la modal. Vous pouvez fermer la modal en cliquant sur le
                bouton X, en appuyant sur Escape, ou en cliquant en dehors de la modal.
              </p>
              <div className="flex gap-3">
                <Button variant="primary" onClick={() => setIsModalOpen(false)}>
                  Confirmer
                </Button>
                <Button variant="secondary" onClick={() => setIsModalOpen(false)}>
                  Annuler
                </Button>
              </div>
            </div>
          </Modal>
        </Card>

        {/* Spinners */}
        <Card>
          <h2 className="mb-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">Spinners</h2>
          <div className="flex flex-wrap items-center gap-8">
            <Spinner size="xs" />
            <Spinner size="sm" />
            <Spinner size="md" />
            <Spinner size="lg" />
            <Spinner size="xl" />
            <Spinner size="md" label="Chargement..." />
            <Spinner size="md" variant="white" className="bg-gray-800 p-4 rounded" />
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ComponentsDemo;
