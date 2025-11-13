# 🧪 Testing Infrastructure - PriceWatch Backend

## 📋 Vue d'ensemble

Ce document décrit l'infrastructure de tests mise en place pour le backend PriceWatch. **Tous les tests sont maintenant des tests unitaires utilisant pytest avec mocks**, garantissant une exécution rapide et fiable sans dépendances externes.

---

## 📊 Statistiques des Tests

### Tests Unitaires avec Pytest et Mocks
- **Total**: 63 tests unitaires ✅
- **Scraper Service**: 17 tests (86% coverage) ✅
- **Email Service**: 13 tests (100% coverage) ✅
- **Price History Service**: 13 tests (100% coverage) ✅
- **Celery Tasks**: 11 tests (100% pass rate) ✅
- **Security Functions**: 9 tests (password validation, tokens, hashing) ✅
- **Taux de réussite**: 100% (63/63) ✅

### Anciens Tests d'Intégration (optionnels, scripts Python avec serveur réel)
- **test_api.py**: Tests de base de l'API (6 tests) - pour tests end-to-end manuels
- **test_security.py**: Tests des fonctionnalités de sécurité (7 tests) - pour tests end-to-end manuels
- **test_price_history.py**: Tests de l'historique des prix (8 tests) - pour tests end-to-end manuels
- **test_pagination.py**: Tests de pagination, filtrage et tri (8 tests) - pour tests end-to-end manuels
- **Note**: Ces tests nécessitent un serveur lancé et ne font pas partie de la suite de tests automatisés

### Coverage Global
- **Services Core**: 100% coverage (email: 100%, price_history: 100%, scraper: 86%)
- **Models**: 100% coverage
- **Schemas**: 100% coverage
- **Config**: 100% coverage
- **Security**: 83% coverage
- **Total du projet**: 70% (incluant endpoints, core, main)

---

## 🏗️ Structure des Tests

```
Backend/
├── tests/
│   ├── test_unit_scraper.py           # Tests unitaires scraper (pytest + mocks) ✅
│   ├── test_unit_email.py             # Tests unitaires email (pytest + mocks) ✅
│   ├── test_unit_price_history.py     # Tests unitaires price_history (pytest + mocks) ✅
│   ├── test_unit_celery_tasks.py      # Tests unitaires Celery (pytest + mocks) ✅
│   ├── test_unit_security.py          # Tests unitaires security (pytest + mocks) ✅
│   ├── test_api.py                    # [Optionnel] Scripts end-to-end API
│   ├── test_security.py               # [Optionnel] Scripts end-to-end sécurité
│   ├── test_price_history.py          # [Optionnel] Scripts end-to-end historique
│   └── test_pagination.py             # [Optionnel] Scripts end-to-end pagination
├── pytest.ini                          # Configuration pytest
├── .flake8                             # Configuration flake8
├── pyproject.toml                      # Configuration black, isort, mypy
├── run_unit_tests.sh                   # Script tests unitaires (pytest)
├── run_all_tests.sh                    # Script tous les tests
└── run_linting.sh                      # Script qualité de code
```

---

## 🚀 Lancer les Tests

### Tests Unitaires avec Coverage

```bash
cd Backend

# Via script (recommandé)
./run_unit_tests.sh

# Via Docker (meilleure isolation)
docker-compose exec backend python3 -m pytest tests/ -v --cov=app --cov-report=term-missing -m unit

# Tests spécifiques
docker-compose exec backend python3 -m pytest tests/test_unit_scraper.py -v -m unit
```

### Tests d'Intégration

```bash
cd Backend

# Tous les tests d'intégration
./run_tests.sh

# Test spécifique
python3 tests/test_security.py
python3 tests/test_pagination.py
```

### Tous les Tests

```bash
cd Backend

# Unitaires + Intégration
./run_all_tests.sh
```

---

## 🔍 Qualité de Code

### Linting et Formatting

```bash
cd Backend

# Vérifier tout
./run_linting.sh

# Black (formatage)
python3 -m black app/ tasks.py

# Flake8 (linting)
python3 -m flake8 app/ tasks.py

# isort (organisation imports)
python3 -m isort app/ tasks.py

# MyPy (vérification types)
python3 -m mypy app/
```

### Standards de Qualité

- **Line Length**: 120 caractères (black, flake8)
- **Import Order**: PEP8 + black profile (isort)
- **Type Hints**: Recommandé mais pas obligatoire (mypy)

---

## 📝 Markers Pytest

Les tests utilisent des markers pour une exécution sélective:

```python
@pytest.mark.unit          # Tests unitaires
@pytest.mark.integration   # Tests d'intégration
@pytest.mark.scraper       # Tests du scraper
@pytest.mark.email         # Tests du service email
@pytest.mark.celery        # Tests des tâches Celery
@pytest.mark.slow          # Tests lents
```

### Utilisation des Markers

```bash
# Tous les tests unitaires
pytest -m unit

# Tous les tests du scraper
pytest -m scraper

# Tests unitaires du scraper
pytest -m "unit and scraper"

# Exclure les tests lents
pytest -m "not slow"
```

