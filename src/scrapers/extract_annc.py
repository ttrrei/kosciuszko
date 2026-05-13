"""Offline-friendly ASX announcement extraction scaffold."""

from __future__ import annotations

import re
from typing import Any


REQUIRED_KEYS = ("SYMBOL", "DATE", "TITLE")


def process_symbol(symbol: str, raw_text: str | None = None) -> dict[str, Any]:
    """Parse an announcement sample into the normalized ODS dictionary shape."""
    result: dict[str, Any] = {"SYMBOL": symbol, "DATE": None, "TITLE": None}
    if not raw_text:
        return result

    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw_text, flags=re.DOTALL)
    date_match = re.search(r'data-field=["\']date["\'][^>]*>([^<]+)', raw_text)
    result["TITLE"] = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else None
    result["DATE"] = date_match.group(1).strip() if date_match else None
    return result
