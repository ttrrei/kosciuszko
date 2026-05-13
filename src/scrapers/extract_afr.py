"""Offline-friendly AFR extraction scaffold."""

from __future__ import annotations

import re
from typing import Any


REQUIRED_KEYS = ("SYMBOL", "PRICE", "DATE")


def process_symbol(symbol: str, raw_text: str | None = None) -> dict[str, Any]:
    """Parse an AFR sample into the normalized ODS dictionary shape."""
    result: dict[str, Any] = {"SYMBOL": symbol, "PRICE": None, "DATE": None}
    if not raw_text:
        return result

    price_match = re.search(r'data-field=["\']price["\'][^>]*>([^<]+)', raw_text)
    date_match = re.search(r'data-field=["\']date["\'][^>]*>([^<]+)', raw_text)
    result["PRICE"] = price_match.group(1).strip() if price_match else None
    result["DATE"] = date_match.group(1).strip() if date_match else None
    return result
