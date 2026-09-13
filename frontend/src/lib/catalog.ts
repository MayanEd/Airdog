import catalog from "@/data/catalog.json";
import type { Category, CmsPage, NewsItem, Product } from "./api";

type LocaleMap<T> = Record<string, T[]>;

const data = catalog as {
  categories: LocaleMap<Category>;
  products: LocaleMap<Product>;
  news: LocaleMap<NewsItem>;
  pages: LocaleMap<CmsPage>;
};

function localeKey(locale: string) {
  return locale in data.categories ? locale : "en";
}

export function getCategories(locale: string): Category[] {
  return data.categories[localeKey(locale)] || [];
}

export function getCategory(locale: string, slug: string): Category | undefined {
  return getCategories(locale).find((c) => c.slug === slug);
}

export function getProducts(locale: string, opts?: { q?: string; category?: string }): Product[] {
  let rows = data.products[localeKey(locale)] || [];
  if (opts?.category) {
    rows = rows.filter((p) => p.category_slug === opts.category);
  }
  if (opts?.q) {
    const q = opts.q.toLowerCase();
    rows = rows.filter((p) =>
      [p.name, p.sku, p.slug, p.subtitle, p.description || ""].join(" ").toLowerCase().includes(q),
    );
  }
  return rows;
}

export function getProduct(locale: string, slug: string): Product | undefined {
  return getProducts(locale).find((p) => p.slug === slug);
}

export function getProductById(locale: string, id: number): Product | undefined {
  return getProducts(locale).find((p) => p.id === id);
}

export function getNews(locale: string): NewsItem[] {
  return data.news[localeKey(locale)] || [];
}

export function getNewsItem(locale: string, slug: string): NewsItem | undefined {
  return getNews(locale).find((n) => n.slug === slug);
}

export function getPage(locale: string, slug: string): CmsPage | undefined {
  return (data.pages[localeKey(locale)] || []).find((p) => p.slug === slug);
}

export function categorySlugs() {
  return [...new Set(getCategories("en").map((c) => c.slug))];
}

export function productSlugs() {
  return [...new Set(getProducts("en").map((p) => p.slug))];
}

export function newsSlugs() {
  return [...new Set(getNews("en").map((n) => n.slug))];
}

export function pageSlugs() {
  return [...new Set((data.pages.en || []).map((p) => p.slug))];
}
