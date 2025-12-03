# RoadMap Frontend - PriceWatch (Application Utilisateur)

## Vue d'ensemble

Ce document trace les fonctionnalités à développer pour le frontend de PriceWatch (application utilisateur), **organisé par ordre de priorité**.

> **Note** : Ce frontend est dédié aux utilisateurs finaux. Un frontend admin séparé sera développé ultérieurement.

> **Référence Design** : Voir [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) pour les spécifications complètes des couleurs, typographie, composants et styles.

> **Maquette** : Voir [../Maquette/](../Maquette/) pour les pages ou composants qui sont déjà réalisés depuis figma.

---

## Fonctionnalités Implémentées

### ✅ Setup & Infrastructure (Priorité 1)

#### 1.1 Setup du Projet - COMPLET ✅
- ✅ **Initialisation Vite + React + TypeScript**
  - Configuration du projet avec Vite 7.2.4
  - TypeScript 5.9.3 strict mode activé
  - Structure de dossiers organisée selon l'architecture définie
- ✅ **Configuration Tailwind CSS v4**
  - Installation et configuration complète (Tailwind v4.1.17 avec plugin Vite)
  - Thème personnalisé avec toutes les couleurs du design system :
    - Primary (bleu) : `#2563EB` avec variantes 50-900
    - Success (vert) : `#16A34A` avec variantes
    - Danger (rouge) : `#DC3545` avec variantes
    - **Error** : `#EF4444` (variante alternative)
    - **Warning** (orange) : `#F59E0B` avec variantes 50-700
    - Gray (neutre) : variantes 50-900
    - Slate (textes) : 400, 500, 800
    - Background light/dark : `#F8FAFC` / `#101722`
  - Plugins @tailwindcss/forms et @tailwindcss/typography
  - Border radius personnalisés (0.375rem, 0.5rem, 0.75rem, full)
- ✅ **Import des Google Fonts**
  - Police Inter (weights 400, 500, 600, 700, 900) avec preconnect
  - Material Symbols Outlined pour les icônes
  - Optimisation avec preconnect pour performance
- ✅ **Configuration des outils de qualité**
  - ESLint avec règles TypeScript/React
  - Prettier pour le formatage
  - Scripts lint, lint:fix, format, format:check
- ✅ **Configuration de l'environnement**
  - Variables d'environnement (.env)
  - Configuration VITE_API_URL
  - Configuration Docker Compose pour développement

#### 1.2 Design System - Composants de Base - COMPLET ✅
- ✅ **Composants UI fondamentaux** (`components/ui/`)
  - Button (primary, secondary, danger) avec support isLoading, icons, sizes (sm, md, lg)
  - Input avec support leftIcon/rightIcon, label, error, helperText
  - Card avec hover effect et padding configurable (none, sm, md, lg)
  - Badge avec 5 variantes (success, primary, warning, danger, neutral) et support icon/dot
- ✅ **Composants feedback essentiels**
  - Toast/Notification avec 4 variantes et auto-dismiss configurable
  - ToastContainer pour afficher les notifications
  - Hook useToast avec méthodes success, error, warning, info
  - Modal/Dialog avec backdrop blur, tailles (sm, md, lg, xl), close on Escape/backdrop
  - Spinner/Loader avec variants (primary, white, current) et tailles (xs-xl)
- ✅ **Barrel exports**
  - Tous les composants exportés depuis `@/components/ui/index.ts`

#### 1.3 Infrastructure Technique - COMPLET ✅
- ✅ **Client HTTP (Axios)**
  - Instance Axios configurée dans `api/client.ts`
  - Intercepteur pour JWT (Authorization header avec Bearer token)
  - Intercepteur pour refresh token automatique sur 401
  - Gestion globale des erreurs API avec extraction de messages
- ✅ **Routing (React Router v7)**
  - Configuration complète des routes dans `router.tsx`
  - Routes protégées avec ProtectedRoute wrapper
  - Routes publiques avec PublicRoute wrapper (redirections si authentifié)
  - Lazy loading des pages avec React.lazy et Suspense
  - PageLoader avec spinner (border-primary-600)
  - Page 404 avec fallback
  - Redirections automatiques (/ → /dashboard, non-auth → /login)
- ✅ **State Management**
  - AuthContext pour l'authentification complète
  - Gestion du user connecté avec tokens (localStorage)
  - Hooks useAuth disponible pour tous les composants
  - React Query configuré pour cache API (TanStack Query)

#### Structure API - COMPLET ✅
- ✅ **Services API organisés**
  - `api/auth.ts` : login, register, me, refresh, verifyEmail, forgotPassword, resetPassword
  - `api/products.ts` : getAll (avec filtres/pagination), getById, create, update, delete, checkPrice, getHistory, getStats
  - `api/preferences.ts` : get, create, update, delete
  - Barrel exports dans `api/index.ts`

