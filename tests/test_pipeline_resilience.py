from scraper.scraper_main import extract

def test_extract_resilience():
    pages = [
        ("url1", "<html><title>ok</title><a href='x'>x</a></html>"),
        ("url2", None),  # broken page
    ]
    data = extract(pages)
    assert any(d.get("title") == "ok" for d in data)
