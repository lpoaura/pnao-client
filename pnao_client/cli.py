"""Interface en ligne de commande pour importer les données PNAO."""

import argparse

from .api import PnaoApiClient
from .config import PNAO_PASSWORD, PNAO_USERNAME
from .database import DatabaseClient
from .downloader import PnaoDownloader


def main():
    """Exécuter la commande ``pnao`` à partir des arguments de la ligne de commande.

    La sous-commande ``fetch`` construit les clients avec la configuration de
    l'environnement, importe les exports pris en charge et affiche un message
    de fin. Sans sous-commande, affiche l'aide.

    Les erreurs des clients et du téléchargement sont propagées à l'appelant.

    :returns: ``None``.
    :raises SystemExit: Si l'aide est demandée ou si les arguments sont invalides.
    """
    parser = argparse.ArgumentParser("pnao")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("fetch")

    args = parser.parse_args()

    if args.cmd == "fetch":
        api = PnaoApiClient(PNAO_USERNAME, PNAO_PASSWORD)
        db = DatabaseClient()
        PnaoDownloader(api, db).fetch_all()
        print("Import terminé")
    else:
        parser.print_help()
