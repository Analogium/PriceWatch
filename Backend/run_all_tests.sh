#!/bin/bash
# Script pour exécuter tous les tests (unitaires + intégration)

set -e

echo "🧪 PriceWatch - Exécution de tous les tests"
echo "============================================"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

exit_code=0

# Tests unitaires
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  TESTS UNITAIRES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

python3 -m pytest tests/test_unit_*.py -v --cov=app --cov-report=term-missing --cov-fail-under=80 -m unit

if [ $? -ne 0 ]; then
    exit_code=1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  TESTS D'INTÉGRATION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Tests d'intégration
for test_file in tests/test_api.py tests/test_security.py tests/test_price_history.py tests/test_pagination.py; do
    if [ -f "$test_file" ]; then
        test_name=$(basename $test_file .py)
        echo -e "${BLUE}▶ Exécution: $test_name${NC}"
        python3 "$test_file"
        if [ $? -ne 0 ]; then
            exit_code=1
        fi
        echo ""
    fi
done

echo ""
echo "============================================"

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les tests ont réussi!${NC}"
    echo ""
    echo -e "${GREEN}📊 Rapport de couverture: htmlcov/index.html${NC}"
else
    echo -e "${RED}❌ Certains tests ont échoué${NC}"
fi

exit $exit_code
