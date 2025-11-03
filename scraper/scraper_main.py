import asyncio
import logging
from scraper.parser import parse_and_sanitize
from storage.database import Database

logger = logging.getLogger(__name__)


class AsyncScraper:
    def __init__(self, pages):
        self.pages = pages
        self.logger = logging.getLogger(__name__)
        self.db = Database()

    async def process_page(self, page):
        url, html = page
        try:
            data = parse_and_sanitize(html)
            await asyncio.sleep(0)  # simulate async I/O
            if isinstance(data, list):
                self.logger.info(f"Parsed {url} ({len(data)} items)")
                return data
            else:
                self.logger.info(f"Parsed {url} (1 item)")
                return [data]
        except Exception as e:
            self.logger.error(f"Scrape error {e} on {url}")
            return []

    async def run(self):
        tasks = [self.process_page(p) for p in self.pages]
        results = await asyncio.gather(*tasks)
        batch = [item for sublist in results for item in sublist if item]
        if batch:
            self.db.save_batch(batch)
            self.logger.info(f"Saved {len(batch)} records in batch")
        else:
            self.logger.warning("No records scraped")
        return batch


def run(pages):
    asyncio.run(AsyncScraper(pages).run())


def extract(pages):
    """Compatibilité ancienne API"""
    try:
        scraper = AsyncScraper(pages)
        result = asyncio.run(scraper.run())
        return result if isinstance(result, list) else []
    except Exception as e:
        logging.getLogger(__name__).error(f"Extraction failed: {e}")
        return []


def extract_data_from_html(url, html):
    """
    Parse HTML et retourne un dict structuré :
    {'title': str, 'url': url, 'content': str}
    Toujours renvoie un dict même en cas d'erreur.
    """
    try:
        parsed = parse_and_sanitize(html) or {}
        title = parsed.get("title", "") if isinstance(parsed, dict) else ""
        return {"title": title.strip(), "url": url, "content": title.strip()}
    except Exception as e:
        logger.error("parse error %s: %s", url, e)
        return {"title": "", "url": url, "content": ""}


def run_scraper(crawled_data):
    """
    Reçoit une liste de (url, html). Retourne une liste de dicts structurés.
    Gère les erreurs d’entrée et continue.
    """
    results = []
    for item in crawled_data:
        try:
            url, html = item
        except Exception:
            logger.error("bad crawled item, expected (url, html): %r", item)
            continue
        if not html:
            logger.warning("empty html for %s", url)
            continue

        record = extract_data_from_html(url, html)
        results.append(record)
    return results
