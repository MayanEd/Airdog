from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Page

router = APIRouter(prefix="/pages", tags=["pages"])


@router.get("/{slug}")
def get_page(slug: str, db: Annotated[Session, Depends(get_db)], locale: str = Query("en")):
    page = db.query(Page).filter(Page.slug == slug, Page.locale == locale).first()
    if not page:
        page = db.query(Page).filter(Page.slug == slug, Page.locale == "en").first()
    if not page:
        raise HTTPException(404, "Page not found")
    return {"slug": page.slug, "locale": page.locale, "title": page.title, "body": page.body}
