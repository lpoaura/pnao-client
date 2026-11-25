"""Configuration chargée à l'import depuis l'environnement et un fichier ``.env``.

``load_dotenv`` complète l'environnement sans remplacer les variables déjà
présentes. Les valeurs sont lues une seule fois à l'import du module.

.. data:: PNAO_BASE_URL

   URL de base de l'API, par défaut ``https://pnao.geomatika.fr/v6``.

.. data:: PNAO_USERNAME

   Identifiant PNAO, ou ``None`` si la variable est absente.

.. data:: PNAO_PASSWORD

   Mot de passe PNAO, ou ``None`` si la variable est absente.

.. data:: DATABASE_URL

   URL de connexion SQLAlchemy, ou ``None`` si la variable est absente.

.. data:: DB_SCHEMA

   Schéma PostgreSQL lu depuis ``PNAO_DB_SCHEMA``, par défaut ``pnao``.
   La valeur est validée à l'import : elle doit être un identifiant SQL
   simple (lettres, chiffres, ``_``, commençant par une lettre ou ``_``,
   63 caractères maximum), sinon un :exc:`ValueError` est levé. Cette
   validation protège l'interpolation du schéma dans les ordres SQL
   (``CREATE SCHEMA``) contre toute injection.
"""

import os
import re

from dotenv import load_dotenv

load_dotenv()

PNAO_BASE_URL = os.getenv("PNAO_BASE_URL", "https://pnao.geomatika.fr/v6")
PNAO_USERNAME = os.getenv("PNAO_USERNAME")
PNAO_PASSWORD = os.getenv("PNAO_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")
DB_SCHEMA = os.getenv("PNAO_DB_SCHEMA", "pnao")

# Identifiant PostgreSQL valide : 63 octets max, sans caractère spécial.
_SCHEMA_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]{0,62}")
if not _SCHEMA_PATTERN.fullmatch(DB_SCHEMA):
    raise ValueError(
        f"PNAO_DB_SCHEMA doit être un identifiant SQL simple "
        f"(lettres, chiffres, '_', 63 caractères max), reçu : {DB_SCHEMA!r}"
    )
