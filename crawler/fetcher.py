import aiohttp
import asyncio
import logging

class AsyncFetcher:
    def __init__(self, delay=0.5, retries=2, backoff=1.5, concurrency=5):
        self.delay = delay
        self.retries = retries
        self.backoff = backoff
        self.semaphore = asyncio.Semaphore(concurrency)
        self.logger = logging.getLogger(__name__)

    async def _get(self, session, url, headers=None):
        async with session.get(url, headers=headers, timeout=10) as resp:
            text = await resp.text()
            return text, resp.status

    async def fetch(self, url, headers=None):
        async with self.semaphore:
            delay = self.delay
            for attempt in range(self.retries + 1):
                try:
                    async with aiohttp.ClientSession() as session:
                        text, status = await self._get(session, url, headers)
                        if status == 200:
                            self.logger.debug(f"Fetched: {url}")
                            await asyncio.sleep(self.delay)
                            return text
                        else:
                            self.logger.warning(f"Status {status} for {url}")
                except Exception as e:
                    self.logger.error(f"Fetch error {e} for {url}, retry {attempt}")
                    await asyncio.sleep(delay)
                    delay *= self.backoff
            return None
