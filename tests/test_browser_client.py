from unittest.mock import MagicMock, patch

import pytest

from src.scrapers.browser_client import BrowserClient


class MockBrowserClient(BrowserClient):
    """Concrete scraper used to exercise BrowserClient behaviour."""

    def process_symbol(self, symbol):
        if symbol == "FAIL":
            raise Exception("Forced Failure")
        return {"symbol": symbol, "data": 123}


@pytest.fixture
def mock_config(monkeypatch):
    monkeypatch.setenv("DB_USER", "ADMIN")
    monkeypatch.setenv("DB_PASSWORD", "PASS")
    monkeypatch.setenv("DB_DSN", "DSN")
    monkeypatch.setenv("BATCH_SIZE", "2")


@patch("selenium.webdriver.Chrome")
def test_driver_options_optimization(mock_chrome, mock_config):
    """
    测试驱动配置优化：
    验证是否设置了 headless 和禁用图片，这在 1GB 内存环境下是必须的。
    """
    scraper = MockBrowserClient()
    scraper._init_driver()

    _, kwargs = mock_chrome.call_args
    options = kwargs.get("options")

    assert options.headless is True
    opt_str = str(options.arguments)
    assert "--disable-gpu" in opt_str
    assert "--no-sandbox" in opt_str
    assert "--disable-dev-shm-usage" in opt_str
    assert "--blink-settings=imagesEnabled=false" in opt_str
    assert (
        options.experimental_options["prefs"]["profile.managed_default_content_settings.images"]
        == 2
    )


@patch("selenium.webdriver.Chrome")
def test_resilience_and_tracking(mock_chrome, mock_config):
    """
    测试容错与追踪逻辑：
    验证当部分 Symbol 失败时，scraper 是否能继续运行，并记录失败项。
    """
    scraper = MockBrowserClient()
    symbols = ["AAPL", "FAIL", "GOOG"]

    results, failed_symbols = scraper.run(symbols)

    assert len(results) == 2
    assert "FAIL" in failed_symbols
    assert len(failed_symbols) == 1


@patch("selenium.webdriver.Chrome")
def test_mandatory_cleanup(mock_chrome, mock_config):
    """
    测试强制清理：
    验证无论如何，driver.quit() 都会被执行，防止内存泄露。
    """
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    scraper = MockBrowserClient()
    results, failed_symbols = scraper.run(["FAIL"])

    assert results == []
    assert failed_symbols == ["FAIL"]
    assert mock_driver.quit.called
