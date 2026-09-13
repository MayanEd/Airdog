import { getProductById, getProducts } from "./catalog";
import type { Product } from "./api";

const CART_KEY = "airdog_cart";
const USER_KEY = "airdog_user";
const USERS_KEY = "airdog_users";
const INQUIRIES_KEY = "airdog_inquiries";
const CONTACTS_KEY = "airdog_contacts";
const EXTRA_PRODUCTS_KEY = "airdog_extra_products";
const DELETED_PRODUCTS_KEY = "airdog_deleted_products";
export const CART_EVENT = "airdog-cart";

type CartLine = { id: number; productId: number; quantity: number };
type StoredUser = { id: number; email: string; password: string; name: string; phone: string; is_admin: boolean };
type Inquiry = {
  id: number;
  user_id: number | null;
  name: string;
  email: string;
  phone: string;
  country: string;
  address: string;
  message: string;
  status: string;
  created_at: string;
  total_yen: number;
  items: { sku: string; quantity: number; price_yen: number }[];
};
type Contact = { id: number; name: string; email: string; product: string; message: string };

function read<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function write(key: string, value: unknown) {
  localStorage.setItem(key, JSON.stringify(value));
}

function emitCart() {
  window.dispatchEvent(new Event(CART_EVENT));
}

function seedUsers(): StoredUser[] {
  const rows = read<StoredUser[]>(USERS_KEY, []);
  if (rows.length) return rows;
  const seeded = [
    {
      id: 1,
      email: "admin@example.com",
      password: "admin1234",
      name: "Admin",
      phone: "",
      is_admin: true,
    },
  ];
  write(USERS_KEY, seeded);
  return seeded;
}

function publicUser(u: StoredUser) {
  return { id: u.id, email: u.email, name: u.name, phone: u.phone, is_admin: u.is_admin };
}

function serializeCart(locale: string) {
  const lines = read<CartLine[]>(CART_KEY, []);
  const items = lines
    .map((line) => {
      const product = getProductById(locale, line.productId);
      if (!product) return null;
      return {
        id: line.id,
        quantity: line.quantity,
        line_yen: line.quantity * product.price_yen,
        product,
      };
    })
    .filter(Boolean) as {
    id: number;
    quantity: number;
    line_yen: number;
    product: Product;
  }[];
  const total_yen = items.reduce((sum, row) => sum + row.line_yen, 0);
  const count = items.reduce((sum, row) => sum + row.quantity, 0);
  return { items, total_yen, count };
}

function currentUser(): StoredUser | null {
  const session = read<{ email: string } | null>(USER_KEY, null);
  if (!session) return null;
  return seedUsers().find((u) => u.email === session.email) || null;
}

function adminProducts(): Product[] {
  const extra = read<Product[]>(EXTRA_PRODUCTS_KEY, []);
  const deleted = read<number[]>(DELETED_PRODUCTS_KEY, []);
  return [...getProducts("en").filter((p) => !deleted.includes(p.id)), ...extra];
}

