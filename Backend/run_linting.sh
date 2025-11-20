#!/bin/bash
# Script pour exécuter les outils de linting et formatting
# docker-compose exec -T backend /app/run_linting.sh 2>&1


set -e

echo "🔍 PriceWatch - Analyse de la qualité du code"
echo "=============================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

exit_code=0

# Black (formatting)
echo -e "${BLUE}▶ Vérification du formatage avec Black...${NC}"
if python3 -m black --check app/ tasks.py 2>/dev/null; then
    echo -e "${GREEN}✓ Black: Code correctement formaté${NC}"
else
    echo -e "${YELLOW}⚠ Black: Certains fichiers nécessitent un formatage${NC}"
    echo -e "${YELLOW}  Exécutez: python3 -m black app/ tasks.py${NC}"
    exit_code=1
fi
echo ""

# Flake8 (linting)
echo -e "${BLUE}▶ Analyse du code avec Flake8...${NC}"
if python3 -m flake8 app/ tasks.py 2>/dev/null; then
    echo -e "${GREEN}✓ Flake8: Aucun problème détecté${NC}"
else
    echo -e "${RED}✗ Flake8: Problèmes de style détectés${NC}"
    exit_code=1
fi
echo ""

# isort (import sorting)
echo -e "${BLUE}▶ Vérification de l'ordre des imports avec isort...${NC}"
if python3 -m isort --check-only app/ tasks.py 2>/dev/null; then
    echo -e "${GREEN}✓ isort: Imports correctement ordonnés${NC}"
else
    echo -e "${YELLOW}⚠ isort: Certains imports nécessitent un réordonnancement${NC}"
    echo -e "${YELLOW}  Exécutez: python3 -m isort app/ tasks.py${NC}"
    exit_code=1
fi
echo ""

# MyPy (type checking)
echo -e "${BLUE}▶ Vérification des types avec MyPy...${NC}"
if python3 -m mypy app/ 2>/dev/null; then
    echo -e "${GREEN}✓ MyPy: Types corrects${NC}"
else
    echo -e "${YELLOW}⚠ MyPy: Avertissements de typage détectés${NC}"
    # Don't fail on mypy warnings for now
fi
echo ""

echo "=============================================="

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les checks de qualité ont réussi!${NC}"
else
    echo -e "${YELLOW}⚠️  Certains checks ont échoué (voir ci-dessus)${NC}"
fi

exit $exit_code
