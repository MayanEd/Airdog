from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import News
from ..serialize import pick_tr

router = APIRouter(prefix="/news", tags=["news"])


@router.get("")
def list_news(db: Annotated[Session, Depends(get_db)], locale: str = Query("en")):
    items = db.query(News).options(joinedload(News.translations)).order_by(News.published_at.desc()).all()
    out = []
    for n in items:
        tr = pick_tr(n.translations, locale)
        out.append(
            {
                "id": n.id,
                "slug": n.slug,
                "published_at": n.published_at.isoformat(),
                "title": tr.title if tr else n.slug,
                "body": tr.body if tr else "",
            }
        )
    return out


@router.get("/{slug}")
def get_news(slug: str, db: Annotated[Session, Depends(get_db)], locale: str = Query("en")):
    n = db.query(News).options(joinedload(News.translations)).filter(News.slug == slug).first()
    if not n:
        from fastapi import HTTPException

        raise HTTPException(404, "Not found")
    tr = pick_tr(n.translations, locale)
    return {
        "id": n.id,
        "slug": n.slug,
        "published_at": n.published_at.isoformat(),
        "title": tr.title if tr else n.slug,
        "body": tr.body if tr else "",
    }
