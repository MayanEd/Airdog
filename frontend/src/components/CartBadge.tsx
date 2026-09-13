"use client";

import { useEffect, useState } from "react";
import { Link } from "@/i18n/navigation";
import { CART_EVENT } from "@/lib/clientStore";
import { apiFetch } from "@/lib/shopApi";

export default function CartBadge() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    function load() {
      apiFetch("/api/cart?locale=en")
        .then((r) => r.json())
        .then((d) => setCount(d.count || 0))
        .catch(() => setCount(0));
    }
    load();
    window.addEventListener(CART_EVENT, load);
    return () => window.removeEventListener(CART_EVENT, load);
  }, []);
  return (
    <Link href="/cart" className="cart-link" aria-label="Cart">
      🛒
      {count > 0 ? <span className="cart-badge">{count}</span> : null}
    </Link>
  );
}
