"use client";

import { FormEvent, useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";

export default function LoginPage() {
  const t = useTranslations("auth");
  const router = useRouter();
  const [error, setError] = useState("");
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const res = await fetch("/api/auth/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: fd.get("email"), password: fd.get("password") }),
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
      <h1>{t("loginTitle")}</h1>
      <form className="form" onSubmit={onSubmit}>
        <label>
          {t("email")}
          <input name="email" type="email" required />
        </label>
        <label>
          {t("password")}
          <input name="password" type="password" required minLength={6} />
        </label>
        {error ? <p className="alert error">{error}</p> : null}
        <button className="btn-primary" type="submit">
          {t("submitLogin")}
        </button>
      </form>
      <p>
        {t("noAccount")} <Link href="/register">{t("submitRegister")}</Link>
      </p>
    </div>
  );
}
