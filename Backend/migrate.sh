#!/bin/bash
# Script de migration automatique pour PriceWatch

set -e  # Arrêter en cas d'erreur

echo "🔄 PriceWatch - Migration automatique de la base de données"
echo "============================================================"
echo ""

# Vérifier si un message de migration est fourni
if [ -z "$1" ]; then
    echo "❌ Erreur: Veuillez fournir un message de migration"
    echo ""
    echo "Usage: ./migrate.sh \"message_de_migration\""
    echo "Exemple: ./migrate.sh \"add user fields\""
    exit 1
fi

MESSAGE="$1"

echo "📝 Message de migration: $MESSAGE"
echo ""

# Générer la migration
echo "🔍 Génération de la migration..."
docker-compose exec -T backend alembic revision --autogenerate -m "$MESSAGE"

if [ $? -ne 0 ]; then
    echo "❌ Échec de la génération de la migration"
    exit 1
fi

echo "✅ Migration générée avec succès"
echo ""

# Appliquer la migration
echo "⬆️  Application de la migration..."
docker-compose exec -T backend alembic upgrade head

if [ $? -ne 0 ]; then
    echo "❌ Échec de l'application de la migration"
    exit 1
fi

echo ""
echo "✅ Migration appliquée avec succès!"
echo ""
echo "📊 État actuel de la base de données:"
docker-compose exec -T backend alembic current

echo ""
echo "🎉 Terminé!"
