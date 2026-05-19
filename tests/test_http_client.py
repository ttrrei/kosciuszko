from unittest.mock import MagicMock, patch

from src.scrapers.http_client import HttpClient


@patch("requests.get")
def test_get_uses_browser_headers_and_default_timeout(mock_get):
    response = MagicMock()
    mock_get.return_value = response

    client = HttpClient()
    result = client.get("https://example.test/api")

    assert result is response
    mock_get.assert_called_once()
    _, kwargs = mock_get.call_args
    assert kwargs["timeout"] == 10
    assert "Mozilla/5.0" in kwargs["headers"]["User-Agent"]
    response.raise_for_status.assert_called_once()


@patch("requests.get")
def test_get_allows_headers_and_timeout_override(mock_get):
    response = MagicMock()
    mock_get.return_value = response

    client = HttpClient(headers={"X-Client": "Kosciuszko"})
    client.get(
        "https://example.test/api",
        headers={"Accept": "application/json"},
        timeout=3,
        params={"symbol": "AAPL"},
    )

    _, kwargs = mock_get.call_args
    assert kwargs["timeout"] == 3
    assert kwargs["params"] == {"symbol": "AAPL"}
    assert kwargs["headers"]["X-Client"] == "Kosciuszko"
    assert kwargs["headers"]["Accept"] == "application/json"
