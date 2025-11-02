import asyncio
import logging
from scraper.parser_html import parse_html
from scraper.cleaner import sanitize
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
            await asyncio.sleep(0)  # simulation d’I/O
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
        return batch
