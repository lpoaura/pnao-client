# Checklist de release

## Configuration initiale

- Dans GitHub, **Settings → Pages → Build and deployment**, sélectionner **GitHub Actions**.
- Créer l’environnement GitHub `pypi` et limiter ses déploiements aux tags `v*`.
- Dans PyPI, configurer un **Trusted Publisher** (ou un pending publisher pour une
  première publication) : propriétaire `lpoaura`, dépôt `pnao-client`, workflow
  `release.yml`, environnement `pypi`. Aucun secret PyPI n’est nécessaire.
- Protéger `main` avec les contrôles `Quality`, `Tests (Python 3.12)`,
  `Tests (Python 3.13)`, `Tests (Python 3.14)`, `Build` et `Documentation build`.
- Restreindre la création, modification et suppression des tags `X.Y.Z` aux responsables
  des releases via un ruleset GitHub.

## Publier une version stable

- [ ] Mettre à jour CHANGELOG.md et la version dans pyproject.toml.
- [ ] Fusionner les changements sur main après validation de la CI et de la documentation.
- [ ] Créer et pousser le tag `X.Y.Z` sur le commit validé. Le tag doit correspondre
      exactement à la version du paquet ; les préversions ne sont pas prises en charge.
- [ ] Vérifier le workflow Release : il relance la CI et Sphinx sur le tag, publie
      les archives validées sur PyPI, puis crée la GitHub Release avec ces archives.
- [ ] Vérifier PyPI et les notes générées de la GitHub Release.
- [ ] Vérifier GitHub Pages, qui présente la documentation courante de main.

Une version publiée sur PyPI ne peut pas être remplacée. Si seule la création de
la GitHub Release échoue après publication, relancer uniquement les jobs échoués.
