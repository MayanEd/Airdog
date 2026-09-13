export function assetUrl(path: string) {
  if (!path.startsWith("/")) return path;
  const base = process.env.NEXT_PUBLIC_BASE_PATH || "";
  return `${base}${path}`;
}

export const isStatic = process.env.NEXT_PUBLIC_STATIC === "1";
