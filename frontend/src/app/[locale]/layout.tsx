import { NextIntlClientProvider, hasLocale } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";
import { Noto_Sans_HK, Noto_Sans_SC, Work_Sans } from "next/font/google";
import { notFound } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import CookieNotice from "@/components/CookieNotice";
import { apiGet, type Category } from "@/lib/api";
import { routing } from "@/i18n/routing";
import "../globals.css";

const workSans = Work_Sans({ subsets: ["latin"], variable: "--font-work" });
const notoSc = Noto_Sans_SC({ variable: "--font-sc", weight: ["400", "500", "600"] });
const notoHk = Noto_Sans_HK({ variable: "--font-hk", weight: ["400", "500", "600"] });

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const messages = (await import(`../../../messages/${locale}.json`)).default as { meta: { title: string; description: string } };
  return { title: messages.meta.title, description: messages.meta.description };
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) notFound();
  setRequestLocale(locale);
  const messages = await getMessages();
  let categories: Category[] = [];
  try {
    categories = await apiGet<Category[]>("/categories", locale);
  } catch {
    categories = [];
  }
  return (
    <html lang={locale} className={`${workSans.variable} ${notoSc.variable} ${notoHk.variable}`}>
      <body style={{ ["--font-sans" as string]: `${workSans.style.fontFamily}, ${locale === "zh-HK" ? notoHk.style.fontFamily : notoSc.style.fontFamily}` }}>
        <NextIntlClientProvider messages={messages}>
          <Header categories={categories} />
          <main>{children}</main>
          <Footer />
          <CookieNotice />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
