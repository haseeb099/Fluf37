import {
  Code2,
  Landmark,
  Newspaper,
  Plug,
  TrendingUp,
  Users,
  Webhook,
  type LucideIcon,
} from "lucide-react";

const ICONS: Record<string, LucideIcon> = {
  users: Users,
  ledger: Landmark,
  landmark: Landmark,
  trending: TrendingUp,
  newspaper: Newspaper,
  code: Code2,
  webhook: Webhook,
  plug: Plug,
};

export function pluginIcon(name: string): LucideIcon {
  return ICONS[name] || Plug;
}

export function dataModeBadge(mode?: string): "success" | "warning" | "default" | "outline" {
  if (mode === "live") return "success";
  if (mode === "demo") return "warning";
  if (mode === "stub" || mode === "empty") return "outline";
  return "default";
}

export function connectionBadge(state?: string): "success" | "warning" | "critical" | "outline" {
  if (state === "connected") return "success";
  if (state === "degraded") return "warning";
  if (state === "error") return "critical";
  return "outline";
}
