#!/bin/bash
# Script pour exécuter les tests unitaires avec couverture de code

set -e

echo "🧪 PriceWatch - Exécution des tests unitaires avec couverture"
echo "=============================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}▶ Installation des dépendances de test...${NC}"
pip install -q pytest pytest-cov pytest-mock pytest-asyncio responses

echo ""
echo -e "${BLUE}▶ Exécution des tests unitaires avec couverture...${NC}"
echo "------------------------------------------------------------"

# Run pytest with coverage
python3 -m pytest tests/test_unit_*.py -v \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-fail-under=80 \
    -m unit

exit_code=$?

echo ""
echo "=============================================================="

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les tests unitaires ont réussi!${NC}"
    echo ""
    echo -e "${GREEN}📊 Rapport de couverture généré dans htmlcov/index.html${NC}"
    echo ""
else
    echo -e "${RED}❌ Certains tests ont échoué ou la couverture est insuffisante${NC}"
    echo ""
fi

exit $exit_code
