import argparse

from .api import PnaoApiClient
from .config import PNAO_PASSWORD, PNAO_USERNAME
from .database import DatabaseClient
from .downloader import PnaoDownloader


def main():
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
