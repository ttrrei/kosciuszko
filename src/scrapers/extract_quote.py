"""Yahoo Finance quote extraction placeholder."""

from __future__ import annotations

import logging
from typing import Any

from src.scrapers.http_client import HttpClient


logger = logging.getLogger(__name__)


class QuoteScraper(HttpClient):
    """HTTP scraper placeholder for frequent Yahoo Finance quote pulls."""

    def process_symbol(self, symbol: str) -> Any:
        logger.info("Quote scraper placeholder for %s", symbol)
        return None
