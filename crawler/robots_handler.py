import aiohttp
import asyncio
import logging
import time
from urllib.parse import urlparse
from urllib import robotparser
from config.settings import config

logger = logging.getLogger(__name__)

# Lecture config YAML
ROBOTS_ENABLED = config.get("crawler", {}).get("robots", {}).get("enabled", True)
CACHE_EXPIRY = config.get("crawler", {}).get("robots", {}).get("cache_expiry", 3600)


class RobotsHandler:
    """Gère le téléchargement et le respect du fichier robots.txt avec cache et verrouillage."""

    def __init__(self):
        self.parsers = {}  # {domain: (parser, timestamp)}
        self.lock = asyncio.Lock()

    async def fetch_robots_txt(self, base_url):
        """Télécharge le robots.txt d’un domaine."""
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=5) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        logger.debug(f"robots.txt chargé depuis {robots_url}")
                        return text
                    logger.warning(f"Pas de robots.txt ({resp.status}) pour {robots_url}")
        except Exception as e:
            logger.warning(f"Erreur robots.txt {robots_url} : {e}")
        return None

    async def get_parser(self, base_url):
        """Retourne un robotparser valide pour le domaine, avec cache."""
        parsed = urlparse(base_url)
        domain = parsed.netloc
        now = time.time()

        async with self.lock:
            # Vérifie si un parser récent existe déjà
            if domain in self.parsers:
                parser, timestamp = self.parsers[domain]
                if now - timestamp < CACHE_EXPIRY:
                    return parser

            # Sinon, recharge
            text = await self.fetch_robots_txt(base_url)
            parser = robotparser.RobotFileParser()
            parser.set_url(f"{parsed.scheme}://{domain}/robots.txt")
            parser.parse(text.splitlines() if text else [])
            self.parsers[domain] = (parser, now)
            return parser

    async def is_allowed(self, url, user_agent="*"):
        """Vérifie si l’accès est autorisé selon le robots.txt."""
        if not ROBOTS_ENABLED:
            return True
        parser = await self.get_parser(url)
        return parser.can_fetch(user_agent, url)
