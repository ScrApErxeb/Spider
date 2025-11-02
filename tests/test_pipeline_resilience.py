import pytest
import logging
from scraper.scraper_main import extract

class DummyDB:
    def __init__(self):
        self.saved = []
    def save_batch(self, data):
        if data == ["crash"]:
            raise Exception("DB fail")
        self.saved.extend(data)

def test_extract_resilience(monkeypatch, caplog):
    # on simule les dépendances pour forcer des erreurs contrôlées
    caplog.set_level(logging.ERROR)

    def bad_parse(html):
        if "bad" in html:
            raise Exception("Parse error")
        return [html.upper()]

    def bad_clean(data):
        if "CLEANFAIL" in data:
            raise Exception("Clean error")
        return [d.strip() for d in data]

    # patch des modules
    monkeypatch.setattr("scraper.scraper_main.parse_html", bad_parse)
    monkeypatch.setattr("scraper.scraper_main.sanitize", bad_clean)
    monkeypatch.setattr("scraper.scraper_main.Database", lambda: DummyDB())

    # cas avec erreurs mixtes
    pages = [
        ("ok page", "http://ok"),
        ("bad html", "http://fail-parse"),
        ("CLEANFAIL", "http://fail-clean"),
        ("crash", "http://db-fail"),
    ]

    result = extract(pages)

    # vérifications
    assert isinstance(result, list)
    assert all(isinstance(x, str) for x in result)
    assert any("error" in r.message.lower() for r in caplog.records)
    assert "Extraction failed" not in caplog.text  # pas de crash global
