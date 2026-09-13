import { setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { apiGet, type CmsPage } from "@/lib/api";
import { pageSlugs } from "@/lib/catalog";
import { routing } from "@/i18n/routing";

export function generateStaticParams() {
  return routing.locales.flatMap((locale) => pageSlugs().map((slug) => ({ locale, slug })));
}

export const dynamicParams = false;

export default async function CmsPageView({ params }: { params: Promise<{ locale: string; slug: string }> }) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  let page: CmsPage;
  try {
    page = await apiGet<CmsPage>(`/pages/${slug}`, locale);
  } catch {
    notFound();
  }
  return (
    <div className="container section prose">
      <h1>{page.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: page.body }} />
    </div>
  );
}
