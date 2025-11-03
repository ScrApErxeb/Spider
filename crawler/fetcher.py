import aiohttp
import asyncio
import logging
import time
from urllib.parse import urlparse

from config.settings import HEADERS, HTTP_TIMEOUT, RETRY_COUNT, RATE_LIMIT_PER_DOMAIN


class AsyncFetcher:
    """Téléchargeur asynchrone avec réutilisation de session, retries, et rate limit par domaine."""

    def __init__(self, delay=0.5, retries=RETRY_COUNT, backoff=1.5, concurrency=5):
        self.delay = delay
        self.retries = retries
        self.backoff = backoff
        self.semaphore = asyncio.Semaphore(concurrency)
        self.logger = logging.getLogger(__name__)
        self.lock = asyncio.Lock()
        self.session = None
        self.domain_locks = {}  # {domaine: timestamp dernier accès}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def _rate_limit(self, domain: str):
        """Applique une limite de fréquence par domaine."""
        now = time.time()
        last_access = self.domain_locks.get(domain, 0)
        interval = 1.0 / max(RATE_LIMIT_PER_DOMAIN, 1)
        if now - last_access < interval:
            await asyncio.sleep(interval - (now - last_access))
        self.domain_locks[domain] = time.time()

    async def _get(self, url, headers=None):
        domain = urlparse(url).netloc
        await self._rate_limit(domain)
        async with self.session.get(url, headers=headers or HEADERS, timeout=HTTP_TIMEOUT) as resp:
            text = await resp.text(errors="ignore")
            return text, resp.status

    async def fetch(self, url, headers=None):
        """Télécharge une page avec retries et backoff exponentiel."""
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


async def fetch_url(url, headers=None, timeout=HTTP_TIMEOUT, retries=RETRY_COUNT):
    """Version simplifiée pour usage ponctuel."""
    async with aiohttp.ClientSession(headers=headers or HEADERS) as session:
        for attempt in range(1, retries + 1):
            try:
                async with session.get(url, timeout=timeout) as resp:
                    if resp.status == 200:
                        text = await resp.text(errors="ignore")
                        logging.debug(f"Fetched: {url}")
                        return text
                    else:
                        logging.warning(f"Status {resp.status} for {url}")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logging.warning(f"Tentative {attempt}/{retries} échouée pour {url}: {e}")
    return None
