
# pnao-client

![CI](https://github.com/lpoaura/pnao-client/actions/workflows/ci.yml/badge.svg)
![Docs](https://github.com/lpoaura/pnao-client/actions/workflows/docs.yml/badge.svg)
![Release](https://github.com/lpoaura/pnao-client/actions/workflows/release.yml/badge.svg)

Client Python pour l’API **PNAO** avec :
- CLI `poetry run pnao fetch`
- Authentification JWT avec rafraîchissement
- Stockage PostgreSQL (JSONB + index GIN)
- Migrations Alembic
- Documentation Sphinx (Markdown)

## Installation
```bash
poetry install
```

## Commande principale

```bash
poetry run alembic upgrade head
```

Lancer le téléchargement des données depuis l'API

```bash
poetry run pnao fetch
```

## Documentation
La documentation HTML est publiée automatiquement sur GitHub Pages.

## Release
Voir `RELEASE_CHECKLIST.md`
