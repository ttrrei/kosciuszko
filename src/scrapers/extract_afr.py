"""AFR quote extraction using profile-driven selectors."""

from __future__ import annotations

import json
import logging
import os
import re
from html.parser import HTMLParser
from importlib.util import find_spec
from typing import Any

if find_spec("bs4") is not None:
    from bs4 import BeautifulSoup
else:
    BeautifulSoup = None

from src.scrapers.http_client import HttpClient

logger = logging.getLogger(__name__)


class ExtractAfr(HttpClient):
    """Fetch AFR quote pages and dual-write structured and EAV records."""

    def __init__(self):
        super().__init__()
        profile_path = os.path.join("config", "scrapers_profile.json")
        with open(profile_path, "r", encoding="utf-8") as f:
            self.profile = json.load(f)["afr"]

        self.table_struct = self.profile["table_struct"]
        self.table_eav = self.profile["table_eav"]
        self.url_template = self.profile["url_template"]
        self.struct_keys = self.profile["struct_keys"]
        self.eav_keys = self.profile["eav_keys"]
        self.selectors = self.profile["selectors"]

    def process_symbol(self, symbol: str) -> None:
        """Fetch an AFR quote page, parse configured metrics, and dual-write them."""
        code = symbol.upper()
        url = self.url_template.format(symbol=symbol.lower())
        save_path = f"data/samples/afr/{code}.html"
        resp = self.get(url, save_raw_to=save_path)

        if not resp or resp.status_code != 200:
            logger.error("Failed to fetch AFR data for %s", symbol)
            return None

        return self._process_html(code, resp.text)

    def _process_html(self, code: str, html: str, *, merge: bool = True) -> None:
        soup = BeautifulSoup(html, "html.parser") if BeautifulSoup else None
        current_time = self.config.get("current_timestamp")

        raw_metrics = {}
        for metric_name, selector in self.selectors.items():
            raw_metrics[metric_name] = self._parse_by_selector(soup, selector, html=html)

        struct_record = [
            {
                "CODE": code,
                "PRICE": self._to_float(raw_metrics.get("PRICE")),
                "VOLUME": self._to_float(raw_metrics.get("VOLUME")),
                "UPDATE_TIME": current_time,
            }
        ]

        eav_records = []
        for tag, val in raw_metrics.items():
            if val is not None:
                eav_records.append(
                    {
                        "CODE": code,
                        "TAG": tag,
                        "INFO": str(val),
                        "UPDATE_TIME": current_time,
                    }
                )

        if merge and self.db is not None:
            if struct_record and struct_record[0]["PRICE"] is not None:
                self.db.execute_merge(
                    self.table_struct,
                    struct_record,
                    primary_keys=self.struct_keys,
                )

            if eav_records:
                self.db.execute_merge(
                    self.table_eav,
                    eav_records,
                    primary_keys=self.eav_keys,
                )

    def _parse_by_selector(
        self,
        soup: Any,
        selector: dict[str, Any],
        *,
        html: str | None = None,
    ) -> str | None:
        """Extract with configured selectors; update JSON if AFR markup changes."""
        try:
            attrs = {selector["attr"]: selector["value"]} if selector["attr"] else {}
            if soup is not None:
                element = soup.find(name=selector["tag"], attrs=attrs)
                return element.text.strip() if element else None
            if html is not None:
                return _find_text_by_attrs(html, attrs)
            return None
        except (AttributeError, KeyError, TypeError) as e:
            logger.warning("Selector failed to extract: %s. Error: %s", selector, e)
            return None

    def _to_float(self, val: str | None) -> float | None:
        if not val:
            return None
        try:
            return float(val.replace(",", "").replace("$", "").strip())
        except ValueError:
            return None


def _find_text_by_attrs(html: str, attrs: dict[str, Any]) -> str | None:
    parser = _AttrTextParser(attrs)
    parser.feed(html)
    return parser.first_text


class _AttrTextParser(HTMLParser):
    def __init__(self, attrs: dict[str, Any]):
        super().__init__()
        self.attrs = attrs
        self._capture_depth = 0
        self._parts: list[str] = []
        self.first_text: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.first_text is not None:
            return
        attr_map = dict(attrs)
        if self._capture_depth or all(attr_map.get(k) == v for k, v in self.attrs.items()):
            self._capture_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self.first_text is not None or not self._capture_depth:
            return
        self._capture_depth -= 1
        if self._capture_depth == 0:
            text = "".join(self._parts).strip()
            self.first_text = text if text else None

    def handle_data(self, data: str) -> None:
        if self._capture_depth and self.first_text is None:
            self._parts.append(data)


def process_symbol(symbol: str, raw_text: str | None = None) -> dict[str, Any]:
    """Backward-compatible offline parser used by legacy sample tests."""
    result: dict[str, Any] = {"SYMBOL": symbol, "PRICE": None, "DATE": None}
    if not raw_text:
        return result

    price_match = re.search(r'data-field=["\']price["\'][^>]*>([^<]+)', raw_text)
    date_match = re.search(r'data-field=["\']date["\'][^>]*>([^<]+)', raw_text)
    result["PRICE"] = price_match.group(1).strip() if price_match else None
    result["DATE"] = date_match.group(1).strip() if date_match else None
    return result
