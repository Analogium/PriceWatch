# 🕷️ Scraping Avancé - Documentation

## Vue d'ensemble

PriceWatch implémente plusieurs fonctionnalités avancées de scraping pour améliorer la fiabilité, les performances et éviter les blocages :

- **Rotation des User-Agents** - Évite la détection comme bot
- **Cache Redis** - Réduit les requêtes redondantes
- **Circuit Breaker** - Protège contre la surcharge des sites
- **Proxies rotatifs** - Évite les blocages IP

---

## 1. Rotation des User-Agents

### Description

La rotation des User-Agents permet d'éviter la détection comme bot en variant les headers HTTP à chaque requête. PriceWatch utilise un pool de 15 User-Agents réalistes simulant différents navigateurs et systèmes d'exploitation.

### Utilisation

```python
from app.services.scraper_advanced import UserAgentRotator

# Obtenir un User-Agent aléatoire
ua = UserAgentRotator.get_random()

# Obtenir des headers complets avec User-Agent
headers = UserAgentRotator.get_headers(include_full_headers=True)

# Obtenir uniquement le User-Agent
headers = UserAgentRotator.get_headers(include_full_headers=False)
```

### Pool de User-Agents

Le pool comprend :
- **Chrome** (Windows, macOS, Linux) - Versions 120, 121, 122
- **Firefox** (Windows, macOS, Linux) - Versions 121, 122
- **Safari** (macOS) - Version 17.1, 17.2
- **Edge** (Windows) - Versions 120, 121

### Intégration

La rotation est **automatique** dans `PriceScraper`. À chaque tentative de scraping, un nouveau User-Agent est sélectionné aléatoirement.

```python
# Automatiquement utilisé dans scrape_product()
scraper = PriceScraper()
result = scraper.scrape_product(url)  # User-Agent rotatif appliqué
```

---

## 2. Cache Redis

### Description

Le cache Redis stocke les résultats de scraping pour éviter de refaire des requêtes inutiles vers les sites e-commerce. Chaque résultat est mis en cache avec un TTL (Time-To-Live) configurable.

### Configuration

Variables d'environnement dans `.env` :

```env
SCRAPER_CACHE_ENABLED=true          # Activer/désactiver le cache
SCRAPER_CACHE_TTL=3600              # Durée de vie en secondes (1h par défaut)
```

### Utilisation

```python
from app.services.scraper_advanced import ScraperCache

# Initialisation
cache = ScraperCache(default_ttl=3600)

# Vérifier le cache
cached_data = cache.get(url)
if cached_data:
    print(f"Cache HIT: {cached_data}")

# Mettre en cache un résultat
data = {"name": "Product", "price": 99.99}
cache.set(url, data, ttl=1800)  # 30 minutes

# Invalider le cache pour une URL
cache.invalidate(url)

# Vider tout le cache scraper
cache.clear_all()
```

### Intégration

Le cache est **automatiquement utilisé** dans `PriceScraper` :

```python
scraper = PriceScraper(use_cache=True, cache_ttl=3600)

# Premier appel : scraping réel
result1 = scraper.scrape_product(url)

# Deuxième appel : résultat depuis le cache (si < 1h)
result2 = scraper.scrape_product(url)

# Forcer un scraping frais (bypass cache)
result3 = scraper.scrape_product(url, bypass_cache=True)
```

### Avantages

- ✅ **Réduit la charge** sur les sites e-commerce
- ✅ **Améliore les performances** (pas de requête HTTP)
- ✅ **Évite les blocages** (moins de requêtes = moins suspicieux)
- ✅ **Économise des ressources** (bande passante, CPU)

### Clés de cache

Les clés sont générées avec un hash MD5 de l'URL :
```
scraper_cache:<md5_hash>
```

Exemple :
```
scraper_cache:5d41402abc4b2a76b9719d911017c592
```

---

## 3. Circuit Breaker

### Description

Le Circuit Breaker implémente le pattern de résilience pour protéger les sites e-commerce contre la surcharge. Lorsqu'un site rencontre trop d'échecs consécutifs, le circuit s'ouvre automatiquement et bloque temporairement les requêtes.

### États du Circuit

1. **CLOSED** (Fermé) - État normal, requêtes autorisées
2. **OPEN** (Ouvert) - Trop d'échecs, requêtes bloquées
3. **HALF_OPEN** (Semi-ouvert) - Test de récupération

