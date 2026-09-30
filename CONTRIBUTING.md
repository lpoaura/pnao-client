
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
