"use client";

import { FormEvent, useState } from "react";
import { useTranslations } from "next-intl";
import { apiFetch } from "@/lib/shopApi";

export default function ContactPage() {
  const t = useTranslations("contact");
  const [ok, setOk] = useState(false);
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const res = await apiFetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: fd.get("name"),
        email: fd.get("email"),
        product: fd.get("product"),
        message: fd.get("message"),
      }),
    });
    if (res.ok) setOk(true);
  }
  return (
    <div className="container section">
      <h1>{t("title")}</h1>
      <p>{t("intro")}</p>
      {ok ? (
        <p className="alert">{t("success")}</p>
      ) : (
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
            {t("product")}
            <input name="product" />
          </label>
          <label>
            {t("message")}
            <textarea name="message" rows={6} required />
          </label>
          <button className="btn-primary" type="submit">
            {t("submit")}
          </button>
        </form>
      )}
    </div>
  );
}
