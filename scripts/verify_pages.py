import urllib.request
from pathlib import Path

checks = [
    ("http://localhost:3000/en", ["Best Rate Price", "LINE UP", "Find products", "header-logo", "hero-slide"]),
    ("http://localhost:3000/zh-CN", ["最优惠价格", "查找商品", "购物车"]),
    ("http://localhost:3000/zh-HK", ["最優惠價錢", "尋找商品", "購物車", "空氣清新機"]),
    ("http://localhost:3000/en/products/airdog-x5d-white", ["AIR-X5-H1W510", "Add to cart", "0.0146", "AQI"]),
    ("http://localhost:3000/en/categories/x-series", ["X5D", "X8D Pro", "X1D"]),
    ("http://localhost:3000/en/pages/faq", ["membership", "FAQ"]),
    ("http://localhost:3000/en/pages/medical", ["TPA", "warranty"]),
    ("http://localhost:3000/en/login", ["password"]),
    ("http://localhost:3000/en/cart", ["Shopping cart"]),
    ("http://localhost:3000/admin", ["Admin login", "admin@example.com"]),
]
lines = []
for url, needles in checks:
    html = urllib.request.urlopen(url, timeout=15).read().decode("utf-8", "replace")
    missing = [n for n in needles if n not in html]
    lines.append(f"OK {url}" if not missing else f"MISS {url} {missing}")
Path("verify-out.txt").write_text("\n".join(lines), encoding="utf-8")
