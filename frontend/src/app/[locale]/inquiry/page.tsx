"use client";

import { FormEvent, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { formatYen } from "@/lib/api";

export default function InquiryPage() {
  const t = useTranslations("inquiry");
  const locale = useLocale();
  const [ok, setOk] = useState(false);
  const [err, setErr] = useState("");
  const [total, setTotal] = useState(0);
  const [empty, setEmpty] = useState(false);
  useEffect(() => {
    fetch(`/api/cart?locale=${locale}`, { credentials: "include" })
      .then((r) => r.json())
      .then((d) => {
        setTotal(d.total_yen || 0);
        setEmpty(!d.items?.length);
      });
  }, [locale]);
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const res = await fetch(`/api/inquiries?locale=${locale}`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: fd.get("name"),
        email: fd.get("email"),
        phone: fd.get("phone"),
        country: fd.get("country"),
        address: fd.get("address"),
        message: fd.get("message"),
      }),
    });
    if (!res.ok) {
      setErr(t("needItems"));
      return;
    }
    setOk(true);
  }
  if (ok) {
    return (
      <div className="container section">
        <p className="alert">{t("success")}</p>
        <Link href="/">{t("submit")}</Link>
      </div>
    );
  }
  return (
    <div className="container section">
      <h1>{t("title")}</h1>
      <p>{t("intro")}</p>
      {empty ? (
        <p>
          {t("needItems")} <Link href="/products">→</Link>
        </p>
      ) : (
        <p>
          {formatYen(total)}
        </p>
      )}
      <form className="form" onSubmit={onSubmit}>
        <label>
          {t("name")}
          <input name="name" required />
        </label>
        <label>
          {t("email")}
          <input name="email" type="email" required />
        </label>
        <label>
          {t("phone")}
          <input name="phone" />
        </label>
        <label>
          {t("country")}
          <input name="country" required />
        </label>
        <label>
          {t("address")}
          <textarea name="address" rows={3} required />
        </label>
        <label>
          {t("message")}
          <textarea name="message" rows={4} />
        </label>
        {err ? <p className="alert error">{err}</p> : null}
        <button className="btn-primary" type="submit" disabled={empty}>
          {t("submit")}
        </button>
      </form>
    </div>
  );
}
