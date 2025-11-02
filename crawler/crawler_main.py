import asyncio
import logging
from crawler.queue_manager import QueueManager
from crawler.fetcher import AsyncFetcher
from .fetcher import fetch_page
from .robots_handler import allowed

import logging


logger = logging.getLogger(__name__)


class AsyncCrawler:
    def __init__(self, start_urls):
        self.start_urls = start_urls
        self.q = QueueManager()
        for u in start_urls:
            self.q.enqueue(u)
        self.fetcher = AsyncFetcher()
        self.logger = logging.getLogger(__name__)

    async def visit(self, url):
        html = await self.fetcher.fetch(url)
        if html:
            self.logger.info(f"Visited {url} ({len(html)} chars)")
            # placeholder : collect links or data here
        else:
            self.logger.warning(f"Failed to fetch {url}")

    async def crawl(self):
        tasks = []
        while not self.q.is_empty():
            url = self.q.dequeue()
            tasks.append(asyncio.create_task(self.visit(url)))
        await asyncio.gather(*tasks)
        self.logger.info("Crawl complete")

def run(start_urls):
    crawler = AsyncCrawler(start_urls)
    asyncio.run(crawler.crawl())



def run_crawler(start_urls):
    """
    Retourne une liste de tuples (url, html).
    Tolère les échecs et continue.
    """
    q = QueueManager(start_urls)
    results = []

    while not q.empty():
        url = q.dequeue()
        if not url:
            continue
        try:
            html = fetch_page(url)
        except Exception as e:
            logger.error("fetch error %s: %s", url, e)
            html = None
        if html:
            results.append((url, html))
    return results