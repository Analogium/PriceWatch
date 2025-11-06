# 🗺️ RoadMap Backend - PriceWatch

## 📋 Vue d'ensemble

Ce document trace l'état d'avancement du backend de PriceWatch, ce qui a été implémenté et ce qui reste à faire.

---

## ✅ Fonctionnalités Implémentées

### 🏗️ Infrastructure de base
- [x] Configuration FastAPI avec CORS
- [x] Structure du projet organisée (MVC)
- [x] Configuration via variables d'environnement
- [x] Base de données PostgreSQL avec SQLAlchemy ORM
- [x] Conteneurisation Docker
- [x] Endpoints de santé (`/health`, `/`)

### 🔐 Authentification & Sécurité
- [x] Système d'authentification JWT
- [x] Hachage sécurisé des mots de passe (bcrypt)
- [x] Routes d'authentification :
  - `POST /api/v1/auth/register` - Inscription
  - `POST /api/v1/auth/login` - Connexion
  - `GET /api/v1/auth/me` - Informations utilisateur
- [x] Middleware de vérification du token JWT
- [x] Gestion des dépendances utilisateur (`get_current_user`)

### 📦 Gestion des Produits
- [x] CRUD complet pour les produits :
  - `GET /api/v1/products` - Liste des produits de l'utilisateur
  - `POST /api/v1/products` - Ajout d'un produit
  - `GET /api/v1/products/{id}` - Détails d'un produit
  - `PUT /api/v1/products/{id}` - Mise à jour (nom, prix cible)
  - `DELETE /api/v1/products/{id}` - Suppression
  - `POST /api/v1/products/{id}/check` - Vérification manuelle du prix
- [x] Extraction automatique des données produit lors de l'ajout (nom, prix, image)
- [x] Mise à jour de `last_checked` à chaque vérification

### 🕷️ Web Scraping
- [x] Service de scraping implémenté (`app/services/scraper.py`)
- [x] Support multi-sites (Amazon, Fnac, Darty, etc.)
- [x] Extraction du titre, prix et image
- [x] Gestion des erreurs de scraping

### 📧 Notifications Email
- [x] Service email implémenté (`app/services/email.py`)
- [x] Envoi d'alertes lors de baisse de prix
- [x] Template d'email avec informations du produit
- [x] Exécution en tâche de fond (BackgroundTasks)

### ⏰ Tâches Planifiées (Celery)
- [x] Configuration Celery + Redis
- [x] Tâche `check_all_prices` - Vérification quotidienne de tous les produits
- [x] Tâche `check_single_product` - Vérification d'un produit spécifique
- [x] Celery Beat configuré (exécution toutes les 24h)
- [x] Envoi automatique d'alertes si prix ≤ seuil

### 🗄️ Base de Données
- [x] Modèle `User` :
  - id, email, password_hash, created_at
- [x] Modèle `Product` :
  - id, user_id, name, url, image, current_price, target_price, last_checked, created_at
- [x] Relations One-to-Many (User → Products)
- [x] Création automatique des tables au démarrage

### 📝 Schémas Pydantic
- [x] Schémas utilisateur (UserCreate, UserLogin, UserResponse, Token)
- [x] Schémas produit (ProductCreate, ProductUpdate, ProductResponse)
- [x] Validation des emails et données

---

## 🚧 Fonctionnalités à Implémenter

### 🔒 Sécurité & Authentification
- [ ] **Refresh tokens** pour renouveler l'accès sans redemander les identifiants
- [ ] **Limitation de taux (rate limiting)** pour prévenir les abus
- [ ] **Vérification d'email** lors de l'inscription (envoi de lien de confirmation)
- [ ] **Réinitialisation de mot de passe** (forgot password flow)
- [ ] **OAuth2** - Connexion via Google/GitHub (optionnel)
- [ ] **Politique de mots de passe forts** (longueur minimale, complexité)

### 📊 Historique des Prix
- [ ] **Modèle `PriceHistory`** pour stocker l'évolution des prix
  - id, product_id, price, recorded_at
- [ ] **Endpoint** `GET /api/v1/products/{id}/history` - Récupérer l'historique
- [ ] Enregistrement automatique des prix à chaque vérification
- [ ] Graphiques d'évolution des prix (intégration frontend)

### 🛡️ Gestion des Erreurs Avancée
- [ ] **Logging structuré** (rotation des logs, niveaux de log)
- [ ] **Retry logic** pour le scraping en cas d'échec temporaire
- [ ] **Circuit breaker** pour éviter de surcharger les sites cibles
- [ ] **Monitoring** - Alertes en cas d'échec massif de scraping
- [ ] **Gestion des produits indisponibles** (out of stock detection)

### 🕷️ Amélioration du Scraping
- [ ] **Support Playwright/Selenium** pour sites JavaScript dynamiques
- [ ] **Détection automatique du site** (pattern matching sur URL)
- [ ] **Gestion des CAPTCHAs** (délégation à service tiers ou proxies rotatifs)
- [ ] **Proxies rotatifs** pour éviter les blocages IP
- [ ] **User-Agent rotation** pour simuler différents navigateurs
- [ ] **Support de nouveaux sites** (Cdiscount, Boulanger, Leclerc, etc.)
- [ ] **Cache des résultats de scraping** (éviter de rescraper trop souvent)

### 📧 Notifications Avancées
- [ ] **Webhooks** pour intégrations externes (Slack, Discord)
- [ ] **Notifications push** (via Firebase ou services similaires)
- [ ] **SMS** via Twilio (optionnel, coût à considérer)
- [ ] **Préférences de notification par utilisateur** (fréquence, canaux)
- [ ] **Résumé hebdomadaire** (email récapitulatif des baisses de prix)
- [ ] **Templates d'emails personnalisables**

