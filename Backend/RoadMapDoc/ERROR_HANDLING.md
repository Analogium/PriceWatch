# 🛡️ Gestion des Erreurs - Documentation

Cette documentation décrit les fonctionnalités de gestion des erreurs implémentées dans PriceWatch pour améliorer la fiabilité et le monitoring du système.

## 📊 Vue d'ensemble

Les trois principales fonctionnalités implémentées sont :
1. **Logging structuré** avec rotation de fichiers
2. **Retry logic** pour le scraping avec backoff exponentiel
3. **Détection de produits indisponibles** (out of stock)

---

## 📝 Logging Structuré

### Description

Système de logging professionnel avec support de rotation de fichiers, niveaux de log configurables et format JSON optionnel.

### Fichiers impliqués

- `app/core/logging_config.py` - Configuration du logging
- `app/core/config.py` - Variables d'environnement

### Configuration

Variables d'environnement (`.env`) :

```env
# Logging Configuration
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR=./logs                    # Répertoire des logs
ENABLE_JSON_LOGS=false           # Format JSON pour parsing automatique
ENABLE_LOG_ROTATION=true         # Rotation quotidienne des logs
```

### Fonctionnalités

#### Rotation des logs
- **Rotation quotidienne** à minuit
- **Rétention** : 30 jours pour les logs généraux, 90 jours pour les erreurs
- **Fichiers séparés** :
  - `pricewatch.log` - Tous les logs (DEBUG et plus)
  - `pricewatch_errors.log` - Erreurs uniquement (ERROR et CRITICAL)

#### Format des logs

**Format texte** (par défaut) :
```
2025-11-14 15:30:45 - app.services.scraper - INFO - Successfully scraped https://amazon.fr/product: iPhone 14 - €799.99
```

**Format JSON** (avec `ENABLE_JSON_LOGS=true`) :
```json
{
  "timestamp": "2025-11-14T15:30:45Z",
  "level": "INFO",
  "logger": "app.services.scraper",
  "message": "Successfully scraped product",
  "module": "scraper",
  "function": "scrape_product",
  "line": 76
}
```

#### Contexte additionnel

Le système supporte l'ajout de contexte aux logs :

```python
from app.core.logging_config import get_logger, LogContext

logger = get_logger(__name__)

with LogContext(logger, user_id=123, product_id=456):
    logger.info("Price updated")
    # Log inclura automatiquement user_id et product_id
```

### Intégration

Le logging est intégré dans :
- ✅ `app/main.py` - Démarrage de l'application
- ✅ `app/services/scraper.py` - Scraping avec détails des tentatives
- ✅ `app/services/email.py` - Envoi d'emails avec erreurs SMTP
- ✅ `tasks.py` - Tâches Celery avec statistiques

### Exemples de logs

**Scraping réussi** :
```
INFO - Scraping attempt 1/3 for URL: https://amazon.fr/product
INFO - Successfully scraped https://amazon.fr/product: iPhone 14 - €799.99
```

**Erreur avec retry** :
```
WARNING - Timeout on attempt 1 for https://amazon.fr/product: Connection timeout
INFO - Waiting 2s before retry...
INFO - Scraping attempt 2/3 for URL: https://amazon.fr/product
INFO - Successfully scraped https://amazon.fr/product: iPhone 14 - €799.99
```

**Produit indisponible** :
```
WARNING - Product unavailable at URL: https://amazon.fr/product
WARNING - Product 123 is unavailable: Product is no longer available
INFO - Marked product 123 as unavailable
```

---

## 🔄 Retry Logic

### Description

Mécanisme de retry automatique pour le scraping avec backoff exponentiel et gestion intelligente des erreurs.

### Fichiers impliqués

- `app/services/scraper.py` - Implémentation du retry logic

### Configuration

```python
scraper = PriceScraper(
    max_retries=3,      # Nombre maximum de tentatives
    retry_delay=2       # Délai de base entre les tentatives (en secondes)
)
```

