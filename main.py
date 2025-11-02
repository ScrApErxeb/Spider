from crawler.crawler_main import run_crawler
from scraper.scraper_main import run_scraper
from storage.database import Database
from utils.export_utils import export_json, export_csv  # ou storage.exporter

def main():
    start_urls = ["http://example.com", "http://test.com"]
    crawled = run_crawler(start_urls)
    parsed = run_scraper(crawled)

    db = Database(path="data/project.db")
    db.connect()
    # Option A: save content strings
    contents = [p.get("content", "") for p in parsed]
    db.save_batch(contents)

    # Option B: save structured tuples (title, url, content)
    # tuples = [(p.get("title",""), p.get("url",""), p.get("content","")) for p in parsed]
    # db.save_batch(tuples)

    export_json(parsed)
    export_csv(parsed)
