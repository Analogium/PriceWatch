# 🚀 DevOps & Déploiement - PriceWatch

Ce document décrit l'infrastructure DevOps mise en place pour PriceWatch, incluant le CI/CD, le monitoring et le déploiement en production.

---

## 📋 Vue d'ensemble

L'infrastructure DevOps comprend :
- **CI/CD Pipeline** : GitHub Actions pour tests automatiques et déploiement
- **Healthchecks Avancés** : Monitoring de tous les composants (DB, Redis, Celery)
- **Monitoring des Erreurs** : Intégration Sentry pour la détection des erreurs
- **Configuration Production** : Docker Compose optimisé pour la production

---

## 🔄 CI/CD Pipeline (GitHub Actions)

### Fichier de configuration
`.github/workflows/ci.yml`

### Jobs exécutés

1. **Lint** (Code Quality)
   - Black (formatage)
   - isort (imports)
   - flake8 (linting)
   - mypy (type checking)

2. **Test** (Unit Tests)
   - Exécute tous les tests unitaires
   - Génère un rapport de couverture
   - Upload vers Codecov

3. **Docker Build**
   - Construit l'image Docker
   - Utilise le cache GitHub Actions

4. **Security Scan**
   - Safety (vulnérabilités des dépendances)
   - Bandit (analyse de sécurité du code)

5. **Integration Test** (main/master uniquement)
   - Lance Docker Compose
   - Exécute les tests d'intégration

6. **Deploy** (main/master uniquement)
   - Placeholder pour déploiement automatisé

### Déclencheurs
- Push sur `main`, `master`, `develop`
- Pull requests vers ces branches

### Variables d'environnement
```yaml
DATABASE_URL: postgresql://pricewatch:pricewatch@localhost:5432/pricewatch_test
REDIS_URL: redis://localhost:6379/0
SECRET_KEY: test-secret-key-for-ci-pipeline-only
```

---

## 🏥 Healthchecks Avancés

### Endpoints disponibles

| Endpoint | Description | Usage |
|----------|-------------|-------|
| `GET /health/` | Health check basique | Vérification rapide API |
| `GET /health/detailed` | Health check détaillé | Monitoring complet |
| `GET /health/ready` | Readiness probe (K8s) | Kubernetes readiness |
| `GET /health/live` | Liveness probe (K8s) | Kubernetes liveness |

### Composants vérifiés

#### Base de données PostgreSQL
- Connectivité (SELECT 1)
- Version PostgreSQL
- Nombre de tables

#### Redis
- Ping
- Version Redis
- Clients connectés
- Mémoire utilisée
- Uptime

#### Celery Workers
- Workers actifs
- Tâches enregistrées
- Tâches planifiées (Beat schedule)

### Exemple de réponse `/health/detailed`
```json
{
  "status": "healthy",
  "timestamp": "2025-11-20T10:30:00.000000",
  "service": "pricewatch-api",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "version": "PostgreSQL 15.0",
      "tables": 5
    },
    "redis": {
      "status": "healthy",
      "version": "7.0.0",
      "connected_clients": 3,
      "used_memory_human": "2.5M",
      "uptime_in_seconds": 86400
    },
    "celery": {
      "status": "healthy",
      "workers": 2,
      "active_workers": ["worker1@host", "worker2@host"],
      "registered_tasks": 3,
      "scheduled_tasks": ["check-prices-6h", "check-prices-12h", "check-prices-24h"]
    }
  }
}
```

### Statuts possibles
- `healthy` : Tous les composants fonctionnent
- `degraded` : Un ou plusieurs composants défaillants
- `unhealthy` : Composant individuel défaillant

---

## 📊 Monitoring avec Sentry

### Configuration

1. **Variables d'environnement requises**
   ```bash
   SENTRY_DSN=https://your-key@sentry.io/project-id
   SENTRY_ENVIRONMENT=production  # ou staging, development
   SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% des transactions
   SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% des profils
   ```

2. **Intégrations activées**
   - FastAPI (transactions automatiques)
   - SQLAlchemy (queries DB)
   - Celery (tâches background)
   - Redis (opérations cache)

### Fonctionnalités
- Capture automatique des exceptions
- Performance monitoring (traces)
- Profiling des requêtes
- Alertes en temps réel
- Breadcrumbs pour le debugging

### Bonnes pratiques
- Ne jamais envoyer de PII (`send_default_pii=False`)
- Utiliser des environnements séparés (dev, staging, prod)
- Configurer des alertes appropriées dans Sentry

---

## 🐳 Docker Compose Production

### Fichier
`docker-compose.prod.yml`

### Caractéristiques

#### Sécurité
- Pas d'exposition de ports pour DB et Redis
- Réseau Docker isolé
- Mots de passe via variables d'environnement

#### Performance
- Workers Uvicorn : 4 (backend)
- Workers Celery : 4 (concurrency)
- Limites de ressources CPU/RAM configurées

