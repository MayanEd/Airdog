import uuid
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user_optional
from ..database import get_db
from ..models import CartItem, Product, User
from ..schemas import CartAddIn, CartUpdateIn
from ..serialize import product_out

router = APIRouter(prefix="/cart", tags=["cart"])
SESSION_COOKIE = "airdog_session"


def _session_id(response: Response, session: str | None) -> str:
    if session:
        return session
    sid = uuid.uuid4().hex
    response.set_cookie(SESSION_COOKIE, sid, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 30)
    return sid


def _cart_query(db: Session, user: User | None, sid: str):
    q = db.query(CartItem).options(
        joinedload(CartItem.product).joinedload(Product.translations),
        joinedload(CartItem.product).joinedload(Product.category),
    )
    if user:
        return q.filter(CartItem.user_id == user.id)
    return q.filter(CartItem.session_id == sid, CartItem.user_id.is_(None))


def _serialize(items: list[CartItem], locale: str):
    rows = []
    total = 0
    for item in items:
        p = product_out(item.product, locale)
        line = item.quantity * item.product.price_yen
        total += line
        rows.append({"id": item.id, "quantity": item.quantity, "line_yen": line, "product": p})
    return {"items": rows, "total_yen": total, "count": sum(i.quantity for i in items)}


@router.get("")
def get_cart(
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
    airdog_session: Annotated[str | None, Cookie()] = None,
    locale: str = "en",
):
    sid = _session_id(response, airdog_session)
    items = _cart_query(db, user, sid).all()
    return _serialize(items, locale)


@router.post("")
def add_cart(
    payload: CartAddIn,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
    airdog_session: Annotated[str | None, Cookie()] = None,
    locale: str = "en",
):
    if payload.quantity < 1:
        raise HTTPException(400, "Invalid quantity")
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    sid = _session_id(response, airdog_session)
    q = _cart_query(db, user, sid).filter(CartItem.product_id == payload.product_id)
    existing = q.first()
    if existing:
        existing.quantity += payload.quantity
    else:
        db.add(
            CartItem(
                user_id=user.id if user else None,
                session_id="" if user else sid,
                product_id=payload.product_id,
                quantity=payload.quantity,
            )
        )
    db.commit()
    items = _cart_query(db, user, sid).all()
    return _serialize(items, locale)


@router.patch("/{item_id}")
def update_cart(
    item_id: int,
    payload: CartUpdateIn,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
    airdog_session: Annotated[str | None, Cookie()] = None,
    locale: str = "en",
):
    sid = _session_id(response, airdog_session)
    item = _cart_query(db, user, sid).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")
    if payload.quantity < 1:
        db.delete(item)
    else:
        item.quantity = payload.quantity
    db.commit()
    return _serialize(_cart_query(db, user, sid).all(), locale)


@router.delete("/{item_id}")
def delete_cart(
    item_id: int,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
    airdog_session: Annotated[str | None, Cookie()] = None,
    locale: str = "en",
):
    sid = _session_id(response, airdog_session)
    item = _cart_query(db, user, sid).filter(CartItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return _serialize(_cart_query(db, user, sid).all(), locale)
