from unittest.mock import Mock, call

import pytest

from pnao_client.api import PnaoApiClient
from pnao_client.database import DatabaseClient
from pnao_client.downloader import PnaoDownloader


@pytest.mark.parametrize(
    "areas",
    [
        [],
        [{"code_aire": "A1", "id": 1}],
        [{"code_aire": "A1"}, {"code_aire": "A2"}],
    ],
)
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
    api.export_zsm_coeur.return_value = [{"code_aire": "A1"}, {"code_aire": "A2"}]
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
        db.insert.assert_called_once_with("zsm_coeur", {"code_aire": "A1"})
    api.export_zsm_tampon.assert_not_called()


@pytest.mark.parametrize("export", [{"code_aire": "A1"}, "not-a-list", 42])
def test_fetch_all_rejects_export_that_is_not_a_list(export):
    api, db = Mock(spec=PnaoApiClient), Mock(spec=DatabaseClient)
    api.export_zsm_coeur.return_value = export

    with pytest.raises(ValueError, match="une liste"):
        PnaoDownloader(api, db).fetch_all()

    db.insert.assert_not_called()
    api.export_zsm_tampon.assert_not_called()


@pytest.mark.parametrize(
    "area", ["A1", {"id": 1}, {"code_aire": ""}, {"code_aire": None}, 42]
)
def test_fetch_all_rejects_area_without_code_aire(area):
    api, db = Mock(spec=PnaoApiClient), Mock(spec=DatabaseClient)
    api.export_zsm_coeur.return_value = [{"code_aire": "A0"}, area]

    with pytest.raises(ValueError, match="code_aire"):
        PnaoDownloader(api, db).fetch_all()

    # L'export entier est validé avant la moindre insertion.
    db.insert.assert_not_called()
