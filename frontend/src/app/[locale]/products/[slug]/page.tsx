import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import AddToCart from "@/components/AddToCart";
import { apiGet, formatYen, type Product } from "@/lib/api";
import { Link } from "@/i18n/navigation";

export default async function ProductPage({ params }: { params: Promise<{ locale: string; slug: string }> }) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("product");
  const tNav = await getTranslations("nav");
  let product: Product;
  try {
    product = await apiGet<Product>(`/products/${slug}`, locale);
  } catch {
    notFound();
  }
  let specs: { label: string; value: string }[] = [];
  try {
    specs = JSON.parse(product.specs_json || "[]");
  } catch {
    specs = [];
  }
  return (
    <div className="container">
      <p className="crumbs">
        <Link href="/">{tNav("home")}</Link> &gt;{" "}
        {product.category_slug ? (
          <Link href={`/categories/${product.category_slug}`}>{product.category_slug}</Link>
        ) : null}{" "}
        &gt; {product.name}
      </p>
      <div className="pdp">
        <div className="pdp-gallery">
          <img src={product.image} alt={product.name} />
        </div>
        <div>
          <h1>{product.name}</h1>
          <p>{product.subtitle}</p>
          <p className="price-lg">
            {formatYen(product.price_yen)} <small>{t("priceTaxIn")}</small>
          </p>
          <p>
            <strong>{t("sku")}:</strong> {product.sku}
          </p>
          {product.color ? (
            <p>
              <strong>{t("color")}:</strong> {product.color}
            </p>
          ) : null}
          {product.size ? (
            <p>
              <strong>{t("size")}:</strong> {product.size}
            </p>
          ) : null}
          <p>
            <strong>{t("stock")}:</strong> {t("in_stock")}
          </p>
          <AddToCart productId={product.id} />
        </div>
      </div>
      <div className="prose">
        <h2>{t("description")}</h2>
        <p>{product.description}</p>
        <h2>{t("included")}</h2>
        <p>{product.included}</p>
        <h2>{t("specs")}</h2>
        <table className="spec-table">
          <tbody>
            {specs.map((row) => (
              <tr key={row.label}>
                <th>{row.label}</th>
                <td>{row.value}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {product.disclaimers ? (
          <>
            <h2>{t("disclaimers")}</h2>
            <p>{product.disclaimers}</p>
          </>
        ) : null}
      </div>
    </div>
  );
}
