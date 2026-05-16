"""Yahoo Finance quote extraction using the scraper profile."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from src.scrapers.http_client import HttpClient

logger = logging.getLogger(__name__)


class ExtractQuote(HttpClient):
    """Fetch and persist Yahoo Finance hourly history for ASX symbols."""

    def __init__(self):
        super().__init__()
        profile_path = os.path.join("config", "scrapers_profile.json")
        with open(profile_path, "r", encoding="utf-8") as f:
            self.profile = json.load(f)["yahoo"]

        self.target_table = self.profile["target_table"]
        self.url_template = self.profile["url_template"]
        self.primary_keys = self.profile["primary_keys"]
        self.filter_seconds = self.profile["filter_seconds"]

    def process_symbol(self, symbol: str) -> list[dict[str, Any]] | None:
        """Fetch, filter, normalize, and merge Yahoo chart rows for ``symbol``."""
        code = symbol.upper()
        url = self.url_template.format(symbol=code)
        save_path = f"data/samples/yahoo/{code}.json"

        resp = self.get(
            url,
            save_raw_to=save_path if self.config.get("debug") else None,
        )

        if not resp or resp.status_code != 200:
            logger.error("Failed to fetch Yahoo data for %s", symbol)
            return None

        return self._process_payload(code, resp.json())

    def _process_payload(
        self, code: str, data: dict[str, Any], *, merge: bool = True
    ) -> list[dict[str, Any]] | None:
        result = data.get("chart", {}).get("result", [None])[0]
        if not result or "timestamp" not in result:
            return None

        timestamps = result["timestamp"]
        indicators = result.get("indicators", {}).get("quote", [{}])[0]

        records = []
        for i, ts in enumerate(timestamps):
            if ts % self.filter_seconds == 0:
                record = {
                    "CODE": code,
                    "RAW_TIMESTAMP": ts,
                    "OPEN_PRICE": _safe_get(indicators.get("open", []), i),
                    "HIGH_PRICE": _safe_get(indicators.get("high", []), i),
                    "LOW_PRICE": _safe_get(indicators.get("low", []), i),
                    "CLOSE_PRICE": _safe_get(indicators.get("close", []), i),
                    "VOLUME": _safe_get(indicators.get("volume", []), i),
                }
                if record["CLOSE_PRICE"] is not None and record["VOLUME"] is not None:
                    records.append(record)

        if merge and records and self.db is not None:
            self.db.execute_merge(
                self.target_table,
                records,
                primary_keys=self.primary_keys,
            )
        return records


def _safe_get(values: list[Any], index: int) -> Any:
    return values[index] if index < len(values) else None


def process_symbol(symbol: str, raw_text: str | None = None) -> dict[str, Any]:
    """Backward-compatible offline parser used by legacy sample tests."""
    result: dict[str, Any] = {"SYMBOL": symbol, "PRICE": None, "DATE": None}
    if not raw_text:
        return result

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        return result

    quote = payload.get("quote", payload)
    result["SYMBOL"] = quote.get("symbol", symbol)
    result["PRICE"] = quote.get("regularMarketPrice") or quote.get("price")
    result["DATE"] = quote.get("regularMarketTime") or quote.get("date")
    return result
