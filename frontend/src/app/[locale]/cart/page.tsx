"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { formatYen } from "@/lib/api";

type Cart = {
  items: { id: number; quantity: number; line_yen: number; product: { slug: string; name: string; sku: string; price_yen: number; image: string } }[];
  total_yen: number;
};

export default function CartPage() {
  const t = useTranslations("cart");
  const locale = useLocale();
  const [cart, setCart] = useState<Cart | null>(null);
  function load() {
    fetch(`/api/cart?locale=${locale}`, { credentials: "include" })
      .then((r) => r.json())
      .then(setCart);
  }
  useEffect(() => {
    load();
  }, [locale]);
  async function update(id: number, quantity: number) {
    await fetch(`/api/cart/${id}?locale=${locale}`, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quantity }),
    });
    load();
  }
  if (!cart) return <div className="container section">…</div>;
  return (
    <div className="container section">
      <h1>{t("title")}</h1>
      {cart.items.length === 0 ? (
        <p>
          {t("empty")} <Link href="/products">{t("continue")}</Link>
        </p>
      ) : (
        <>
          <table className="cart-table">
            <thead>
              <tr>
                <th></th>
                <th>Item</th>
                <th>{t("total")}</th>
              </tr>
            </thead>
            <tbody>
              {cart.items.map((item) => (
                <tr key={item.id}>
                  <td>
                    <img src={item.product.image} alt="" width={80} />
                  </td>
                  <td>
                    <Link href={`/products/${item.product.slug}`}>{item.product.name}</Link>
                    <div>
                      <input
                        className="qty"
                        type="number"
                        min={1}
                        defaultValue={item.quantity}
                        onBlur={(e) => update(item.id, Number(e.target.value))}
                      />
                      <button type="button" className="btn-ghost" onClick={() => update(item.id, 0)}>
                        {t("remove")}
                      </button>
                    </div>
                  </td>
                  <td>{formatYen(item.line_yen)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="cart-total">
            {t("total")}: {formatYen(cart.total_yen)}
          </p>
          <Link className="btn-primary" href="/inquiry" style={{ display: "inline-block" }}>
            {t("checkout")}
          </Link>
        </>
      )}
    </div>
  );
}
