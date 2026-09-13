# Unretrieved or excluded assets

The image crawl completed (see `frontend/public/assets/manifest.json`). The items below could not be mirrored as interactive pages, or were intentionally omitted.

## Pages and services

| Item | Reason | Alternative in this project |
| --- | --- | --- |
| `https://airdogjapan-service.jp/` | Separate Japan-only filter-exchange portal | [`/pages/filter-service`](frontend) informational page + outbound link |
| Contact form HTML (`/shop/contact/contact.aspx`) | HTTP **403** during fetch | Rebuilt contact form posting to FastAPI `/contact` |
| `https://www.airdogjapan.co.jp/sitemap_index.xml` | HTTP **500** | Manual crawl of nav, categories, product URLs |
| GTM / Facebook / Yahoo / Microsoft Clarity / LINE pixels | Tracking, not storefront | Omitted |
| Online payments (cards, Amazon Pay) | Out of MVP | Inquiry checkout |
| Full historic news bodies beyond the five homepage headlines | Only those URLs were seeded after crawl of listing titles | Add via Admin or extend `backend/app/seed.py` |
| CARE+ coupon phone flow (`0120-331-193`) | Japan free-dial only | CARE+ page + inquiry CTA |
| Japan Specified Commercial Transactions Act page | Domestic JP legal listing | Translated **Seller information** page for overseas customers |

## Japanese text inside photographs

Hero and campaign JPEGs still contain Japanese type baked into the pixels (for example “世界最強レベルの空気清浄機”, medical-facility banners). Translated HTML overlays are drawn on the homepage slider. Remaining in-image JP copy is listed in the downloaded originals under `frontend/public/assets/img/usr/slider/` and `img/campaign/`.

## Product photography

Category and slider images were saved locally. Some SKU-specific studio shots on the Japan PDP may use hashed CMS filenames; those extra frames are in the crawl dump when discovered. If a SKU still uses a slider photo as its primary image, replace `products.image` in Admin.
