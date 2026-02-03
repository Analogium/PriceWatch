# Cookies pour le Scraping

Ce dossier contient les fichiers de cookies utilisés par le scraper Playwright pour contourner les protections anti-bot d'Amazon et d'autres sites.

## Pourquoi les cookies sont nécessaires

Amazon a des protections anti-bot très agressives qui bloquent :
- Les requêtes HTTP classiques (BeautifulSoup)
- Les navigateurs headless (Playwright) même avec stealth mode

En injectant des cookies de session d'un utilisateur légitime, Amazon fait confiance à la session et ne bloque pas le scraping.

## Comment exporter les cookies

### Option A : Extension Cookie-Editor (Recommandé)

1. Installer l'extension **Cookie-Editor** ([Firefox](https://addons.mozilla.org/fr/firefox/addon/cookie-editor/) / [Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm))
2. Se connecter à amazon.fr avec votre compte
3. Cliquer sur l'icône Cookie-Editor
4. Cliquer sur **Export** > **Export as JSON**
5. Sauvegarder le contenu dans `Backend/cookies/amazon_cookies.json`

### Option B : Via les DevTools

1. Se connecter à amazon.fr
2. Ouvrir les DevTools (F12)
3. Aller dans **Application** > **Cookies** > **amazon.fr**
4. Copier les cookies importants (voir liste ci-dessous)
5. Créer manuellement le fichier JSON

## Format du fichier

Le fichier doit être un tableau JSON de cookies :

```json
[
  {
    "name": "session-id",
    "value": "XXX-XXXXXXX-XXXXXXX",
    "domain": ".amazon.fr",
    "path": "/",
    "secure": true,
    "httpOnly": false
  },
  {
    "name": "session-token",
    "value": "XXXXXXXXXXXXX",
    "domain": ".amazon.fr",
    "path": "/",
    "secure": true,
    "httpOnly": true
  }
]
```

## Cookies Amazon essentiels

| Cookie | Description | Obligatoire |
|--------|-------------|-------------|
| `session-id` | ID de session | Oui |
| `session-id-time` | Timestamp session | Oui |
| `session-token` | Token CSRF | Oui |
| `ubid-acbfr` | ID utilisateur | Oui |
| `at-acbfr` | Token auth | Si connecté |
| `sess-at-acbfr` | Session auth | Si connecté |
| `x-acbfr` | Token divers | Recommandé |
| `lc-acbfr` | Langue | Recommandé |

## Expiration des cookies

Les cookies Amazon expirent généralement après **2 à 4 semaines**.

Si le scraping Amazon commence à échouer régulièrement, il faut renouveler les cookies en répétant la procédure d'export.

L'application enverra une notification par email à l'admin si les cookies semblent expirés (échecs répétés sur Amazon).

## Sécurité

- **Ne jamais commiter les fichiers cookies** (ils sont ignorés par .gitignore)
- Les cookies donnent accès au compte Amazon - les traiter comme des credentials
- Utiliser de préférence un compte Amazon secondaire

## Fichiers supportés

- `amazon_cookies.json` - Cookies Amazon.fr
- `fnac_cookies.json` - Cookies Fnac.com (si nécessaire)
- `cdiscount_cookies.json` - Cookies Cdiscount.com (si nécessaire)

## Upload via API

Les administrateurs peuvent aussi uploader les cookies via l'endpoint API :

```bash
curl -X POST "http://localhost:8000/api/v1/admin/cookies/amazon" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "cookies=@amazon_cookies.json"
```
