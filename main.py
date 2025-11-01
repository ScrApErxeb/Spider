import logging
import time
from crawler.crawler_main import crawl
from scraper.scraper_main import extract
from storage.database import save
from storage.exporter import export_json, export_csv
from config.settings import load_env, get_root_urls, get_delay

logger = logging.getLogger("main")

def init_system():
    load_env()
    logger.info("Configuration chargée.")

def pipeline():
    start_time = time.time()
    urls = get_root_urls()
    logger.info("Début du crawl sur %s", urls)
    pages = []
    try:
        pages = crawl(start_urls=urls)
    except Exception as e:
        logger.exception("Erreur lors du crawl: %s", e)

    logger.info("Pages récupérées: %d", len(pages))
    data = []
    try:
        data = extract(pages)
    except Exception as e:
        logger.exception("Erreur lors de l'extraction: %s", e)

    try:
        save(data)
        export_json(data)
        export_csv(data)
    except Exception as e:
        logger.exception("Erreur lors du stockage/export: %s", e)

    duration = time.time() - start_time
    logger.info("Pipeline terminé en %.2fs. pages=%d items=%d", duration, len(pages), len(data))

def main():
    try:
        init_system()
        pipeline()
        logger.info("Execution normale.")
    except Exception as e:
        logger.exception("Crash non attendu: %s", e)

if __name__ == "__main__":
    main()
