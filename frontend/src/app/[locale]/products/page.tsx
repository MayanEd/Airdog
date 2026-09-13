import { getTranslations, setRequestLocale } from "next-intl/server";
import ProductCard from "@/components/ProductCard";
import { apiGet, type Product } from "@/lib/api";

export default async function ProductsPage({
  params,
  searchParams,
}: {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ q?: string }>;
}) {
  const { locale } = await params;
  const { q } = await searchParams;
  setRequestLocale(locale);
  const t = await getTranslations("nav");
  const path = q ? `/products?q=${encodeURIComponent(q)}` : "/products";
  let products: Product[] = [];
  try {
    products = await apiGet<Product[]>(path, locale);
  } catch {
    products = [];
  }
  return (
    <div className="container section">
      <div className="page-hero">
        <h1>{q ? `${t("search")}: ${q}` : t("allProducts")}</h1>
      </div>
      <div className="product-grid">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
