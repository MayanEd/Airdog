from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ContactMessage
from ..schemas import ContactIn

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post("")
def create_contact(payload: ContactIn, db: Annotated[Session, Depends(get_db)]):
    msg = ContactMessage(
        name=payload.name,
        email=payload.email,
        product=payload.product,
        message=payload.message,
    )
    db.add(msg)
    db.commit()
    return {"ok": True, "id": msg.id}
