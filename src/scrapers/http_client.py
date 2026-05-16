"""Lightweight HTTP client helpers for scraper ingestion."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


class HttpClient:
    """Small wrapper around ``requests.Session`` with optional raw sampling."""

    DEFAULT_TIMEOUT_SECONDS = 15

    def __init__(self, *, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self.timeout = timeout
        self.session = requests.Session()
        now = datetime.now(timezone.utc)
        self.config = {
            "debug": False,
            "current_date": now.date().isoformat(),
            "current_timestamp": now.isoformat(),
        }
        self.db = _build_db_operator()

    def get(
        self,
        url: str,
        *,
        save_path: str | Path | None = None,
        save_raw_to: str | Path | None = None,
        **kwargs: Any,
    ):
        """GET ``url`` and optionally persist the raw response body.

        Args:
            url: URL to request.
            save_path: Optional local file path where ``response.text`` should
                be written when the request succeeds with HTTP 200.
            save_raw_to: Compatibility alias for ``save_path`` used by scraper
                implementations.
            **kwargs: Additional keyword arguments passed to ``requests``.

        Returns:
            The original ``requests.Response`` instance.
        """
        kwargs.setdefault("timeout", self.timeout)
        response = self.session.get(url, **kwargs)

        output_target = save_path if save_path is not None else save_raw_to
        if output_target is not None and response.status_code == 200:
            output_path = Path(output_target)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(response.text, encoding=response.encoding or "utf-8")

        return response


def _build_db_operator():
    """Create the DB operator when runtime env is configured, otherwise defer it."""
    from src.db_operator import DbOperator

    try:
        return DbOperator()
    except ValueError:
        return None
