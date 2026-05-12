from pathlib import Path
from unittest.mock import MagicMock

from src.scrapers.browser_client import BrowserClient
from src.scrapers.http_client import HttpClient
from src.utils.diff_tool import html_diff, unified_diff


def test_http_client_get_can_save_successful_raw_response(tmp_path):
    client = HttpClient(timeout=3)
    response = MagicMock(status_code=200, text="raw body", encoding="utf-8")
    client.session.get = MagicMock(return_value=response)

    save_path = tmp_path / "nested" / "quote.html"
    returned = client.get("https://example.invalid/quote", save_path=save_path)

    assert returned is response
    assert save_path.read_text(encoding="utf-8") == "raw body"
    client.session.get.assert_called_once_with(
        "https://example.invalid/quote",
        timeout=3,
    )


def test_http_client_get_does_not_save_non_200_response(tmp_path):
    client = HttpClient()
    response = MagicMock(status_code=500, text="error", encoding="utf-8")
    client.session.get = MagicMock(return_value=response)

    save_path = tmp_path / "failed" / "response.html"
    client.get("https://example.invalid/fail", save_path=save_path)

    assert not save_path.exists()


def test_browser_client_can_save_page_source(tmp_path):
    driver = MagicMock(page_source="<html>sample</html>")
    client = BrowserClient(driver)

    save_path = client.save_page_source(tmp_path / "browser" / "page.html")

    assert save_path == tmp_path / "browser" / "page.html"
    assert save_path.read_text(encoding="utf-8") == "<html>sample</html>"


def test_diff_tool_can_emit_text_and_html_reports(tmp_path):
    old_file = tmp_path / "old.html"
    new_file = tmp_path / "new.html"
    report_file = tmp_path / "reports" / "diff.html"
    old_file.write_text("price=1\nstatus=old\n", encoding="utf-8")
    new_file.write_text("price=2\nstatus=new\n", encoding="utf-8")

    text_report = unified_diff(old_file, new_file)
    html_report_path = html_diff(old_file, new_file, report_file)

    assert "-price=1" in text_report
    assert "+price=2" in text_report
    assert html_report_path == report_file
    assert report_file.exists()
