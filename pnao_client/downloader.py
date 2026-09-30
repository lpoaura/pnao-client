from .api import PnaoApiClient
from .database import DatabaseClient


class PnaoDownloader:
    def __init__(self, api: PnaoApiClient, db: DatabaseClient):
        self.api = api
        self.db = db

    def fetch_all(self):
        self.db.ensure_schema()
        zsm_coeur = self.api.export_zsm_coeur()
        for area in zsm_coeur:
            self.db.insert("zsm_coeur", area)
        # NOTE : Buffer areas are actually disabled
        # zsm_tampon = self.api.export_zsm_tampon()
        # for area in zsm_tampon:
        #     self.db.insert("zsm_tampon", area)