---

## 🧪 Tests Unitaires - Détails

### Scraper Service (17 tests) ✅

**Couverture**: 86%
**Statut**: Tous les tests passent

Tests inclus:
- Initialisation du scraper
- Scraping Amazon (succès, échec, variations de prix)
- Scraping Fnac (succès, échec)
- Scraping Darty (succès, échec)
- Scraping générique (meta tags)
- Gestion des erreurs (timeout, HTTP errors, HTML invalide)
- Singleton pattern

**Fichier**: [tests/test_unit_scraper.py](../tests/test_unit_scraper.py)

### Email Service (13 tests) ✅

**Couverture**: 100%
**Statut**: Tous les tests passent

Tests inclus:
- Initialisation du service
- Envoi d'alertes de prix (contenu, calculs)
- Envoi d'emails de vérification
- Envoi d'emails de réinitialisation de mot de passe
- Gestion des erreurs SMTP
- Sécurité (STARTTLS)
- Envois multiples

**Fichier**: [tests/test_unit_email.py](../tests/test_unit_email.py)

### Price History Service (13 tests) ✅

**Couverture**: 100%
**Statut**: Tous les tests passent

Tests inclus:
- Enregistrement de prix
- Récupération de l'historique (avec/sans limite)
- Calcul de statistiques (min, max, moyenne)
- Pourcentage de changement
- Vérification si enregistrement nécessaire
- Gestion des cas vides
- Singleton pattern

**Fichier**: [tests/test_unit_price_history.py](../tests/test_unit_price_history.py)

### Celery Tasks (11 tests) ✅

**Statut**: Tous les tests passent

Tests inclus:
- check_all_prices (succès, erreurs, alertes)
- check_single_product (succès, erreurs, alertes)
- Enregistrement de l'historique des prix
- Gestion des produits non trouvés
- Gestion des échecs de scraping
- Session database management

**Fichier**: [tests/test_unit_celery_tasks.py](../tests/test_unit_celery_tasks.py)

### Security Functions (9 tests) ✅

**Statut**: Tous les tests passent

Tests inclus:
- Validation de la force des mots de passe (6 tests)
- Création et décodage de tokens JWT
- Hachage et vérification des mots de passe
- Gestion des tokens invalides

**Fichier**: [tests/test_unit_security.py](../tests/test_unit_security.py)

---

## 📈 Coverage Reports

### Générer un Rapport HTML

```bash
cd Backend
docker-compose exec backend python3 -m pytest tests/ --cov=app --cov-report=html -m unit
```

Le rapport sera disponible dans `htmlcov/index.html`

### Générer un Rapport XML (CI/CD)

```bash
docker-compose exec backend python3 -m pytest tests/ --cov=app --cov-report=xml -m unit
```

### Configuration Coverage

Fichier `pytest.ini`:
```ini
[coverage:run]
source = app
omit =
    */tests/*
    */migrations/*
    */__pycache__/*
    */venv/*

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
```

---

## 🛠️ Outils de Test

### Dépendances

```
pytest==7.4.4              # Framework de test
pytest-asyncio==0.23.3     # Support async
pytest-cov==4.1.0          # Coverage
pytest-mock==3.12.0        # Mocking
responses==0.24.1          # HTTP mocking
httpx==0.26.0              # Client HTTP pour tests
```

### Dépendances de Qualité

```
black==24.1.1              # Formatage automatique
flake8==7.0.0              # Linting
mypy==1.8.0                # Type checking
isort==5.13.2              # Import sorting
```

---

## 🎯 Bonnes Pratiques

### Écriture de Tests

1. **Isolation**: Chaque test doit être indépendant
2. **Mocking**: Utiliser des mocks pour les dépendances externes
3. **Arrange-Act-Assert**: Structurer les tests clairement
4. **Nommage**: Noms descriptifs (`test_function_scenario_expected`)
5. **Documentation**: Docstrings pour tests complexes

### Exemple de Test

```python
@pytest.mark.unit
@pytest.mark.scraper
def test_scrape_product_amazon_url(self, mock_get):
    """Test scrape_product with Amazon URL."""
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<html>...</html>"
    mock_get.return_value = mock_response

    # Act
    result = self.scraper.scrape_product("https://www.amazon.fr/product")

    # Assert
    assert result is not None
    assert result.name == "Product Name"
    assert result.price == 99.99
    mock_get.assert_called_once()
```

---

## 🔄 Intégration Continue (CI/CD)

### Recommandations GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Unit Tests
        run: |
          docker-compose up -d
          docker-compose exec -T backend pytest tests/ -v --cov=app --cov-report=xml -m unit

      - name: Run Linting
        run: |
          docker-compose exec -T backend python3 -m black --check app/
          docker-compose exec -T backend python3 -m flake8 app/

      - name: Upload Coverage
        uses: codecov/codecov-action@v2
```

---

## 📚 Ressources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Black Code Style](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)

---

**Dernière mise à jour**: 13/11/2025
