const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = "demo-key";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Nexus-Key": API_KEY,
      ...options?.headers,
    },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
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
