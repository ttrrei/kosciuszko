"""Offline-friendly consensus extraction scaffold."""

from __future__ import annotations

from typing import Any


REQUIRED_KEYS = ("SYMBOL", "DATE", "CONSENSUS")


def process_symbol(symbol: str, raw_text: str | None = None) -> dict[str, Any]:
    """Return the normalized consensus dictionary shape for future parser work."""
    return {"SYMBOL": symbol, "DATE": None, "CONSENSUS": None}
