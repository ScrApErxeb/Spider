import aiohttp
import asyncio
import logging


HEADERS = {
    "User-Agent": "SpiderBot/0.8 (+https://github.com/ScrApErxeb/Spider)",
}
TIMEOUT = 15
RETRY_COUNT = 3



class AsyncFetcher:
    def __init__(self, delay=0.5, retries=2, backoff=1.5, concurrency=5):
        self.delay = delay
        self.retries = retries
        self.backoff = backoff
        self.semaphore = asyncio.Semaphore(concurrency)
        self.logger = logging.getLogger(__name__)

    async def _get(self, session, url, headers=None):
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT) as resp:
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

async def fetch_url(url, headers=None, timeout=10, retries=3):
    """Télécharge le contenu HTML d'une URL avec gestion des erreurs et retries."""
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=timeout) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        logging.debug(f"Fetched: {url}")
                        return text
                    else:
                        logging.warning(f"Status {resp.status} for {url}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.warning(f"Tentative {attempt+1}/{retries} échouée pour {url}: {e}")
    return None