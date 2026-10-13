# Utilisation

## Configurer l'accès PNAO et la bdd

```bash
cp .env.sample .env
editor .env
```

Initialisation du schéma d'accueil des données dans la base de données

```bash
poetry run pnao upgradedb
```

Cette commande applique les migrations jusqu'à la dernière version avec
`DATABASE_URL`.

Si un message d'erreur indique que l'utilisateur doit être superuser pour créer l'extension postgis, vous pouvez soit configurer l'utilisateur postgresql en superuser (non recommandé!), soit créer l'extension avec un compte superuser (recommandé).

## Lancer le téléchargement

```bash
poetry run pnao fetch
```

### Générer une révision Alembic

Depuis la racine du projet :

```bash
poetry run alembic revision --autogenerate -m "description"
```

La comparaison utilise `PNAO_DB_SCHEMA` (par défaut `pnao`) et se limite aux
tables présentes dans les modèles SQLAlchemy. Les tables PostGIS et les tables
étrangères aux modèles ne produisent donc pas de suppressions. La suppression
d'une table retirée des modèles doit être écrite explicitement dans une révision.
Les opérations générées conservent un schéma explicite, même lorsque celui-ci
est le schéma par défaut de la connexion. Les révisions historiques ciblent
explicitement `pnao` ; changer `PNAO_DB_SCHEMA` ne les réécrit pas.
