from bs4 import BeautifulSoup

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return {
        "title": soup.title.string if soup.title else "",
        "links": [a.get("href") for a in soup.find_all("a", href=True)]
    }
