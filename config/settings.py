from pathlib import Path
import yaml, logging, logging.config

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

def load_config():
    if not CONFIG_PATH.exists():
        logging.warning(f"{CONFIG_PATH} introuvable. Valeurs par défaut utilisées.")
        return {}
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

from aiohttp import ClientTimeout

t = config["crawler"].get("timeout", 10)
if isinstance(t, dict):
    HTTP_TIMEOUT = ClientTimeout(**t)
else:
    HTTP_TIMEOUT = ClientTimeout(total=float(t))

# === Extraction des valeurs ===
MAX_PAGES = config.get("crawler", {}).get("max_pages", 50)

# === Configuration du logging ===
if "version" in config:
    logging.config.dictConfig(config)
else:
    logging.basicConfig(
        level=getattr(logging, config.get("logging", {}).get("level", "INFO").upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

# === Extraction des valeurs avec fallback par défaut ===
HEADERS = config.get("crawler", {}).get("headers", {})
START_URLS = config.get("crawler", {}).get("start_urls", ["http://example.com"])
#HTTP_TIMEOUT = config.get("crawler", {}).get("timeout", 10)
RETRY_COUNT = config.get("crawler", {}).get("retries", 3)
ALLOWED_LANGS = set(config.get("crawler", {}).get("languages", ["en"]))
RESPECT_ROBOTS = config.get("crawler", {}).get("robots", True)  # ← ajouté ici


# --- Rate limiting ---
RATE_LIMIT_PER_DOMAIN = config.get("crawler", {}).get("rate_limit", {})
RATE_LIMIT_ENABLED = RATE_LIMIT_PER_DOMAIN.get("enabled", False)
RATE_LIMIT_DELAY = RATE_LIMIT_PER_DOMAIN.get("delay", 0)


#=== Stockage des données ===
DB_PATH = config.get("storage", {}).get("database_path", "data/project.db")
EXPORT_DIR = config.get("storage", {}).get("export_dir", "exports")


#=== Logging ===
LOG_FILE = config.get("logging", {}).get("file", "logs/pipeline.log")
LOG_LEVEL = getattr(logging, config.get("logging", {}).get("level", "INFO").upper(), logging.INFO)
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
logging.info("Configuration chargée avec succès.")

if __name__ == "__main__":
    print("Chargement config :", bool(config))
    print("URLs de départ :", START_URLS)
    print("Respect robots.txt :", RESPECT_ROBOTS)
