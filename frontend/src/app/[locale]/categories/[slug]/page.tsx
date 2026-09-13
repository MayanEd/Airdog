import { setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import ProductCard from "@/components/ProductCard";
import { apiGet, type Category, type Product } from "@/lib/api";
import { Link } from "@/i18n/navigation";
import { categorySlugs } from "@/lib/catalog";
import { assetUrl } from "@/lib/paths";
import { routing } from "@/i18n/routing";

export function generateStaticParams() {
  return routing.locales.flatMap((locale) => categorySlugs().map((slug) => ({ locale, slug })));
}

export const dynamicParams = false;

export default async function CategoryPage({ params }: { params: Promise<{ locale: string; slug: string }> }) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  let cat: Category;
  try {
    cat = await apiGet<Category>(`/categories/${slug}`, locale);
  } catch {
    notFound();
  }
  let products: Product[] = [];
  try {
    products = await apiGet<Product[]>(`/products?category=${slug}`, locale);
  } catch {
    products = [];
  }
  return (
    <div className="container section">
      <p className="crumbs">
        <Link href="/">Home</Link> &gt; {cat.name}
      </p>
      <div className="page-hero">
        <h1>{cat.name}</h1>
        <p>{cat.description}</p>
      </div>
      {cat.image ? <img src={assetUrl(cat.image)} alt="" style={{ width: "100%", maxHeight: 320, objectFit: "cover", marginBottom: 24 }} /> : null}
      <div className="product-grid">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
