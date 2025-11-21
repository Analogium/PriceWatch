# PriceWatch - Design Brief pour Stitch

## 1. Présentation du Projet

**Nom**: PriceWatch
**Type**: Application web de surveillance de prix e-commerce
**Objectif**: Permettre aux utilisateurs de suivre les prix de produits en ligne et recevoir des alertes quand les prix baissent sous un seuil défini.

**Proposition de valeur**: "Surveillez les prix, pas vos onglets."

---

## 2. Utilisateurs Cibles

- **Profil principal**: Acheteurs en ligne réguliers (25-45 ans)
- **Besoins**: Économiser de l'argent, éviter de vérifier manuellement les prix
- **Contexte d'utilisation**: Desktop principalement, mobile pour consultation rapide

---

## 3. Exigences SEO et Performance

### 3.1 Structure SEO

#### Balises meta essentielles
- **Title** unique par page (50-60 caractères)
- **Meta description** optimisée (150-160 caractères)
- **Canonical URL** pour éviter le contenu dupliqué
- **Open Graph** (og:title, og:description, og:image) pour partage social
- **Twitter Cards** (twitter:card, twitter:title, twitter:image)

#### Hiérarchie des titres
- Un seul `<h1>` par page (mot-clé principal)
- Structure logique H1 → H2 → H3
- Mots-clés dans les sous-titres

#### URLs optimisées
- URLs courtes et descriptives
- Mots-clés dans l'URL
- Structure: `/fonctionnalites`, `/tarifs`, `/connexion`, `/inscription`

### 3.2 Pages SEO-friendly (Landing Pages)

#### Page d'accueil
**Mots-clés cibles**: surveillance prix, alerte prix, tracker prix, comparateur prix
- H1: "Surveillez les prix et économisez automatiquement"
- Contenu structuré avec H2/H3 pour fonctionnalités
- Section FAQ avec schema.org FAQPage
- Témoignages utilisateurs

#### Page "Comment ça marche"
**Mots-clés**: suivre prix produit, alerte baisse prix, notification prix
- Guide étape par étape
- Images avec alt text optimisé
- Liens internes vers inscription

#### Page "Sites supportés"
**Mots-clés**: tracker prix Amazon, surveillance Fnac, alerte Cdiscount
- Liste des 6 sites supportés avec descriptions
- Schema.org pour liste de services

#### Page "Tarifs" (si applicable)
- Comparaison claire des plans
- Schema.org Product/Offer
- FAQ sur les tarifs

#### Blog/Articles (optionnel mais recommandé)
- Conseils pour économiser
- Guides d'achat
- Actualités e-commerce

### 3.3 Performance Web (Core Web Vitals)

#### Optimisations requises
- **LCP (Largest Contentful Paint)** < 2.5s
  - Images optimisées (WebP, lazy loading)
  - Preload des ressources critiques
- **FID (First Input Delay)** < 100ms
  - JavaScript différé/asynchrone
  - Code splitting
- **CLS (Cumulative Layout Shift)** < 0.1
  - Dimensions d'images définies
  - Fonts avec font-display: swap

#### Images
- Format WebP avec fallback
- Attributs `width` et `height` définis
- Alt text descriptif avec mots-clés
- Lazy loading pour images below-the-fold

### 3.4 Données Structurées (Schema.org)

```json
// Page d'accueil - WebApplication
{
  "@type": "WebApplication",
  "name": "PriceWatch",
  "description": "Application de surveillance de prix en ligne",
  "applicationCategory": "ShoppingApplication",
  "operatingSystem": "Web"
}

// FAQ
{
  "@type": "FAQPage",
  "mainEntity": [...]
}

// Avis utilisateurs
{
  "@type": "Product",
  "aggregateRating": {...}
}
```

### 3.5 Accessibilité (a11y)

- Contraste WCAG AA minimum (4.5:1)
- Labels pour tous les champs de formulaire
- Navigation au clavier complète
- ARIA labels pour éléments interactifs
- Skip links pour navigation principale

---

## 4. Pages et Écrans Requis

### 4.1 Pages Publiques (SEO importantes)

#### Page d'accueil (Landing)
- Hero section avec H1 optimisé et proposition de valeur
- Section "Comment ça marche" (3 étapes avec icônes)
- Section sites e-commerce supportés (logos: Amazon, Fnac, Darty, Cdiscount, Boulanger, E.Leclerc)
- Section avantages/bénéfices
- Témoignages utilisateurs (schema.org Review)
- FAQ (schema.org FAQPage)
- CTA vers inscription
- Footer avec liens (À propos, Contact, CGU, Politique de confidentialité)

