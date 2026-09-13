from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Category
from ..serialize import category_out

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
def list_categories(db: Annotated[Session, Depends(get_db)], locale: str = Query("en")):
    cats = (
        db.query(Category)
        .options(joinedload(Category.translations))
        .order_by(Category.sort_order)
        .all()
    )
    return [category_out(c, locale) for c in cats]


@router.get("/{slug}")
def get_category(slug: str, db: Annotated[Session, Depends(get_db)], locale: str = Query("en")):
    cat = (
        db.query(Category)
        .options(joinedload(Category.translations))
        .filter(Category.slug == slug)
        .first()
    )
    if not cat:
        from fastapi import HTTPException

        raise HTTPException(404, "Category not found")
    return category_out(cat, locale)
