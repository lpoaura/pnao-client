
# Contribuer

Merci pour votre intérêt !

## Règles
- Python >= 3.12
- Poetry obligatoire
- Tests requis pour toute PR

## Tests

Les tests unitaires sont dans `tests/`. Ils simulent les appels HTTP et les
sessions SQLAlchemy : aucun serveur PNAO, PostgreSQL ou fichier `.env` personnel
n’est nécessaire. Ils couvrent l’authentification, les exports, la persistance,
la CLI, la configuration et le schéma SQL PostgreSQL généré.

```bash
poetry run pytest --cov=pnao_client --cov-branch --cov-report=term-missing
```

## Qualité du code

Installer les dépendances de développement avec `poetry install --with dev`.
Ruff assure le lint, le tri des imports et le formatage :

```bash
poetry run ruff check --fix .
poetry run ruff format .
```

Pour vérifier le code sans le modifier (comme en CI) :

```bash
poetry run ruff check .
poetry run ruff format --check .
```

## Intégration continue

- `ci.yml` vérifie Ruff et le verrouillage Poetry, lance les tests sous différentes versions de Python
  avec un seuil de couverture de 100 %, puis construit et
  vérifie la wheel et l’archive source. La CLI installée depuis la wheel est
  testée hors du dépôt. Les rapports et archives sont conservés comme artefacts.
- `docs.yml` construit Sphinx sans avertissements sur les PR et sur main ; seul
  un push sur main déploie la documentation sur GitHub Pages.
- `release.yml` publie sur un tag stable `X.Y.Z`, après validation de la CI et
  de la documentation. Voir `RELEASE_CHECKLIST.md` pour la configuration initiale.

Pour vérifier la documentation localement :

```bash
poetry install --with docs
poetry run sphinx-build -b html -W --keep-going docs/source docs/_build/html
```
