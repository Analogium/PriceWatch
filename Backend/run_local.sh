#!/bin/bash

# Script pour lancer le backend en local (sans Docker)

echo "🚀 Démarrage de PriceWatch Backend (mode local)"

# Vérifier si le virtual environment existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé. Copie de .env.example..."
    cp .env.example .env
    echo "⚙️  Veuillez éditer le fichier .env avec vos configurations."
fi

# Lancer le serveur
echo "✅ Démarrage du serveur FastAPI sur http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
