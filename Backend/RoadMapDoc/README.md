# 📚 Documentation Backend - PriceWatch

Bienvenue dans la documentation du backend PriceWatch !

## 📂 Structure de la Documentation

### 📖 Documents Principaux

1. **[../RoadMap.md](../RoadMap.md)**
   - Vue d'ensemble complète du projet
   - État d'avancement de toutes les fonctionnalités
   - Roadmap des versions futures
   - Notes techniques et architecture

2. **[SECURITY_FEATURES.md](SECURITY_FEATURES.md)**
   - Documentation détaillée des fonctionnalités de sécurité
   - Configuration et usage de chaque feature
   - Schémas de base de données
   - Bonnes pratiques de sécurité

3. **[QUICKSTART_SECURITY.md](QUICKSTART_SECURITY.md)**
   - Guide de démarrage rapide
   - Exemples de curl pour tester
   - Configuration minimale requise
   - FAQ et troubleshooting

---

## 🎯 Par où commencer ?

### Pour développeurs nouveaux sur le projet
👉 Lisez d'abord [../RoadMap.md](../RoadMap.md) pour comprendre l'architecture globale

### Pour tester les nouvelles fonctionnalités de sécurité
👉 Consultez [QUICKSTART_SECURITY.md](QUICKSTART_SECURITY.md) et lancez les tests

### Pour implémenter de nouvelles features
👉 Référez-vous à [SECURITY_FEATURES.md](SECURITY_FEATURES.md) comme exemple de documentation

---

## 🚀 Démarrage Rapide

```bash
# 1. Cloner et installer
cd Backend
pip install -r requirements.txt

# 2. Configurer l'environnement
cp .env.example .env
# Modifier .env avec vos paramètres

# 3. Lancer le backend
uvicorn app.main:app --reload

# 4. Tester les fonctionnalités
./run_tests.sh
```

---

## 📋 Checklist pour Contribuer

Avant de créer une Pull Request :

- [ ] Le code respecte les standards Python (PEP 8)
- [ ] Les nouvelles fonctionnalités sont documentées
- [ ] Les tests passent (`python test_security.py`)
- [ ] Le RoadMap.md est mis à jour si nécessaire
- [ ] Les variables d'environnement sont documentées
- [ ] Les nouvelles routes sont listées dans la documentation

---

## 🔗 Liens Utiles

### Documentation Externe
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/docs/)

### Sécurité
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)

---

## 📝 Conventions de Documentation

### Pour ajouter une nouvelle fonctionnalité

1. **Implémenter le code** avec commentaires clairs
2. **Ajouter des tests** dans `test_*.py`
3. **Mettre à jour RoadMap.md** :
   - Cocher ✅ dans "Fonctionnalités Implémentées"
   - Décocher dans "Fonctionnalités à Implémenter"
4. **Créer une documentation détaillée** (optionnel pour features majeures)
5. **Mettre à jour ce README** si nécessaire

### Format de Documentation

```markdown
# Titre de la Feature

## Vue d'ensemble
Description courte de ce que fait la feature

## Configuration
Variables d'environnement nécessaires

## Usage
Exemples de code / API calls

## Tests
Comment tester la feature

## Notes Techniques
Détails d'implémentation importants
```

---

## 🏗️ Architecture du Backend

```
Backend/
├── app/
│   ├── api/
│   │   ├── endpoints/     # Routes API
│   │   └── dependencies.py # Dépendances (auth, DB)
│   ├── core/
│   │   ├── config.py      # Configuration
│   │   ├── security.py    # Fonctions de sécurité
│   │   └── rate_limit.py  # Rate limiting
│   ├── db/
│   │   └── base.py        # Configuration DB
│   ├── models/            # Modèles SQLAlchemy
│   ├── schemas/           # Schémas Pydantic
│   ├── services/          # Services métier
│   └── main.py            # Point d'entrée FastAPI
├── RoadMapDoc/            # 📚 Cette documentation
│   ├── README.md          # Ce fichier
│   ├── SECURITY_FEATURES.md
│   └── QUICKSTART_SECURITY.md
├── test_security.py       # Tests de sécurité
├── run_tests.sh           # Script de test
├── RoadMap.md             # Roadmap principale
└── requirements.txt       # Dépendances Python
```

---

## 🧪 Tests

### Lancer tous les tests
```bash
./run_tests.sh
```

### Tester une fonctionnalité spécifique
```bash
# Voir test_security.py pour exemples
python test_security.py
```

### Coverage (à implémenter)
```bash
pytest --cov=app tests/
```

---

## 🤝 Contribution

### Workflow recommandé

1. Créer une branche feature : `git checkout -b feature/nom-feature`
2. Implémenter la fonctionnalité
3. Tester localement
4. Documenter
5. Commit avec message descriptif
6. Push et créer une PR

### Style de Code

- **Python** : PEP 8
- **Imports** : Ordre alphabétique par catégorie
- **Docstrings** : Format Google style
- **Type hints** : Obligatoires pour fonctions publiques

---

## 📞 Support

### En cas de problème

1. Consultez la FAQ dans [QUICKSTART_SECURITY.md](QUICKSTART_SECURITY.md)
2. Vérifiez les logs du backend
3. Assurez-vous que Redis est actif
4. Vérifiez la configuration `.env`

### Signaler un bug

Incluez dans votre rapport :
- Description du problème
- Étapes pour reproduire
- Logs d'erreur
- Environnement (OS, Python version, etc.)

---

## 📅 Historique des Versions

### Version 1.1 - Sécurité Avancée (06/11/2025)
- ✨ Refresh tokens
- ✨ Rate limiting
- ✨ Vérification d'email
- ✨ Réinitialisation de mot de passe
- ✨ Politique de mots de passe forts
- 📚 Documentation complète

### Version 1.0 - MVP (Date initiale)
- ✅ Authentification JWT
- ✅ CRUD Produits
- ✅ Web Scraping
- ✅ Tâches Celery
- ✅ Notifications Email

---

**Maintenu par** : Équipe PriceWatch
**Dernière mise à jour** : 06/11/2025
