
# Contribuer

Merci pour votre intérêt !

## Règles
- Python >= 3.12
- Poetry obligatoire
- Tests requis pour toute PR

## Tests
```bash
poetry run pytest --cov=pnao_client
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
