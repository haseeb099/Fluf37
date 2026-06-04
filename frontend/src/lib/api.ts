const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_NEXUS_API_KEY || "demo-key";

let cachedToken: string | null = null;

/** Parse FastAPI error bodies into a short user-facing message. */
export function parseApiError(body: string, status: number): string {
  try {
    const parsed = JSON.parse(body) as { detail?: string | { msg?: string }[] };
    const detail = parsed.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg;
  } catch {
    /* plain text */
  }
  const trimmed = body.trim();
  if (trimmed) return trimmed;
  return `Request failed (${status})`;
}

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Nexus-Key": API_KEY,
    ...(options?.headers as Record<string, string> | undefined),
  };
  if (cachedToken) {
    headers.Authorization = `Bearer ${cachedToken}`;
  }
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(parseApiError(body, res.status));
  }
  return res.json();
}

export type NexusRole = "viewer" | "analyst" | "admin";

export async function fetchAuthToken(role: NexusRole = "viewer"): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Nexus-Key": API_KEY,
      "X-Nexus-Role": role,
    },
  });
  if (!res.ok) throw new Error(await res.text());
  const body = (await res.json()) as { access_token: string };
  cachedToken = body.access_token;
  return cachedToken;
}

export function getCachedAuthToken(): string | null {
  return cachedToken;
}

export async function getSourcesStatus() {
  return fetchApi<{ sources: unknown[] }>("/api/v1/sources/status");
}

export async function connectSource(source: string) {
  await fetchAuthToken("admin");
  return fetchApi(`/api/v1/connect/${source}`, { method: "POST" });
}

export async function syncSource(source: string) {
  await fetchAuthToken("analyst");
  return fetchApi(`/api/v1/connect/${source}/sync`, { method: "POST" });
}

export async function runPipelineDemo() {
  await fetchAuthToken("analyst");
  return fetchApi("/api/v1/nexus/run/demo", { method: "POST" });
}

export async function runRiskReview() {
  await fetchAuthToken("analyst");
  return fetchApi<{
    summary: { review_id: string; blind_spots_count: number; top_recommendation: string };
    findings: unknown[];
  }>("/api/v1/risk-review/run", { method: "POST" });
}

export async function getPlatformInfo() {
  return fetchApi<import("@/types/integrations").PlatformInfo>("/api/v1/platform/info");
}

export async function getHealth() {
  const res = await fetch(`${API_URL}/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json() as Promise<import("@/types/integrations").HealthInfo>;
}

export async function getPluginCatalog(params?: { category?: string; installed?: boolean }) {
  const qs = new URLSearchParams();
  if (params?.category) qs.set("category", params.category);
  if (params?.installed) qs.set("installed", "true");
  const q = qs.toString();
  return fetchApi<import("@/types/integrations").PluginCatalogResponse>(
    `/api/v1/plugins${q ? `?${q}` : ""}`
  );
}

export async function getPlugin(pluginId: string) {
  return fetchApi<import("@/types/integrations").PluginManifest>(`/api/v1/plugins/${pluginId}`);
}

export async function registerPlugin(body: import("@/types/integrations").PluginRegistrationRequest) {
  await fetchAuthToken("admin");
  return fetchApi<import("@/types/integrations").PluginManifest>("/api/v1/plugins/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function unregisterPlugin(pluginId: string) {
  await fetchAuthToken("admin");
  return fetchApi<{ removed: string }>(`/api/v1/plugins/${pluginId}`, { method: "DELETE" });
}

export async function disconnectSource(source: string) {
  await fetchAuthToken("admin");
  return fetchApi(`/api/v1/connect/${source}`, { method: "DELETE" });
}

export async function getConnectors() {
  return fetchApi<{ types: string[]; capabilities: unknown[] }>("/api/v1/connectors");
}

export async function getDecisions() {
  return fetchApi<unknown[]>("/api/v1/decisions/");
}

export async function getMemoryGraph() {
  return fetchApi<{ nodes: unknown[]; edges: unknown[] }>("/api/v1/memory/graph");
}

export async function getEvolutionReport() {
  return fetchApi("/api/v1/evolution/report");
}

export async function submitOutcome(id: string, outcome: "correct" | "incorrect") {
  return fetchApi(`/api/v1/decisions/${id}/outcome`, {
    method: "POST",
    body: JSON.stringify({ outcome }),
  });
}
