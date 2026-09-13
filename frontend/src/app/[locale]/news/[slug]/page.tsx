import { setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { apiGet, type NewsItem } from "@/lib/api";
import { Link } from "@/i18n/navigation";

export default async function NewsDetailPage({ params }: { params: Promise<{ locale: string; slug: string }> }) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  let item: NewsItem;
  try {
    item = await apiGet<NewsItem>(`/news/${slug}`, locale);
  } catch {
    notFound();
  }
  return (
    <div className="container section prose">
      <p className="crumbs">
        <Link href="/news">NEWS</Link>
      </p>
      <time>{item.published_at.slice(0, 10)}</time>
      <h1>{item.title}</h1>
      <p>{item.body}</p>
    </div>
  );
}
