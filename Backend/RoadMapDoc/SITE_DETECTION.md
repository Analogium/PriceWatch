# 🕷️ Détection Automatique de Sites - Documentation

Cette documentation décrit le système de détection automatique de sites e-commerce et le support multi-sites implémenté dans PriceWatch.

## 📊 Vue d'ensemble

PriceWatch détecte automatiquement le site e-commerce à partir de l'URL du produit et utilise le scraper approprié. Le système supporte **6 sites majeurs** :

1. 🛒 **Amazon** (multi-pays : .fr, .com, .de, .co.uk, .es, .it)
2. 📚 **Fnac** (.com, .fr)
3. ⚡ **Darty** (.com)
4. 💰 **Cdiscount** (.com)
5. 🔌 **Boulanger** (.com, .fr)
6. 🛍️ **E.Leclerc** (e.leclerc, e-leclerc)

---

## 🔍 Classe SiteDetector

### Description

La classe `SiteDetector` est responsable de la détection automatique du site à partir de l'URL.

### Emplacement

[app/services/scraper.py](../app/services/scraper.py:19-62)

### Configuration des patterns

```python
SITE_PATTERNS = {
    'amazon': ['amazon.fr', 'amazon.com', 'amazon.de', 'amazon.co.uk', 'amazon.es', 'amazon.it'],
    'fnac': ['fnac.com', 'fnac.fr'],
    'darty': ['darty.com'],
    'cdiscount': ['cdiscount.com'],
    'boulanger': ['boulanger.com', 'boulanger.fr'],
    'leclerc': ['e.leclerc', 'e-leclerc'],
}
```

### Utilisation

```python
from app.services.scraper import SiteDetector

# Détection automatique
site = SiteDetector.detect_site("https://www.amazon.fr/dp/B08L5VNF78")
# Retourne: 'amazon'

site = SiteDetector.detect_site("https://www.cdiscount.com/product/123")
# Retourne: 'cdiscount'

site = SiteDetector.detect_site("https://www.unknownsite.com/product/123")
# Retourne: None
```

### Fonctionnalités

- ✅ **Insensible à la casse** : Fonctionne avec majuscules/minuscules
- ✅ **Gestion du préfixe www.** : Détecte avec ou sans `www.`
- ✅ **Support multi-pays** : Amazon fonctionne sur tous les domaines
- ✅ **URLs complexes** : Fonctionne avec paramètres GET, ancres, etc.
- ✅ **Robuste** : Gestion gracieuse des URLs invalides

### Algorithme

1. Parse l'URL avec `urlparse()`
2. Extrait le domaine (netloc)
3. Supprime le préfixe `www.` si présent
4. Compare le domaine avec chaque pattern défini
5. Retourne le nom du site ou `None`

---

## 🛒 Scrapers Spécifiques

### Amazon

**Domaines supportés** : amazon.fr, amazon.com, amazon.de, amazon.co.uk, amazon.es, amazon.it

**Éléments extraits** :
```python
# Title
title_elem = soup.find('span', {'id': 'productTitle'})

# Price
price_whole = soup.find('span', {'class': 'a-price-whole'})
price_fraction = soup.find('span', {'class': 'a-price-fraction'})

# Image
image_elem = soup.find('img', {'id': 'landingImage'})
```

**Détection d'indisponibilité** :
```python
availability_elem = soup.find('div', {'id': 'availability'})
```

### Fnac

**Domaines supportés** : fnac.com, fnac.fr

**Éléments extraits** :
```python
# Title
title_elem = soup.find('h1', {'class': 'f-productHeader-Title'})

# Price
price_elem = soup.find('span', {'class': 'f-priceBox-price'})

# Image
image_elem = soup.find('img', {'class': 'f-productVisuals-mainImage'})
```

**Détection d'indisponibilité** :
```python
availability_elem = soup.find('div', {'class': 'f-productHeader-buyingArea'})
```

### Darty

**Domaines supportés** : darty.com

**Éléments extraits** :
```python
# Title
title_elem = soup.find('h1', {'class': 'product_title'})

# Price
price_elem = soup.find('span', {'class': 'product_price'})

# Image
image_elem = soup.find('img', {'class': 'product_image'})
```

**Détection d'indisponibilité** :
```python
availability_elem = soup.find('div', {'class': 'product_availability'})
```

### Cdiscount ✨ NEW

**Domaines supportés** : cdiscount.com

