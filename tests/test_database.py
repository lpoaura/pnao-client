from unittest.mock import MagicMock, Mock

import pytest

from pnao_client import database
from pnao_client.models import PnaoRawData


@pytest.fixture
def client(monkeypatch):
    engine = MagicMock()
    create_engine = Mock(return_value=engine)
    monkeypatch.setattr(database, "create_engine", create_engine)
    monkeypatch.setattr(database, "DATABASE_URL", "postgresql://example/test")
    client = database.DatabaseClient()
    create_engine.assert_called_once_with("postgresql://example/test")
    return client


def test_ensure_schema_uses_transaction(client, monkeypatch):
    monkeypatch.setattr(database, "DB_SCHEMA", "unit_test")
    client.ensure_schema()
    client.engine.begin.assert_called_once_with()
    connection = client.engine.begin.return_value.__enter__.return_value
    assert [str(call.args[0]) for call in connection.execute.call_args_list] == [
        "CREATE SCHEMA IF NOT EXISTS unit_test",
        "CREATE EXTENSION IF NOT EXISTS postgis",
    ]
    client.engine.begin.return_value.__exit__.assert_called_once_with(None, None, None)


def test_insert_persists_payload_and_commits(client, monkeypatch):
    session_factory = MagicMock()
    monkeypatch.setattr(database, "Session", session_factory)
    session = session_factory.return_value.__enter__.return_value
    payload = {"id": 3, "geometry": {"type": "Point", "coordinates": [1, 2]}}

    client.insert("zsm_coeur", payload)

    session_factory.assert_called_once_with(client.engine)
    record = session.add.call_args.args[0]
    assert isinstance(record, PnaoRawData)
    assert record.source == "zsm_coeur"
    assert record.payload == payload
    assert [call[0] for call in session.mock_calls] == ["add", "commit"]
    session_factory.return_value.__exit__.assert_called_once_with(None, None, None)


def test_commit_failure_propagates_and_closes_session(client, monkeypatch):
    session_factory = MagicMock()
    monkeypatch.setattr(database, "Session", session_factory)
    session = session_factory.return_value.__enter__.return_value
    error = RuntimeError("commit failed")
    session.commit.side_effect = error

    with pytest.raises(RuntimeError, match="commit failed"):
        client.insert("zsm_coeur", {"id": 1})

    exit_args = session_factory.return_value.__exit__.call_args.args
    assert exit_args[0] is RuntimeError
    assert exit_args[1] is error
