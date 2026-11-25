import runpy
from unittest.mock import patch

import pytest

from pnao_client import config


@pytest.mark.parametrize(
    "environment",
    [
        {},
        {
            "PNAO_BASE_URL": "https://custom.example",
            "PNAO_USERNAME": "alice",
            "PNAO_PASSWORD": "secret",
            "DATABASE_URL": "postgresql://custom/db",
            "PNAO_DB_SCHEMA": "custom_schema",
        },
        {"PNAO_DB_SCHEMA": "_A9"},
    ],
)
def test_configuration_reads_environment_and_defaults(environment):
    with (
        patch.dict("os.environ", environment, clear=True),
        patch("dotenv.load_dotenv") as load_dotenv,
    ):
        settings = runpy.run_path(config.__file__)

    load_dotenv.assert_called_once_with()
    assert settings["PNAO_BASE_URL"] == environment.get(
        "PNAO_BASE_URL", "https://pnao.geomatika.fr/v6"
    )
    assert settings["DB_SCHEMA"] == environment.get("PNAO_DB_SCHEMA", "pnao")
    for name in ("PNAO_USERNAME", "PNAO_PASSWORD", "DATABASE_URL"):
        assert settings[name] == environment.get(name)


@pytest.mark.parametrize(
    "schema",
    [
        "pnao; DROP TABLE raw_data; --",
        "pnao schema",
        "1schema",
        "schéma",
        "",
        "a" * 64,
    ],
)
def test_configuration_rejects_invalid_db_schema(schema):
    with (
        patch.dict("os.environ", {"PNAO_DB_SCHEMA": schema}, clear=True),
        patch("dotenv.load_dotenv"),
        pytest.raises(ValueError, match="PNAO_DB_SCHEMA"),
    ):
        runpy.run_path(config.__file__)
