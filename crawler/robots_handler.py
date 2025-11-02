import urllib.robotparser

def allowed(url: str, user_agent: str = "*") -> bool:
    """Vérifie si l’URL est autorisée par robots.txt."""
    try:
        parts = url.split("/")
        base = f"{parts[0]}//{parts[2]}"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{base}/robots.txt")
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True
