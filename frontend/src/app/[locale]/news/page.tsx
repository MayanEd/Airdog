import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { apiGet, type NewsItem } from "@/lib/api";

export default async function NewsListPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("home");
  const news = await apiGet<NewsItem[]>("/news", locale).catch(() => [] as NewsItem[]);
  return (
    <div className="container section">
      <div className="section-title">
        <h2>{t("news")}</h2>
        <span>{t("newsSub")}</span>
      </div>
      <ul className="news-list">
        {news.map((n) => (
          <li key={n.slug}>
            <Link href={`/news/${n.slug}`}>
              <time>{n.published_at.slice(0, 10).replaceAll("-", ".")}</time>
              <span>{n.title}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
