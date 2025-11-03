import asyncio
import logging
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from crawler.fetcher import fetch_url
from config.settings import MAX_PAGES



def is_allowed_language(html_content, allowed_langs):
    match = re.search(r'<html[^>]+lang=["\']?([a-zA-Z-]+)', html_content, re.IGNORECASE)
    if match:
        lang = match.group(1).split('-')[0].lower()
        return lang in allowed_langs
    return False


async def crawl_page(url, headers, timeout, retries, allowed_langs, visited, to_visit, results):
    try:
        html = await fetch_url(url, headers=headers, timeout=timeout, retries=retries)
        if not html:
            logging.warning(f"Échec : {url}")
            return

        if not is_allowed_language(html, allowed_langs):
            logging.info(f"Ignoré (langue non autorisée) : {url}")
            return

        results.append((url, html))
        visited.add(url)
        logging.info(f"OK: {url} ({len(results)}/{MAX_PAGES})")

        # Extraction des nouveaux liens
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all("a", href=True):
            abs_url = urljoin(url, tag["href"])
            if abs_url.startswith(("http://", "https://")):
                domain = urlparse(abs_url).netloc
                if domain and abs_url not in visited and abs_url not in to_visit and len(visited) + len(to_visit) < MAX_PAGES:
                    to_visit.append(abs_url)

    except Exception as e:
        logging.error(f"Erreur {url}: {e}")


async def async_run_crawler(start_urls, headers, timeout, retries, allowed_langs):
    visited = set()
    to_visit = list(start_urls)
    results = []

    while to_visit and len(visited) < MAX_PAGES:
        current_batch = to_visit[:5]
        to_visit = to_visit[5:]

        tasks = [
            crawl_page(u, headers, timeout, retries, allowed_langs, visited, to_visit, results)
            for u in current_batch
        ]
        await asyncio.gather(*tasks)

    return results


def run_crawler(start_urls, headers, timeout, retries, allowed_langs):
    logging.info(f"Crawl lancé avec {len(start_urls)} URL(s)")
    try:
        results = asyncio.run(async_run_crawler(start_urls, headers, timeout, retries, allowed_langs))
    except Exception as e:
        logging.error(f"Erreur fatale du crawler : {e}")
        results = []

    logging.info(f"{len(results)} pages valides collectées.")
    return results
