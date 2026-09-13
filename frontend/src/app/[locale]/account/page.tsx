"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { formatYen } from "@/lib/api";

type Inquiry = {
  id: number;
  status: string;
  created_at: string;
  total_yen: number;
  items: { sku: string; quantity: number; price_yen: number }[];
};

export default function AccountPage() {
  const t = useTranslations("account");
  const router = useRouter();
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);
  const [rows, setRows] = useState<Inquiry[]>([]);
  useEffect(() => {
    fetch("/api/auth/me", { credentials: "include" }).then(async (r) => {
      if (!r.ok) {
        router.push("/login");
        return;
      }
      setUser(await r.json());
    });
    fetch("/api/inquiries/mine", { credentials: "include" })
      .then((r) => (r.ok ? r.json() : []))
      .then(setRows);
  }, [router]);
  if (!user) return <div className="container section">…</div>;
  return (
    <div className="container section">
      <h1>{t("title")}</h1>
      <p>
        {user.name} / {user.email}
      </p>
      <h2>{t("orders")}</h2>
      {rows.length === 0 ? (
        <p>{t("empty")}</p>
      ) : (
        <table className="cart-table">
          <thead>
            <tr>
              <th>#</th>
              <th>{t("status")}</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.status}</td>
                <td>{formatYen(r.total_yen)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <p>
        <Link href="/products">{t("empty") === t("empty") ? "→" : ""}</Link>
      </p>
    </div>
  );
}
