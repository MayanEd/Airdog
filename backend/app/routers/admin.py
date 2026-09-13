from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..auth import get_admin_user, hash_password
from ..database import get_db
from ..models import (
    Category,
    CategoryTranslation,
    ContactMessage,
    Inquiry,
    News,
    NewsTranslation,
    Page,
    Product,
    ProductImage,
    ProductTranslation,
    User,
)
from ..schemas import (
    CategoryAdminIn,
    InquiryStatusIn,
    NewsAdminIn,
    PageAdminIn,
    ProductAdminIn,
    UserUpdateIn,
)
from ..serialize import product_out

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_admin_user)])


@router.get("/users")
def list_users(db: Annotated[Session, Depends(get_db)]):
    users = db.query(User).order_by(User.id).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "phone": u.phone,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.post("/users")
def create_user(payload: dict[str, Any], db: Annotated[Session, Depends(get_db)]):
    email = (payload.get("email") or "").lower()
    if not email or db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "Invalid or duplicate email")
    user = User(
        email=email,
        password_hash=hash_password(payload.get("password") or "changeme"),
        name=payload.get("name") or "",
        phone=payload.get("phone") or "",
        is_admin=bool(payload.get("is_admin")),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.patch("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdateIn, db: Annotated[Session, Depends(get_db)]):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.password:
        user.password_hash = hash_password(payload.password)
    if payload.is_admin is not None:
        user.is_admin = payload.is_admin
    db.commit()
    return {"ok": True}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)], admin: Annotated[User, Depends(get_admin_user)]):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    if user.id == admin.id:
        raise HTTPException(400, "Cannot delete yourself")
    db.delete(user)
    db.commit()
    return {"ok": True}


@router.get("/products")
def admin_products(db: Annotated[Session, Depends(get_db)]):
    products = db.query(Product).options(joinedload(Product.translations)).order_by(Product.id).all()
    return [product_out(p, "en", detail=True) for p in products]


@router.post("/products")
def create_product(payload: ProductAdminIn, db: Annotated[Session, Depends(get_db)]):
    if db.query(Product).filter((Product.sku == payload.sku) | (Product.slug == payload.slug)).first():
        raise HTTPException(400, "SKU or slug exists")
    p = Product(
        sku=payload.sku,
        slug=payload.slug,
        category_id=payload.category_id,
        price_yen=payload.price_yen,
        stock_status=payload.stock_status,
        color=payload.color,
        size=payload.size,
        is_service=payload.is_service,
        featured=payload.featured,
        sort_order=payload.sort_order,
        image=payload.image,
    )
    db.add(p)
    db.flush()
    for tr in payload.translations:
        db.add(
            ProductTranslation(
                product_id=p.id,
                locale=tr.get("locale", "en"),
                name=tr.get("name", payload.sku),
                subtitle=tr.get("subtitle", ""),
                description=tr.get("description", ""),
                included=tr.get("included", ""),
                specs_json=tr.get("specs_json", "[]"),
                disclaimers=tr.get("disclaimers", ""),
            )
        )
    for img in payload.images:
        db.add(ProductImage(product_id=p.id, url=img.get("url", ""), alt=img.get("alt", ""), sort_order=img.get("sort_order", 0)))
    db.commit()
    return {"id": p.id}


@router.patch("/products/{product_id}")
def update_product(product_id: int, payload: dict[str, Any], db: Annotated[Session, Depends(get_db)]):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Product not found")
    for field in ("sku", "slug", "category_id", "price_yen", "stock_status", "color", "size", "is_service", "featured", "sort_order", "image"):
        if field in payload:
            setattr(p, field, payload[field])
    if "translations" in payload:
        db.query(ProductTranslation).filter(ProductTranslation.product_id == p.id).delete()
        for tr in payload["translations"]:
            db.add(
                ProductTranslation(
                    product_id=p.id,
                    locale=tr.get("locale", "en"),
                    name=tr.get("name", p.sku),
                    subtitle=tr.get("subtitle", ""),
                    description=tr.get("description", ""),
                    included=tr.get("included", ""),
                    specs_json=tr.get("specs_json", "[]"),
                    disclaimers=tr.get("disclaimers", ""),
                )
            )
    db.commit()
    return {"ok": True}


@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(404, "Product not found")
    db.delete(p)
    db.commit()
    return {"ok": True}


@router.get("/inquiries")
def list_inquiries(db: Annotated[Session, Depends(get_db)]):
    rows = db.query(Inquiry).options(joinedload(Inquiry.items)).order_by(Inquiry.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "phone": r.phone,
            "country": r.country,
            "address": r.address,
            "message": r.message,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
            "items": [
                {"sku": i.sku, "quantity": i.quantity, "price_yen": i.price_yen} for i in r.items
            ],
            "total_yen": sum(i.quantity * i.price_yen for i in r.items),
        }
        for r in rows
    ]


@router.patch("/inquiries/{inquiry_id}")
def update_inquiry(inquiry_id: int, payload: InquiryStatusIn, db: Annotated[Session, Depends(get_db)]):
    row = db.get(Inquiry, inquiry_id)
    if not row:
        raise HTTPException(404, "Not found")
    row.status = payload.status
    db.commit()
    return {"ok": True}


@router.get("/contacts")
def list_contacts(db: Annotated[Session, Depends(get_db)]):
    rows = db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "product": r.product,
            "message": r.message,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@router.get("/news")
def admin_news(db: Annotated[Session, Depends(get_db)]):
    items = db.query(News).options(joinedload(News.translations)).order_by(News.published_at.desc()).all()
    return [
        {
            "id": n.id,
            "slug": n.slug,
            "published_at": n.published_at.isoformat(),
            "translations": [{"locale": t.locale, "title": t.title, "body": t.body} for t in n.translations],
        }
        for n in items
    ]


@router.post("/news")
def create_news(payload: NewsAdminIn, db: Annotated[Session, Depends(get_db)]):
    n = News(slug=payload.slug, published_at=payload.published_at or datetime.utcnow())
    db.add(n)
    db.flush()
    for tr in payload.translations:
        db.add(
            NewsTranslation(
                news_id=n.id,
                locale=tr.get("locale", "en"),
                title=tr.get("title", ""),
                body=tr.get("body", ""),
            )
        )
    db.commit()
    return {"id": n.id}


@router.get("/pages")
def admin_pages(db: Annotated[Session, Depends(get_db)]):
    pages = db.query(Page).order_by(Page.slug, Page.locale).all()
    return [{"id": p.id, "slug": p.slug, "locale": p.locale, "title": p.title, "body": p.body} for p in pages]


@router.put("/pages")
def upsert_page(payload: PageAdminIn, db: Annotated[Session, Depends(get_db)]):
    page = db.query(Page).filter(Page.slug == payload.slug, Page.locale == payload.locale).first()
    if not page:
        page = Page(slug=payload.slug, locale=payload.locale, title=payload.title, body=payload.body)
        db.add(page)
    else:
        page.title = payload.title
        page.body = payload.body
    db.commit()
    return {"ok": True}


@router.post("/categories")
def create_category(payload: CategoryAdminIn, db: Annotated[Session, Depends(get_db)]):
    cat = Category(
        slug=payload.slug,
        image=payload.image,
        sort_order=payload.sort_order,
        show_in_nav=payload.show_in_nav,
    )
    db.add(cat)
    db.flush()
    for tr in payload.translations:
        db.add(
            CategoryTranslation(
                category_id=cat.id,
                locale=tr.get("locale", "en"),
                name=tr.get("name", payload.slug),
                description=tr.get("description", ""),
            )
        )
    db.commit()
    return {"id": cat.id}
