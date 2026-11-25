"""Accès HTTP aux exports PNAO avec gestion du jeton d'authentification."""

import json
import logging
import time

import requests

from .config import PNAO_BASE_URL

logger = logging.getLogger(__name__)

# Délai (connexion, lecture) en secondes : un serveur qui ne répond pas ne
# doit pas bloquer le client indéfiniment.
HTTP_TIMEOUT = (5, 30)
# Taille maximale d'un corps de réponse accepté (100 Mio) : protection contre
# une réponse anormalement volumineuse qui saturerait la mémoire.
MAX_RESPONSE_BYTES = 100 * 1024 * 1024


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

    def close(self):
        """Effacer les identifiants et le jeton conservés en mémoire.

        :returns: ``None``. Remplace les secrets par ``None``.
        """
        self.username = None
        self.password = None
        self.token = None
        self.expires_at = 0

    def __del__(self):
        self.close()

    @staticmethod
    def _decode_json(response):
        """Décoder le corps JSON d'une réponse en limitant la taille lue.

        Le corps est lu par morceaux via ``iter_content`` et la lecture
        est interrompue dès que :data:`MAX_RESPONSE_BYTES` est dépassé.

        :param response: Réponse ``requests`` ouverte en ``stream=True``.
        :returns: Contenu JSON décodé.
        :raises ValueError: Si le corps dépasse :data:`MAX_RESPONSE_BYTES`.
        :raises json.JSONDecodeError: Si le corps n'est pas un JSON valide.
        """
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                raise ValueError(
                    f"Réponse trop volumineuse : plus de {MAX_RESPONSE_BYTES} octets"
                )
            chunks.append(chunk)
        return json.loads(b"".join(chunks))

    def authenticate(self):
        """Obtenir un jeton et mettre à jour sa date d'expiration.

        Envoie les identifiants au service d'authentification. Le champ
        ``expires`` de la réponse est interprété comme une durée en secondes ;
        son absence entraîne l'utilisation d'une durée de 3 600 secondes.

        :returns: ``None``. Met à jour ``token`` et ``expires_at``.
        :raises requests.exceptions.HTTPError: Si le serveur renvoie une erreur
            HTTP.
        :raises requests.exceptions.ConnectionError: Si la connexion échoue.
        :raises requests.exceptions.Timeout: Si le délai :data:`HTTP_TIMEOUT`
            est dépassé.
        :raises json.JSONDecodeError: Si la réponse n'est pas un document JSON
            valide.
        :raises ValueError: Si la réponse dépasse :data:`MAX_RESPONSE_BYTES`.
        :raises KeyError: Si la réponse ne contient pas de champ ``token``.
        """
        json_load = {"username": self.username, "password": self.password}
        r = requests.post(
            f"{PNAO_BASE_URL}/v6/services/webservices/auth/0/",
            json=json_load,
            timeout=HTTP_TIMEOUT,
            stream=True,
        )
        r.raise_for_status()
        data = self._decode_json(r)
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
        :raises requests.exceptions.Timeout: Si le délai :data:`HTTP_TIMEOUT`
            est dépassé.
        :raises json.JSONDecodeError: Si la réponse n'est pas un document JSON
            valide.
        :raises ValueError: Si la réponse dépasse :data:`MAX_RESPONSE_BYTES`.
        """
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = f"{PNAO_BASE_URL}{endpoint}"
        logger.debug("Calling URL: %s", url)
        r = requests.get(
            url, headers=self._headers(), timeout=HTTP_TIMEOUT, stream=True
        )
        logger.debug("Status: %s", r.status_code)
        r.raise_for_status()
        return self._decode_json(r)

    def export_zsm_coeur(self):
        """Récupérer l'export des zones de sensibilité majeure (ZSM) cœur.

        :returns: Contenu JSON décodé du service ``export_zsm_coeur``.

        Les erreurs de :meth:`get` sont propagées à l'appelant.
        """
        logger.debug("ZSM Coeur")
        return self.get("/v6/services/webservices/data/0/export_zsm_coeur")

    def export_zsm_tampon(self):
        """Demander l'export des zones de sensibilité majeure (ZSM) tampon.

        Le service est actuellement signalé comme désactivé. Cette méthode
        effectue néanmoins la requête ; le téléchargement habituel via
        :meth:`~pnao_client.downloader.PnaoDownloader.fetch_all` ne l'appelle pas.

        :returns: Contenu JSON décodé du service ``export_zsm_tampon``.

        Les erreurs de :meth:`get` sont propagées à l'appelant.
        """
        logger.debug("ZSM Tampon")
        return self.get("/v6/services/webservices/data/0/export_zsm_tampon")
