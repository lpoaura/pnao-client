"""Persistance des exports PNAO dans PostgreSQL via SQLAlchemy."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from .config import DATABASE_URL, DB_SCHEMA
from .models import PnaoRawData


class DatabaseClient:
    """Enregistrer les données brutes PNAO dans PostgreSQL.

    Le moteur SQLAlchemy utilise ``DATABASE_URL`` et les modèles ciblent le
    schéma défini par ``DB_SCHEMA``. Chaque insertion possède sa transaction.

    :ivar engine: Moteur SQLAlchemy utilisé pour les connexions et les sessions.
    """

    def __init__(self):
        """Créer le moteur à partir de ``DATABASE_URL`` sans ouvrir de connexion.

        Les erreurs de configuration de SQLAlchemy sont propagées à l'appelant.
        """
        self.engine = create_engine(DATABASE_URL)

    def ensure_database_requirements(self):
        """Créer le schéma de destination et activer PostGIS s'ils sont absents.

        Exécute les deux instructions dans une même transaction. Le compte
        PostgreSQL doit disposer des droits nécessaires. Les tables ne sont pas
        créées par cette méthode ; elles sont gérées par les migrations Alembic.

        :returns: ``None``.
        :raises sqlalchemy.exc.SQLAlchemyError: Si la connexion ou une
            instruction SQL échoue.
        """
        with self.engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    def insert(self, source, payload):
        """Insérer un enregistrement brut et valider sa transaction.

        Ouvre une session dédiée et la ferme même en cas d'erreur. Chaque appel
        ajoute une ligne, sans dédoublonnage ni mise à jour des lignes existantes.

        :param str source: Nom de l'export d'origine, limité à 50 caractères.
        :param dict payload: Données sérialisables en JSON à stocker en JSONB.
        :returns: ``None``.
        :raises sqlalchemy.exc.SQLAlchemyError: Si l'insertion ou la validation
            de la transaction échoue.
        """
        with Session(self.engine) as s:
            s.add(PnaoRawData(source=source, payload=payload))
            s.commit()
