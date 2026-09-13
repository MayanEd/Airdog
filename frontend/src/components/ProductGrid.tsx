"use client";

import { useEffect, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import ProductCard from "@/components/ProductCard";
import type { Product } from "@/lib/api";

export default function ProductGrid({ products }: { products: Product[] }) {
  const t = useTranslations("nav");
  const [q, setQ] = useState<string | null>(null);
  useEffect(() => {
    setQ(new URLSearchParams(window.location.search).get("q") || "");
  }, []);
  const rows = useMemo(() => {
    if (!q) return products;
    const needle = q.toLowerCase();
    return products.filter((p) =>
      [p.name, p.sku, p.slug, p.subtitle, p.description || ""].join(" ").toLowerCase().includes(needle),
    );
  }, [products, q]);
  const title = q ? `${t("search")}: ${q}` : t("allProducts");
  return (
    <div className="container section">
      <div className="page-hero">
        <h1>{title}</h1>
      </div>
      <div className="product-grid">
        {rows.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
