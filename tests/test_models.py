from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from pnao_client.config import DB_SCHEMA
from pnao_client.models import PnaoRawData


def test_postgresql_table_preserves_json_and_timestamp_contract():
    table = PnaoRawData.__table__
    ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))

    assert table.schema == DB_SCHEMA
    assert "PRIMARY KEY (id)" in ddl
    assert "source VARCHAR(50) NOT NULL" in ddl
    assert "payload JSONB NOT NULL" in ddl
    assert "created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL" in ddl


def test_postgresql_indexes_support_source_and_json_queries():
    table = PnaoRawData.__table__
    indexes = {
        tuple(column.name for column in index.columns): str(
            CreateIndex(index).compile(dialect=postgresql.dialect())
        )
        for index in table.indexes
    }

    assert ("source",) in indexes
    assert "USING gin (payload)" in indexes[("payload",)]
