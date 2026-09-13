import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";

export default async function Footer() {
  const t = await getTranslations("footer");
  const links = [
    ["/pages/guide", t("guide")],
    ["/pages/faq", t("faq")],
    ["/pages/shipping", t("shipping")],
    ["/pages/returns", t("returns")],
    ["/pages/warranty", t("warranty")],
    ["/pages/import-attention", t("import")],
    ["/pages/privacy", t("privacy")],
    ["/pages/company", t("company")],
    ["/pages/seller-info", t("seller")],
    ["/contact", t("contact")],
    ["/pages/terms-of-sales", t("sales")],
    ["/pages/terms-of-use", t("use")],
    ["/pages/terms-of-airdogcare", t("careTerms")],
  ] as const;
  return (
    <footer className="site-footer">
      <ul className="footer-links">
        {links.map(([href, label]) => (
          <li key={href}>
            <Link href={href}>{label}</Link>
          </li>
        ))}
        <li>
          <a href="https://www.instagram.com/airdog.tokyo/" target="_blank" rel="noreferrer">
            {t("instagram")}
          </a>
        </li>
        <li>
          <a href="https://www.facebook.com/airdog.tokyo" target="_blank" rel="noreferrer">
            {t("facebook")}
          </a>
        </li>
      </ul>
      <p className="copy">{t("copyright")}</p>
    </footer>
  );
}
