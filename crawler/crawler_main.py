from .queue_manager import QueueManager
from .fetcher import Fetcher
from .robots_handler import RobotsHandler

def crawl(start_urls=["https://example.com"]):
    q = QueueManager()
    f = Fetcher()
    r = RobotsHandler()
    pages = []

    for url in start_urls:
        q.enqueue(url)

    while not q.is_empty():
        url = q.dequeue()
        if not r.allowed(url):
            continue
        html = f.fetch(url)
        if html:
            pages.append((url, html))
            q.seen(url)
    return pages
