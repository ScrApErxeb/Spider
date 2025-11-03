from pydantic import BaseModel, HttpUrl, ValidationError, field_validator
import logging

class PageSchema(BaseModel):
    title: str
    url: HttpUrl
    description: str

    @field_validator("title", "description")
    def strip_fields(cls, v):
        return v.strip() if isinstance(v, str) else v

def validate_pages(parsed):
    """Valide et nettoie la liste des pages extraites."""
    valid = []
    for p in parsed:
        try:
            data = {
                "title": p.get("title", "").strip(),
                "url": p.get("url", "").strip(),
                "description": p.get("description", p.get("content", "")).strip(),
            }
            valid.append(PageSchema(**data).model_dump())
        except ValidationError as e:
            logging.warning(f"Validation ignorée pour {p.get('url','?')} : {e.errors()}")
    return valid
