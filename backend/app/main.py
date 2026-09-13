import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, SessionLocal, engine
from .routers import admin, auth, cart, categories, contact, inquiries, news, pages, products
from .seed import seed_if_empty


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(
            db,
            os.getenv("ADMIN_EMAIL", "admin@example.com"),
            os.getenv("ADMIN_PASSWORD", "admin1234"),
        )
    finally:
        db.close()
    yield


app = FastAPI(title="Airdog API", lifespan=lifespan)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(news.router)
app.include_router(pages.router)
app.include_router(cart.router)
app.include_router(inquiries.router)
app.include_router(contact.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"ok": True}
