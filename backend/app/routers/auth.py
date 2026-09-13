from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..auth import COOKIE_NAME, create_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import CartItem, User
from ..schemas import LoginIn, RegisterIn, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def set_auth_cookie(response: Response, user: User) -> None:
    response.set_cookie(
        COOKIE_NAME,
        create_token(user),
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )


def merge_guest_cart(db: Session, user: User, session_id: str | None) -> None:
    if not session_id:
        return
    guests = db.query(CartItem).filter(CartItem.session_id == session_id, CartItem.user_id.is_(None)).all()
    for item in guests:
        existing = (
            db.query(CartItem)
            .filter(CartItem.user_id == user.id, CartItem.product_id == item.product_id)
            .first()
        )
        if existing:
            existing.quantity += item.quantity
            db.delete(item)
        else:
            item.user_id = user.id
            item.session_id = ""


@router.post("/register", response_model=UserOut)
def register(
    payload: RegisterIn,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    airdog_session: Annotated[str | None, Cookie()] = None,
):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(400, "Email already registered")
    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        name=payload.name,
        phone=payload.phone,
    )
    db.add(user)
    db.flush()
    merge_guest_cart(db, user, airdog_session)
    db.commit()
    db.refresh(user)
    set_auth_cookie(response, user)
    return user


@router.post("/login", response_model=UserOut)
def login(
    payload: LoginIn,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    airdog_session: Annotated[str | None, Cookie()] = None,
):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    merge_guest_cart(db, user, airdog_session)
    db.commit()
    set_auth_cookie(response, user)
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: Annotated[User, Depends(get_current_user)]):
    return user
