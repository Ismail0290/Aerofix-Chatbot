export function getApiBaseUrl(): string {
  return (
    process.env.AEROFIX_API_URL ??
    process.env.NEXT_PUBLIC_AEROFIX_API_URL ??
    "http://127.0.0.1:8000"
  ).replace(/\/$/, "");
}
