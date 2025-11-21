# RoadMap Frontend - PriceWatch (Application Utilisateur)

## Vue d'ensemble

Ce document trace les fonctionnalités à développer pour le frontend de PriceWatch (application utilisateur), **organisé par ordre de priorité**.

> **Note** : Ce frontend est dédié aux utilisateurs finaux. Un frontend admin séparé sera développé ultérieurement.

---

## Fonctionnalités Implémentées

*Aucune fonctionnalité implémentée pour le moment.*

---

## Fonctionnalités à Implémenter (par priorité)

### Priorité 1 - CRITIQUE (Setup & Auth)

#### 1.1 Setup du Projet
- [ ] **Initialisation Vite + React + TypeScript**
  - Configuration du projet avec Vite
  - TypeScript strict mode activé
  - Structure de dossiers organisée
- [ ] **Configuration Tailwind CSS**
  - Installation et configuration
  - Thème personnalisé (couleurs, fonts)
  - Plugin forms et typography
- [ ] **Configuration des outils de qualité**
  - ESLint avec règles TypeScript/React
  - Prettier pour le formatage
  - Husky pour pre-commit hooks
- [ ] **Configuration de l'environnement**
  - Variables d'environnement (.env)
  - Configuration API_URL
  - Mode développement/production

#### 1.2 Infrastructure Technique
- [ ] **Client HTTP (Axios)**
  - Instance Axios configurée
  - Intercepteur pour JWT (Authorization header)
  - Intercepteur pour refresh token automatique
  - Gestion globale des erreurs API
- [ ] **Routing (React Router v6)**
  - Configuration des routes
  - Routes protégées (PrivateRoute)
  - Redirections automatiques
  - Layout principal
- [ ] **State Management**
  - Context API pour l'authentification
  - Zustand ou Context pour l'état global
  - Gestion du user connecté

#### 1.3 Authentification
- [ ] **Page de connexion**
  - Formulaire email/mot de passe
  - Validation des champs
  - Affichage des erreurs
  - Lien vers inscription/mot de passe oublié
  - Stockage sécurisé des tokens
- [ ] **Page d'inscription**
  - Formulaire email/mot de passe/confirmation
  - Validation en temps réel du mot de passe
    - Minimum 8 caractères
    - Majuscule, minuscule, chiffre, caractère spécial
  - Message de confirmation (vérifier email)
- [ ] **Vérification d'email**
  - Page de confirmation avec token URL
  - Feedback visuel (succès/erreur)
  - Redirection vers login
- [ ] **Mot de passe oublié**
  - Formulaire de demande (email)
  - Message de confirmation
- [ ] **Réinitialisation du mot de passe**
  - Formulaire nouveau mot de passe
  - Validation de la force du mot de passe
  - Feedback succès/erreur

---

### Priorité 2 - HAUTE (Core Features)

#### 2.1 Layout & Navigation
- [ ] **Header/Navbar**
  - Logo PriceWatch
  - Navigation principale
  - Menu utilisateur (profil, déconnexion)
  - Indicateur de connexion
- [ ] **Layout principal**
  - Structure responsive
  - Container principal
  - Footer (optionnel)
- [ ] **Navigation mobile**
  - Menu hamburger
  - Sidebar ou drawer
  - Navigation adaptative

#### 2.2 Dashboard - Liste des Produits
- [ ] **Affichage des produits**
  - Liste/grille des produits suivis
  - Card produit avec :
    - Image du produit
    - Nom du produit
    - Prix actuel vs prix cible
    - Indicateur visuel (atteint/non atteint)
    - Date dernière vérification
    - Badge indisponible si applicable
- [ ] **Pagination**
  - Navigation entre pages
  - Sélection du nombre d'items par page
  - Affichage des métadonnées (total, pages)
- [ ] **Recherche**
  - Champ de recherche
  - Recherche par nom ou URL
  - Debounce pour performance