### 🔄 Optimisation des Tâches Planifiées
- [ ] **Tâches par utilisateur** (vérifications à des heures différentes)
- [ ] **Priorité des vérifications** (produits proches du seuil en premier)
- [ ] **Parallelisation** du scraping (plusieurs produits en même temps)
- [ ] **Configuration de fréquence par produit** (toutes les 6h, 12h, 24h)
- [ ] **Pause automatique** des produits inactifs (non vérifiés depuis longtemps)

### 💳 Monétisation & Plans
- [ ] **Modèle `Subscription`** (plan, statut, date d'expiration)
- [ ] **Limitation par plan** :
  - Free : 5 produits, vérif quotidienne
  - Pro : 50 produits, vérif toutes les 6h
  - Business : 500 produits, vérif personnalisée
- [ ] **Intégration Stripe** pour paiements
- [ ] **Webhook Stripe** pour mise à jour automatique du statut
- [ ] **Endpoint** `GET /api/v1/users/subscription` - Info abonnement
- [ ] **Upgrade/downgrade** de plan

### 🧪 Tests & Qualité
- [ ] **Tests unitaires** (pytest) pour :
  - Authentification
  - CRUD produits
  - Services (scraper, email)
  - Tâches Celery
- [ ] **Tests d'intégration** (base de données)
- [ ] **Tests E2E** (simulation de flux utilisateur complet)
- [ ] **Coverage minimum** de 80%
- [ ] **CI/CD pipeline** (GitHub Actions / GitLab CI)
- [ ] **Linting & formatting** (black, flake8, mypy)

### 📊 Administration & Analytics
- [ ] **Endpoint admin** pour statistiques globales
- [ ] **Dashboard admin** :
  - Nombre d'utilisateurs
  - Nombre de produits suivis
  - Taux de réussite du scraping
  - Alertes envoyées
- [ ] **Logs d'activité** (qui a ajouté/supprimé quoi)
- [ ] **Export CSV** des données utilisateur (RGPD)

### 🔧 DevOps & Déploiement
- [ ] **Migrations Alembic** (gestion des changements de schéma)
- [ ] **Variables d'environnement sécurisées** (secrets management)
- [ ] **Healthchecks avancés** (vérification DB, Redis, Celery)
- [ ] **Backup automatique** de la base de données
- [ ] **Déploiement production** (AWS, GCP, DigitalOcean)
- [ ] **Monitoring** (Sentry, New Relic, DataDog)
- [ ] **Load balancing** pour haute disponibilité

### 📱 API Améliorations
- [ ] **Pagination** pour les listes de produits
- [ ] **Filtres & tri** (par prix, date d'ajout, nom)
- [ ] **Recherche** de produits par nom/URL
- [ ] **Bulk operations** (ajout/suppression multiple)
- [ ] **Rate limiting par utilisateur**
- [ ] **Versioning API** (v2, v3...)
- [ ] **Documentation OpenAPI enrichie** (exemples, descriptions)

### 🌍 Internationalisation
- [ ] **Support multi-devises** (EUR, USD, GBP)
- [ ] **Détection automatique de la devise** depuis l'URL
- [ ] **Conversion de devises** (API taux de change)
- [ ] **Support multi-langues** pour les emails/notifications

### 🔎 Fonctionnalités Avancées
- [ ] **Comparaison de prix** entre plusieurs sites pour un même produit
- [ ] **Alertes de disponibilité** (produit de nouveau en stock)
- [ ] **Prédiction de prix** (ML pour anticiper les baisses)
- [ ] **Partage de listes** (wishlists publiques/privées)
- [ ] **Import de liste de souhaits** depuis Amazon/autres sites
- [ ] **Extension navigateur** pour ajout rapide de produits

---

## 🐛 Bugs Connus & Points d'Attention

- [ ] **Gestion des sites qui changent leur structure HTML** (scraping fragile)
- [ ] **Pas de gestion des produits supprimés/indisponibles** sur le site marchand
- [ ] **Pas de limite sur le nombre de produits par utilisateur** (risque d'abus en Free)
- [ ] **Pas de validation de l'URL** lors de l'ajout (peut être une URL invalide)
- [ ] **Emails pas testés en production** (configuration SMTP à valider)
- [ ] **Celery Beat ne persiste pas l'état** (redémarrage = perte du schedule)

---

## 🎯 Priorités pour les prochaines releases

### Version 1.1 (Court terme)
1. Historique des prix
2. Tests unitaires de base
3. Migrations Alembic
4. Rate limiting
5. Amélioration de la gestion des erreurs

### Version 1.2 (Moyen terme)
1. Refresh tokens
2. Réinitialisation de mot de passe
3. Support Playwright pour scraping JS
4. Notifications webhook
5. Pagination & filtres API

### Version 2.0 (Long terme)
1. Système de plans & abonnements
2. Intégration Stripe
3. Dashboard admin
4. Comparaison multi-sites
5. Extension navigateur

---

## 📝 Notes Techniques

### Dépendances actuelles
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- Celery 5.3.6 + Redis 5.0.1
- BeautifulSoup4 4.12.3
- Python-jose (JWT)
- Bcrypt (hachage)

### Points d'attention architecture
- Le scraping est synchrone (bloquant) → envisager async avec `httpx` ou `aiohttp`
- Celery Beat nécessite Redis running en continu
- Pas de cache actuellement → envisager Redis pour cache des scraped data
- Logs pas structurés → implémenter logging.config

---

**Dernière mise à jour** : 06/11/2025
