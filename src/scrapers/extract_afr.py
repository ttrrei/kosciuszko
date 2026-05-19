"""AFR market data extraction placeholder."""

from __future__ import annotations

import logging
from typing import Any

from src.scrapers.http_client import HttpClient


logger = logging.getLogger(__name__)


class AfrScraper(HttpClient):
    """HTTP scraper placeholder for frequent AFR market data pulls."""

    def process_symbol(self, symbol: str) -> Any:
        logger.info("AFR scraper placeholder for %s", symbol)
        return None
