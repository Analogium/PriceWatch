# 🗺️ RoadMap Backend - PriceWatch

## 📋 Vue d'ensemble

Ce document trace l'état d'avancement du backend de PriceWatch, ce qui a été implémenté et ce qui reste à faire, **organisé par ordre de priorité**.

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
  - `POST /api/v1/auth/refresh` - Rafraîchir le token ✨ NEW
  - `POST /api/v1/auth/verify-email` - Vérifier l'email ✨ NEW
  - `POST /api/v1/auth/forgot-password` - Demander réinitialisation ✨ NEW
  - `POST /api/v1/auth/reset-password` - Réinitialiser mot de passe ✨ NEW
- [x] Middleware de vérification du token JWT
- [x] Gestion des dépendances utilisateur (`get_current_user`)
- [x] **Refresh tokens** (7 jours) avec access tokens courts (30 min) ✨ NEW
- [x] **Rate limiting** basé sur Redis (100 req/min par IP) ✨ NEW
- [x] **Politique de mots de passe forts** (8+ chars, majuscule, minuscule, chiffre, spécial) ✨ NEW
- [x] **Vérification d'email** avec token unique envoyé par email ✨ NEW
- [x] **Réinitialisation de mot de passe** avec token temporaire (1h) ✨ NEW

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
- [x] Suivi de disponibilité avec `is_available` et `unavailable_since` ✨ NEW

### 📊 Historique des Prix
- [x] **Modèle `PriceHistory`** pour stocker l'évolution des prix
  - id, product_id, price, recorded_at
