from .parser_html import parse_html
from .cleaner import sanitize

def extract(pages):
    raw = [parse_html(html) for _, html in pages]
    return sanitize(raw)
