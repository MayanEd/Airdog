from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user_optional
from ..database import get_db
from ..models import Inquiry, InquiryItem, User
from ..schemas import InquiryIn
from .cart import _cart_query, _session_id

router = APIRouter(prefix="/inquiries", tags=["inquiries"])


@router.post("")
def create_inquiry(
    payload: InquiryIn,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
    airdog_session: Annotated[str | None, Cookie()] = None,
    locale: str = "en",
):
    sid = _session_id(response, airdog_session)
    items = _cart_query(db, user, sid).all()
    if not items:
        raise HTTPException(400, "Cart is empty")
    inquiry = Inquiry(
        user_id=user.id if user else None,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        country=payload.country,
        address=payload.address,
        message=payload.message,
        status="new",
    )
    db.add(inquiry)
    db.flush()
    for item in items:
        db.add(
            InquiryItem(
                inquiry_id=inquiry.id,
                product_id=item.product_id,
                sku=item.product.sku,
                name=item.product.sku,
                quantity=item.quantity,
                price_yen=item.product.price_yen,
            )
        )
        db.delete(item)
    db.commit()
    return {"id": inquiry.id, "status": inquiry.status}


@router.get("/mine")
def my_inquiries(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User | None, Depends(get_current_user_optional)],
):
    if not user:
        raise HTTPException(401, "Not authenticated")
    rows = (
        db.query(Inquiry)
        .options(joinedload(Inquiry.items))
        .filter(Inquiry.user_id == user.id)
        .order_by(Inquiry.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
            "items": [
                {"sku": i.sku, "quantity": i.quantity, "price_yen": i.price_yen} for i in r.items
            ],
            "total_yen": sum(i.quantity * i.price_yen for i in r.items),
        }
        for r in rows
    ]
