from pathlib import Path
from unittest.mock import patch

import pytest

from src.scrapers.extract_afr import process_symbol


SAMPLE_DIR = Path("data/samples/afr")
REQUIRED_KEYS = ("SYMBOL", "PRICE", "DATE")


def _load_first_real_sample(sample_dir: Path) -> str:
    candidates = sorted(
        path
        for path in sample_dir.iterdir()
        if path.is_file() and path.name not in {".gitkeep", "README.md"}
    )
    if not candidates:
        pytest.skip(f"No real AFR snapshot sample found in {sample_dir}")
    return candidates[0].read_text(encoding="utf-8", errors="replace")


def test_extract_afr_from_real_local_sample_without_network():
    sample_text = _load_first_real_sample(SAMPLE_DIR)

    with patch("src.scrapers.http_client.requests.Session.get") as mock_get:
        result = process_symbol("BHP.AX", sample_text)

    mock_get.assert_not_called()
    for key in REQUIRED_KEYS:
        assert key in result
    assert result["SYMBOL"]
