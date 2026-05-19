"""ASX official list extraction placeholder."""

from __future__ import annotations

import logging
from typing import Any

from src.scrapers.browser_client import BrowserClient


logger = logging.getLogger(__name__)


class ListScraper(BrowserClient):
    """Browser scraper placeholder for weekly ASX official lists."""

    def process_symbol(self, symbol: str) -> Any:
        logger.info("List scraper placeholder for %s", symbol)
        return None
