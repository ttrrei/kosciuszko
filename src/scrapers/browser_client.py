"""Browser client helpers for JavaScript-rendered scraper sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class BrowserClient:
    """Wrapper for a Selenium-like driver with raw page-source sampling."""

    def __init__(self, driver: Any):
        self.driver = driver

    def save_page_source(self, file_path: str | Path) -> Path:
        """Persist the current browser page source and return the saved path."""
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.driver.page_source, encoding="utf-8")
        return output_path
