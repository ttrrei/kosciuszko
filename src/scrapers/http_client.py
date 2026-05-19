"""Lightweight HTTP client base for frequent Kosciuszko API scrapers."""

from __future__ import annotations

from typing import Any

import requests


class HttpClient:
    """Requests-based client for high-frequency, low-memory scrapers.

    Yahoo and AFR style endpoints do not need Selenium. This class keeps those
    scrapers cheap by centralising a browser-like User-Agent and a short default
    timeout while leaving source-specific parsing to concrete extractors.
    """

    DEFAULT_TIMEOUT = 10
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept": (
            "application/json,text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
    }

    def __init__(self, headers: dict[str, str] | None = None) -> None:
        self.headers = {**self.DEFAULT_HEADERS, **(headers or {})}

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """Issue a GET request with lightweight defaults and status checking."""
        headers = {**self.headers, **kwargs.pop("headers", {})}
        timeout = kwargs.pop("timeout", self.DEFAULT_TIMEOUT)

        response = requests.get(url, headers=headers, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
