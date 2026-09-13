import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import HeroSlider from "@/components/HeroSlider";
import { apiGet, type Category, type NewsItem } from "@/lib/api";

export default async function HomePage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("home");
  const tNav = await getTranslations("nav");
  let news: NewsItem[] = [];
  let cats: Category[] = [];
  try {
    news = await apiGet<NewsItem[]>("/news", locale);
    cats = await apiGet<Category[]>("/categories", locale);
  } catch {
    news = [];
    cats = [];
  }
  const lineup = cats.filter((c) => ["x-series", "mini", "moi", "options", "filter-service", "care-plus"].includes(c.slug));
  return (
    <>
      <HeroSlider />
      <section className="section">
        <div className="container">
          <div className="section-title">
            <h2>{t("news")}</h2>
            <span>{t("newsSub")}</span>
          </div>
          <ul className="news-list">
            {news.slice(0, 5).map((n) => (
              <li key={n.slug}>
                <Link href={`/news/${n.slug}`}>
                  <time>{n.published_at.slice(0, 10).replaceAll("-", ".")}</time>
                  <span>{n.title}</span>
                </Link>
              </li>
            ))}
          </ul>
          <p style={{ textAlign: "center", marginTop: 16 }}>
            <Link href="/news">{t("readMore")}</Link>
          </p>
        </div>
      </section>
      <section className="section" style={{ background: "#fafafa" }}>
        <div className="container">
          <div className="section-title">
            <h2>{t("lineup")}</h2>
            <span>{t("lineupSub")}</span>
          </div>
          <div className="lineup-grid">
            {lineup.map((c) => (
              <Link key={c.slug} href={c.slug === "filter-service" ? "/pages/filter-service" : c.slug === "care-plus" ? "/pages/care-plus" : `/categories/${c.slug}`} className="lineup-card">
                <img src={c.image} alt={c.name} />
                <h3>{c.name}</h3>
                <p>{c.description}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <div className="section-title">
            <h2>{t("special")}</h2>
            <span>{t("specialSub")}</span>
          </div>
          <div className="lineup-grid">
            <Link href="/pages/medical" className="lineup-card">
              <img src="/assets/img/campaign/medical_banner_20250119.jpg" alt="" />
              <h3>{tNav("medical")}</h3>
            </Link>
            <Link href="/pages/care-plus" className="lineup-card">
              <img src="/assets/img/usr/slider/slider_airdogcare-plus.jpg" alt="Airdog CARE+" />
              <h3>Airdog CARE+</h3>
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
