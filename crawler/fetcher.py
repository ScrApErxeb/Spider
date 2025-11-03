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

    async def fetch(self, url, headers=None, timeout=10, retries=3):
        from aiohttp import ClientTimeout

        # --- normaliser timeout ---
        if isinstance(timeout, dict):
            timeout = ClientTimeout(**timeout)
        elif not isinstance(timeout, ClientTimeout):
            timeout = ClientTimeout(total=float(timeout))

        for attempt in range(1, retries + 1):
            try:
                async with self.session.get(url, headers=headers, timeout=timeout) as resp:
                    if resp.status == 200:
                        return await resp.text(errors="ignore")
                    else:
                        logging.warning(f"Status {resp.status} pour {url}")
            except Exception as e:
                logging.error(f"Fetch error {e} pour {url}, retry {attempt}")
