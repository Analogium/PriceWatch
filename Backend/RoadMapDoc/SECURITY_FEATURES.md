# 🔒 Security Features Documentation

## Vue d'ensemble

Ce document décrit toutes les fonctionnalités de sécurité implémentées dans PriceWatch Backend.

---

## 🎯 Fonctionnalités Implémentées

### 1. Refresh Tokens

**Fichier**: [app/core/security.py](../app/core/security.py:58-64)

Les refresh tokens permettent de renouveler les access tokens expirés sans redemander les identifiants.

**Avantages**:
- Access tokens courts (30 min) pour limiter l'exposition
- Refresh tokens longs (7 jours) pour une meilleure UX
- Les tokens incluent un champ `type` pour distinguer access/refresh

**Usage**:
```python
# Login retourne maintenant access_token + refresh_token
POST /api/v1/auth/login
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}

# Réponse
{
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
}

# Rafraîchir le token
POST /api/v1/auth/refresh
{
    "refresh_token": "eyJ..."
}
```

---

### 2. Politique de Mots de Passe Forts

**Fichier**: [app/core/security.py](../app/core/security.py:22-42)

Validation stricte des mots de passe lors de l'inscription et de la réinitialisation.

**Règles configurables** (dans `.env`):
- `MIN_PASSWORD_LENGTH`: Longueur minimale (défaut: 8)
- `REQUIRE_UPPERCASE`: Au moins une majuscule (défaut: true)
- `REQUIRE_LOWERCASE`: Au moins une minuscule (défaut: true)
- `REQUIRE_DIGIT`: Au moins un chiffre (défaut: true)
- `REQUIRE_SPECIAL_CHAR`: Au moins un caractère spécial (défaut: true)

**Exemple de validation**:
```python
# Mot de passe faible
"weakpass" → Rejeté (pas de majuscule, pas de chiffre, pas de spécial)

# Mot de passe fort
"SecurePass123!" → Accepté ✓
```

---

### 3. Rate Limiting

**Fichier**: [app/core/rate_limit.py](../app/core/rate_limit.py)

Protection contre les attaques par force brute et abus.

**Configuration** (dans `.env`):
- `RATE_LIMIT_REQUESTS`: Nombre de requêtes autorisées (défaut: 100)
- `RATE_LIMIT_PERIOD`: Période en secondes (défaut: 60)

**Fonctionnement**:
- Utilise Redis pour le comptage distribué
- Limite par IP (avec support X-Forwarded-For)
- Retourne HTTP 429 si limite dépassée
- Graceful degradation si Redis indisponible

**Appliqué sur**:
- `/auth/register`
- `/auth/login`
- `/auth/refresh`
- `/auth/forgot-password`
- `/auth/reset-password`

---

### 4. Vérification d'Email

**Fichiers**:
- [app/api/endpoints/auth.py](../app/api/endpoints/auth.py:166-186)
- [app/services/email.py](../app/services/email.py:48-78)

**Workflow**:
1. L'utilisateur s'inscrit
2. Un token de vérification unique est généré
3. Un email est envoyé avec un lien de vérification
4. L'utilisateur clique sur le lien
5. Le compte est activé

**Base de données**:
- `users.is_verified`: Boolean (défaut: false)
- `users.verification_token`: String (token unique)

**Endpoints**:
```python
# Inscription (génère et envoie le token)
POST /api/v1/auth/register

# Vérification
POST /api/v1/auth/verify-email
{
    "token": "abc123..."
}
```

---

### 5. Réinitialisation de Mot de Passe

**Fichiers**:
- [app/api/endpoints/auth.py](../app/api/endpoints/auth.py:189-257)
- [app/services/email.py](../app/services/email.py:80-112)

**Workflow sécurisé**:
1. L'utilisateur demande une réinitialisation
2. Un token est généré avec expiration (1h)
3. Email envoyé avec lien de réinitialisation
4. L'utilisateur clique et entre un nouveau mot de passe
5. Validation de la force du mot de passe
6. Mise à jour du mot de passe

**Sécurité**:
- Le token expire après 1 heure
- Pas de confirmation si l'email existe (anti-énumération)
- Validation du nouveau mot de passe
- Token supprimé après utilisation

**Base de données**:
- `users.reset_token`: String (token unique)
- `users.reset_token_expires`: DateTime

**Endpoints**:
```python
# Demande de réinitialisation
POST /api/v1/auth/forgot-password
{
    "email": "user@example.com"
}

# Réinitialisation
POST /api/v1/auth/reset-password
{
    "token": "reset_token_here",
    "new_password": "NewSecurePass123!"
}
```

---

## 🗄️ Modifications de la Base de Données

### Table `users` - Nouveaux champs

```sql
ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN verification_token VARCHAR;
ALTER TABLE users ADD COLUMN reset_token VARCHAR;
ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP;
```

**Migration automatique**: Les champs sont ajoutés automatiquement au démarrage si vous utilisez `Base.metadata.create_all()`.

---

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
# Sécurité
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
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

# Email (pour vérification et reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@pricewatch.com

# Redis (pour rate limiting et Celery)
REDIS_URL=redis://redis:6379/0
```

---

## 🧪 Tests

### Lancer les tests

```bash
# S'assurer que le backend est lancé
cd Backend
python test_security.py
```

### Tests couverts

1. ✅ Validation de force de mot de passe
2. ✅ Inscription avec vérification d'email
3. ✅ Login avec access + refresh tokens
4. ✅ Rate limiting
5. ✅ Flux de réinitialisation de mot de passe
6. ✅ Prévention des doublons d'email
7. ✅ Gestion des identifiants invalides

---

## 📋 API Endpoints Résumé

| Méthode | Endpoint | Description | Rate Limited |
|---------|----------|-------------|--------------|
| POST | `/auth/register` | Inscription + envoi email vérification | ✅ |
| POST | `/auth/login` | Connexion + tokens | ✅ |
| POST | `/auth/refresh` | Rafraîchir access token | ✅ |
| GET | `/auth/me` | Info utilisateur connecté | ❌ |
| POST | `/auth/verify-email` | Vérifier email | ❌ |
| POST | `/auth/forgot-password` | Demander réinit mot de passe | ✅ |
| POST | `/auth/reset-password` | Réinitialiser mot de passe | ✅ |

---

## 🔐 Bonnes Pratiques

### Pour les développeurs

1. **Toujours utiliser HTTPS en production**
2. **Changer SECRET_KEY en production** (générer avec `openssl rand -hex 32`)
3. **Configurer les CORS correctement** (pas de `*` en prod)
4. **Logger les tentatives échouées** pour détecter les attaques
5. **Monitorer les 429 (rate limit)** pour ajuster les limites

### Pour les utilisateurs

1. **Utiliser des mots de passe uniques**
2. **Activer la vérification d'email**
3. **Ne jamais partager les tokens**
4. **Se déconnecter sur machines publiques**

---

## 🚨 Sécurité Supplémentaire Recommandée

### À implémenter prochainement

- [ ] **2FA/MFA** (authentification à deux facteurs)
- [ ] **Session management** (révocation de tokens)
- [ ] **IP whitelisting** pour certaines opérations sensibles
- [ ] **Audit logs** des actions sensibles
- [ ] **CAPTCHA** sur login après X échecs
- [ ] **Device fingerprinting** pour détecter activités suspectes
- [ ] **Email sur connexion inhabituelle** (nouveau device/IP)

---

## 📚 Références

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

**Dernière mise à jour**: 06/11/2025
