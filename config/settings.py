from pathlib import Path
import yaml, logging, logging.config
from aiohttp import ClientTimeout

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

def load_config():
    if not CONFIG_PATH.exists():
        logging.warning(f"{CONFIG_PATH} introuvable. Valeurs par défaut utilisées.")
        return {}
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# === Timeout HTTP ===
t = config.get("crawler", {}).get("timeout", 10)
if isinstance(t, dict):
    HTTP_TIMEOUT = ClientTimeout(**t)
else:
    try:
        HTTP_TIMEOUT = ClientTimeout(total=float(t))
    except Exception:
        HTTP_TIMEOUT = ClientTimeout(total=10)

# === Paramètres principaux ===
START_URLS = config.get("crawler", {}).get("start_urls", ["http://example.com"])
HEADERS = config.get("crawler", {}).get("headers", {})
RETRY_COUNT = config.get("crawler", {}).get("retries", 3)
MAX_PAGES = config.get("crawler", {}).get("max_pages", 50)
RESPECT_ROBOTS = config.get("crawler", {}).get("robots")
ALLOWED_LANGS = set(config.get("crawler", {}).get("languages", ["en"]))

# === Limitation de vitesse ===
RATE_LIMIT = config.get("crawler", {}).get("rate_limit", {})
RATE_LIMIT_ENABLED = RATE_LIMIT.get("enabled", False)
RATE_LIMIT_DELAY = RATE_LIMIT.get("delay", 0)

# === Cache HTTP ===
HTTP_CACHE = config.get("http_cache", {})
HTTP_CACHE_ENABLED = HTTP_CACHE.get("enabled", True)
HTTP_CACHE_TTL = HTTP_CACHE.get("ttl", 300)

# === Stockage ===
DB_PATH = config.get("storage", {}).get("database_path", "data/project.db")
EXPORT_DIR = config.get("storage", {}).get("export_dir", "exports")

# === Logging ===
if "version" in config:
    logging.config.dictConfig(config)
else:
    logging.basicConfig(
        level=getattr(logging, config.get("logging", {}).get("level", "INFO").upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

LOG_FILE = config.get("logging", {}).get("file", "logs/pipeline.log")
LOG_LEVEL = getattr(logging, config.get("logging", {}).get("level", "INFO").upper(), logging.INFO)
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

logging.info("Configuration chargée avec succès.")

if __name__ == "__main__":
    print("Chargement config :", bool(config))
    print("URLs de départ :", START_URLS)
    print("Respect robots.txt :", RESPECT_ROBOTS)
