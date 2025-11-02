import asyncio
import logging
from scraper.parser import parse_html
from scraper.parser import sanitize
from scraper.async_scraper import AsyncScraper
from storage.database import Database

class AsyncScraper:
    def __init__(self, pages):
        self.pages = pages
        self.logger = logging.getLogger(__name__)
        self.db = Database()

    async def process_page(self, page):
        html, url = page
        try:
            data = parse_html(html)
            clean = sanitize(data)
            await asyncio.sleep(0)  # simulate async I/O
            self.logger.info(f"Parsed {url} ({len(clean)} items)")
            return clean
        except Exception as e:
            self.logger.error(f"Scrape error {e} on {url}")
            return []

    async def run(self):
        tasks = [self.process_page(p) for p in self.pages]
        results = await asyncio.gather(*tasks)
        batch = [item for sublist in results for item in sublist]
        if batch:
            self.db.save_batch(batch)
            self.logger.info(f"Saved {len(batch)} records in batch")
        else:
            self.logger.warning("No records scraped")
        return batch  # <-- ajout du retour


def run(pages):
    asyncio.run(AsyncScraper(pages).run())

# compatibilité ancienne API
def extract(pages):
    try:
        scraper = AsyncScraper(pages)
        result = asyncio.run(scraper.run())
        if not isinstance(result, list):
            return []
        return result
    except Exception as e:
        logging.getLogger(__name__).error(f"Extraction failed: {e}")
        return []
    



# scraper/scraper_main.py

logger = logging.getLogger(__name__)

def extract_data_from_html(url, html):
    """
    Parse HTML et retourne un dict structuré:
    {'title': str, 'url': url, 'content': str}
    Toujours renvoie un dict même en cas d'erreur (valeurs vides).
    """
    try:
        parsed = parse_html(html) or {}
        # parsed peut contenir 'title', 'links', etc.
        title = parsed.get("title", "") if isinstance(parsed, dict) else ""
        # content = title + maybe first paragraph; keep simple
        content = title.strip()
        return {"title": title, "url": url, "content": content}
    except Exception as e:
        logger.error("parse error %s: %s", url, e)
        return {"title": "", "url": url, "content": ""}

def run_scraper(crawled_data):
    """
    Reçoit liste de (url, html). Retourne liste de dicts structurés.
    Gère les erreurs par entrée et continue.
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
        # optional cleaning step (expects list or dict->wrap)
        try:
            # sanitize expects a list of records in earlier code; adapt safely
            cleaned = sanitize([record]) if callable(sanitize) else [record]
            # sanitize returns a list; take first if exists
            if cleaned:
                results.append(cleaned[0] if isinstance(cleaned[0], dict) else record)
            else:
                results.append(record)
        except Exception as e:
            logger.error("clean error %s: %s", url, e)
            results.append(record)
    return results
