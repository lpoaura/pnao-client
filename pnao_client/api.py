"""Accès HTTP aux exports PNAO avec gestion du jeton d'authentification."""

import logging
import time

import requests

from .config import PNAO_BASE_URL

logger = logging.getLogger(__name__)


class PnaoApiClient:
    """Client HTTP de l'API PNAO avec authentification par jeton Bearer.

    Les requêtes utilisent l'URL de base définie par ``PNAO_BASE_URL``.
    L'authentification est effectuée lors de la première requête, puis renouvelée
    lorsque le jeton expire dans moins de 30 secondes.

    :param str username: Identifiant du compte PNAO.
    :param str password: Mot de passe du compte PNAO.
    :ivar token: Jeton d'accès courant, ou ``None`` avant l'authentification.
    :ivar expires_at: Date d'expiration du jeton en secondes depuis l'époque Unix.
    """

    def __init__(self, username, password):
        """Conserver les identifiants sans effectuer de requête réseau.

        :param str username: Identifiant du compte PNAO.
        :param str password: Mot de passe du compte PNAO.
        """
        self.username = username
        self.password = password
        self.token = None
        self.expires_at = 0

    def authenticate(self):
        """Obtenir un jeton et mettre à jour sa date d'expiration.

        Envoie les identifiants au service d'authentification. Le champ
        ``expires`` de la réponse est interprété comme une durée en secondes ;
        son absence entraîne l'utilisation d'une durée de 3 600 secondes.

        :returns: ``None``. Met à jour ``token`` et ``expires_at``.
        :raises requests.exceptions.HTTPError: Si le serveur renvoie une erreur
            HTTP.
        :raises requests.exceptions.ConnectionError: Si la connexion échoue.
        :raises requests.exceptions.JSONDecodeError: Si la réponse n'est pas un
            document JSON valide.
        :raises KeyError: Si la réponse ne contient pas de champ ``token``.
        """
        json_load = {"username": self.username, "password": self.password}
        r = requests.post(
            f"{PNAO_BASE_URL}/v6/services/webservices/auth/0/",
            json=json_load,
        )
        r.raise_for_status()
        data = r.json()
        self.token = data["token"]
        self.expires_at = time.time() + data.get("expires", 3600)

    def _headers(self):
        """Construire l'en-tête d'autorisation avec un jeton à jour.

        Appelle :meth:`authenticate` si le jeton est absent ou expire dans moins
        de 30 secondes, et propage les erreurs d'authentification.

        :returns: En-tête ``Authorization`` contenant le jeton Bearer.
        :rtype: dict[str, str]
        """
        if not self.token or time.time() > self.expires_at - 30:
            self.authenticate()
        return {"Authorization": f"Bearer {self.token}"}

    def get(self, endpoint):
        """Effectuer une requête GET authentifiée et décoder la réponse JSON.

        Renouvelle le jeton si nécessaire avant l'envoi de la requête.
        Les erreurs d'authentification sont propagées à l'appelant.

        :param str endpoint: Chemin à ajouter à ``PNAO_BASE_URL``. Un ``/`` initial
            est ajouté s'il est absent.
        :returns: Contenu JSON décodé, sans transformation ni validation de son
            schéma ; son type dépend de la réponse du service.
        :raises requests.exceptions.HTTPError: Si le serveur renvoie une erreur
            HTTP.
        :raises requests.exceptions.ConnectionError: Si la connexion échoue.
        :raises requests.exceptions.JSONDecodeError: Si la réponse n'est pas un
            document JSON valide.
        """
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = f"{PNAO_BASE_URL}{endpoint}"
        print("Calling URL:", url)
        r = requests.get(url, headers=self._headers())
        print("Status:", r.status_code)
        r.raise_for_status()
        return r.json()

    def export_zsm_coeur(self):
        """Récupérer l'export des zones de sensibilité majeure (ZSM) cœur.

        :returns: Contenu JSON décodé du service ``export_zsm_coeur``.

        Les erreurs de :meth:`get` sont propagées à l'appelant.
        """
        print("ZSM Coeur")
        return self.get("/v6/services/webservices/data/0/export_zsm_coeur")

    def export_zsm_tampon(self):
        """Demander l'export des zones de sensibilité majeure (ZSM) tampon.

        Le service est actuellement signalé comme désactivé. Cette méthode
        effectue néanmoins la requête ; le téléchargement habituel via
        :meth:`~pnao_client.downloader.PnaoDownloader.fetch_all` ne l'appelle pas.

        :returns: Contenu JSON décodé du service ``export_zsm_tampon``.

        Les erreurs de :meth:`get` sont propagées à l'appelant.
        """
        print("ZSM Tampon")
        return self.get("/v6/services/webservices/data/0/export_zsm_tampon")
