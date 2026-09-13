import { handleStaticApi } from "./clientStore";
import { isStatic } from "./paths";

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  if (!isStatic) {
    return fetch(path, { credentials: "include", ...init });
  }
  const result = handleStaticApi(path, init);
  return new Response(JSON.stringify(result.body), {
    status: result.status,
    headers: { "Content-Type": "application/json" },
  });
}
