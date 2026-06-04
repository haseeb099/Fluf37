import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getAgentColor(agentId: string): string {
  const map: Record<string, string> = {
    connector: "#34d399",
    silent_finder: "#fbbf24",
    adversarial: "#f87171",
    traceback: "#a78bfa",
    decision: "#38bdf8",
    evolution: "#fde047",
  };
  return map[agentId] || "#38bdf8";
}

export function getSeverityColor(severity: string): string {
  const map: Record<string, string> = {
    critical: "#ef4444",
    high: "#f97316",
    medium: "#fbbf24",
    low: "#94a3b8",
  };
  return map[severity] || "#94a3b8";
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}
