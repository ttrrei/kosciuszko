"""ASX daily announcement extraction placeholder."""

from __future__ import annotations

import logging
from typing import Any

from src.scrapers.browser_client import BrowserClient


logger = logging.getLogger(__name__)


class AnnouncementScraper(BrowserClient):
    """Browser scraper placeholder for daily ASX announcements."""

    def process_symbol(self, symbol: str) -> Any:
        logger.info("Announcement scraper placeholder for %s", symbol)
        return None
