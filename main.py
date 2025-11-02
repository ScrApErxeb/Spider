"""
Main pipeline orchestrating:
- Crawler: récupère les pages à partir des URLs sources.
- Scraper: extrait les données pertinentes.
- Storage: enregistre dans la base et exporte en JSON/CSV.

Version: 0.8.2
Auteur: ScrApErxeb
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler

from config.settings import (
    HEADERS, HTTP_TIMEOUT, RETRY_COUNT,
    DB_PATH, LOG_FILE, LOG_FORMAT, LOG_LEVEL, ALLOWED_LANGS
)


from crawler.crawler_main import run_crawler
from scraper.scraper_main import run_scraper
from storage.database import Database
from utils.export_utils import export_json, export_csv


def get_start_urls():
    """Lit les URLs à partir des arguments CLI ou du fichier urls.txt."""
    if len(sys.argv) > 1:
        return sys.argv[1:]
    try:
        with open("urls.txt", "r", encoding="utf-8") as f:
            return [u.strip() for u in f if u.strip()]
    except FileNotFoundError:
        logging.warning("Aucune URL fournie. Fichier urls.txt manquant.")
        return ["http://google.com"]


def main():
    """Pipeline principal orchestrant crawler → scraper → stockage/export."""
    # === LOGGING SETUP ======================================================
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=[handler, logging.StreamHandler()])

    logging.info("=== DÉMARRAGE DU PIPELINE ===")

    # === INPUT ==============================================================
    start_urls = get_start_urls()
    logging.debug(f"URLs de départ : {start_urls}")

    # === CRAWLER ============================================================
    crawled = run_crawler(
    start_urls=start_urls,
    headers=HEADERS,
    timeout=HTTP_TIMEOUT,
    retries=RETRY_COUNT,
    allowed_langs=ALLOWED_LANGS
)

    logging.info(f"{len(crawled)} pages récupérées")
    if crawled:
        sample = str(crawled[:1])
        logging.debug(f"Crawled sample ({len(sample)} chars): {sample[:500]}{'...' if len(sample) > 500 else ''}")

    # === SCRAPER ============================================================
    parsed = run_scraper(crawled)
    logging.info(f"{len(parsed)} éléments analysés")
    if parsed:
        logging.debug(f"Parsed sample: {parsed[:1]}")

    # === DATABASE ==========================================================
    db = Database(path=DB_PATH)
    db.connect()
    tuples = [(p.get("title", ""), p.get("url", ""), p.get("content", "")) for p in parsed]
    db.save_batch(tuples)
    logging.info(f"{len(tuples)} enregistrements sauvegardés")

    # === EXPORTS ===========================================================
    json_path = export_json(parsed)
    csv_path = export_csv(parsed)
    logging.info(f"Exports terminés : {json_path}, {csv_path}")

    logging.info("=== PIPELINE TERMINÉ ===")
    print(f"Pipeline terminé : {len(parsed)} éléments extraits et enregistrés.")


if __name__ == "__main__":
    main()
