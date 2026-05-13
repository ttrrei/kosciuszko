"""Lightweight HTTP client helpers for scraper ingestion."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class HttpClient:
    """Small wrapper around ``requests.Session`` with optional raw sampling."""

    DEFAULT_TIMEOUT_SECONDS = 15

    def __init__(self, *, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, url: str, *, save_path: str | Path | None = None, **kwargs: Any):
        """GET ``url`` and optionally persist the raw response body.

        Args:
            url: URL to request.
            save_path: Optional local file path where ``response.text`` should
                be written when the request succeeds with HTTP 200.
            **kwargs: Additional keyword arguments passed to ``requests``.

        Returns:
            The original ``requests.Response`` instance.
        """
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.get(url, **kwargs)

        if save_path is not None and response.status_code == 200:
            output_path = Path(save_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(response.text, encoding=response.encoding or "utf-8")

        return response
