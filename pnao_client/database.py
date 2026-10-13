"""Persistance des exports PNAO dans PostgreSQL via SQLAlchemy."""

from sqlalchemy import create_engine, text,func
from sqlalchemy.dialects.postgresql import insert
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
        """Insérer ou mettre à jour un enregistrement brut et valider sa transaction.

        Ouvre une session dédiée et la ferme même en cas d'erreur. Chaque appel
        ajoute une ligne ou met à jour source et payload si code_aire existe déjà.

        :param str source: Nom de l'export d'origine, limité à 50 caractères.
        :param dict payload: Données sérialisables en JSON à stocker en JSONB.
        :returns: ``None``.
        :raises sqlalchemy.exc.SQLAlchemyError: Si l'insertion ou la validation
            de la transaction échoue.
        """
        statement = insert(PnaoRawData).values(
            source=source, payload=payload, code_aire=payload["code_aire"]
        )
        statement = statement.on_conflict_do_update(
            index_elements=[PnaoRawData.code_aire],
            set_={
                "source": statement.excluded.source,
                "payload": statement.excluded.payload,
                "updated_at": func.now()
            },
        )
        with Session(self.engine) as s:
            s.execute(statement)
            s.commit()
