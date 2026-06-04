"use client";

import { Card } from "@/components/ui/Card";
import { useNexusStore } from "@/store/nexusStore";
import { Activity, AlertCircle, CheckCircle2, Plug } from "lucide-react";
import Link from "next/link";

export function KpiStrip() {
  const blindSpots = useNexusStore((s) => s.blindSpots);
  const decisions = useNexusStore((s) => s.decisions);
  const pipelineState = useNexusStore((s) => s.pipelineState);
  const isConnected = useNexusStore((s) => s.isConnected);

  const critical = blindSpots.filter((b) => b.severity === "critical").length;
  const complete = pipelineState === "COMPLETE";

  const items = [
    {
      label: "Findings",
      value: blindSpots.length,
      sub: critical ? `${critical} critical` : "Run review to scan",
      icon: AlertCircle,
      accent: critical > 0 ? "text-red-400" : "text-slate-400",
    },
    {
      label: "Decisions",
      value: decisions.length,
      sub: complete ? "Ready for sign-off" : "Pending review",
      icon: CheckCircle2,
      accent: "text-emerald-400",
    },
    {
      label: "Pipeline",
      value: pipelineState,
      sub: isConnected ? "Stream connected" : "Reconnect WS",
      icon: Activity,
      accent: complete ? "text-emerald-400" : "text-sky-400",
    },
    {
      label: "Integrations",
      value: "Hub",
      sub: "Plugins & sources",
      icon: Plug,
      accent: "text-sky-400",
      href: "/integrations",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {items.map((item) => {
        const Icon = item.icon;
        const inner = (
          <Card className="glass-panel-hover p-4 h-full">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-muted uppercase tracking-wide">{item.label}</p>
                <p className="text-xl font-semibold text-slate-100 mt-1 truncate">{item.value}</p>
                <p className="text-xs text-muted mt-1">{item.sub}</p>
              </div>
              <Icon className={`h-5 w-5 shrink-0 ${item.accent}`} />
            </div>
          </Card>
        );
        return item.href ? (
          <Link key={item.label} href={item.href} className="block">
            {inner}
          </Link>
        ) : (
          <div key={item.label}>{inner}</div>
        );
      })}
    </div>
  );
}
