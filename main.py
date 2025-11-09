import asyncio
import logging
import os
import yaml
from logging.handlers import RotatingFileHandler

from storage.validators import validate_pages
from config.settings import (
    RESPECT_ROBOTS,
    HEADERS,
    HTTP_TIMEOUT,
    RETRY_COUNT,
    DB_PATH,
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL,
    ALLOWED_LANGS,
    CONFIG_PATH,
    START_URLS as CONFIG_URLS,
)
from utils.handlers import RobotsHandler
from crawler.crawler_main import run_crawler
from scraper.scraper_main import run_scraper
from storage.database import Database
from storage.exporter import export_json, export_csv


# === CHARGEMENT DES URLS ===
def get_start_urls():
    import sys
    if len(sys.argv) > 1:
        return sys.argv[1:]
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r", encoding="utf-8") as f:
            urls = [u.strip() for u in f if u.strip()]
            if urls:
                return urls
    if CONFIG_URLS:
        return CONFIG_URLS
    return ["http://example.com"]


# === FLUSH CALLBACK ===
async def flush_to_scraper(pages_batch):
    """Appelé par le crawler tous les 20 résultats."""
    logging.info(f"Flush: traitement d’un lot de {len(pages_batch)} pages")
    parsed = run_scraper(pages_batch)  # Extraction
    validated = validate_pages(parsed)
    tuples = [(p["title"], str(p["url"]), p["description"]) for p in validated]
    if tuples:
        with Database(DB_PATH) as db:
            db.save_batch(tuples)
        logging.info(f"{len(tuples)} enregistrements sauvegardés (batch flush)")
    else:
        logging.warning("Aucune donnée valide à sauvegarder dans ce lot")


# === PIPELINE PRINCIPAL ===
async def main():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=[handler, logging.StreamHandler()])

    logging.info("=== DÉMARRAGE DU PIPELINE ===")

    start_urls = get_start_urls()
    logging.info(f"URLs de départ : {start_urls}")

    # Filtrage robots.txt
    if RESPECT_ROBOTS:
        allowed_urls = []
        for url in start_urls:
            robots = RobotsHandler()
            if await robots.is_allowed(url):
                allowed_urls.append(url)
        start_urls = allowed_urls or start_urls
        logging.info(f"{len(start_urls)} URLs après filtrage robots.txt")

    # --- CRAWLER AVEC FLUSH ---
    crawled = await run_crawler(
        start_urls=start_urls,
        headers=HEADERS,
        timeout=HTTP_TIMEOUT,
        retries=RETRY_COUNT,
        allowed_langs=ALLOWED_LANGS,
        flush_callback=flush_to_scraper,  # ici la fonction de flush
    )

    # --- FIN DE PIPELINE ---
    logging.info(f"{len(crawled)} pages récupérées au total (flush inclus)")
    json_path = export_json(crawled)
    csv_path = export_csv(crawled)
    logging.info(f"Exports terminés : {json_path}, {csv_path}")
    logging.info("=== PIPELINE TERMINÉ ===")
    print(f"Pipeline terminé : {len(crawled)} pages traitées.")


if __name__ == "__main__":
    asyncio.run(main())
