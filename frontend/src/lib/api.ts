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

export async function fetchAuthToken(): Promise<string> {
  const res = await fetch(`${API_URL}/api/v1/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Nexus-Key": API_KEY,
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
  return fetchApi(`/api/v1/connect/${source}`, { method: "POST" });
}

export async function syncSource(source: string) {
  return fetchApi(`/api/v1/connect/${source}/sync`, { method: "POST" });
}

export async function runPipelineDemo() {
  return fetchApi("/api/v1/nexus/run/demo", { method: "POST" });
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
