from unittest.mock import patch

import pytest

# Keep collection independent of the developer's .env and credentials.
with (
    patch("dotenv.load_dotenv"),
    patch.dict(
        "os.environ",
        {
            "PNAO_BASE_URL": "https://pnao.example",
            "PNAO_USERNAME": "test-user",
            "PNAO_PASSWORD": "test-password",
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "PNAO_DB_SCHEMA": "pnao_test",
        },
    ),
):
    from pnao_client import config  # noqa: F401


@pytest.fixture(autouse=True)
def block_external_services(monkeypatch):
    def unexpected_call(*args, **kwargs):
        pytest.fail("Unit tests must not access HTTP services or PostgreSQL")

    monkeypatch.setattr("requests.sessions.Session.request", unexpected_call)
    monkeypatch.setattr("psycopg2.connect", unexpected_call)