**Éléments extraits** :
```python
# Title
title_elem = soup.find('h1', {'itemprop': 'name'})
# Fallback
title_elem = soup.find('h1', {'class': 'fpDesCol1'})

# Price - Multiple formats
price_elem = soup.find('span', {'class': 'fpPrice'})
price_elem = soup.find('span', {'itemprop': 'price'})
price_elem = soup.find('meta', {'itemprop': 'price'})

# Image
image_elem = soup.find('img', {'class': 'img', 'itemprop': 'image'})
```

**Détection d'indisponibilité** :
```python
availability_elem = soup.find('div', {'class': 'fpStockAvailability'})
```

### Boulanger ✨ NEW

**Domaines supportés** : boulanger.com, boulanger.fr

**Éléments extraits** :
```python
# Title
title_elem = soup.find('h1', {'class': 'product-title'})
title_elem = soup.find('h1', {'itemprop': 'name'})

# Price
price_elem = soup.find('span', {'class': 'price'})
price_elem = soup.find('meta', {'itemprop': 'price'})

# Image
image_elem = soup.find('img', {'class': 'product-visual__image'})
```

**Détection d'indisponibilité** :
```python
availability_elem = soup.find('div', {'class': 'availability'})
```

### E.Leclerc ✨ NEW

**Domaines supportés** : e.leclerc, e-leclerc

**Éléments extraits** :
```python
# Title
title_elem = soup.find('h1', {'class': 'product-name'})
title_elem = soup.find('h1', {'itemprop': 'name'})

# Price
price_elem = soup.find('span', {'class': 'product-price'})
price_elem = soup.find('meta', {'itemprop': 'price'})

# Image
image_elem = soup.find('img', {'class': 'product-image'})
```

**Détection d'indisponibilité** :
```python
availability_elem = soup.find('span', {'class': 'stock-status'})
```

---

## 🔄 Flux de Scraping Amélioré

### 1. Détection automatique du site

```python
# Dans scrape_product()
site = SiteDetector.detect_site(url)
```

### 2. Routage vers le scraper approprié

```python
if site == 'amazon':
    result = self._scrape_amazon(soup)
elif site == 'fnac':
    result = self._scrape_fnac(soup)
elif site == 'darty':
    result = self._scrape_darty(soup)
elif site == 'cdiscount':
    result = self._scrape_cdiscount(soup)
elif site == 'boulanger':
    result = self._scrape_boulanger(soup)
elif site == 'leclerc':
    result = self._scrape_leclerc(soup)
else:
    # Generic scraper pour sites inconnus
    logger.info(f"Using generic scraper for unknown site: {url}")
    result = self._scrape_generic(soup)
```

### 3. Logs automatiques

Le système génère automatiquement des logs :

```
INFO - Detected site 'amazon' from domain 'amazon.fr'
INFO - Scraping attempt 1/3 for URL: https://www.amazon.fr/...
INFO - Successfully scraped https://www.amazon.fr/...: iPhone 14 - €799.99
```

Pour sites inconnus :
```
DEBUG - Unknown site from domain 'example.com'
INFO - Using generic scraper for unknown site: https://www.example.com/product
```

---

## 🧪 Tests

### Tests de détection

Fichier : [tests/test_unit_site_detection.py](../tests/test_unit_site_detection.py)

**24 tests unitaires** couvrant :
- Détection de tous les sites supportés
- Support multi-pays Amazon
- Insensibilité à la casse
- Gestion des URL complexes
- URLs sans www.
- Gestion des erreurs
- Validation des patterns

### Tests des scrapers

Fichier : [tests/test_unit_new_scrapers.py](../tests/test_unit_new_scrapers.py)

**13 tests unitaires** couvrant :
- Scraping Cdiscount (3 tests)
- Scraping Boulanger (3 tests)
- Scraping E.Leclerc (3 tests)
- Routage correct vers les scrapers (4 tests)

### Exécution des tests

```bash
cd Backend

# Tests de détection uniquement
docker-compose exec backend python3 -m pytest tests/test_unit_site_detection.py -v

# Tests des nouveaux scrapers
docker-compose exec backend python3 -m pytest tests/test_unit_new_scrapers.py -v

# Tous les tests
./run_unit_tests.sh
```

**Résultats** :
- ✅ 24/24 tests de détection passent (100%)
- ✅ 13/13 tests de scrapers passent (100%)
- ✅ Coverage total : 73% (scraper.py : 85%)

---

## 📝 Ajout d'un Nouveau Site

Pour ajouter le support d'un nouveau site (ex: Carrefour) :

