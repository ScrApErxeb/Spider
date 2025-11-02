from dataclasses import dataclass, asdict

@dataclass
class PageModel:
    title: str
    url: str
    content: str

@dataclass
class DataModel:
    key: str
    value: str

def to_dict(obj):
    return asdict(obj)

def from_dict(d):
    return PageModel(**d)
