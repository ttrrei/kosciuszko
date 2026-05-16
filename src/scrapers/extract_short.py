"""Shortman CSV extraction using the scraper profile."""

from __future__ import annotations

import csv
import io
import json
import logging
import os
from typing import Any

from src.scrapers.http_client import HttpClient

logger = logging.getLogger(__name__)


class ExtractShort(HttpClient):
    """Fetch and persist the latest Shortman CSV snapshot."""

    def __init__(self):
        super().__init__()
        profile_path = os.path.join("config", "scrapers_profile.json")
        with open(profile_path, "r", encoding="utf-8") as f:
            self.profile = json.load(f)["shortman"]

        self.target_table = self.profile["target_table"]
        self.csv_url = self.profile["url"]
        self.primary_keys = self.profile["primary_keys"]
        self.csv_mappings = self.profile["csv_mappings"]

    def run(self) -> list[dict[str, Any]] | None:
        """Fetch, normalize, and merge the latest Shortman CSV rows."""
        save_path = "data/samples/shortman/LATEST.csv"
        resp = self.get(self.csv_url, save_raw_to=save_path)

        if not resp or resp.status_code != 200:
            logger.error("Failed to fetch Shortman CSV")
            return None

        records = self._parse_csv(resp.text)
        if records and self.db is not None:
            self.db.execute_merge(
                self.target_table,
                records,
                primary_keys=self.primary_keys,
            )
        return records

    def _parse_csv(self, text: str) -> list[dict[str, Any]]:
        f = io.StringIO(text)
        reader = csv.DictReader(f)

        records = []
        for row in reader:
            try:
                record = {
                    "PRODUCT_NAME": row.get(self.csv_mappings["PRODUCT_NAME"]),
                    "CODE": row.get(self.csv_mappings["CODE"]),
                    "SHORT_POSITIONS": self._parse_num(
                        row.get(self.csv_mappings["SHORT_POSITIONS"])
                    ),
                    "TOTAL_ISSUE": self._parse_num(
                        row.get(self.csv_mappings["TOTAL_ISSUE"])
                    ),
                    "PERCENTAGE": self._parse_num(
                        row.get(self.csv_mappings["PERCENTAGE"])
                    ),
                    "UPDATE_DATE": self.config.get("current_date"),
                }
                if record["CODE"]:
                    records.append(record)
            except (KeyError, TypeError, ValueError) as e:
                logger.debug("Skipping CSV row parse due to: %s", e)
                continue
        return records

    def _parse_num(self, val: str | None) -> float | None:
        if not val:
            return None
        try:
            return float(val.replace(",", "").replace("%", ""))
        except ValueError:
            return None
