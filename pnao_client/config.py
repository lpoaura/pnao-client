
import os
from dotenv import load_dotenv
load_dotenv()

PNAO_BASE_URL = os.getenv("PNAO_BASE_URL", "https://pnao.geomatika.fr/v6")
PNAO_USERNAME = os.getenv("PNAO_USERNAME")
PNAO_PASSWORD = os.getenv("PNAO_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")
DB_SCHEMA = os.getenv("PNAO_DB_SCHEMA", "pnao")
