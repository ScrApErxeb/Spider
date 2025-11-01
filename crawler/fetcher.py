import requests
import time

class Fetcher:
    def __init__(self, delay=1):
        self.delay = delay

    def fetch(self, url):
        time.sleep(self.delay)
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            return r.text
        except requests.RequestException:
            return None
