import runpy
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from sqlalchemy.dialects import postgresql


@pytest.mark.parametrize("offline", [False, True])
def test_schema_is_created_in_transaction_before_migrations(monkeypatch, offline):
    context = MagicMock()
    context.config.config_file_name = None
    context.is_offline_mode.return_value = offline
    events = []
    context.begin_transaction.return_value.__enter__.side_effect = lambda: (
        events.append("begin")
    )
    context.begin_transaction.return_value.__exit__.side_effect = lambda *args: (
        events.append("end")
    )
    context.execute.side_effect = lambda statement: events.append(
        str(statement.compile(dialect=postgresql.dialect()))
    )
    context.run_migrations.side_effect = lambda: events.append("migrate")
    monkeypatch.setattr("alembic.context", context)
    monkeypatch.setattr("sqlalchemy.engine_from_config", MagicMock())

    runpy.run_path(str(Path(__file__).resolve().parents[1] / "alembic/env.py"))

    assert events == [
        "begin",
        "CREATE SCHEMA IF NOT EXISTS pnao",
        "migrate",
        "end",
    ]
    assert context.configure.call_args.kwargs["version_table_schema"] == "pnao"