```
CLOSED ──(5 échecs)──> OPEN ──(60s timeout)──> HALF_OPEN ──(2 succès)──> CLOSED
   │                      │                         │
   │                      └─────(timeout pas écoulé)─┘
   └────────────────(succès)──────────────────────────┘
```

### Configuration

Variables d'environnement :

```env
SCRAPER_CIRCUIT_BREAKER_ENABLED=true     # Activer/désactiver
SCRAPER_CIRCUIT_BREAKER_THRESHOLD=5      # Nombre d'échecs avant ouverture
SCRAPER_CIRCUIT_BREAKER_TIMEOUT=60       # Secondes avant tentative de récupération
```

### Utilisation

```python
from app.services.scraper_advanced import CircuitBreaker

# Initialisation
breaker = CircuitBreaker(
    failure_threshold=5,      # Ouvre après 5 échecs
    recovery_timeout=60,      # 60s avant test de récupération
    success_threshold=2       # 2 succès pour fermer
)

# Vérifier si le site est disponible
if breaker.is_available("amazon"):
    try:
        # Effectuer le scraping
        result = scrape_amazon()
        breaker.record_success("amazon")  # Enregistrer le succès
    except Exception:
        breaker.record_failure("amazon")  # Enregistrer l'échec
else:
    print("Circuit OPEN - requêtes bloquées pour amazon")

# Réinitialiser manuellement un circuit
breaker.reset("amazon")
```

### Intégration

Le circuit breaker est **automatiquement géré** dans `PriceScraper` :

```python
scraper = PriceScraper(use_circuit_breaker=True)

# Le circuit breaker vérifie automatiquement l'état avant chaque scraping
result = scraper.scrape_product(url)
# Si circuit OPEN -> retourne None
# Si circuit CLOSED/HALF_OPEN -> tente le scraping
```

### Suivi par site

Le circuit breaker suit l'état **par site e-commerce** :
- `amazon` (Amazon.fr, .com, .de, etc.)
- `fnac`
- `darty`
- `cdiscount`
- `boulanger`
- `leclerc`

Chaque site a son propre circuit indépendant.

### Avantages

- ✅ **Évite la surcharge** des sites
- ✅ **Réduit les erreurs en cascade** (fail fast)
- ✅ **Auto-récupération** après timeout
- ✅ **Protège l'application** contre les bans IP

---

## 4. Proxies Rotatifs

### Description

Les proxies rotatifs permettent de faire passer les requêtes de scraping par différentes adresses IP, évitant ainsi les blocages basés sur l'IP source.

### Configuration

Variables d'environnement :

```env
SCRAPER_PROXY_ENABLED=false                        # Activer/désactiver
PROXY_LIST=http://proxy1:8080,http://proxy2:8080  # Liste de proxies
```

Format des proxies :
```
http://ip:port
http://username:password@ip:port
https://ip:port
```

### Utilisation

```python
from app.services.scraper_advanced import ProxyRotator

# Initialisation avec liste de proxies
proxies = [
    "http://proxy1.example.com:8080",
    "http://user:pass@proxy2.example.com:8080"
]
rotator = ProxyRotator(proxy_list=proxies)

# Obtenir le prochain proxy (rotation)
proxy = rotator.get_next()

# Obtenir un proxy aléatoire
proxy = rotator.get_random()

# Obtenir un dict pour requests
proxies_dict = rotator.get_proxies_dict()
# Retourne: {"http": "...", "https": "..."}

# Ajouter/supprimer des proxies dynamiquement
rotator.add_proxy("http://newproxy:8080")
rotator.remove_proxy("http://oldproxy:8080")
```

### Intégration

Les proxies sont **automatiquement utilisés** dans `PriceScraper` :

```python
scraper = PriceScraper(use_proxy=True)

# Les proxies sont automatiquement rotés à chaque requête
result = scraper.scrape_product(url)
```

### Sélection des proxies

Deux modes disponibles :
1. **Rotation séquentielle** - `get_next()` : 1 → 2 → 3 → 1 → ...
2. **Sélection aléatoire** - `get_random()` : choix aléatoire à chaque appel

`PriceScraper` utilise la **sélection aléatoire** par défaut.

### ⚠️ Important

- Les proxies doivent être **fiables et rapides**
- Les proxies gratuits peuvent être **lents ou instables**
- Privilégiez des proxies **résidentiels** pour le scraping e-commerce
- Testez vos proxies avant de les ajouter

---

## 🔧 Configuration Globale

### Fichier `.env`