### 1. Ajouter le pattern de domaine

```python
SITE_PATTERNS = {
    # ... sites existants ...
    'carrefour': ['carrefour.fr', 'carrefour.com'],
}
```

### 2. Créer le scraper spécifique

```python
def _scrape_carrefour(self, soup: BeautifulSoup) -> Optional[ProductScrapedData]:
    """Scrape Carrefour product page."""
    try:
        # Title
        title_elem = soup.find('h1', {'class': 'product-title'})
        name = title_elem.text.strip() if title_elem else "Unknown Product"

        # Price
        price_elem = soup.find('span', {'class': 'price'})
        if price_elem:
            price_str = price_elem.text.strip().replace('€', '').replace(',', '.')
            price = float(re.sub(r'[^\d.]', '', price_str))
        else:
            logger.warning("Failed to extract price from Carrefour page")
            return None

        # Image
        image_elem = soup.find('img', {'class': 'product-image'})
        image = image_elem.get('src') if image_elem else None

        return ProductScrapedData(name=name, price=price, image=image)

    except Exception as e:
        logger.error(f"Error parsing Carrefour page: {str(e)}", exc_info=True)
        return None
```

### 3. Ajouter le routage

```python
# Dans scrape_product()
elif site == 'carrefour':
    result = self._scrape_carrefour(soup)
```

### 4. Ajouter la détection d'indisponibilité

```python
# Dans _is_product_unavailable()
elif site == 'carrefour':
    availability_elem = soup.find('div', {'class': 'stock-info'})
    if availability_elem:
        availability_text = availability_elem.get_text().lower()
        if 'indisponible' in availability_text or 'rupture' in availability_text:
            return True
```

### 5. Créer les tests

```python
def test_detect_carrefour(self):
    """Test detection of Carrefour."""
    url = "https://www.carrefour.fr/product/123"
    assert SiteDetector.detect_site(url) == 'carrefour'

def test_scrape_carrefour_success(self):
    """Test successful Carrefour scraping."""
    html = """..."""
    soup = BeautifulSoup(html, 'html.parser')
    scraper = PriceScraper()
    result = scraper._scrape_carrefour(soup)
    assert result is not None
    assert result.price == 19.99
```

---

## 📊 Statistiques

### Sites supportés

| Site | Domaines | Tests | Statut |
|------|----------|-------|--------|
| Amazon | 6 (.fr, .com, .de, .uk, .es, .it) | ✅ | Opérationnel |
| Fnac | 2 (.com, .fr) | ✅ | Opérationnel |
| Darty | 1 (.com) | ✅ | Opérationnel |
| Cdiscount | 1 (.com) | ✅ | Opérationnel |
| Boulanger | 2 (.com, .fr) | ✅ | Opérationnel |
| E.Leclerc | 2 (e.leclerc, e-leclerc) | ✅ | Opérationnel |
| **Total** | **14 domaines** | **37 tests** | **6 sites** |

### Coverage

- **app/services/scraper.py** : 85% (300 lignes)
- **Tests unitaires** : 113 tests (100% de réussite)
- **Coverage total** : 73%

---

## 🚀 Prochaines étapes

### Priorité Haute
- [ ] Tester les scrapers en production avec URLs réelles
- [ ] Monitorer les taux de succès par site
- [ ] Ajuster les sélecteurs si sites changent leur structure

### Priorité Moyenne
- [ ] Support Playwright/Selenium pour sites JavaScript
- [ ] Ajout d'autres sites (Carrefour, Auchan, Intermarché)
- [ ] Cache des résultats de scraping
- [ ] Détection automatique des changements de structure HTML

### Priorité Basse
- [ ] Scraping de reviews/notes produits
- [ ] Détection de promotions/soldes
- [ ] Historique de disponibilité
- [ ] Comparaison de prix entre sites

---

## 📚 Références

### Code source
- [app/services/scraper.py](../app/services/scraper.py) - Implémentation complète
- [tests/test_unit_site_detection.py](../tests/test_unit_site_detection.py) - Tests de détection
- [tests/test_unit_new_scrapers.py](../tests/test_unit_new_scrapers.py) - Tests des scrapers
- [test_site_detection.py](../test_site_detection.py) - Script de test rapide

### Documentation liée
- [RoadMap.md](RoadMap.md) - Roadmap complète
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Gestion des erreurs
- [TESTING.md](TESTING.md) - Documentation des tests

---

**Dernière mise à jour** : 15/11/2025
