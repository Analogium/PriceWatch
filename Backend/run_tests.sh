#!/bin/bash
# Script pour exécuter tous les tests du backend

set -e

echo "🧪 PriceWatch - Exécution des tests"
echo "===================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour exécuter un test
run_test() {
    local test_file=$1
    local test_name=$2

    echo -e "${BLUE}▶ Exécution: ${test_name}${NC}"
    echo "------------------------------------"

    if python3 "tests/${test_file}"; then
        echo -e "${GREEN}✓ ${test_name} - SUCCÈS${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ ${test_name} - ÉCHEC${NC}"
        echo ""
        return 1
    fi
}

# Compteurs
total_tests=0
passed_tests=0
failed_tests=0

# Tests disponibles
tests=(
    "test_api.py:Tests API de base"
    "test_security.py:Tests de sécurité"
    "test_price_history.py:Tests historique des prix"
)

# Exécuter tous les tests
for test_entry in "${tests[@]}"; do
    IFS=':' read -r test_file test_name <<< "$test_entry"

    total_tests=$((total_tests + 1))

    if run_test "$test_file" "$test_name"; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
done

# Résumé
echo "===================================="
echo "📊 RÉSUMÉ DES TESTS"
echo "===================================="
echo "Total: $total_tests"
echo -e "${GREEN}Réussis: $passed_tests${NC}"
if [ $failed_tests -gt 0 ]; then
    echo -e "${RED}Échoués: $failed_tests${NC}"
else
    echo "Échoués: $failed_tests"
fi
echo ""

# Code de sortie
if [ $failed_tests -gt 0 ]; then
    echo -e "${RED}❌ Certains tests ont échoué${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Tous les tests ont réussi!${NC}"
    exit 0
fi
