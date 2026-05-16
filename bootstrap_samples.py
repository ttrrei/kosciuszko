"""Download seed scraper snapshots for local offline TDD runs.

The generated files are intentionally runtime artifacts and should not be
committed. They let the scraper tests parse realistic Yahoo, Shortman, and AFR
responses without making network calls during pytest.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests

USER_AGENT = "Mozilla/5.0"
TIMEOUT_SECONDS = 30
YAHOO_SEED_URL = (
    "https://query2.finance.yahoo.com/v8/finance/chart/CBA.AX?interval=1h&range=2d"
)
SHORTMAN_SEED_URL = "https://www.shortman.com.au/downloadeddata/latest.csv"
AFR_SEED_URL = "https://www.afr.com/company/asx/bhp"


def download_seeds() -> None:
    """Download Yahoo, Shortman, and AFR seed snapshots into data/samples/."""
    print("正在下载本地 TDD 测试需要的种子快照...")

    _download_yahoo_seed()
    _download_shortman_seed()
    _download_afr_seed()


def _download_yahoo_seed() -> None:
    os.makedirs("data/samples/yahoo", exist_ok=True)
    resp = requests.get(
        YAHOO_SEED_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
    )
    if resp.status_code == 200:
        output_path = Path("data/samples/yahoo/CBA.json")
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(resp.json(), f, indent=4, sort_keys=True)
        print(f"✅ Yahoo 种子下载成功 ({output_path})")
    else:
        print(f"⚠️ Yahoo 种子下载失败: HTTP {resp.status_code}")


def _download_shortman_seed() -> None:
    os.makedirs("data/samples/shortman", exist_ok=True)
    resp = requests.get(SHORTMAN_SEED_URL, timeout=TIMEOUT_SECONDS)
    if resp.status_code == 200:
        output_path = Path("data/samples/shortman/LATEST.csv")
        with output_path.open("w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"✅ Shortman 种子下载成功 ({output_path})")
    else:
        print(f"⚠️ Shortman 种子下载失败: HTTP {resp.status_code}")


def _download_afr_seed() -> None:
    os.makedirs("data/samples/afr", exist_ok=True)
    resp = requests.get(
        AFR_SEED_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
    )
    if resp.status_code == 200:
        output_path = Path("data/samples/afr/BHP.html")
        with output_path.open("w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"✅ AFR 种子下载成功 ({output_path})")
    else:
        print(f"⚠️ AFR 种子下载失败: HTTP {resp.status_code}")


if __name__ == "__main__":
    download_seeds()
