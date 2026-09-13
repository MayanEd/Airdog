"use client";

import { useLocale } from "next-intl";
import { Link, usePathname } from "@/i18n/navigation";

const LABELS: Record<string, string> = { en: "EN", "zh-CN": "简", "zh-HK": "繁" };

export default function LanguageSwitcher() {
  const locale = useLocale();
  const pathname = usePathname();
  return (
    <div className="lang-switch" aria-label="Language">
      {(["en", "zh-CN", "zh-HK"] as const).map((loc) => (
        <Link key={loc} href={pathname} locale={loc} className={loc === locale ? "active" : ""}>
          {LABELS[loc]}
        </Link>
      ))}
    </div>
  );
}
