# Composants UI - PriceWatch

Ce dossier contient tous les composants UI de base du design system PriceWatch.

## Composants disponibles

### Button

Bouton avec support de plusieurs variantes, tailles, états de chargement et icônes.

**Props:**
- `variant`: 'primary' | 'secondary' | 'danger' (défaut: 'primary')
- `size`: 'sm' | 'md' | 'lg' (défaut: 'md')
- `isLoading`: boolean (défaut: false)
- `leftIcon`: ReactNode
- `rightIcon`: ReactNode
- `fullWidth`: boolean (défaut: false)

**Exemple:**
```tsx
import { Button } from '@/components/ui';

<Button variant="primary" size="md" onClick={handleClick}>
  Cliquez ici
</Button>

<Button
  variant="primary"
  isLoading={isSubmitting}
  leftIcon={<span className="material-symbols-outlined">add</span>}
>
  Ajouter
</Button>
```

---

### Input

Champ de saisie avec support des icônes, labels, erreurs et texte d'aide.

**Props:**
- `label`: string
- `error`: string
- `helperText`: string
- `leftIcon`: ReactNode
- `rightIcon`: ReactNode
- `fullWidth`: boolean (défaut: false)

**Exemple:**
```tsx
import { Input } from '@/components/ui';

<Input
  label="Email"
  type="email"
  placeholder="Entrez votre email"
  leftIcon={<span className="material-symbols-outlined">mail</span>}
  fullWidth
/>

<Input
  label="Mot de passe"
  type="password"
  error="Le mot de passe est requis"
  fullWidth
/>
```

---

### Card

Container avec bordures, ombre et padding configurable.

**Props:**
- `hover`: boolean (défaut: false) - Active l'effet hover
- `padding`: 'none' | 'sm' | 'md' | 'lg' (défaut: 'md')

**Exemple:**
```tsx
import { Card } from '@/components/ui';

<Card hover padding="md">
  <h3>Titre de la card</h3>
  <p>Contenu de la card</p>
</Card>
```

---

### Badge

Petit badge pour afficher des statuts ou tags.

**Props:**
- `variant`: 'success' | 'primary' | 'warning' | 'danger' | 'neutral' (défaut: 'neutral')
- `icon`: ReactNode
- `dot`: boolean (défaut: false) - Affiche un point de couleur

**Exemple:**
```tsx
import { Badge } from '@/components/ui';

<Badge variant="success">Actif</Badge>
<Badge variant="warning" dot>En attente</Badge>
<Badge variant="primary" icon={<span className="material-symbols-outlined">star</span>}>
  Premium
</Badge>
```

---

### Toast / Notification

Notifications avec auto-dismiss et 4 variantes.

**Utilisation via le hook useToast:**

```tsx
import { useToast } from '@/hooks/useToast';
import { ToastContainer } from '@/components/ui';

function MyComponent() {
  const { toasts, success, error, warning, info } = useToast();

  const handleSuccess = () => {
    success('Opération réussie !', 'Succès', 5000);
  };

  return (
    <>
      <ToastContainer toasts={toasts} />
      <button onClick={handleSuccess}>Afficher une notification</button>
    </>
  );
}
```

**Méthodes disponibles:**
- `success(message, title?, duration?)`: Notification de succès
- `error(message, title?, duration?)`: Notification d'erreur
- `warning(message, title?, duration?)`: Notification d'avertissement
- `info(message, title?, duration?)`: Notification d'information

---

### Modal

Dialog modal avec backdrop, support de différentes tailles.

**Props:**
- `isOpen`: boolean - État d'ouverture de la modal
- `onClose`: () => void - Callback de fermeture
- `title`: string
- `size`: 'sm' | 'md' | 'lg' | 'xl' (défaut: 'md')
- `showCloseButton`: boolean (défaut: true)
- `closeOnBackdropClick`: boolean (défaut: true)
- `closeOnEscape`: boolean (défaut: true)

**Exemple:**
```tsx
import { useState } from 'react';
import { Modal, Button } from '@/components/ui';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Ouvrir la modal</Button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Titre de la modal"
        size="md"
      >
        <p>Contenu de la modal</p>
        <Button onClick={() => setIsOpen(false)}>Fermer</Button>
      </Modal>
    </>
  );
}
```

---

### Spinner

Indicateur de chargement avec différentes tailles et variantes.

**Props:**
- `size`: 'xs' | 'sm' | 'md' | 'lg' | 'xl' (défaut: 'md')
- `variant`: 'primary' | 'white' | 'current' (défaut: 'primary')
- `label`: string

**Exemple:**
```tsx
import { Spinner } from '@/components/ui';

<Spinner size="md" />
<Spinner size="lg" label="Chargement..." />
<Spinner size="sm" variant="white" />
```

---

## Import

Tous les composants peuvent être importés depuis `@/components/ui` :

```tsx
import { Button, Input, Card, Badge, Modal, Spinner, ToastContainer } from '@/components/ui';
import { useToast } from '@/hooks/useToast';
```

---

## Design System

Ces composants suivent les spécifications du design system PriceWatch défini dans `/Frontend/RoadMapDoc/DESIGN_SYSTEM.md`.

**Couleurs principales:**
- Primary: #2563EB (bleu)
- Success: #16A34A (vert)
- Danger: #DC3545 / #EF4444 (rouge)
- Warning: #F59E0B (orange)
- Neutral: Gray palette

**Dark mode:**
Tous les composants supportent le dark mode via la classe `dark` sur l'élément `<html>`.

---

## Tests

Pour visualiser tous les composants, consultez la page de démonstration :

```tsx
import ComponentsDemo from '@/pages/ComponentsDemo';
```
