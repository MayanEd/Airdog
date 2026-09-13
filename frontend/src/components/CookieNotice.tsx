"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

export default function CookieNotice() {
  const t = useTranslations("cookie");
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (!localStorage.getItem("airdog_cookie")) setOpen(true);
  }, []);
  if (!open) return null;
  return (
    <div className="cookie">
      <span>{t("text")}</span>
      <button
        type="button"
        onClick={() => {
          localStorage.setItem("airdog_cookie", "1");
          setOpen(false);
        }}
      >
        {t("accept")}
      </button>
    </div>
  );
}
