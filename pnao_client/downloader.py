"""Orchestration du téléchargement des exports PNAO vers PostgreSQL."""

from .api import PnaoApiClient
from .database import DatabaseClient


class PnaoDownloader:
    """Coordonner le téléchargement des exports et leur stockage en base.

    :param api: Client HTTP utilisé pour récupérer les exports PNAO.
    :type api: pnao_client.api.PnaoApiClient
    :param db: Client chargé de préparer la base et d'enregistrer les données.
    :type db: pnao_client.database.DatabaseClient
    """

    def __init__(self, api: PnaoApiClient, db: DatabaseClient):
        """Conserver les clients fournis sans lancer le téléchargement.

        :param api: Client HTTP PNAO.
        :param db: Client de persistance PostgreSQL.
        """
        self.api = api
        self.db = db

    def fetch_all(self):
        """Importer les ZSM cœur après préparation du schéma et de PostGIS.

        Récupère l'export cœur, puis insère chaque élément avec la source
        ``zsm_coeur``. L'export tampon n'est pas appelé car il est actuellement
        signalé comme désactivé.

        Les erreurs de préparation, de téléchargement et d'insertion sont
        propagées et interrompent l'import. Les insertions déjà validées restent
        en base ; relancer l'import peut donc créer des doublons.

        :returns: ``None``.
        """
        self.db.ensure_database_requirements()
        zsm_coeur = self.api.export_zsm_coeur()
        for area in zsm_coeur:
            self.db.insert("zsm_coeur", area)
        # NOTE : Buffer areas are actually disabled
        # zsm_tampon = self.api.export_zsm_tampon()
        # for area in zsm_tampon:
        #     self.db.insert("zsm_tampon", area)
