const API = process.env.API_URL || "http://127.0.0.1:8000";

export async function apiGet<T>(path: string, locale = "en"): Promise<T> {
  const join = path.includes("?") ? "&" : "?";
  const res = await fetch(`${API}${path}${join}locale=${encodeURIComponent(locale)}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`API ${res.status} ${path}`);
  }
  return res.json();
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
