import json
from unittest.mock import MagicMock

import bootstrap_samples


def test_download_seeds_writes_expected_sample_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    yahoo_resp = MagicMock(status_code=200)
    yahoo_resp.json.return_value = {"chart": {"result": []}}
    short_resp = MagicMock(status_code=200, text="Product,Code\nSample,CBA\n")
    afr_resp = MagicMock(status_code=200, text="<html>BHP</html>")
    mock_get = MagicMock(side_effect=[yahoo_resp, short_resp, afr_resp])
    monkeypatch.setattr(bootstrap_samples.requests, "get", mock_get)

    bootstrap_samples.download_seeds()

    yahoo_path = tmp_path / "data" / "samples" / "yahoo" / "CBA.json"
    short_path = tmp_path / "data" / "samples" / "shortman" / "LATEST.csv"
    afr_path = tmp_path / "data" / "samples" / "afr" / "BHP.html"

    assert json.loads(yahoo_path.read_text(encoding="utf-8")) == {
        "chart": {"result": []}
    }
    assert short_path.read_text(encoding="utf-8") == "Product,Code\nSample,CBA\n"
    assert afr_path.read_text(encoding="utf-8") == "<html>BHP</html>"
    assert mock_get.call_count == 3
