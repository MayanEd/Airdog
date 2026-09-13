import { setRequestLocale } from "next-intl/server";
import ProductGrid from "@/components/ProductGrid";
import { apiGet, type Product } from "@/lib/api";

export default async function ProductsPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  let products: Product[] = [];
  try {
    products = await apiGet<Product[]>("/products", locale);
  } catch {
    products = [];
  }
  return <ProductGrid products={products} />;
}

