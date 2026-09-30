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
"""

import os

from dotenv import load_dotenv

load_dotenv()

PNAO_BASE_URL = os.getenv("PNAO_BASE_URL", "https://pnao.geomatika.fr/v6")
PNAO_USERNAME = os.getenv("PNAO_USERNAME")
PNAO_PASSWORD = os.getenv("PNAO_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")
DB_SCHEMA = os.getenv("PNAO_DB_SCHEMA", "pnao")