- [ ] **Tri**
  - Sélecteur de tri (dropdown)
  - Options : nom, prix actuel, prix cible, date création, dernière vérif
  - Ordre ascendant/descendant
- [ ] **États vides et loading**
  - Skeleton loading pendant chargement
  - Empty state si aucun produit
  - Message d'erreur si échec

#### 2.3 Ajout d'un Produit
- [ ] **Formulaire d'ajout**
  - Champ URL du produit
  - Champ prix cible
  - Sélecteur fréquence de vérification (6h, 12h, 24h)
  - Bouton de soumission
- [ ] **Feedback utilisateur**
  - Loading pendant le scraping
  - Affichage du produit créé (nom, image, prix extrait)
  - Message d'erreur si URL invalide ou scraping échoué
  - Redirection vers dashboard après succès

#### 2.4 Détail d'un Produit
- [ ] **Vue détaillée**
  - Image grande taille
  - Nom complet du produit
  - Prix actuel et prix cible
  - Date de création
  - Dernière vérification
  - Statut de disponibilité
  - Lien vers le site marchand (nouvelle fenêtre)
- [ ] **Actions sur le produit**
  - Bouton "Vérifier le prix maintenant"
  - Bouton "Modifier"
  - Bouton "Supprimer" (avec confirmation)

#### 2.5 Modification d'un Produit
- [ ] **Formulaire de modification**
  - Champ nom (pré-rempli)
  - Champ prix cible (pré-rempli)
  - Sélecteur fréquence (pré-rempli)
  - Boutons Sauvegarder/Annuler
- [ ] **Feedback**
  - Toast de confirmation
  - Mise à jour en temps réel dans la liste

#### 2.6 Suppression d'un Produit
- [ ] **Modal de confirmation**
  - Message de confirmation
  - Nom du produit à supprimer
  - Boutons Confirmer/Annuler
- [ ] **Feedback**
  - Toast de confirmation
  - Suppression de la liste sans rechargement

---

### Priorité 3 - MOYENNE (Historique & Préférences)

#### 3.1 Historique des Prix
- [ ] **Graphique d'évolution**
  - Graphique en ligne (Chart.js ou Recharts)
  - Axe X : dates
  - Axe Y : prix
  - Ligne du prix cible (référence)
  - Tooltip avec détails
  - Période configurable (7j, 30j, 90j, tout)
- [ ] **Liste chronologique**
  - Tableau des prix enregistrés
  - Date et heure
  - Prix
  - Variation par rapport au précédent
- [ ] **Statistiques**
  - Prix minimum historique
  - Prix maximum historique
  - Prix moyen
  - Variation en pourcentage
  - Nombre de relevés

#### 3.2 Préférences Utilisateur
- [ ] **Page des paramètres**
  - Section notifications
  - Section webhooks
- [ ] **Notifications email**
  - Toggle activer/désactiver
  - Toggle alertes baisse de prix
  - Toggle alertes disponibilité
  - Toggle résumé hebdomadaire
  - Sélecteur fréquence de notification
- [ ] **Webhooks**
  - Toggle activer/désactiver
  - Champ URL du webhook
  - Sélecteur type (Slack, Discord, Custom)
  - Test de webhook (optionnel)
- [ ] **Sauvegarde**
  - Bouton sauvegarder
  - Feedback de confirmation

---

### Priorité 4 - BASSE (UX/UI Polish)

#### 4.1 Composants UI Réutilisables
- [ ] **Design System de base**
  - Button (primary, secondary, danger, sizes)
  - Input (text, email, password, number)
  - Select/Dropdown
  - Checkbox/Toggle
  - Card
  - Badge/Tag
  - Avatar
- [ ] **Composants feedback**
  - Toast/Notifications
  - Modal/Dialog
  - Alert/Banner
  - Spinner/Loader
  - Skeleton
  - Progress bar
- [ ] **Composants navigation**
  - Breadcrumb
  - Tabs
  - Pagination

