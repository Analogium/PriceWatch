# 🏷️ PriceWatch — Backend API

Application de surveillance de prix en ligne avec notifications automatiques.

## 📋 Prérequis

- Python 3.12+
- Docker & Docker Compose (recommandé)
- PostgreSQL (si lancement en local sans Docker)
- Redis (si lancement en local sans Docker)

## 🚀 Démarrage rapide avec Docker

### 1. Configuration de l'environnement

```bash
# Copier le fichier d'exemple
cd Backend
cp .env.example .env

# Éditer le fichier .env avec vos configurations
# Notamment les paramètres SMTP pour l'envoi d'emails
```

### 2. Générer une clé secrète

```bash
# Générer une clé secrète pour JWT
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copier la clé générée dans .env → SECRET_KEY
```

### 3. Lancer l'application avec Docker

```bash
# Retourner à la racine du projet
cd ..

# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f backend
```

### 4. Accéder à l'API

- **API**: http://localhost:8000
- **Documentation interactive (Swagger)**: http://localhost:8000/docs
- **Documentation alternative (ReDoc)**: http://localhost:8000/redoc

## 🛠️ Démarrage en local (sans Docker)

### 1. Installer les dépendances

```bash
cd Backend
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurer la base de données

**Option A: SQLite (pour développement rapide)**

Modifier dans `.env`:
```env
DATABASE_URL=sqlite:///./pricewatch.db
```

**Option B: PostgreSQL (recommandé pour production)**

```bash
# Installer et démarrer PostgreSQL
# Créer la base de données
createdb pricewatch

# Utiliser dans .env:
DATABASE_URL=postgresql://user:password@localhost:5432/pricewatch
```

### 3. Lancer le serveur

```bash
# Avec le script fourni
./run_local.sh

# Ou manuellement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Tester l'API

### Avec le script de test Python

```bash
# Assurez-vous que le serveur est lancé
python test_api.py
```

### Avec cURL

```bash
# Health check
curl http://localhost:8000/health

# Créer un utilisateur
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Se connecter
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Utiliser le token reçu
TOKEN="votre_token_ici"

# Ajouter un produit à surveiller
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"url":"https://www.amazon.fr/dp/B0EXAMPLE","target_price":199.99}'

# Voir tous les produits suivis
curl http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN"
```

## 📚 Structure du projet

```
Backend/
├── app/
│   ├── api/
│   │   ├── dependencies.py      # Dépendances (auth, db)
│   │   └── endpoints/
│   │       ├── auth.py          # Routes d'authentification
│   │       └── products.py      # Routes des produits
│   ├── core/
│   │   ├── config.py            # Configuration
│   │   └── security.py          # JWT, hash passwords
│   ├── db/
│   │   └── base.py              # Configuration SQLAlchemy
│   ├── models/
│   │   ├── user.py              # Modèle User
│   │   └── product.py           # Modèle Product
│   ├── schemas/
│   │   ├── user.py              # Schémas Pydantic User
│   │   └── product.py           # Schémas Pydantic Product
│   ├── services/
│   │   ├── scraper.py           # Service de scraping
│   │   └── email.py             # Service d'envoi d'emails
│   └── main.py                  # Point d'entrée FastAPI
├── tasks.py                     # Tâches Celery (vérification prix)
├── requirements.txt             # Dépendances Python
├── Dockerfile                   # Image Docker
└── .env                         # Variables d'environnement
```

## 🔐 Endpoints API

### Authentification

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/v1/auth/register` | Créer un compte |
| `POST` | `/api/v1/auth/login` | Se connecter (renvoie JWT) |
| `GET` | `/api/v1/auth/me` | Infos utilisateur actuel |

### Produits

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/v1/products` | Liste des produits suivis |
| `POST` | `/api/v1/products` | Ajouter un produit |
| `GET` | `/api/v1/products/{id}` | Détails d'un produit |
| `PUT` | `/api/v1/products/{id}` | Modifier un produit |
| `DELETE` | `/api/v1/products/{id}` | Supprimer un produit |
| `POST` | `/api/v1/products/{id}/check` | Vérifier le prix manuellement |

## ⚙️ Configuration des emails

Pour recevoir les alertes de baisse de prix, configurez vos paramètres SMTP dans `.env`:

### Avec Gmail

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre.email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application
EMAIL_FROM=noreply@pricewatch.com
```

> **Note**: Pour Gmail, vous devez créer un "mot de passe d'application" dans les paramètres de sécurité de votre compte Google.

### Avec SendGrid (recommandé pour production)

```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=votre_api_key_sendgrid
EMAIL_FROM=noreply@pricewatch.com
```

## 🔄 Tâches planifiées (Celery)

Le système utilise Celery pour vérifier automatiquement les prix:

```bash
# Lancer le worker Celery (si non lancé par Docker)
celery -A tasks worker --loglevel=info

# Lancer le scheduler (Celery Beat)
celery -A tasks beat --loglevel=info
```

**Fréquence par défaut**: Vérification quotidienne (toutes les 24h)

Pour modifier la fréquence, éditez `tasks.py`:

```python
celery_app.conf.beat_schedule = {
    'check-prices-daily': {
        'task': 'check_all_prices',
        'schedule': 21600.0,  # Toutes les 6 heures
    },
}
```

## 🐛 Dépannage

### Problème: Base de données non accessible

```bash
# Vérifier que PostgreSQL est lancé
docker-compose ps

# Voir les logs de la base
docker-compose logs db
```

### Problème: Scraping ne fonctionne pas

Les sites e-commerce peuvent bloquer les scrapers. Solutions:

1. Utilisez un délai entre les requêtes
2. Ajoutez plus de headers dans `services/scraper.py`
3. Utilisez Playwright pour les sites dynamiques

### Problème: Emails non envoyés

```bash
# Vérifier la configuration SMTP dans .env
# Tester l'envoi manuel:
python -c "from app.services.email import email_service; email_service.send_price_alert('test@example.com', 'Test Product', 99.99, 149.99, 'https://example.com')"
```

## 🔧 Commandes Docker utiles

```bash
# Arrêter tous les services
docker-compose down

# Reconstruire les images
docker-compose build

# Voir les logs
docker-compose logs -f backend

# Accéder au shell du backend
docker-compose exec backend bash

# Réinitialiser la base de données
docker-compose down -v  # ATTENTION: supprime les données
docker-compose up -d
```

## 📝 Prochaines étapes

1. ✅ Backend API fonctionnel
2. 🔄 Frontend React (à venir)
3. 🔄 Tests unitaires avec pytest
4. 🔄 Déploiement (Railway, Render, etc.)
5. 🔄 Système de plans (Free, Pro, Business)

## 📞 Support

Pour toute question ou problème, consultez la documentation complète dans [PriceWatch.md](PriceWatch.md)

---

**PriceWatch** : *surveillez les prix, pas vos onglets.* 🏷️
