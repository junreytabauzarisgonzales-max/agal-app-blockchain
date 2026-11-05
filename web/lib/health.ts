import { BACKEND_HEALTH_URL } from "@/lib/config";

export interface HealthResult {
  status: "online" | "unavailable" | "unknown";
  detail: string;
}

export async function checkBackendHealth(signal: AbortSignal): Promise<HealthResult> {
  try {
    const response = await fetch(BACKEND_HEALTH_URL, {
      signal,
      cache: "no-store",
      credentials: "omit",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      return { status: "unavailable", detail: `The health endpoint returned HTTP ${response.status}.` };
    }
    const body: unknown = await response.json();
    if (typeof body === "object" && body !== null && "status" in body && body.status === "ok") {
      return { status: "online", detail: "The health endpoint responded successfully. This checks API reachability, not database or ledger readiness." };
    }
    return { status: "unknown", detail: "The endpoint responded, but its health could not be confirmed." };
  } catch {
    return { status: "unknown", detail: "Could not confirm status from this browser. A connection, timeout, or browser access restriction may prevent the check." };
  }
}
