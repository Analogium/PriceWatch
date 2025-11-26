#!/bin/bash
# Script pour exécuter les outils de linting et formatting pour le Frontend

set -e

echo "🔍 PriceWatch Frontend - Analyse de la qualité du code"
echo "====================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

exit_code=0

# ESLint (linting)
echo -e "${BLUE}▶ Analyse du code avec ESLint...${NC}"
if npm run lint 2>/dev/null; then
    echo -e "${GREEN}✓ ESLint: Aucun problème détecté${NC}"
else
    echo -e "${RED}✗ ESLint: Problèmes détectés${NC}"
    echo -e "${YELLOW}  Exécutez: npm run lint:fix${NC}"
    exit_code=1
fi
echo ""

# Prettier (formatting)
echo -e "${BLUE}▶ Vérification du formatage avec Prettier...${NC}"
if npm run format:check 2>/dev/null; then
    echo -e "${GREEN}✓ Prettier: Code correctement formaté${NC}"
else
    echo -e "${YELLOW}⚠ Prettier: Certains fichiers nécessitent un formatage${NC}"
    echo -e "${YELLOW}  Exécutez: npm run format${NC}"
    exit_code=1
fi
echo ""

# TypeScript (type checking)
echo -e "${BLUE}▶ Vérification des types avec TypeScript...${NC}"
if npm run type-check 2>/dev/null; then
    echo -e "${GREEN}✓ TypeScript: Types corrects${NC}"
else
    echo -e "${RED}✗ TypeScript: Erreurs de typage détectées${NC}"
    exit_code=1
fi
echo ""

echo "====================================================="

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les checks de qualité ont réussi!${NC}"
else
    echo -e "${YELLOW}⚠️  Certains checks ont échoué (voir ci-dessus)${NC}"
fi

exit $exit_code
