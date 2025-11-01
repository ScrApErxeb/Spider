import requests
import time
import logging

logger = logging.getLogger("crawler.fetcher")

class Fetcher:
    def __init__(self, delay=1, retries=2, backoff=0.5):
        self.delay = delay
        self.retries = retries
        self.backoff = backoff

    def _get(self, url, headers=None, timeout=5):
        return requests.get(url, headers=headers, timeout=timeout)

    def fetch(self, url, headers=None):
        time.sleep(self.delay)
        last_exc = None
        for attempt in range(1, self.retries + 2):
            try:
                resp = self._get(url, headers=headers)
                resp.raise_for_status()
                return resp.text
            except requests.RequestException as e:
                last_exc = e
                logger.warning("fetch fail [%s] attempt %d: %s", url, attempt, e)
                time.sleep(self.backoff * attempt)
        logger.error("fetch failed after retries: %s", url)
        raise last_exc
