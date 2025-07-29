import pytest
from nexa_sdk.client import NexaClient
from nexa_sdk.exceptions import NexaAPIError
from unittest.mock import patch, MagicMock
import requests

def test_headers_with_api_key():
    client = NexaClient(api_key="abc")
    headers = client._headers()
    assert headers["Authorization"] == "Bearer abc"
    assert headers["Content-Type"] == "application/json"

def test_headers_with_extra():
    client = NexaClient(api_key="abc")
    headers = client._headers({"X-Test": "1"})
    assert headers["X-Test"] == "1"

def test_request_success():
    client = NexaClient(api_key="abc")
    with patch("requests.request") as mock_req:
        mock_resp = mock_req.return_value
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True}
        mock_resp.raise_for_status = lambda: None
        resp = client.request("GET", "/test")
        assert resp["ok"] is True

def test_request_raises_nexa_api_error():
    client = NexaClient(api_key="abc")
    with patch("requests.request") as mock_req:
        mock_req.side_effect = requests.RequestException("fail")
        with pytest.raises(NexaAPIError):
            client.request("GET", "/fail")

def test_request_returns_none_on_204():
    client = NexaClient(api_key="abc")
    with patch("requests.request") as mock_req:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.raise_for_status = lambda: None
        mock_req.return_value = mock_resp
        result = client.request("GET", "/no-content")
        assert result is None 