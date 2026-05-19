"""Shared Selenium scraper foundation for low-memory Ironbark workers."""

from __future__ import annotations

import abc
import logging
import tempfile
from typing import Any, Iterable

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.config import Config


logger = logging.getLogger(__name__)


class BrowserClient(abc.ABC):
    """Browser base class for resource-constrained, fault-tolerant Selenium scrapers.

    Ironbark has only 1GB RAM, so this class owns the dirty work common to all
    scrapers: start Chrome with a defensive low-memory profile, isolate each
    symbol so one failure does not crash the full queue, and always release the
    browser process at the end of a run.
    """

    def __init__(self) -> None:
        self.config = Config()
        self.driver: Any | None = None

    def _build_options(self) -> Options:
        """Build Chrome options optimized for Ironbark's 1GB RAM limit."""
        chrome_options = Options()

        # Keep this explicit attribute for the existing tests and older Selenium
        # callers, while also passing the actual Chrome flag below.
        chrome_options.headless = True

        # Core survival flags for small Linux VMs / containers.
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        chrome_options.add_argument(
            f"--disk-cache-dir={tempfile.gettempdir()}/kosciuszko-chrome-cache"
        )

        # Further reduce memory and network pressure. CSS is disabled because the
        # scrapers should rely on DOM/data content rather than visual rendering.
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        return chrome_options

    def _init_driver(self) -> None:
        """Initialize Selenium Chrome with low-memory defaults."""
        chrome_options = self._build_options()

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
        except Exception as exc:
            logger.error("浏览器驱动初始化失败: %s", exc)
            raise

    @abc.abstractmethod
    def process_symbol(self, symbol: str) -> Any:
        """Process one symbol and return source-specific scraped data."""
        raise NotImplementedError

    def run(self, symbols: Iterable[str]) -> tuple[list[Any], list[str]]:
        """Run a resilient scrape loop and return successes plus retry targets.

        Args:
            symbols: Symbols that should be processed by the concrete scraper.

        Returns:
            A tuple of ``(results, failed_symbols)``. ``failed_symbols`` is the
            hand-off point for later recovery passes in the multi-pass strategy.
        """
        results: list[Any] = []
        failed_symbols: list[str] = []
        symbol_list = list(symbols)

        if not symbol_list:
            return results, failed_symbols

        if not self.driver:
            self._init_driver()

        try:
            for symbol in symbol_list:
                try:
                    logger.info("正在处理: %s", symbol)
                    data = self.process_symbol(symbol)
                    if data:
                        results.append(data)
                except Exception as exc:  # noqa: BLE001 - queue isolation is intentional.
                    logger.error("处理 %s 时发生错误: %s", symbol, exc)
                    failed_symbols.append(symbol)
        finally:
            self.cleanup()

        return results, failed_symbols

    def cleanup(self) -> None:
        """Release browser resources even if Chrome reports a shutdown error."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as exc:  # noqa: BLE001 - cleanup must not mask scrape results.
                logger.warning("关闭浏览器时发生异常: %s", exc)
            finally:
                self.driver = None