### Stratégie de Retry

#### Tentatives
- **3 tentatives maximum** par défaut
- **Backoff exponentiel** : délai augmente à chaque tentative
  - Tentative 1 échoue → attend 2 secondes
  - Tentative 2 échoue → attend 4 secondes
  - Tentative 3 échoue → attend 6 secondes

#### Erreurs avec retry
- ⏱️ **Timeout** : Retry
- 🌐 **Erreurs réseau** : Retry
- 🔌 **Connection refused** : Retry
- ⚠️ **HTTP 5xx** : Retry

#### Erreurs SANS retry
- 🚫 **HTTP 404** (Not Found) : Lève `ProductUnavailableError`
- 🚫 **HTTP 410** (Gone) : Lève `ProductUnavailableError`
- 🚫 **ProductUnavailableError** : Propagé immédiatement

### Exemples d'utilisation

```python
from app.services.scraper import scraper, ProductUnavailableError

try:
    result = scraper.scrape_product("https://amazon.fr/product")
    if result:
        print(f"Prix: {result.price} €")
except ProductUnavailableError:
    print("Produit indisponible")
```

### Logs générés

```
INFO - Scraping attempt 1/3 for URL: https://amazon.fr/product
WARNING - Timeout on attempt 1 for https://amazon.fr/product: Connection timeout
INFO - Waiting 2s before retry...
INFO - Scraping attempt 2/3 for URL: https://amazon.fr/product
WARNING - HTTP error 503 on attempt 2 for https://amazon.fr/product
INFO - Waiting 4s before retry...
INFO - Scraping attempt 3/3 for URL: https://amazon.fr/product
INFO - Successfully scraped https://amazon.fr/product: Product Name - €99.99
```

---

## 🚫 Détection de Produits Indisponibles

### Description

Détection automatique des produits qui ne sont plus disponibles sur les sites marchands, avec marquage dans la base de données.

### Fichiers impliqués

- `app/services/scraper.py` - Détection d'indisponibilité
- `app/models/product.py` - Nouveaux champs dans le modèle
- `app/schemas/product.py` - Schémas Pydantic mis à jour
- `tasks.py` - Gestion dans les tâches Celery

### Nouveaux champs du modèle Product

```python
class Product(Base):
    # ... autres champs ...
    is_available = Column(Boolean, default=True, nullable=False)
    unavailable_since = Column(DateTime, nullable=True)
```

### Détection

#### Indicateurs génériques
Le système détecte les textes suivants (insensibles à la casse) :
- 🇫🇷 Français : "actuellement indisponible", "rupture de stock", "produit indisponible", "n'est plus disponible", "épuisé", "article supprimé"
- 🇬🇧 Anglais : "out of stock", "no longer available", "temporarily out of stock", "sold out"
- 🔍 Autres : "page introuvable", "404"

#### Détection spécifique par site

**Amazon** :
```html
<div id="availability">
    <span>Actuellement indisponible</span>
</div>
```

**Fnac** :
```html
<div class="f-productHeader-buyingArea">
    Produit indisponible
</div>
```

**Darty** :
```html
<div class="product_availability">
    En rupture de stock
</div>
```

### Gestion dans les tâches Celery

#### Marquage automatique

Quand un produit devient indisponible :
```python
product.is_available = False
product.unavailable_since = datetime.utcnow()
product.last_checked = datetime.utcnow()
```

Quand un produit redevient disponible :
```python
product.is_available = True
product.unavailable_since = None
```

#### Logs Celery

```
INFO - Checking product 123: iPhone 14
WARNING - Product 123 is unavailable: Product is no longer available: https://amazon.fr/...
INFO - Marked product 123 as unavailable

# Plus tard...
INFO - Checking product 123: iPhone 14
INFO - Product 123 is available again!
```

### API Response

Les endpoints retournent maintenant les champs de disponibilité :