#### 4.2 Améliorations UX
- [ ] **Loading states**
  - Skeletons pour toutes les listes
  - Spinners pour les actions
  - Optimistic updates
- [ ] **Empty states**
  - Messages clairs et actions
  - Illustrations (optionnel)
- [ ] **Error handling**
  - Error boundaries React
  - Pages d'erreur (404, 500)
  - Messages d'erreur user-friendly
  - Retry automatique
- [ ] **Feedback actions**
  - Toasts pour succès/erreur
  - Confirmation pour actions destructives

#### 4.3 Responsive Design
- [ ] **Mobile-first**
  - Breakpoints Tailwind (sm, md, lg, xl)
  - Navigation adaptative
  - Cards responsive
  - Formulaires adaptés
- [ ] **Touch-friendly**
  - Boutons assez grands
  - Espacement suffisant
  - Swipe actions (optionnel)

#### 4.4 Accessibilité (a11y)
- [ ] **Standards WCAG**
  - Labels ARIA appropriés
  - Navigation clavier complète
  - Focus visible
  - Contraste couleurs suffisant
  - Alt text pour images
  - Rôles sémantiques

---

### Priorité 5 - OPTIMISATIONS

#### 5.1 Performance
- [ ] **Code splitting**
  - Lazy loading des routes
  - Dynamic imports
  - Suspense boundaries
- [ ] **Cache & State**
  - React Query ou SWR pour cache API
  - Stale-while-revalidate
  - Invalidation intelligente
- [ ] **Optimisations React**
  - Memoization (useMemo, useCallback)
  - Virtualization pour grandes listes
  - Image optimization

#### 5.2 PWA (Optionnel)
- [ ] **Service Worker**
  - Cache offline
  - Background sync
- [ ] **Manifest**
  - Installation sur mobile
  - Splash screen
  - Icônes

---

## Structure de Dossiers

```
Frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/                    # Services API
│   │   ├── client.ts           # Instance Axios configurée
│   │   ├── auth.ts             # Endpoints auth
│   │   ├── products.ts         # Endpoints products
│   │   └── preferences.ts      # Endpoints preferences
│   ├── components/             # Composants réutilisables
│   │   ├── ui/                 # Composants UI de base
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── ...
│   │   ├── layout/             # Composants de layout
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Layout.tsx
│   │   └── products/           # Composants spécifiques produits
│   │       ├── ProductCard.tsx
│   │       ├── ProductForm.tsx
│   │       ├── PriceChart.tsx
│   │       └── ...
│   ├── contexts/               # React Contexts
│   │   └── AuthContext.tsx
│   ├── hooks/                  # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useProducts.ts
│   │   └── useToast.ts
│   ├── pages/                  # Pages par route
│   │   ├── auth/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── ForgotPassword.tsx
│   │   │   ├── ResetPassword.tsx
│   │   │   └── VerifyEmail.tsx
│   │   ├── dashboard/
│   │   │   └── Dashboard.tsx
│   │   ├── products/
│   │   │   ├── ProductDetail.tsx
│   │   │   ├── ProductAdd.tsx
│   │   │   └── ProductEdit.tsx
│   │   └── settings/
│   │       └── Settings.tsx
│   ├── types/                  # TypeScript interfaces
│   │   ├── auth.ts
│   │   ├── product.ts
│   │   └── preferences.ts
│   ├── utils/                  # Helpers et utilitaires
│   │   ├── formatters.ts       # Format prix, dates
│   │   ├── validators.ts       # Validation formulaires
│   │   └── constants.ts
│   ├── styles/                 # Styles globaux
│   │   └── globals.css
│   ├── App.tsx                 # Composant racine
│   ├── main.tsx                # Point d'entrée
│   └── router.tsx              # Configuration routes
├── .env.example
├── .eslintrc.cjs
├── .prettierrc
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

## Endpoints API Consommés

### Authentification (`/api/v1/auth`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/register` | Inscription |
| POST | `/login` | Connexion |
| GET | `/me` | Info utilisateur connecté |
| POST | `/refresh` | Refresh du token |
| POST | `/verify-email` | Vérification email |
| POST | `/forgot-password` | Demande reset password |
| POST | `/reset-password` | Reset du password |