#### Types TypeScript - COMPLET ✅
- ✅ **Types définis et organisés**
  - `types/auth.ts` : User, Token, LoginCredentials, RegisterData, AuthState
  - `types/product.ts` : Product, ProductCreate, ProductUpdate, PaginatedProducts, PriceHistory, PriceStats, ProductFilters
  - `types/preferences.ts` : UserPreferences, UserPreferencesUpdate, NotificationFrequency, WebhookType
  - Barrel exports dans `types/index.ts`

#### Utilitaires - COMPLET ✅
- ✅ **Utils organisés**
  - `utils/cn.ts` : Class name merger (clsx + tailwind-merge)
  - `utils/constants.ts` : CHECK_FREQUENCIES, NOTIFICATION_FREQUENCIES, WEBHOOK_TYPES, SORT_OPTIONS, PAGE_SIZES
  - `utils/formatters.ts` : formatPrice, formatDate, formatDateTime, formatRelativeTime, formatPercentage
  - `utils/validators.ts` : Schémas Zod pour tous les formulaires (login, register, forgot/reset password, product CRUD)
  - Barrel exports dans `utils/index.ts`

#### Pages Structure - COMPLET ✅
- ✅ **Pages créées (skeleton)**
  - Auth : Login, Register, ForgotPassword, ResetPassword, VerifyEmail
  - Dashboard : Dashboard (liste produits)
  - Products : ProductAdd, ProductDetail, ProductEdit
  - Settings : Settings (préférences utilisateur)
  - Toutes les pages utilisent le design system (bg-gray-50, text-gray-900, text-gray-600)

#### 1.4 Authentification - COMPLET ✅
- ✅ **Toutes les pages d'authentification implémentées**
  - Login : Formulaire avec validation, toggle visibilité mot de passe, design conforme maquette
  - Register : Formulaire avec validation temps réel, indicateurs force mot de passe, toggles visibilité
  - VerifyEmail : États loading/success/error, extraction token URL, feedback visuel
  - ForgotPassword : Formulaire demande reset, états conditionnels
  - ResetPassword : Validation mot de passe, indicateurs visuels, gestion token
- ✅ **Intégration complète avec le backend**
  - AuthContext pour gestion état authentification
  - API calls vers endpoints FastAPI
  - Gestion tokens (access + refresh) en localStorage
  - Toasts pour feedback utilisateur
- ✅ **Design system appliqué**
  - Composants Input avec icônes Material Symbols et toggles cliquables
  - Cards, Buttons, Spinners conformes au design system
  - Responsive et conforme aux maquettes Figma

#### 2.1 Layout & Navigation - COMPLET ✅
- ✅ **Composants layout créés** (`components/layout/`)
  - Header : Navigation principale avec logo, menu utilisateur, dropdown, menu mobile
  - Footer : Logo, copyright dynamique, liens (À propos, Support, Confidentialité)
  - Layout : Structure responsive flex column avec header/main/footer
- ✅ **Intégration complète**
  - ProtectedRoute wrapper avec Layout automatique
  - Toutes les pages protégées (Dashboard, Products, Settings) utilisent le Layout
  - Sticky header avec backdrop blur et z-index 50
  - Container responsive (mx-auto px-4 py-6/py-8)
- ✅ **Navigation**
  - Desktop : Navigation horizontale avec états actifs (primary-50/primary-700)
  - Mobile : Menu hamburger avec menu déroulant
  - Avatar utilisateur avec initiale de l'email
  - Dropdown menu avec déconnexion
- ✅ **Qualité du code**
  - ESLint, Prettier, TypeScript checks passés
  - Barrel exports dans `components/layout/index.ts`

#### 2.2 Dashboard - Liste des Produits - COMPLET ✅
- ✅ **Composants produits créés** (`components/products/`)
  - ProductCard : Card avec image, nom, prix, actions (détails, refresh, suppression)
  - EmptyState : États vides (aucun produit, recherche vide)
  - LoadingState : Skeleton loading avec 6 cards animées
  - SearchBar : Champ de recherche avec debounce 300ms et bouton clear
  - SortSelect : Sélecteur tri avec toggle ordre (asc/desc)
  - Pagination : Navigation pages avec numéros, prev/next, métadonnées
