from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Category, Product
from ..serialize import product_out

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products(
    db: Annotated[Session, Depends(get_db)],
    locale: str = Query("en"),
    category: str | None = None,
    q: str | None = None,
):
    query = db.query(Product).options(
        joinedload(Product.translations),
        joinedload(Product.category),
        joinedload(Product.images),
    )
    if category:
        query = query.join(Category).filter(Category.slug == category)
    products = query.order_by(Product.sort_order, Product.id).all()
    out = []
    ql = (q or "").strip().lower()
    for p in products:
        item = product_out(p, locale)
        if ql:
            blob = f"{item['name']} {item['subtitle']} {p.sku} {p.color}".lower()
            if ql not in blob:
                continue
        out.append(item)
    return out


@router.get("/{slug}")
def get_product(slug: str, db: Annotated[Session, Depends(get_db)], locale: str = Query("en")):
    p = (
        db.query(Product)
        .options(
            joinedload(Product.translations),
            joinedload(Product.category),
            joinedload(Product.images),
        )
        .filter((Product.slug == slug) | (Product.sku == slug))
        .first()
    )
    if not p:
        raise HTTPException(404, "Product not found")
    return product_out(p, locale, detail=True)