#### Résilience
- `restart: always` sur tous les services
- Healthchecks Docker natifs
- Dépendances avec conditions

#### Nginx Reverse Proxy
- Gzip compression
- Rate limiting (100 req/min)
- Headers de sécurité
- Support SSL/TLS (à configurer)

### Démarrage en production

```bash
# Copier et configurer l'environnement
cp Backend/.env.production.example Backend/.env.production
# Éditer Backend/.env.production avec vos valeurs

# Variables Docker Compose
export POSTGRES_PASSWORD=your_secure_password
export REDIS_PASSWORD=your_redis_password

# Démarrer les services
docker-compose -f docker-compose.prod.yml up -d

# Vérifier le statut
docker-compose -f docker-compose.prod.yml ps

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Ressources allouées

| Service | CPU Limit | Memory Limit |
|---------|-----------|--------------|
| Backend | 1 CPU | 1 GB |
| Celery Worker | 0.5 CPU | 512 MB |
| Celery Beat | 0.25 CPU | 256 MB |
| Nginx | 0.25 CPU | 128 MB |

---

## 🔧 Configuration Production

### Fichier `.env.production`

Copier depuis `.env.production.example` et configurer :

```bash
# Sécurité
SECRET_KEY=<générer avec: python -c "import secrets; print(secrets.token_urlsafe(64))">

# Base de données
POSTGRES_PASSWORD=<mot de passe fort>
DATABASE_URL=postgresql://pricewatch:${POSTGRES_PASSWORD}@db:5432/pricewatch

# Redis
REDIS_PASSWORD=<mot de passe fort>
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# Email
SMTP_HOST=<votre serveur SMTP>
SMTP_PASSWORD=<mot de passe SMTP>

# Sentry
SENTRY_DSN=<DSN depuis sentry.io>
SENTRY_ENVIRONMENT=production
```

---

## 🌐 Nginx Configuration

### Fichier
`nginx/nginx.conf`

### Fonctionnalités
- Reverse proxy vers le backend FastAPI
- Rate limiting : 100 req/min par IP
- Gzip compression pour JSON
- Headers de sécurité (XSS, Frame, Content-Type)
- Health check passthrough sans rate limiting

### SSL/TLS (à configurer)
1. Obtenir un certificat (Let's Encrypt recommandé)
2. Placer dans `nginx/ssl/`
3. Décommenter la configuration HTTPS

---

## 📈 Métriques et Alertes

### Métriques recommandées à monitorer

1. **Infrastructure**
   - CPU/RAM usage
   - Disk I/O
   - Network traffic

2. **Application**
   - Request latency (p50, p95, p99)
   - Error rate
   - Requests per second

3. **Base de données**
   - Connection pool usage
   - Query latency
   - Active transactions

4. **Redis**
   - Memory usage
   - Connected clients
   - Commands per second

5. **Celery**
   - Queue length
   - Task execution time
   - Failed tasks

### Alertes suggérées

| Métrique | Seuil Warning | Seuil Critical |
|----------|--------------|----------------|
| CPU Usage | > 70% | > 90% |
| Memory Usage | > 80% | > 95% |
| Error Rate | > 1% | > 5% |
| Response Time (p95) | > 500ms | > 2000ms |
| Celery Queue | > 100 tasks | > 500 tasks |

---

## 🔒 Checklist Sécurité Production

- [ ] Changer tous les mots de passe par défaut
- [ ] Générer une nouvelle `SECRET_KEY`
- [ ] Configurer SSL/TLS
- [ ] Restreindre les CORS origins
- [ ] Activer le rate limiting
- [ ] Configurer les backups de la base de données
- [ ] Mettre en place le monitoring Sentry
- [ ] Configurer les alertes
- [ ] Tester les healthchecks
- [ ] Documenter la procédure de rollback

---

## 📝 Scripts utiles

### Vérification rapide de santé
```bash
curl http://localhost:8000/health/detailed | jq
```

### Voir les logs des erreurs
```bash
docker-compose -f docker-compose.prod.yml logs --tail=100 backend | grep ERROR
```

### Restart gracieux
```bash
docker-compose -f docker-compose.prod.yml restart backend celery_worker
```

### Backup de la base de données
```bash
docker-compose -f docker-compose.prod.yml exec db \
  pg_dump -U pricewatch pricewatch > backup_$(date +%Y%m%d).sql
```

---

## 🚀 Prochaines améliorations

- [ ] Kubernetes manifests (Helm charts)
- [ ] Terraform pour infrastructure as code
- [ ] Prometheus + Grafana pour métriques détaillées
- [ ] ELK Stack pour log aggregation
- [ ] Vault pour secrets management
- [ ] Blue-Green deployment
- [ ] Auto-scaling basé sur les métriques

---

**Dernière mise à jour** : 2025-11-20