- ✅ **Affichage des produits**
  - Grille responsive (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
  - Cards produit avec image, nom, prix actuel/cible, indicateurs visuels
  - Badge "Prix atteint!" si current_price <= target_price
  - Badge "Indisponible" si is_available = false
  - Formatage prix (Intl.NumberFormat EUR), dates (formatDate, formatDateTime)
  - Fréquence de vérification affichée (6h, 12h, 24h)
  - Actions : Détails (lien), Vérifier prix (refresh), Supprimer (avec confirmation)
- ✅ **Fonctionnalités complètes**
  - Pagination : Navigation entre pages avec page_size=12
  - Recherche : Debounce 300ms, reset page à 1 lors de la recherche
  - Tri : 5 options (nom, prix actuel, prix cible, date création, dernière vérif) + ordre asc/desc
  - États vides et loading : EmptyState si aucun produit, LoadingState pendant chargement
  - Gestion erreurs : Toast error avec extraction message API
- ✅ **Intégration API**
  - productsApi.getAll avec filtres (page, page_size, search, sort_by, order)
  - productsApi.delete avec confirmation + refresh liste
  - productsApi.checkPrice avec mise à jour optimiste dans la liste
  - Toast feedback pour toutes les actions (succès, erreur, info)
- ✅ **UX/UI**
  - Header responsive avec bouton "Ajouter un produit"
  - Filtres cachés si aucun produit
  - Smooth scroll to top lors du changement de page
  - Toasts informatifs lors des actions (vérification prix, suppression)
- ✅ **Qualité du code**
  - ESLint, Prettier, TypeScript checks passés
  - Barrel exports dans `components/products/index.ts`
  - Type safety complet avec types Product, SortBy, SortOrder, PaginatedProducts

#### 2.3 Ajout d'un Produit - COMPLET ✅
- ✅ **ProductForm component créé** (`components/products/ProductForm.tsx`)
  - Formulaire avec React Hook Form + Zod validation
  - Champ URL avec validation (type url, required)
  - Champ prix cible avec validation (number, min 0.01€, positive)
  - Sélecteur fréquence de vérification (radio buttons : 6h, 12h, 24h)
  - Icônes Material Symbols (link, euro, schedule)
  - Messages d'aide sous chaque champ
  - Gestion des erreurs de validation avec affichage inline
  - Bouton submit avec état loading
- ✅ **Page ProductAdd complète** (`pages/products/ProductAdd.tsx`)
  - Header avec titre et description
  - Intégration du formulaire ProductForm
  - États de chargement pendant le scraping
  - Affichage du produit créé avec aperçu visuel
  - Card de feedback success avec icône check_circle
  - Aperçu produit : image, nom, prix actuel, prix cible, fréquence
  - Formatage prix (Intl.NumberFormat EUR)
  - Redirection automatique vers dashboard après 2 secondes
  - Message informatif pendant le scraping (spinner + texte)
  - Bouton retour vers le dashboard (disabled pendant loading)
- ✅ **Validation des données**
  - Schéma Zod productCreateSchema avec validations strictes
  - URL : format url valide + min 1 caractère
  - Prix cible : number, positive, min 0.01€
  - Fréquence : union de literals (6, 12, 24) avec default 24
  - Messages d'erreur en français
- ✅ **Intégration API**
  - productsApi.create avec données du formulaire
  - Gestion des erreurs avec extraction message backend
  - Toast success/error avec messages appropriés
  - Loading state pendant l'appel API
- ✅ **UX/UI**
  - Layout max-w-2xl centré pour le formulaire
  - Card pour contenir le formulaire
  - États visuels clairs (loading, success, error)
  - Feedback immédiat avec toasts et cards colorées
  - Bouton retour toujours accessible (sauf pendant loading)
  - Radio buttons stylisés avec hover effects
- ✅ **Qualité du code**
  - ESLint, Prettier, TypeScript checks passés (0 erreur)
  - ProductForm exporté dans barrel export `components/products/index.ts`
  - Type safety complet avec ProductCreateFormData, Product
  - Validators mis à jour avec validations strictes

#### 2.4 Détail d'un Produit - COMPLET ✅
- ✅ **Page ProductDetail complète** (`pages/products/ProductDetail.tsx`)
  - Layout max-w-4xl avec back button vers dashboard
  - Chargement des données produit via productsApi.getById
  - Loading state avec skeleton animé
  - Gestion des erreurs avec redirection vers dashboard
- ✅ **Vue détaillée du produit**
  - Image grande taille (w-64 h-64 md responsive) ou placeholder
  - Nom complet du produit (titre h1)
  - Badge de statut dynamique :
    - Indisponible (danger) : produit non disponible
    - Prix cible atteint (success) : current_price <= target_price
    - En surveillance (neutral) : en cours de suivi
  - Prix actuel (grand, bold) et prix cible (primary)
  - Lien externe vers le site marchand (open_in_new icon, nouvelle fenêtre)
- ✅ **Informations complémentaires** (grid 2 colonnes responsive)
  - Fréquence de vérification (schedule icon) : "Toutes les X heures"
  - Dernière vérification (update icon) : date relative + tooltip date complète
  - Date de création (calendar_today icon) : date formatée
  - Indisponible depuis (error icon, danger color) : affiché si unavailable_since existe
- ✅ **Actions sur le produit** (3 boutons)
  - "Vérifier le prix maintenant" (refresh icon, primary) : appel productsApi.checkPrice
  - "Modifier" (edit icon, secondary) : navigation vers /products/:id/edit
  - "Supprimer" (delete icon, danger) : ouverture modal de confirmation
- ✅ **Modal de confirmation de suppression**
  - Titre "Confirmer la suppression"
  - Message d'avertissement sur l'irréversibilité
  - Affichage du nom du produit à supprimer (card grise)
  - Boutons Annuler (secondary) et Supprimer (danger, loading)
  - Appel productsApi.delete puis redirection vers dashboard
  - Toast success après suppression
- ✅ **États et feedback**
  - Loading states pour chaque action (checking price, deleting)
  - Toast notifications (success/error) pour chaque action
  - Skeleton loading pendant chargement initial
  - Désactivation des boutons pendant les actions
- ✅ **Qualité du code**
  - ESLint, Prettier, TypeScript checks passés (0 erreur)
  - Type safety complet avec Product, useParams, useNavigate
  - Formatters utilisés : formatPrice, formatDateTime, formatRelativeTime
  - Composants UI réutilisés : Card, Button, Badge, Modal

#### 2.5 Modification d'un Produit - COMPLET ✅
- ✅ **Page ProductEdit complète** (`pages/products/ProductEdit.tsx`)
  - Layout max-w-2xl avec back button vers la page détail du produit
  - Chargement des données produit via productsApi.getById
  - Formulaire pré-rempli avec les données du produit (name, target_price, check_frequency)
  - Loading state avec skeleton animé pendant le chargement
  - Gestion des erreurs avec redirection vers dashboard
- ✅ **Formulaire de modification**
  - React Hook Form + Zod validation avec productUpdateSchema
  - Champ nom du produit (text input, shopping_bag icon)
  - Champ prix cible (number input, euro icon, min 0.01€, step 0.01)
  - Radio buttons pour la fréquence de vérification (6h, 12h, 24h)
  - Validation Zod : nom optionnel, prix positif min 0.01€, fréquence 6/12/24
  - Messages d'aide sous chaque champ
  - Gestion des erreurs de validation inline
- ✅ **Actions et navigation**
  - Bouton "Annuler" (secondary) : retour vers /products/:id
  - Bouton "Sauvegarder" (primary, save icon) : soumission du formulaire
  - État isSubmitting pour désactiver les boutons pendant la requête
  - Navigation automatique vers la page détail après succès
- ✅ **Intégration API**
  - productsApi.update avec les données du formulaire
  - Toast success "Produit modifié avec succès !" après mise à jour
  - Toast error "Impossible de modifier le produit" en cas d'échec
  - Mise à jour de l'état local du produit après succès
- ✅ **UX/UI**
  - Card englobant le formulaire
  - Header avec titre et description
  - Radio buttons stylisés avec hover effects (border-primary-500, bg-primary-50)
  - Skeleton loading responsive pendant le chargement initial
  - Désactivation de tous les champs pendant la soumission
- ✅ **Qualité du code**
  - ESLint, Prettier, TypeScript checks passés (0 erreur)
  - Type safety complet avec ProductUpdateFormData, Product
  - Reset du formulaire avec les données du produit (reset method)
  - Composants UI réutilisés : Card, Button, Input

---

## Fonctionnalités à Implémenter (par priorité)

### Priorité 1 - CRITIQUE (Setup & Auth)

#### 1.1 Setup du Projet ✅
- [x] **Initialisation Vite + React + TypeScript**
  - Configuration du projet avec Vite
  - TypeScript strict mode activé
  - Structure de dossiers organisée
- [x] **Configuration Tailwind CSS**
  - Installation et configuration (Tailwind v4)
  - Thème personnalisé avec couleurs du design system :
    - `primary`: #2563EB
    - `background-light`: #F8FAFC
    - `background-dark`: #101722
    - `success`: #16A34A
    - `danger`: #DC3545
  - Plugin forms et typography
  - Border radius custom (0.375rem, 0.5rem, 0.75rem)
- [x] **Import des Google Fonts**
  - Police Inter (weights 400, 500, 600, 700, 900)
  - Material Symbols Outlined pour les icônes
- [x] **Configuration des outils de qualité**
  - ESLint avec règles TypeScript/React
  - Prettier pour le formatage
- [x] **Configuration de l'environnement**
  - Variables d'environnement (.env)
  - Configuration API_URL
  - Mode développement/production

#### 1.2 Design System - Composants de Base - COMPLET ✅
- ✅ **Composants UI fondamentaux**
  - ✅ Button (primary, secondary, danger)
    - Primary : `bg-primary-600 text-white rounded-lg h-10/h-11 px-4 hover:bg-primary-700 focus:ring-2 focus:ring-primary-600`
    - Secondary : `bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-lg px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700`
    - Danger : `bg-danger-600 text-white rounded-lg px-4 py-2 hover:bg-danger-700`
    - États : hover, focus, disabled (`disabled:opacity-50 disabled:cursor-not-allowed`)
    - Support isLoading, leftIcon, rightIcon, fullWidth
    - Tailles : sm, md, lg
  - ✅ Input avec icônes
    - Styles : `rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 h-11 px-4 focus:border-primary-600 focus:ring-2 focus:ring-primary-600/20`
    - Placeholder : `placeholder:text-gray-400 dark:placeholder:text-gray-500`
    - Support leftIcon et rightIcon
    - Support label, error, helperText
  - ✅ Card de base
    - Styles : `rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm p-4/p-6`
    - Hover effect : `hover:shadow-lg hover:border-primary-600/50 transition-all duration-300`
    - Padding configurable : none, sm, md, lg
  - ✅ Badge/Tag
    - Success : `bg-success-100 dark:bg-success-900/50 text-success-700 dark:text-success-300`
    - Primary : `bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300`
    - Warning : `bg-warning-100 dark:bg-warning-900/50 text-warning-700 dark:text-warning-300`
    - Danger : `bg-danger-100 dark:bg-danger-900/50 text-danger-700 dark:text-danger-300`
    - Neutral : `bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300`
    - Styles de base : `inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium`
    - Support icon et dot indicator
- ✅ **Composants feedback essentiels**
  - ✅ Toast/Notification (succès, erreur, info, warning)
    - ToastContainer pour afficher les notifications
    - Hook useToast avec méthodes success, error, warning, info
    - Auto-dismiss configurable
  - ✅ Modal/Dialog de base avec backdrop
    - Backdrop blur
    - Tailles : sm, md, lg, xl
    - Close on Escape et backdrop click configurables
    - Gestion du scroll body
  - ✅ Spinner/Loader
    - Variants : primary, white, current
    - Tailles : xs, sm, md, lg, xl
    - Support label optionnel
- ✅ **Variables CSS pour dark mode**
  - Configuration des couleurs light/dark complète dans index.css
  - Toggle de thème (à implémenter pour activer/désactiver la classe `dark`)
- ✅ **Barrel exports**
  - Tous les composants exportés depuis `@/components/ui`

#### 1.3 Infrastructure Technique ✅ (voir section Fonctionnalités Implémentées)
- [x] **Client HTTP (Axios)** - Complet
- [x] **Routing (React Router v7)** - Complet
- [x] **State Management** - Complet

#### 1.4 Authentification - COMPLET ✅
- ✅ **Page de connexion**
  - Formulaire email/mot de passe avec React Hook Form + Zod
  - Validation des champs en temps réel
  - Affichage des erreurs avec composant Input
  - Toggle de visibilité du mot de passe
  - Icônes Material Symbols (mail, lock, visibility)
  - Lien vers inscription/mot de passe oublié
  - Stockage sécurisé des tokens (localStorage)
  - Design conforme à la maquette Figma
- ✅ **Page d'inscription**
  - Formulaire email/mot de passe/confirmation avec React Hook Form + Zod
  - Validation en temps réel du mot de passe avec indicateurs visuels :
    - Minimum 8 caractères
    - Majuscule, minuscule, chiffre, caractère spécial
  - Toggles de visibilité pour les 2 champs mot de passe
  - Message de confirmation (vérifier email) avec toast
  - Design conforme à la maquette Figma
  - Redirection vers /login après inscription
- ✅ **Vérification d'email**
  - Page de confirmation avec token URL (query param)
  - Feedback visuel (succès/erreur) avec icônes et couleurs
  - États : loading (spinner), success (vert), error (rouge)
  - Redirection vers login après succès
  - Gestion des erreurs (token invalide/expiré)
- ✅ **Mot de passe oublié**
  - Formulaire de demande (email) avec validation
  - Message de confirmation après envoi
  - État conditionnel (formulaire/confirmation)
  - Lien retour vers connexion
- ✅ **Réinitialisation du mot de passe**
  - Formulaire nouveau mot de passe avec confirmation
  - Validation de la force du mot de passe (indicateurs visuels)
  - Token extrait de l'URL
  - Feedback succès/erreur avec états conditionnels
  - Vérification du token avant affichage du formulaire
  - Redirection vers login après succès

---

### Priorité 2 - HAUTE (Core Features)

#### 2.1 Layout & Navigation - COMPLET ✅
- ✅ **Header/Navbar**
  - Logo PriceWatch cliquable (redirection vers dashboard)
  - Navigation principale (Tableau de bord, Ajouter un produit, Paramètres)
  - Menu utilisateur avec dropdown (email, avatar, déconnexion)
  - Avatar avec initiale de l'email
  - États actifs avec surlignage primary-50/primary-700
  - Sticky header avec backdrop blur
- ✅ **Layout principal**
  - Structure responsive flex column (header, main, footer)
  - Container mx-auto avec padding responsive (px-4, py-6/py-8)
  - Footer avec logo, copyright dynamique et liens
  - Option showFooter configurable
  - Fond bg-gray-50 appliqué globalement
- ✅ **Navigation mobile**
  - Menu hamburger fonctionnel
  - Navigation adaptative avec menu déroulant
  - Info utilisateur et déconnexion dans le menu mobile
  - Transitions et états hover

#### 2.2 Dashboard - Liste des Produits - COMPLET ✅
- ✅ **Affichage des produits**
  - Grille responsive des produits suivis (grid-cols-1 md:2 lg:3)
  - Card produit avec :
    - Image du produit (ou placeholder)
    - Nom du produit (line-clamp-2)
    - Prix actuel vs prix cible (formatage EUR)
    - Indicateur visuel (badge vert si prix atteint, rouge si indisponible)
    - Date dernière vérification (formatDate)
    - Fréquence de vérification (6h/12h/24h)
    - Actions : Détails, Vérifier prix, Supprimer
- ✅ **Pagination**
  - Navigation entre pages avec numéros (max 7 pages visibles)
  - Affichage des métadonnées (page X sur Y)
  - Boutons prev/next avec disabled states
  - Smooth scroll to top lors du changement
- ✅ **Recherche**
  - Champ de recherche avec icône
  - Recherche par nom ou URL (backend)
  - Debounce 300ms pour performance
  - Bouton clear pour réinitialiser
- ✅ **Tri**
  - Sélecteur de tri (select)
  - Options : nom, prix actuel, prix cible, date création, dernière vérif
  - Toggle ordre ascendant/descendant (icône flèche)
  - Reset page à 1 lors du changement
- ✅ **États vides et loading**
  - Skeleton loading pendant chargement (6 cards animées)
  - Empty state si aucun produit (avec CTA "Ajouter produit")
  - Empty state pour recherche vide (avec bouton "Effacer")
  - Toast error si échec chargement

#### 2.3 Ajout d'un Produit - COMPLET ✅
- [x] **Formulaire d'ajout**
  - Champ URL du produit
  - Champ prix cible
  - Sélecteur fréquence de vérification (6h, 12h, 24h)
  - Bouton de soumission
- [x] **Feedback utilisateur**
  - Loading pendant le scraping
  - Affichage du produit créé (nom, image, prix extrait)
  - Message d'erreur si URL invalide ou scraping échoué
  - Redirection vers dashboard après succès

#### 2.4 Détail d'un Produit - COMPLET ✅
- [x] **Vue détaillée**
  - Image grande taille
  - Nom complet du produit
  - Prix actuel et prix cible
  - Date de création
  - Dernière vérification
  - Statut de disponibilité
  - Lien vers le site marchand (nouvelle fenêtre)
- [x] **Actions sur le produit**
  - Bouton "Vérifier le prix maintenant"
  - Bouton "Modifier"
  - Bouton "Supprimer" (avec confirmation)

#### 2.5 Modification d'un Produit - COMPLET ✅
- [x] **Formulaire de modification**
  - Champ nom (pré-rempli)
  - Champ prix cible (pré-rempli)
  - Sélecteur fréquence (pré-rempli)
  - Boutons Sauvegarder/Annuler
- [x] **Feedback**
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
  - Prix actuel
  - Prix minimum historique
  - Prix maximum historique
  - Prix moyen
  - Variation en pourcentage (price_change_percentage)
  - Nombre de relevés

#### 3.2 Préférences Utilisateur
- [ ] **Page des paramètres**
  - Section notifications
  - Section webhooks
- [ ] **Notifications email**
  - Toggle activer/désactiver (email_notifications)
  - Toggle alertes baisse de prix (price_drop_alerts)
  - Toggle alertes disponibilité (availability_alerts)
  - Toggle résumé hebdomadaire (weekly_summary)
  - Sélecteur fréquence : instant, daily, weekly (notification_frequency)
- [ ] **Webhooks**
  - Toggle activer/désactiver (webhook_notifications)
  - Champ URL du webhook (webhook_url)
  - Sélecteur type : Slack, Discord, Custom (webhook_type)
  - Test de webhook (optionnel)
- [ ] **Sauvegarde**
  - Bouton sauvegarder
  - Feedback de confirmation

---

### Priorité 4 - BASSE (UX/UI Polish & Accessibilité)

#### 4.1 Composants UI Avancés
- [ ] **Composants supplémentaires**
  - Select/Dropdown personnalisé
  - Checkbox/Toggle animé
  - Avatar avec fallback
  - Progress bar
  - Alert/Banner
- [ ] **Composants navigation**
  - Breadcrumb
  - Tabs

#### 4.2 Améliorations UX
- [ ] **Loading states avancés**
  - Skeletons pour toutes les listes
  - Optimistic updates
- [ ] **Empty states**
  - Messages clairs et actions
  - Illustrations (optionnel)
- [ ] **Error handling avancé**
  - Error boundaries React
  - Pages d'erreur (404, 500)
  - Retry automatique sur erreurs réseau

#### 4.3 Responsive Design - Vérification
- [ ] **Tests responsive complets**
  - Vérifier tous les breakpoints (sm, md, lg, xl)
  - Navigation mobile fluide
  - Cards et grilles adaptatives
  - Formulaires adaptés au mobile
- [ ] **Touch-friendly**
  - Boutons minimum 44x44px
  - Espacement suffisant entre éléments cliquables
  - Swipe actions (optionnel)

#### 4.4 Accessibilité (a11y)
- [ ] **Standards WCAG AA**
  - Labels ARIA appropriés sur tous les composants
  - Navigation clavier complète (Tab, Enter, Escape)
  - Focus visible sur tous les éléments interactifs
  - Alt text pour toutes les images
  - Rôles sémantiques (button, link, navigation, main)
- [ ] **Validation contraste couleurs**
  - Vérifier primary (#2563EB) sur fond blanc
  - Vérifier success (#16A34A) lisibilité
  - Vérifier textes gris sur fonds clairs/sombres
  - Utiliser un outil comme axe ou Lighthouse

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

**Query params pour GET `/products`** :
- `page` (int, default: 1) - Numéro de page
- `page_size` (int, default: 20, max: 100) - Items par page
- `search` (string, optional) - Recherche par nom ou URL
- `sort_by` (enum: name, current_price, target_price, created_at, last_checked)
- `order` (enum: asc, desc)

### Préférences (`/api/v1/users`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/preferences` | Récupérer préférences |
| POST | `/preferences` | Créer préférences |
| PUT | `/preferences` | Modifier préférences |
| DELETE | `/preferences` | Supprimer préférences |

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
  current_price: number;
  lowest_price: number;
  highest_price: number;
  average_price: number;
  price_change_percentage: number | null;
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
  notification_frequency: 'instant' | 'daily' | 'weekly';
  price_drop_alerts: boolean;
  weekly_summary: boolean;
  availability_alerts: boolean;
}

interface UserPreferencesUpdate {
  email_notifications?: boolean;
  webhook_notifications?: boolean;
  webhook_url?: string | null;
  webhook_type?: 'slack' | 'discord' | 'custom' | null;
  notification_frequency?: 'instant' | 'daily' | 'weekly';
  price_drop_alerts?: boolean;
  weekly_summary?: boolean;
  availability_alerts?: boolean;
}
```

---

## Dépendances Principales

### Core
- React 19.2.0
- TypeScript 5.9.3
- Vite 7.2.4

### Styling
- Tailwind CSS 4.1.17
- @tailwindcss/vite 4.1.17
- @tailwindcss/forms 0.5.10
- @tailwindcss/typography 0.5.19

### Routing & State
- React Router 7.9.6
- Zustand 5.0.8 (disponible)
- Context API (AuthContext implémenté)

### HTTP & Data
- Axios 1.13.2
- TanStack React Query 5.90.10

### UI Components
- Headless UI (ou Radix UI)
- React Icons (ou Heroicons)

### Charts
- Recharts (ou Chart.js)

### Forms
- React Hook Form 7.66.1
- Zod 4.1.13 (validation)
- @hookform/resolvers 5.2.2

### Utils
- date-fns 4.1.0 (dates)
- clsx 2.1.1 (classnames)
- tailwind-merge 3.4.0 (merge classes)

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

## Documentation Associée

- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Spécifications complètes du design system (couleurs, typographie, composants, Tailwind config)

---

**Dernière mise à jour** : 2025-12-03

### Changelog
- **2025-12-03** :
  - ✅ **Modification d'un Produit (2.5)** - Page d'édition complète et fonctionnelle
    - Page ProductEdit : Layout max-w-2xl, back button vers page détail, skeleton loading
    - Formulaire pré-rempli avec données du produit (name, target_price, check_frequency)
    - React Hook Form + Zod validation avec productUpdateSchema
    - Champs : Nom du produit (text input, shopping_bag icon), Prix cible (number, euro icon), Fréquence (radio buttons 6h/12h/24h)
    - Validation Zod : nom optionnel min 1 caractère, prix positif min 0.01€, fréquence 6/12/24
    - Actions : Bouton Annuler (secondary, retour vers détail) et Sauvegarder (primary, save icon)
    - Intégration API : productsApi.update avec toast success/error
    - Navigation automatique vers page détail après succès
    - États : isLoading (skeleton), isSubmitting (désactive tous les champs)
    - UX/UI : Card englobant formulaire, radio buttons stylisés avec hover effects
    - Qualité : ESLint, Prettier, TypeScript checks passés (0 erreur)
- **2025-12-02** :
  - ✅ **Détail d'un Produit (2.4)** - Page détaillée complète et fonctionnelle
    - Page ProductDetail : Layout max-w-4xl, back button vers dashboard, skeleton loading
    - Vue détaillée : Image grande taille (ou placeholder), nom complet, badge statut dynamique
    - Badges : Indisponible (danger), Prix cible atteint (success), En surveillance (neutral)
    - Affichage prix : Prix actuel (grand, bold) et prix cible (primary, xl)
    - Lien externe vers site marchand (open_in_new icon, nouvelle fenêtre)
    - Infos complémentaires en grid responsive : fréquence, dernière vérif, date création, indisponibilité
    - Actions : Vérifier prix (refresh, primary), Modifier (edit, secondary), Supprimer (delete, danger)
    - Modal de confirmation suppression : Titre, message avertissement, nom produit, boutons Annuler/Supprimer
    - États loading pour chaque action (checking price, deleting)
    - Toast notifications pour toutes les actions (success/error)
    - Intégration API : getById, checkPrice, delete avec redirection dashboard
    - Formatters : formatPrice, formatDateTime, formatRelativeTime
    - Gestion erreurs : Toast + redirection dashboard si produit introuvable
    - Qualité : ESLint, Prettier, TypeScript checks passés (0 erreur)
- **2025-12-01** :
  - ✅ **Ajout d'un Produit (2.3)** - Formulaire d'ajout de produit complet et fonctionnel
    - Composant ProductForm : Formulaire avec React Hook Form + Zod (URL, prix cible, fréquence)
    - Page ProductAdd : États loading/success/error, aperçu du produit créé, redirection automatique
    - Validation stricte : URL valide, prix positif min 0.01€, fréquence 6/12/24h
    - Radio buttons stylisés pour la fréquence avec hover effects
    - Feedback visuel complet : card success avec aperçu produit (image, nom, prix, fréquence)
    - Message informatif pendant le scraping avec spinner
    - Intégration API productsApi.create avec gestion erreurs
    - Toast notifications success/error
    - Formatage prix (EUR) et affichage des infos scrapées
    - Bouton retour vers dashboard (disabled pendant loading)
    - Qualité : ESLint, Prettier, TypeScript checks passés (0 erreur)
- **2025-11-28** :
  - ✅ **Dashboard - Liste des Produits (2.2)** - Page dashboard complète et fonctionnelle
    - Composants products : ProductCard, EmptyState, LoadingState, SearchBar, SortSelect, Pagination
    - Grille responsive avec cards produits complètes (image, nom, prix, badges, actions)
    - Pagination avec navigation intelligente (max 7 pages visibles, prev/next)
    - Recherche avec debounce 300ms et bouton clear
    - Tri avec 5 options (nom, prix actuel, prix cible, date création, dernière vérif) + toggle ordre
    - États vides (aucun produit, recherche vide) et loading (skeleton 6 cards)
    - Intégration API complète (getAll, delete, checkPrice)
    - Actions : Détails (navigation), Vérifier prix (refresh), Supprimer (confirmation)
    - Toasts feedback pour toutes les actions
    - Formatage prix (EUR) et dates (fr-FR)
    - Badges "Prix atteint!" (vert) et "Indisponible" (rouge)
    - Header responsive avec bouton "Ajouter un produit"
    - Smooth scroll to top lors du changement de page
    - Type safety complet avec types Product, SortBy, SortOrder, PaginatedProducts
    - Qualité : ESLint, Prettier, TypeScript checks passés (0 erreur)
- **2025-11-27** :
  - ✅ **Layout & Navigation (2.1)** - Structure complète de l'application
    - Header/Navbar : Logo cliquable, navigation principale, menu utilisateur avec dropdown
    - Footer : Logo, copyright dynamique, liens utiles
    - Layout responsive : Structure flex column, container responsive, sticky header avec backdrop blur
    - Navigation mobile : Menu hamburger fonctionnel avec menu déroulant
    - Avatar utilisateur avec initiale de l'email
    - États actifs (primary-50/primary-700) et transitions
    - Intégration automatique dans toutes les pages protégées via ProtectedRoute
  - ✅ **Qualité frontend** - Scripts de linting et vérifications complètes
    - Script run_linting.sh créé (ESLint, Prettier, TypeScript)
    - Tous les checks de qualité passent (0 erreur)
    - Composants routes séparés (PageLoader, ProtectedRoute, PublicRoute)
    - Hook useAuth extrait dans fichier séparé
- **2025-11-26** :
  - ✅ **Authentification complète (1.4)** - Toutes les pages d'authentification fonctionnelles
    - Page de connexion avec toggle visibilité mot de passe et design conforme maquette
    - Page d'inscription avec validation temps réel et indicateurs force mot de passe
    - Vérification d'email avec états loading/success/error
    - Mot de passe oublié et réinitialisation avec validation
  - ✅ **Composant Input amélioré** - Support rightIconClickable pour toggles interactifs
  - ✅ **Dark mode** - Configuration class-based (au lieu de media query automatique)
  - ✅ **Backend OAuth2** - Migration vers OAuth2PasswordRequestForm standard
  - ✅ **Tests unitaires** - 282 tests passants avec 72.80% de couverture
- **2025-11-25** :
  - ✅ Setup complet (Vite, React, TypeScript, Tailwind v4)
  - ✅ Infrastructure technique (Axios, React Router v7, AuthContext)
  - ✅ Structure API complète avec tous les endpoints
  - ✅ Types TypeScript complets
  - ✅ Utilitaires (formatters, validators, constants)
  - ✅ Pages skeleton créées avec design system
  - ✅ Design system étendu (warning, error, slate colors)
  - ✅ Configuration Docker Compose
  - ✅ **Composants UI de base** (Button, Input, Card, Badge, Toast, Modal, Spinner)
  - ✅ Hook useToast pour la gestion des notifications
  - ✅ Barrel exports pour tous les composants UI
- **2025-11-22** : Création initiale de la roadmap