export function handleStaticApi(path: string, init?: RequestInit): { status: number; body: unknown } {
  const url = new URL(path, "https://airdog.local");
  const method = (init?.method || "GET").toUpperCase();
  const locale = url.searchParams.get("locale") || "en";
  const body = init?.body ? JSON.parse(String(init.body)) : {};
  const pathname = url.pathname.replace(/\/$/, "") || "/";

  if (pathname === "/api/auth/me" && method === "GET") {
    const user = currentUser();
    return user ? { status: 200, body: publicUser(user) } : { status: 401, body: { detail: "Unauthorized" } };
  }
  if (pathname === "/api/auth/login" && method === "POST") {
    const user = seedUsers().find((u) => u.email === body.email && u.password === body.password);
    if (!user) return { status: 401, body: { detail: "Invalid credentials" } };
    write(USER_KEY, { email: user.email });
    return { status: 200, body: publicUser(user) };
  }
  if (pathname === "/api/auth/logout" && method === "POST") {
    localStorage.removeItem(USER_KEY);
    return { status: 200, body: { ok: true } };
  }
  if (pathname === "/api/auth/register" && method === "POST") {
    const users = seedUsers();
    if (users.some((u) => u.email === body.email)) return { status: 400, body: { detail: "Exists" } };
    const user: StoredUser = {
      id: Date.now(),
      email: String(body.email || ""),
      password: String(body.password || ""),
      name: String(body.name || ""),
      phone: String(body.phone || ""),
      is_admin: false,
    };
    users.push(user);
    write(USERS_KEY, users);
    write(USER_KEY, { email: user.email });
    return { status: 200, body: publicUser(user) };
  }

  if (pathname === "/api/cart" && method === "GET") {
    return { status: 200, body: serializeCart(locale) };
  }
  if (pathname === "/api/cart" && method === "POST") {
    const lines = read<CartLine[]>(CART_KEY, []);
    const existing = lines.find((l) => l.productId === body.product_id);
    if (existing) existing.quantity += Number(body.quantity || 1);
    else lines.push({ id: Date.now(), productId: Number(body.product_id), quantity: Number(body.quantity || 1) });
    write(CART_KEY, lines);
    emitCart();
    return { status: 200, body: serializeCart(locale) };
  }
  const cartItem = pathname.match(/^\/api\/cart\/(\d+)$/);
  if (cartItem && method === "PATCH") {
    let lines = read<CartLine[]>(CART_KEY, []);
    const id = Number(cartItem[1]);
    if (Number(body.quantity) < 1) lines = lines.filter((l) => l.id !== id);
    else lines = lines.map((l) => (l.id === id ? { ...l, quantity: Number(body.quantity) } : l));
    write(CART_KEY, lines);
    emitCart();
    return { status: 200, body: serializeCart(locale) };
  }

  if (pathname === "/api/inquiries" && method === "POST") {
    const cart = serializeCart(locale);
    if (!cart.items.length) return { status: 400, body: { detail: "Empty cart" } };
    const inquiries = read<Inquiry[]>(INQUIRIES_KEY, []);
    const user = currentUser();
    inquiries.push({
      id: Date.now(),
      user_id: user?.id ?? null,
      name: String(body.name || ""),
      email: String(body.email || ""),
      phone: String(body.phone || ""),
      country: String(body.country || ""),
      address: String(body.address || ""),
      message: String(body.message || ""),
      status: "new",
      created_at: new Date().toISOString(),
      total_yen: cart.total_yen,
      items: cart.items.map((i) => ({ sku: i.product.sku, quantity: i.quantity, price_yen: i.product.price_yen })),
    });
    write(INQUIRIES_KEY, inquiries);
    write(CART_KEY, []);
    emitCart();
    return { status: 200, body: { ok: true } };
  }
  if (pathname === "/api/inquiries/mine" && method === "GET") {
    const user = currentUser();
    if (!user) return { status: 401, body: [] };
    return {
      status: 200,
      body: read<Inquiry[]>(INQUIRIES_KEY, []).filter((i) => i.user_id === user.id || i.email === user.email),
    };
  }

  if (pathname === "/api/contact" && method === "POST") {
    const contacts = read<Contact[]>(CONTACTS_KEY, []);
    contacts.push({
      id: Date.now(),
      name: String(body.name || ""),
      email: String(body.email || ""),
      product: String(body.product || ""),
      message: String(body.message || ""),
    });
    write(CONTACTS_KEY, contacts);
    return { status: 200, body: { ok: true } };
  }

  const user = currentUser();
  const adminDenied = { status: 403, body: { detail: "Admin only" } };
  if (pathname.startsWith("/api/admin") && (!user || !user.is_admin)) return adminDenied;

  if (pathname === "/api/admin/products" && method === "GET") return { status: 200, body: adminProducts() };
  if (pathname === "/api/admin/products" && method === "POST") {
    const extra = read<Product[]>(EXTRA_PRODUCTS_KEY, []);
    extra.push({
      id: Date.now(),
      sku: String(body.sku || ""),
      slug: String(body.slug || body.sku || "").toLowerCase(),
      price_yen: Number(body.price_yen || 0),
      stock_status: "in_stock",
      color: String(body.color || ""),
      size: "",
      is_service: false,
      image: String(body.image || "/assets/img/usr/slider/slider_lineup.jpg"),
      category_slug: null,
      name: String(body.translations?.[0]?.name || body.name || body.sku),
      subtitle: "",
      description: String(body.translations?.[0]?.description || ""),
    });
    write(EXTRA_PRODUCTS_KEY, extra);
    return { status: 200, body: { ok: true } };
  }
  const delProduct = pathname.match(/^\/api\/admin\/products\/(\d+)$/);
  if (delProduct && method === "DELETE") {
    const id = Number(delProduct[1]);
    write(
      EXTRA_PRODUCTS_KEY,
      read<Product[]>(EXTRA_PRODUCTS_KEY, []).filter((p) => p.id !== id),
    );
    write(DELETED_PRODUCTS_KEY, [...read<number[]>(DELETED_PRODUCTS_KEY, []), id]);
    return { status: 200, body: { ok: true } };
  }

  if (pathname === "/api/admin/users" && method === "GET") return { status: 200, body: seedUsers().map(publicUser) };
  if (pathname === "/api/admin/users" && method === "POST") {
    const users = seedUsers();
    users.push({
      id: Date.now(),
      email: String(body.email || ""),
      password: String(body.password || ""),
      name: String(body.name || ""),
      phone: "",
      is_admin: Boolean(body.is_admin),
    });
    write(USERS_KEY, users);
    return { status: 200, body: { ok: true } };
  }

  if (pathname === "/api/admin/inquiries" && method === "GET") return { status: 200, body: read<Inquiry[]>(INQUIRIES_KEY, []) };
  const patchInquiry = pathname.match(/^\/api\/admin\/inquiries\/(\d+)$/);
  if (patchInquiry && method === "PATCH") {
    const id = Number(patchInquiry[1]);
    write(
      INQUIRIES_KEY,
      read<Inquiry[]>(INQUIRIES_KEY, []).map((row) => (row.id === id ? { ...row, status: String(body.status) } : row)),
    );
    return { status: 200, body: { ok: true } };
  }
  if (pathname === "/api/admin/contacts" && method === "GET") return { status: 200, body: read<Contact[]>(CONTACTS_KEY, []) };

  return { status: 404, body: { detail: "Not found" } };
}
