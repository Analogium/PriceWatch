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

### 📊 Historique des Prix
- [x] **Modèle `PriceHistory`** pour stocker l'évolution des prix
  - id, product_id, price, recorded_at
- [x] **Endpoint** `GET /api/v1/products/{id}/history` - Récupérer l'historique avec limite configurable ✨ NEW
- [x] **Endpoint** `GET /api/v1/products/{id}/history/stats` - Statistiques de prix (min, max, moyenne, changement %) ✨ NEW
- [x] Enregistrement automatique des prix à chaque vérification (produits et tâches Celery) ✨ NEW
- [x] Évite les duplications (n'enregistre que si le prix a changé) ✨ NEW

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
- [x] Email de vérification d'inscription ✨ NEW
- [x] Email de réinitialisation de mot de passe ✨ NEW

### ⏰ Tâches Planifiées (Celery)
- [x] Configuration Celery + Redis
- [x] Tâche `check_all_prices` - Vérification quotidienne de tous les produits
- [x] Tâche `check_single_product` - Vérification d'un produit spécifique
- [x] Celery Beat configuré (exécution toutes les 24h)
- [x] Envoi automatique d'alertes si prix ≤ seuil
- [x] Enregistrement automatique de l'historique des prix ✨ NEW

### 🗄️ Base de Données & Migrations
- [x] Modèle `User` :
  - id, email, password_hash, created_at
  - is_verified, verification_token ✨ NEW
  - reset_token, reset_token_expires ✨ NEW
- [x] Modèle `Product` :
  - id, user_id, name, url, image, current_price, target_price, last_checked, created_at
- [x] Modèle `PriceHistory` : ✨ NEW
  - id, product_id, price, recorded_at
- [x] Relations One-to-Many (User → Products, Product → PriceHistory)
- [x] **Migrations Alembic** configurées et fonctionnelles ✨ NEW
- [x] Scripts d'automatisation (`migrate.sh`, `reset_db.sh`) ✨ NEW

### 📝 Schémas Pydantic
- [x] Schémas utilisateur (UserCreate, UserLogin, UserResponse, Token)
- [x] Schémas produit (ProductCreate, ProductUpdate, ProductResponse)
- [x] Schémas refresh token, reset password, email verification ✨ NEW
- [x] Schémas historique des prix (PriceHistoryResponse, PriceHistoryStats) ✨ NEW
- [x] Validation des emails et données

### 🧪 Tests
- [x] Suite de tests de sécurité (`tests/test_security.py`)
- [x] Suite de tests d'historique des prix (`tests/test_price_history.py`)
- [x] Suite de tests de pagination, filtres et tri (`tests/test_pagination.py`) ✨ NEW
- [x] Tests API de base (`tests/test_api.py`)
- [x] Script d'exécution des tests (`run_tests.sh`)

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

#### 🧪 Tests & Qualité - PRIORITÉ HAUTE
- [ ] **Tests unitaires** complets (pytest) pour :
  - Services (scraper, email, price_history)
  - Tâches Celery
  - Endpoints API complets
- [ ] **Coverage minimum** de 80%
- [ ] **Linting & formatting** (black, flake8, mypy)
  - Assure la qualité du code
  - Facilite la maintenance

#### 🛡️ Gestion des Erreurs - PRIORITÉ HAUTE
- [ ] **Logging structuré** (rotation des logs, niveaux de log)
  - Facilite le débogage en production
  - Permet le monitoring
- [ ] **Retry logic** pour le scraping en cas d'échec temporaire
  - Améliore la fiabilité du système
  - Évite les faux négatifs
- [ ] **Gestion des produits indisponibles** (out of stock detection)
  - Informe l'utilisateur si un produit n'existe plus

#### 🕷️ Amélioration du Scraping - PRIORITÉ MOYENNE
- [ ] **Support Playwright/Selenium** pour sites JavaScript dynamiques
  - Nécessaire pour certains sites modernes
  - Élargit la compatibilité
- [ ] **Détection automatique du site** (pattern matching sur URL)
  - Simplifie l'ajout de produits
- [ ] **Support de nouveaux sites** (Cdiscount, Boulanger, Leclerc, etc.)
  - Élargit la couverture

---

### 🎯 Version 1.3 - Moyen terme (Priorité MOYENNE)

#### 📧 Notifications Avancées
- [ ] **Préférences de notification par utilisateur** (fréquence, canaux)
  - Modèle UserPreferences
  - Endpoint de configuration
- [ ] **Résumé hebdomadaire** (email récapitulatif des baisses de prix)
  - Tâche Celery hebdomadaire
- [ ] **Webhooks** pour intégrations externes (Slack, Discord)
  - Permet l'intégration avec d'autres outils

#### 🔄 Optimisation des Tâches Planifiées
- [ ] **Configuration de fréquence par produit** (toutes les 6h, 12h, 24h)
  - Ajoute un champ `check_frequency` au modèle Product
  - Plus de flexibilité pour l'utilisateur
- [ ] **Priorité des vérifications** (produits proches du seuil en premier)
  - Optimise les vérifications les plus importantes
- [ ] **Parallelisation** du scraping (plusieurs produits en même temps)
  - Améliore les performances

#### 📊 Administration & Analytics
- [ ] **Endpoint admin** pour statistiques globales
  - Nombre d'utilisateurs, produits, taux de succès scraping
- [ ] **Dashboard admin** basique
  - Interface de monitoring
- [ ] **Export CSV** des données utilisateur (RGPD)
  - Conformité légale

#### 🔧 DevOps & Déploiement
- [ ] **CI/CD pipeline** (GitHub Actions / GitLab CI)
  - Tests automatiques sur chaque commit
  - Déploiement automatisé
- [ ] **Healthchecks avancés** (vérification DB, Redis, Celery)
  - Monitoring de tous les composants
- [ ] **Monitoring** (Sentry pour erreurs)
  - Détection rapide des problèmes en production

---

### 🎯 Version 2.0 - Long terme (Priorité BASSE)

#### 💳 Monétisation & Plans
- [ ] **Modèle `Subscription`** (plan, statut, date d'expiration)
- [ ] **Limitation par plan** :
  - Free : 5 produits, vérif quotidienne
  - Pro : 50 produits, vérif toutes les 6h
  - Business : 500 produits, vérif personnalisée
- [ ] **Intégration Stripe** pour paiements
- [ ] **Webhook Stripe** pour mise à jour automatique du statut
- [ ] **Rate limiting par utilisateur** selon le plan

#### 🕷️ Scraping Avancé
- [ ] **Gestion des CAPTCHAs** (délégation à service tiers)
- [ ] **Proxies rotatifs** pour éviter les blocages IP
- [ ] **User-Agent rotation**
- [ ] **Cache des résultats de scraping** (éviter rescraper trop souvent)
- [ ] **Circuit breaker** pour éviter de surcharger les sites

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

---

## 🐛 Bugs Connus & Points d'Attention

### Bugs Critiques
- [ ] **Pas de limite sur le nombre de produits par utilisateur** (risque d'abus en Free)
- [ ] **Celery Beat ne persiste pas l'état** (redémarrage = perte du schedule)

### Bugs Importants
- [ ] **Pas de validation de l'URL** lors de l'ajout (peut être une URL invalide)
- [ ] **Pas de gestion des produits supprimés/indisponibles** sur le site marchand
- [ ] **Emails pas testés en production** (configuration SMTP à valider)

### Améliorations Techniques
- [ ] **Gestion des sites qui changent leur structure HTML** (scraping fragile)
- [ ] Le scraping est synchrone (bloquant) → envisager async avec `httpx` ou `aiohttp`
- [ ] Pas de cache actuellement → envisager Redis pour cache des scraped data
- [ ] Logs pas structurés → implémenter logging.config

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

### Scripts utiles
- **[migrate.sh](../migrate.sh)** - Génération et application de migrations Alembic
- **[reset_db.sh](../reset_db.sh)** - Réinitialisation de la base de données (vide les tables)
- **[run_tests.sh](../run_tests.sh)** - Exécution de tous les tests

### Tests disponibles
- **[tests/test_security.py](../tests/test_security.py)** - Tests des fonctionnalités de sécurité
- **[tests/test_price_history.py](../tests/test_price_history.py)** - Tests de l'historique des prix
- **[tests/test_pagination.py](../tests/test_pagination.py)** - Tests de pagination, filtres et tri
- **[tests/test_api.py](../tests/test_api.py)** - Tests API de base

### Lancer les tests

```bash
cd Backend

# Tous les tests
./run_tests.sh

# Tests spécifiques
python3 tests/test_security.py
python3 tests/test_price_history.py
python3 tests/test_pagination.py
```

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

**Dernière mise à jour** : 10/11/2025
