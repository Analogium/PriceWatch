#!/bin/bash
# Script pour vider toutes les données de la base de données
# Les tables restent présentes, seules les données sont supprimées

set -e

echo "⚠️  ATTENTION: Vidage de la base de données"
echo "============================================================"
echo ""
echo "⚠️  Cela va SUPPRIMER toutes les données (les tables restent intactes)!"
echo ""

# Demander confirmation
read -p "Êtes-vous sûr de vouloir continuer? (oui/non): " confirmation

if [ "$confirmation" != "oui" ]; then
    echo "❌ Annulé"
    exit 0
fi

echo ""
echo "🔄 Vidage de toutes les tables..."

# Vider toutes les tables SAUF alembic_version
docker-compose exec -T db psql -U pricewatch -d pricewatch << 'EOF'
-- Vider les tables utilisateur (CASCADE pour gérer les clés étrangères)
TRUNCATE users CASCADE;
TRUNCATE products CASCADE;
TRUNCATE price_history CASCADE;

-- Note: On ne touche PAS à alembic_version pour garder le schéma intact
EOF

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du vidage des tables"
    exit 1
fi

echo ""
echo "✅ Toutes les données ont été supprimées"
echo ""
echo "📊 Vérification - Comptage des données:"

docker-compose exec -T db psql -U pricewatch -d pricewatch << 'EOF'
SELECT
    'users' as table_name,
    COUNT(*) as count
FROM users
UNION ALL
SELECT
    'products' as table_name,
    COUNT(*) as count
FROM products
UNION ALL
SELECT
    'price_history' as table_name,
    COUNT(*) as count
FROM price_history;
EOF

echo ""
echo "🎉 Terminé! La base de données est vide (tables intactes)."
