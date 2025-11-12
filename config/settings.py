from pathlib import Path
import yaml
import logging
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

# === CRAWLER ===
CRAWLER = config.get("crawler", {})
START_URLS = CRAWLER.get("start_urls", [])
HEADERS = CRAWLER.get("headers", {})
TIMEOUT = CRAWLER.get("timeout", 10)
VERIFY_SSL = CRAWLER.get("verify_ssl", True)
RETRIES = CRAWLER.get("retries", 3)
MAX_PAGES = CRAWLER.get("max_pages", 50)
SCRAPER_FLUSH_SIZE = 20
RESPECT_ROBOTS = CRAWLER.get("robots", False)
RATE_LIMIT_PER_DOMAIN = CRAWLER.get("rate_limit_per_domain", 1)
RATE_LIMIT_ENABLED = CRAWLER.get("rate_limit_enabled", True)
RATE_LIMIT_DELAY = RATE_LIMIT_PER_DOMAIN  # requêtes par seconde
# === Réessais réseau ===
RETRY_COUNT = config.get("crawler", {}).get("retries", 3)

# === Langues autorisées ===
ALLOWED_LANGS = config.get("crawler", {}).get("allowed_langs", ["en", "fr"])


# === CACHE & STORAGE ===
HTTP_CACHE = config.get("http_cache", {})
HTTP_CACHE_ENABLED = HTTP_CACHE.get("enabled", True)
HTTP_CACHE_TTL = HTTP_CACHE.get("ttl", 300)

STORAGE = config.get("storage", {})
DB_PATH = STORAGE.get("database_path", "data/project.db")
EXPORT_DIR = STORAGE.get("export_dir", "exports")

# === LOGGING SIMPLE ===
LOG_FILE = config.get("logging", {}).get("file", "logs/pipeline.log")
LOG_LEVEL = getattr(logging, config.get("logging", {}).get("level", "INFO").upper(), logging.INFO)
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


# Resolve LOG_FILE against BASE_DIR and ensure parent directory exists so
# creating a FileHandler won't raise FileNotFoundError when 'logs/' is missing.
from pathlib import Path as _Path
_log_path = _Path(LOG_FILE)
if not _log_path.is_absolute():
    _log_path = BASE_DIR / _log_path
try:
    _log_path.parent.mkdir(parents=True, exist_ok=True)
except Exception:
    # If we cannot create the directory, fall back to stdout-only logging
    logging.warning(f"Impossible de créer le répertoire de logs: {_log_path.parent}")

# Use the resolved path when attaching the FileHandler
LOG_FILE_PATH = str(_log_path)

# ...
TIMEOUT = CRAWLER.get("timeout", 10)
if isinstance(TIMEOUT, dict):
    HTTP_TIMEOUT = ClientTimeout(**TIMEOUT)
else:
    try:
        HTTP_TIMEOUT = ClientTimeout(total=float(TIMEOUT))
    except Exception:
        HTTP_TIMEOUT = ClientTimeout(total=10)


logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.info("Configuration chargée avec succès.")
