# 🚀 Guide Rapide - Nouvelles Fonctionnalités de Sécurité

## Ce qui a été ajouté

### 🔐 5 Nouvelles Fonctionnalités de Sécurité

1. **Refresh Tokens** - Tokens de longue durée pour renouveler l'accès
2. **Rate Limiting** - Protection contre les attaques par force brute
3. **Vérification d'Email** - Activation de compte par email
4. **Réinitialisation de Mot de Passe** - Flow sécurisé de reset
5. **Politique de Mots de Passe Forts** - Validation stricte

---

## 📋 Nouveaux Endpoints API

```
POST /api/v1/auth/refresh            → Rafraîchir le token
POST /api/v1/auth/verify-email       → Vérifier l'email
POST /api/v1/auth/forgot-password    → Demander réinitialisation
POST /api/v1/auth/reset-password     → Réinitialiser le mot de passe
```

---

## 🧪 Tester les Nouvelles Fonctionnalités

### Option 1 : Script de test automatique

```bash
cd Backend
./run_tests.sh
```

### Option 2 : Test manuel avec curl

#### 1. Inscription (avec mot de passe fort)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

#### 2. Login (récupère access + refresh tokens)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Réponse** :
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### 3. Rafraîchir le token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "VOTRE_REFRESH_TOKEN"
  }'
```

#### 4. Demander réinitialisation de mot de passe
```bash
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

---

## ⚙️ Configuration Requise

### Variables d'environnement (.env)

Ajoutez ces nouvelles variables à votre fichier `.env` :

```env
# Tokens
REFRESH_TOKEN_EXPIRE_DAYS=7

# Politique de mots de passe
MIN_PASSWORD_LENGTH=8
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_DIGIT=true
REQUIRE_SPECIAL_CHAR=true

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Email (déjà configuré normalement)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@pricewatch.com
```

### Base de données

Les nouvelles colonnes seront créées automatiquement au démarrage :
- `users.is_verified`
- `users.verification_token`
- `users.reset_token`
- `users.reset_token_expires`

---

## 🔍 Vérification Rapide

### 1. Vérifier que Redis est actif

```bash
docker ps | grep redis
# ou si Redis local
redis-cli ping
# Doit retourner: PONG
```

### 2. Vérifier que le backend démarre sans erreur

```bash
cd Backend
uvicorn app.main:app --reload
```

Vérifiez les logs - vous devriez voir :
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3. Tester le rate limiting

Lancez plusieurs requêtes rapides :
```bash
for i in {1..10}; do curl http://localhost:8000/api/v1/auth/me; done
```

Après ~100 requêtes en 1 minute, vous devriez recevoir :
```json
{
  "detail": "Rate limit exceeded. Maximum 100 requests per 60 seconds."
}
```

---

## 📝 Fichiers Modifiés/Créés

### Nouveaux fichiers
- ✨ `app/core/rate_limit.py` - Middleware de rate limiting
- ✨ `test_security.py` - Tests automatisés
- ✨ `run_tests.sh` - Script de lancement des tests
- ✨ `RoadMapDoc/SECURITY_FEATURES.md` - Documentation complète
- ✨ `RoadMapDoc/QUICKSTART_SECURITY.md` - Ce fichier

### Fichiers modifiés
- 📝 `app/core/config.py` - Nouvelles variables de config
- 📝 `app/core/security.py` - Fonctions de sécurité avancées
- 📝 `app/models/user.py` - Nouveaux champs (is_verified, tokens, etc.)
- 📝 `app/schemas/user.py` - Nouveaux schémas pour les endpoints
- 📝 `app/api/endpoints/auth.py` - Nouveaux endpoints de sécurité
- 📝 `app/services/email.py` - Templates d'emails (vérification, reset)
- 📝 `RoadMap.md` - Mise à jour de la roadmap

---

## ❓ FAQ Rapide

**Q: Le rate limiting fonctionne sans Redis ?**
A: Oui, graceful degradation - si Redis n'est pas disponible, le rate limiting est désactivé.

**Q: Les emails sont envoyés automatiquement ?**
A: Oui, lors de l'inscription et de la demande de reset. Assurez-vous que SMTP est configuré.

**Q: Les anciens tokens restent valides ?**
A: Oui, les access tokens existants continuent de fonctionner. Le login retourne maintenant aussi un refresh token.

**Q: Comment tester la vérification d'email ?**
A: Regardez dans la base de données le champ `verification_token` de l'utilisateur créé, puis appelez `/verify-email` avec ce token.

**Q: Les mots de passe faibles sont rejetés ?**
A: Oui, lors de l'inscription ET de la réinitialisation. Testez avec "weak" → rejeté, "StrongPass123!" → accepté.

---

## 🎯 Prochaines Étapes

1. ✅ Tester toutes les nouvelles fonctionnalités
2. 📧 Configurer SMTP pour les emails en production
3. 🔍 Monitorer les logs de rate limiting
4. 📊 Implémenter l'historique des prix (prochaine feature)
5. 🧪 Ajouter des tests unitaires avec pytest

---

**Besoin d'aide ?** Consultez la [documentation complète](SECURITY_FEATURES.md)

**Dernière mise à jour** : 06/11/2025
