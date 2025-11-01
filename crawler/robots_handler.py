import urllib.robotparser

class RobotsHandler:
    def __init__(self):
        self.parsers = {}

    def allowed(self, url, user_agent="*"):
        domain = url.split("/")[2]
        if domain not in self.parsers:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"https://{domain}/robots.txt")
            rp.read()
            self.parsers[domain] = rp
        return self.parsers[domain].can_fetch(user_agent, url)
