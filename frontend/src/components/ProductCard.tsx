import { Link } from "@/i18n/navigation";
import { formatYen, type Product } from "@/lib/api";

export default function ProductCard({ product }: { product: Product }) {
  return (
    <article className="product-card">
      <Link href={`/products/${product.slug}`}>
        <img src={product.image} alt={product.name} />
        <h3>{product.name}</h3>
        <p className="meta">{product.subtitle}</p>
        <p className="price">{formatYen(product.price_yen)}</p>
      </Link>
    </article>
  );
}
