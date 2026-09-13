"use client";

import { useEffect, useState } from "react";
import { Link } from "@/i18n/navigation";

export default function CartBadge() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    fetch("/api/cart?locale=en", { credentials: "include" })
      .then((r) => r.json())
      .then((d) => setCount(d.count || 0))
      .catch(() => setCount(0));
  }, []);
  return (
    <Link href="/cart" className="cart-link" aria-label="Cart">
      🛒
      {count > 0 ? <span className="cart-badge">{count}</span> : null}
    </Link>
  );
}
