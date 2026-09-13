import {
  getCategories,
  getCategory,
  getNews,
  getNewsItem,
  getPage,
  getProduct,
  getProducts,
} from "./catalog";
import { isStatic } from "./paths";

const API = process.env.API_URL || "http://127.0.0.1:8000";

function staticGet(path: string, locale: string): unknown {
  const url = new URL(path, "https://airdog.local");
  const pathname = url.pathname;
  const q = url.searchParams.get("q") || undefined;
  const category = url.searchParams.get("category") || undefined;

  if (pathname === "/categories") return getCategories(locale);
  if (pathname.startsWith("/categories/")) {
    const slug = pathname.slice("/categories/".length);
    const row = getCategory(locale, slug);
    if (!row) throw new Error(`API 404 ${path}`);
    return row;
  }
  if (pathname === "/products") return getProducts(locale, { q, category });
  if (pathname.startsWith("/products/")) {
    const slug = pathname.slice("/products/".length);
    const row = getProduct(locale, slug);
    if (!row) throw new Error(`API 404 ${path}`);
    return row;
  }
  if (pathname === "/news") return getNews(locale);
  if (pathname.startsWith("/news/")) {
    const slug = pathname.slice("/news/".length);
    const row = getNewsItem(locale, slug);
    if (!row) throw new Error(`API 404 ${path}`);
    return row;
  }
  if (pathname.startsWith("/pages/")) {
    const slug = pathname.slice("/pages/".length);
    const row = getPage(locale, slug);
    if (!row) throw new Error(`API 404 ${path}`);
    return row;
  }
  throw new Error(`API 404 ${path}`);
}

export async function apiGet<T>(path: string, locale = "en"): Promise<T> {
  if (isStatic) {
    return staticGet(path, locale) as T;
  }
  try {
    const join = path.includes("?") ? "&" : "?";
    const res = await fetch(`${API}${path}${join}locale=${encodeURIComponent(locale)}`, {
      cache: "no-store",
    });
    if (res.ok) return res.json();
  } catch {
    // Fall back to the bundled catalog when the API is not running (Docker image build, local export).
  }
  return staticGet(path, locale) as T;
}

export function formatYen(value: number) {
  return `¥${value.toLocaleString("ja-JP")}`;
}

export type Category = {
  id: number;
  slug: string;
  image: string;
  name: string;
  description: string;
  show_in_nav: boolean;
};

export type Product = {
  id: number;
  sku: string;
  slug: string;
  price_yen: number;
  stock_status: string;
  color: string;
  size: string;
  is_service: boolean;
  image: string;
  category_slug: string | null;
  name: string;
  subtitle: string;
  description?: string;
  included?: string;
  specs_json?: string;
  disclaimers?: string;
  images?: { url: string; alt: string }[];
};

export type NewsItem = {
  id: number;
  slug: string;
  published_at: string;
  title: string;
  body: string;
};

export type CmsPage = {
  slug: string;
  title: string;
  body: string;
};
