import pytest
from crawler.fetcher import AsyncFetcher

@pytest.mark.asyncio
async def test_fetch_success(monkeypatch):
    class DummyResponse:
        status = 200
        async def text(self): return "ok"
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass

    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        def get(self, url, headers=None, timeout=10):
            return DummyResponse()

    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **kw: DummySession())
    f = AsyncFetcher(delay=0, retries=0)
    result = await f.fetch("http://x")
    assert result == "ok"


@pytest.mark.asyncio
async def test_fetch_retries(monkeypatch):
    calls = {"n": 0}

    class DummyResponse:
        status = 200
        async def text(self): return "done"
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass

    class DummySession:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        def get(self, url, headers=None, timeout=10):
            calls["n"] += 1
            if calls["n"] < 2:
                raise Exception("conn")
            return DummyResponse()

    monkeypatch.setattr("aiohttp.ClientSession", lambda *a, **kw: DummySession())
    f = AsyncFetcher(delay=0, retries=1, backoff=0)
    result = await f.fetch("http://x")
    assert result == "done"
    assert calls["n"] == 2
