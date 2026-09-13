# Airdog overseas storefront

Multilingual official-style shop for customers outside Japan: **English**, **Simplified Chinese (Mainland)**, and **Traditional Chinese (Hong Kong)**. Visual layout follows [airdogjapan.co.jp](https://www.airdogjapan.co.jp/). Checkout is **inquiry-only** (no payment gateway).

## Stack

- Next.js 16 storefront (`frontend/`) with `next-intl`
- FastAPI + SQLAlchemy (`backend/`)
- MySQL 8
- Docker Compose

## Run with Docker

```bash
copy .env.example .env
docker compose up --build
```

- Storefront: http://localhost:3000/en
- API docs: http://localhost:8001/docs
- Admin: http://localhost:3000/admin (default `admin@example.com` / `admin1234`)
- MySQL on host port **3307** (container 3306) in case 3306 is already taken

Languages: `/en`, `/zh-CN`, `/zh-HK`.

## Local development (without full Docker for the web app)

1. Start MySQL and API: `docker compose up mysql api`
2. In `frontend/`: `npm install && set API_URL=http://127.0.0.1:8000 && npm run dev`

Refresh assets from the Japan site:

```bash
py -3.12 scripts/crawl_assets.py
```

## Notes

Brand names (`Airdog`, `TPA`, model numbers) are not translated. Some hero photographs still contain Japanese type; translated HTML overlays sit on top. Gaps are listed in `UNRETRIEVED.md`.
