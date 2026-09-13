"use client";

import { FormEvent, useState } from "react";
import { useTranslations } from "next-intl";

export default function AddToCart({ productId }: { productId: number }) {
  const t = useTranslations("product");
  const [qty, setQty] = useState(1);
  const [msg, setMsg] = useState("");
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const res = await fetch("/api/cart?locale=en", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: qty }),
    });
    setMsg(res.ok ? t("added") : "Error");
  }
  return (
    <form onSubmit={onSubmit}>
      <label>
        {t("quantity")}{" "}
        <input className="qty" type="number" min={1} value={qty} onChange={(e) => setQty(Number(e.target.value))} />
      </label>
      <button className="btn-primary" type="submit">
        {t("addToCart")}
      </button>
      {msg ? <p className="alert">{msg}</p> : null}
    </form>
  );
}
