# 🏷️ PriceWatch — Suivi intelligent de prix en ligne

## 📘 Description

**PriceWatch** est une application web SaaS permettant aux utilisateurs de **surveiller le prix de produits en ligne** (Amazon, Fnac, Darty, etc.) et de recevoir une **alerte automatique** lorsque le prix passe sous un seuil défini.

L’objectif : **simplifier la veille de prix** pour les consommateurs et e-commerçants sans avoir à vérifier manuellement les sites chaque jour.

---

## 🚀 Stack Technique

### 🖥️ Frontend
- **Framework** : React 18 + Vite  
- **Langage** : TypeScript  
- **UI Library** : Tailwind CSS *(ou Material UI)*  
- **State Management** : Zustand *(léger et moderne)*  
- **Charts** : Recharts *(pour l’historique des prix)*  
- **Auth** : JWT (stocké dans localStorage)

### 🧠 Backend
- **Framework** : FastAPI  
- **Langage** : Python 3.12  
- **ORM** : SQLAlchemy  
- **Base de données** : PostgreSQL *(ou SQLite pour le MVP)*  
- **Authentification** : JWT avec `fastapi-jwt-auth`  
- **Scraping** : `requests` + `BeautifulSoup` *(et éventuellement `playwright` pour sites dynamiques)*  
- **Tâches planifiées** : `Celery` + `Redis` *(ou `cron` simple en MVP)*  
- **Notifications** : Email via `smtplib` ou SendGrid API  
- **Conteneurisation** : Docker + Docker Compose

---

## 🗂️ Architecture du projet

pricewatch/
├── backend/
│
├── frontend/
│
└── docker-compose.yml

---

## 📋 Fonctionnalités attendues

### MVP (Phase 1)
- [x] Inscription / connexion utilisateur (JWT)
- [x] Ajout d’un produit à surveiller via URL
- [x] Extraction automatique du **titre**, **image** et **prix actuel**
- [x] Stockage des données par utilisateur
- [x] Vérification quotidienne des prix (via tâche planifiée)
- [x] Envoi d’un email si le prix ≤ seuil cible
- [x] Tableau de bord utilisateur affichant :
  - Liste des produits suivis  
  - Prix actuel  
  - Seuil cible  
  - Dernière vérification  

---

## 🧮 Modèle de données

### User
| Champ | Type | Description |
|--------|------|-------------|
| id | int | Identifiant unique |
| email | string | Adresse email unique |
| password_hash | string | Mot de passe haché |
| created_at | datetime | Date d’inscription |

### Product
| Champ | Type | Description |
|--------|------|-------------|
| id | int | Identifiant produit |
| user_id | int (FK → users.id) | Propriétaire |
| name | string | Nom du produit |
| url | string | Lien d’origine |
| image | string | URL image miniature |
| current_price | float | Dernier prix connu |
| target_price | float | Seuil de notification |
| last_checked | datetime | Dernière vérification |
| created_at | datetime | Date d’ajout |

---

## ⚙️ API REST

### 🔐 Authentification
| Méthode | Route | Description |
|----------|--------|-------------|
| `POST /auth/register` | Crée un compte utilisateur |
| `POST /auth/login` | Retourne un JWT |
| `GET /auth/me` | Renvoie les infos du compte connecté |

### 📦 Produits
| Méthode | Route | Description |
|----------|--------|-------------|
| `GET /products` | Liste les produits suivis par l’utilisateur |
| `POST /products` | Ajoute un produit à suivre |
| `PUT /products/{id}` | Met à jour un produit (seuil, nom…) |
| `DELETE /products/{id}` | Supprime un produit |
| `POST /products/check` | Force une vérification manuelle du prix |

---

## 🔄 Workflow utilisateur

1. L’utilisateur crée un compte et se connecte  
2. Il colle une **URL produit** à surveiller  
3. Le backend récupère :
   - Nom du produit  
   - Image miniature  
   - Prix actuel  
4. L’utilisateur définit un **prix cible**  
5. Un job quotidien vérifie le prix :
   - Si le prix baisse sous le seuil → email envoyé  
6. L’utilisateur peut visualiser tous ses suivis dans le tableau de bord

---

## 📧 Exemple de notification email

> **Objet : 🔔 Baisse de prix détectée !**  
>
> Bonjour 👋  
> Le produit **Écran LG 27UL500 4K** vient de passer à **249,00 €** (ancien prix : 289,99 €).  
>
> 👉 [Voir le produit sur Amazon](https://www.amazon.fr/dp/B0C5VCBLXX)

---

## 💸 Monétisation (idées futures)
| Plan | Prix | Fonctionnalités |
|------|------|----------------|
| **Free** | 0€ | 5 produits, vérif quotidienne |
| **Pro** | 4.99€/mois | 50 produits, vérif toutes les 6h |
| **Business** | 14.99€/mois | 500 produits, export CSV, comparaison concurrentielle |

---

## 🧩 Outils Dev & Environnement

- **Backend** :  
  - `uvicorn` pour le serveur  
  - `alembic` pour les migrations  
  - `.env` pour la configuration (DB_URL, JWT_SECRET, etc.)

- **Frontend** :  
  - `axios` pour les requêtes API  
  - `react-router-dom` pour la navigation  
  - `dotenv` pour gérer les URLs d’API

- **Tests** :  
  - Backend : `pytest`  
  - Frontend : `vitest` + `react-testing-library`

---

## 🧭 Objectif final

Un SaaS léger, utile et automatisé :  
- **Facile à utiliser**  
- **Économe en ressources** (pas d’IA coûteuse)  
- **Basé sur une valeur réelle pour les utilisateurs**

> PriceWatch : *surveillez les prix, pas vos onglets.*

---
