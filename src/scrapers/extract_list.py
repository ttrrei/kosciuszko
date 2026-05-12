"""Offline-friendly ASX list extraction scaffold."""

from __future__ import annotations

from typing import Any


REQUIRED_KEYS = ("SYMBOL", "NAME", "DATE")


def process_symbol(symbol: str, raw_text: str | None = None) -> dict[str, Any]:
    """Return the normalized list dictionary shape for future parser work."""
    return {"SYMBOL": symbol, "NAME": None, "DATE": None}
