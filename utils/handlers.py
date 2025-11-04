# handlers.py
import aiohttp
import asyncio
import logging
import re
from urllib.parse import urljoin
from langdetect import detect, DetectorFactory
from bs4 import BeautifulSoup

DetectorFactory.seed = 0
logger = logging.getLogger(__name__)


# ============================================================
# === ROBOTS HANDLER =========================================
# ============================================================

import aiohttp
import asyncio
import logging
from urllib.parse import urljoin, urlparse
from config.settings import RESPECT_ROBOTS  # import du flag global

logger = logging.getLogger(__name__)

class RobotsHandler:
    """Gère robots.txt avec cache et respect des règles disallow."""

    def __init__(self):
        self.cache = {}
        self.lock = asyncio.Lock()

    async def _fetch_robots(self, base_url):
        robots_url = urljoin(base_url, "/robots.txt")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=10) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    logger.warning(f"Pas de robots.txt ({resp.status}) pour {robots_url}")
        except Exception as e:
            logger.warning(f"Erreur robots.txt {robots_url}: {e}")
        return ""

    async def is_allowed(self, url, user_agent="*"):
        """Retourne True si l’accès est permis selon robots.txt, sauf si désactivé."""
        if not RESPECT_ROBOTS:
            return True  # robots.txt ignoré globalement

        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        async with self.lock:
            if base not in self.cache:
                rules = await self._fetch_robots(base)
                self.cache[base] = self._parse_robots(rules)

            disallowed = self.cache[base].get(user_agent, [])
            for path in disallowed:
                if parsed.path.startswith(path):
                    return False

        return True

    def _parse_robots(self, text):
        rules = {}
        current_agent = None
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower().startswith("user-agent:"):
                current_agent = line.split(":", 1)[1].strip()
                rules[current_agent] = []
            elif line.lower().startswith("disallow:") and current_agent:
                path = line.split(":", 1)[1].strip()
                if path:
                    rules[current_agent].append(path)
        return rules



# ============================================================
# === LANGUAGE HANDLER =======================================
# ============================================================

class LanguageHandler:
    """Détecte la langue d’un contenu HTML."""

    def __init__(self, allowed_langs=None):
        self.allowed = set(allowed_langs or ["en"])

    def detect_language(self, html):
        """Combine heuristique <html lang>, métadonnées et langdetect."""
        if not html:
            return None

        # 1. Méta ou attribut <html lang="">
        soup = BeautifulSoup(html, "html.parser")
        meta_lang = (
            soup.html.get("lang") if soup.html else None
        ) or soup.find("meta", attrs={"http-equiv": "content-language"})
        if meta_lang:
            lang = meta_lang.get("content") if hasattr(meta_lang, "get") else meta_lang
            lang = re.split(r"[-_]", lang.lower())[0]
            return lang

        # 2. Heuristique fréquence caractères (latin, cyrillique, arabe, chinois)
        text = soup.get_text().strip()[:2000]
        if not text:
            return None
        counts = {
            "zh": len(re.findall(r"[\u4e00-\u9fff]", text)),
            "ru": len(re.findall(r"[\u0400-\u04FF]", text)),
            "ar": len(re.findall(r"[\u0600-\u06FF]", text)),
            "la": len(re.findall(r"[a-zA-Z]", text))
        }
        if max(counts.values()) > 20:
            code = max(counts, key=counts.get)
            if code == "la":
                try:
                    code = detect(text)
                except Exception:
                    code = "en"
            return code

        # 3. Fallback langdetect
        try:
            return detect(text)
        except Exception:
            return None

    def is_allowed(self, html):
        """Vérifie si la langue détectée est autorisée."""
        lang = self.detect_language(html)
        return lang in self.allowed if lang else False
