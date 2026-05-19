from src.scrapers.browser_client import BrowserClient
from src.scrapers.extract_afr import AfrScraper
from src.scrapers.extract_annc import AnnouncementScraper
from src.scrapers.extract_consensus import ConsensusScraper
from src.scrapers.extract_list import ListScraper
from src.scrapers.extract_quote import QuoteScraper
from src.scrapers.http_client import HttpClient


def test_http_scrapers_use_http_client():
    assert issubclass(QuoteScraper, HttpClient)
    assert issubclass(AfrScraper, HttpClient)


def test_browser_scrapers_use_browser_client():
    assert issubclass(AnnouncementScraper, BrowserClient)
    assert issubclass(ListScraper, BrowserClient)
    assert issubclass(ConsensusScraper, BrowserClient)
