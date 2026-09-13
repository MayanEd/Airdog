from typing import Any

from .models import CategoryTranslation, ProductTranslation


def pick_tr(items: list, locale: str):
    by = {t.locale: t for t in items}
    return by.get(locale) or by.get("en") or (items[0] if items else None)


def category_out(cat, locale: str) -> dict[str, Any]:
    tr = pick_tr(cat.translations, locale)
    return {
        "id": cat.id,
        "slug": cat.slug,
        "image": cat.image,
        "sort_order": cat.sort_order,
        "show_in_nav": cat.show_in_nav,
        "name": tr.name if tr else cat.slug,
        "description": tr.description if tr else "",
    }


def product_out(p, locale: str, detail: bool = False) -> dict[str, Any]:
    tr: ProductTranslation | None = pick_tr(p.translations, locale)
    data: dict[str, Any] = {
        "id": p.id,
        "sku": p.sku,
        "slug": p.slug,
        "price_yen": p.price_yen,
        "stock_status": p.stock_status,
        "color": p.color,
        "size": p.size,
        "is_service": p.is_service,
        "featured": p.featured,
        "image": p.image,
        "category_id": p.category_id,
        "category_slug": p.category.slug if p.category else None,
        "name": tr.name if tr else p.sku,
        "subtitle": tr.subtitle if tr else "",
    }
    if detail and tr:
        data.update(
            {
                "description": tr.description,
                "included": tr.included,
                "specs_json": tr.specs_json,
                "disclaimers": tr.disclaimers,
                "images": [{"url": i.url, "alt": i.alt} for i in sorted(p.images, key=lambda x: x.sort_order)],
            }
        )
    return data
