import pytest
import requests
from crawler.fetcher import Fetcher

class DummyResp:
    def __init__(self, text="", status=200):
        self.text = text
        self.status_code = status
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.RequestException("HTTP error")

def test_fetcher_retries(monkeypatch):
    calls = {"n": 0}

    def fake_get(url, headers=None, timeout=5):
        calls["n"] += 1
        if calls["n"] < 2:
            raise requests.RequestException("conn")
        return DummyResp(text="ok", status=200)

    f = Fetcher(delay=0, retries=1, backoff=0)
    monkeypatch.setattr(f, "_get", fake_get)
    result = f.fetch("http://x")
    assert result == "ok"
    assert calls["n"] == 2
