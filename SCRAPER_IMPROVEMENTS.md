# Améliorations du Scraper - Instructions

## Contexte

Le scraper Amazon échoue systématiquement à cause de CAPTCHAs. Le circuit breaker est en état OPEN avec 46+ échecs consécutifs. Les fichiers concernés sont dans `Backend/app/services/`.

---

## Améliorations à implémenter

### 1. Nettoyage automatique des URLs Amazon

**Fichier** : `Backend/app/services/scraper.py`

**Problème** : Les URLs Amazon avec paramètres de tracking (`dib=`, `pd_rd_r=`, etc.) déclenchent la détection anti-bot.

**Solution** : Ajouter une méthode dans `PriceScraper` pour nettoyer les URLs avant scraping.

```python
import re

def _clean_amazon_url(self, url: str) -> str:
    """Extrait uniquement /dp/ASIN ou /gp/product/ASIN de l'URL Amazon."""
    # Pattern pour extraire l'ASIN (10 caractères alphanumériques)
    asin_match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
    if asin_match:
        asin = asin_match.group(1)
        # Extraire le domaine
        domain_match = re.search(r'(https?://[^/]+)', url)
        if domain_match:
            return f"{domain_match.group(1)}/dp/{asin}"
    return url
```

**Appel** : Au début de `scrape_product()` et dans `playwright_scraper.py` avant chaque requête Amazon.

---

### 2. Intégrer playwright-stealth

**Fichier** : `Backend/app/services/playwright_scraper.py`

**Problème** : Les flags `--disable-blink-features=AutomationControlled` ne suffisent pas. Amazon détecte toujours Playwright.

**Installation** :
```bash
pip install playwright-stealth
```

**Ajouter dans requirements.txt** :
```
playwright-stealth>=1.0.6
```

**Modification du code** : Remplacer le lancement du browser dans `PlaywrightScraper._scrape_amazon()` :

```python
from playwright_stealth import stealth_async

async with async_playwright() as p:
    browser = await p.chromium.launch(
        headless=True,
        args=[
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    )
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent=UserAgentRotator.get_random(),
        locale="fr-FR",
        timezone_id="Europe/Paris",
    )
    page = await context.new_page()
    await stealth_async(page)  # <-- Ajouter cette ligne
    # ... reste du code
```

---

### 3. Augmenter les délais pour Amazon

**Fichier** : `Backend/app/services/scraper.py` et `playwright_scraper.py`

**Problème** : Délais actuels (2-5s) trop courts pour Amazon.

**Solution** : Ajouter des délais spécifiques par site.

```python
SITE_DELAYS = {
    "amazon": {"min": 5, "max": 10},
    "fnac": {"min": 2, "max": 4},
    "default": {"min": 1, "max": 3},
}

def _get_delay(self, site: str) -> float:
    delays = SITE_DELAYS.get(site, SITE_DELAYS["default"])
    return random.uniform(delays["min"], delays["max"])
```

**Appliquer** : Avant chaque requête et entre les retries.

---

### 4. Ajouter un Referer réaliste

**Fichier** : `Backend/app/services/scraper_advanced.py`

**Problème** : Absence de Referer = comportement suspect.

**Solution** : Modifier `UserAgentRotator.get_headers()` :

```python
REFERERS = {
    "amazon": [
        "https://www.google.fr/search?q=amazon",
        "https://www.google.fr/",
        "https://www.amazon.fr/",
    ],
    "default": [
        "https://www.google.fr/",
    ],
}

@classmethod
def get_headers(cls, site: str = "default", include_full_headers: bool = True) -> Dict[str, str]:
    headers = {"User-Agent": cls.get_random()}
    if include_full_headers:
        referers = cls.REFERERS.get(site, cls.REFERERS["default"])
        headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": random.choice(referers),  # <-- Ajout
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",  # <-- Changé de "none" à "cross-site"
            "Sec-Fetch-User": "?1",  # <-- Ajout
            "Cache-Control": "max-age=0",
        })
    return headers
```

---

### 5. Augmenter le seuil du circuit breaker pour Amazon

**Fichier** : `Backend/app/services/scraper_advanced.py`

**Problème** : Seuil de 5 échecs trop bas pour Amazon qui renvoie souvent des CAPTCHAs.

**Solution** : Seuils différenciés par site.

```python
CIRCUIT_BREAKER_THRESHOLDS = {
    "amazon": {"failure_threshold": 10, "recovery_timeout": 120},
    "default": {"failure_threshold": 5, "recovery_timeout": 60},
}
```

---

### 6. (Optionnel) Rotation de proxies

**Fichier** : `Backend/app/core/config.py`

Si les améliorations ci-dessus ne suffisent pas, activer la rotation de proxies résidentiels.

```env
SCRAPER_PROXY_ENABLED=True
PROXY_LIST=http://user:pass@proxy1:port,http://user:pass@proxy2:port
```

Services recommandés : Bright Data, Oxylabs, ou SOAX (proxies résidentiels FR).

---

## Ordre d'implémentation recommandé

1. **Nettoyage URLs** (impact immédiat, 10 lignes)
2. **playwright-stealth** (impact élevé, simple)
3. **Referer réaliste** (impact moyen, simple)
4. **Délais augmentés** (impact moyen, simple)
5. **Seuils circuit breaker** (qualité de vie)
6. **Proxies** (si toujours bloqué)

---

## Commande pour reset le circuit breaker après les modifications

```bash
docker exec pricewatch_redis redis-cli KEYS "circuit*" | xargs docker exec -i pricewatch_redis redis-cli DEL
```

Puis rebuild :
```bash
docker compose up -d --build pricewatch_backend
```

---

## Tests

Après implémentation, tester avec une URL Amazon simple :
```
https://www.amazon.fr/dp/B0BN93SMP5
```
