"use client";

import { FormEvent, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import LanguageSwitcher from "./LanguageSwitcher";
import CartBadge from "./CartBadge";
import type { Category } from "@/lib/api";

export default function Header({ categories }: { categories: Category[] }) {
  const t = useTranslations("nav");
  const promo = useTranslations("promo");
  const router = useRouter();
  const [q, setQ] = useState("");
  const [user, setUser] = useState<{ name: string; email: string; is_admin: boolean } | null>(null);

  useEffect(() => {
    fetch("/api/auth/me", { credentials: "include" })
      .then((r) => (r.ok ? r.json() : null))
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  function onSearch(e: FormEvent) {
    e.preventDefault();
    router.push(`/products?q=${encodeURIComponent(q)}`);
  }

  return (
    <header className="site-header">
      <div className="header-top">
        <Link href="/" className="logo">
          <img src="/assets/img/usr/common/header-logo.webp" alt="Airdog Japan" />
        </Link>
        <form className="search-form" onSubmit={onSearch}>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={t("searchPlaceholder")}
            aria-label={t("search")}
          />
          <button type="submit" aria-label={t("search")}>
            🔍
          </button>
        </form>
        <div className="header-tools">
          <LanguageSwitcher />
          {user ? (
            <>
              <Link href="/account">{t("account")}</Link>
              <span className="sep">/</span>
              <button
                className="btn-ghost"
                type="button"
                onClick={async () => {
                  await fetch("/api/auth/logout", { method: "POST", credentials: "include" });
                  setUser(null);
                  router.refresh();
                }}
              >
                {t("logout")}
              </button>
              {user.is_admin ? <a href="/admin">Admin</a> : null}
            </>
          ) : (
            <>
              <Link href="/login">{t("login")}</Link>
              <span className="sep">/</span>
              <Link href="/register">{t("register")}</Link>
            </>
          )}
          <CartBadge />
        </div>
      </div>
      <nav className="global-nav">
        <ul className="nav-inner">
          <li className="nav-item">
            <Link href="/products">{t("findProducts")} ▾</Link>
            <div className="dropdown">
              {categories
                .filter((c) => c.show_in_nav)
                .map((c) => (
                  <Link key={c.slug} href={`/categories/${c.slug}`}>
                    {c.name}
                  </Link>
                ))}
            </div>
          </li>
          <li>
            <Link href="/news">{t("news")}</Link>
          </li>
          <li>
            <Link href="/contact">{t("contact")}</Link>
          </li>
          <li>
            <Link href="/pages/faq">{t("faq")}</Link>
          </li>
          <li>
            <Link href="/pages/medical">{t("medical")}</Link>
          </li>
        </ul>
      </nav>
      <div className="promo-bar">
        <p>{promo("headline")}</p>
        <p className="note">{promo("note")}</p>
      </div>
    </header>
  );
}
