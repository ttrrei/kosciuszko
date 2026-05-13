"""Offline-friendly Yahoo quote extraction scaffold."""

from __future__ import annotations

import json
from typing import Any


REQUIRED_KEYS = ("SYMBOL", "PRICE", "DATE")


def process_symbol(symbol: str, raw_text: str | None = None) -> dict[str, Any]:
    """Parse a quote sample into the normalized ODS dictionary shape."""
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