```env
# ===== SCRAPING AVANCÉ =====

# Cache Redis
SCRAPER_CACHE_ENABLED=true
SCRAPER_CACHE_TTL=3600

# Circuit Breaker
SCRAPER_CIRCUIT_BREAKER_ENABLED=true
SCRAPER_CIRCUIT_BREAKER_THRESHOLD=5
SCRAPER_CIRCUIT_BREAKER_TIMEOUT=60

# Proxies
SCRAPER_PROXY_ENABLED=false
PROXY_LIST=
```

### Exemple d'utilisation complète

```python
from app.services.scraper import PriceScraper

# Initialisation avec toutes les fonctionnalités avancées
scraper = PriceScraper(
    max_retries=3,
    retry_delay=2,
    use_cache=True,             # Utilise le cache Redis
    cache_ttl=3600,             # 1 heure de cache
    use_circuit_breaker=True,   # Active le circuit breaker
    use_proxy=False             # Proxies désactivés (pas nécessaire par défaut)
)

# Scraping avec toutes les fonctionnalités
url = "https://www.amazon.fr/dp/B08N5WRWNW"
try:
    result = scraper.scrape_product(url)
    if result:
        print(f"✅ Scraped: {result.name} - €{result.price}")
    else:
        print("❌ Scraping failed (circuit breaker open?)")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 📊 Monitoring

### Logs

Les fonctionnalités avancées génèrent des logs détaillés :

```
[INFO] PriceScraper initialized (cache=True, circuit_breaker=True, proxy=False)
[INFO] Cache HIT for URL: https://www.amazon.fr/...
[DEBUG] Selected User-Agent: Mozilla/5.0 (Windows NT...)
[INFO] Circuit CLOSED for 'amazon' - requests allowed
[WARNING] Circuit failure for 'amazon': 3/5
[WARNING] Circuit OPEN for 'amazon' - requests blocked
[INFO] Circuit moving to HALF_OPEN state (recovery attempt)
```

### Métriques Redis

Vous pouvez surveiller les états du circuit breaker dans Redis :

```bash
# Liste des clés circuit breaker
redis-cli KEYS "circuit_breaker:*"

# État d'un circuit
redis-cli GET "circuit_breaker:amazon:state"

# Nombre d'échecs
redis-cli GET "circuit_breaker:amazon:failures"
```

---

## 🧪 Tests

Tests unitaires disponibles dans `tests/test_unit_scraper_advanced.py` :

```bash
# Exécuter tous les tests
pytest tests/test_unit_scraper_advanced.py -v

# Tests spécifiques
pytest tests/test_unit_scraper_advanced.py::TestUserAgentRotator -v
pytest tests/test_unit_scraper_advanced.py::TestScraperCache -v
pytest tests/test_unit_scraper_advanced.py::TestCircuitBreaker -v
pytest tests/test_unit_scraper_advanced.py::TestProxyRotator -v
```

**Couverture** : 41 tests, 100% de couverture

---

## 🚀 Bonnes Pratiques

### 1. Cache

- ✅ Utilisez le cache pour les vérifications fréquentes
- ✅ Ajustez le TTL selon vos besoins (1h par défaut)
- ✅ Utilisez `bypass_cache=True` pour les vérifications manuelles
- ❌ N'utilisez pas de TTL trop long (données obsolètes)

### 2. Circuit Breaker

- ✅ Gardez les valeurs par défaut sauf besoins spécifiques
- ✅ Surveillez les logs pour détecter les circuits ouverts
- ✅ Réinitialisez manuellement si nécessaire
- ❌ Ne désactivez pas sauf pour debug

### 3. User-Agent

- ✅ Laissez la rotation activée (automatique)
- ✅ Le pool est déjà optimisé
- ❌ N'ajoutez pas de User-Agents suspects ou obsolètes

### 4. Proxies

- ✅ Utilisez uniquement si nécessaire (blocages IP fréquents)
- ✅ Testez vos proxies avant ajout
- ✅ Privilégiez des proxies résidentiels
- ❌ N'utilisez pas de proxies gratuits en production

---

## 📚 Références

- **Pattern Circuit Breaker** : [Martin Fowler](https://martinfowler.com/bliki/CircuitBreaker.html)
- **Redis Caching** : [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- **User-Agent Strings** : [WhatIsMyBrowser](https://www.whatismybrowser.com/guides/the-latest-user-agent/)

---

**Dernière mise à jour** : 2025-12-23
