from unittest.mock import Mock, call

import pytest

from pnao_client.api import PnaoApiClient
from pnao_client.database import DatabaseClient
from pnao_client.downloader import PnaoDownloader


@pytest.mark.parametrize("areas", [[], [{"id": 1}], [{"id": 1}, {"id": 2}]])
def test_fetch_all_initializes_schema_and_imports_only_core_areas(areas):
    api, db = Mock(spec=PnaoApiClient), Mock(spec=DatabaseClient)
    api.export_zsm_coeur.return_value = areas
    events = Mock()
    events.attach_mock(api, "api")
    events.attach_mock(db, "db")

    PnaoDownloader(api, db).fetch_all()

    assert events.mock_calls == [
        call.db.ensure_database_requirements(),
        call.api.export_zsm_coeur(),
    ] + [call.db.insert("zsm_coeur", area) for area in areas]
    api.export_zsm_tampon.assert_not_called()


@pytest.mark.parametrize("failure", ["schema", "export", "insert"])
def test_fetch_all_stops_on_failure(failure):
    api, db = Mock(spec=PnaoApiClient), Mock(spec=DatabaseClient)
    api.export_zsm_coeur.return_value = [{"id": 1}, {"id": 2}]
    operation = {
        "schema": db.ensure_database_requirements,
        "export": api.export_zsm_coeur,
        "insert": db.insert,
    }[failure]
    operation.side_effect = RuntimeError("failed")

    with pytest.raises(RuntimeError, match="failed"):
        PnaoDownloader(api, db).fetch_all()

    if failure == "schema":
        api.export_zsm_coeur.assert_not_called()
    if failure != "insert":
        db.insert.assert_not_called()
    else:
        db.insert.assert_called_once_with("zsm_coeur", {"id": 1})
    api.export_zsm_tampon.assert_not_called()
