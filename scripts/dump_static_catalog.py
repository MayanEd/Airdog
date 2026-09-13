"""Dump catalog JSON for the GitHub Pages static export (no live MySQL required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, joinedload  # noqa: E402

from app.database import Base  # noqa: E402
from app.models import Category, News, Page, Product  # noqa: E402
from app.seed import LOCALES, seed_if_empty  # noqa: E402
from app.serialize import category_out, pick_tr, product_out  # noqa: E402

OUT = ROOT / "frontend" / "src" / "data" / "catalog.json"


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = Session(engine)
    seed_if_empty(db, "admin@example.com", "admin1234")

    catalog: dict = {"categories": {}, "products": {}, "news": {}, "pages": {}}
    for locale in LOCALES:
        cats = (
            db.query(Category)
            .options(joinedload(Category.translations))
            .order_by(Category.sort_order)
            .all()
        )
        products = (
            db.query(Product)
            .options(
                joinedload(Product.translations),
                joinedload(Product.category),
                joinedload(Product.images),
            )
            .order_by(Product.sort_order, Product.id)
            .all()
        )
        news = (
            db.query(News)
            .options(joinedload(News.translations))
            .order_by(News.published_at.desc())
            .all()
        )
        pages = db.query(Page).filter(Page.locale == locale).order_by(Page.slug).all()
        catalog["categories"][locale] = [category_out(c, locale) for c in cats]
        catalog["products"][locale] = [product_out(p, locale, detail=True) for p in products]
        catalog["news"][locale] = [
            {
                "id": n.id,
                "slug": n.slug,
                "published_at": n.published_at.isoformat(),
                "title": (pick_tr(n.translations, locale).title if pick_tr(n.translations, locale) else n.slug),
                "body": (pick_tr(n.translations, locale).body if pick_tr(n.translations, locale) else ""),
            }
            for n in news
        ]
        catalog["pages"][locale] = [
            {"slug": p.slug, "title": p.title, "body": p.body} for p in pages
        ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
