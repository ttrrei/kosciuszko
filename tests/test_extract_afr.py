from pathlib import Path
from unittest.mock import patch

from src.scrapers.extract_afr import process_symbol


SAMPLE_PATH = Path("data/samples/afr/afr_sample.html")


def test_extract_afr_from_local_sample_without_network():
    with patch("src.scrapers.http_client.requests.Session.get") as mock_get:
        result = process_symbol("BHP.AX", SAMPLE_PATH.read_text(encoding="utf-8"))

    mock_get.assert_not_called()
    assert "SYMBOL" in result
    assert "PRICE" in result
    assert "DATE" in result
    assert result["SYMBOL"] == "BHP.AX"
