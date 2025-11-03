"""
Main pipeline orchestrating:
- Crawler: récupère les pages à partir des URLs sources.
- Scraper: extrait les données pertinentes.
- Storage: enregistre dans la base et exporte en JSON/CSV.

Version: 0.8.5
Auteur: ScrApErxeb
"""

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
)

from utils.handlers import RobotsHandler
from crawler.crawler_main import run_crawler
from scraper.scraper_main import run_scraper
from storage.database import Database
from storage.exporter import export_json, export_csv
from config.settings import START_URLS as CONFIG_URLS




# =====================================================================
# === CHARGEMENT DES URLS =============================================
# =====================================================================

def load_urls_from_yaml(default=["http://example.com"]):
    """Charge les URLs depuis config.yaml, sinon renvoie la valeur par défaut."""
    try:
        if not os.path.exists(CONFIG_PATH):
            logging.warning("config.yaml introuvable, fallback activé.")
            return default
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        urls = cfg.get("sources")
        if not urls:
            logging.warning("Section 'sources' absente du YAML, fallback activé.")
            return default
        urls = [u.strip() for u in urls if isinstance(u, str) and u.strip()]
        return urls or default
    except Exception as e:
        logging.error(f"Erreur YAML ({CONFIG_PATH}): {e}, fallback utilisé.")
        return default


def load_urls_from_txt(default=["http://example.com"]):
    """Lit les URLs depuis urls.txt si présent."""
    if not os.path.exists("urls.txt"):
        logging.warning("urls.txt introuvable, fallback activé.")
        return default
    try:
        with open("urls.txt", "r", encoding="utf-8") as f:
            urls = [u.strip() for u in f if u.strip()]
        return urls or default
    except Exception as e:
        logging.error(f"Erreur lecture urls.txt: {e}, fallback utilisé.")
        return default


def get_start_urls():
    """Détermine la liste d'URLs à crawler.
    Priorité :
      1. Arguments CLI
      2. Fichier urls.txt
      3. config.yaml
      4. Valeur par défaut
    """
    import sys

    if len(sys.argv) > 1:
        return sys.argv[1:]
    try:
        with open("urls.txt", "r", encoding="utf-8") as f:
            urls = [u.strip() for u in f if u.strip()]
            if urls:
                return urls
    except FileNotFoundError:
        logging.warning("urls.txt introuvable, fallback activé.")

    if CONFIG_URLS:
        return CONFIG_URLS
    return ["http://example.com"]


# =====================================================================
# === PIPELINE PRINCIPAL ==============================================
# =====================================================================

async def main():
    """Pipeline principal orchestrant crawler → scraper → stockage/export."""
    # --- LOGGING SETUP ---
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=[handler, logging.StreamHandler()])

    logging.info("=== DÉMARRAGE DU PIPELINE ===")

    # --- INPUT ---
    start_urls = get_start_urls()
    logging.info(f"URLs de départ : {start_urls}")

    # --- FILTRAGE ROBOTS.TXT ---
    if RESPECT_ROBOTS:
        allowed_urls = []
        for url in start_urls:
            robots = RobotsHandler()
            allowed = await robots.is_allowed(url)
            if not allowed:
                logging.warning(f"Bloqué par robots.txt : {url}")
                continue
            allowed_urls.append(url)
        start_urls = allowed_urls or start_urls
        logging.info(f"Filtrage robots.txt actif, {len(start_urls)} URLs restantes.")
    else:
        logging.info("Respect de robots.txt désactivé par configuration.")

    # --- CRAWLER ---
    crawled = await run_crawler(
        start_urls=start_urls,
        headers=HEADERS,
        timeout=HTTP_TIMEOUT,
        retries=RETRY_COUNT,
        allowed_langs=ALLOWED_LANGS,
    )
    logging.info(f"{len(crawled)} pages récupérées")

    # --- SCRAPER ---
    parsed = run_scraper(crawled)
    logging.info(f"{len(parsed)} éléments analysés")


    # --- DATABASE ---
    validated = validate_pages(parsed)
    tuples = [
    (p["title"], str(p["url"]), p["description"])
    for p in validated
    ]
    with Database(DB_PATH) as db:
        db.save_batch(tuples)
    logging.info(f"{len(tuples)} enregistrements sauvegardés")


    # --- EXPORTS ---
    json_path = export_json(parsed)
    csv_path = export_csv(parsed)
    logging.info(f"Exports terminés : {json_path}, {csv_path}")

    logging.info("=== PIPELINE TERMINÉ ===")
    print(f"Pipeline terminé : {len(parsed)} éléments extraits et enregistrés.")


# =====================================================================
# === EXECUTION DIRECTE ==============================================
# =====================================================================

if __name__ == "__main__":
    asyncio.run(main())
