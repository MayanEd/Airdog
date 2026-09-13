import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const api = process.env.API_URL || "http://127.0.0.1:8000";
const isStatic = process.env.NEXT_PUBLIC_STATIC === "1";
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

const nextConfig: NextConfig = {
  output: isStatic ? "export" : "standalone",
  images: { unoptimized: true },
  trailingSlash: isStatic,
  ...(basePath ? { basePath } : {}),
};

if (!isStatic) {
  nextConfig.rewrites = async () => [{ source: "/api/:path*", destination: `${api}/:path*` }];
}

export default withNextIntl(nextConfig);
