"use client";

import { Badge } from "@/components/ui/Badge";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { getPlatformInfo } from "@/lib/api";
import { useHealthStatus } from "@/hooks/useHealthStatus";
import type { PlatformInfo } from "@/types/integrations";
import { AlertTriangle, Shield, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

export function PlatformStatusBanner() {
  const [platform, setPlatform] = useState<PlatformInfo | null>(null);
  const health = useHealthStatus();

  useEffect(() => {
    getPlatformInfo().then(setPlatform).catch(() => setPlatform(null));
  }, []);

  if (!platform && !health) return null;

  const llmLive = health?.llm_mode === "live";

  return (
    <Card className="border-sky-500/15 bg-gradient-to-r from-sky-950/30 to-transparent">
      <CardHeader className="mb-0">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Shield className="h-4 w-4 text-sky-400" />
              <span className="text-xs font-semibold uppercase tracking-wide text-sky-400">
                Platform status
              </span>
            </div>
            <CardTitle>{platform?.product_wedge ?? "Pre-Release Risk Review"}</CardTitle>
            <CardDescription>
              {platform?.deployment_mode ?? "demo"} deployment ·{" "}
              {platform?.launch_verdict?.replace("_", " ") ?? "pilot ready"}
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant={llmLive ? "success" : "warning"}>
              <Sparkles className="h-3 w-3 mr-1 inline" />
              LLM {health?.llm_mode ?? "canned"}
              {health?.llm_provider ? ` · ${health.llm_provider}` : ""}
            </Badge>
            <Badge variant={platform?.uses_demo_pipeline ? "warning" : "success"}>
              {platform?.uses_demo_pipeline ? "demo data" : "live data"}
            </Badge>
          </div>
        </div>
        {platform?.pilot_blockers && platform.pilot_blockers.length > 0 && (
          <div className="mt-4 pt-4 border-t border-border">
            <p className="text-xs text-amber-400/90 flex items-center gap-1.5 mb-2">
              <AlertTriangle className="h-3.5 w-3.5" />
              Pilot checklist
            </p>
            <ul className="text-xs text-muted space-y-1">
              {platform.pilot_blockers.slice(0, 3).map((b) => (
                <li key={b}>· {b}</li>
              ))}
            </ul>
          </div>
        )}
      </CardHeader>
    </Card>
  );
}
