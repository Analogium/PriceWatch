# Tâche : Passer les jobs Celery à une fréquence horaire

## 🎯 Objectif

Améliorer la précision des vérifications de prix en passant les jobs Celery Beat d'une fréquence de 6h/12h/24h à une **vérification horaire** pour tous les jobs.

## 📋 Contexte

**Problème actuel** : Les produits sont vérifiés avec un délai imprécis à cause des cycles fixes de Celery Beat.
- Exemple : Un produit créé à 20:00 avec fréquence 6h sera vérifié ~7-18h après sa création au lieu de 6h pile

**Solution** : Lancer les jobs toutes les heures. Le filtre `last_checked` dans le code garantit qu'on vérifie uniquement les produits éligibles, donc **pas de surcharge de scraping**.

## 📊 Impact attendu

| Fréquence produit | Avant | Après | Amélioration |
|-------------------|-------|-------|--------------|
| 6h | 6h à 12h | 6h à 7h | ✅ Précision +83% |
| 12h | 12h à 24h | 12h à 13h | ✅ Précision +92% |
| 24h | 24h à 48h | 24h à 25h | ✅ Précision +96% |

**Note importante** : Le nombre total de vérifications reste identique grâce au filtre temporel dans `check_prices_by_frequency()`.

---

## 🔧 Instructions d'implémentation

### Étape 1 : Modifier la configuration Celery Beat

**Fichier à modifier** : `/home/lambert/apps/PriceWatch/Backend/tasks.py`

**Localisation** : Lignes 391-407 (section `celery_app.conf.beat_schedule`)

**Modification à effectuer** :

```python
# AVANT (configuration actuelle)
celery_app.conf.beat_schedule = {
    "check-prices-6h": {
        "task": "check_prices_by_frequency",
        "schedule": 21600.0,  # Run every 6 hours (in seconds)
        "args": (6,),  # Check products with 6h frequency
    },
    "check-prices-12h": {
        "task": "check_prices_by_frequency",
        "schedule": 43200.0,  # Run every 12 hours (in seconds)
        "args": (12,),  # Check products with 12h frequency
    },
    "check-prices-24h": {
        "task": "check_prices_by_frequency",
        "schedule": 86400.0,  # Run every 24 hours (in seconds)
        "args": (24,),  # Check products with 24h frequency
    },
}

# APRÈS (nouvelle configuration horaire)
celery_app.conf.beat_schedule = {
    "check-prices-6h": {
        "task": "check_prices_by_frequency",
        "schedule": 3600.0,  # Run every 1 hour (in seconds) - improved precision
        "args": (6,),  # Check products with 6h frequency
    },
    "check-prices-12h": {
        "task": "check_prices_by_frequency",
        "schedule": 3600.0,  # Run every 1 hour (in seconds) - improved precision
        "args": (12,),  # Check products with 12h frequency
    },
    "check-prices-24h": {
        "task": "check_prices_by_frequency",
        "schedule": 3600.0,  # Run every 1 hour (in seconds) - improved precision
        "args": (24,),  # Check products with 24h frequency
    },
}
```

**Action concrète** : Utiliser l'outil `Edit` pour remplacer uniquement les valeurs `schedule:` en gardant tout le reste identique.

---

### Étape 2 : Reconstruire et redémarrer les containers

**Commandes à exécuter** :

```bash
# Se placer dans le répertoire apps
cd /home/lambert/apps

# Reconstruire les images (pour inclure le code modifié)
docker compose build pricewatch-backend pricewatch-celery-worker pricewatch-celery-beat

# Redémarrer les services
docker compose up -d pricewatch-backend pricewatch-celery-worker pricewatch-celery-beat

# Attendre 30 secondes pour que tout démarre
sleep 30
```

---

### Étape 3 : Vérifier que tout fonctionne

**Vérifications à faire** :

