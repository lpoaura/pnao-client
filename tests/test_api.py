import json
from unittest.mock import Mock

import pytest
import requests

from pnao_client import api


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(api, "PNAO_BASE_URL", "https://pnao.example")
    monkeypatch.setattr(api.time, "time", lambda: 1000)
    return api.PnaoApiClient("alice", "secret")


def make_response(payload):
    """Construire une fausse réponse streamée avec un corps JSON."""
    body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    response = Mock()
    response.iter_content.return_value = [body]
    return response


@pytest.mark.parametrize("expiry, expected", [(None, 4600), (120, 1120)])
def test_authenticate(client, monkeypatch, expiry, expected):
    data = {"token": "new-token"}
    if expiry is not None:
        data["expires"] = expiry
    response = make_response(data)
    post = Mock(return_value=response)
    monkeypatch.setattr(api.requests, "post", post)

    client.authenticate()

    post.assert_called_once_with(
        "https://pnao.example/v6/services/webservices/auth/0/",
        json={"username": "alice", "password": "secret"},
        timeout=api.HTTP_TIMEOUT,
        stream=True,
    )
    response.raise_for_status.assert_called_once_with()
    assert client.token == "new-token"
    assert client.expires_at == expected


def test_authentication_failure_preserves_token(client, monkeypatch):
    client.token = "old-token"
    client.expires_at = 900
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError("unauthorized")
    monkeypatch.setattr(api.requests, "post", Mock(return_value=response))

    with pytest.raises(requests.HTTPError, match="unauthorized"):
        client.authenticate()

    response.iter_content.assert_not_called()
    assert (client.token, client.expires_at) == ("old-token", 900)


@pytest.mark.parametrize(
    "token, expires_at, refresh",
    [
        (None, 0, True),
        ("old", 999, True),
        ("old", 1029, True),
        ("old", 1030, False),
        ("old", 2000, False),
    ],
)
def test_headers_refresh_when_needed(client, monkeypatch, token, expires_at, refresh):
    client.token, client.expires_at = token, expires_at

    def authenticate():
        client.token = "renewed"

    auth = Mock(side_effect=authenticate)
    monkeypatch.setattr(client, "authenticate", auth)

    assert client._headers() == {
        "Authorization": f"Bearer {'renewed' if refresh else token}"
    }
    assert auth.call_count == int(refresh)


@pytest.mark.parametrize("endpoint", ["/areas", "areas"])
def test_get_normalizes_endpoint_and_returns_json(client, monkeypatch, endpoint):
    client.token, client.expires_at = "valid", 2000
    response = make_response([{"id": 42}])
    get = Mock(return_value=response)
    monkeypatch.setattr(api.requests, "get", get)

    assert client.get(endpoint) == [{"id": 42}]
    get.assert_called_once_with(
        "https://pnao.example/areas",
        headers={"Authorization": "Bearer valid"},
        timeout=api.HTTP_TIMEOUT,
        stream=True,
    )
    response.raise_for_status.assert_called_once_with()


def test_get_rejects_http_error_before_decoding(client, monkeypatch):
    client.token, client.expires_at = "valid", 2000
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError("server error")
    monkeypatch.setattr(api.requests, "get", Mock(return_value=response))

    with pytest.raises(requests.HTTPError, match="server error"):
        client.get("areas")
    response.iter_content.assert_not_called()


def test_get_propagates_connection_failure(client, monkeypatch):
    client.token, client.expires_at = "valid", 2000
    monkeypatch.setattr(
        api.requests, "get", Mock(side_effect=requests.ConnectionError("offline"))
    )
    with pytest.raises(requests.ConnectionError, match="offline"):
        client.get("areas")


@pytest.mark.parametrize("name", ["coeur", "tampon"])
def test_exports_use_expected_endpoint(client, monkeypatch, name):
    get = Mock(return_value=[{"id": 1}])
    monkeypatch.setattr(client, "get", get)
    assert getattr(client, f"export_zsm_{name}")() == [{"id": 1}]
    get.assert_called_once_with(f"/v6/services/webservices/data/0/export_zsm_{name}")


def test_decode_json_stops_reading_past_max_response_bytes(client, monkeypatch):
    monkeypatch.setattr(api, "MAX_RESPONSE_BYTES", 10)
    response = Mock()
    response.iter_content.return_value = [b"12345", b"67890", b"abc"]

    with pytest.raises(ValueError, match="trop volumineuse"):
        client._decode_json(response)


def test_decode_json_reads_chunked_body(client):
    response = Mock()
    response.iter_content.return_value = [b'{"a": ', b"1}"]

    assert client._decode_json(response) == {"a": 1}
    response.iter_content.assert_called_once_with(chunk_size=65536)


def test_decode_json_rejects_empty_body(client):
    response = Mock()
    response.iter_content.return_value = []

    with pytest.raises(json.JSONDecodeError):
        client._decode_json(response)


def test_close_clears_credentials_and_token(client):
    client.token = "tok"
    client.expires_at = 123

    client.close()

    assert client.username is None
    assert client.password is None
    assert client.token is None
    assert client.expires_at == 0


def test_del_clears_credentials_and_token(client):
    client.token = "tok"

    client.__del__()

    assert client.username is None
    assert client.password is None
    assert client.token is None
    assert client.expires_at == 0
