"""
Main pipeline orchestrating:
- Crawler: récupère les pages à partir des URLs sources.
- Scraper: extrait les données pertinentes.
- Storage: enregistre dans la base et exporte en JSON/CSV.

Version: 0.8.4
Auteur: ScrApErxeb
"""

import logging
import sys
import os
import yaml
from logging.handlers import RotatingFileHandler

from config.settings import (
    HEADERS, HTTP_TIMEOUT, RETRY_COUNT,
    DB_PATH, LOG_FILE, LOG_FORMAT, LOG_LEVEL,
    ALLOWED_LANGS, CONFIG_PATH
)

from crawler.crawler_main import run_crawler
from scraper.scraper_main import run_scraper
from storage.database import Database
from storage.exporter import export_json, export_csv


# =====================================================================
# === SOURCES D’URL ===================================================
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


from config.settings import START_URLS as CONFIG_URLS

def get_start_urls():
    """Détermine la liste d'URLs à crawler.
    Ordre de priorité :
    1. Arguments CLI
    2. Fichier urls.txt
    3. config.yaml
    4. Valeur par défaut
    """
    import sys, logging

    # 1. Ligne de commande
    if len(sys.argv) > 1:
        return sys.argv[1:]

    # 2. Fichier urls.txt
    try:
        with open("urls.txt", "r", encoding="utf-8") as f:
            urls = [u.strip() for u in f if u.strip()]
            if urls:
                return urls
    except FileNotFoundError:
        logging.warning("urls.txt introuvable, fallback activé.")

    # 3. config.yaml
    if CONFIG_URLS:
        return CONFIG_URLS

    # 4. Défaut
    return ["http://example.com"]



# =====================================================================
# === MAIN PIPELINE ===================================================
# =====================================================================

def main():
    """Pipeline principal orchestrant crawler → scraper → stockage/export."""
    # --- LOGGING SETUP ------------------------------------------------
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=[handler, logging.StreamHandler()])

    logging.info("=== DÉMARRAGE DU PIPELINE ===")

    # --- INPUT --------------------------------------------------------
    start_urls = get_start_urls()
    logging.info(f"URLs de départ : {start_urls}")

    # --- CRAWLER ------------------------------------------------------
    crawled = run_crawler(
        start_urls=start_urls,
        headers=HEADERS,
        timeout=HTTP_TIMEOUT,
        retries=RETRY_COUNT,
        allowed_langs=ALLOWED_LANGS
    )
    logging.info(f"{len(crawled)} pages récupérées")

    # --- SCRAPER ------------------------------------------------------
    parsed = run_scraper(crawled)
    logging.info(f"{len(parsed)} éléments analysés")

    # --- DATABASE -----------------------------------------------------
    db = Database(path=DB_PATH)
    db.connect()
    tuples = [
        (
            p.get("title", ""),
            p.get("url", ""),
            p.get("description", p.get("content", ""))
        )
        for p in parsed
    ]
    db.save_batch(tuples)
    db.close()
    logging.info(f"{len(tuples)} enregistrements sauvegardés")

    # --- EXPORTS ------------------------------------------------------
    json_path = export_json(parsed)
    csv_path = export_csv(parsed)
    logging.info(f"Exports terminés : {json_path}, {csv_path}")

    logging.info("=== PIPELINE TERMINÉ ===")
    print(f"Pipeline terminé : {len(parsed)} éléments extraits et enregistrés.")


# =====================================================================
# === EXECUTION DIRECTE ==============================================
# =====================================================================

if __name__ == "__main__":
    main()
