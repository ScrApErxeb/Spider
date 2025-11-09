import asyncio
import logging
from scraper.parser import parse_and_sanitize
from storage.database import Database
from config.settings import SCRAPER_FLUSH_SIZE

logger = logging.getLogger(__name__)


class AsyncScraper:
    def __init__(self, pages, flush_size=SCRAPER_FLUSH_SIZE):
        self.pages = pages
        self.flush_size = flush_size
        self.logger = logging.getLogger(__name__)
        self.db = Database()

    async def process_page(self, page):
        url, html = page
        try:
            data = parse_and_sanitize(html)
            await asyncio.sleep(0)
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
        batch = []
        for i, page in enumerate(self.pages, 1):
            data = await self.process_page(page)
            batch.extend(data)
            if len(batch) >= 20:
                self.db.save_batch(batch)
                batch.clear()
                self.logger.info(f"Flush at {i}/{len(self.pages)}")

        if batch:  # flush final
            self.db.save_batch(batch)
            self.logger.info("Final flush done")


def run(pages):
    asyncio.run(AsyncScraper(pages).run())


def extract(pages):
    try:
        scraper = AsyncScraper(pages)
        result = asyncio.run(scraper.run())
        return result if isinstance(result, list) else []
    except Exception as e:
        logging.getLogger(__name__).error(f"Extraction failed: {e}")
        return []
