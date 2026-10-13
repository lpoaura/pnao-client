"""Interface en ligne de commande pour importer les données PNAO."""

import argparse
from pathlib import Path

from alembic import command
from alembic.config import Config

from .api import PnaoApiClient
from .config import PNAO_PASSWORD, PNAO_USERNAME
from .database import DatabaseClient
from .downloader import PnaoDownloader


def upgrade_database():
    """Appliquer toutes les migrations à la base configurée par DATABASE_URL."""
    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).parent / "migrations").replace("%", "%%")
    )
    command.upgrade(config, "head")
    print("Base de données mise à jour")


def fetch_main():
    """Exécuter la commande d'import ``fetch``."""
    parser = argparse.ArgumentParser("fetch")
    parser.parse_args()
    fetch_data()


def fetch_data():
    """Importer les exports PNAO dans la base de données."""
    api = PnaoApiClient(PNAO_USERNAME, PNAO_PASSWORD)
    db = DatabaseClient()
    PnaoDownloader(api, db).fetch_all()
    print("Import terminé")


def main():
    """Exécuter la commande ``pnao`` à partir des arguments de la ligne de commande.

    La sous-commande ``fetch`` construit les clients avec la configuration de
    l'environnement, importe les exports pris en charge et affiche un message
    de fin. La sous-commande ``upgradedb`` applique les migrations Alembic.
    Sans sous-commande, affiche l'aide.

    Les erreurs des clients et du téléchargement sont propagées à l'appelant.

    :returns: ``None``.
    :raises SystemExit: Si l'aide est demandée ou si les arguments sont invalides.
    """
    parser = argparse.ArgumentParser("pnao")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("fetch")
    sub.add_parser("upgradedb", help="Appliquer les migrations de la base de données")

    args = parser.parse_args()

    if args.cmd == "fetch":
        fetch_data()
    elif args.cmd == "upgradedb":
        upgrade_database()
    else:
        parser.print_help()