1. **Vérifier que les containers sont healthy** :
```bash
docker ps --filter "name=pricewatch" --format "table {{.Names}}\t{{.Status}}"
```

Résultat attendu : Tous les containers doivent avoir le statut `(healthy)`

2. **Vérifier les logs de Celery Beat** :
```bash
docker logs pricewatch_celery_beat --tail 50
```

Chercher : `beat: Starting...` (doit être récent)

3. **Vérifier la nouvelle configuration** :
```bash
docker exec pricewatch_celery_beat python3 -c "from tasks import celery_app; import json; schedule = {k: {'schedule': str(v['schedule']), 'task': v['task']} for k, v in celery_app.conf.beat_schedule.items()}; print(json.dumps(schedule, indent=2))"
```

Résultat attendu :
```json
{
  "check-prices-6h": {
    "schedule": "3600.0",
    "task": "check_prices_by_frequency"
  },
  "check-prices-12h": {
    "schedule": "3600.0",
    "task": "check_prices_by_frequency"
  },
  "check-prices-24h": {
    "schedule": "3600.0",
    "task": "check_prices_by_frequency"
  }
}
```

4. **Attendre et vérifier qu'un job s'exécute** :

Attendre jusqu'à la prochaine heure ronde (ex: si il est 15:43, attendre jusqu'à 16:00), puis :

```bash
docker logs pricewatch_celery_worker --tail 100 | grep "Starting price check"
```

Vous devriez voir des logs indiquant que les tâches s'exécutent.

---

## ✅ Critères de succès

- [ ] Le fichier `tasks.py` a été modifié avec les nouvelles valeurs `schedule: 3600.0`
- [ ] Les containers ont été reconstruits et redémarrés
- [ ] Tous les containers pricewatch sont `(healthy)`
- [ ] La commande de vérification de config affiche `"schedule": "3600.0"` pour les 3 jobs
- [ ] Au bout d'une heure, des jobs se sont exécutés (visible dans les logs)

---

## 🔄 Rollback (si problème)

Si quelque chose ne fonctionne pas, revenir à l'ancienne configuration :

```python
celery_app.conf.beat_schedule = {
    "check-prices-6h": {
        "task": "check_prices_by_frequency",
        "schedule": 21600.0,  # Revenir à 6h
        "args": (6,),
    },
    "check-prices-12h": {
        "task": "check_prices_by_frequency",
        "schedule": 43200.0,  # Revenir à 12h
        "args": (12,),
    },
    "check-prices-24h": {
        "task": "check_prices_by_frequency",
        "schedule": 86400.0,  # Revenir à 24h
        "args": (24,),
    },
}
```

Puis reconstruire et redémarrer.

---

## 📝 Notes importantes

1. **Pas d'impact sur le nombre de scraping** : Le filtre `last_checked` garantit qu'on vérifie uniquement les produits éligibles. Le nombre total de vérifications reste le même.

2. **Meilleure répartition de la charge** : Au lieu d'avoir des pics de vérification toutes les 6h, la charge est répartie sur chaque heure.

3. **Précision améliorée** : Les produits seront vérifiés beaucoup plus proche de leur fréquence cible (±1h au lieu de ±6h).

4. **Celerybeat-schedule** : Le fichier `celerybeat-schedule` dans le container sera automatiquement mis à jour avec la nouvelle configuration.

---

## 🎯 Résumé de la tâche

1. Éditer `/home/lambert/apps/PriceWatch/Backend/tasks.py` : Changer les 3 valeurs `schedule:` à `3600.0`
2. Exécuter : `docker compose build pricewatch-backend pricewatch-celery-worker pricewatch-celery-beat`
3. Exécuter : `docker compose up -d pricewatch-backend pricewatch-celery-worker pricewatch-celery-beat`
4. Vérifier que tout fonctionne avec les commandes de l'Étape 3

**Temps estimé** : 5-10 minutes

**Complexité** : Faible (modification simple, infrastructure déjà en place)
