from dotenv import load_dotenv
import os
import logging.config
import yaml
from pathlib import Path

def load_env():
    load_dotenv()
    _load_logging()

def _load_logging():
    log_conf = Path(__file__).parent / "logging_conf.yaml"
    if log_conf.exists():
        with open(log_conf, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)

def get(key, default=None):
    return os.getenv(key, default)

def get_root_urls():
    roots = os.getenv("ROOT_URLS", "https://example.com")
    return [r.strip() for r in roots.split(",") if r.strip()]

def get_user_agent():
    return os.getenv("USER_AGENT", "SimpleBot/0.2")

def get_delay():
    try:
        return float(os.getenv("FETCH_DELAY", "1"))
    except ValueError:
        return 1.0
