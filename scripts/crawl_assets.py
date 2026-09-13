#!/usr/bin/env python3
"""Download public storefront assets from airdogjapan.co.jp into frontend/public/assets."""

from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "public" / "assets"
LOG = ROOT / "UNRETRIEVED.md"

BASE = "https://www.airdogjapan.co.jp"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

KNOWN_ASSETS = [
    "/img/usr/common/header-logo.webp",
    "/img/usr/slider/slider_topplate.jpg",
    "/img/usr/slider/slider_cleaner.jpg",
    "/img/usr/slider/slider_medical.jpg",
    "/img/usr/slider/slider_lineup.jpg",
    "/img/usr/slider/slider_x5d.jpg",
    "/img/usr/slider/slider_x1d.jpg",
    "/img/usr/slider/slider_x3d.jpg",
    "/img/usr/slider/slider_x8dpro.jpg",
    "/img/usr/slider/slider_airdogcare-plus.jpg",
    "/img/usr/slider/slider_mini.jpg",
    "/img/usr/slider/slider_moi.jpg",
    "/img/category/1/Airdog-Type-01.jpg",
    "/img/category/1/Airdog-Type-02.jpg",
    "/img/category/1/Airdog-Type-03.jpg",
    "/img/category/1/Airdog-Type-05.jpg",
    "/img/category/1/Airdog-Type-06.jpg",
    "/img/category/1/Airdog-Type-07.jpg",
    "/img/campaign/medical_banner_20250119.jpg",
    "/img/icon/up.gif",
    "/favicon.ico",
]

PAGES = [
    "/",
    "/shop/default.aspx",
    "/shop/c/c0/",
    "/shop/c/c10/",
    "/shop/c/c20/",
    "/shop/c/c2020/",
    "/shop/c/c30/",
    "/shop/c/c70/",
    "/shop/e/eALL/",
    "/shop/pages/medical.aspx",
    "/shop/pages/airdogcare-plus.aspx",
    "/shop/pages/company.aspx",
    "/shop/pages/faq.aspx",
    "/shop/pages/guide.aspx",
    "/shop/pages/guide02.aspx",
    "/shop/pages/guide04.aspx",
    "/shop/pages/import-attention.aspx",
    "/shop/pages/privacy.aspx",
    "/shop/g/gAIR-X1-H1W510/",
    "/shop/g/gAIR-X3-H1W510/",
    "/shop/g/gAIR-X3-H1B510/",
    "/shop/g/gAIR-X5-H1W510/",
    "/shop/g/gAIR-X8-H1W510/",
    "/shop/g/gAIR-MN-H1W520/",
    "/shop/g/gAIR-MN-H1B520/",
    "/shop/topic/topicdetaillist.aspx?category=0",
]

CTX = ssl.create_default_context()
IMG_EXT = re.compile(r"\.(?:jpe?g|png|webp|gif|svg|ico)(?:\?|$)", re.I)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = dict(attrs)
        for key in ("src", "href", "data-src", "data-lazy", "data-original"):
            val = ad.get(key)
            if val:
                self.urls.append(val)
        srcset = ad.get("srcset")
        if srcset:
            for part in srcset.split(","):
                self.urls.append(part.strip().split(" ")[0])


def request(url: str) -> tuple[int, bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=30) as res:
            return res.status, res.read(), res.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read() if exc.fp else b"", ""
    except Exception as exc:  # noqa: BLE001
        return 0, str(exc).encode("utf-8", "replace"), ""


def local_path(url: str) -> Path:
    parsed = urlparse(url)
    rel = parsed.path.lstrip("/")
    if not rel or rel.endswith("/"):
        rel = (rel + "index.bin").lstrip("/")
    return OUT / rel


def save_bytes(url: str, data: bytes) -> Path:
    dest = local_path(url)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest


def is_asset(url: str) -> bool:
    path = urlparse(url).path.lower()
    if IMG_EXT.search(path):
        return True
    return any(x in path for x in ("/img/", "/contents/", "/upload/", "/images/"))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    failed: list[str] = []
    fetched: list[str] = []
    seen: set[str] = set()

    queue = [urljoin(BASE, p) for p in KNOWN_ASSETS + PAGES]

    while queue:
        url = queue.pop(0)
        if url in seen or not url.startswith(BASE):
            continue
        seen.add(url)
        status, body, ctype = request(url)
        time.sleep(0.15)
        if status != 200 or not body:
            failed.append(f"- `{url}` — HTTP {status or 'network error'}")
            continue

        if is_asset(url) or (ctype.startswith("image/") if ctype else False):
            save_bytes(url, body)
            fetched.append(url)
            continue

        if "html" in (ctype or "") or url.rstrip("/").endswith((".aspx", "")) or "/shop/" in url:
            parser = LinkParser()
            try:
                parser.feed(body.decode("utf-8", "ignore"))
            except Exception:
                continue
            for raw in parser.urls:
                abs_url = urljoin(url, raw.split("?")[0])
                if not abs_url.startswith(BASE) or abs_url in seen:
                    continue
                if is_asset(abs_url):
                    queue.append(abs_url)
                elif "/shop/g/" in abs_url and abs_url.count("/") >= 5:
                    queue.append(abs_url)

    manifest = {
        "fetched": sorted(set(fetched)),
        "failed": failed,
        "count": len(set(fetched)),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = [
        "# Unretrieved or excluded assets",
        "",
        "This file is generated during the asset crawl and then extended with known gaps.",
        "",
        "## Crawl failures",
        "",
    ]
    lines.extend(failed or ["- None"])
    lines += [
        "",
        f"## Downloaded images: {len(set(fetched))}",
        "",
        "See `frontend/public/assets/manifest.json`.",
        "",
    ]
    LOG.write_text("\n".join(lines), encoding="utf-8")
    print(f"Downloaded {len(set(fetched))} assets, {len(failed)} failures")


if __name__ == "__main__":
    main()