```json
{
  "id": 123,
  "name": "iPhone 14",
  "current_price": 799.99,
  "target_price": 699.00,
  "is_available": false,
  "unavailable_since": "2025-11-14T15:30:45Z",
  "last_checked": "2025-11-14T16:00:00Z"
}
```

### Exception ProductUnavailableError

```python
from app.services.scraper import ProductUnavailableError

try:
    result = scraper.scrape_product(url)
except ProductUnavailableError as e:
    # Gérer l'indisponibilité
    logger.warning(f"Product unavailable: {e}")
    # Ne pas réessayer
```

---

## 🧪 Tests

### Tests implémentés

Fichier `tests/test_unit_error_handling.py` contient **13 tests** :

#### Retry Logic (4 tests)
- ✅ `test_retry_on_timeout` - Retry sur timeout
- ✅ `test_retry_exhaustion` - Abandon après max retries
- ✅ `test_no_retry_on_404` - Pas de retry sur 404
- ✅ `test_exponential_backoff` - Vérification du backoff exponentiel

#### Détection d'indisponibilité (6 tests)
- ✅ `test_detect_unavailable_generic` - Détection générique
- ✅ `test_detect_available_product` - Produit disponible non marqué
- ✅ `test_detect_out_of_stock_english` - Détection en anglais
- ✅ `test_detect_rupture_de_stock` - Détection en français
- ✅ `test_detect_amazon_unavailability` - Détection Amazon spécifique
- ✅ `test_unavailable_error_raised` - Exception levée correctement

#### Intégration Logging (3 tests)
- ✅ `test_logging_on_success` - Logs de succès
- ✅ `test_logging_on_failure` - Logs d'échec
- ✅ `test_logging_unavailability` - Logs d'indisponibilité

### Exécuter les tests

```bash
cd Backend

# Tests spécifiques error handling
docker-compose exec backend python3 -m pytest tests/test_unit_error_handling.py -v

# Tous les tests unitaires
./run_unit_tests.sh
```

---

## 📈 Métriques et Monitoring

### Statistiques Celery

Les tâches Celery loguent maintenant des statistiques :

```
INFO - Starting price check for 50 products
INFO - Price check completed: 42 checked, 5 unavailable, 3 errors
```

### Analyse des logs

Avec le format JSON, vous pouvez facilement analyser les logs :

```bash
# Compter les produits indisponibles aujourd'hui
cat logs/pricewatch.log | jq 'select(.message | contains("unavailable")) | .product_id' | sort | uniq -c

# Taux de succès du scraping
cat logs/pricewatch.log | jq 'select(.module == "scraper") | .level' | sort | uniq -c

# Temps de response moyen (si ajouté dans les logs)
cat logs/pricewatch.log | jq 'select(.duration) | .duration' | awk '{sum+=$1; count++} END {print sum/count}'
```

---

## 🚀 Améliorations futures

### Priorité Moyenne
- [ ] **Alertes email pour produits indisponibles** - Notifier l'utilisateur
- [ ] **Dashboard admin** - Visualisation des métriques de disponibilité
- [ ] **Historique d'indisponibilité** - Tracker les périodes d'indisponibilité

### Priorité Basse
- [ ] **Prédiction de réapprovisionnement** - ML pour prédire quand un produit revient
- [ ] **Alertes de retour en stock** - Notification quand produit redevient disponible
- [ ] **Intégration Sentry** - Monitoring des erreurs en production

---

## 📚 Références

### Documentation liée
- [RoadMap.md](RoadMap.md) - Roadmap complète du projet
- [TESTING.md](TESTING.md) - Documentation des tests
- [SECURITY_FEATURES.md](SECURITY_FEATURES.md) - Fonctionnalités de sécurité

### Code source
- [app/core/logging_config.py](../app/core/logging_config.py)
- [app/services/scraper.py](../app/services/scraper.py)
- [tasks.py](../tasks.py)
- [tests/test_unit_error_handling.py](../tests/test_unit_error_handling.py)

---

**Dernière mise à jour** : 14/11/2025
