import logging
from crawler.crawler_main import crawl
from scraper.scraper_main import extract
from storage.database import save
from storage.exporter import export_json, export_csv
from config.settings import load_env, get_root_urls, get_delay


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


logger = logging.getLogger("main")

def init_system():
    load_env()
    logger.info("Configuration chargée.")

def pipeline():
    urls = get_root_urls()
    delay = get_delay()
    logger.info(f"Début du crawl sur {urls} (delay={delay}s)")
    pages = crawl(start_urls=urls)
    data = extract(pages)
    save(data)
    export_json(data)
    export_csv(data)
    logger.info("Pipeline terminé.")

def summary():
    logger.info("Pipeline exécuté avec succès.")

def main():
    init_system()
    pipeline()
    summary()

if __name__ == "__main__":
    main()
