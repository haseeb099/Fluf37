import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getSeverityColor(severity: string): string {
  const map: Record<string, string> = {
    critical: "#ff1744",
    high: "#ff6d00",
    medium: "#ffd600",
    low: "#00e676",
  };
  return map[severity] || "#888";
}

export function getAgentColor(agentId: string): string {
  const map: Record<string, string> = {
    connector: "#00ff88",
    silent_finder: "#ff9900",
    adversarial: "#ff3366",
    traceback: "#9966ff",
    decision: "#00d4ff",
    evolution: "#ffff00",
  };
  return map[agentId] || "#00d4ff";
}
