
import logging
import time, requests
from .config import PNAO_BASE_URL

logger = logging.getLogger(__name__)

class PnaoApiClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.expires_at = 0

    def authenticate(self):
        r = requests.post(
            f"{PNAO_BASE_URL}/v6/services/webservices/auth/0/",
            json={"username": self.username, "password": self.password},
        )
        r.raise_for_status()
        data = r.json()
        self.token = data["token"]
        self.expires_at = time.time() + data.get("expires", 3600)

    def _headers(self):
        if not self.token or time.time() > self.expires_at - 30:
            self.authenticate()
        return {"Authorization": f"Bearer {self.token}"}

    def get(self, endpoint):
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = f"{PNAO_BASE_URL}{endpoint}"
        print("Calling URL:", url)
        r = requests.get(url, headers=self._headers())
        print("Status:", r.status_code)
        r.raise_for_status()
        return r.json()

    def export_zsm_coeur(self):
        print("ZSM Coeur")
        return self.get("/v6/services/webservices/data/0/export_zsm_coeur")

    def export_zsm_tampon(self):
        print("ZSM Tampon")
        return self.get("/v6/services/webservices/data/0/export_zsm_tampon")
