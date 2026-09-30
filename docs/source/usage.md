# Utilisation

## Configurer l'accès PNAO et la bdd

```bash
cp .env.sample .env
editor .env
```

Initialisation du schéma d'accueil des données dans la base de données

```bash
poetry run alembic upgrade head
```

Si un message d'erreur indique que l'utilisateur doit être superuser pour créer l'extension postgis, vous pouvez soit configurer l'utilisateur postgresql en superuser (non recommandé!), soit créer l'extension avec un compte superuser (recommandé).

## Lancer le téléchargement

```bash
poetry run pnao fetch
```