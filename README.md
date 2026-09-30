
# pnao-client

![CI](https://github.com/lpoaura/pnao-client/actions/workflows/ci.yml/badge.svg)
![Docs](https://github.com/lpoaura/pnao-client/actions/workflows/docs.yml/badge.svg)
![Release](https://github.com/lpoaura/pnao-client/actions/workflows/release.yml/badge.svg)

Le gypaète barbu est l'une des espèces d'oiseaux les plus menacées en Europe. À ce titre, il bénéficie d'un plan national d'actions, avec la création de « ZSM » : Zones de Sensibilité Majeure dans différents massifs.

Cette application est un client pour l'application GeoMatika qui permet le téléchargement de ces zones de sensibilité majeure pour les injecter dans une base de données PostgreSQL/PostGIS.

<img height="100" src="docs/source/_static/pnao2biodivsports.svg">


## Installation

### Installer la commande

```bash
poetry install
```

### Configurer l'accès PNAO et la bdd

```bash
cp .env.sample .env
editor .env
```

Initialisation du schéma d'accueil des données dans la base de données

```bash
poetry run alembic upgrade head
```

Si un message d'erreur indique que l'utilisateur doit être superuser pour créer l'extension postgis, vous pouvez soit configurer l'utilisateur postgresql en superuser (non recommandé!), soit créer l'extension avec un compte superuser (recommandé).

Lancer le téléchargement des données depuis l'API

```bash
poetry run pnao fetch
```

## Documentation
La documentation HTML est publiée automatiquement sur GitHub Pages.

## Release

Voir `RELEASE_CHECKLIST.md`

## Equipe

<a href="">
<img height="100px" src="https://auvergne-rhone-alpes.lpo.fr/wp-content/uploads/LPO_AuRA.svg" title="DREAL AuRA">
</a>

[@lpofredc](https://github.com/lpofredc/) ([LPO Auvergne-Rhône-Alpes](https://github.com/lpoaura/)), lead developer

---

<a href="https://github.com/lpoaura/pnao-client/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=lpoaura/pnao-client" />
</a>

---