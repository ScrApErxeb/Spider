import aiohttp
import asyncio
import logging


HEADERS = {
    "User-Agent": "SpiderBot/0.8 (+https://github.com/ScrApErxeb/Spider)",
}
TIMEOUT = 15
RETRY_COUNT = 3


class AsyncFetcher:
    """Téléchargeur asynchrone réutilisant une seule session HTTP."""
    def __init__(self, delay=0.5, retries=3, backoff=1.5, concurrency=5):
        self.delay = delay
        self.retries = retries
        self.backoff = backoff
        self.semaphore = asyncio.Semaphore(concurrency)
        self.logger = logging.getLogger(__name__)
        self.lock = asyncio.Lock()
        self.session = None  # session HTTP unique

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def _get(self, url, headers=None):
        async with self.session.get(url, headers=headers or HEADERS, timeout=TIMEOUT) as resp:
            text = await resp.text()
            return text, resp.status

    async def fetch(self, url, headers=None):
        async with self.semaphore:
            delay = self.delay
            for attempt in range(1, self.retries + 2):
                try:
                    text, status = await self._get(url, headers)
                    if status == 200:
                        async with self.lock:
                            self.logger.debug(f"Fetched: {url}")
                        await asyncio.sleep(self.delay)
                        return text
                    else:
                        async with self.lock:
                            self.logger.warning(f"Status {status} for {url}")
                except Exception as e:
                    async with self.lock:
                        self.logger.error(f"Fetch error {e} for {url}, retry {attempt}")
                    await asyncio.sleep(delay)
                    delay *= self.backoff
            return None


async def fetch_url(url, headers=None, timeout=10, retries=3):
    """Utilitaire simplifié réutilisant une session unique."""
    async with aiohttp.ClientSession(headers=headers or HEADERS) as session:
        for attempt in range(1, retries + 1):
            try:
                async with session.get(url, timeout=timeout) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        logging.debug(f"Fetched: {url}")
                        return text
                    else:
                        logging.warning(f"Status {resp.status} for {url}")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logging.warning(f"Tentative {attempt}/{retries} échouée pour {url}: {e}")
    return None
