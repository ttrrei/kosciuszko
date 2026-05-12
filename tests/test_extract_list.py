from pathlib import Path
from unittest.mock import patch

from src.scrapers.extract_list import process_symbol


SAMPLE_PATH = Path("data/samples/list/list_sample.csv")


def test_extract_list_from_local_sample_without_network():
    with patch("src.scrapers.http_client.requests.Session.get") as mock_get:
        result = process_symbol("BHP.AX", SAMPLE_PATH.read_text(encoding="utf-8"))

    mock_get.assert_not_called()
    assert "SYMBOL" in result
    assert "NAME" in result
    assert "DATE" in result
    assert result["SYMBOL"] == "BHP.AX"
