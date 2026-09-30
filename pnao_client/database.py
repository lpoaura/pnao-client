from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from .config import DATABASE_URL, DB_SCHEMA
from .models import PnaoRawData


class DatabaseClient:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)

    def ensure_schema(self):
        with self.engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DB_SCHEMA}"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    def insert(self, source, payload):
        with Session(self.engine) as s:
            s.add(PnaoRawData(source=source, payload=payload))
            s.commit()
