import logging
from .parser_html import parse_html
from .cleaner import sanitize

logger = logging.getLogger("scraper.main")

def extract(pages):
    raw = []
    for url, html in pages:
        try:
            parsed = parse_html(html)
            parsed["source"] = url
            raw.append(parsed)
        except Exception as e:
            logger.error("parse error %s: %s", url, e)
            continue
    return sanitize(raw)
