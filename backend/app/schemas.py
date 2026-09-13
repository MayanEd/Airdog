from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = ""
    phone: str = ""


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    phone: str
    is_admin: bool

    class Config:
        from_attributes = True


class UserUpdateIn(BaseModel):
    name: str | None = None
    phone: str | None = None
    password: str | None = None
    is_admin: bool | None = None


class CartAddIn(BaseModel):
    product_id: int
    quantity: int = 1


class CartUpdateIn(BaseModel):
    quantity: int


class InquiryIn(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    country: str = ""
    address: str = ""
    message: str = ""


class ContactIn(BaseModel):
    name: str
    email: EmailStr
    product: str = ""
    message: str


class ProductAdminIn(BaseModel):
    sku: str
    slug: str
    category_id: int | None = None
    price_yen: int = 0
    stock_status: str = "in_stock"
    color: str = ""
    size: str = ""
    is_service: bool = False
    featured: bool = False
    sort_order: int = 0
    image: str = ""
    translations: list[dict] = []
    images: list[dict] = []


class CategoryAdminIn(BaseModel):
    slug: str
    image: str = ""
    sort_order: int = 0
    show_in_nav: bool = True
    translations: list[dict] = []


class NewsAdminIn(BaseModel):
    slug: str
    published_at: datetime | None = None
    translations: list[dict] = []


class PageAdminIn(BaseModel):
    slug: str
    locale: str
    title: str
    body: str = ""


class InquiryStatusIn(BaseModel):
    status: str
