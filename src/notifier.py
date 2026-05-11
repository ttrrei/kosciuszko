"""Pushover notification client for Kosciuszko crawler alerts."""

from __future__ import annotations

import sys
import types
from importlib.util import find_spec
from typing import Any

from src.config import Config


if find_spec("requests") is not None:
    import requests
else:
    requests = types.ModuleType("requests")

    class _RequestException(Exception):
        """Fallback request error used when requests is unavailable."""

    def _missing_post(*_args: Any, **_kwargs: Any) -> Any:
        raise _RequestException("requests is required to send Pushover notifications.")

    requests.RequestException = _RequestException
    requests.post = _missing_post
    sys.modules["requests"] = requests


class Notifier:
    """Small, stateless Pushover notifier for crawler status and alerts."""

    API_URL = "https://api.pushover.net/1/messages.json"
    TIMEOUT_SECONDS = 5

    def __init__(self):
        self._config = Config()
        self._token = self._config.PUSHOVER_TOKEN
        self._user_key = self._config.PUSHOVER_USER_KEY

    def send(self, message: str, *, title: str = "Kosciuszko", priority: int = 0) -> bool:
        """Send a Pushover message and return whether delivery was accepted.

        The crawler must not be blocked by notification failures, so missing
        credentials, rejected API responses, and network exceptions all return
        ``False`` instead of raising to the caller.
        """
        if not self._token or not self._user_key:
            return False

        payload = {
            "token": self._token,
            "user": self._user_key,
            "message": message,
            "title": title,
            "priority": priority,
        }

        try:
            response = requests.post(
                self.API_URL,
                data=payload,
                timeout=self.TIMEOUT_SECONDS,
            )
        except requests.RequestException:
            return False

        return response.status_code == 200
