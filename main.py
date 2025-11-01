from crawler.crawler_main import crawl
from scraper.scraper_main import extract
from storage.database import save
from config.settings import load_env

def init_system():
    load_env()

def pipeline():
    pages = crawl()
    data = extract(pages)
    save(data)

def summary():
    print("Pipeline exécuté avec succès.")

def main():
    init_system()
    pipeline()
    summary()

if __name__ == "__main__":
    main()
