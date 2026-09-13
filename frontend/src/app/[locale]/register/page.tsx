"use client";

import { FormEvent, useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";

export default function RegisterPage() {
  const t = useTranslations("auth");
  const router = useRouter();
  const [error, setError] = useState("");
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const res = await fetch("/api/auth/register", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: fd.get("email"),
        password: fd.get("password"),
        name: fd.get("name"),
        phone: fd.get("phone"),
      }),
    });
    if (!res.ok) {
      setError(t("error"));
      return;
    }
    router.push("/account");
    router.refresh();
  }
  return (
    <div className="container section">
      <h1>{t("registerTitle")}</h1>
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
          {t("password")}
          <input name="password" type="password" required minLength={6} />
        </label>
        {error ? <p className="alert error">{error}</p> : null}
        <button className="btn-primary" type="submit">
          {t("submitRegister")}
        </button>
      </form>
      <p>
        {t("hasAccount")} <Link href="/login">{t("submitLogin")}</Link>
      </p>
    </div>
  );
}