### Produits (`/api/v1/products`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Liste paginée des produits |
| POST | `/` | Ajouter un produit |
| GET | `/{id}` | Détail d'un produit |
| PUT | `/{id}` | Modifier un produit |
| DELETE | `/{id}` | Supprimer un produit |
| POST | `/{id}/check` | Vérifier le prix |
| GET | `/{id}/history` | Historique des prix |
| GET | `/{id}/history/stats` | Statistiques de prix |

### Préférences (`/api/v1/users`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/preferences` | Récupérer préférences |
| POST | `/preferences` | Créer préférences |
| PUT | `/preferences` | Modifier préférences |
| DELETE | `/preferences` | Supprimer préférences |

---

## Types TypeScript

### Auth

```typescript
interface User {
  id: number;
  email: string;
  created_at: string;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
}

interface Token {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}
```

### Product

```typescript
interface Product {
  id: number;
  user_id: number;
  name: string;
  url: string;
  image: string | null;
  current_price: number;
  target_price: number;
  last_checked: string;
  created_at: string;
  is_available: boolean;
  unavailable_since: string | null;
  check_frequency: 6 | 12 | 24;
}

interface ProductCreate {
  url: string;
  target_price: number;
  check_frequency?: 6 | 12 | 24;
}

interface ProductUpdate {
  name?: string;
  target_price?: number;
  check_frequency?: 6 | 12 | 24;
}

interface PaginatedProducts {
  items: Product[];
  metadata: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
}

interface PriceHistory {
  id: number;
  product_id: number;
  price: number;
  recorded_at: string;
}

interface PriceStats {
  lowest_price: number;
  highest_price: number;
  average_price: number;
  price_change_percent: number;
  total_records: number;
}
```

### Preferences

```typescript
interface UserPreferences {
  id: number;
  user_id: number;
  email_notifications: boolean;
  webhook_notifications: boolean;
  webhook_url: string | null;
  webhook_type: 'slack' | 'discord' | 'custom' | null;
  notification_frequency: string;
  price_drop_alerts: boolean;
  weekly_summary: boolean;
  availability_alerts: boolean;
}
```

---

## Dépendances Principales

### Core
- React 18
- TypeScript 5
- Vite 5

### Styling
- Tailwind CSS 3
- @tailwindcss/forms
- @tailwindcss/typography

### Routing & State
- React Router 6
- Zustand (ou Context API)

### HTTP & Data
- Axios
- React Query (ou SWR)

### UI Components
- Headless UI (ou Radix UI)
- React Icons (ou Heroicons)

### Charts
- Recharts (ou Chart.js)

### Forms
- React Hook Form
- Zod (validation)

### Utils
- date-fns (dates)
- clsx (classnames)

### Dev
- ESLint
- Prettier
- Husky

---

## Notes Techniques

### Gestion des Tokens
- Access token stocké en mémoire (state)
- Refresh token en localStorage (ou httpOnly cookie si SSR)
- Intercepteur Axios pour auto-refresh
- Redirect vers login si refresh échoue

### Validation Formulaires
- Validation côté client avec Zod
- Messages d'erreur en français
- Validation en temps réel pour UX

### Gestion des Erreurs API
- Intercepteur global pour erreurs
- Toast pour erreurs utilisateur
- Console pour erreurs développeur
- Retry automatique pour erreurs réseau

---

## Commandes

```bash
# Installation
npm install

# Développement
npm run dev

# Build production
npm run build

# Preview build
npm run preview

# Linting
npm run lint

# Formatage
npm run format

# Type check
npm run type-check
```

---

**Dernière mise à jour** : 2025-11-21
