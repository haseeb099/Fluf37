/** Map raw backend agent errors to user-facing copy. */
export function formatAgentError(data: unknown): string {
  const raw =
    typeof data === "string" ? data : JSON.stringify(data ?? "Agent error");
  const lower = raw.toLowerCase();
  if (lower.includes("429") || lower.includes("rate_limit") || lower.includes("rate limit")) {
    return "Groq daily token limit reached — review completed with demo narrative. Retry later or set NEXUS_LIVE_LLM=false.";
  }
  if (lower.includes("invalid_token")) {
    return "WebSocket authentication failed";
  }
  if (raw.length > 200) {
    return `${raw.slice(0, 200)}…`;
  }
  return raw;
}
