import asyncio
import logging
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from crawler.fetcher import AsyncFetcher
from utils.handlers import RobotsHandler
from config.settings import MAX_PAGES, RESPECT_ROBOTS, config

# --- RATE LIMITING PAR DOMAINE ---
RATE_LIMITS = config.get("crawler", {}).get("rate_limit_per_domain", 1)
_domain_locks = {}
_domain_timestamps = {}


def _get_domain_lock(domain):
    if domain not in _domain_locks:
        _domain_locks[domain] = asyncio.Lock()
    return _domain_locks[domain]


async def _rate_limit(domain):
    """Limite les requêtes par domaine selon rate_limit_per_domain (req/s)."""
    if RATE_LIMITS <= 0:
        return
    delay = 1 / RATE_LIMITS
    lock = _get_domain_lock(domain)
    async with lock:
        last = _domain_timestamps.get(domain, 0)
        now = asyncio.get_event_loop().time()
        wait_time = delay - (now - last)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        _domain_timestamps[domain] = asyncio.get_event_loop().time()


def is_allowed_language(html_content, allowed_langs):
    match = re.search(r'<html[^>]+lang=["\']?([a-zA-Z-]+)', html_content, re.IGNORECASE)
    if match:
        lang = match.group(1).split('-')[0].lower()
        return lang in allowed_langs
    return False


async def crawl_page(fetcher, url, headers, timeout, retries, allowed_langs, visited, to_visit, results):
    try:
        domain = urlparse(url).netloc

        # Respect robots.txt
        robots = RobotsHandler()
        if not await robots.is_allowed(url):
            logging.info(f"Robots.txt interdit : {url}")
            return

        await _rate_limit(domain)  # Appliquer rate limiting

        html = await fetcher.fetch(url, headers=headers)
        if not html:
            logging.warning(f"Échec : {url}")
            return

        if not is_allowed_language(html, allowed_langs):
            logging.info(f"Ignoré (langue non autorisée) : {url}")
            return

        results.append({"url": url, "content": html})
        visited.add(url)
        logging.info(f"OK: {url} ({len(results)}/{MAX_PAGES})")

        # Extraction de nouveaux liens
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all("a", href=True):
            abs_url = urljoin(url, tag["href"])
            if abs_url.startswith(("http://", "https://")):
                domain = urlparse(abs_url).netloc
                if (
                    domain
                    and abs_url not in visited
                    and abs_url not in to_visit
                    and len(visited) + len(to_visit) < MAX_PAGES
                ):
                    to_visit.append(abs_url)

    except Exception as e:
        logging.error(f"Erreur {url}: {e}")


async def async_run_crawler(start_urls, headers, timeout, retries, allowed_langs):
    visited = set()
    to_visit = list(start_urls)
    results = []

    async with AsyncFetcher() as fetcher:
        while to_visit and len(visited) < MAX_PAGES:
            current_batch = to_visit[:5]
            to_visit = to_visit[5:]

            tasks = [
                crawl_page(fetcher, u, headers, timeout, retries, allowed_langs, visited, to_visit, results)
                for u in current_batch
            ]
            await asyncio.gather(*tasks)

    return results


async def run_crawler(start_urls, headers, timeout, retries, allowed_langs):
    """Crawler principal (asynchrone)."""
    visited = set()
    to_visit = list(start_urls)
    results = []

    async with AsyncFetcher() as fetcher:
        while to_visit and len(visited) < MAX_PAGES:
            current_batch = to_visit[:5]
            to_visit = to_visit[5:]
            tasks = [
                crawl_page(fetcher, u, headers, timeout, retries, allowed_langs, visited, to_visit, results)
                for u in current_batch
            ]
            await asyncio.gather(*tasks)

    return results
