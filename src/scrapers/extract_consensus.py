"""Analyst consensus extraction placeholder."""

from __future__ import annotations

import logging
from typing import Any

from src.scrapers.browser_client import BrowserClient


logger = logging.getLogger(__name__)


class ConsensusScraper(BrowserClient):
    """Browser scraper placeholder for weekly analyst consensus data."""

    def process_symbol(self, symbol: str) -> Any:
        logger.info("Consensus scraper placeholder for %s", symbol)
        return None