- [x] **Endpoint** `GET /api/v1/products/{id}/history` - Récupérer l'historique avec limite configurable ✨ NEW
- [x] **Endpoint** `GET /api/v1/products/{id}/history/stats` - Statistiques de prix (min, max, moyenne, changement %) ✨ NEW
- [x] Enregistrement automatique des prix à chaque vérification (produits et tâches Celery) ✨ NEW
- [x] Évite les duplications (n'enregistre que si le prix a changé) ✨ NEW

### 🕷️ Web Scraping
- [x] Service de scraping implémenté (`app/services/scraper.py`)
- [x] Support multi-sites : Amazon, Fnac, Darty, Cdiscount, Boulanger, E.Leclerc ✨ NEW
- [x] Détection automatique du site par pattern matching ✨ NEW
- [x] Extraction du titre, prix et image
- [x] Gestion des erreurs de scraping avec retry logic et logging ✨ NEW

### 📧 Notifications Email & Webhooks
- [x] Service email implémenté (`app/services/email.py`)
- [x] Envoi d'alertes lors de baisse de prix
- [x] Template d'email avec informations du produit
- [x] Exécution en tâche de fond (BackgroundTasks)
- [x] Email de vérification d'inscription ✨ NEW
- [x] Email de réinitialisation de mot de passe ✨ NEW
- [x] Respect des préférences utilisateur (email_notifications, price_drop_alerts) ✨ **NEW**
- [x] Envoi de webhooks pour notifications externes ✨ **NEW**
  - [x] Support Slack (blocks interactifs)
  - [x] Support Discord (embeds colorés)
  - [x] Support webhook personnalisé (JSON générique)

### ⏰ Tâches Planifiées (Celery)
- [x] Configuration Celery + Redis
- [x] Tâche `check_all_prices` - Vérification quotidienne de tous les produits
- [x] Tâche `check_single_product` - Vérification d'un produit spécifique
- [x] Tâche `check_prices_by_frequency` - Vérification selon la fréquence configurée (6h, 12h, 24h) ✨ **NEW**
- [x] Celery Beat configuré avec 3 schedules (6h, 12h, 24h) ✨ **NEW**
- [x] Envoi automatique d'alertes si prix ≤ seuil
- [x] Enregistrement automatique de l'historique des prix ✨ NEW

### 🗄️ Base de Données & Migrations
- [x] Modèle `User` :
  - id, email, password_hash, created_at
  - is_verified, verification_token ✨ NEW
  - reset_token, reset_token_expires ✨ NEW
- [x] Modèle `Product` :
  - id, user_id, name, url, image, current_price, target_price, last_checked, created_at
  - check_frequency (6, 12, or 24 hours) ✨ **NEW**
- [x] Modèle `PriceHistory` : ✨ NEW
  - id, product_id, price, recorded_at
- [x] Modèle `UserPreferences` : ✨ **NEW**
  - id, user_id, email_notifications, webhook_notifications, webhook_url
  - notification_frequency, price_drop_alerts, weekly_summary, availability_alerts, webhook_type
- [x] Relations One-to-Many (User → Products, Product → PriceHistory)
- [x] Relations One-to-One (User → UserPreferences) ✨ **NEW**
- [x] **Migrations Alembic** configurées et fonctionnelles ✨ NEW
- [x] Scripts d'automatisation (`migrate.sh`, `reset_db.sh`) ✨ NEW

### 📝 Schémas Pydantic
- [x] Schémas utilisateur (UserCreate, UserLogin, UserResponse, Token)
- [x] Schémas produit (ProductCreate, ProductUpdate, ProductResponse)
- [x] Schémas refresh token, reset password, email verification ✨ NEW
- [x] Schémas historique des prix (PriceHistoryResponse, PriceHistoryStats) ✨ NEW
- [x] Schémas préférences utilisateur (UserPreferencesCreate, UserPreferencesUpdate, UserPreferencesResponse) ✨ **NEW**
- [x] Validation des emails et données
- [x] Validation des URLs de webhook avec field_validator ✨ **NEW**

### 🧪 Tests
- [x] Suite de tests d'intégration (4 suites)
  - [x] Tests API de base (`tests/test_api.py`)
  - [x] Tests de sécurité (`tests/test_security.py`)
  - [x] Tests d'historique des prix (`tests/test_price_history.py`)
  - [x] Tests de pagination, filtres et tri (`tests/test_pagination.py`) ✨ NEW
- [x] Suite de tests unitaires (325 tests) ✨ **AMÉLIORÉ**
  - [x] Tests scraper service (17 tests, 79% coverage) ✅
  - [x] Tests email service (14 tests, 95% coverage) ✅
  - [x] Tests price_history service (13 tests, 100% coverage) ✅
  - [x] Tests Celery tasks (11 tests, 100% coverage) ✅
  - [x] Tests error handling (13 tests, retry logic, unavailability detection) ✅
  - [x] Tests security (16 tests, 96% coverage) ✅
  - [x] Tests site detection (24 tests, 100% réussite) ✅
  - [x] Tests nouveaux scrapers (13 tests, Cdiscount/Boulanger/Leclerc) ✅
  - [x] Tests API dependencies (6 tests, 100% coverage) ✅
  - [x] Tests rate limiting (18 tests, 92% coverage) ✅
  - [x] Tests auth endpoints (21 tests, 96% coverage) ✅
  - [x] Tests logging (17 tests, 99% coverage) ✅
  - [x] Tests database (4 tests, 100% coverage) ✅
  - [x] Tests main app (11 tests, 100% coverage) ✅
  - [x] Tests imports (6 tests) ✅
  - [x] Tests user preferences (14 tests, 100% coverage) ✅ **NEW**
  - [x] Tests check frequency (13 tests, 100% coverage) ✅ **NEW**
  - [x] Tests priority calculation (10 tests, 100% coverage) ✅ **NEW**
  - [x] Tests parallel scraping (11 tests, 100% coverage) ✅ **NEW**
  - [x] Tests health endpoints (20 tests, 100% coverage) ✅ **NEW**
  - [x] Tests scraper advanced (41 tests, 100% coverage) ✅ **NEW**
  - **Total: 325 tests unitaires** avec **65% de couverture globale**
- [x] Infrastructure de tests ✨ NEW
  - [x] pytest avec markers (unit, integration, scraper, email, celery) ✨ NEW
  - [x] pytest-cov pour coverage reporting (**60% total**) ✨ **AMÉLIORÉ**
  - [x] pytest-mock pour mocking ✨ NEW
  - [x] Seuil de couverture minimal de 70% appliqué ✨ **NEW**
- [x] Scripts d'exécution des tests ✨ NEW
  - [x] `run_tests.sh` - Tests d'intégration
  - [x] `run_unit_tests.sh` - Tests unitaires avec coverage ✨ NEW
  - [x] `run_all_tests.sh` - Tous les tests ✨ NEW
- [x] Outils de qualité de code ✨ NEW
  - [x] black (formatage automatique) ✨ NEW
  - [x] flake8 (linting) ✨ NEW
  - [x] isort (organisation imports) ✨ NEW
  - [x] mypy (vérification types) ✨ NEW
  - [x] `run_linting.sh` - Script de vérification ✨ NEW

---

## 🚧 Fonctionnalités à Implémenter (par priorité)

### 🎯 Version 1.2 - En cours (Priorité HAUTE)

#### 📱 API Améliorations - ✅ COMPLÉTÉ
- [x] **Pagination** pour les listes de produits ✨ NEW
  - `GET /api/v1/products?page=1&page_size=20`
  - Métadonnées complètes (total_items, total_pages, has_next, has_previous)
  - Améliore les performances pour les utilisateurs avec beaucoup de produits
- [x] **Filtres & tri** (par prix, date d'ajout, nom) ✨ NEW
  - `GET /api/v1/products?sort_by=current_price&order=asc`
  - Tri par: name, current_price, target_price, created_at, last_checked
  - Ordre: asc (ascendant) ou desc (descendant)
  - Facilite la navigation dans les produits
- [x] **Recherche** de produits par nom/URL ✨ NEW
  - `GET /api/v1/products?search=iphone`
  - Recherche insensible à la casse dans le nom et l'URL
  - Améliore l'expérience utilisateur
- [x] **Combinaison de fonctionnalités** ✨ NEW
  - Possibilité de combiner pagination + tri + recherche
  - Ex: `GET /api/v1/products?page=1&page_size=10&search=laptop&sort_by=current_price&order=asc`

#### 🧪 Tests & Qualité - ✅ COMPLÉTÉ
- [x] **Tests unitaires** complets (pytest) pour : ✨ **AMÉLIORÉ**
  - [x] Scraper service (17 tests, 79% coverage) ✨ NEW
  - [x] Email service (14 tests, 95% coverage) ✨ NEW
  - [x] Price history service (13 tests, 100% coverage) ✨ NEW
  - [x] Tâches Celery (11 tests, 100% coverage) ✨ NEW
  - [x] API dependencies (6 tests, 100% coverage) ✨ NEW
  - [x] Rate limiting (18 tests, 92% coverage) ✨ NEW
  - [x] Auth endpoints (21 tests, 96% coverage) ✨ NEW
  - [x] Logging (17 tests, 99% coverage) ✨ NEW
  - [x] Database (4 tests, 100% coverage) ✨ NEW
  - [x] Main app (11 tests, 100% coverage) ✨ NEW
  - [x] Security (16 tests, 96% coverage) ✨ NEW
  - [x] User preferences (14 tests, 100% coverage) ✨ **NEW**
  - [x] Check frequency (13 tests, 100% coverage) ✨ **NEW**
  - [x] Priority calculation (10 tests, 100% coverage) ✨ **NEW**
  - [x] Tests health endpoints (20 tests, 100% coverage) ✅ **NEW**
  - **Total: 284 tests unitaires** avec **62% de couverture globale**
- [x] **Infrastructure de tests** ✨ NEW
  - pytest avec markers (unit, integration, scraper, email, celery)
  - pytest-cov pour coverage tracking avec seuil minimal de 70%
  - pytest-mock pour mocking complet
  - Scripts d'exécution (run_unit_tests.sh, run_all_tests.sh)
- [x] **Linting & formatting** (black, flake8, mypy, isort) ✨ NEW
  - Configuration complète (.flake8, pyproject.toml)
  - Script run_linting.sh pour vérification automatique
  - Assure la qualité et maintenabilité du code

#### 🛡️ Gestion des Erreurs - ✅ COMPLÉTÉ
- [x] **Logging structuré** (rotation des logs, niveaux de log) ✨ NEW
  - Module de logging avec rotation quotidienne (30 jours de rétention)
  - Support des logs JSON structurés pour parsing facile
  - Logs séparés pour erreurs (90 jours de rétention)
  - Configuration via variables d'environnement (LOG_LEVEL, LOG_DIR)
  - Intégré dans scraper, email, tasks Celery et main
- [x] **Retry logic** pour le scraping en cas d'échec temporaire ✨ NEW
  - 3 tentatives maximum par défaut (configurable)
  - Backoff exponentiel (2s, 4s, 6s...)
  - Pas de retry sur erreurs 404/410
  - Logs détaillés de chaque tentative
- [x] **Gestion des produits indisponibles** (out of stock detection) ✨ NEW
  - Détection automatique multi-langues (FR/EN)
  - Support spécifique Amazon, Fnac, Darty
  - Nouveaux champs: is_available, unavailable_since
  - Exception ProductUnavailableError pour gérer l'indisponibilité
  - Marquage automatique dans les tâches Celery

#### 🕷️ Amélioration du Scraping - ✅ PARTIELLEMENT COMPLÉTÉ
- [X] **Support Playwright/Selenium** pour sites JavaScript dynamiques
  - Nécessaire pour certains sites modernes
  - Élargit la compatibilité
- [x] **Détection automatique du site** (pattern matching sur URL) ✨ NEW
  - Classe SiteDetector pour reconnaissance automatique des domaines
  - Support multi-pays pour Amazon (.fr, .com, .de, .co.uk, .es, .it)
  - Pattern matching robuste avec gestion www. et sous-domaines
  - 24 tests unitaires (100% de réussite)
- [x] **Support de nouveaux sites** (Cdiscount, Boulanger, Leclerc) ✨ NEW
  - Scrapers spécifiques pour Cdiscount, Boulanger, E.Leclerc
  - Détection d'indisponibilité pour chaque site
  - Tests unitaires complets (13 tests)
  - Total : 6 sites supportés (Amazon, Fnac, Darty, Cdiscount, Boulanger, Leclerc)

---

### 🎯 Version 1.3 - Moyen terme (Priorité MOYENNE)

#### 📧 Notifications Avancées
- [x] **Préférences de notification par utilisateur** (fréquence, canaux) ✨ **NEW**
  - [x] Modèle `UserPreferences` avec champs de configuration
  - [x] Endpoints CRUD complets (`GET`, `POST`, `PUT`, `DELETE /api/v1/preferences`)
  - [x] Validation des URLs de webhook avec Pydantic
  - [x] Préférences respectées dans l'envoi d'emails (email_notifications, price_drop_alerts)
  - [x] Création automatique de préférences par défaut si inexistantes
  - [x] Tests unitaires complets (14 tests, 100% coverage)
- [x] **Webhooks** pour intégrations externes (Slack, Discord, custom) ✨ **NEW**
  - [x] Support Slack avec format de blocks interactifs
  - [x] Support Discord avec format embed coloré
  - [x] Support webhook personnalisé (JSON générique)
  - [x] Validation de l'URL de webhook (http/https requis)
  - [x] Gestion des erreurs webhook sans bloquer l'envoi d'email
  - [x] Tests unitaires pour les 3 formats de webhook

#### 🔄 Optimisation des Tâches Planifiées
- [x] **Configuration de fréquence par produit** (toutes les 6h, 12h, 24h) ✨ **NEW**
  - Champ `check_frequency` ajouté au modèle Product
  - Validation Pydantic pour valeurs autorisées (6, 12, 24)
  - Tâches Celery distinctes pour chaque fréquence
  - Filtre automatique basé sur `last_checked` pour éviter les vérifications trop fréquentes
  - 13 tests unitaires (100% coverage)
  - Plus de flexibilité pour l'utilisateur
- [x] **Priorité des vérifications** (produits proches du seuil en premier) ✨ **NEW**
  - Fonction `calculate_priority()` basée sur le pourcentage de distance au prix cible
  - Produits à/sous le seuil vérifiés en premier (priorité maximale)
  - Tri automatique des produits par priorité avant vérification
  - 10 tests unitaires (100% coverage)
  - Optimise les vérifications pour détecter rapidement les baisses importantes
- [x] **Parallélisation** du scraping (plusieurs produits en même temps) ✨ **NEW**
  - ThreadPoolExecutor pour scraping concurrent
  - Configuration via `MAX_PARALLEL_SCRAPERS` (5 par défaut) et `SCRAPING_BATCH_SIZE` (10 par défaut)
  - Fonction `scrape_single_product_safe()` thread-safe avec gestion d'erreurs
  - Fonction `scrape_products_parallel()` pour traitement par batch
  - Intégration complète dans `check_prices_by_frequency()`
  - 11 tests unitaires (100% coverage)
  - Améliore significativement les performances pour les vérifications massives

#### 📊 Administration & Analytics - ✅ COMPLÉTÉ
- [x] **Modèle ScrapingStats** pour tracking des performances de scraping ✨ **NEW**
  - Enregistre site_name, status, response_time, error_message
  - Indexes sur site_name et created_at pour requêtes rapides
- [x] **Champ is_admin** dans le modèle User pour gestion des rôles ✨ **NEW**
  - Permission par défaut: False
  - Validation via dependency get_current_admin_user
- [x] **AdminService** complet avec analytics avancées ✨ **NEW**
  - get_global_stats(): Statistiques système (users, products, scraping)
  - get_site_stats(): Statistiques par site (success rate, response time)
  - get_user_stats(): Statistiques utilisateur détaillées
  - log_scraping_stat(): Enregistrement automatique des scrapes
- [x] **Endpoints admin** avec contrôle d'accès basé sur rôles ✨ **NEW**
  - GET /api/v1/admin/stats/global - Statistiques globales
  - GET /api/v1/admin/stats/site/{site_name} - Stats par site
  - GET /api/v1/admin/stats/users - Liste stats tous utilisateurs (pagination)
  - GET /api/v1/admin/stats/users/{user_id} - Stats utilisateur spécifique
  - GET /api/v1/admin/stats/scraping - Stats de scraping récentes
  - POST /api/v1/admin/users/{user_id}/admin - Promouvoir en admin
  - DELETE /api/v1/admin/users/{user_id}/admin - Révoquer rôle admin
  - DELETE /api/v1/admin/users/{user_id} - Supprimer utilisateur
- [x] **Export RGPD** (CSV et JSON) ✨ **NEW**
  - GET /api/v1/admin/export/user/{user_id}/csv - Export CSV
  - GET /api/v1/admin/export/user/{user_id}/json - Export JSON
  - Options: include_products, include_price_history, include_preferences
  - Conformité RGPD complète
- [x] **Protection des endpoints** ✨ **NEW**
  - Tous les endpoints admin requièrent is_admin=True
  - Impossibilité de se révoquer soi-même ou se supprimer
- [x] **Tests unitaires complets** (16 tests, 100% coverage) ✨ **NEW**
  - Tests AdminService (get_stats, export data, log scraping)
  - Tests dependencies (get_current_admin_user)
  - Tests cas d'erreur et edge cases

#### 🔧 DevOps & Déploiement - ✅ COMPLÉTÉ
- [x] **CI/CD pipeline** (GitHub Actions) ✨ **NEW**
  - Tests automatiques sur chaque commit (lint, unit tests, security scan)
  - Build Docker automatisé
  - Tests d'intégration sur main/master
  - Placeholder pour déploiement automatisé
- [x] **Healthchecks avancés** (vérification DB, Redis, Celery) ✨ **NEW**
  - `GET /health/` - Health check basique
  - `GET /health/detailed` - Health check détaillé de tous les composants
  - `GET /health/ready` - Kubernetes readiness probe
  - `GET /health/live` - Kubernetes liveness probe
  - Monitoring de PostgreSQL, Redis et Celery workers
- [x] **Monitoring** (Sentry pour erreurs) ✨ **NEW**
  - Intégration Sentry avec FastAPI, SQLAlchemy, Celery et Redis
  - Performance monitoring avec traces et profiling
  - Configuration via variables d'environnement
- [x] **Docker Compose production** ✨ **NEW**
  - Configuration optimisée avec limites de ressources
  - Nginx reverse proxy avec rate limiting et SSL
  - Réseau Docker isolé pour la sécurité
  - Healthchecks Docker natifs

---

### 🎯 Version 2.0 - Long terme (Priorité BASSE)

#### 🕷️ Scraping Avancé - ✅ COMPLÉTÉ
- [ ] **Gestion des CAPTCHAs** (délégation à service tiers)
- [x] **Proxies rotatifs** pour éviter les blocages IP ✨ **NEW**
  - Classe ProxyRotator pour rotation/sélection aléatoire de proxies
  - Configuration via variable PROXY_LIST (liste séparée par virgules)
  - Support désactivable via SCRAPER_PROXY_ENABLED
  - Tests unitaires complets (10 tests)
- [x] **User-Agent rotation** ✨ **NEW**
  - Pool de 15 User-Agents réalistes (Chrome, Firefox, Safari, Edge)
  - Rotation automatique à chaque requête de scraping
  - Headers complets ou minimaux selon les besoins
  - Tests unitaires complets (5 tests)
- [x] **Cache des résultats de scraping** (éviter rescraper trop souvent) ✨ **NEW**
  - Cache Redis avec TTL configurable (défaut: 1 heure)
  - Clés de cache basées sur hash MD5 des URLs
  - Méthodes: get, set, invalidate, clear_all
  - Bypass cache disponible pour forcer un scraping frais
  - Tests unitaires complets (11 tests)
- [x] **Circuit breaker** pour éviter de surcharger les sites ✨ **NEW**
  - Implémentation du pattern Circuit Breaker (CLOSED, OPEN, HALF_OPEN)
  - États stockés dans Redis pour distribution
  - Configuration: seuil d'échecs (5), timeout de récupération (60s)
  - Gestion automatique par site (amazon, fnac, darty, etc.)
  - Tests unitaires complets (12 tests)

#### Notifications par mail (préférences utilisateur)
- [ ] **Notifications par mail** (email récapitulatif des baisses de prix)
  - Tâche Celery hebdomadaire
  - Tâche Celery quotidienne
  - Tâche Celery instantanée

#### 🔎 Fonctionnalités Avancées
- [ ] **Comparaison de prix** entre plusieurs sites pour un même produit
- [ ] **Alertes de disponibilité** (produit de nouveau en stock)
- [ ] **Prédiction de prix** (ML pour anticiper les baisses)
- [ ] **Partage de listes** (wishlists publiques/privées)
- [ ] **Import de liste de souhaits** depuis Amazon
- [ ] **Extension navigateur** pour ajout rapide

#### 🌍 Internationalisation
- [ ] **Support multi-devises** (EUR, USD, GBP)
- [ ] **Détection automatique de la devise** depuis l'URL
- [ ] **Conversion de devises** (API taux de change)
- [ ] **Support multi-langues** pour emails/notifications

#### 🚀 Production & Scale
- [ ] **Variables d'environnement sécurisées** (secrets management)
- [ ] **Backup automatique** de la base de données
- [ ] **Déploiement production** (AWS, GCP, DigitalOcean)
- [ ] **Load balancing** pour haute disponibilité
- [ ] **Versioning API** (v2, v3...)

#### 💳 Monétisation & Plans
- [ ] **Modèle `Subscription`** (plan, statut, date d'expiration)
- [ ] **Limitation par plan** :
  - Free : 5 produits, vérif quotidienne
  - Pro : 50 produits, vérif toutes les 6h
  - Business : 500 produits, vérif personnalisée
- [ ] **Intégration Stripe** pour paiements
- [ ] **Webhook Stripe** pour mise à jour automatique du statut
- [ ] **Rate limiting par utilisateur** selon le plan

---

## 🐛 Bugs Connus & Points d'Attention

### Bugs Critiques
- [ ] **Pas de limite sur le nombre de produits par utilisateur** (risque d'abus en Free)
- [ ] **Celery Beat ne persiste pas l'état** (redémarrage = perte du schedule)

### Bugs Importants
- [ ] **Pas de validation de l'URL** lors de l'ajout (peut être une URL invalide)
- [x] **Pas de gestion des produits supprimés/indisponibles** sur le site marchand ✅ CORRIGÉ
- [ ] **Emails pas testés en production** (configuration SMTP à valider)

### Améliorations Techniques
- [ ] **Gestion des sites qui changent leur structure HTML** (scraping fragile)
- [ ] Le scraping est synchrone (bloquant) → envisager async avec `httpx` ou `aiohttp`
- [ ] Pas de cache actuellement → envisager Redis pour cache des scraped data
- [x] Logs pas structurés → implémenter logging.config ✅ CORRIGÉ

---

## 📝 Notes Techniques

### Dépendances actuelles
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- Celery 5.3.6 + Redis 5.0.1
- BeautifulSoup4 4.12.3
- Python-jose (JWT)
- Bcrypt (hachage)
- Alembic (migrations)

### Architecture
- Backend FastAPI avec architecture MVC
- Base de données PostgreSQL avec ORM SQLAlchemy
- Redis pour Celery et rate limiting
- Celery Beat pour tâches planifiées
- Docker pour conteneurisation

---

## 📚 Documentation & Scripts

### Fichiers de documentation
- **[RoadMap.md](RoadMap.md)** - Ce fichier : Vue d'ensemble et roadmap
- **[SECURITY_FEATURES.md](SECURITY_FEATURES.md)** - Documentation sécurité
- **[ADMIN_FEATURES.md](ADMIN_FEATURES.md)** - Documentation administration et analytics
- **[DEVOPS.md](DEVOPS.md)** - Documentation DevOps, CI/CD et déploiement ✨ **NEW**
- **[SCRAPING_ADVANCED.md](SCRAPING_ADVANCED.md)** - Documentation des fonctionnalités avancées de scraping ✨ **NEW**

### Scripts utiles
- **[migrate.sh](../migrate.sh)** - Génération et application de migrations Alembic
- **[reset_db.sh](../reset_db.sh)** - Réinitialisation de la base de données (vide les tables)
- **[run_tests.sh](../run_tests.sh)** - Exécution de tous les tests (intégration)
- **[run_unit_tests.sh](../run_unit_tests.sh)** - Exécution des tests unitaires avec coverage ✨ NEW
- **[run_all_tests.sh](../run_all_tests.sh)** - Exécution de tous les tests (unitaires + intégration) ✨ NEW
- **[run_linting.sh](../run_linting.sh)** - Vérification de la qualité du code (black, flake8, isort, mypy) ✨ NEW

### Tests disponibles

#### Tests d'intégration
- **[tests/test_api.py](../tests/test_api.py)** - Tests API de base
- **[tests/test_security.py](../tests/test_security.py)** - Tests des fonctionnalités de sécurité
- **[tests/test_price_history.py](../tests/test_price_history.py)** - Tests de l'historique des prix
- **[tests/test_pagination.py](../tests/test_pagination.py)** - Tests de pagination, filtres et tri

#### Tests unitaires ✨ **AMÉLIORÉ**
- **[tests/test_unit_scraper.py](../tests/test_unit_scraper.py)** - Tests du service de scraping (17 tests, 79% coverage)
- **[tests/test_unit_email.py](../tests/test_unit_email.py)** - Tests du service email (14 tests, 95% coverage)
- **[tests/test_unit_price_history.py](../tests/test_unit_price_history.py)** - Tests du service price_history (13 tests, 100% coverage)
- **[tests/test_unit_celery_tasks.py](../tests/test_unit_celery_tasks.py)** - Tests des tâches Celery (10 tests, 100% coverage)
- **[tests/test_unit_error_handling.py](../tests/test_unit_error_handling.py)** - Tests de gestion d'erreurs (13 tests)
- **[tests/test_unit_security.py](../tests/test_unit_security.py)** - Tests de sécurité (16 tests, 96% coverage)
- **[tests/test_unit_site_detection.py](../tests/test_unit_site_detection.py)** - Tests de détection de sites (24 tests, 100% réussite)
- **[tests/test_unit_new_scrapers.py](../tests/test_unit_new_scrapers.py)** - Tests nouveaux scrapers (13 tests)
- **[tests/test_unit_dependencies.py](../tests/test_unit_dependencies.py)** - Tests API dependencies (6 tests, 100% coverage)
- **[tests/test_unit_rate_limit.py](../tests/test_unit_rate_limit.py)** - Tests rate limiting (18 tests, 92% coverage)
- **[tests/test_unit_auth_endpoints.py](../tests/test_unit_auth_endpoints.py)** - Tests auth endpoints (21 tests, 96% coverage)
- **[tests/test_unit_logging.py](../tests/test_unit_logging.py)** - Tests logging (17 tests, 99% coverage)
- **[tests/test_unit_db.py](../tests/test_unit_db.py)** - Tests database (4 tests, 100% coverage)
- **[tests/test_unit_main.py](../tests/test_unit_main.py)** - Tests main app (11 tests, 100% coverage)
- **[tests/test_unit_imports.py](../tests/test_unit_imports.py)** - Tests imports (6 tests)
- **[tests/test_unit_preferences.py](../tests/test_unit_preferences.py)** - Tests user preferences (14 tests, 100% coverage) ✨ **NEW**
- **[tests/test_unit_check_frequency.py](../tests/test_unit_check_frequency.py)** - Tests check frequency (13 tests, 100% coverage) ✨ **NEW**
- **[tests/test_unit_priority.py](../tests/test_unit_priority.py)** - Tests priority calculation (10 tests, 100% coverage) ✨ **NEW**
- **[tests/test_unit_health.py](../tests/test_unit_health.py)** - Tests health endpoints (20 tests, 100% coverage) ✨ **NEW**
- **[tests/test_unit_scraper_advanced.py](../tests/test_unit_scraper_advanced.py)** - Tests scraping avancé (41 tests, 100% coverage) ✨ **NEW**

**Total : 325 tests unitaires avec 65% de couverture globale**

### Lancer les tests

```bash
cd Backend

# Tous les tests (unitaires + intégration)
./run_all_tests.sh

# Tests unitaires avec coverage
./run_unit_tests.sh

# Tests d'intégration uniquement
./run_tests.sh

# Tests spécifiques d'intégration
python3 tests/test_security.py
python3 tests/test_price_history.py
python3 tests/test_pagination.py

# Tests unitaires via Docker (recommandé)
docker-compose exec backend python3 -m pytest tests/ -v --cov=app -m unit

# Vérification de la qualité du code
./run_linting.sh
```

### Configuration des tests
- **[pytest.ini](../pytest.ini)** - Configuration pytest avec markers et coverage
- **[.flake8](../.flake8)** - Configuration flake8 pour linting
- **[pyproject.toml](../pyproject.toml)** - Configuration black, isort et mypy

### Utiliser l'API avec pagination et filtres

```bash
# Liste paginée (page 1, 20 items par page)
GET /api/v1/products?page=1&page_size=20

# Recherche par nom ou URL
GET /api/v1/products?search=iphone

# Tri par prix (ascendant)
GET /api/v1/products?sort_by=current_price&order=asc

# Tri par nom (descendant)
GET /api/v1/products?sort_by=name&order=desc

# Combinaison: recherche + tri + pagination
GET /api/v1/products?search=laptop&sort_by=current_price&order=asc&page=1&page_size=10

# Réponse exemple:
{
  "items": [
    {
      "id": 1,
      "name": "Product Name",
      "current_price": 199.99,
      ...
    }
  ],
  "metadata": {
    "page": 1,
    "page_size": 20,
    "total_items": 45,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
  }
}
```

### Utiliser les migrations

```bash
cd Backend

# Créer et appliquer une migration
./migrate.sh "Description de la migration"

# Vérifier l'état actuel
docker-compose exec backend alembic current

# Réinitialiser la DB (vider toutes les données)
./reset_db.sh
```

---

**Dernière mise à jour** : 2025-12-23
