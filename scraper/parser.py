from html.parser import HTMLParser

class LinkTitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.title = ""
        self.description = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, val in attrs:
                if attr == "href":
                    self.links.append(val)
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            attrs_dict = dict(attrs)
            if attrs_dict.get("name") == "description":
                self.description = attrs_dict.get("content", "").strip()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()


def parse_and_sanitize(url: str, html: str):
    parser = LinkTitleParser()
    parser.feed(html)

    return {
        "url": url,
        "title": parser.title.strip() if parser.title else "",
        "description": parser.description.strip() if parser.description else "",
        "links": parser.links
    }
