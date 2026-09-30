from unittest.mock import Mock

import pytest

from pnao_client import cli


@pytest.fixture
def services(monkeypatch):
    api, db, downloader = Mock(), Mock(), Mock()
    monkeypatch.setattr(cli, "PnaoApiClient", api)
    monkeypatch.setattr(cli, "DatabaseClient", db)
    monkeypatch.setattr(cli, "PnaoDownloader", downloader)
    monkeypatch.setattr(cli, "PNAO_USERNAME", "alice")
    monkeypatch.setattr(cli, "PNAO_PASSWORD", "secret")
    return api, db, downloader


def test_fetch_runs_import(services, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["pnao", "fetch"])
    cli.main()
    api, db, downloader = services
    api.assert_called_once_with("alice", "secret")
    db.assert_called_once_with()
    downloader.assert_called_once_with(api.return_value, db.return_value)
    downloader.return_value.fetch_all.assert_called_once_with()
    assert "Import terminé" in capsys.readouterr().out


@pytest.mark.parametrize("args, code", [([], None), (["--help"], 0), (["invalid"], 2)])
def test_help_and_invalid_commands_do_not_initialize_services(
    services, monkeypatch, capsys, args, code
):
    monkeypatch.setattr("sys.argv", ["pnao", *args])
    if code is None:
        cli.main()
    else:
        with pytest.raises(SystemExit) as exc:
            cli.main()
        assert exc.value.code == code
    output = capsys.readouterr()
    assert "usage:" in output.out + output.err
    for service in services:
        service.assert_not_called()


def test_failed_import_does_not_report_success(services, monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["pnao", "fetch"])
    services[2].return_value.fetch_all.side_effect = RuntimeError("import failed")
    with pytest.raises(RuntimeError, match="import failed"):
        cli.main()
    assert "Import terminé" not in capsys.readouterr().out
