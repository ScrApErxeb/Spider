import yaml
import logging
from pathlib import Path

CONFIG_PATH = Path("config/config.yaml")

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Fichier de configuration introuvable : {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# --- Charger le fichier YAML ---
config = load_config()

# --- Extraire les paramètres ---
HEADERS = config["crawler"]["headers"]
START_URLS = config["crawler"]["start_urls"]
HTTP_TIMEOUT = config["crawler"]["timeout"]
RETRY_COUNT = config["crawler"]["retries"]
ALLOWED_LANGS = set(config["crawler"]["languages"])

DB_PATH = config["storage"]["database_path"]
EXPORT_DIR = config["storage"]["export_dir"]

LOG_FILE = config["logging"]["file"]
LOG_LEVEL = getattr(logging, config["logging"]["level"].upper(), logging.INFO)
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# --- Configurer le logging global ---
logging.basicConfig(
    level=LOG_LEVEL,
    filename=LOG_FILE,
    format=LOG_FORMAT,
    encoding="utf-8"
)

logging.info("Configuration chargée avec succès.")
