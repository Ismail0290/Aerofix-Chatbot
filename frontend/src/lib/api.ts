import { getApiBaseUrl } from "./config";
import type {
  ContextResponse,
  DevicesResponse,
  FailuresResponse,
  LatestLogsResponse,
  PriorityResponse,
} from "./types";

async function apiGet<T>(path: string): Promise<T> {
  const base = getApiBaseUrl();
  const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;
  const res = await fetch(url, {
    next: { revalidate: 15 },
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(
      `API ${res.status} ${res.statusText}${text ? `: ${text.slice(0, 200)}` : ""}`
    );
  }
  return res.json() as Promise<T>;
}

export function fetchDevices() {
  return apiGet<DevicesResponse>("/devices");
}

export function fetchPriorityTickets() {
  return apiGet<PriorityResponse>("/priority-tickets");
}

export function fetchFailureAnalytics() {
  return apiGet<FailuresResponse>("/analytics/failures");
}

export function fetchLatestLogs(deviceId: string) {
  return apiGet<LatestLogsResponse>(`/logs/latest/${encodeURIComponent(deviceId)}`);
}

export function fetchDeviceContext(deviceId: string) {
  return apiGet<ContextResponse>(
    `/device/context/${encodeURIComponent(deviceId)}`
  );
}