#### Page de connexion
- Formulaire: email, mot de passe
- Lien "Mot de passe oublié"
- Lien vers inscription
- Meta noindex (pas de SEO nécessaire)

#### Page d'inscription
- Formulaire: email, mot de passe, confirmation mot de passe
- Indicateur de force du mot de passe (8+ caractères, majuscule, minuscule, chiffre, caractère spécial)
- Lien vers connexion
- Meta noindex

#### Page de réinitialisation mot de passe
- Étape 1: Saisie email
- Étape 2: Saisie nouveau mot de passe (après clic sur lien email)
- Meta noindex

---

### 4.2 Pages Authentifiées (Dashboard)

#### Dashboard principal - Liste des produits
**Éléments clés**:
- Barre de recherche (recherche par nom/URL)
- Filtres de tri (par prix, date d'ajout, nom) - ordre ascendant/descendant
- Pagination (20 items par page)
- Bouton "Ajouter un produit"

**Carte produit** (affichage grille ou liste):
- Image du produit (lazy loading, alt text)
- Nom du produit
- Prix actuel (mise en évidence)
- Prix cible défini
- Indicateur de progression vers le prix cible (barre ou pourcentage)
- Statut de disponibilité (disponible/indisponible)
- Dernière vérification (date/heure)
- Fréquence de vérification (6h, 12h, 24h)
- Actions: Voir détails, Modifier, Supprimer, Vérifier maintenant

**États visuels des produits**:
- Prix atteint (vert) - prix actuel ≤ prix cible
- En surveillance (neutre) - prix au-dessus du cible
- Indisponible (gris/barré) - produit non disponible

#### Modal/Page - Ajouter un produit
- Champ URL du produit (obligatoire)
- Champ prix cible (obligatoire)
- Sélecteur fréquence de vérification (6h, 12h, 24h)
- Prévisualisation automatique (nom, image, prix actuel) après saisie URL

#### Page détail produit
- Image grande taille
- Informations complètes du produit
- **Graphique d'historique des prix** (courbe temporelle)
- Statistiques: prix min, prix max, prix moyen, variation %
- Formulaire de modification (nom, prix cible, fréquence)
- Bouton "Vérifier le prix maintenant"
- Bouton "Supprimer"

#### Page Préférences utilisateur
**Notifications email**:
- Toggle: Activer/désactiver les notifications email
- Toggle: Alertes de baisse de prix
- Toggle: Résumé hebdomadaire
- Toggle: Alertes de disponibilité

**Webhooks** (notifications externes):
- Toggle: Activer/désactiver les webhooks
- Sélecteur type: Slack, Discord, Personnalisé
- Champ URL du webhook
- Bouton test webhook

**Compte**:
- Email (lecture seule)
- Bouton changer mot de passe
- Bouton supprimer compte

---

### 4.3 Pages Admin (si utilisateur admin)

#### Dashboard Admin
- Statistiques globales:
  - Nombre total d'utilisateurs
  - Nombre total de produits surveillés
  - Taux de réussite du scraping
  - Temps de réponse moyen

#### Statistiques par site
- Tableau avec: nom du site, nombre de produits, taux de succès, temps moyen

#### Gestion utilisateurs
- Liste paginée des utilisateurs
- Actions: Voir stats, Promouvoir admin, Supprimer
- Export données utilisateur (RGPD)

---

## 5. Composants UI Réutilisables

### Navigation
- **Header**: Logo (avec alt text), navigation principale, menu utilisateur (avatar + dropdown)
- **Breadcrumbs** pour SEO et UX
- **Footer**: Liens légaux, réseaux sociaux, sitemap

### Éléments de formulaire
- Input text avec validation et labels accessibles
- Input email avec validation
- Input password avec toggle visibilité
- Select/Dropdown
- Toggle switch avec ARIA
- Boutons (primaire, secondaire, danger)

### Feedback utilisateur
- Toast notifications (succès, erreur, info)
- Loading states (spinners, skeletons)
- États vides (aucun produit, aucun résultat de recherche)
- Messages d'erreur inline

### Data display
- Cartes produit
- Tableaux avec tri et pagination
- Graphiques (ligne pour historique prix)
- Badges de statut
- Progress bars

---

## 6. Directives de Design

### Palette de couleurs suggérée
- **Primaire**: Bleu (confiance, technologie) - #2563EB
- **Succès/Prix atteint**: Vert - #16A34A
- **Alerte/Baisse de prix**: Orange - #EA580C
- **Erreur/Indisponible**: Rouge - #DC2626
- **Neutre**: Gris pour textes secondaires et bordures
- **Contraste WCAG AA** respecté pour tous les textes

### Typographie
- Police moderne et lisible (Inter, Poppins, ou similaire)
- Hiérarchie claire (titres, sous-titres, corps, légendes)
- Tailles minimales: 16px corps, 14px légendes
- Line-height: 1.5 minimum pour lisibilité

### Style général
- Design moderne et épuré
- Espacement généreux (système 8px)
- Coins arrondis (border-radius: 8px)
- Ombres subtiles pour profondeur
- Mode sombre optionnel

### Responsive
- Mobile-first pour performance
- Breakpoints: 375px, 768px, 1024px, 1440px
- Touch targets minimum 44x44px sur mobile

---

## 7. Interactions et Micro-animations

- Hover sur les cartes produit (élévation)
- Transition sur les toggles (respect prefers-reduced-motion)
- Animation de chargement lors de la vérification de prix
- Feedback visuel sur les boutons (pressed state)
- Animation du graphique d'historique au chargement

---

## 8. Flux Utilisateur Principal

1. **Découverte** (SEO/Social) → Page d'accueil
2. **Inscription** → Vérification email → **Connexion**
3. **Dashboard vide** → Clic "Ajouter produit"
4. **Modal ajout** → Saisie URL → Prévisualisation → Définir prix cible → Confirmer
5. **Dashboard avec produit** → Surveillance automatique
6. **Notification** (email/webhook) quand prix atteint
7. **Détail produit** → Consulter historique → Modifier/Supprimer

---

## 9. États et Edge Cases

### États de chargement
- Skeleton screens pour chargement initial (meilleur pour CLS)
- Vérification manuelle d'un prix en cours
- Ajout d'un nouveau produit (scraping en cours)

### États d'erreur
- URL invalide ou site non supporté
- Échec du scraping (produit non trouvé)
- Erreur réseau
- Session expirée

### États vides
- Aucun produit surveillé (avec CTA clair)
- Aucun résultat de recherche
- Aucun historique de prix

---

## 10. Informations Techniques (pour référence)

### API Endpoints principaux
- `POST /api/v1/auth/register` - Inscription
- `POST /api/v1/auth/login` - Connexion
- `GET /api/v1/products` - Liste produits (pagination, tri, recherche)
- `POST /api/v1/products` - Ajouter produit
- `GET /api/v1/products/{id}` - Détail produit
- `GET /api/v1/products/{id}/history` - Historique prix
- `GET /api/v1/products/{id}/history/stats` - Stats prix
- `PUT /api/v1/products/{id}` - Modifier produit
- `DELETE /api/v1/products/{id}` - Supprimer produit
- `POST /api/v1/products/{id}/check` - Vérifier prix manuellement

### Données produit
```json
{
  "id": 1,
  "name": "iPhone 15 Pro",
  "url": "https://amazon.fr/dp/...",
  "image": "https://...",
  "current_price": 1199.99,
  "target_price": 999.99,
  "is_available": true,
  "check_frequency": 12,
  "last_checked": "2025-01-15T10:30:00",
  "created_at": "2025-01-01T08:00:00"
}
```

---

## 11. Livrables Attendus

1. **Maquettes haute fidélité** pour toutes les pages listées
2. **Design system** avec composants réutilisables
3. **Prototypes interactifs** pour les flux principaux
4. **Assets exportables** (icônes, illustrations si nécessaire)
5. **Spécifications** pour les développeurs (espacements, couleurs, typographie)
6. **Guidelines SEO** intégrées (structure H1-H6, alt texts, etc.)

---

## 12. Priorités

### Phase 1 (MVP)
- Page d'accueil optimisée SEO
- Page de connexion/inscription
- Dashboard avec liste de produits
- Modal ajout produit
- Page détail produit avec historique

### Phase 2
- Page préférences utilisateur
- Notifications et webhooks
- Mode sombre
- Pages SEO additionnelles (Comment ça marche, FAQ)

### Phase 3
- Dashboard admin
- Blog/Contenu SEO
- Fonctionnalités avancées

---

## 13. Checklist SEO pour chaque page

- [ ] Title unique et optimisé (50-60 caractères)
- [ ] Meta description (150-160 caractères)
- [ ] Un seul H1 avec mot-clé principal
- [ ] Hiérarchie H2-H6 logique
- [ ] Images avec alt text descriptif
- [ ] URLs propres et descriptives
- [ ] Liens internes pertinents
- [ ] Schema.org approprié
- [ ] Open Graph et Twitter Cards
- [ ] Canonical URL
- [ ] Temps de chargement < 3s
- [ ] Mobile-friendly
- [ ] Contraste accessible

---

**Contact**: [Votre email]
**Date**: 2025-01-21
